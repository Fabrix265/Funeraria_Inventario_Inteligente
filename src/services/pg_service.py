import glob
import logging
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Optional

from src.config.db import POSTGRES_SERVER, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD

logger = logging.getLogger(__name__)

# En Windows evitamos que se abra una ventana de consola por cada ejecución.
_SIN_VENTANA = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def _nombre_variable(nombre: str) -> str:
    return nombre.upper().replace("-", "_") + "_PATH"


def _orden_version(ruta: str) -> tuple:
    coincidencia = re.search(r"[-\\/](\d{1,2})(?:\.(\d+))?", ruta)
    if not coincidencia:
        return (0, 0)
    return (int(coincidencia.group(1)), int(coincidencia.group(2) or 0))


def localizar_binario(nombre: str) -> Optional[str]:
    """Busca pg_dump o psql: primero la variable del .env, luego el PATH, luego
    las instalaciones habituales de PostgreSQL. Devuelve None si no existe."""
    explicita = os.getenv(_nombre_variable(nombre))
    if explicita and Path(explicita).is_file():
        return str(Path(explicita))

    nombre_exe = f"{nombre}.exe" if os.name == "nt" else nombre
    candidatos = [c for c in (shutil.which(nombre), shutil.which(nombre_exe)) if c]

    instalaciones = []
    if os.name == "nt":
        for base in (r"C:\Program Files\PostgreSQL", r"C:\Program Files (x86)\PostgreSQL"):
            instalaciones += glob.glob(os.path.join(base, "*", "bin", nombre_exe))
    else:
        instalaciones += glob.glob(f"/usr/lib/postgresql/*/bin/{nombre}")
        instalaciones += [f"/usr/bin/{nombre}", f"/usr/local/bin/{nombre}"]

    candidatos += sorted(instalaciones, key=_orden_version, reverse=True)

    for candidato in candidatos:
        if Path(candidato).is_file():
            return str(Path(candidato))
    return None


def requerido(nombre: str) -> str:
    ruta = localizar_binario(nombre)
    if not ruta:
        raise RuntimeError(
            f"No se encontró '{nombre}'. Instala el cliente de PostgreSQL o define "
            f"{_nombre_variable(nombre)} en el archivo .env."
        )
    return ruta


def disponibilidad() -> dict:
    dump = localizar_binario("pg_dump")
    psql = localizar_binario("psql")
    return {
        "pg_dump_disponible": bool(dump),
        "psql_disponible": bool(psql),
        "pg_dump_ruta": dump,
        "psql_ruta": psql,
    }


def _argumentos_conexion(base_datos: Optional[str] = None) -> list:
    return [
        "--host", str(POSTGRES_SERVER or "localhost"),
        "--port", str(POSTGRES_PORT or "5432"),
        "--username", str(POSTGRES_USER or ""),
        "--dbname", str(base_datos or POSTGRES_DB or ""),
    ]


def _entorno() -> dict:
    env = os.environ.copy()
    # La contraseña viaja solo en el entorno, nunca en la línea de comandos.
    env["PGPASSWORD"] = str(POSTGRES_PASSWORD or "")
    sslmode = os.getenv("PGSSLMODE")
    if sslmode:
        env["PGSSLMODE"] = sslmode
    else:
        env.pop("PGSSLMODE", None)
    return env


def _ejecutar(cmd: list, env: dict, timeout: int) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            creationflags=_SIN_VENTANA,
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError(
            f"'{os.path.basename(cmd[0])}' tardó más de {timeout} segundos y se canceló."
        )
    except FileNotFoundError as e:
        raise RuntimeError(f"No se pudo ejecutar '{os.path.basename(cmd[0])}': {e}")


def volcar(destino: Path, timeout: int = 600, base_datos: Optional[str] = None) -> int:
    """Genera un archivo .sql con todo el contenido de la base de datos."""
    binario = requerido("pg_dump")
    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        binario,
        *_argumentos_conexion(base_datos),
        "--format=plain",
        "--no-owner",
        "--no-privileges",
        "--clean",
        "--if-exists",
        f"--file={destino}",
    ]

    proceso = _ejecutar(cmd, _entorno(), timeout)
    if proceso.returncode != 0:
        detalle = (proceso.stderr or proceso.stdout or "").strip()
        raise RuntimeError(f"pg_dump terminó con error: {detalle}")

    if not destino.is_file() or destino.stat().st_size == 0:
        raise RuntimeError("pg_dump no generó ningún archivo de respaldo.")

    return destino.stat().st_size


def cerrar_conexiones_ajenas(base_datos: Optional[str] = None) -> int:
    """Cierra las demás conexiones abiertas a la base de datos.

    pg_dump genera DROP TABLE, que necesita un bloqueo exclusivo: si la
    aplicación u otra herramienta tienen una transacción abierta, la
    restauración se quedaría esperando hasta el timeout. Devuelve cuántas
    sesiones se cerraron.
    """
    binario = requerido("psql")
    consulta = (
        "SELECT count(*) FROM (SELECT pg_terminate_backend(pid) AS ok "
        "FROM pg_stat_activity "
        "WHERE datname = current_database() AND pid <> pg_backend_pid()) x"
    )
    cmd = [
        binario,
        *_argumentos_conexion(base_datos),
        "-X",
        "-q",
        "-A",
        "-t",
        "-c",
        consulta,
    ]
    proceso = _ejecutar(cmd, _entorno(), 30)
    if proceso.returncode != 0:
        detalle = (proceso.stderr or proceso.stdout or "").strip()
        logger.warning("No se pudieron cerrar conexiones ajenas: %s", detalle)
        return 0
    try:
        return int((proceso.stdout or "0").strip().splitlines()[-1])
    except (ValueError, IndexError):
        return 0


def restaurar(
    dump: Path, timeout: int = 600, base_datos: Optional[str] = None
) -> str:
    """Aplica un archivo .sql sobre la base de datos actual.

    Se ejecuta en una sola transacción: si algo falla, no se queda a medias.
    """
    binario = requerido("psql")
    dump = Path(dump)
    if not dump.is_file():
        raise RuntimeError("El archivo .sql a restaurar no existe.")

    cmd = [
        binario,
        *_argumentos_conexion(base_datos),
        "--single-transaction",
        "--set", "ON_ERROR_STOP=1",
        f"--file={dump}",
    ]

    proceso = _ejecutar(cmd, _entorno(), timeout)
    salida = ((proceso.stdout or "") + (proceso.stderr or "")).strip()
    if proceso.returncode != 0:
        raise RuntimeError(f"psql terminó con error: {salida}")

    return salida
