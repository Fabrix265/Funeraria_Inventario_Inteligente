from fastapi import APIRouter, Depends, Query, status
from typing import List, Optional
from src.deps.db_session import SessionDep
from src.deps.role_check import get_current_admin, get_current_user
from src.services.vehiculo_service import VehiculoService
from src.schemas.vehiculo import VehiculoLeer, VehiculoCrear
from src.models.vehiculo import TipoVehiculo

vehiculo_router = APIRouter()

@vehiculo_router.get("/", response_model=List[VehiculoLeer])
def listar_vehiculos(
    db: SessionDep,
    tipo: Optional[TipoVehiculo] = Query(None, description="Filtrar por tipo: porta_ataud, porta_flores, mixto, auto, microbus"),
    _ = Depends(get_current_user)
):
    return VehiculoService.obtener_todos(db, tipo)

@vehiculo_router.post("/", response_model=VehiculoLeer, status_code=status.HTTP_201_CREATED)
def crear_vehiculo(
    vehiculo_in: VehiculoCrear,
    db: SessionDep,
    _ = Depends(get_current_admin)
):
    return VehiculoService.crear(db, vehiculo_in)

@vehiculo_router.put("/{vehiculo_id}", response_model=VehiculoLeer)
def actualizar_vehiculo(
    vehiculo_id: int,
    vehiculo_in: VehiculoCrear,
    db: SessionDep,
    _ = Depends(get_current_admin)
):
    return VehiculoService.actualizar(db, vehiculo_id, vehiculo_in)

@vehiculo_router.delete("/{vehiculo_id}")
def eliminar_vehiculo(
    vehiculo_id: int,
    db: SessionDep,
    _ = Depends(get_current_admin)
):
    return VehiculoService.eliminar(db, vehiculo_id)