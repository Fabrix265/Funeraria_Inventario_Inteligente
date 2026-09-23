import os
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordRequestForm
from src.deps.db_session import SessionDep
from src.services.auth_service import AuthService
from src.deps.limiter import limiter
from src.services import bitacora_service
from src.schemas.auth import RecuperarRequest, ResetPasswordRequest

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

@limiter.limit("5/minute")
@auth_router.post("/password-recovery")
def recuperar_contrasena(
    request: Request,
    datos: RecuperarRequest,
    db: SessionDep,
):
    app_url = os.getenv("APP_URL", "http://localhost:4200")
    encontrado = AuthService.solicitar_recuperacion(db, datos.email, app_url)
    bitacora_service.registrar(
        db,
        usuario_id=None,
        usuario_nombre="",
        accion="solicitud_recuperacion",
        modulo="auth",
        detalle=(
            f"Solicitud de restablecimiento para {datos.email.lower()}"
            if encontrado
            else "Solicitud de restablecimiento para correo no registrado"
        ),
        ip_address=request.client.host if request.client else None,
    )
    return {
        "message": "Si el correo está registrado, recibirás un enlace para restablecer tu contraseña."
    }

@limiter.limit("5/minute")
@auth_router.post("/reset-password")
def restablecer_contrasena(
    request: Request,
    datos: ResetPasswordRequest,
    db: SessionDep,
):
    resultado = AuthService.restablecer_contrasena(db, datos.token, datos.password)
    bitacora_service.registrar(
        db,
        usuario_id=resultado.get("usuario_id"),
        usuario_nombre=resultado.get("usuario_nombre", ""),
        accion="password_reset",
        modulo="auth",
        detalle="Contraseña restablecida correctamente",
        ip_address=request.client.host if request.client else None,
    )
    return {"message": resultado["message"]}