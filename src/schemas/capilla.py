from pydantic import BaseModel, ConfigDict, Field
from typing import List

class CapillaBase(BaseModel):
    modelo: str = Field(min_length=1, max_length=100)
    stock: int = Field(ge=0, description="Cantidad de capillas disponibles")

class CapillaCrear(CapillaBase):
    pass

class CapillaImagenLeer(BaseModel):
    id: int
    url: str
    model_config = ConfigDict(from_attributes=True)

class CapillaLeer(CapillaBase):
    id: int
    activo: bool
    imagenes: List[CapillaImagenLeer] = []
    model_config = ConfigDict(from_attributes=True)