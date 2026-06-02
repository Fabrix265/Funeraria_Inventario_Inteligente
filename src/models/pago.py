from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class EstadoPago(str, Enum):
    pendiente = "pendiente"
    completado = "completado"
    fallido = "fallido"
    cancelado = "cancelado"

class Pago(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    id_servicio: int = Field(foreign_key="servicio.id")
    stripe_payment_intent_id: str         
    monto: int                         
    moneda: str = Field(default="pen")
    estado: EstadoPago = Field(default=EstadoPago.pendiente)
    descripcion: Optional[str] = None
    fecha_creacion: datetime = Field(default_factory=datetime.utcnow)
    fecha_actualizacion: Optional[datetime] = None