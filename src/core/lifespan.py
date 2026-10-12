import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlmodel import SQLModel, Session
from src.config.db import engine
from src.models.user import User, Role, Permission
from src.models import (
    Servicio, Ataud, Capilla, Vehiculo, Contratante, Fallecido, ServicioVehiculo,
    ServicioArchivo, Bitacora, OAuthToken, PasswordResetToken, EmailChangeRequest,
    Respaldo, RespaldoConfig, TokenRestauracion,
)
from src.core.seed import ejecutar_seeding
from src.core.schema_bootstrap import asegurar_esquema_usuarios


def inicializar_base_de_datos():
    """Crea las tablas que falten, repara el esquema de usuarios y siembra permisos.

    Se usa al arrancar y tambien despues de restaurar un respaldo, porque la BD
    restaurada puede ser anterior a estas tablas y a estos permisos.
    """
    SQLModel.metadata.create_all(engine)
    asegurar_esquema_usuarios(engine)
    with Session(engine) as session:
        ejecutar_seeding(session)


@asynccontextmanager
async def lifespan(app: FastAPI):
    inicializar_base_de_datos()

    yield