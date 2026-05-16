from pydantic import BaseModel, ConfigDict, Field

class ContratanteBase(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    dni: str = Field(pattern=r"^\d{8}$")
    telefono: str = Field(pattern=r"^\d{9}$")

class ContratanteCrear(ContratanteBase):
    pass

class ContratanteLeer(ContratanteBase):
    id: int
    model_config = ConfigDict(from_attributes=True)