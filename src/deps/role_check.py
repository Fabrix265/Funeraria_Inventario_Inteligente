from fastapi import Depends, HTTPException, status
from src.core.security import decode_token
from src.models.user import CargoEnum

def get_current_admin(token: dict = Depends(decode_token)):
    if token.get("cargo") != CargoEnum.administrador:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Acceso denegado: Se requiere ser Administrador"
        )
    return token

def get_current_user(token: dict = Depends(decode_token)):
    return token