import hashlib
import json
import logging
import os
import re
import secrets
import tempfile
import time
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Tuple

from fastapi import HTTPException
from sqlalchemy import text
from sqlmodel import Session, select, func

from src.config.db import engine, POSTGRES_DB
from src.core.lifespan import inicializar_base_de_datos
from src.models.respaldo import Respaldo, RespaldoConfig, TokenRestauracion
from src.models.servicio_archivo import ServicioArchivo
from src.models.user import User
from src.schemas.respaldo import RespaldoLeer, RespaldoEstadoLeer
from src.services import backup_jobs, bitacora_service, pg_service
from src.services.archivo_service import obtener_carpeta_servicio
from src.services.drive_service import (
    GoogleDriveService,
    CARPETA_SERVICIOS,
    CARPETA_BACKUPS,
    CARPETA_BASE_DATOS,
    CARPETA_SNAPSHOTS,
)

logger = logging.getLogger(__name__)

PASOS_RESPALDO = [
    "Verificando el entorno",
    "Volcando la base de datos",
    "Subiendo el archivo .sql",
    "Copiando los documentos de servicios",
    "Escribiendo el manifiesto",
    "Replicando el historico de respaldos .sql",
    "Registrando el respaldo",
]

PASOS_RESTAURACION = [
    "Verificando el archivo respaldado",
    "Generando un respaldo de seguridad",
    "Restaurando la base de datos",
    "Restaurando los documentos de servicios",
    "Reconectando y verificando el sistema",
]

PASOS_RECUPERAR = [
    "Verificando los documentos respaldados",
    "Restaurando los documentos faltantes",
    "Registrando el resultado",
]


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------

def directorio_trabajo() -> Path:
    base = os.getenv("BACKUP_TEMP_DIR")
    ruta = Path(base) if base else Path(tempfile.gettempdir()) / "funeraria-respaldos"
    ruta.mkdir(parents=True, exist_ok=True)
    _podar(ruta)
    return ruta


def _podar(ruta: Path, dias: int = 30) -> None:
    """Borra los .sql locales de más de 30 días para no llenar el disco."""
    limite = time.time() - dias * 86400
    for archivo in ruta.glob("*.sql"):
        try:
            if archivo.stat().st_mtime < limite:
                archivo.unlink()
        except OSError:
            pass


def _sha256_de(ruta: Path) -> str:
    resumen = hashlib.sha256()
    with open(ruta, "rb") as file:
        for bloque in iter(lambda: file.read(65536), b""):
            resumen.update(bloque)
    return resumen.hexdigest()


def _marca() -> str:
    return datetime.utcnow().strftime("%Y%m%d_%H%M%S")


def _sanitizar(valor: str) -> str:
    limpio = re.sub(r"[^\w\-]+", "_", valor or "").strip("_")
    return limpio or "base_datos"


def formatear_tamano(bytees: int) -> str:
    if bytees < 1024:
        return f"{bytees} B"
    if bytees < 1024 * 1024:
        return f"{bytees / 1024:.1f} KB"
    return f"{bytees / (1024 * 1024):.1f} MB"


def a_respaldo_leer(respaldo: Respaldo) -> RespaldoLeer:
    item = RespaldoLeer.model_validate(respaldo)
    item.drive_file_url = (
        f"https://drive.google.com/uc?id={respaldo.drive_file_id}"
        if respaldo.drive_file_id
        else None
    )
    return item


def _guardar(db: Session, respaldo: Respaldo) -> None:
    respaldo.updated_at = datetime.utcnow()
    db.add(respaldo)
    db.commit()
    db.refresh(respaldo)


# ---------------------------------------------------------------------------
# Consultas
# ---------------------------------------------------------------------------

def obtener_config(db: Session) -> RespaldoConfig:
    config = db.exec(select(RespaldoConfig)).first()
    if not config:
        config = RespaldoConfig()
        db.add(config)
        db.commit()
        db.refresh(config)
    return config


def actualizar_config(db: Session, datos: dict) -> RespaldoConfig:
    config = obtener_config(db)
    for campo, valor in datos.items():
        setattr(config, campo, valor)
    config.updated_at = datetime.utcnow()
    db.add(config)
    db.commit()
    db.refresh(config)
    return config


def descargar(db: Session, respaldo_id: int) -> Tuple[bytes, str]:
    respaldo = obtener(db, respaldo_id)
    if respaldo.estado != "completado":
        raise HTTPException(
            status_code=400,
            detail="Ese respaldo no se puede descargar porque no se completó.",
        )
    datos = GoogleDriveService(db).descargar_archivo(respaldo.drive_file_id)
    if not datos:
        raise HTTPException(
            status_code=500,
            detail="No se pudo descargar el archivo desde Google Drive.",
        )
    return datos, respaldo.nombre_archivo


def _borrar_tokens(db: Session, respaldo_ids) -> int:
    """Quita los códigos de confirmación de los respaldos que van a borrarse.

    La tabla token_restauracion apunta a respaldo.id y bloquearía el DELETE.
    """
    ids = [i for i in respaldo_ids if i]
    if not ids:
        return 0
    filas = list(
        db.exec(
            select(TokenRestauracion).where(TokenRestauracion.respaldo_id.in_(ids))
        ).all()
    )
    for fila in filas:
        db.delete(fila)
    if filas:
        # Se fuerza el DELETE ahora: sin esto, el orden del mismo flush no
        # está garantizado y 'respaldo' se borraría antes que sus códigos.
        db.flush()
    return len(filas)


