from fastapi import APIRouter, Depends, Request
from typing import List
from sqlmodel import select
from src.deps.db_session import SessionDep
from src.core.security import CheckerPermisos
from src.services.role_service import RoleService
from src.schemas.user import RoleCrear, RoleDetalleLeer, PermissionLeer
from src.models.user import Permission 
from src.services import bitacora_service

role_router = APIRouter()

@role_router.get("/permits", response_model=List[PermissionLeer], dependencies=[Depends(CheckerPermisos("usuarios:listar"))])
def listar_todos_los_permisos(db: SessionDep):
    permisos = db.exec(
        select(Permission).where(~Permission.nombre.startswith("usuarios:"))
    ).all()
    return permisos

@role_router.post("/", response_model=RoleDetalleLeer, dependencies=[Depends(CheckerPermisos("usuarios:crear"))])
def crear_nuevo_rol(
    request: Request,
    rol_in: RoleCrear, db: SessionDep,
    token: dict = Depends(CheckerPermisos("usuarios:crear")),
):
    resultado = RoleService.crear_rol(db, rol_in)
    bitacora_service.registrar(
        db,
        usuario_id=int(token.get("sub")),
        usuario_nombre=token.get("username", ""),
        accion="crear",
        modulo="roles",
        detalle=f"Rol '{resultado.nombre}' creado",
        ip_address=request.client.host if request.client else None,
    )
    return resultado

@role_router.delete("/{role_id}", dependencies=[Depends(CheckerPermisos("usuarios:eliminar"))])
def eliminar_rol(
    request: Request,
    role_id: int, db: SessionDep,
    token: dict = Depends(CheckerPermisos("usuarios:eliminar")),
):
    resultado = RoleService.eliminar_rol(db, role_id)
    bitacora_service.registrar(
        db,
        usuario_id=int(token.get("sub")),
        usuario_nombre=token.get("username", ""),
        accion="eliminar",
        modulo="roles",
        detalle=f"Rol #{role_id} eliminado",
        ip_address=request.client.host if request.client else None,
    )
    return resultado

@role_router.get("/", response_model=List[RoleDetalleLeer], dependencies=[Depends(CheckerPermisos("usuarios:listar"))])
def listar_roles(db: SessionDep):
    return RoleService.listar_roles(db)
