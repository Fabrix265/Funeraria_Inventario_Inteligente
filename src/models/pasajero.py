from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.servicio import Servicio

class Pasajero(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(nullable=False, max_length=100)
    dni_pasajero: str = Field(nullable=False, max_length=8)
    id_servicio: int = Field(foreign_key="servicio.id", nullable=False)

    servicio: "Servicio" = Relationship(back_populates="pasajeros")
