import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlmodel import SQLModel, Session
from src.config.db import engine
from src.models.user import User, Role, Permission
from src.models import Servicio, Ataud, Capilla, Vehiculo, Contratante, Fallecido, ServicioVehiculo, ServicioArchivo, Bitacora, OAuthToken, PasswordResetToken, EmailChangeRequest
from src.core.seed import ejecutar_seeding
from src.core.schema_bootstrap import asegurar_esquema_usuarios

@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)

    asegurar_esquema_usuarios(engine)

    with Session(engine) as session:
        ejecutar_seeding(session)

    yield