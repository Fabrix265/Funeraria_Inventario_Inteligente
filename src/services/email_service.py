import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

logger = logging.getLogger(__name__)


def enviar_correo(
    destinatario: str,
    asunto: str,
    cuerpo_html: str,
    cuerpo_texto: Optional[str] = None,
) -> bool:
    host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    port = int(os.getenv("SMTP_PORT", "587"))
    usuario = os.getenv("SMTP_USER", "")
    password = os.getenv("SMTP_PASSWORD", "").replace(" ", "")
    remitente = os.getenv("EMAIL_FROM", usuario)

    if not usuario or not password:
        logger.error("SMTP_USER / SMTP_PASSWORD no configurados en .env")
        return False

    mensaje = MIMEMultipart("alternative")
    mensaje["From"] = remitente
    mensaje["To"] = destinatario
    mensaje["Subject"] = asunto
    if cuerpo_texto:
        mensaje.attach(MIMEText(cuerpo_texto, "plain", "utf-8"))
    mensaje.attach(MIMEText(cuerpo_html, "html", "utf-8"))

    try:
        with smtplib.SMTP(host, port, timeout=15) as servidor:
            servidor.ehlo()
            servidor.starttls()
            servidor.login(usuario, password)
            servidor.sendmail(remitente, [destinatario], mensaje.as_string())
        return True
    except Exception as e:
        logger.error("No se pudo enviar el correo a %s: %s", destinatario, str(e))
        return False
