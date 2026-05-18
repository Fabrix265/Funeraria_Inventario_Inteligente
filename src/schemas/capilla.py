from pydantic import BaseModel, ConfigDict, Field

class CapillaBase(BaseModel):
    modelo: str = Field(min_length=1, max_length=100)
    stock: int = Field(ge=0, description="Cantidad de capillas disponibles")

class CapillaCrear(CapillaBase):
    pass

class CapillaLeer(CapillaBase):
    id: int
    model_config = ConfigDict(from_attributes=True)