def _quitar_de_drive(db: Session, respaldo: Respaldo) -> bool:
    """Borra de Drive el .sql, su manifiesto y la carpeta de documentos.

    Devuelve False si no se pudo borrar el .sql principal; el resto se hace
    "best effort" porque no invalidan la operación.
    """
    drive = GoogleDriveService(db)
    ok = True

    if respaldo.drive_file_id and not drive.eliminar_archivo(respaldo.drive_file_id):
        logger.error("No se pudo borrar de Drive el archivo %s", respaldo.nombre_archivo)
        ok = False

    if respaldo.drive_manifesto_id and not drive.eliminar_archivo(respaldo.drive_manifesto_id):
        logger.warning("No se pudo borrar de Drive el manifiesto de %s", respaldo.etiqueta)

    if respaldo.drive_folder_archivos_id and not drive.eliminar_carpeta_recursiva(
        respaldo.drive_folder_archivos_id
    ):
        logger.warning("No se pudo borrar de Drive el snapshot de %s", respaldo.etiqueta)

    return ok


def eliminar(
    db: Session,
    respaldo_id: int,
    usuario_id: Optional[int],
    usuario_nombre: str,
    ip_address: Optional[str] = None,
) -> dict:
    respaldo = obtener(db, respaldo_id)

    if respaldo.estado != "completado":
        raise HTTPException(
            status_code=409,
            detail="Solo se pueden eliminar respaldos que terminaron correctamente.",
        )

    completados = listar_completados(db)

    if len(completados) <= 2:
        raise HTTPException(
            status_code=409,
            detail=(
                "El sistema debe conservar al menos 2 respaldos, por lo que este "
                "no se puede eliminar."
            ),
        )

    if completados[0].id != respaldo_id:
        raise HTTPException(
            status_code=409,
            detail="Solo se puede eliminar el respaldo más antiguo. Elimina ese primero.",
        )

    if not _quitar_de_drive(db, respaldo):
        raise HTTPException(
            status_code=500,
            detail=(
                "No se pudo eliminar el archivo del respaldo desde Google Drive. "
                "Intenta nuevamente."
            ),
        )

    etiqueta = respaldo.etiqueta
    _borrar_tokens(db, [respaldo_id])
    db.delete(respaldo)
    db.commit()

    bitacora_service.registrar(
        db,
        usuario_id=usuario_id,
        usuario_nombre=usuario_nombre,
        accion="eliminar",
        modulo="respaldos",
        detalle=f"Respaldo #{respaldo_id} ({etiqueta}) eliminado",
        ip_address=ip_address,
    )

    restantes = contar_completados(db)
    return {
        "eliminado": True,
        "respaldo_id": respaldo_id,
        "respaldos_restantes": restantes,
        "puede_eliminar_otro": restantes > 2,
    }


def _podar_por_maximo(db: Session) -> int:
    """Conserva como máximo N respaldos retirando los más antiguos.

    Se ejecuta al finalizar una creación, nunca antes: si el respaldo nuevo
    falla no se pierde ninguno anterior.
    """
    config = obtener_config(db)
    completados = listar_completados(db)
    if len(completados) <= config.maximo_respaldos:
        return 0

    excedentes = completados[: len(completados) - config.maximo_respaldos]
    retirados = 0
    for viejo in excedentes:
        if not _quitar_de_drive(db, viejo):
            break
        _borrar_tokens(db, [viejo.id])
        db.delete(viejo)
        db.commit()
        retirados += 1
        logger.info(
            "Respaldo antiguo #%s retirado por el límite de %s respaldos",
            viejo.id, config.maximo_respaldos,
        )
    return retirados


def resincronizar(
    db: Session,
    usuario_id: Optional[int] = None,
    usuario_nombre: str = "",
    ip_address: Optional[str] = None,
    registrar_bitacora: bool = True,
) -> dict:
    """Reconstruye la tabla de respaldos a partir de los manifiestos de Drive.

    Es la fuente de verdad: si la base de datos fue restaurada y la tabla
    'respaldo' quedó vacía o atrasada, este proceso la pone al día.
    """
    drive = GoogleDriveService(db)
    carpeta_bd = _asegurar_ruta(drive, CARPETA_BASE_DATOS)

    encontrados: dict = {}
    ilegibles = 0
    for item in drive.listar_contenido(carpeta_bd, "archivos"):
        if not item.get("name", "").lower().endswith(".json"):
            continue
        crudo = drive.descargar_archivo(item["id"])
        if not crudo:
            ilegibles += 1
            continue
        try:
            datos = json.loads(crudo)
        except (ValueError, UnicodeDecodeError):
            ilegibles += 1
            continue
        if not isinstance(datos, dict) or datos.get("id") is None:
            continue
        encontrados[int(datos["id"])] = (datos, item["id"])

    existentes = {r.id: r for r in db.exec(select(Respaldo)).all()}
    creados = actualizados = 0

    for respaldo_id, (datos, manifiesto_id) in sorted(encontrados.items()):
        campos = {
            "etiqueta": datos.get("etiqueta") or f"Respaldo {respaldo_id}",
            "fecha": _parsear_fecha(datos.get("fecha")),
            "nombre_archivo": datos.get("nombre_archivo") or datos.get("archivo") or "",
            "drive_file_id": datos.get("drive_file_id") or "",
            "drive_manifesto_id": manifiesto_id,
            "drive_folder_archivos_id": datos.get("drive_folder_archivos_id"),
            "tamano_bytes": int(datos.get("tamano_bytes") or 0),
            "sha256": datos.get("sha256"),
            "cantidad_archivos": int(datos.get("cantidad_archivos") or 0),
            "estado": datos.get("estado") or "completado",
            "tipo": datos.get("tipo") or "manual",
            "observacion": datos.get("observacion"),
            "usuario_id": datos.get("usuario_id"),
            "usuario_nombre": datos.get("usuario_nombre") or datos.get("usuario") or "",
        }

        fila = existentes.get(respaldo_id)
        if fila:
            for campo, valor in campos.items():
                setattr(fila, campo, valor)
            fila.estado = _estado_definitivo(fila.estado)
            fila.updated_at = datetime.utcnow()
            db.add(fila)
            actualizados += 1
        else:
            campos["estado"] = _estado_definitivo(campos["estado"])
            db.add(Respaldo(id=respaldo_id, **campos))
            creados += 1

    borrados = 0
    activo = backup_jobs.en_ejecucion()
    en_curso = {activo.respaldo_id} if activo and activo.respaldo_id else set()
    huerfanos = [
        fila.id
        for fila in existentes.values()
        # Se conservan los que están en Drive y el que se está creando ahora
        # mismo; un "en proceso" huérfano es un resto de una corrida fallida.
        if fila.id not in encontrados and fila.id not in en_curso
    ]
    if huerfanos:
        _borrar_tokens(db, huerfanos)
        for respaldo_id in huerfanos:
            db.delete(existentes[respaldo_id])
            borrados += 1

    db.commit()
    _resetear_secuencia(db)

    if registrar_bitacora:
        bitacora_service.registrar(
            db,
            usuario_id=usuario_id,
            usuario_nombre=usuario_nombre,
            accion="actualizar",
            modulo="respaldos",
            detalle=(
                f"Respaldos resincronizados desde Google Drive "
                f"({creados} nuevos, {actualizados} actualizados, {borrados} retirados)"
            ),
            ip_address=ip_address,
        )

    return {
        "creados": creados,
        "actualizados": actualizados,
        "eliminados": borrados,
        "manifiestos_ilegibles": ilegibles,
        "total": len(encontrados),
    }


