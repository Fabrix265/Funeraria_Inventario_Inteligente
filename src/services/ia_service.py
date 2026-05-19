import io
import json
import logging
import traceback
from abc import ABC, abstractmethod
from typing import Dict, Any

import torch
from PIL import Image, ImageOps, ImageFilter
Image.MAX_IMAGE_PIXELS = None

from fastapi import HTTPException, status
from fastapi.concurrency import run_in_threadpool
from transformers import Qwen2_5_VLForConditionalGeneration, AutoProcessor, BitsAndBytesConfig
from qwen_vl_utils import process_vision_info

logger = logging.getLogger("fastapi")

PROMPT_CONTRATO = """Eres un asistente especializado en leer contratos funerarios escaneados.
El contrato tiene DOS zonas claramente distintas que NO debes confundir:

ZONA 1 - MEMBRETE (IGNORAR para extracción de datos):
- Es el encabezado superior con el nombre y logo de la funeraria.
- Contiene la dirección y teléfonos DE LA EMPRESA (ej: "Av. Condorcanqui...", "044-679338").
- NUNCA uses estos datos para rellenar campos del contrato.

ZONA 2 - CUERPO DEL CONTRATO (ÚNICA fuente válida):
- Empieza donde dice "CONTRATO" y tiene campos con líneas para rellenar.
- Campos escritos a mano o mecanografiados por el cliente:
* "Trujillo, __ de __ del 20__" → fecha
* "Señor(a):" → contratante_nombre
* "Teléfono:" → contratante_telefono (junto al nombre del contratante)
* "Doc. Identidad:" → contratante_dni
* "Dirección:" → direccion_velacion (dirección del cliente/velatorio, NO de la empresa)
* "Oxiso:" o "Occiso:" → fallecido_nombre
* "Velatorio:" → puede complementar direccion_velacion si dice "SU CASA" u otro lugar
* "Forma de Pago:" → tipo_pago
* Tabla "COSTO DEL SERVICIO": filas Ataúd, Capilla ardiente, Carroza, Carroza para flores, Cargadores → extraer modelo/descripción y cantidades
* "TOTAL" al pie → costo

REGLAS ESTRICTAS:
- Devuelve ÚNICAMENTE el JSON sin ningún texto adicional, sin markdown, sin ```.
- Lee cada campo con atención, no inventes datos.
- Para "tipo_pago" usa SOLO una de estas palabras exactas: directo, seguro, mixto.
Si dice "al contado", "efectivo", "dinero", "cheque" usa "directo".
Si dice "seguro", "aseguradora" usa "seguro".
Si es combinación usa "mixto". Si no está claro usa null.
- Para "ids_vehiculos_detectados" usa SOLO estos valores exactos: porta_ataud, porta_flores, mixto, auto, microbus.
Detecta si hay descripción escrita en las filas "Carroza" (→ porta_ataud) y "Carroza para flores" (→ porta_flores).
Si no hay nada escrito en esas filas, usa [].
- Para "cantidad_cargadores" lee la fila "Cargadores" de la tabla. Solo acepta 4, 6 o null.
- Para "fecha" combina día, mes y año escritos en el campo "Trujillo, __ de __ del 20__". Formato YYYY-MM-DD.
- Para "contratante_dni" lee el campo "Doc. Identidad:" del cuerpo del contrato. Extrae exactamente 8 dígitos. Si no son 8 dígitos usa null.
- Para "contratante_telefono" lee el campo "Teléfono:" que está en la misma línea o muy cerca del campo "Señor(a):".
IGNORA los teléfonos del membrete superior de la empresa (044-679338, 943441226, 980494319, 044-564963).
- Para "direccion_velacion" lee ÚNICAMENTE el campo etiquetado como "Dirección:" en el cuerpo del contrato.
El campo "Velatorio:" es DIFERENTE y debe ser IGNORADO completamente para este dato.
- Para "ataud_modelo" lee la descripción escrita en la fila "Ataúd" de la tabla COSTO DEL SERVICIO.
- Para "ataud_color" extrae el color si está mencionado junto al modelo del ataúd.
- Para "capilla_modelo" lee la descripción escrita en la fila "Capilla ardiente".
- Para "costo" lee el valor numérico del campo "TOTAL" al pie del contrato.
- Si un campo no aparece o no puedes leerlo con certeza usa null.

Estructura JSON exacta:
{
"fecha": "YYYY-MM-DD o null",
"contratante_nombre": "nombre completo en mayusculas o null",
"contratante_dni": "exactamente 8 digitos o null",
"contratante_telefono": "solo digitos sin guiones ni espacios o null",
"fallecido_nombre": "nombre completo en mayusculas o null",
"direccion_velacion": "valor del campo Direccion del contrato o null",
"tipo_pago": "directo o seguro o mixto o null",
"ataud_modelo": "descripcion escrita en fila Ataud de la tabla o null",
"ataud_color": "color del ataud o null",
"capilla_modelo": "descripcion escrita en fila Capilla ardiente o null",
"ids_vehiculos_detectados": [],
"cantidad_cargadores": null,
"costo": 0.0
}"""


