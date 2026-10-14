"""Cifrado simétrico de archivos antes de subirlos a Google Drive.

Usa Fernet (AES-128 en modo CBC + HMAC-SHA256) de la librería `cryptography`.
La clave se lee de la variable de entorno ENCRYPTION_KEY, que debe ser una
clave Fernet válida (32 bytes en base64 urlsafe).
"""

import os
import logging

from cryptography.fernet import Fernet, InvalidToken

logger = logging.getLogger(__name__)


class CryptoConfigError(RuntimeError):
    """La variable ENCRYPTION_KEY falta o no es una clave Fernet válida."""


class CryptoError(RuntimeError):
    """No se pudo descifrar el contenido (dato corrupto o clave incorrecta)."""


def obtener_fernet() -> Fernet:
    """Construye el objeto Fernet a partir de la variable de entorno."""
    clave = os.getenv("ENCRYPTION_KEY", "").strip()
    if not clave:
        raise CryptoConfigError(
            "Falta la variable de entorno ENCRYPTION_KEY. Genera una con "
            "'python -c \"from cryptography.fernet import Fernet; "
            "print(Fernet.generate_key().decode())\"' y añádela al .env del backend."
        )
    try:
        return Fernet(clave.encode("utf-8"))
    except (ValueError, TypeError) as error:
        raise CryptoConfigError(
            f"ENCRYPTION_KEY no es una clave Fernet válida: {error}"
        ) from error


def encriptar_bytes(datos: bytes) -> bytes:
    """Devuelve el contenido cifrado con Fernet."""
    return obtener_fernet().encrypt(datos)


def desencriptar_bytes(datos: bytes) -> bytes:
    """Devuelve el contenido original a partir de un token Fernet."""
    try:
        return obtener_fernet().decrypt(datos)
    except InvalidToken as error:
        raise CryptoError(
            "No se pudo desencriptar: el contenido no es un archivo cifrado "
            "válido o la clave ENCRYPTION_KEY es incorrecta."
        ) from error