def _estado_definitivo(valor: str) -> str:
    """Los manifiestos más antiguos guardaban el estado transitorio
    'en_proceso'; para la lista eso ya es terminal: el archivo está en Drive."""
    return valor if valor in ("completado", "fallido") else "completado"


def _parsear_fecha(valor):
    if isinstance(valor, datetime):
        return valor
    if not valor:
        return datetime.utcnow()
    try:
        return datetime.fromisoformat(str(valor).replace("Z", "+00:00")).replace(tzinfo=None)
    except ValueError:
        return datetime.utcnow()


def _resetear_secuencia(db: Session) -> None:
    """Ajusta la secuencia de 'respaldo.id' tras cargar ids fijos desde Drive."""
    try:
        db.exec(
            text(
                "SELECT setval(pg_get_serial_sequence('respaldo','id'), "
                "COALESCE((SELECT MAX(id) FROM respaldo), 0) + 1, false)"
            )
        )
        db.commit()
    except Exception as error:
        db.rollback()
        logger.warning("No se pudo ajustar la secuencia de respaldo.id: %s", error)


def listar(db: Session) -> List[Respaldo]:
    return list(db.exec(select(Respaldo).order_by(Respaldo.fecha.desc())).all())


def listar_completados(db: Session) -> List[Respaldo]:
    """Respaldos buenos, del más antiguo al más reciente."""
    return list(
        db.exec(
            select(Respaldo)
            .where(Respaldo.estado == "completado")
            .order_by(Respaldo.fecha.asc(), Respaldo.id.asc())
        ).all()
    )


def contar_completados(db: Session) -> int:
    return db.exec(
        select(func.count(Respaldo.id)).where(Respaldo.estado == "completado")
    ).one()


def obtener_mas_antiguo(db: Session) -> Optional[Respaldo]:
    completados = listar_completados(db)
    return completados[0] if completados else None


def obtener(db: Session, respaldo_id: int) -> Respaldo:
    respaldo = db.get(Respaldo, respaldo_id)
    if not respaldo:
        raise HTTPException(status_code=404, detail="Respaldo no encontrado")
    return respaldo


def _asegurar_ruta(drive: GoogleDriveService, ruta: str) -> str:
    """Crea (si hace falta) una ruta como 'backups/base_datos' y devuelve el id."""
    padre: Optional[str] = None
    for parte in [p for p in ruta.split("/") if p]:
        padre = drive.obtener_o_crear_carpeta(parte, padre)
    return padre


def _buscar_ruta(drive: GoogleDriveService, ruta: str) -> Optional[str]:
    """Igual que _asegurar_ruta pero solo consulta, nunca crea carpetas."""
    actual = drive.FOLDER_ID
    for parte in [p for p in ruta.split("/") if p]:
        encontrada = None
        for hijo in drive.listar_contenido(actual, "carpetas"):
            if hijo.get("name") == parte:
                encontrada = hijo.get("id")
                break
        if not encontrada:
            return None
        actual = encontrada
    return actual


