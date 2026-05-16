from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from src.core.lifespan import lifespan
from src.utils.http_error_handler import http_error_handler

from src.routers.auth_router import auth_router
from src.routers.user_router import user_router
from src.routers.ataud_router import ataud_router
from src.routers.capilla_router import capilla_router
from src.routers.vehiculo_router import vehiculo_router
from src.routers.servicio_router import servicio_router
from src.routers.fallecido_router import fallecido_router
from src.routers.contratante_router import contratante_router

app = FastAPI(
    title="Inventario Funeraria Aranzabal API",
    version="1.0",
    lifespan=lifespan
)

app.middleware("http")(http_error_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Permite todos, se deberia cambiar por la URL del frontend en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

@app.get("/", tags=["Home"])
def home():
    return JSONResponse(content={"message": "Funcionando"})

app.include_router(auth_router, prefix="/auth", tags=["Autenticación"])

app.include_router(user_router, prefix="/users", tags=["Usuarios"])

app.include_router(ataud_router, prefix="/ataudes", tags=["Inventario - Ataúdes"])

app.include_router(capilla_router, prefix="/capillas", tags=["Inventario - Capillas"])

app.include_router(vehiculo_router, prefix="/vehiculos", tags=["Inventario - Vehículos"])

app.include_router(servicio_router, prefix="/servicios", tags=["Servicios"])

app.include_router(fallecido_router, prefix="/fallecidos", tags=["Fallecidos"])

app.include_router(contratante_router, prefix="/contratantes", tags=["Contratantes"]) 