def preprocesar_imagen(imagen_bytes: bytes, max_dim: int = 1600) -> Image.Image:
    imagen = Image.open(io.BytesIO(imagen_bytes))

    # 1. Escala de grises → volver a RGB (modelo necesita 3 canales)
    imagen = imagen.convert("L").convert("RGB")
    ancho, alto = imagen.size

    # 2. Recortar márgenes vacíos
    bbox = imagen.convert("L").getbbox()
    if bbox:
        imagen = imagen.crop(bbox)
        logger.info(f"Crop márgenes: {ancho}x{alto} → {imagen.size[0]}x{imagen.size[1]}")
        ancho, alto = imagen.size

    # 3. Redimensionar si supera max_dim
    if ancho > max_dim or alto > max_dim:
        escala      = max_dim / max(ancho, alto)
        nuevo_ancho = int(ancho * escala)
        nuevo_alto  = int(alto * escala)
        imagen      = imagen.resize((nuevo_ancho, nuevo_alto), Image.Resampling.LANCZOS)
        logger.info(f"Redimensionado: {ancho}x{alto} → {nuevo_ancho}x{nuevo_alto}")

    # 4. Normalizar contraste
    imagen = ImageOps.autocontrast(imagen, cutoff=1)
    logger.info("Autocontraste aplicado")

    # 5. Nitidez leve
    imagen = imagen.filter(ImageFilter.SHARPEN)
    logger.info("Nitidez aplicada")

    return imagen


def limpiar_y_parsear_json(contenido: str) -> Dict[str, Any]:
    contenido = contenido.strip()
    if "```" in contenido:
        lineas = [l for l in contenido.split("\n") if not l.strip().startswith("```")]
        contenido = "\n".join(lineas).strip()
    inicio = contenido.find("{")
    fin    = contenido.rfind("}")
    if inicio != -1 and fin != -1:
        contenido = contenido[inicio:fin+1]
    return json.loads(contenido)


def normalizar_campos(datos: Dict[str, Any]) -> Dict[str, Any]:
    tipo_raw = str(datos.get("tipo_pago") or "").lower().strip()
    if any(p in tipo_raw for p in ["seguro", "aseguradora", "poliza"]):
        datos["tipo_pago"] = "seguro"
    elif any(p in tipo_raw for p in ["mixto", "combinado", "parcial"]):
        datos["tipo_pago"] = "mixto"
    elif any(p in tipo_raw for p in ["directo", "efectivo", "dinero", "contado", "cheque"]):
        datos["tipo_pago"] = "directo"
    elif tipo_raw in ["directo", "seguro", "mixto"]:
        datos["tipo_pago"] = tipo_raw
    else:
        datos["tipo_pago"] = None

    if datos.get("cantidad_cargadores") not in [4, 6, None]:
        datos["cantidad_cargadores"] = None

    validos = {"porta_ataud", "porta_flores", "mixto", "auto", "microbus"}
    raw = datos.get("ids_vehiculos_detectados", [])
    datos["ids_vehiculos_detectados"] = [v for v in raw if v in validos] if isinstance(raw, list) else []

    dni = str(datos.get("contratante_dni") or "").strip()
    if not (dni.isdigit() and len(dni) == 8):
        datos["contratante_dni"] = None

    telefono_raw = str(datos.get("contratante_telefono") or "").strip()
    telefono_limpio = "".join(filter(str.isdigit, telefono_raw))
    datos["contratante_telefono"] = telefono_limpio if telefono_limpio else None

    if str(datos.get("ataud_color") or "").lower() in ["null", "none", ""]:
        datos["ataud_color"] = None

    return datos


