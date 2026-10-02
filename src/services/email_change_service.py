import hashlib
import hmac
import logging
import os
import secrets
import string
from datetime import datetime, timedelta
from typing import List

from fastapi import HTTPException, status
from sqlmodel import Session, func, select

from src.models.email_change_request import EmailChangeRequest
from src.models.user import User
from src.services.auth_service import AuthService
from src.services.email_service import enviar_correo

logger = logging.getLogger(__name__)

LONGITUD_CODIGO = 6
TTL_MINUTOS = 10
MAX_INTENTOS = 5


class EmailChangeService:

    @staticmethod
    def _hash_codigo(user_id: int, codigo: str) -> str:
        secreto = os.getenv("SECURITY_KEY", "").encode("utf-8")
        return hmac.new(
            secreto, f"{user_id}:{codigo}".encode("utf-8"), hashlib.sha256
        ).hexdigest()

    @staticmethod
    def _generar_codigo() -> str:
        return "".join(secrets.choice(string.digits) for _ in range(LONGITUD_CODIGO))

    @staticmethod
    def email_disponible(db: Session, email: str, excluir_user_id: int) -> bool:
        statement = (
            select(User)
            .where(func.lower(User.email) == email.lower())
            .where(User.id != excluir_user_id)
        )
        return db.exec(statement).first() is None

    @staticmethod
    def _html_codigo(username: str, codigo: str) -> str:
        return f"""
        <div style="font-family:Arial,sans-serif;max-width:560px;margin:auto;border:1px solid #e0e0e0;border-radius:8px;padding:24px;">
            <h2 style="margin-top:0;color:#0f172a;">Confirma tu nuevo correo</h2>
            <p>Hola <strong>{username}</strong>:</p>
            <p>Escribe este código en la aplicación para confirmar el cambio de correo de tu cuenta:</p>
            <p style="text-align:center;">
                <span style="display:inline-block;background:#0f172a;color:#ffffff;font-size:28px;letter-spacing:10px;padding:16px 28px;border-radius:6px;">{codigo}</span>
            </p>
            <p style="color:#666;font-size:13px;">Este código es válido por {TTL_MINUTOS} minutos. Si no solicitaste este cambio, ignora este correo: tu cuenta seguirá con el correo anterior.</p>
        </div>
        """

    @staticmethod
    def _texto_codigo(username: str, codigo: str) -> str:
        return (
            f"Hola {username},\n\n"
            f"Escribe este código en la aplicación para confirmar el cambio de correo "
            f"de tu cuenta:\n\n"
            f"    {codigo}\n\n"
            f"El código es válido por {TTL_MINUTOS} minutos. Si no solicitaste este "
            f"cambio, ignora este correo: tu cuenta seguirá con el correo anterior."
        )

    @staticmethod
    def _html_cambio(username: str, email_anterior: str, email_nuevo: str) -> str:
        return f"""
        <div style="font-family:Arial,sans-serif;max-width:560px;margin:auto;border:1px solid #e0e0e0;border-radius:8px;padding:24px;">
            <h2 style="margin-top:0;color:#0f172a;">El correo de tu cuenta fue cambiado</h2>
            <p>Hola <strong>{username}</strong>:</p>
            <p>El correo de recuperación de tu cuenta acaba de cambiar:</p>
            <p>
                Anterior: <span style="color:#666;">{email_anterior}</span><br>
                Nuevo: <strong>{email_nuevo}</strong>
            </p>
            <p style="color:#666;font-size:13px;">Si no fuiste tú, cambia tu contraseña de inmediato y comunícate con el administrador de la funeraria.</p>
        </div>
        """

    @staticmethod
    def _texto_cambio(username: str, email_anterior: str, email_nuevo: str) -> str:
        return (
            f"Hola {username},\n\n"
            f"El correo de recuperación de tu cuenta acaba de cambiar:\n\n"
            f"    Anterior: {email_anterior}\n"
            f"    Nuevo:     {email_nuevo}\n\n"
            f"Si no fuiste tu, cambia tu contrasena de inmediato y comunicate con el "
            f"administrador de la funeraria."
        )

    @classmethod
    def _pendientes(cls, db: Session, user_id: int) -> List[EmailChangeRequest]:
        return list(
            db.exec(
                select(EmailChangeRequest).where(
                    EmailChangeRequest.user_id == user_id,
                    EmailChangeRequest.usado_en.is_(None),
                )
            ).all()
        )

    @classmethod
    def _descartar_pendientes(cls, db: Session, user_id: int) -> None:
        for pendiente in cls._pendientes(db, user_id):
            db.delete(pendiente)
        db.commit()

    @classmethod
    def solicitar(cls, db: Session, user_id: int, email_nuevo: str, password_actual: str) -> None:
        user = db.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        if not user.activo:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="La cuenta está desactivada. Contacte al administrador.",
            )

        if not AuthService.verify_password(password_actual, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="La contraseña actual es incorrecta",
            )

        email_nuevo = email_nuevo.strip().lower()
        if email_nuevo == user.email.lower():
            raise HTTPException(status_code=400, detail="El nuevo correo es igual al actual")
        if not cls.email_disponible(db, email_nuevo, user_id):
            raise HTTPException(status_code=400, detail="El correo ya está en uso")

        cls._descartar_pendientes(db, user_id)

        codigo = cls._generar_codigo()
        solicitud = EmailChangeRequest(
            user_id=user.id,
            email_anterior=user.email,
            email_nuevo=email_nuevo,
            codigo_hash=cls._hash_codigo(user.id, codigo),
            expira_en=datetime.utcnow() + timedelta(minutes=TTL_MINUTOS),
        )
        db.add(solicitud)
        db.commit()

        if not enviar_correo(
            email_nuevo,
            "Confirma tu nuevo correo",
            cls._html_codigo(user.username, codigo),
            cls._texto_codigo(user.username, codigo),
        ):
            logger.error("No se pudo enviar el codigo de cambio de correo a %s", email_nuevo)

    @classmethod
    def confirmar(
        cls, db: Session, user_id: int, email_nuevo: str, codigo: str
    ) -> tuple[User, str]:
        email_nuevo = email_nuevo.strip().lower()
        ahora = datetime.utcnow()

        vigente = [
            pendiente
            for pendiente in cls._pendientes(db, user_id)
            if pendiente.email_nuevo == email_nuevo
            and pendiente.expira_en > ahora
        ]
        if not vigente:
            raise HTTPException(
                status_code=400, detail="El código no es válido o ha expirado"
            )
        registro = vigente[0]

        if registro.intentos >= MAX_INTENTOS:
            raise HTTPException(
                status_code=400,
                detail="Demasiados intentos fallidos. Solicita un código nuevo.",
            )

        if not hmac.compare_digest(
            registro.codigo_hash, cls._hash_codigo(user_id, codigo.strip())
        ):
            registro.intentos += 1
            db.add(registro)
            db.commit()
            raise HTTPException(
                status_code=400, detail="El código no es válido o ha expirado"
            )

        user = db.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        if not cls.email_disponible(db, email_nuevo, user_id):
            raise HTTPException(status_code=400, detail="El correo ya está en uso")

        email_anterior = user.email
        user.email = email_nuevo
        user.token_version += 1
        registro.usado_en = ahora
        db.add(user)
        db.add(registro)
        db.commit()
        db.refresh(user)

        if not enviar_correo(
            email_anterior,
            "El correo de tu cuenta fue cambiado",
            cls._html_cambio(user.username, email_anterior, email_nuevo),
            cls._texto_cambio(user.username, email_anterior, email_nuevo),
        ):
            logger.error("No se pudo notificar el cambio de correo a %s", email_anterior)

        return user, email_anterior

    @classmethod
    def cancelar(cls, db: Session, user_id: int) -> None:
        cls._descartar_pendientes(db, user_id)
