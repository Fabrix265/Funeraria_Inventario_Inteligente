from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional

class Capilla(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    modelo: str = Field(nullable=False, max_length=100, index=True)
    stock: int = Field(default=0, nullable=False) 

    servicios: List["Servicio"] = Relationship(back_populates="capilla")