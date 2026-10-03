from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field

ESTADOS_RESPALDO = ("en_proceso", "completado", "fallido")
TIPOS_RESPALDO = ("manual", "seguridad")


class Respaldo(SQLModel, table=True):
    __tablename__ = "respaldo"

    id: Optional[int] = Field(default=None, primary_key=True)
    etiqueta: str = Field(max_length=255)
    fecha: datetime = Field(default_factory=datetime.utcnow, index=True)

    nombre_archivo: str = Field(max_length=255)
    drive_file_id: str = Field(max_length=255)
    drive_manifesto_id: Optional[str] = Field(default=None, max_length=255)
    drive_folder_archivos_id: Optional[str] = Field(default=None, max_length=255)

    tamano_bytes: int = Field(default=0)
    cantidad_archivos: int = Field(default=0)
    sha256: Optional[str] = Field(default=None, max_length=64)

    estado: str = Field(default="en_proceso", max_length=20, index=True)
    mensaje_error: Optional[str] = Field(default=None)
    tipo: str = Field(default="manual", max_length=20)

    observacion: Optional[str] = Field(default=None, max_length=255)
    usuario_id: Optional[int] = Field(default=None)
    usuario_nombre: Optional[str] = Field(default=None, max_length=50)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class RespaldoConfig(SQLModel, table=True):
    __tablename__ = "respaldo_config"

    id: Optional[int] = Field(default=None, primary_key=True)
    frecuencia_dias: int = Field(default=1, ge=1, le=90)
    dias_advertencia: int = Field(default=2, ge=1, le=90)
    maximo_respaldos: int = Field(default=15, ge=2, le=200)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class TokenRestauracion(SQLModel, table=True):
    __tablename__ = "token_restauracion"

    id: Optional[int] = Field(default=None, primary_key=True)
    respaldo_id: int = Field(foreign_key="respaldo.id", index=True)
    usuario_id: Optional[int] = Field(default=None)
    token_hash: str = Field(max_length=64, unique=True, index=True)
    expira_en: datetime = Field(index=True)
    intentos: int = Field(default=0)
    usado_en: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
