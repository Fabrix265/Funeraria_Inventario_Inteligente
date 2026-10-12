from pydantic import BaseModel, ConfigDict
from typing import List
from src.models.vehiculo import TipoVehiculo

class VehiculoBase(BaseModel):
    tipo: TipoVehiculo

class VehiculoCrear(VehiculoBase):
    pass

class VehiculoImagenLeer(BaseModel):
    id: int
    url: str
    model_config = ConfigDict(from_attributes=True)

class VehiculoLeer(VehiculoBase):
    id: int
    activo: bool
    imagenes: List[VehiculoImagenLeer] = [] 
    model_config = ConfigDict(from_attributes=True)