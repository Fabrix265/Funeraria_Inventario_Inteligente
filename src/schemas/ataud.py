from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from src.models.ataud import TipoAtaud

class AtaudBase(BaseModel):
    modelo: str = Field(min_length=1, max_length=100)
    color: str = Field(min_length=1, max_length=50)
    tipo: TipoAtaud
    stock: int = Field(ge=0)

class AtaudCrear(AtaudBase):
    pass

class AtaudModificar(BaseModel):
    modelo: Optional[str] = Field(None, min_length=1, max_length=100)
    color: Optional[str] = Field(None, min_length=1, max_length=50)
    tipo: Optional[TipoAtaud] = None
    stock: Optional[int] = Field(None, ge=0)

class AtaudLeer(AtaudBase):
    id: int
    model_config = ConfigDict(from_attributes=True)