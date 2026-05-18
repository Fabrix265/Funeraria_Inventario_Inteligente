from typing import Optional
from fastapi import APIRouter, Depends, Query
from src.deps.db_session import SessionDep
from src.deps.role_check import get_current_user, get_current_admin
from src.schemas.contratante import ContratanteLeer, ContratanteBase
from src.services.contratante_service import ContratanteService

contratante_router = APIRouter()

@contratante_router.get("/", response_model=list[ContratanteLeer])
def listar_contratantes(
    session: SessionDep, 
    nombre: Optional[str] = Query(None, description="Filtrar por nombre"),
    dni: Optional[str] = Query(None, description="Filtrar por DNI exacto"),
    _ = Depends(get_current_user)
):
    return ContratanteService.listar_todos(session, nombre=nombre, dni=dni)

@contratante_router.get("/{id}", response_model=ContratanteLeer)
def obtener_contratante(
    id: int, 
    session: SessionDep, 
    token: dict = Depends(get_current_user) 
):
    return ContratanteService.obtener_por_id(session, id)

@contratante_router.patch("/{id}", response_model=ContratanteLeer)
def actualizar_contratante(
    id: int, 
    datos: ContratanteBase, 
    session: SessionDep, 
    token: dict = Depends(get_current_admin)
):
    campos = datos.model_dump(exclude_unset=True)
    return ContratanteService.actualizar(session, id, campos)

@contratante_router.delete("/{id}")
def eliminar(id: int, session: SessionDep, token: dict = Depends(get_current_admin)):
    return ContratanteService.eliminar(session, id)