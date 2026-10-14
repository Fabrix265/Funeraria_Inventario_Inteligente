from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import List, Optional
import re

COLOR_PATTERN = re.compile(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ]+(?:\s[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\-]+)*$")

class AtaudBase(BaseModel):
    modelo: str = Field(min_length=1, max_length=100)
    color: str = Field(min_length=1, max_length=50)
    stock: int = Field(ge=0)

    @field_validator("color")
    @classmethod
    def validar_color(cls, v: str) -> str:
        if not COLOR_PATTERN.match(v):
            raise ValueError("El color solo puede contener letras, espacios y guiones")
        return v

class AtaudCrear(AtaudBase):
    pass

class AtaudModificar(BaseModel):
    modelo: Optional[str] = Field(None, min_length=1, max_length=100)
    color: Optional[str] = Field(None, min_length=1, max_length=50)
    stock: Optional[int] = Field(None, ge=0)
    activo: Optional[bool] = None

    @field_validator("color")
    @classmethod
    def validar_color(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not COLOR_PATTERN.match(v):
            raise ValueError("El color solo puede contener letras, espacios y guiones")
        return v

class AtaudImagenLeer(BaseModel):
    id: int
    url: str
    model_config = ConfigDict(from_attributes=True)

class AtaudLeer(AtaudBase):
    id: int
    activo: bool
    imagenes: List[AtaudImagenLeer] = []
    model_config = ConfigDict(from_attributes=True)