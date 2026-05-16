from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional
from enum import Enum

class TipoAtaud(str, Enum):
    economico = "economico"
    vip = "vip"

class Ataud(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    modelo: str = Field(nullable=False, max_length=100, index=True)
    color: str = Field(nullable=False, max_length=50)
    stock: int = Field(default=0, nullable=False, ge=0)
    tipo: TipoAtaud = Field(nullable=False, index=True)

    servicios: List["Servicio"] = Relationship(back_populates="ataud")