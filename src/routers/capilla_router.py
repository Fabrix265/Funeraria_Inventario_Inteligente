from fastapi import APIRouter, Depends, Query, Request, status, UploadFile, File
from typing import List, Optional

from src.deps.db_session import SessionDep
from src.core.security import CheckerPermisos
from src.services.capilla_service import CapillaService
from src.schemas.capilla import CapillaLeer, CapillaCrear
from src.schemas.stock import StockUpdate
from src.schemas.estado import EstadoUpdate
from src.services import bitacora_service

capilla_router = APIRouter()

@capilla_router.get("/", response_model=List[CapillaLeer], dependencies=[Depends(CheckerPermisos("capillas:leer"))])
def listar_capillas(
    db: SessionDep,
    modelo: Optional[str] = Query(None, description="Filtrar capillas por nombre de modelo"),
    activo: Optional[bool] = Query(None),
):
    return CapillaService.obtener_todas(db, modelo, activo=activo)

@capilla_router.post("/", response_model=CapillaLeer, status_code=status.HTTP_201_CREATED, dependencies=[Depends(CheckerPermisos("capillas:crear"))])
def crear_capilla(
    request: Request,
    capilla_in: CapillaCrear,
    db: SessionDep,
    token: dict = Depends(CheckerPermisos("capillas:crear")),
):
    resultado = CapillaService.crear(db, capilla_in)
    bitacora_service.registrar(
        db,
        usuario_id=int(token.get("sub")),
        usuario_nombre=token.get("username", ""),
        accion="crear",
        modulo="capillas",
        detalle=f"Capilla '{resultado.modelo}' creada",
        ip_address=request.client.host if request.client else None,
    )
    return resultado

@capilla_router.put("/{capilla_id}", response_model=CapillaLeer, dependencies=[Depends(CheckerPermisos("capillas:actualizar"))])
def actualizar_capilla(
    request: Request,
    capilla_id: int,
    capilla_in: CapillaCrear,
    db: SessionDep,
    token: dict = Depends(CheckerPermisos("capillas:actualizar")),
):
    resultado = CapillaService.actualizar(db, capilla_id, capilla_in)
    bitacora_service.registrar(
        db,
        usuario_id=int(token.get("sub")),
        usuario_nombre=token.get("username", ""),
        accion="actualizar",
        modulo="capillas",
        detalle=f"Capilla #{capilla_id} actualizada",
        ip_address=request.client.host if request.client else None,
    )
    return resultado

@capilla_router.delete("/{capilla_id}", dependencies=[Depends(CheckerPermisos("capillas:eliminar"))])
def eliminar_capilla(
    request: Request,
    capilla_id: int,
    db: SessionDep,
    token: dict = Depends(CheckerPermisos("capillas:eliminar")),
):
    resultado = CapillaService.eliminar(db, capilla_id)
    bitacora_service.registrar(
        db,
        usuario_id=int(token.get("sub")),
        usuario_nombre=token.get("username", ""),
        accion="eliminar",
        modulo="capillas",
        detalle=f"Capilla #{capilla_id} eliminada",
        ip_address=request.client.host if request.client else None,
    )
    return resultado

@capilla_router.patch("/{capilla_id}/stock", response_model=CapillaLeer, dependencies=[Depends(CheckerPermisos("capillas:actualizar"))])
def actualizar_stock_capilla(
    request: Request,
    capilla_id: int,
    stock_in: StockUpdate,
    db: SessionDep,
    token: dict = Depends(CheckerPermisos("capillas:actualizar")),
):
    resultado = CapillaService.actualizar_stock(db, capilla_id, stock_in.cantidad)
    signo = "+" if stock_in.cantidad > 0 else ""
    bitacora_service.registrar(
        db,
        usuario_id=int(token.get("sub")),
        usuario_nombre=token.get("username", ""),
        accion="actualizar_stock",
        modulo="capillas",
        detalle=f"Stock de capilla #{capilla_id} cambiado en {signo}{stock_in.cantidad} (nuevo: {resultado.stock})",
        ip_address=request.client.host if request.client else None,
    )
    return resultado

@capilla_router.patch("/{capilla_id}/status", response_model=CapillaLeer, dependencies=[Depends(CheckerPermisos("capillas:actualizar"))])
def cambiar_estado_capilla(
    request: Request,
    capilla_id: int, datos: EstadoUpdate, db: SessionDep,
    token: dict = Depends(CheckerPermisos("capillas:actualizar")),
):
    resultado = CapillaService.cambiar_estado(db, capilla_id, datos.activo)
    estado = "activada" if datos.activo else "desactivada"
    bitacora_service.registrar(
        db,
        usuario_id=int(token.get("sub")),
        usuario_nombre=token.get("username", ""),
        accion="cambiar_estado",
        modulo="capillas",
        detalle=f"Capilla #{capilla_id} {estado}",
        ip_address=request.client.host if request.client else None,
    )
    return resultado

@capilla_router.post("/{capilla_id}/imagenes", response_model=CapillaLeer, dependencies=[Depends(CheckerPermisos("capillas:actualizar"))])
def agregar_imagen_capilla(
    request: Request,
    capilla_id: int,
    imagen: UploadFile = File(...),
    db: SessionDep = None,
    token: dict = Depends(CheckerPermisos("capillas:actualizar")),
):
    resultado = CapillaService.agregar_imagen(db, capilla_id, imagen)
    bitacora_service.registrar(
        db,
        usuario_id=int(token.get("sub")),
        usuario_nombre=token.get("username", ""),
        accion="agregar_imagen",
        modulo="capillas",
        detalle=f"Imagen agregada a capilla #{capilla_id}",
        ip_address=request.client.host if request.client else None,
    )
    return resultado


@capilla_router.delete("/{capilla_id}/imagenes/{imagen_id}", response_model=CapillaLeer, dependencies=[Depends(CheckerPermisos("capillas:actualizar"))])
def eliminar_imagen_capilla(
    request: Request,
    capilla_id: int,
    imagen_id: int,
    db: SessionDep,
    token: dict = Depends(CheckerPermisos("capillas:actualizar")),
):
    resultado = CapillaService.eliminar_imagen(db, capilla_id, imagen_id)
    bitacora_service.registrar(
        db,
        usuario_id=int(token.get("sub")),
        usuario_nombre=token.get("username", ""),
        accion="eliminar_imagen",
        modulo="capillas",
        detalle=f"Imagen #{imagen_id} eliminada de capilla #{capilla_id}",
        ip_address=request.client.host if request.client else None,
    )
    return resultado