def estado(db: Session) -> RespaldoEstadoLeer:
    disponibilidad = pg_service.disponibilidad()
    drive = GoogleDriveService(db)

    drive_conectado = False
    drive_motivo = "no_autorizado"
    carpeta_raiz_id = None
    carpeta_servicios_id = None
    carpeta_base_datos_id = None
    carpeta_archivos_id = None

    try:
        info = drive.verificar_estado()
        drive_conectado = bool(info.get("autorizado"))
        drive_motivo = info.get("motivo")
        if drive_conectado:
            carpeta_raiz_id = drive.FOLDER_ID or None
            carpeta_servicios_id = _buscar_ruta(drive, CARPETA_SERVICIOS)
            carpeta_base_datos_id = _buscar_ruta(drive, CARPETA_BASE_DATOS)
            carpeta_archivos_id = _buscar_ruta(drive, CARPETA_SNAPSHOTS)
    except Exception as error:  # un problema de Drive no debe tumbar la página
        logger.warning("No se pudo leer el estado de Google Drive: %s", error)
        drive_motivo = str(error)

    config = obtener_config(db)
    total = db.exec(select(func.count(Respaldo.id))).one() or 0
    ultimo = db.exec(
        select(Respaldo)
        .where(Respaldo.estado == "completado")
        .order_by(Respaldo.fecha.desc())
    ).first()

    dias: Optional[int] = None
    vigencia = "nunca"
    siguiente: Optional[datetime] = None
    if ultimo:
        dias = max(0, (datetime.utcnow() - ultimo.fecha).days)
        siguiente = ultimo.fecha + timedelta(days=config.frecuencia_dias)
        if dias >= config.dias_advertencia:
            vigencia = "vencido"
        elif dias >= config.frecuencia_dias:
            vigencia = "proximo"
        else:
            vigencia = "al_dia"

    job = backup_jobs.en_ejecucion()

    return RespaldoEstadoLeer(
        pg_dump_disponible=disponibilidad["pg_dump_disponible"],
        psql_disponible=disponibilidad["psql_disponible"],
        pg_dump_ruta=disponibilidad["pg_dump_ruta"],
        psql_ruta=disponibilidad["psql_ruta"],
        drive_conectado=drive_conectado,
        drive_motivo=drive_motivo,
        total_respaldos=total,
        ultimo_respaldo=a_respaldo_leer(ultimo) if ultimo else None,
        dias_desde_ultimo=dias,
        vigencia=vigencia,
        fecha_siguiente_recomendada=siguiente,
        config=config,
        carpeta_servicios_id=carpeta_servicios_id,
        carpeta_base_datos_id=carpeta_base_datos_id,
        carpeta_archivos_id=carpeta_archivos_id,
        carpeta_raiz_id=carpeta_raiz_id,
        job_en_ejecucion=job.a_dict() if job else None,
        maximo_alcanzado=total >= config.maximo_respaldos,
    )


# ---------------------------------------------------------------------------
# Generación del respaldo
# ---------------------------------------------------------------------------

def crear_job() -> "backup_jobs.JobRespaldo":
    return backup_jobs.crear("creacion", PASOS_RESPALDO)


def ejecutar_respaldo(
    db: Session,
    job,
    usuario_id: Optional[int],
    usuario_nombre: str,
    observacion: Optional[str],
    ip_address: Optional[str] = None,
    tipo: str = "manual",
) -> Respaldo:
    marca = _marca()
    respaldo: Optional[Respaldo] = None
    try:
        respaldo = _nueva_fila(
            db, job, marca, usuario_id, usuario_nombre, observacion, tipo
        )

        _verificar_entorno(db, job)
        ruta_sql, bytes_sql, nombre_sql, tamano, sha = _volcar(job, marca)
        _subir_sql(db, job, respaldo, nombre_sql, bytes_sql, tamano, sha)
        fallidos = _copiar_documentos(db, job, respaldo, marca)
        _escribir_manifiesto(db, job, respaldo, nombre_sql, tamano, sha, usuario_nombre)
        historico = _replicar_historico(db, job, respaldo, marca)
        poda = _registrar(db, job, respaldo, usuario_id, usuario_nombre, ip_address)
    except Exception as error:
        if respaldo is not None:
            _fallido(db, respaldo, error)
        job.fallar(str(error))
        raise

    job.terminar(
        {
            "respaldo_id": respaldo.id,
            "tamano_bytes": respaldo.tamano_bytes,
            "cantidad_archivos": respaldo.cantidad_archivos,
            "documentos_fallidos": fallidos,
            "historico_copiado": historico,
            **poda,
        }
    )
    return respaldo


def _nueva_fila(
    db: Session,
    job,
    marca: str,
    usuario_id: Optional[int],
    usuario_nombre: str,
    observacion: Optional[str],
    tipo: str = "manual",
) -> Respaldo:
    respaldo = Respaldo(
        etiqueta=f"Respaldo {marca}",
        fecha=datetime.utcnow(),
        nombre_archivo="",
        drive_file_id="",
        estado="en_proceso",
        tipo=tipo,
        observacion=observacion,
        usuario_id=usuario_id,
        usuario_nombre=usuario_nombre,
    )
    db.add(respaldo)
    db.commit()
    db.refresh(respaldo)
    job.respaldo_id = respaldo.id
    return respaldo


def _verificar_entorno(db: Session, job) -> None:
    with job.paso(PASOS_RESPALDO[0]):
        if not pg_service.disponibilidad()["pg_dump_disponible"]:
            raise RuntimeError(
                "No se encontró 'pg_dump'. Instala el cliente de PostgreSQL o define "
                "PG_DUMP_PATH en el archivo .env del backend."
            )
        drive = GoogleDriveService(db)
        if not drive.verificar_estado().get("autorizado"):
            raise RuntimeError(
                "Google Drive no está conectado. Conéctalo desde tu perfil antes de generar el respaldo."
            )
        _asegurar_ruta(drive, CARPETA_SERVICIOS)
        _asegurar_ruta(drive, CARPETA_BASE_DATOS)
        _asegurar_ruta(drive, CARPETA_SNAPSHOTS)


def _volcar(job, marca: str) -> Tuple[Path, bytes, str, int, str]:
    with job.paso(PASOS_RESPALDO[1]):
        nombre_sql = f"{_sanitizar(POSTGRES_DB)}_{marca}.sql"
        ruta_sql = directorio_trabajo() / nombre_sql
        tamano = pg_service.volcar(ruta_sql)
        sha = _sha256_de(ruta_sql)
        return ruta_sql, ruta_sql.read_bytes(), nombre_sql, tamano, sha


def _subir_sql(
    db: Session, job, respaldo: Respaldo, nombre_sql: str,
    bytes_sql: bytes, tamano: int, sha: str,
) -> None:
    with job.paso(PASOS_RESPALDO[2]):
        subida = GoogleDriveService(db).subir_archivo(
            bytes_sql, nombre_sql, CARPETA_BASE_DATOS
        )
        if not subida or not subida.get("file_id"):
            raise RuntimeError("No se pudo subir el archivo .sql a Google Drive.")
        respaldo.nombre_archivo = nombre_sql
        respaldo.drive_file_id = subida["file_id"]
        respaldo.tamano_bytes = tamano
        respaldo.sha256 = sha
        _guardar(db, respaldo)


