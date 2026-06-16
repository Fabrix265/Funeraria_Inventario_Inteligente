from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from src.models.pago import EstadoPago


class PagoCrear(BaseModel):
    id_servicio: int
    monto: int = Field(gt=0, description="Monto en centavos, ej: 10000 = S/100.00")
    moneda: str = "pen"
    descripcion: Optional[str] = None


class PagoLeer(BaseModel):
    id: int
    id_servicio: int
    stripe_payment_intent_id: str
    monto: int
    moneda: str
    estado: EstadoPago
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime] = None

    class Config:
        from_attributes = True


class PagoResponse(PagoLeer):
    client_secret: str


class PagoEstadoUpdate(BaseModel):
    estado: EstadoPago
    fecha_actualizacion: datetime