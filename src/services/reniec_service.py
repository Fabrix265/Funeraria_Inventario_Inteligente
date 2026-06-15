import httpx
import os
from fastapi import HTTPException

RENIEC_API_URL = "https://api.decolecta.com/v1/reniec/dni"
RENIEC_TOKEN   = os.getenv("RENIEC_TOKEN")

class ReniecService:
    @staticmethod
    async def consultar_dni(dni: str) -> dict:
        if not dni or not dni.isdigit() or len(dni) != 8:
            raise HTTPException(status_code=400, detail="DNI inválido — debe tener exactamente 8 dígitos")

        if not RENIEC_TOKEN:
            raise HTTPException(status_code=503, detail="Token RENIEC no configurado")

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(
                    RENIEC_API_URL,
                    params={"numero": dni},
                    headers={
                        "Authorization": f"Bearer {RENIEC_TOKEN}",
                        "Accept": "application/json"
                    }
                )
            except httpx.ConnectError:
                raise HTTPException(status_code=503, detail="No se pudo conectar con el servicio RENIEC")

        if response.status_code == 401:
            raise HTTPException(status_code=503, detail="Token RENIEC inválido o expirado")
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="DNI no encontrado")
        if response.status_code == 422:
            raise HTTPException(status_code=400, detail="DNI inválido según el servicio")
        if response.status_code != 200:
            raise HTTPException(status_code=502, detail=f"Error al consultar RENIEC ({response.status_code})")

        data = response.json()
        print("RESPUESTA DECOLECTA:", data)
        return {
                "dni":              data.get("document_number"),
                "nombres":          data.get("first_name"),
                "apellido_paterno": data.get("first_last_name"),
                "apellido_materno": data.get("second_last_name"),
                "nombre_completo":  data.get("full_name")
        }