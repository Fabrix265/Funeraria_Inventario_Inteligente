from sqlmodel import SQLModel, Field, Relationship
from typing import Optional

class Fallecido(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(nullable=False, max_length=100)
    dni: str = Field(nullable=False, max_length=8, unique=True, index=True)

    servicio: Optional["Servicio"] = Relationship(back_populates="fallecido")