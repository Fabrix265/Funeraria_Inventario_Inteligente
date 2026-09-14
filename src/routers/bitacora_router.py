from fastapi import APIRouter, Depends, Query
from typing import Optional
from src.deps.db_session import SessionDep
from src.core.security import CheckerPermisos
from src.schemas.bitacora import BitacoraRead, BitacoraListResponse
from src.services import bitacora_service

bitacora_router = APIRouter()


@bitacora_router.get("/", response_model=BitacoraListResponse)
def listar_bitacora(
    db: SessionDep,
    fecha_inicio: Optional[str] = Query(None),
    fecha_fin: Optional[str] = Query(None),
    usuario_id: Optional[int] = Query(None),
    accion: Optional[str] = Query(None),
    modulo: Optional[str] = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    _token: dict = Depends(CheckerPermisos("bitacora:listar")),
):
    return bitacora_service.listar(
        db,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        usuario_id=usuario_id,
        accion=accion,
        modulo=modulo,
        offset=offset,
        limit=limit,
    )


@bitacora_router.get("/{bitacora_id}", response_model=BitacoraRead)
def obtener_bitacora(
    bitacora_id: int,
    db: SessionDep,
    _token: dict = Depends(CheckerPermisos("bitacora:listar")),
):
    resultado = bitacora_service.obtener_por_id(db, bitacora_id)
    if not resultado:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Registro de bitacora no encontrado")
    return resultado
