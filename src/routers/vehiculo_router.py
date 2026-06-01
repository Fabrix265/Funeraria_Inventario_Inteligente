from fastapi import APIRouter, Depends, Query, status
from typing import List, Optional

from src.deps.db_session import SessionDep
from src.core.security import CheckerPermisos
from src.services.vehiculo_service import VehiculoService
from src.schemas.vehiculo import VehiculoLeer, VehiculoCrear
from src.schemas.estado import EstadoUpdate
from src.models.vehiculo import TipoVehiculo

vehiculo_router = APIRouter()

@vehiculo_router.get("/", response_model=List[VehiculoLeer], dependencies=[Depends(CheckerPermisos("vehiculos:leer"))])
def listar_vehiculos(
    db: SessionDep,
    tipo: Optional[TipoVehiculo] = Query(None, description="Filtrar por tipo: porta_ataud, porta_flores, mixto, auto, microbus"),
    activo: Optional[bool] = Query(None),
):
    return VehiculoService.obtener_todos(db, tipo, activo=activo)

@vehiculo_router.post("/", response_model=VehiculoLeer, status_code=status.HTTP_201_CREATED, dependencies=[Depends(CheckerPermisos("vehiculos:crear"))])
def crear_vehiculo(
    vehiculo_in: VehiculoCrear,
    db: SessionDep,
):
    return VehiculoService.crear(db, vehiculo_in)

@vehiculo_router.put("/{vehiculo_id}", response_model=VehiculoLeer, dependencies=[Depends(CheckerPermisos("vehiculos:actualizar"))])
def actualizar_vehiculo(
    vehiculo_id: int,
    vehiculo_in: VehiculoCrear,
    db: SessionDep,
):
    return VehiculoService.actualizar(db, vehiculo_id, vehiculo_in)

@vehiculo_router.delete("/{vehiculo_id}", dependencies=[Depends(CheckerPermisos("vehiculos:eliminar"))])
def eliminar_vehiculo(
    vehiculo_id: int,
    db: SessionDep,
):
    return VehiculoService.eliminar(db, vehiculo_id)

@vehiculo_router.patch("/{vehiculo_id}/status", response_model=VehiculoLeer, dependencies=[Depends(CheckerPermisos("vehiculos:actualizar"))])
def cambiar_estado_vehiculo(vehiculo_id: int, datos: EstadoUpdate, db: SessionDep):
    return VehiculoService.cambiar_estado(db, vehiculo_id, datos.activo)