def _escribir_manifiesto(
    db: Session, job, respaldo: Respaldo, nombre_sql: str,
    tamano: int, sha: str, usuario_nombre: str,
) -> None:
    """Sube el .json con los datos del respaldo.

    Ese archivo es la fuente de verdad: si la tabla 'respaldo' se pierde al
    restaurar, el historial se reconstruye leyendo estos manifiestos.
    """
    with job.paso(PASOS_RESPALDO[4]):
        manifiesto = {
            "id": respaldo.id,
            "etiqueta": respaldo.etiqueta,
            "fecha": respaldo.fecha.isoformat(),
            "tipo": respaldo.tipo,
            # El manifiesto se escribe cuando todo ya está en Drive, así que a
            # partir de ahí el respaldo es válido: no debe heredar el
            # estado transitorio "en_proceso" de la fila.
            "estado": "completado",
            "observacion": respaldo.observacion,
            "nombre_archivo": nombre_sql,
            "drive_file_id": respaldo.drive_file_id,
            "tamano_bytes": tamano,
            "sha256": sha,
            "cantidad_archivos": respaldo.cantidad_archivos,
            "drive_folder_archivos_id": respaldo.drive_folder_archivos_id,
            "usuario_id": respaldo.usuario_id,
            "usuario_nombre": usuario_nombre,
            "base_datos": POSTGRES_DB,
        }
        nombre_json = nombre_sql.rsplit(".", 1)[0] + ".json"
        subida = GoogleDriveService(db).subir_archivo(
            json.dumps(manifiesto, ensure_ascii=False, indent=2).encode("utf-8"),
            nombre_json,
            CARPETA_BASE_DATOS,
        )
        if not subida or not subida.get("file_id"):
            raise RuntimeError("No se pudo subir el manifiesto del respaldo.")
        respaldo.drive_manifesto_id = subida["file_id"]
        _guardar(db, respaldo)


def _copiar_documentos(db: Session, job, respaldo: Respaldo, marca: str) -> list:
    """Copia todos los documentos de servicios a backups/archivos/<marca>/."""
    with job.paso(PASOS_RESPALDO[3]):
        drive = GoogleDriveService(db)
        carpeta_snapshots = _asegurar_ruta(drive, CARPETA_SNAPSHOTS)
        carpeta_snapshot = drive.obtener_o_crear_carpeta(marca, carpeta_snapshots)

        archivos = list(db.exec(select(ServicioArchivo)).all())
        carpetas: dict = {}
        entradas: list = []
        fallidos: list = []

        for archivo in archivos:
            try:
                nombre_carpeta = obtener_carpeta_servicio(archivo.servicio)
            except Exception:
                nombre_carpeta = "sin_servicio"

            if nombre_carpeta not in carpetas:
                carpetas[nombre_carpeta] = drive.obtener_o_crear_carpeta(
                    nombre_carpeta, carpeta_snapshot
                )

            try:
                copia = drive.copiar_archivo(
                    archivo.drive_file_id, carpetas[nombre_carpeta], archivo.nombre_original
                )
            except Exception as error:
                fallidos.append(
                    {"archivo_id": archivo.id, "nombre": archivo.nombre_original, "motivo": str(error)}
                )
                continue

            entradas.append(
                {
                    "archivo_id": archivo.id,
                    "id_servicio": archivo.id_servicio,
                    "tipo": getattr(archivo.tipo, "value", str(archivo.tipo)),
                    "nombre_original": archivo.nombre_original,
                    "carpeta": nombre_carpeta,
                    "mime_type": archivo.mime_type,
                    "origen_file_id": archivo.drive_file_id,
                    "copia_file_id": copia["file_id"],
                }
            )

        manifiesto = {
            "respaldo_id": respaldo.id,
            "fecha": respaldo.fecha.isoformat(),
            "total_archivos": len(entradas),
            "fallidos": fallidos,
            "archivos": entradas,
        }
        nombre_m = f"_manifiesto_{marca}.json"
        subida = drive.subir_archivo(
            json.dumps(manifiesto, ensure_ascii=False, indent=2).encode("utf-8"),
            nombre_m,
            f"{CARPETA_SNAPSHOTS}/{marca}",
        )
        if not subida or not subida.get("file_id"):
            raise RuntimeError("No se pudo subir el manifiesto de los documentos.")

        respaldo.cantidad_archivos = len(entradas)
        respaldo.drive_folder_archivos_id = carpeta_snapshot
        _guardar(db, respaldo)
        return fallidos


def _replicar_historico(db: Session, job, respaldo: Respaldo, marca: str) -> int:
    """Copia el histórico de .sql y .json al interior del snapshot.

    Es la redundancia que pide el requisito: la carpeta secundaria guarda
    también los respaldos de la base de datos.
    """
    with job.paso(PASOS_RESPALDO[5]):
        drive = GoogleDriveService(db)
        carpeta_bd = _asegurar_ruta(drive, CARPETA_BASE_DATOS)
        carpeta_snapshot = respaldo.drive_folder_archivos_id or _asegurar_ruta(
            drive, f"{CARPETA_SNAPSHOTS}/{marca}"
        )
        destino = drive.obtener_o_crear_carpeta("base_datos", carpeta_snapshot)

        copiados = 0
        for item in drive.listar_contenido(carpeta_bd, "archivos"):
            if not item.get("name", "").lower().endswith((".sql", ".json")):
                continue
            try:
                drive.copiar_archivo(item["id"], destino, item["name"])
                copiados += 1
            except Exception as error:
                # No abortamos el respaldo por un archivo histórico que no se
                # pueda copiar: el .sql y los documentos ya están en Drive.
                logger.warning(
                    "No se pudo copiar el histórico %s al snapshot %s: %s",
                    item.get("name"), marca, error,
                )
        return copiados


