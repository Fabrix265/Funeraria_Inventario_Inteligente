from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
import os
from dotenv import load_dotenv
from sqlmodel import Session, select
from src.config.db import engine
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

def decode_token(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        payload = jwt.decode(token, SECURITY_KEY, algorithms=[ALGORITHM])
        if payload.get("sub") is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido: falta identificación de usuario",
            )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión expirada o token inválido. Por favor, inicie sesión nuevamente.",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_db():
    with Session(engine) as session:
        yield session

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