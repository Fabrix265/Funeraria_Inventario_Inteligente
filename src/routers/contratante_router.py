from typing import Optional
from fastapi import APIRouter, Depends, Query, Request
from src.deps.db_session import SessionDep
from src.core.security import CheckerPermisos
from src.schemas.contratante import ContratanteLeer, ContratanteBase
from src.schemas.estado import EstadoUpdate
from src.services.contratante_service import ContratanteService
from src.services import bitacora_service

contratante_router = APIRouter()

@contratante_router.get("/", response_model=list[ContratanteLeer], dependencies=[Depends(CheckerPermisos("contratantes:leer"))])
def listar_contratantes(
    session: SessionDep,
    nombre: Optional[str] = Query(None),
    dni: Optional[str] = Query(None),
    activo: Optional[bool] = Query(None),
):
    return ContratanteService.listar_todos(session, nombre=nombre, dni=dni, activo=activo)

@contratante_router.get("/{id}", response_model=ContratanteLeer, dependencies=[Depends(CheckerPermisos("contratantes:leer"))])
def obtener_contratante(id: int, session: SessionDep):
    return ContratanteService.obtener_por_id(session, id)

@contratante_router.patch("/{id}", response_model=ContratanteLeer, dependencies=[Depends(CheckerPermisos("contratantes:actualizar"))])
def actualizar_contratante(
    request: Request,
    id: int, datos: ContratanteBase, session: SessionDep,
    token: dict = Depends(CheckerPermisos("contratantes:actualizar")),
):
    campos = datos.model_dump(exclude_unset=True)
    resultado = ContratanteService.actualizar(session, id, campos)
    bitacora_service.registrar(
        session,
        usuario_id=int(token.get("sub")),
        usuario_nombre=token.get("username", ""),
        accion="actualizar",
        modulo="contratantes",
        detalle=f"Contratante #{id} actualizado",
        ip_address=request.client.host if request.client else None,
    )
    return resultado

@contratante_router.patch("/{id}/status", response_model=ContratanteLeer, dependencies=[Depends(CheckerPermisos("contratantes:actualizar"))])
def cambiar_estado_contratante(
    request: Request,
    id: int, datos: EstadoUpdate, session: SessionDep,
    token: dict = Depends(CheckerPermisos("contratantes:actualizar")),
):
    resultado = ContratanteService.cambiar_estado(session, id, datos.activo)
    estado = "activado" if datos.activo else "desactivado"
    bitacora_service.registrar(
        session,
        usuario_id=int(token.get("sub")),
        usuario_nombre=token.get("username", ""),
        accion="cambiar_estado",
        modulo="contratantes",
        detalle=f"Contratante #{id} {estado}",
        ip_address=request.client.host if request.client else None,
    )
    return resultado

@contratante_router.delete("/{id}", dependencies=[Depends(CheckerPermisos("contratantes:eliminar"))])
def eliminar(
    request: Request,
    id: int, session: SessionDep,
    token: dict = Depends(CheckerPermisos("contratantes:eliminar")),
):
    resultado = ContratanteService.eliminar(session, id)
    bitacora_service.registrar(
        session,
        usuario_id=int(token.get("sub")),
        usuario_nombre=token.get("username", ""),
        accion="eliminar",
        modulo="contratantes",
        detalle=f"Contratante #{id} eliminado",
        ip_address=request.client.host if request.client else None,
    )
    return resultado
