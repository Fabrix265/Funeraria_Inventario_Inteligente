from typing import Optional
from fastapi import APIRouter, Depends, Query, Request
from src.deps.db_session import SessionDep
from src.core.security import CheckerPermisos
from src.schemas.fallecido import FallecidoLeer, FallecidoBase
from src.schemas.estado import EstadoUpdate
from src.services.fallecido_service import FallecidoService
from src.services import bitacora_service

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
def actualizar_fallecido(
    request: Request,
    id: int, datos: FallecidoBase, session: SessionDep,
    token: dict = Depends(CheckerPermisos("fallecidos:actualizar")),
):
    campos = datos.model_dump(exclude_unset=True)
    resultado = FallecidoService.actualizar(session, id, campos)
    bitacora_service.registrar(
        session,
        usuario_id=int(token.get("sub")),
        usuario_nombre=token.get("username", ""),
        accion="actualizar",
        modulo="fallecidos",
        detalle=f"Fallecido #{id} actualizado",
        ip_address=request.client.host if request.client else None,
    )
    return resultado

@fallecido_router.patch("/{id}/status", response_model=FallecidoLeer, dependencies=[Depends(CheckerPermisos("fallecidos:actualizar"))])
def cambiar_estado_fallecido(
    request: Request,
    id: int, datos: EstadoUpdate, session: SessionDep,
    token: dict = Depends(CheckerPermisos("fallecidos:actualizar")),
):
    resultado = FallecidoService.cambiar_estado(session, id, datos.activo)
    estado = "activado" if datos.activo else "desactivado"
    bitacora_service.registrar(
        session,
        usuario_id=int(token.get("sub")),
        usuario_nombre=token.get("username", ""),
        accion="cambiar_estado",
        modulo="fallecidos",
        detalle=f"Fallecido #{id} {estado}",
        ip_address=request.client.host if request.client else None,
    )
    return resultado

@fallecido_router.delete("/{id}", dependencies=[Depends(CheckerPermisos("fallecidos:eliminar"))])
def eliminar(
    request: Request,
    id: int, session: SessionDep,
    token: dict = Depends(CheckerPermisos("fallecidos:eliminar")),
):
    resultado = FallecidoService.eliminar(session, id)
    bitacora_service.registrar(
        session,
        usuario_id=int(token.get("sub")),
        usuario_nombre=token.get("username", ""),
        accion="eliminar",
        modulo="fallecidos",
        detalle=f"Fallecido #{id} eliminado",
        ip_address=request.client.host if request.client else None,
    )
    return resultado
