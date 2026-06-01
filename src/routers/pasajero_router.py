from typing import List
from fastapi import APIRouter, Depends
from src.deps.db_session import SessionDep
from src.core.security import CheckerPermisos
from src.schemas.pasajero import PasajeroLeer, PasajeroCrear
from src.services.pasajero_service import PasajeroService

pasajero_router = APIRouter()

@pasajero_router.get(
    "/services/{servicio_id}",
    response_model=List[PasajeroLeer],
    dependencies=[Depends(CheckerPermisos("pasajeros:listar"))],
)
def listar_pasajeros(servicio_id: int, session: SessionDep):
    return PasajeroService.listar_por_servicio(session, servicio_id)

@pasajero_router.post(
    "/services/{servicio_id}",
    response_model=PasajeroLeer,
    status_code=201,
    dependencies=[Depends(CheckerPermisos("pasajeros:crear"))],
)
def agregar_pasajero(servicio_id: int, datos: PasajeroCrear, session: SessionDep):
    return PasajeroService.agregar_pasajero(session, servicio_id, datos.model_dump())

@pasajero_router.patch(
    "/{pasajero_id}",
    response_model=PasajeroLeer,
    dependencies=[Depends(CheckerPermisos("pasajeros:actualizar"))],
)
def actualizar_pasajero(pasajero_id: int, datos: PasajeroCrear, session: SessionDep):
    return PasajeroService.actualizar(session, pasajero_id, datos.model_dump(exclude_unset=True))

@pasajero_router.delete(
    "/{pasajero_id}",
    dependencies=[Depends(CheckerPermisos("pasajeros:eliminar"))],
)
def eliminar_pasajero(pasajero_id: int, session: SessionDep):
    return PasajeroService.eliminar(session, pasajero_id)
