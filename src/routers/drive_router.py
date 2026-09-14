from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Request
from src.deps.db_session import SessionDep
from src.core.security import decode_token
from src.schemas.drive import DriveAuthUrlResponse, DriveStatusResponse, DriveUploadResponse
from src.services.drive_service import GoogleDriveService
from src.services import bitacora_service

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
        raise HTTPException(status_code=400, detail="No se pudieron intercambiar los tokens de Google. Verifica que el codigo no haya expirado o sido usado ya.")
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
    request: Request,
    db: SessionDep,
    file: UploadFile = File(...),
    carpeta: str = "servicios",
    token: dict = Depends(decode_token),
):
    service = GoogleDriveService(db)
    file_bytes = file.file.read()
    resultado = service.subir_archivo(file_bytes, file.filename, carpeta)
    if not resultado:
        raise HTTPException(status_code=500, detail="No se pudo subir el archivo a Google Drive. Verifica la configuracion de GOOGLE_DRIVE_FOLDER_ID y que la autorizacion sea valida.")
    bitacora_service.registrar(
        db,
        usuario_id=int(token.get("sub")),
        usuario_nombre=token.get("username", ""),
        accion="crear",
        modulo="drive",
        detalle=f"Archivo '{file.filename}' subido a Drive carpeta '{carpeta}'",
        ip_address=request.client.host if request.client else None,
    )
    return DriveUploadResponse(**resultado)
