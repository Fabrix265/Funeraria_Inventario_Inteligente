from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.servicio import Servicio

class Fallecido(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(nullable=False, max_length=100)
    dni_fallecido: str = Field(nullable=False, max_length=8, index=True)
    activo: bool = Field(default=True, index=True)

    servicio: Optional["Servicio"] = Relationship(back_populates="fallecido")