def _registrar(
    db: Session, job, respaldo: Respaldo,
    usuario_id: Optional[int], usuario_nombre: str, ip_address: Optional[str],
) -> dict:
    with job.paso(PASOS_RESPALDO[6]):
        respaldo.estado = "completado"
        respaldo.mensaje_error = None
        _guardar(db, respaldo)

        retirados = _podar_por_maximo(db)

        bitacora_service.registrar(
            db,
            usuario_id=usuario_id,
            usuario_nombre=usuario_nombre,
            accion="crear",
            modulo="respaldos",
            detalle=(
                f"Respaldo #{respaldo.id} generado ({formatear_tamano(respaldo.tamano_bytes)}, "
                f"{respaldo.cantidad_archivos} documentos)"
                + (f"; se retiraron {retirados} respaldo(s) antiguos" if retirados else "")
            ),
            ip_address=ip_address,
        )
        return {"respaldos_retirados": retirados}


def _fallido(db: Session, respaldo: Respaldo, error: Exception) -> None:
    try:
        respaldo.estado = "fallido"
        respaldo.mensaje_error = str(error)
        _guardar(db, respaldo)
    except Exception:
        logger.exception("No se pudo marcar el respaldo %s como fallido", respaldo.id)


def tarea_crear(
    job_id: str,
    usuario_id: Optional[int],
    usuario_nombre: str,
    observacion: Optional[str],
    ip_address: Optional[str] = None,
) -> None:
    """Punto de entrada que corre en segundo plano tras responder 202."""
    job = backup_jobs.obtener(job_id)
    if not job:
        return
    try:
        with Session(engine) as db:
            ejecutar_respaldo(db, job, usuario_id, usuario_nombre, observacion, ip_address)
    except Exception as error:
        logger.exception("El job de respaldo %s terminó con error", job_id)
        if job.estado == "en_proceso":
            job.fallar(str(error))


# ---------------------------------------------------------------------------
# Codigo de confirmacion de la restauracion
# ---------------------------------------------------------------------------

VIGENCIA_CODIGO_MINUTOS = 10
MAXIMO_INTENTOS_CODIGO = 6


def _hash_codigo(codigo: str) -> str:
    return hashlib.sha256(codigo.encode("utf-8")).hexdigest()


def generar_codigo(
    db: Session,
    respaldo_id: int,
    usuario_id: Optional[int],
    usuario_nombre: str = "",
    ip_address: Optional[str] = None,
) -> dict:
    respaldo = obtener(db, respaldo_id)
    if respaldo.estado != "completado":
        raise HTTPException(
            status_code=409,
            detail="Solo se puede restaurar un respaldo que terminó correctamente.",
        )

    previos = db.exec(
        select(TokenRestauracion).where(
            TokenRestauracion.respaldo_id == respaldo_id,
            TokenRestauracion.usado_en.is_(None),
        )
    ).all()
    for anterior in previos:
        db.delete(anterior)

    codigo = secrets.token_hex(6)  # 12 caracteres, 48 bits
    fila = TokenRestauracion(
        respaldo_id=respaldo_id,
        usuario_id=usuario_id,
        token_hash=_hash_codigo(codigo),
        expira_en=datetime.utcnow() + timedelta(minutes=VIGENCIA_CODIGO_MINUTOS),
    )
    db.add(fila)
    db.commit()
    db.refresh(fila)

    bitacora_service.registrar(
        db,
        usuario_id=usuario_id,
        usuario_nombre=usuario_nombre,
        accion="generar",
        modulo="respaldos",
        detalle=f"Código de confirmación emitido para restaurar el respaldo #{respaldo_id}",
        ip_address=ip_address,
    )

    return {"token": codigo, "expira_en": fila.expira_en}


def validar_codigo(
    db: Session,
    respaldo_id: int,
    codigo: str,
    usuario_id: Optional[int],
) -> None:
    ahora = datetime.utcnow()
    activos = list(
        db.exec(
            select(TokenRestauracion).where(
                TokenRestauracion.respaldo_id == respaldo_id,
                TokenRestauracion.usado_en.is_(None),
                TokenRestauracion.expira_en > ahora,
            )
        ).all()
    )

    coincidencia = next(
        (f for f in activos if f.token_hash == _hash_codigo(codigo)), None
    )

    if not coincidencia:
        for fila in activos:
            fila.intentos = (fila.intentos or 0) + 1
            if fila.intentos >= MAXIMO_INTENTOS_CODIGO:
                fila.usado_en = ahora
            db.add(fila)
        db.commit()
        raise HTTPException(
            status_code=400,
            detail="El código de confirmación no es válido.",
        )

    if coincidencia.usuario_id and usuario_id and coincidencia.usuario_id != usuario_id:
        raise HTTPException(
            status_code=400,
            detail="Ese código fue generado por otro usuario. Genera uno nuevo.",
        )

    coincidencia.usado_en = ahora
    db.add(coincidencia)
    db.commit()


# ---------------------------------------------------------------------------
# Restauracion
# ---------------------------------------------------------------------------

def crear_job_restauracion(respaldo_id: int):
    job = backup_jobs.crear("restauracion", PASOS_RESTAURACION, respaldo_id)
    return job


def crear_job_recuperacion(respaldo_id: int):
    job = backup_jobs.crear("recuperacion", PASOS_RECUPERAR, respaldo_id)
    return job


