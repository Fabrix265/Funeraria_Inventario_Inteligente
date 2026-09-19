import os
import io
import logging
from datetime import datetime
from typing import Optional
from urllib.parse import urlencode

from sqlmodel import Session, select
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload

from src.models.oauth_token import OAuthToken

logger = logging.getLogger(__name__)


class _BytesIODownloader:
    """Helper to download Google Drive files into a BytesIO buffer."""

    def __init__(self, request, buffer):
        self._request = request
        self._buffer = buffer
        self._done = False

    def next_chunk(self):
        while not self._done:
            status, done = self._request.next_chunk()
            if status:
                self._buffer.write(status)
            self._done = done


SCOPES = ["https://www.googleapis.com/auth/drive.file"]


class GoogleDriveService:
    def __init__(self, db: Session):
        self.db = db
        self.CLIENT_ID = os.getenv("GOOGLE_DRIVE_CLIENT_ID", "")
        self.CLIENT_SECRET = os.getenv("GOOGLE_DRIVE_CLIENT_SECRET", "")
        self.REDIRECT_URI = os.getenv("GOOGLE_DRIVE_REDIRECT_URI", "http://localhost:8000/drive/callback")
        self.FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID", "")

    def obtener_url_autorizacion(self) -> str:
        params = {
            "client_id": self.CLIENT_ID,
            "redirect_uri": self.REDIRECT_URI,
            "response_type": "code",
            "scope": " ".join(SCOPES),
            "access_type": "offline",
            "prompt": "consent",
        }
        return "https://accounts.google.com/o/oauth2/auth?" + urlencode(params)

    def intercambiar_codigo(self, code: str) -> bool:
        import httpx

        response = httpx.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": self.CLIENT_ID,
                "client_secret": self.CLIENT_SECRET,
                "redirect_uri": self.REDIRECT_URI,
                "grant_type": "authorization_code",
            },
        )
        if response.status_code != 200:
            logger.error("Error intercambiando codigo de Google: %s - %s", response.status_code, response.text)
            return False

        tokens = response.json()
        expiry = None
        if "expires_in" in tokens:
            expiry = datetime.utcnow().timestamp() + tokens["expires_in"]
            expiry = datetime.utcfromtimestamp(expiry)

        token_existente = self.db.exec(
            select(OAuthToken).where(OAuthToken.proveedor == "google_drive")
        ).first()

        if token_existente:
            token_existente.access_token = tokens["access_token"]
            token_existente.refresh_token = tokens.get("refresh_token", token_existente.refresh_token)
            token_existente.token_expiry = expiry
            self.db.add(token_existente)
        else:
            nuevo_token = OAuthToken(
                proveedor="google_drive",
                access_token=tokens["access_token"],
                refresh_token=tokens.get("refresh_token", ""),
                token_expiry=expiry,
            )
            self.db.add(nuevo_token)

        self.db.commit()
        return True

    def _obtener_credenciales(self) -> Optional[Credentials]:
        token = self.db.exec(
            select(OAuthToken).where(OAuthToken.proveedor == "google_drive")
        ).first()

        if not token:
            return None

        creds = Credentials(
            token=token.access_token,
            refresh_token=token.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=self.CLIENT_ID,
            client_secret=self.CLIENT_SECRET,
            scopes=SCOPES,
        )

        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            token.access_token = creds.token
            if creds.expiry:
                token.token_expiry = creds.expiry
            self.db.add(token)
            self.db.commit()

        return creds

    def _asegurar_carpeta(self, service, parent_id: str, nombre_carpeta: str) -> str:
        query = (
            f"name='{nombre_carpeta}' and "
            f"'{parent_id}' in parents and "
            f"mimeType='application/vnd.google-apps.folder' and "
            f"trashed=false"
        )
        results = service.files().list(q=query, fields="files(id)").execute()
        items = results.get("files", [])
        if items:
            return items[0]["id"]

        file_metadata = {
            "name": nombre_carpeta,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [parent_id],
        }
        file = service.files().create(body=file_metadata, fields="id").execute()
        return file["id"]

    def subir_archivo(
        self,
        file_bytes: bytes,
        filename: str,
        carpeta: str = "servicios",
    ) -> Optional[dict]:
        creds = self._obtener_credenciales()
        if not creds:
            logger.error("No hay credenciales de Google Drive configuradas")
            return None

        try:
            service = build("drive", "v3", credentials=creds)

            parent_id = self.FOLDER_ID
            for parte in carpeta.split("/"):
                if parte:
                    parent_id = self._asegurar_carpeta(service, parent_id, parte)

            ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
            mime_map = {
                "pdf": "application/pdf",
                "png": "image/png",
                "jpg": "image/jpeg",
                "jpeg": "image/jpeg",
                "doc": "application/msword",
                "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            }
            mime_type = mime_map.get(ext, "application/octet-stream")

            media = MediaIoBaseUpload(
                io.BytesIO(file_bytes),
                mimetype=mime_type,
                resumable=True,
            )

            file_metadata = {
                "name": filename,
                "parents": [parent_id],
            }

            file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields="id",
            ).execute()

            file_id = file["id"]
            url = f"https://drive.google.com/uc?id={file_id}"

            return {
                "file_id": file_id,
                "url": url,
                "filename": filename,
            }
        except Exception as e:
            logger.error("Error subiendo archivo a Google Drive: %s", str(e))
            return None

    def obtener_url_archivo(self, file_id: str) -> str:
        return f"https://drive.google.com/uc?id={file_id}"

    def descargar_archivo(self, file_id: str) -> Optional[bytes]:
        creds = self._obtener_credenciales()
        if not creds:
            return None
        try:
            service = build("drive", "v3", credentials=creds)
            request = service.files().get_media(fileId=file_id)
            buffer = io.BytesIO()
            downloader = MediaIoBaseDownload(buffer, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
            return buffer.getvalue()
        except Exception as e:
            logger.error("Error descargando archivo de Drive: %s", str(e))
            return None

    def eliminar_archivo(self, file_id: str) -> bool:
        creds = self._obtener_credenciales()
        if not creds:
            return False
        try:
            service = build("drive", "v3", credentials=creds)
            service.files().delete(fileId=file_id).execute()
            return True
        except Exception as e:
            logger.error("Error eliminando archivo de Drive: %s", str(e))
            return False

    def reemplazar_archivo(
        self,
        file_id: str,
        file_bytes: bytes,
        filename: str,
    ) -> Optional[dict]:
        creds = self._obtener_credenciales()
        if not creds:
            return None
        try:
            service = build("drive", "v3", credentials=creds)

            ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
            mime_map = {
                "pdf": "application/pdf",
                "png": "image/png",
                "jpg": "image/jpeg",
                "jpeg": "image/jpeg",
            }
            mime_type = mime_map.get(ext, "application/octet-stream")

            media = MediaIoBaseUpload(
                io.BytesIO(file_bytes),
                mimetype=mime_type,
                resumable=True,
            )

            service.files().update(
                fileId=file_id,
                body={"name": filename},
                media_body=media,
            ).execute()

            return {
                "file_id": file_id,
                "url": self.obtener_url_archivo(file_id),
                "filename": filename,
            }
        except Exception as e:
            logger.error("Error reemplazando archivo en Drive: %s", str(e))
            return None

    def verificar_estado(self) -> dict:
        token = self.db.exec(
            select(OAuthToken).where(OAuthToken.proveedor == "google_drive")
        ).first()

        if not token:
            return {"autorizado": False, "expira_en": None}

        expira_str = None
        if token.token_expiry:
            expira_str = token.token_expiry.isoformat()

        return {
            "autorizado": True,
            "expira_en": expira_str,
        }
