import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlmodel import SQLModel, Session, select
from src.config.db import engine

from src.models.user import User, CargoEnum
from src.services.user_service import UserService
from src.schemas.user import UserCrear

from src.models import User, Servicio, Ataud, Capilla, Vehiculo, Contratante, Fallecido, ServicioVehiculo

@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        admin_username = os.getenv("ADMIN_USER")
        admin_password = os.getenv("ADMIN_PASSWORD")

        if admin_username and admin_password:
            statement = select(User).where(User.username == admin_username)
            existing_admin = session.exec(statement).first()

            if not existing_admin:
                print(f"Inicializando sistema: Creando admin '{admin_username}'...")
                
                user_data = UserCrear(
                    username=admin_username,
                    password=admin_password,
                    cargo=CargoEnum.administrador
                )
                
                UserService.crear_usuario(session, user_data)
                
                print("Administrador inicial creado con éxito.")
            else:
                print(f"ℹEl administrador '{admin_username}' ya está configurado.")
        else:
            print("Advertencia: No se detectaron ADMIN_USER o ADMIN_PASSWORD en el .env")

    yield