def ejecutar_restauracion(
    job,
    respaldo_id: int,
    usuario_id: Optional[int],
    usuario_nombre: str,
    ver_token: Optional[int],
    restaurar_archivos: bool = True,
    ip_address: Optional[str] = None,
) -> dict:
    """Restaura la base de datos y los documentos desde un respaldo.

    Cada fase usa su propia sesión: al reconstruir las tablas, cualquier
    sesión abierta anteriormente queda inservible.
    """
    # --- 1. Verificar el archivo -----------------------------------------
    with job.paso(PASOS_RESTAURACION[0]):
        if not pg_service.disponibilidad()["psql_disponible"]:
            raise RuntimeError(
                "No se encontró 'psql'. Instala el cliente de PostgreSQL o define "
                "PSQL_PATH en el archivo .env del backend."
            )
        with Session(engine) as db:
            respaldo = obtener(db, respaldo_id)
            if respaldo.estado != "completado":
                raise RuntimeError(
                    "Ese respaldo no se puede restaurar porque no terminó bien."
                )
            drive = GoogleDriveService(db)
            datos = drive.descargar_archivo(respaldo.drive_file_id)
            if not datos:
                raise RuntimeError(
                    "No se pudo descargar el archivo .sql desde Google Drive."
                )
            nombre = respaldo.nombre_archivo or f"respaldo_{respaldo_id}.sql"
            ruta_sql = directorio_trabajo() / nombre
            ruta_sql.write_bytes(datos)
            if respaldo.sha256 and _sha256_de(ruta_sql) != respaldo.sha256:
                raise RuntimeError(
                    "El archivo del respaldo está dañado: el checksum no coincide "
                    "con el registrado al generarlo."
                )
            manifiesto = _leer_manifiesto_documentos(drive, respaldo)
            snapshot_id = respaldo.drive_folder_archivos_id

    # --- 2. Respaldo de seguridad de lo que hay ahora ---------------------
    with job.paso(PASOS_RESTAURACION[1]):
        job_seguridad = backup_jobs.JobRespaldo(
            uuid.uuid4().hex[:16], "creacion", list(PASOS_RESPALDO)
        )
        with Session(engine) as db:
            ejecutar_respaldo(
                db,
                job_seguridad,
                usuario_id,
                usuario_nombre,
                f"Respaldo de seguridad previo a la restauración del respaldo #{respaldo_id}",
                ip_address,
                tipo="seguridad",
            )
        if job_seguridad.estado != "completado" or not job_seguridad.respaldo_id:
            raise RuntimeError(
                "No se pudo generar el respaldo de seguridad. La restauración se canceló."
            )
        seguridad_id = job_seguridad.respaldo_id

    # --- 3. Restaurar la base de datos ------------------------------------
    with job.paso(PASOS_RESTAURACION[2]):
        engine.dispose()
        cerradas = pg_service.cerrar_conexiones_ajenas()
        if cerradas:
            logger.warning("Se cerraron %s conexiones antes de restaurar", cerradas)
        try:
            pg_service.restaurar(ruta_sql)
        finally:
            engine.dispose()

    # --- 4. Documentos de servicios ---------------------------------------
    recuperados = {"revisados": 0, "recuperados": 0, "omitidos": 0, "fallidos": 0}
    if restaurar_archivos:
        with job.paso(PASOS_RESTAURACION[3]):
            with Session(engine) as db:
                recuperados = _recuperar_documentos(
                    db, respaldo_id, manifiesto, snapshot_id
                )
    else:
        job.omitir(
            PASOS_RESTAURACION[3],
            "Omitido: el administrador eligió restaurar solo la base de datos.",
        )

    # --- 5. Reconectar y verificar ----------------------------------------
    with job.paso(PASOS_RESTAURACION[4]):
        engine.dispose()
        inicializar_base_de_datos()
        with Session(engine) as db:
            invalidadas = _invalidar_sesiones(db, usuario_id, usuario_nombre, ver_token)
            resumen_respaldos = resincronizar(
                db,
                usuario_id=usuario_id,
                usuario_nombre=usuario_nombre,
                ip_address=ip_address,
                registrar_bitacora=False,
            )
            bitacora_service.registrar(
                db,
                usuario_id=usuario_id,
                usuario_nombre=usuario_nombre,
                accion="restaurar",
                modulo="respaldos",
                detalle=(
                    f"Base de datos restaurada desde el respaldo #{respaldo_id}; "
                    f"respaldo de seguridad #{seguridad_id} generado antes; "
                    f"{invalidadas} sesión(es) cerrada(s)"
                ),
                ip_address=ip_address,
            )

    resultado = {
        "respaldo_id": respaldo_id,
        "respaldo_seguridad_id": seguridad_id,
        "documentos": recuperados,
        "sesiones_cerradas": invalidadas,
        "respaldos_resincronizados": resumen_respaldos,
        "archivos_restaurados": restaurar_archivos,
    }
    job.terminar(resultado)
    return resultado


def tarea_restaurar(
    job_id: str,
    respaldo_id: int,
    usuario_id: Optional[int],
    usuario_nombre: str,
    ver_token: Optional[int],
    restaurar_archivos: bool = True,
    ip_address: Optional[str] = None,
) -> None:
    job = backup_jobs.obtener(job_id)
    if not job:
        return
    try:
        ejecutar_restauracion(
            job,
            respaldo_id,
            usuario_id,
            usuario_nombre,
            ver_token,
            restaurar_archivos,
            ip_address,
        )
    except Exception as error:
        logger.exception("La restauración del respaldo %s falló", respaldo_id)
        if job.estado == "en_proceso":
            job.fallar(str(error))


