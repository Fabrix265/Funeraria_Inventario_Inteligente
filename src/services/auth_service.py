from sqlmodel import Session, select
from fastapi import HTTPException, status
from passlib.context import CryptContext
from src.models.user import User
from src.core.security import create_access_token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @classmethod
    def login(cls, db: Session, username: str, password_plain: str):
        statement = select(User).where(User.username == username)
        user = db.exec(statement).first()

        if not user or not cls.verify_password(password_plain, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Nombre de usuario o contraseña incorrectos",
                headers={"WWW-Authenticate": "Bearer"},
            )

        roles_usuario = [rol.nombre for rol in user.roles]

        permisos_usuario = list(set(
            permiso.nombre
            for rol in user.roles
            for permiso in rol.permisos
        ))

        token_data = {
            "sub": str(user.id),
            "username": user.username,
            "roles": roles_usuario,
            "permisos": permisos_usuario
        }
        
        token = create_access_token(token_data)
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "username": user.username,
                "roles": roles_usuario,
                "permisos": permisos_usuario
            }
        }