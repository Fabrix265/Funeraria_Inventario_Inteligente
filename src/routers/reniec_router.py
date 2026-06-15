from fastapi import APIRouter, Depends
from src.core.security import decode_token
from src.services.reniec_service import ReniecService

reniec_router = APIRouter()

@reniec_router.get("/{dni}")
async def consultar_dni(dni: str, token: dict = Depends(decode_token)):
    return await ReniecService.consultar_dni(dni)