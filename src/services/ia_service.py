import io
import json
import logging
import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Any
from PIL import Image
from fastapi import HTTPException, status
from fastapi.concurrency import run_in_threadpool

logger = logging.getLogger("fastapi")

class ExtractorIAInterface(ABC):
    @abstractmethod
    def extraer_datos_contrato(self, imagen_bytes: bytes) -> Dict[str, Any]:
        pass

class QwenVLMockStrategy(ExtractorIAInterface):
    def extraer_datos_contrato(self, imagen_bytes: bytes) -> Dict[str, Any]:
        try:
            import time
            time.sleep(3)
            
            mock_data = {
                "fecha": "2025-07-24",
                "contratante_nombre": "MANUEL PAREDES IDIAQUEZ",
                "contratante_dni": "41632357",
                "contratante_telefono": "962923436",
                "fallecido_nombre": "ADELA ENRIQUEZ RIOS",
                "direccion_velacion": "AV. SANTA # 1094",
                "tipo_pago": "mixto",
                "ataud_modelo": "Lincol Biblia",
                "ataud_color": None,
                "capilla_modelo": "Iluminada", 
                "ids_vehiculos_detectados": ["porta_ataud", "porta_flores", "microbus", "auto"],
                "cantidad_cargadores": 4,
                "costo": 4500.00
            }
            return mock_data
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error en simulación: {str(e)}"
            )

def obtener_extractor_ia() -> ExtractorIAInterface:
    return QwenVLMockStrategy()

class IAService:
    @staticmethod
    async def procesar_imagen_contrato(imagen_bytes: bytes) -> Dict[str, Any]:
        extractor = obtener_extractor_ia()
        datos = await run_in_threadpool(extractor.extraer_datos_contrato, imagen_bytes)
        return datos