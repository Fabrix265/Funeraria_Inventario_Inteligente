from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional, TYPE_CHECKING
from datetime import date
from enum import Enum
from decimal import Decimal

if TYPE_CHECKING:
    from src.models.user import User
    from src.models.ataud import Ataud
    from src.models.capilla import Capilla
    from src.models.fallecido import Fallecido
    from src.models.contratante import Contratante
    from src.models.vehiculo import Vehiculo

from src.models.servicio_vehiculo import ServicioVehiculo

class TipoPago(str, Enum):
    directo = "directo"
    seguro = "seguro"
    mixto = "mixto"

class Servicio(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    # FKs
    id_usuario: int = Field(foreign_key="user.id", nullable=False)
    id_ataud: Optional[int] = Field(default=None, foreign_key="ataud.id")
    id_capilla: int = Field(foreign_key="capilla.id", nullable=False)
    id_contratante: int = Field(foreign_key="contratante.id", nullable=False)
    id_fallecido: int = Field(foreign_key="fallecido.id", nullable=False, unique=True)
    
    # Datos
    direccion_velacion: str = Field(nullable=False, max_length=200)
    tipo_pago: TipoPago = Field(nullable=False, index=True)
    costo: Decimal = Field(default=0.0, decimal_places=2)
    arreglo_flora: bool = Field(default=False)
    fecha: date = Field(nullable=False, index=True)
    cantidad_cargadores: Optional[int] = Field(default=None)
    director_sepelio: bool = Field(default=False)

    # Relaciones
    usuario: "User" = Relationship(back_populates="servicios")
    
    ataud: Optional["Ataud"] = Relationship(
        back_populates="servicios",
        sa_relationship_kwargs={"lazy": "selectin"}
    )
    capilla: "Capilla" = Relationship(
        back_populates="servicios",
        sa_relationship_kwargs={"lazy": "selectin"}
    )
    contratante: "Contratante" = Relationship(
        back_populates="servicios",
        sa_relationship_kwargs={"lazy": "selectin"}
    )
    fallecido: "Fallecido" = Relationship(
        back_populates="servicio",
        sa_relationship_kwargs={"lazy": "selectin"}
    )
    
    vehiculos_asignados: List["ServicioVehiculo"] = Relationship(
        back_populates="servicio",
        sa_relationship_kwargs={"lazy": "selectin"}
    )