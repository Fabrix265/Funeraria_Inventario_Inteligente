from fastapi import APIRouter, Depends, Query
from typing import List, Optional

from src.deps.db_session import SessionDep
from src.deps.role_check import get_current_admin, get_current_user
from src.services.ataud_service import AtaudService
from src.schemas.ataud import AtaudLeer, AtaudCrear, AtaudModificar
from src.models.ataud import TipoAtaud
from src.schemas.stock import StockUpdate

ataud_router = APIRouter()

@ataud_router.get("/", response_model=List[AtaudLeer])
def listar_ataudes(
    db: SessionDep,
    modelo: Optional[str] = Query(None),
    color: Optional[str] = Query(None),
    stock: Optional[int] = Query(None, description="Ver ataudes con stock mayor o igual a este número"),
    tipo: Optional[TipoAtaud] = Query(None),
    _ = Depends(get_current_user)
):
    return AtaudService.obtener_todos(db, modelo, color, stock, tipo)

@ataud_router.post("/", response_model=AtaudLeer)
def crear_ataud(
    ataud_in: AtaudCrear, 
    db: SessionDep, 
    _ = Depends(get_current_admin)
):
    return AtaudService.crear(db, ataud_in)

@ataud_router.patch("/{ataud_id}", response_model=AtaudLeer)
def modificar_ataud(
    ataud_id: int, 
    ataud_in: AtaudModificar, 
    db: SessionDep, 
    _ = Depends(get_current_admin)
):
    return AtaudService.actualizar(db, ataud_id, ataud_in)

@ataud_router.delete("/{ataud_id}")
def eliminar_ataud(
    ataud_id: int, 
    db: SessionDep, 
    _ = Depends(get_current_admin)
):
    return AtaudService.eliminar(db, ataud_id)

@ataud_router.patch("/{ataud_id}/stock", response_model=AtaudLeer)
def actualizar_stock_ataud(
    ataud_id: int, 
    stock_in: StockUpdate, 
    db: SessionDep, 
    _ = Depends(get_current_admin)
):
    return AtaudService.actualizar_stock(db, ataud_id, stock_in.cantidad)