from datetime import datetime
from typing import Optional
from io import BytesIO
from sqlmodel import Session, select, func
from openpyxl import Workbook
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


def _aplicar_filtros(
    query,
    *,
    fecha_inicio: Optional[str] = None,
    fecha_fin: Optional[str] = None,
    usuario_id: Optional[int] = None,
    accion: Optional[str] = None,
    modulo: Optional[str] = None,
):
    if fecha_inicio:
        query = query.where(Bitacora.created_at >= datetime.fromisoformat(fecha_inicio))
    if fecha_fin:
        query = query.where(Bitacora.created_at <= datetime.fromisoformat(fecha_fin))
    if usuario_id is not None:
        query = query.where(Bitacora.usuario_id == usuario_id)
    if accion:
        query = query.where(Bitacora.accion == accion)
    if modulo:
        query = query.where(Bitacora.modulo == modulo)
    return query


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
    filtros = dict(fecha_inicio=fecha_inicio, fecha_fin=fecha_fin, usuario_id=usuario_id, accion=accion, modulo=modulo)

    query = _aplicar_filtros(select(Bitacora), **filtros)
    count_query = _aplicar_filtros(select(func.count(Bitacora.id)), **filtros)

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


def exportar_excel(
    db: Session,
    *,
    fecha_inicio: Optional[str] = None,
    fecha_fin: Optional[str] = None,
    usuario_id: Optional[int] = None,
    accion: Optional[str] = None,
    modulo: Optional[str] = None,
) -> bytes:
    query = _aplicar_filtros(
        select(Bitacora),
        fecha_inicio=fecha_inicio, fecha_fin=fecha_fin,
        usuario_id=usuario_id, accion=accion, modulo=modulo,
    )
    registros = db.exec(query.order_by(Bitacora.created_at.desc())).all()

    wb = Workbook()
    ws = wb.active
    ws.title = "Bitacora"
    ws.append(["ID", "Fecha", "Usuario", "Acción", "Módulo", "Detalle", "IP"])

    for r in registros:
        ws.append([
            r.id,
            r.created_at.strftime("%d/%m/%Y %H:%M") if r.created_at else "",
            r.usuario_nombre,
            r.accion,
            r.modulo,
            r.detalle or "",
            r.ip_address or "",
        ])

    for columna in ws.columns:
        largo = max((len(str(c.value)) for c in columna if c.value is not None), default=10)
        ws.column_dimensions[columna[0].column_letter].width = min(largo + 2, 50)

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()
