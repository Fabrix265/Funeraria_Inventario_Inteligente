from typing import Optional
from pydantic import BaseModel


class DriveAuthUrlResponse(BaseModel):
    url: str


class DriveStatusResponse(BaseModel):
    autorizado: bool
    expira_en: Optional[str] = None
    motivo: Optional[str] = None


class DriveUploadResponse(BaseModel):
    file_id: str
    url: str
    filename: str
