from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
import os
from dotenv import load_dotenv
from sqlmodel import Session, select
from src.config.db import engine
from src.deps.db_session import get_db
from src.models.user import User, Role, Permission, UserRoleLink, RolePermissionLink

load_dotenv()

SECURITY_KEY = os.getenv("SECURITY_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 8

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECURITY_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> dict:
    try:
        payload = jwt.decode(token, SECURITY_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión expirada o token inválido. Por favor, inicie sesión nuevamente.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if payload.get("sub") is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido: falta identificación de usuario",
        )

    try:
        user_id = int(payload.get("sub"))
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido: identificación de usuario ilegible",
        )

    usuario = db.get(User, user_id)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="La cuenta ya no existe. Por favor, inicie sesión nuevamente.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="La cuenta está desactivada. Contacte al administrador.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        version_token = int(payload.get("ver", 0))
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido: versión de sesión ilegible",
        )

    if version_token != usuario.token_version:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tu sesión fue cerrada. Por favor, inicie sesión nuevamente.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload

class CheckerPermisos:
    def __init__(self, permiso_requerido: str):
        self.permiso_requerido = permiso_requerido

    def __call__(self, token: dict = Depends(decode_token), db: Session = Depends(get_db)):
        user_id = int(token.get("sub"))

        statement = (
            select(Permission)
            .join(RolePermissionLink, RolePermissionLink.permission_id == Permission.id)
            .join(Role, Role.id == RolePermissionLink.role_id)
            .join(UserRoleLink, UserRoleLink.role_id == Role.id)
            .where(UserRoleLink.user_id == user_id)
            .where(Permission.nombre == self.permiso_requerido)
        )

        permiso_encontrado = db.exec(statement).first()

        if not permiso_encontrado:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No tienes el permiso necesario: '{self.permiso_requerido}'"
            )

        return token