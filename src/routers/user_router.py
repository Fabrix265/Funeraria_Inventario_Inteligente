from fastapi import APIRouter, Depends, Query, Request
from typing import List, Optional
from src.deps.db_session import SessionDep
from src.core.security import decode_token, CheckerPermisos
from src.services.user_service import UserService
from src.schemas.user import UserLeer, UserCrear, UserActualizarSe, RoleLeer, UserActualizarAdmin
from src.schemas.estado import EstadoUpdate
from src.services import bitacora_service

user_router = APIRouter()

@user_router.get("/roles", response_model=List[RoleLeer], dependencies=[Depends(decode_token)])
def listar_roles(db: SessionDep):
    return UserService.obtener_roles(db)

@user_router.post("/", response_model=UserLeer, dependencies=[Depends(CheckerPermisos("usuarios:crear"))])
def crear_usuario(
    request: Request,
    user_in: UserCrear, db: SessionDep,
    token: dict = Depends(CheckerPermisos("usuarios:crear")),
):
    resultado = UserService.crear_usuario(db, user_in)
    bitacora_service.registrar(
        db,
        usuario_id=int(token.get("sub")),
        usuario_nombre=token.get("username", ""),
        accion="crear",
        modulo="usuarios",
        detalle=f"Usuario '{user_in.username}' creado",
        ip_address=request.client.host if request.client else None,
    )
    return resultado

@user_router.get("/", response_model=List[UserLeer], dependencies=[Depends(CheckerPermisos("usuarios:listar"))])
def listar_usuarios(
    db: SessionDep,
    activo: Optional[bool] = Query(None),
):
    return UserService.obtener_usuarios(db, activo=activo)

@user_router.delete("/{user_id}", dependencies=[Depends(CheckerPermisos("usuarios:eliminar"))])
def eliminar_usuario(
    request: Request,
    user_id: int, db: SessionDep, token: dict = Depends(decode_token),
):
    current_user_id = int(token.get("sub"))
    resultado = UserService.eliminar_usuario(db, user_id, current_user_id)
    bitacora_service.registrar(
        db,
        usuario_id=current_user_id,
        usuario_nombre=token.get("username", ""),
        accion="eliminar",
        modulo="usuarios",
        detalle=f"Usuario #{user_id} eliminado",
        ip_address=request.client.host if request.client else None,
    )
    return resultado

@user_router.put("/me", response_model=UserLeer)
def editar_mi_perfil(
    request: Request,
    user_in: UserActualizarSe, db: SessionDep, token: dict = Depends(decode_token),
):
    user_id = int(token.get("sub"))
    resultado = UserService.actualizar_perfil(db, user_id, user_in)
    bitacora_service.registrar(
        db,
        usuario_id=user_id,
        usuario_nombre=token.get("username", ""),
        accion="actualizar",
        modulo="usuarios",
        detalle="Perfil actualizado",
        ip_address=request.client.host if request.client else None,
    )
    return resultado

@user_router.put("/{user_id}", response_model=UserLeer, dependencies=[Depends(CheckerPermisos("usuarios:crear"))])
def actualizar_usuario_como_administrador(
    request: Request,
    user_id: int, user_in: UserActualizarAdmin, db: SessionDep,
    token: dict = Depends(CheckerPermisos("usuarios:crear")),
):
    resultado = UserService.actualizar_usuario_por_admin(db, user_id, user_in)
    bitacora_service.registrar(
        db,
        usuario_id=int(token.get("sub")),
        usuario_nombre=token.get("username", ""),
        accion="actualizar",
        modulo="usuarios",
        detalle=f"Usuario #{user_id} actualizado por administrador",
        ip_address=request.client.host if request.client else None,
    )
    return resultado

@user_router.patch("/{user_id}/status", response_model=UserLeer, dependencies=[Depends(CheckerPermisos("usuarios:crear"))])
def cambiar_estado_usuario(
    request: Request,
    user_id: int, datos: EstadoUpdate, db: SessionDep, token: dict = Depends(decode_token),
):
    current_user_id = int(token.get("sub"))
    resultado = UserService.cambiar_estado(db, user_id, datos.activo, current_user_id)
    estado = "activado" if datos.activo else "desactivado"
    bitacora_service.registrar(
        db,
        usuario_id=current_user_id,
        usuario_nombre=token.get("username", ""),
        accion="cambiar_estado",
        modulo="usuarios",
        detalle=f"Usuario #{user_id} {estado}",
        ip_address=request.client.host if request.client else None,
    )
    return resultado
