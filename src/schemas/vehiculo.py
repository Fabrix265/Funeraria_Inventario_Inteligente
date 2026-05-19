from pydantic import BaseModel, ConfigDict
from src.models.vehiculo import TipoVehiculo

class VehiculoBase(BaseModel):
    tipo: TipoVehiculo

class VehiculoCrear(VehiculoBase):
    pass

class VehiculoLeer(VehiculoBase):
    id: int
    model_config = ConfigDict(from_attributes=True)