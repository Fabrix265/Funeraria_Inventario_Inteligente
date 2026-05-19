from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional

class Contratante(SQLModel,table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(nullable=False, max_length=100)
    dni: str = Field(nullable=False, max_length=8, unique=True, index=True)
    telefono: str = Field(nullable=False, max_length=9)
    
    servicios: List["Servicio"] = Relationship(back_populates="contratante")