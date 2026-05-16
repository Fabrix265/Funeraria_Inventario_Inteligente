from typing import Optional
from fastapi import APIRouter, Depends, Query
from src.deps.db_session import SessionDep
from src.deps.role_check import get_current_user, get_current_admin
from src.schemas.fallecido import FallecidoLeer, FallecidoBase
from src.services.fallecido_service import FallecidoService

fallecido_router = APIRouter()
@fallecido_router.get("/", response_model=list[FallecidoLeer])
def listar_fallecidos(
    session: SessionDep, 
    nombre: Optional[str] = Query(None, description="Filtrar por nombre"),
    dni: Optional[str] = Query(None, description="Filtrar por DNI exacto"),
    _ = Depends(get_current_user)
):
    return FallecidoService.listar_todos(session, nombre=nombre, dni=dni)


@fallecido_router.get("/{id}", response_model=FallecidoLeer)
def obtener_fallecido(
    id: int, 
    session: SessionDep, 
    token: dict = Depends(get_current_user)
):
    return FallecidoService.obtener_por_id(session, id)

@fallecido_router.patch("/{id}", response_model=FallecidoLeer)
def actualizar_fallecido(
    id: int, 
    datos: FallecidoBase, 
    session: SessionDep, 
    token: dict = Depends(get_current_admin)
):
    campos = datos.model_dump(exclude_unset=True)
    return FallecidoService.actualizar(session, id, campos)

@fallecido_router.delete("/{id}")
def eliminar(id: int, session: SessionDep, token: dict = Depends(get_current_admin)):
    return FallecidoService.eliminar(session, id)