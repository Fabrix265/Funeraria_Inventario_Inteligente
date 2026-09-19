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
    activo: bool = Field(default=True, index=True)
    
    servicios: List["ServicioVehiculo"] = Relationship(back_populates="vehiculo")
    imagenes: List["VehiculoImagen"] = Relationship(
        back_populates="vehiculo",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )

class VehiculoImagen(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    vehiculo_id: int = Field(foreign_key="vehiculo.id", nullable=False)
    url: str = Field(nullable=False)
    storage_path: str = Field(nullable=False)

    vehiculo: Optional[Vehiculo] = Relationship(back_populates="imagenes")