from typing import Optional
from fastapi import APIRouter, Depends, Query
from src.deps.db_session import SessionDep
from src.core.security import CheckerPermisos
from src.schemas.fallecido import FallecidoLeer, FallecidoBase
from src.schemas.estado import EstadoUpdate
from src.services.fallecido_service import FallecidoService

fallecido_router = APIRouter()

@fallecido_router.get("/", response_model=list[FallecidoLeer], dependencies=[Depends(CheckerPermisos("fallecidos:leer"))])
def listar_fallecidos(
    session: SessionDep,
    nombre: Optional[str] = Query(None),
    dni_fallecido: Optional[str] = Query(None),
    activo: Optional[bool] = Query(None),
):
    return FallecidoService.listar_todos(session, nombre=nombre, dni_fallecido=dni_fallecido, activo=activo)

@fallecido_router.get("/{id}", response_model=FallecidoLeer, dependencies=[Depends(CheckerPermisos("fallecidos:leer"))])
def obtener_fallecido(id: int, session: SessionDep):
    return FallecidoService.obtener_por_id(session, id)

@fallecido_router.patch("/{id}", response_model=FallecidoLeer, dependencies=[Depends(CheckerPermisos("fallecidos:actualizar"))])
def actualizar_fallecido(id: int, datos: FallecidoBase, session: SessionDep):
    campos = datos.model_dump(exclude_unset=True)
    return FallecidoService.actualizar(session, id, campos)

@fallecido_router.patch("/{id}/status", response_model=FallecidoLeer, dependencies=[Depends(CheckerPermisos("fallecidos:actualizar"))])
def cambiar_estado_fallecido(id: int, datos: EstadoUpdate, session: SessionDep):
    return FallecidoService.cambiar_estado(session, id, datos.activo)

@fallecido_router.delete("/{id}", dependencies=[Depends(CheckerPermisos("fallecidos:eliminar"))])
def eliminar(id: int, session: SessionDep):
    return FallecidoService.eliminar(session, id)
