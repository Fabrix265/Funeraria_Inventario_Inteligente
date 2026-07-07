from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from src.deps.db_session import SessionDep
from src.core.security import decode_token, CheckerPermisos
from src.services.user_service import UserService
from src.schemas.user import UserLeer, UserCrear, UserActualizarSe, RoleLeer, UserActualizarAdmin
from src.schemas.estado import EstadoUpdate

user_router = APIRouter()

@user_router.get("/roles", response_model=List[RoleLeer], dependencies=[Depends(decode_token)])
def listar_roles(db: SessionDep):
    return UserService.obtener_roles(db)

@user_router.post("/", response_model=UserLeer, dependencies=[Depends(CheckerPermisos("usuarios:crear"))])
def crear_usuario(user_in: UserCrear, db: SessionDep):
    return UserService.crear_usuario(db, user_in)

@user_router.get("/", response_model=List[UserLeer], dependencies=[Depends(CheckerPermisos("usuarios:listar"))])
def listar_usuarios(
    db: SessionDep,
    activo: Optional[bool] = Query(None),
):
    return UserService.obtener_usuarios(db, activo=activo)

@user_router.delete("/{user_id}", dependencies=[Depends(CheckerPermisos("usuarios:eliminar"))])
def eliminar_usuario(user_id: int, db: SessionDep, token: dict = Depends(decode_token)):
    current_user_id = int(token.get("sub"))
    return UserService.eliminar_usuario(db, user_id, current_user_id)

@user_router.put("/me", response_model=UserLeer)
def editar_mi_perfil(user_in: UserActualizarSe, db: SessionDep, token: dict = Depends(decode_token)):
    user_id = int(token.get("sub"))
    return UserService.actualizar_perfil(db, user_id, user_in)

@user_router.put("/{user_id}", response_model=UserLeer, dependencies=[Depends(CheckerPermisos("usuarios:crear"))])
def actualizar_usuario_como_administrador(user_id: int, user_in: UserActualizarAdmin, db: SessionDep):
    return UserService.actualizar_usuario_por_admin(db, user_id, user_in)

@user_router.patch("/{user_id}/status", response_model=UserLeer, dependencies=[Depends(CheckerPermisos("usuarios:crear"))])
def cambiar_estado_usuario(user_id: int, datos: EstadoUpdate, db: SessionDep, token: dict = Depends(decode_token)):
    current_user_id = int(token.get("sub"))
    return UserService.cambiar_estado(db, user_id, datos.activo, current_user_id)
