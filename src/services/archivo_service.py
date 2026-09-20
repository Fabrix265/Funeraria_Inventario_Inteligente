import re
import logging
from typing import Optional, List
from datetime import datetime

from sqlmodel import Session, select
from fastapi import HTTPException

from src.models.servicio import Servicio
from src.models.fallecido import Fallecido
from src.models.servicio_archivo import ServicioArchivo, TipoArchivo
from src.services.drive_service import GoogleDriveService

logger = logging.getLogger(__name__)

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "image/png",
    "image/jpeg",
}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def _sanitizar_nombre(nombre: str) -> str:
    nombre = re.sub(r"[^\w\s\-]", "", nombre)
    nombre = re.sub(r"\s+", "_", nombre.strip())
    return nombre[:80] if nombre else "sin_nombre"


def _obtener_carpeta_servicio(servicio: Servicio) -> str:
    nombre = _sanitizar_nombre(servicio.fallecido.nombre)
    dni = servicio.fallecido.dni_fallecido
    return f"{nombre}_{dni}"


def _generar_nombre_archivo(tipo: TipoArchivo, servicio: Servicio, original: str) -> str:
    base = _sanitizar_nombre(
        f"{tipo.value}_{servicio.fallecido.nombre}_{servicio.fallecido.dni_fallecido}"
    )
    ext = original.rsplit(".", 1)[-1].lower() if "." in original else ""
    return f"{base}.{ext}" if ext else base


def listar_archivos(db: Session, servicio_id: int) -> List[ServicioArchivo]:
    servicio = db.get(Servicio, servicio_id)
    if not servicio:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")

    stmt = select(ServicioArchivo).where(ServicioArchivo.id_servicio == servicio_id)
    return list(db.exec(stmt).all())


def subir_archivo(
    db: Session,
    servicio_id: int,
    tipo: TipoArchivo,
    file_bytes: bytes,
    filename: str,
    mime_type: str,
    usuario_id: int,
    usuario_nombre: str,
) -> ServicioArchivo:
    servicio = db.get(Servicio, servicio_id)
    if not servicio:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")

    if mime_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de archivo no permitido: {mime_type}. Use PDF, PNG o JPG.",
        )

    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="El archivo excede el tamaño máximo de 10 MB.",
        )

    existente = db.exec(
        select(ServicioArchivo).where(
            ServicioArchivo.id_servicio == servicio_id,
            ServicioArchivo.tipo == tipo,
        )
    ).first()

    if existente:
        raise HTTPException(
            status_code=400,
            detail=f"Ya existe un archivo de tipo '{tipo.value}' para este servicio. Use la opción de reemplazar.",
        )

    drive = GoogleDriveService(db)
    carpeta_nombre = _obtener_carpeta_servicio(servicio)
    nombre_archivo = _generar_nombre_archivo(tipo, servicio, filename)
    resultado = drive.subir_archivo(file_bytes, nombre_archivo, carpeta_nombre)

    if not resultado:
        raise HTTPException(
            status_code=500,
            detail="No se pudo subir el archivo a Google Drive.",
        )

    archivo = ServicioArchivo(
        id_servicio=servicio_id,
        tipo=tipo,
        nombre_original=nombre_archivo,
        drive_file_id=resultado["file_id"],
        drive_file_url=resultado["url"],
        mime_type=mime_type,
        subido_por=usuario_id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(archivo)
    db.commit()
    db.refresh(archivo)
    return archivo


def descargar_archivo(
    db: Session,
    archivo_id: int,
) -> tuple[bytes, str, str]:
    archivo = db.get(ServicioArchivo, archivo_id)
    if not archivo:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")

    drive = GoogleDriveService(db)
    file_bytes = drive.descargar_archivo(archivo.drive_file_id)

    if not file_bytes:
        raise HTTPException(
            status_code=500,
            detail="No se pudo descargar el archivo de Google Drive.",
        )

    return file_bytes, archivo.mime_type, archivo.nombre_original


def reemplazar_archivo(
    db: Session,
    archivo_id: int,
    file_bytes: bytes,
    filename: str,
    mime_type: str,
    usuario_id: int,
) -> ServicioArchivo:
    archivo = db.get(ServicioArchivo, archivo_id)
    if not archivo:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")

    if mime_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de archivo no permitido: {mime_type}. Use PDF, PNG o JPG.",
        )

    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="El archivo excede el tamaño máximo de 10 MB.",
        )

    servicio = db.get(Servicio, archivo.id_servicio)
    if not servicio:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")

    nombre_archivo = _generar_nombre_archivo(archivo.tipo, servicio, filename)

    drive = GoogleDriveService(db)
    resultado = drive.reemplazar_archivo(archivo.drive_file_id, file_bytes, nombre_archivo)

    if not resultado:
        raise HTTPException(
            status_code=500,
            detail="No se pudo reemplazar el archivo en Google Drive.",
        )

    archivo.nombre_original = nombre_archivo
    archivo.mime_type = mime_type
    archivo.drive_file_url = resultado["url"]
    archivo.updated_at = datetime.utcnow()
    db.add(archivo)
    db.commit()
    db.refresh(archivo)
    return archivo


def eliminar_archivo(
    db: Session,
    archivo_id: int,
) -> dict:
    archivo = db.get(ServicioArchivo, archivo_id)
    if not archivo:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")

    drive = GoogleDriveService(db)
    exito = drive.eliminar_archivo(archivo.drive_file_id)

    if not exito:
        raise HTTPException(
            status_code=500,
            detail="No se pudo eliminar el archivo de Google Drive.",
        )

    db.delete(archivo)
    db.commit()
    return {"message": "Archivo eliminado correctamente"}
