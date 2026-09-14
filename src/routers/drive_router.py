from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from src.deps.db_session import SessionDep
from src.core.security import decode_token
from src.schemas.drive import DriveAuthUrlResponse, DriveStatusResponse, DriveUploadResponse
from src.services.drive_service import GoogleDriveService

drive_router = APIRouter()


@drive_router.get("/auth-url", response_model=DriveAuthUrlResponse)
def obtener_url_auth(
    db: SessionDep,
    _token: dict = Depends(decode_token),
):
    service = GoogleDriveService(db)
    url = service.obtener_url_autorizacion()
    return DriveAuthUrlResponse(url=url)


@drive_router.get("/callback")
def drive_callback(code: str, db: SessionDep):
    service = GoogleDriveService(db)
    exito = service.intercambiar_codigo(code)
    if not exito:
        raise HTTPException(status_code=400, detail="No se pudieron intercambiar los tokens de Google")
    return {"message": "Conexion con Google Drive exitosa"}


@drive_router.get("/status", response_model=DriveStatusResponse)
def drive_status(
    db: SessionDep,
    _token: dict = Depends(decode_token),
):
    service = GoogleDriveService(db)
    return service.verificar_estado()


@drive_router.post("/upload", response_model=DriveUploadResponse)
def subir_archivo(
    db: SessionDep,
    file: UploadFile = File(...),
    carpeta: str = "servicios",
    _token: dict = Depends(decode_token),
):
    service = GoogleDriveService(db)
    file_bytes = file.file.read()
    resultado = service.subir_archivo(file_bytes, file.filename, carpeta)
    if not resultado:
        raise HTTPException(status_code=500, detail="No se pudo subir el archivo a Google Drive")
    return DriveUploadResponse(**resultado)
