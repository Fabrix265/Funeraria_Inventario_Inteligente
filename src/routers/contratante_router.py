from typing import Optional
from fastapi import APIRouter, Depends, Query
from src.deps.db_session import SessionDep
from src.core.security import CheckerPermisos
from src.schemas.contratante import ContratanteLeer, ContratanteBase
from src.services.contratante_service import ContratanteService

contratante_router = APIRouter()

@contratante_router.get("/", response_model=list[ContratanteLeer], dependencies=[Depends(CheckerPermisos("contratantes:leer"))])
def listar_contratantes(
    session: SessionDep,
    nombre: Optional[str] = Query(None),
    dni: Optional[str] = Query(None),
):
    return ContratanteService.listar_todos(session, nombre=nombre, dni=dni)

@contratante_router.get("/{id}", response_model=ContratanteLeer, dependencies=[Depends(CheckerPermisos("contratantes:leer"))])
def obtener_contratante(id: int, session: SessionDep):
    return ContratanteService.obtener_por_id(session, id)

@contratante_router.patch("/{id}", response_model=ContratanteLeer, dependencies=[Depends(CheckerPermisos("contratantes:actualizar"))])
def actualizar_contratante(id: int, datos: ContratanteBase, session: SessionDep):
    campos = datos.model_dump(exclude_unset=True)
    return ContratanteService.actualizar(session, id, campos)

@contratante_router.delete("/{id}", dependencies=[Depends(CheckerPermisos("contratantes:eliminar"))])
def eliminar(id: int, session: SessionDep):
    return ContratanteService.eliminar(session, id)