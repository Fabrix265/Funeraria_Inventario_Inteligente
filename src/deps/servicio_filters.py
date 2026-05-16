from fastapi import Query
from typing import Optional
from datetime import date


def filtros_servicio(
    fecha: Optional[date] = Query(None, description="Filtrar por fecha del servicio (YYYY-MM-DD)"),
    nombre: Optional[str] = Query(None, description="Filtrar por nombre del contratante o fallecido"),
    dni: Optional[str] = Query(None, description="Filtrar por DNI del contratante o fallecido"),
    telefono: Optional[str] = Query(None, description="Filtrar por teléfono del contratante"),
):
    return {"fecha": fecha, "nombre": nombre, "dni": dni, "telefono": telefono}