class ExtractorIAInterface(ABC):
    @abstractmethod
    def extraer_datos_contrato(self, imagen_bytes: bytes) -> Dict[str, Any]:
        pass


class TransformersGPUStrategy(ExtractorIAInterface):

    def __init__(self):
        self.MODEL_ID = "Qwen/Qwen2.5-VL-3B-Instruct"
        self.DEVICE   = "cuda" if torch.cuda.is_available() else "cpu"
        if self.DEVICE != "cuda":
            logger.warning("Sin CUDA. Correrá en CPU, será muy lento.")

        bnb = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
        )
        logger.info("Cargando Qwen2.5-VL-3B-Instruct...")
        self.model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
            self.MODEL_ID, quantization_config=bnb, device_map="auto", trust_remote_code=True,
        )
        self.model.eval()
        self.processor = AutoProcessor.from_pretrained(self.MODEL_ID, trust_remote_code=True)
        logger.info("Modelo cargado.")

    def extraer_datos_contrato(self, imagen_bytes: bytes) -> Dict[str, Any]:
        torch.cuda.empty_cache()
        contenido = ""
        try:
            imagen = preprocesar_imagen(imagen_bytes, max_dim=1600)
            messages = [{
                "role": "user",
                "content": [
                    {"type": "image", "image": imagen, "min_pixels": 512*512, "max_pixels": 1600*1600},
                    {"type": "text", "text": PROMPT_CONTRATO},
                ],
            }]
            text_input = self.processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            image_inputs, video_inputs = process_vision_info(messages)
            inputs = self.processor(text=[text_input], images=image_inputs, videos=video_inputs, padding=True, return_tensors="pt")
            inputs = {k: v.to(self.DEVICE) if isinstance(v, torch.Tensor) else v for k, v in inputs.items()}

            with torch.no_grad():
                generated_ids = self.model.generate(**inputs, max_new_tokens=600, do_sample=False, temperature=None, top_p=None)

            trimmed = [out[len(inp):] for inp, out in zip(inputs["input_ids"], generated_ids)]
            contenido = self.processor.batch_decode(trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]
            logger.info(f"Respuesta del modelo:\n{contenido}")

            datos = limpiar_y_parsear_json(contenido)
            return normalizar_campos(datos)

        except json.JSONDecodeError:
            logger.error(f"JSON invalido:\n{contenido}")
            raise HTTPException(status_code=422, detail="La IA no pudo estructurar la respuesta. Intenta con otra imagen.")
        except Exception as e:
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"Error en inferencia: {str(e)}")
        finally:
            torch.cuda.empty_cache()


class MockStrategy(ExtractorIAInterface):
    def extraer_datos_contrato(self, imagen_bytes: bytes) -> Dict[str, Any]:
        import time; time.sleep(2)
        return {
            "fecha": "2025-07-24",
            "contratante_nombre": "MANUEL PAREDES IDIAQUEZ (MOCK)",
            "contratante_dni": "41632357",
            "contratante_telefono": "962923436",
            "fallecido_nombre": "ADELA ENRIQUEZ RIOS",
            "direccion_velacion": "AV. SANTA # 1094",
            "tipo_pago": "mixto",
            "ataud_modelo": "Lincol Biblia",
            "ataud_color": "Plomo",
            "capilla_modelo": "Iluminada",
            "ids_vehiculos_detectados": ["porta_ataud", "porta_flores"],
            "cantidad_cargadores": 4,
            "costo": 4500.00
        }


_gpu_instancia  = None
_mock_instancia = None
USE_MOCK = False

def obtener_extractor_ia() -> ExtractorIAInterface:
    global _gpu_instancia, _mock_instancia
    if USE_MOCK:
        if _mock_instancia is None:
            _mock_instancia = MockStrategy()
        return _mock_instancia
    else:
        if _gpu_instancia is None:
            logger.info("Cargando modelo por primera vez...")
            _gpu_instancia = TransformersGPUStrategy()
        return _gpu_instancia


class IAService:
    @staticmethod
    async def procesar_imagen_contrato(imagen_bytes: bytes) -> Dict[str, Any]:
        extractor = obtener_extractor_ia()
        return await run_in_threadpool(extractor.extraer_datos_contrato, imagen_bytes)