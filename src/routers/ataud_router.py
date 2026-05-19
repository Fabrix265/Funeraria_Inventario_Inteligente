from fastapi import APIRouter, Depends, Query
from typing import List, Optional

from src.deps.db_session import SessionDep
from src.core.security import CheckerPermisos  # Importamos el validador dinámico granular
from src.services.ataud_service import AtaudService
from src.schemas.ataud import AtaudLeer, AtaudCrear, AtaudModificar
from src.schemas.stock import StockUpdate

ataud_router = APIRouter()

@ataud_router.get("/", response_model=List[AtaudLeer], dependencies=[Depends(CheckerPermisos("ataudes:leer"))])
def listar_ataudes(
    db: SessionDep,
    modelo: Optional[str] = Query(None),
    color: Optional[str] = Query(None),
    stock: Optional[int] = Query(None, description="Ver ataudes con stock mayor o igual a este número")
):
    return AtaudService.obtener_todos(db, modelo, color, stock)

@ataud_router.post("/", response_model=AtaudLeer, dependencies=[Depends(CheckerPermisos("ataudes:crear"))])
def crear_ataud(
    ataud_in: AtaudCrear, 
    db: SessionDep
):
    return AtaudService.crear(db, ataud_in)

@ataud_router.patch("/{ataud_id}", response_model=AtaudLeer, dependencies=[Depends(CheckerPermisos("ataudes:actualizar"))])
def modificar_ataud(
    ataud_id: int, 
    ataud_in: AtaudModificar, 
    db: SessionDep
):
    return AtaudService.actualizar(db, ataud_id, ataud_in)

@ataud_router.delete("/{ataud_id}", dependencies=[Depends(CheckerPermisos("ataudes:eliminar"))])
def eliminar_ataud(
    ataud_id: int, 
    db: SessionDep
):
    return AtaudService.eliminar(db, ataud_id)

@ataud_router.patch("/{ataud_id}/stock", response_model=AtaudLeer, dependencies=[Depends(CheckerPermisos("ataudes:actualizar_stock"))])
def actualizar_stock_ataud(
    ataud_id: int, 
    stock_in: StockUpdate, 
    db: SessionDep
):
    return AtaudService.actualizar_stock(db, ataud_id, stock_in.cantidad)