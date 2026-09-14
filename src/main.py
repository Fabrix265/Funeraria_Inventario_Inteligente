from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from src.core.lifespan import lifespan
from src.utils.http_error_handler import http_error_handler
from src.deps.limiter import limiter

from src.routers.auth_router import auth_router
from src.routers.user_router import user_router
from src.routers.ataud_router import ataud_router
from src.routers.capilla_router import capilla_router
from src.routers.vehiculo_router import vehiculo_router
from src.routers.servicio_router import servicio_router
from src.routers.fallecido_router import fallecido_router
from src.routers.contratante_router import contratante_router
from src.routers.role_router import role_router
from src.routers.reniec_router import reniec_router
from src.routers.bitacora_router import bitacora_router
from src.routers.drive_router import drive_router

app = FastAPI(
    title="Inventario Funeraria Aranzabal API",
    version="1.0",
    lifespan=lifespan
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.middleware("http")(http_error_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
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
app.include_router(role_router, prefix="/roles", tags=["Roles y Permisos"])
app.include_router(ataud_router, prefix="/coffins", tags=["Inventario - Ataúdes"])
app.include_router(capilla_router, prefix="/chapels", tags=["Inventario - Capillas"])
app.include_router(vehiculo_router, prefix="/vehicles", tags=["Inventario - Vehículos"])
app.include_router(servicio_router, prefix="/services", tags=["Servicios"])
app.include_router(fallecido_router, prefix="/deceased", tags=["Fallecidos"])
app.include_router(contratante_router, prefix="/contractors", tags=["Contratantes"])
app.include_router(reniec_router, prefix="/reniec", tags=["RENIEC"])
app.include_router(bitacora_router, prefix="/bitacora", tags=["Bitácora"])
app.include_router(drive_router, prefix="/drive", tags=["Google Drive"])