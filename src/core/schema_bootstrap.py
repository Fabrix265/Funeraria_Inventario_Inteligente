import logging
from typing import List, Tuple

from sqlalchemy import text
from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)

COLUMNAS_USUARIO: List[Tuple[str, str]] = [
    ("email", "VARCHAR(255)"),
    ("token_version", "INTEGER NOT NULL DEFAULT 0"),
]


def _columna_existe(conn, columna: str) -> bool:
    return conn.execute(
        text(
            "SELECT 1 FROM information_schema.columns "
            "WHERE table_name = 'user' AND column_name = :columna"
        ),
        {"columna": columna},
    ).first() is not None


def _normalizar_correos(conn) -> int:
    return conn.execute(
        text('UPDATE "user" SET email = lower(email) WHERE email <> lower(email)')
    ).rowcount


def _colisiones_correo(conn) -> List[str]:
    filas = conn.execute(
        text(
            'SELECT lower(email) AS correo FROM "user" '
            "WHERE email IS NOT NULL GROUP BY lower(email) HAVING count(*) > 1"
        )
    ).all()
    return [f.correo for f in filas]


def asegurar_esquema_usuarios(engine: Engine) -> None:
    with engine.begin() as conn:
        for columna, definicion in COLUMNAS_USUARIO:
            if not _columna_existe(conn, columna):
                logger.warning("Columna user.%s ausente; se agrega a la tabla", columna)
            conn.execute(
                text(f'ALTER TABLE "user" ADD COLUMN IF NOT EXISTS {columna} {definicion}')
            )

        normalizados = _normalizar_correos(conn)
        if normalizados:
            logger.warning("Se normalizaron %s correos a minusculas", normalizados)

        colisiones = _colisiones_correo(conn)
        if colisiones:
            logger.error(
                "No se creo el indice unico de user.email: hay %s correos duplicados "
                "sin distinguir mayusculas: %s",
                len(colisiones),
                ", ".join(colisiones[:10]),
            )
            return

        conn.execute(
            text(
                'CREATE UNIQUE INDEX IF NOT EXISTS "uq_user_email_lower" '
                'ON "user" (lower(email))'
            )
        )
        logger.info("Esquema de usuarios verificado")
