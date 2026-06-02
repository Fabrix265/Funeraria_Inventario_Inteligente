from pydantic import BaseModel, ConfigDict, Field

class PasajeroBase(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    dni_pasajero: str = Field(pattern=r"^\d{8}$")

class PasajeroCrear(PasajeroBase):
    pass

class PasajeroLeer(PasajeroBase):
    id: int
    id_servicio: int
    model_config = ConfigDict(from_attributes=True)
