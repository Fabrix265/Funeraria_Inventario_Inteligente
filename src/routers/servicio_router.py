from fastapi import APIRouter, Depends, HTTPException, status, Query
from src.deps.db_session import SessionDep
from src.deps.role_check import get_current_admin, get_current_user
from src.deps.servicio_filters import filtros_servicio
from src.schemas.servicio import ServicioCrear, ServicioEditar, ServicioLeerCompleto, ServicioPaginado
import src.services.servicio_service as service

servicio_router = APIRouter()

@servicio_router.get("/", response_model=ServicioPaginado)
def listar_servicios(
    session: SessionDep,
    filtros: dict = Depends(filtros_servicio),
    token: dict = Depends(get_current_user),
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
):
    return service.listar_servicios(session, **filtros, offset=offset, limit=limit)

@servicio_router.get("/{servicio_id}", response_model=ServicioLeerCompleto)
def obtener_servicio(servicio_id: int, session: SessionDep, token: dict = Depends(get_current_user)):
    return service.obtener_servicio(session, servicio_id)

@servicio_router.post("/", response_model=ServicioLeerCompleto, status_code=201)
def crear_servicio(datos: ServicioCrear, session: SessionDep, token: dict = Depends(get_current_user)):
    id_usuario = token.get("id") or token.get("sub")
    if id_usuario is None:
        raise HTTPException(status_code=401, detail="Token inválido")
    return service.crear_servicio(session, datos, int(id_usuario))

@servicio_router.patch("/{servicio_id}", response_model=ServicioLeerCompleto)
def modificar_servicio(
    servicio_id: int,
    datos: ServicioEditar,
    session: SessionDep,
    token: dict = Depends(get_current_admin),
):
    campos = datos.model_dump(exclude_unset=True)
    if not campos:
        raise HTTPException(status_code=400, detail="No hay campos para actualizar")
    return service.modificar_servicio(session, servicio_id, campos)

@servicio_router.delete("/{servicio_id}")
def eliminar_servicio(servicio_id: int, session: SessionDep, token: dict = Depends(get_current_admin)):
    return service.eliminar_servicio(session, servicio_id)