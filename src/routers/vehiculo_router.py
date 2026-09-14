from fastapi import APIRouter, Depends, Query, Request, status
from typing import List, Optional

from src.deps.db_session import SessionDep
from src.core.security import CheckerPermisos
from src.services.vehiculo_service import VehiculoService
from src.schemas.vehiculo import VehiculoLeer, VehiculoCrear
from src.schemas.estado import EstadoUpdate
from src.models.vehiculo import TipoVehiculo
from src.services import bitacora_service

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
    request: Request,
    vehiculo_in: VehiculoCrear,
    db: SessionDep,
    token: dict = Depends(CheckerPermisos("vehiculos:crear")),
):
    resultado = VehiculoService.crear(db, vehiculo_in)
    bitacora_service.registrar(
        db,
        usuario_id=int(token.get("sub")),
        usuario_nombre=token.get("username", ""),
        accion="crear",
        modulo="vehiculos",
        detalle=f"Vehiculo tipo '{resultado.tipo.value}' creado",
        ip_address=request.client.host if request.client else None,
    )
    return resultado

@vehiculo_router.put("/{vehiculo_id}", response_model=VehiculoLeer, dependencies=[Depends(CheckerPermisos("vehiculos:actualizar"))])
def actualizar_vehiculo(
    request: Request,
    vehiculo_id: int,
    vehiculo_in: VehiculoCrear,
    db: SessionDep,
    token: dict = Depends(CheckerPermisos("vehiculos:actualizar")),
):
    resultado = VehiculoService.actualizar(db, vehiculo_id, vehiculo_in)
    bitacora_service.registrar(
        db,
        usuario_id=int(token.get("sub")),
        usuario_nombre=token.get("username", ""),
        accion="actualizar",
        modulo="vehiculos",
        detalle=f"Vehiculo #{vehiculo_id} actualizado",
        ip_address=request.client.host if request.client else None,
    )
    return resultado

@vehiculo_router.delete("/{vehiculo_id}", dependencies=[Depends(CheckerPermisos("vehiculos:eliminar"))])
def eliminar_vehiculo(
    request: Request,
    vehiculo_id: int,
    db: SessionDep,
    token: dict = Depends(CheckerPermisos("vehiculos:eliminar")),
):
    resultado = VehiculoService.eliminar(db, vehiculo_id)
    bitacora_service.registrar(
        db,
        usuario_id=int(token.get("sub")),
        usuario_nombre=token.get("username", ""),
        accion="eliminar",
        modulo="vehiculos",
        detalle=f"Vehiculo #{vehiculo_id} eliminado",
        ip_address=request.client.host if request.client else None,
    )
    return resultado

@vehiculo_router.patch("/{vehiculo_id}/status", response_model=VehiculoLeer, dependencies=[Depends(CheckerPermisos("vehiculos:actualizar"))])
def cambiar_estado_vehiculo(
    request: Request,
    vehiculo_id: int, datos: EstadoUpdate, db: SessionDep,
    token: dict = Depends(CheckerPermisos("vehiculos:actualizar")),
):
    resultado = VehiculoService.cambiar_estado(db, vehiculo_id, datos.activo)
    estado = "activado" if datos.activo else "desactivado"
    bitacora_service.registrar(
        db,
        usuario_id=int(token.get("sub")),
        usuario_nombre=token.get("username", ""),
        accion="cambiar_estado",
        modulo="vehiculos",
        detalle=f"Vehiculo #{vehiculo_id} {estado}",
        ip_address=request.client.host if request.client else None,
    )
    return resultado
