from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.servicio import Servicio

class Contratante(SQLModel,table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(nullable=False, max_length=100)
    dni: str = Field(nullable=False, max_length=8, unique=True, index=True)
    telefono: str = Field(nullable=False, max_length=9)
    activo: bool = Field(default=True, index=True)
    
    servicios: List["Servicio"] = Relationship(back_populates="contratante")