"""Pruebas unitarias del cifrado de archivos (Fernet)."""

import pytest
from cryptography.fernet import Fernet

from src.core import crypto


@pytest.fixture
def clave_valida(monkeypatch):
    monkeypatch.setenv("ENCRYPTION_KEY", Fernet.generate_key().decode())


def test_round_trip(clave_valida):
    """El contenido cifrado se recupera tal cual tras descifrarlo."""
    datos = b"certificado de defuncion confidencial"
    cifrado = crypto.encriptar_bytes(datos)

    assert cifrado != datos
    assert crypto.desencriptar_bytes(cifrado) == datos


def test_dos_cifrados_del_mismo_contenido_son_distintos(clave_valida):
    """Fernet incluye un IV aleatorio: el mismo dato no produce el mismo token."""
    datos = b"mismo contenido"
    assert crypto.encriptar_bytes(datos) != crypto.encriptar_bytes(datos)


def test_falta_la_clave(monkeypatch):
    monkeypatch.delenv("ENCRYPTION_KEY", raising=False)
    with pytest.raises(crypto.CryptoConfigError):
        crypto.encriptar_bytes(b"x")


def test_clave_invalida(monkeypatch):
    monkeypatch.setenv("ENCRYPTION_KEY", "esto-no-es-una-clave-fernet")
    with pytest.raises(crypto.CryptoConfigError):
        crypto.encriptar_bytes(b"x")


def test_descifrar_contenido_no_cifrado_falla(clave_valida):
    with pytest.raises(crypto.CryptoError):
        crypto.desencriptar_bytes(b"texto plano sin cifrar")
