from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class BitacoraRead(BaseModel):
    id: int
    usuario_id: Optional[int]
    usuario_nombre: str
    accion: str
    modulo: str
    detalle: Optional[str]
    ip_address: Optional[str]
    created_at: datetime


class BitacoraListResponse(BaseModel):
    items: list[BitacoraRead]
    total: int
    pagina: int
    total_paginas: int
