from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from src.deps.db_session import SessionDep
from src.core.security import decode_token
from src.services.user_service import UserService
from src.schemas.user import UserLeer, UserCrear, UserActualizarSe
from src.models.user import CargoEnum

user_router = APIRouter()

@user_router.post("/", response_model=UserLeer)
def crear_usuario(
    user_in: UserCrear, 
    db: SessionDep, 
    token: dict = Depends(decode_token)
):
    if token.get("cargo") != CargoEnum.administrador:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Solo los administradores pueden crear usuarios"
        )
    return UserService.crear_usuario(db, user_in)

@user_router.get("/", response_model=List[UserLeer])
def listar_usuarios(
    db: SessionDep, 
    token: dict = Depends(decode_token)
):
    es_admin = token.get("cargo") == CargoEnum.administrador
    return UserService.obtener_usuarios(db, es_admin)

@user_router.delete("/{user_id}")
def eliminar_usuario(
    user_id: int, 
    db: SessionDep, 
    token: dict = Depends(decode_token)
):
    if token.get("cargo") != CargoEnum.administrador:
        raise HTTPException(status_code=403, detail="Acceso denegado")
    return UserService.eliminar_usuario(db, user_id)

@user_router.put("/me", response_model=UserLeer)
def editar_mi_perfil(
    user_in: UserActualizarSe, 
    db: SessionDep, 
    token: dict = Depends(decode_token)
):
    user_id = int(token.get("sub"))
    
    return UserService.actualizar_perfil(db, user_id, user_in)