from pydantic import BaseModel, ConfigDict, Field

class FallecidoBase(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    dni: str = Field(pattern=r"^\d{8}$")

class FallecidoCrear(FallecidoBase):
    pass

class FallecidoLeer(FallecidoBase):
    id: int
    model_config = ConfigDict(from_attributes=True)