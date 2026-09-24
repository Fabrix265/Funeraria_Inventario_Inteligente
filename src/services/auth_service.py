import hashlib
import secrets
from datetime import datetime, timedelta
from sqlmodel import Session, select, func
from fastapi import HTTPException, status
from passlib.context import CryptContext
from src.models.user import User
from src.models.password_reset_token import PasswordResetToken
from src.core.security import create_access_token
from src.services.email_service import enviar_correo

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def _hash_token(token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    @classmethod
    def solicitar_recuperacion(cls, db: Session, email: str, app_url: str):
        user = db.exec(select(User).where(func.lower(User.email) == email.lower())).first()
        if not user:
            return False

        ahora = datetime.utcnow()
        tokens_pendientes = db.exec(
            select(PasswordResetToken)
            .where(PasswordResetToken.user_id == user.id, PasswordResetToken.usado_en.is_(None))
        ).all()
        for pendiente in tokens_pendientes:
            if pendiente.expira_en > ahora:
                db.delete(pendiente)
        db.commit()

        token_plano = secrets.token_urlsafe(32)
        registro = PasswordResetToken(
            user_id=user.id,
            token_hash=cls._hash_token(token_plano),
            expira_en=ahora + timedelta(hours=1),
        )
        db.add(registro)
        db.commit()

        enlace = f"{app_url}/restablecer?token={token_plano}"
        cuerpo_html = f"""
        <div style="font-family:Arial,sans-serif;max-width:560px;margin:auto;border:1px solid #e0e0e0;border-radius:8px;padding:24px;">
            <h2 style="margin-top:0;color:#0f172a;">Restablecer contraseña</h2>
            <p>Hola <strong>{user.username}</strong>:</p>
            <p>Recibimos una solicitud para restablecer tu contraseña. Haz clic en el botón para continuar:</p>
            <p style="text-align:center;">
                <a href="{enlace}" style="background:#0f172a;color:#ffffff;text-decoration:none;padding:12px 24px;border-radius:6px;display:inline-block;">Restablecer contraseña</a>
            </p>
            <p style="color:#666;font-size:13px;">Este enlace es válido por 1 hora. Si no solicitaste este cambio, ignora este correo.</p>
        </div>
        """
        enviar_correo(user.email, "Restablece tu contraseña", cuerpo_html)
        return True

    @classmethod
    def restablecer_contrasena(cls, db: Session, token: str, nueva_password: str):
        ahora = datetime.utcnow()
        registro = db.exec(
            select(PasswordResetToken).where(
                PasswordResetToken.token_hash == cls._hash_token(token),
                PasswordResetToken.expira_en > ahora,
                PasswordResetToken.usado_en.is_(None),
            )
        ).first()
        if not registro:
            raise HTTPException(
                status_code=400,
                detail="El enlace no es válido o ha expirado",
            )

        user = db.get(User, registro.user_id)
        if not user:
            raise HTTPException(
                status_code=400,
                detail="El enlace no es válido o ha expirado",
            )

        user.password = pwd_context.hash(nueva_password)
        registro.usado_en = ahora
        db.add(user)
        db.add(registro)
        db.commit()
        return {
            "message": "Contraseña actualizada correctamente",
            "usuario_id": user.id,
            "usuario_nombre": user.username,
        }

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

        if not user.activo:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="La cuenta está desactivada. Contacte al administrador.",
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
            "email": user.email,
            "roles": roles_usuario,
            "permisos": permisos_usuario
        }
        
        token = create_access_token(token_data)
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "roles": roles_usuario,
                "permisos": permisos_usuario
            }
        }