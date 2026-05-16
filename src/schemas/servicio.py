from pydantic import BaseModel, Field, ConfigDict, field_serializer, field_validator
from typing import Any, List, Optional
from datetime import date
from decimal import Decimal

from src.models.servicio import TipoPago
from src.schemas.fallecido import FallecidoCrear
from src.schemas.contratante import ContratanteCrear

class ServicioBase(BaseModel):
    id_ataud: Optional[int] = None
    id_capilla: int
    direccion_velacion: str
    tipo_pago: TipoPago
    costo: Decimal = Field(ge=0, description="Costo total del servicio")
    arreglo_flora: bool = False
    fecha: date = Field(default_factory=date.today)
    cantidad_cargadores: Optional[int] = Field(default=None) 
    director_sepelio: bool = False

    @field_validator('cantidad_cargadores')
    @classmethod
    def validar_cargadores(cls, v: Any):
        if v is not None and v not in [4, 6]:
            raise ValueError('La cantidad de cargadores debe ser 4, 6 o null')
        return v

class ServicioCrear(ServicioBase):
    fallecido: FallecidoCrear 
    contratante: ContratanteCrear
    ids_vehiculos: List[int] = []

class ServicioEditar(BaseModel):
    id_ataud: Optional[int] = None
    id_capilla: Optional[int] = None
    direccion_velacion: Optional[str] = None
    tipo_pago: Optional[TipoPago] = None
    costo: Optional[Decimal] = None
    arreglo_flora: Optional[bool] = None
    fecha: Optional[date] = None
    cantidad_cargadores: Optional[int] = None
    director_sepelio: Optional[bool] = None
    fallecido: Optional[FallecidoCrear] = None
    contratante: Optional[ContratanteCrear] = None
    ids_vehiculos: Optional[List[int]] = None

class ServicioLeerCompleto(BaseModel):
    id: int
    id_usuario: int
    direccion_velacion: str
    tipo_pago: str
    costo: Decimal
    arreglo_flora: bool
    fecha: date
    cantidad_cargadores: Optional[int] = None
    director_sepelio: bool
    
    fallecido: Any 
    contratante: Any
    ataud: Optional[Any] = None
    capilla: Any
    vehiculos_asignados: List[Any] = [] 

    @field_serializer('vehiculos_asignados')
    def serializar_vehiculos(self, v_list: List):
        if not v_list: return []
        return [item.vehiculo for item in v_list if hasattr(item, 'vehiculo')]

    model_config = ConfigDict(from_attributes=True)

class ServicioPaginado(BaseModel):
    total: int
    offset: int
    limit: int
    data: List[ServicioLeerCompleto]