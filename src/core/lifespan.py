import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlmodel import SQLModel, Session
from src.config.db import engine
from src.models.user import User, Role, Permission
from src.models import Servicio, Ataud, Capilla, Vehiculo, Contratante, ServicioVehiculo
from src.core.seed import ejecutar_seeding

@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        ejecutar_seeding(session)

    yield