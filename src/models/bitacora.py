from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class Bitacora(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: Optional[int] = Field(default=None, foreign_key="user.id")
    usuario_nombre: str
    accion: str
    modulo: str
    detalle: Optional[str] = None
    ip_address: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
