from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordRequestForm
from src.deps.db_session import SessionDep
from src.services.auth_service import AuthService
from src.deps.limiter import limiter
from src.services import bitacora_service

auth_router = APIRouter()

@limiter.limit("6/minute")
@auth_router.post("/login")
def login(
    request: Request,
    db: SessionDep, 
    form_data: OAuth2PasswordRequestForm = Depends()
):
    try:
        resultado = AuthService.login(
            db, 
            username=form_data.username, 
            password_plain=form_data.password
        )
        bitacora_service.registrar(
            db,
            usuario_id=resultado["user"].get("user_id"),
            usuario_nombre=form_data.username,
            accion="login_exitoso",
            modulo="auth",
            detalle="Inicio de sesion exitoso",
            ip_address=request.client.host if request.client else None,
        )
        return resultado
    except Exception:
        bitacora_service.registrar(
            db,
            usuario_id=None,
            usuario_nombre=form_data.username,
            accion="login_fallido",
            modulo="auth",
            detalle="Credenciales invalidas",
            ip_address=request.client.host if request.client else None,
        )
        raise