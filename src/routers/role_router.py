from fastapi import APIRouter, Depends
from typing import List
from src.deps.db_session import SessionDep
from src.core.security import CheckerPermisos
from src.services.role_service import RoleService
from src.schemas.user import RoleCrear, RoleDetalleLeer, PermissionLeer

role_router = APIRouter()

@role_router.get("/permisos", response_model=List[PermissionLeer], dependencies=[Depends(CheckerPermisos("usuarios:listar"))])
def listar_todos_los_permisos(db: SessionDep):
    return RoleService.listar_permisos(db)

@role_router.post("/", response_model=RoleDetalleLeer, dependencies=[Depends(CheckerPermisos("usuarios:crear"))])
def crear_nuevo_rol(rol_in: RoleCrear, db: SessionDep):
    return RoleService.crear_rol(db, rol_in)

@role_router.delete("/{role_id}", dependencies=[Depends(CheckerPermisos("usuarios:eliminar"))])
def eliminar_rol(role_id: int, db: SessionDep):
    return RoleService.eliminar_rol(db, role_id)

@role_router.get("/", response_model=List[RoleDetalleLeer], dependencies=[Depends(CheckerPermisos("usuarios:listar"))])
def listar_roles(db: SessionDep):
    return RoleService.listar_roles(db)