from datetime import datetime
from typing import Optional
from sqlmodel import Session, select, func
from src.models.bitacora import Bitacora


def registrar(
    db: Session,
    *,
    usuario_id: Optional[int],
    usuario_nombre: str,
    accion: str,
    modulo: str,
    detalle: Optional[str] = None,
    ip_address: Optional[str] = None,
) -> Bitacora:
    entrada = Bitacora(
        usuario_id=usuario_id,
        usuario_nombre=usuario_nombre,
        accion=accion,
        modulo=modulo,
        detalle=detalle,
        ip_address=ip_address,
    )
    db.add(entrada)
    db.commit()
    db.refresh(entrada)
    return entrada


def listar(
    db: Session,
    *,
    fecha_inicio: Optional[str] = None,
    fecha_fin: Optional[str] = None,
    usuario_id: Optional[int] = None,
    accion: Optional[str] = None,
    modulo: Optional[str] = None,
    offset: int = 0,
    limit: int = 20,
):
    query = select(Bitacora)
    count_query = select(func.count(Bitacora.id))

    if fecha_inicio:
        fecha_dt = datetime.fromisoformat(fecha_inicio)
        query = query.where(Bitacora.created_at >= fecha_dt)
        count_query = count_query.where(Bitacora.created_at >= fecha_dt)
    if fecha_fin:
        fecha_dt = datetime.fromisoformat(fecha_fin)
        query = query.where(Bitacora.created_at <= fecha_dt)
        count_query = count_query.where(Bitacora.created_at <= fecha_dt)
    if usuario_id is not None:
        query = query.where(Bitacora.usuario_id == usuario_id)
        count_query = count_query.where(Bitacora.usuario_id == usuario_id)
    if accion:
        query = query.where(Bitacora.accion == accion)
        count_query = count_query.where(Bitacora.accion == accion)
    if modulo:
        query = query.where(Bitacora.modulo == modulo)
        count_query = count_query.where(Bitacora.modulo == modulo)

    total = db.exec(count_query).one()
    total_paginas = (total + limit - 1) // limit if limit > 0 else 1

    items = db.exec(
        query.order_by(Bitacora.created_at.desc()).offset(offset).limit(limit)
    ).all()

    return {
        "items": items,
        "total": total,
        "pagina": (offset // limit) + 1,
        "total_paginas": total_paginas,
    }


def obtener_por_id(db: Session, bitacora_id: int) -> Optional[Bitacora]:
    return db.get(Bitacora, bitacora_id)
