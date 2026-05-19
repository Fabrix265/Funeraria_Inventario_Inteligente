from sqlmodel import SQLModel, Field, Relationship
from typing import Optional

class ServicioVehiculo(SQLModel, table=True):
    __tablename__ = "servicio_vehiculo"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    id_servicio: int = Field(foreign_key="servicio.id", nullable=False)
    id_vehiculo: int = Field(foreign_key="vehiculo.id", nullable=False)
    
    servicio: "Servicio" = Relationship(back_populates="vehiculos_asignados")
    vehiculo: "Vehiculo" = Relationship(
        back_populates="servicios",
        sa_relationship_kwargs={"lazy": "selectin"}
    )