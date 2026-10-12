from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

from src.models.servicio_archivo import TipoArchivo


class ServicioArchivoRead(BaseModel):
    id: int
    id_servicio: int
    tipo: TipoArchivo
    nombre_original: str
    drive_file_id: str
    drive_file_url: str
    mime_type: str
    subido_por: Optional[int] = None
    usuario_nombre: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ServicioArchivosResponse(BaseModel):
    archivos: list[ServicioArchivoRead]
