from fastapi import APIRouter, Depends, Query, status
from typing import List, Optional

from src.deps.db_session import SessionDep
from src.core.security import CheckerPermisos
from src.services.capilla_service import CapillaService
from src.schemas.capilla import CapillaLeer, CapillaCrear
from src.schemas.stock import StockUpdate

capilla_router = APIRouter()

@capilla_router.get("/", response_model=List[CapillaLeer], dependencies=[Depends(CheckerPermisos("capillas:leer"))])
def listar_capillas(
    db: SessionDep,
    modelo: Optional[str] = Query(None, description="Filtrar capillas por nombre de modelo"),
):
    return CapillaService.obtener_todas(db, modelo)

@capilla_router.post("/", response_model=CapillaLeer, status_code=status.HTTP_201_CREATED, dependencies=[Depends(CheckerPermisos("capillas:crear"))])
def crear_capilla(
    capilla_in: CapillaCrear,
    db: SessionDep,
):
    return CapillaService.crear(db, capilla_in)

@capilla_router.put("/{capilla_id}", response_model=CapillaLeer, dependencies=[Depends(CheckerPermisos("capillas:actualizar"))])
def actualizar_capilla(
    capilla_id: int,
    capilla_in: CapillaCrear,
    db: SessionDep,
):
    return CapillaService.actualizar(db, capilla_id, capilla_in)

@capilla_router.delete("/{capilla_id}", dependencies=[Depends(CheckerPermisos("capillas:eliminar"))])
def eliminar_capilla(
    capilla_id: int,
    db: SessionDep,
):
    return CapillaService.eliminar(db, capilla_id)

@capilla_router.patch("/{capilla_id}/stock", response_model=CapillaLeer, dependencies=[Depends(CheckerPermisos("capillas:actualizar"))])
def actualizar_stock_capilla(
    capilla_id: int,
    stock_in: StockUpdate,
    db: SessionDep,
):
    return CapillaService.actualizar_stock(db, capilla_id, stock_in.cantidad)