from fastapi import APIRouter, Depends, Query, Request
from typing import List, Optional

from src.deps.db_session import SessionDep
from src.core.security import CheckerPermisos
from src.services.ataud_service import AtaudService
from src.schemas.ataud import AtaudLeer, AtaudCrear, AtaudModificar
from src.schemas.stock import StockUpdate
from src.schemas.estado import EstadoUpdate
from src.services import bitacora_service

ataud_router = APIRouter()

@ataud_router.get("/", response_model=List[AtaudLeer], dependencies=[Depends(CheckerPermisos("ataudes:leer"))])
def listar_ataudes(
    db: SessionDep,
    modelo: Optional[str] = Query(None),
    color: Optional[str] = Query(None),
    stock: Optional[int] = Query(None, description="Ver ataudes con stock mayor o igual a este número"),
    activo: Optional[bool] = Query(None),
):
    return AtaudService.obtener_todos(db, modelo, color, stock, activo=activo)

@ataud_router.post("/", response_model=AtaudLeer, dependencies=[Depends(CheckerPermisos("ataudes:crear"))])
def crear_ataud(
    request: Request,
    ataud_in: AtaudCrear, 
    db: SessionDep,
    token: dict = Depends(CheckerPermisos("ataudes:crear")),
):
    resultado = AtaudService.crear(db, ataud_in)
    bitacora_service.registrar(
        db,
        usuario_id=int(token.get("sub")),
        usuario_nombre=token.get("username", ""),
        accion="crear",
        modulo="ataudes",
        detalle=f"Ataud '{resultado.modelo} {resultado.color}' creado",
        ip_address=request.client.host if request.client else None,
    )
    return resultado

@ataud_router.patch("/{ataud_id}", response_model=AtaudLeer, dependencies=[Depends(CheckerPermisos("ataudes:actualizar"))])
def modificar_ataud(
    request: Request,
    ataud_id: int, 
    ataud_in: AtaudModificar, 
    db: SessionDep,
    token: dict = Depends(CheckerPermisos("ataudes:actualizar")),
):
    resultado = AtaudService.actualizar(db, ataud_id, ataud_in)
    bitacora_service.registrar(
        db,
        usuario_id=int(token.get("sub")),
        usuario_nombre=token.get("username", ""),
        accion="actualizar",
        modulo="ataudes",
        detalle=f"Ataud #{ataud_id} actualizado",
        ip_address=request.client.host if request.client else None,
    )
    return resultado

@ataud_router.delete("/{ataud_id}", dependencies=[Depends(CheckerPermisos("ataudes:eliminar"))])
def eliminar_ataud(
    request: Request,
    ataud_id: int, 
    db: SessionDep,
    token: dict = Depends(CheckerPermisos("ataudes:eliminar")),
):
    resultado = AtaudService.eliminar(db, ataud_id)
    bitacora_service.registrar(
        db,
        usuario_id=int(token.get("sub")),
        usuario_nombre=token.get("username", ""),
        accion="eliminar",
        modulo="ataudes",
        detalle=f"Ataud #{ataud_id} eliminado",
        ip_address=request.client.host if request.client else None,
    )
    return resultado

@ataud_router.patch("/{ataud_id}/stock", response_model=AtaudLeer, dependencies=[Depends(CheckerPermisos("ataudes:actualizar_stock"))])
def actualizar_stock_ataud(
    request: Request,
    ataud_id: int, 
    stock_in: StockUpdate, 
    db: SessionDep,
    token: dict = Depends(CheckerPermisos("ataudes:actualizar_stock")),
):
    resultado = AtaudService.actualizar_stock(db, ataud_id, stock_in.cantidad)
    signo = "+" if stock_in.cantidad > 0 else ""
    bitacora_service.registrar(
        db,
        usuario_id=int(token.get("sub")),
        usuario_nombre=token.get("username", ""),
        accion="actualizar_stock",
        modulo="ataudes",
        detalle=f"Stock de ataud #{ataud_id} cambiado en {signo}{stock_in.cantidad} (nuevo: {resultado.stock})",
        ip_address=request.client.host if request.client else None,
    )
    return resultado

@ataud_router.patch("/{ataud_id}/status", response_model=AtaudLeer, dependencies=[Depends(CheckerPermisos("ataudes:actualizar"))])
def cambiar_estado_ataud(
    request: Request,
    ataud_id: int, datos: EstadoUpdate, db: SessionDep,
    token: dict = Depends(CheckerPermisos("ataudes:actualizar")),
):
    resultado = AtaudService.cambiar_estado(db, ataud_id, datos.activo)
    estado = "activado" if datos.activo else "desactivado"
    bitacora_service.registrar(
        db,
        usuario_id=int(token.get("sub")),
        usuario_nombre=token.get("username", ""),
        accion="cambiar_estado",
        modulo="ataudes",
        detalle=f"Ataud #{ataud_id} {estado}",
        ip_address=request.client.host if request.client else None,
    )
    return resultado
