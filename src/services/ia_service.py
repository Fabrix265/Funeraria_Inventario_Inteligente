import io
import json
import logging
import os
import traceback 
from abc import ABC, abstractmethod
from typing import Dict, Any

import torch
from PIL import Image
Image.MAX_IMAGE_PIXELS = None  

from fastapi import HTTPException, status
from fastapi.concurrency import run_in_threadpool
from transformers import Qwen2_5_VLForConditionalGeneration, AutoProcessor, BitsAndBytesConfig
from qwen_vl_utils import process_vision_info

logger = logging.getLogger("fastapi")

PROMPT_CONTRATO = """Analiza esta imagen de un contrato funerario y extrae los datos en formato JSON.
Devuelve ÚNICAMENTE el JSON, sin texto adicional, sin markdown, sin explicaciones.

El JSON debe tener exactamente esta estructura:
{
  "fecha": "YYYY-MM-DD o null",
  "contratante_nombre": "nombre completo o null",
  "contratante_dni": "8 dígitos o null",
  "contratante_telefono": "número o null",
  "fallecido_nombre": "nombre completo o null",
  "direccion_velacion": "dirección exacta o null",
  "tipo_pago": "directo o seguro o mixto o null",
  "ataud_modelo": "modelo del ataúd o null",
  "ataud_color": "color o null",
  "capilla_modelo": "nombre de la capilla o null",
  "ids_vehiculos_detectados": ["porta_ataud", "porta_flores", "mixto", "auto", "microbus"],
  "cantidad_cargadores": numero entero o null,
  "costo": numero decimal o null
}

Para ids_vehiculos_detectados usa solo estos valores exactos: porta_ataud, porta_flores, mixto, auto, microbus.
Si no puedes leer algún campo, ponlo como null."""


def optimizar_y_redimensionar_imagen(imagen_bytes: bytes, max_dim: int = 1200) -> Image.Image:
    imagen = Image.open(io.BytesIO(imagen_bytes)).convert("RGB")
    ancho, alto = imagen.size
    
    if ancho <= max_dim and alto <= max_dim:
        return imagen
        
    if ancho > alto:
        nuevo_ancho = max_dim
        nuevo_alto = int((alto * max_dim) / ancho)
    else:
        nuevo_alto = max_dim
        nuevo_ancho = int((ancho * max_dim) / alto)
        
    logger.info(f"Preprocesamiento Directo: Redimensionando de {ancho}x{alto} a {nuevo_ancho}x{nuevo_alto}")
    return imagen.resize((nuevo_ancho, nuevo_alto), Image.Resampling.LANCZOS)


class ExtractorIAInterface(ABC):
    @abstractmethod
    def extraer_datos_contrato(self, imagen_bytes: bytes) -> Dict[str, Any]:
        pass


class TransformersGPUStrategy(ExtractorIAInterface):
    def __init__(self):
        self.MODEL_ID = "Qwen/Qwen2.5-VL-3B-Instruct"
        self.DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
        
        if self.DEVICE != "cuda":
            logger.warning("¡Atención! No se detectó CUDA. Correrá extremadamente lento en CPU.")

        self.bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True, 
            bnb_4bit_quant_type="nf4",  
        )
        
        logger.info("Cargando Qwen2.5-VL en la GPU local...")
        self.model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
            self.MODEL_ID,
            quantization_config=self.bnb_config,
            device_map="auto",
            trust_remote_code=True,
        )
        self.model.eval()
        
        self.processor = AutoProcessor.from_pretrained(
            self.MODEL_ID,
            trust_remote_code=True,
        )
        logger.info("¡Modelo Qwen cargado exitosamente!")

    def extraer_datos_contrato(self, imagen_bytes: bytes) -> Dict[str, Any]:
        torch.cuda.empty_cache()
        contenido = ""
        
        try:
            imagen_optimizada = optimizar_y_redimensionar_imagen(imagen_bytes, max_dim=800)

            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image", 
                            "image": imagen_optimizada,
                            "min_pixels": 256 * 256,
                            "max_pixels": 800 * 800
                        },
                        {"type": "text", "text": PROMPT_CONTRATO},
                    ],
                }
            ]

            text_input = self.processor.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
            image_inputs, video_inputs = process_vision_info(messages)

            inputs = self.processor(
                text=[text_input],
                images=image_inputs,
                videos=video_inputs,
                padding=True,
                return_tensors="pt",
            )
            
            inputs = {k: v.to(self.DEVICE) if isinstance(v, torch.Tensor) else v for k, v in inputs.items()}

            with torch.no_grad():
                generated_ids = self.model.generate(
                    **inputs,
                    max_new_tokens=512, 
                    do_sample=False, 
                    temperature=None,
                    top_p=None,
                )

            generated_ids_trimmed = [
                out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs["input_ids"], generated_ids)
            ]
            output = self.processor.batch_decode(
                generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
            )
            
            contenido = output[0].strip()

            if contenido.startswith("```"):
                lineas = contenido.split("\n")
                lineas = [l for l in lineas if not l.startswith("```")]
                contenido = "\n".join(lineas).strip()

            datos = json.loads(contenido)
            return datos

        except json.JSONDecodeError:
            logger.error(f"Error en estructura JSON recibida: {contenido}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="La IA leyó el contrato pero no pudo estructurar la respuesta en un JSON válido."
            )
        except Exception as e:
            logger.error("Error crítico durante la inferencia en el service:")
            traceback.print_exc() 
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error en la inferencia por GPU local: {str(e)}"
            )
        finally:
            torch.cuda.empty_cache()


class MockStrategy(ExtractorIAInterface):
    def extraer_datos_contrato(self, imagen_bytes: bytes) -> Dict[str, Any]:
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


_extractor_gpu_instancia = None
_extractor_mock_instancia = None

USE_MOCK = False

def obtener_extractor_ia() -> ExtractorIAInterface:
    global _extractor_gpu_instancia, _extractor_mock_instancia
    
    if USE_MOCK:
        if _extractor_mock_instancia is None:
            _extractor_mock_instancia = MockStrategy()
        return _extractor_mock_instancia
    else:
        if _extractor_gpu_instancia is None:
            logger.info("Primera petición entrante. Cargando pesos del modelo en VRAM...")
            _extractor_gpu_instancia = TransformersGPUStrategy()
        return _extractor_gpu_instancia

class IAService:
    @staticmethod
    async def procesar_imagen_contrato(imagen_bytes: bytes) -> Dict[str, Any]:
        extractor = obtener_extractor_ia()
        datos = await run_in_threadpool(extractor.extraer_datos_contrato, imagen_bytes)
        return datos