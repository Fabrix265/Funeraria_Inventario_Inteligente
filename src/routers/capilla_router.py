from fastapi import APIRouter, Depends, Query, status
from typing import List, Optional

from src.deps.db_session import SessionDep
from src.deps.role_check import get_current_admin, get_current_user
from src.services.capilla_service import CapillaService
from src.schemas.capilla import CapillaLeer, CapillaCrear
from src.schemas.stock import StockUpdate

capilla_router = APIRouter()

@capilla_router.get("/", response_model=List[CapillaLeer])
def listar_capillas(
    db: SessionDep,
    modelo: Optional[str] = Query(None, description="Filtrar capillas por nombre de modelo"),
    _ = Depends(get_current_user)
):
    return CapillaService.obtener_todas(db, modelo)

@capilla_router.post("/", response_model=CapillaLeer, status_code=status.HTTP_201_CREATED)
def crear_capilla(
    capilla_in: CapillaCrear,
    db: SessionDep,
    _ = Depends(get_current_admin)
):
    return CapillaService.crear(db, capilla_in)

@capilla_router.put("/{capilla_id}", response_model=CapillaLeer)
def actualizar_capilla(
    capilla_id: int,
    capilla_in: CapillaCrear,
    db: SessionDep,
    _ = Depends(get_current_admin)
):
    return CapillaService.actualizar(db, capilla_id, capilla_in)

@capilla_router.delete("/{capilla_id}")
def eliminar_capilla(
    capilla_id: int,
    db: SessionDep,
    _ = Depends(get_current_admin)
):
    return CapillaService.eliminar(db, capilla_id)

@capilla_router.patch("/{capilla_id}/stock", response_model=CapillaLeer)
def actualizar_stock_capilla(
    capilla_id: int, 
    stock_in: StockUpdate, 
    db: SessionDep, 
    _ = Depends(get_current_admin)
):
    return CapillaService.actualizar_stock(db, capilla_id, stock_in.cantidad)