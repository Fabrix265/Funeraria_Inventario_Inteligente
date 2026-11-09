import asyncio
import logging
import os
import re
import threading
from datetime import date, datetime, timedelta
from typing import Optional

from fastapi import HTTPException
from sqlmodel import Session

from src.config.db import engine
from src.core.fechas import hoy_local
from src.services.bitacora_service import exportar_excel_dia
from src.services.drive_service import GoogleDriveService, CARPETA_BITACORA

logger = logging.getLogger(__name__)

DIAS_RETENIDOS = 30
FORMATO_NOMBRE = "%Y-%m-%d"

_lock = threading.Lock()


def nombre_archivo(dia: date) -> str:
    return f"{dia.strftime(FORMATO_NOMBRE)}.xlsx"


def _fecha_desde_nombre(nombre: str) -> Optional[date]:
    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}\.xlsx", nombre):
        return None
    try:
        return datetime.strptime(nombre, f"{FORMATO_NOMBRE}.xlsx").date()
    except ValueError:
        return None


def dias_esperados(hoy: date) -> list[date]:
    return [hoy - timedelta(days=dias) for dias in range(DIAS_RETENIDOS, 0, -1)]


def sincronizar(db: Session, hoy: Optional[date] = None) -> dict:
    if not _lock.acquire(blocking=False):
        return {"estado": "omitido", "motivo": "en_curso"}
    try:
        hoy = hoy or hoy_local()
        drive = GoogleDriveService(db)
        if not drive.verificar_estado()["autorizado"]:
            logger.warning("Archivo diario de la bitácora omitido: Google Drive no está autorizado")
            return {"estado": "omitido", "motivo": "no_autorizado"}
        if not drive.FOLDER_ID:
            logger.warning("Archivo diario de la bitácora omitido: falta GOOGLE_DRIVE_FOLDER_ID")
            return {"estado": "omitido", "motivo": "carpeta_no_configurada"}

        carpeta_id = drive.obtener_o_crear_carpeta(CARPETA_BITACORA)
        por_fecha = {}
        for archivo in drive.listar_contenido(carpeta_id, "archivos"):
            dia = _fecha_desde_nombre(archivo["name"])
            if dia is not None:
                por_fecha.setdefault(dia, []).append(archivo)

        creados = []
        eliminados = []
        total = sum(len(archivos) for archivos in por_fecha.values())
        for dia in dias_esperados(hoy):
            if dia in por_fecha:
                continue
            nombre = nombre_archivo(dia)
            contenido = exportar_excel_dia(db, dia)
            if drive.subir_archivo(contenido, nombre, CARPETA_BITACORA) is None:
                logger.error("No se pudo subir el archivo diario de la bitácora %s", nombre)
                continue
            creados.append(nombre)
            total += 1

        limite = hoy - timedelta(days=DIAS_RETENIDOS)
        for dia, archivos in por_fecha.items():
            if dia < limite or dia >= hoy:
                para_eliminar = archivos
            elif len(archivos) > 1:
                para_eliminar = sorted(
                    archivos,
                    key=lambda archivo: datetime.fromisoformat(
                        archivo["modifiedTime"].replace("Z", "+00:00")
                    ),
                    reverse=True,
                )[1:]
            else:
                continue
            for archivo in para_eliminar:
                if drive.eliminar_archivo(archivo["id"]):
                    eliminados.append(archivo["name"])
                    total -= 1
                else:
                    logger.error("No se pudo eliminar el archivo diario de la bitácora %s", archivo["name"])

        resumen = {"estado": "ok", "creados": creados, "eliminados": eliminados, "total": total}
        if creados or eliminados:
            logger.info("Archivo diario de la bitácora: %s", resumen)
        return resumen
    except Exception as error:
        logger.exception("Error al sincronizar el archivo diario de la bitácora")
        return {"estado": "error", "motivo": str(error)}
    finally:
        _lock.release()


def listar(db: Session) -> list[dict]:
    drive = GoogleDriveService(db)
    if not drive.verificar_estado()["autorizado"]:
        raise HTTPException(status_code=503, detail="Google Drive no está conectado. Autoriza la integración desde tu perfil.")
    if not drive.FOLDER_ID:
        raise HTTPException(status_code=503, detail="No hay una carpeta raíz configurada en Google Drive (GOOGLE_DRIVE_FOLDER_ID).")

    carpeta_id = drive.obtener_o_crear_carpeta(CARPETA_BITACORA)
    archivos = []
    for archivo in drive.listar_contenido(carpeta_id, "archivos"):
        dia = _fecha_desde_nombre(archivo["name"])
        if dia is None:
            continue
        archivos.append({
            "file_id": archivo["id"],
            "nombre": archivo["name"],
            "fecha": dia.isoformat(),
            "tamano": int(archivo.get("size", 0) or 0),
        })
    return sorted(archivos, key=lambda archivo: archivo["fecha"], reverse=True)


def descargar(db: Session, file_id: str) -> tuple[bytes, str]:
    archivo = next((archivo for archivo in listar(db) if archivo["file_id"] == file_id), None)
    if archivo is None:
        raise HTTPException(status_code=404, detail="Archivo diario de la bitácora no encontrado.")
    drive = GoogleDriveService(db)
    contenido = drive.descargar_archivo(file_id)
    if contenido is None:
        raise HTTPException(status_code=503, detail="No se pudo descargar el archivo diario de la bitácora desde Google Drive.")
    return contenido, archivo["nombre"]


def _ejecutar_con_sesion() -> None:
    with Session(engine) as db:
        sincronizar(db)


async def bucle_programado(intervalo_segundos: int) -> None:
    await asyncio.sleep(10)
    while True:
        try:
            await asyncio.to_thread(_ejecutar_con_sesion)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Error en el programador del archivo diario de la bitácora")
        await asyncio.sleep(intervalo_segundos)


def configuracion() -> tuple[bool, int]:
    activo = os.getenv("BITACORA_ARCHIVO_AUTO", "true").strip().lower() not in ("false", "0", "no")
    try:
        intervalo = int(os.getenv("BITACORA_ARCHIVO_INTERVALO_MIN", "60"))
    except ValueError:
        intervalo = 60
    return activo, max(5, intervalo) * 60
