from datetime import datetime
from typing import Optional, TYPE_CHECKING
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from src.models.servicio import Servicio
    from src.models.user import User


class TipoArchivo(str, Enum):
    certificado = "certificado"
    acta = "acta"
    dni_contratante = "dni_contratante"
    dni_fallecido = "dni_fallecido"


class ServicioArchivo(SQLModel, table=True):
    __tablename__ = "servicio_archivo"

    id: Optional[int] = Field(default=None, primary_key=True)
    id_servicio: int = Field(foreign_key="servicio.id", nullable=False, index=True)
    tipo: TipoArchivo = Field(nullable=False)
    nombre_original: str = Field(nullable=False, max_length=255)
    drive_file_id: str = Field(nullable=False, max_length=255)
    drive_file_url: str = Field(nullable=False, max_length=500)
    mime_type: str = Field(nullable=False, max_length=100)
    subido_por: Optional[int] = Field(default=None, foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    servicio: "Servicio" = Relationship(
        back_populates="archivos",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    usuario: Optional["User"] = Relationship(
        sa_relationship_kwargs={"lazy": "selectin"},
    )
