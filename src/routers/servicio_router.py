from fastapi import APIRouter, Depends, HTTPException, Query, Request
from src.deps.db_session import SessionDep
from src.core.security import CheckerPermisos, decode_token
from src.deps.servicio_filters import filtros_servicio
from src.schemas.servicio import ServicioCrear, ServicioEditar, ServicioLeerCompleto, ServicioPaginado
import src.services.servicio_service as service
from src.services import bitacora_service

servicio_router = APIRouter()

@servicio_router.get("/", response_model=ServicioPaginado, dependencies=[Depends(CheckerPermisos("servicios:leer"))])
def listar_servicios(
    session: SessionDep,
    filtros: dict = Depends(filtros_servicio),
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
):
    return service.listar_servicios(session, **filtros, offset=offset, limit=limit)

@servicio_router.get("/{servicio_id}", response_model=ServicioLeerCompleto, dependencies=[Depends(CheckerPermisos("servicios:leer"))])
def obtener_servicio(servicio_id: int, session: SessionDep):
    return service.obtener_servicio(session, servicio_id)

@servicio_router.post("/", response_model=ServicioLeerCompleto, status_code=201)
def crear_servicio(
    request: Request,
    datos: ServicioCrear,
    session: SessionDep,
    token: dict = Depends(CheckerPermisos("servicios:crear")),
):
    id_usuario = int(token.get("sub"))
    resultado = service.crear_servicio(session, datos, id_usuario)
    bitacora_service.registrar(
        session,
        usuario_id=id_usuario,
        usuario_nombre=token.get("username", ""),
        accion="crear",
        modulo="servicios",
        detalle=f"Servicio #{resultado.id} creado",
        ip_address=request.client.host if request.client else None,
    )
    return resultado

@servicio_router.patch("/{servicio_id}", response_model=ServicioLeerCompleto, dependencies=[Depends(CheckerPermisos("servicios:actualizar"))])
def modificar_servicio(
    request: Request,
    servicio_id: int,
    datos: ServicioEditar,
    session: SessionDep,
    token: dict = Depends(CheckerPermisos("servicios:actualizar")),
):
    campos = datos.model_dump(exclude_unset=True)
    if not campos:
        raise HTTPException(status_code=400, detail="No hay campos para actualizar")
    resultado = service.modificar_servicio(session, servicio_id, campos)
    bitacora_service.registrar(
        session,
        usuario_id=int(token.get("sub")),
        usuario_nombre=token.get("username", ""),
        accion="actualizar",
        modulo="servicios",
        detalle=f"Servicio #{servicio_id} actualizado",
        ip_address=request.client.host if request.client else None,
    )
    return resultado

@servicio_router.delete("/{servicio_id}", dependencies=[Depends(CheckerPermisos("servicios:eliminar"))])
def eliminar_servicio(
    request: Request,
    servicio_id: int, session: SessionDep,
    token: dict = Depends(CheckerPermisos("servicios:eliminar")),
):
    resultado = service.eliminar_servicio(session, servicio_id)
    bitacora_service.registrar(
        session,
        usuario_id=int(token.get("sub")),
        usuario_nombre=token.get("username", ""),
        accion="eliminar",
        modulo="servicios",
        detalle=f"Servicio #{servicio_id} eliminado",
        ip_address=request.client.host if request.client else None,
    )
    return resultado
