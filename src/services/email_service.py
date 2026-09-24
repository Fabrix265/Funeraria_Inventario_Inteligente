import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def enviar_correo(destinatario: str, asunto: str, cuerpo_html: str) -> bool:
    host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    port = int(os.getenv("SMTP_PORT", "587"))
    usuario = os.getenv("SMTP_USER", "")
    password = os.getenv("SMTP_PASSWORD", "").replace(" ", "")
    remitente = os.getenv("EMAIL_FROM", usuario)

    if not usuario or not password:
        print("ERROR: SMTP_USER / SMTP_PASSWORD no configurados en .env")
        return False

    mensaje = MIMEMultipart("alternative")
    mensaje["From"] = remitente
    mensaje["To"] = destinatario
    mensaje["Subject"] = asunto
    mensaje.attach(MIMEText(cuerpo_html, "html", "utf-8"))

    try:
        with smtplib.SMTP(host, port, timeout=15) as servidor:
            servidor.ehlo()
            servidor.starttls()
            servidor.login(usuario, password)
            servidor.sendmail(remitente, [destinatario], mensaje.as_string())
        return True
    except Exception as e:
        print(f"ERROR_ENVIANDO_EMAIL: {e}")
        return False