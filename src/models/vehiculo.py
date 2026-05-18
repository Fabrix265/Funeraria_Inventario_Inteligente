from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional
from enum import Enum

class TipoVehiculo(str, Enum):
    porta_ataud = "porta_ataud"
    porta_flores = "porta_flores"
    mixto = "mixto"
    auto = "auto"
    microbus = "microbus"

class Vehiculo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tipo: TipoVehiculo = Field(nullable=False, index=True)
    
    servicios: List["ServicioVehiculo"] = Relationship(back_populates="vehiculo")