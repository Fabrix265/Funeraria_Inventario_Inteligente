from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional

class AtaudBase(BaseModel):
    modelo: str = Field(min_length=1, max_length=100)
    color: str = Field(min_length=1, max_length=50)
    stock: int = Field(ge=0)

class AtaudCrear(AtaudBase):
    pass

class AtaudModificar(BaseModel):
    modelo: Optional[str] = Field(None, min_length=1, max_length=100)
    color: Optional[str] = Field(None, min_length=1, max_length=50)
    stock: Optional[int] = Field(None, ge=0)
    activo: Optional[bool] = None

class AtaudImagenLeer(BaseModel):
    id: int
    url: str
    model_config = ConfigDict(from_attributes=True)

class AtaudLeer(AtaudBase):
    id: int
    activo: bool
    imagenes: List[AtaudImagenLeer] = []
    model_config = ConfigDict(from_attributes=True)