def _leer_manifiesto_documentos(
    drive: GoogleDriveService, respaldo: Respaldo
) -> Optional[dict]:
    """Lee el _manifiesto_<marca>.json que describe el snapshot de documentos."""
    if not respaldo.drive_folder_archivos_id:
        return None
    try:
        for item in drive.listar_contenido(respaldo.drive_folder_archivos_id, "archivos"):
            nombre = item.get("name", "")
            if not (nombre.startswith("_manifiesto_") and nombre.endswith(".json")):
                continue
            crudo = drive.descargar_archivo(item["id"])
            if crudo:
                return json.loads(crudo)
    except Exception as error:
        logger.warning("No se pudo leer el manifiesto de documentos: %s", error)
    return None


def _recuperar_documentos(
    db: Session,
    respaldo_id: int,
    manifiesto: Optional[dict],
    snapshot_id: Optional[str],
) -> dict:
    """Vuelve a copiar a Drive los documentos que hoy no existen.

    Solo rellena huecos: nunca toca archivos que siguen ahí, así que no se
    pierde ningún documento subido después del respaldo.
    """
    resumen = {"revisados": 0, "recuperados": 0, "omitidos": 0, "fallidos": 0}
    entradas = (manifiesto or {}).get("archivos") or []
    if not entradas or not snapshot_id:
        resumen["fallidos"] = 0
        return resumen

    por_nombre = {
        (e.get("id_servicio"), e.get("nombre_original")): e for e in entradas
    }

    drive = GoogleDriveService(db)
    carpeta_servicios = _asegurar_ruta(drive, CARPETA_SERVICIOS)
    archivos = list(db.exec(select(ServicioArchivo)).all())

    for archivo in archivos:
        resumen["revisados"] += 1
        try:
            if archivo.drive_file_id and drive.archivo_existe(archivo.drive_file_id):
                resumen["omitidos"] += 1
                continue
        except Exception:
            # No pudimos comprobarlo: asumimos que hace falta y seguimos.
            pass

        entrada = por_nombre.get((archivo.id_servicio, archivo.nombre_original))
        if not entrada or not entrada.get("copia_file_id"):
            resumen["fallidos"] += 1
            continue

        try:
            carpeta = obtener_carpeta_servicio(archivo.servicio)
        except Exception:
            carpeta = "sin_servicio"

        try:
            carpeta_destino = drive.obtener_o_crear_carpeta(carpeta, carpeta_servicios)
            copia = drive.copiar_archivo(
                entrada["copia_file_id"], carpeta_destino, archivo.nombre_original
            )
            archivo.drive_file_id = copia["file_id"]
            db.add(archivo)
            resumen["recuperados"] += 1
        except Exception as error:
            logger.warning(
                "No se pudo recuperar %s: %s", archivo.nombre_original, error
            )
            resumen["fallidos"] += 1

    db.commit()
    return resumen


def _invalidar_sesiones(
    db: Session,
    usuario_id: Optional[int],
    usuario_nombre: Optional[str],
    ver_token: Optional[int],
) -> int:
    """Cierra todas las sesiones abiertas menos la del que está restaurando.

    Al reconstruir la base de datos cambian los ids y las versiones de
    token; forzar el cambio evita que quede viva una sesión con credenciales
    antiguas. El administrador conserva la suya para ver el resultado.
    """
    usuarios = list(db.exec(select(User)).all())
    if not usuarios:
        return 0

    destino = None
    if usuario_nombre:
        destino = next((u for u in usuarios if u.username == usuario_nombre), None)
    if destino is None and usuario_id:
        destino = next((u for u in usuarios if u.id == usuario_id), None)

    cerradas = 0
    for usuario in usuarios:
        if destino is not None and usuario.id == destino.id:
            objetivo = int(ver_token) if ver_token else (usuario.token_version or 0)
            if usuario.token_version != objetivo:
                usuario.token_version = objetivo
                db.add(usuario)
            continue
        usuario.token_version = (usuario.token_version or 0) + 1
        db.add(usuario)
        cerradas += 1

    db.commit()
    return cerradas


def ejecutar_recuperacion(
    job,
    respaldo_id: int,
    usuario_id: Optional[int],
    usuario_nombre: str,
    ip_address: Optional[str] = None,
) -> dict:
    """Solo repone los documentos de un respaldo, sin tocar la base de datos."""
    with job.paso(PASOS_RECUPERAR[0]):
        with Session(engine) as db:
            respaldo = obtener(db, respaldo_id)
            if respaldo.estado != "completado":
                raise RuntimeError("Ese respaldo no contiene documentos utilizables.")
            drive = GoogleDriveService(db)
            manifiesto = _leer_manifiesto_documentos(drive, respaldo)
            snapshot_id = respaldo.drive_folder_archivos_id

    with job.paso(PASOS_RECUPERAR[1]):
        with Session(engine) as db:
            resumen = _recuperar_documentos(db, respaldo_id, manifiesto, snapshot_id)

    with job.paso(PASOS_RECUPERAR[2]):
        with Session(engine) as db:
            bitacora_service.registrar(
                db,
                usuario_id=usuario_id,
                usuario_nombre=usuario_nombre,
                accion="actualizar",
                modulo="respaldos",
                detalle=(
                    f"Documentos recuperados desde el respaldo #{respaldo_id}: "
                    f"{resumen['recuperados']} de {resumen['revisados']}"
                ),
                ip_address=ip_address,
            )

    job.terminar({"respaldo_id": respaldo_id, "documentos": resumen})
    return resumen


def tarea_recuperar(
    job_id: str,
    respaldo_id: int,
    usuario_id: Optional[int],
    usuario_nombre: str,
    ip_address: Optional[str] = None,
) -> None:
    job = backup_jobs.obtener(job_id)
    if not job:
        return
    try:
        ejecutar_recuperacion(
            job, respaldo_id, usuario_id, usuario_nombre, ip_address
        )
    except Exception as error:
        logger.exception("La recuperación de documentos del respaldo %s falló", respaldo_id)
        if job.estado == "en_proceso":
            job.fallar(str(error))
