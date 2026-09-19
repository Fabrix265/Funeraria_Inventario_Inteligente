from fastapi import APIRouter, Depends, UploadFile, File, Form, Request, Response
from typing import Optional
from src.deps.db_session import SessionDep
from src.core.security import CheckerPermisos, decode_token
from src.models.servicio_archivo import TipoArchivo, ServicioArchivo
from src.schemas.servicio_archivo import ServicioArchivoRead, ServicioArchivosResponse
from src.services import archivo_service, bitacora_service

archivo_router = APIRouter()


@archivo_router.get(
    "/servicios/{servicio_id}/archivos",
    response_model=ServicioArchivosResponse,
    dependencies=[Depends(CheckerPermisos("archivos:ver"))],
)
def listar_archivos(servicio_id: int, db: SessionDep):
    archivos = archivo_service.listar_archivos(db, servicio_id)
    result = []
    for a in archivos:
        item = ServicioArchivoRead.model_validate(a)
        if a.usuario:
            item.usuario_nombre = a.usuario.username
        result.append(item)
    return ServicioArchivosResponse(archivos=result)


@archivo_router.post(
    "/servicios/{servicio_id}/archivos",
    response_model=ServicioArchivoRead,
    status_code=201,
)
def subir_archivo(
    servicio_id: int,
    db: SessionDep,
    request: Request,
    tipo: TipoArchivo = Form(...),
    file: UploadFile = File(...),
    token: dict = Depends(CheckerPermisos("archivos:subir")),
):
    file_bytes = file.file.read()
    usuario_id = int(token.get("sub"))
    usuario_nombre = token.get("username", "")

    archivo = archivo_service.subir_archivo(
        db,
        servicio_id,
        tipo,
        file_bytes,
        file.filename or "sin_nombre",
        file.content_type or "application/octet-stream",
        usuario_id,
        usuario_nombre,
    )

    bitacora_service.registrar(
        db,
        usuario_id=usuario_id,
        usuario_nombre=usuario_nombre,
        accion="crear",
        modulo="archivos",
        detalle=f"{tipo.value} subido para servicio #{servicio_id}: {file.filename}",
        ip_address=request.client.host if request.client else None,
    )

    item = ServicioArchivoRead.model_validate(archivo)
    if archivo.usuario:
        item.usuario_nombre = archivo.usuario.username
    return item


@archivo_router.get(
    "/servicios/{servicio_id}/archivos/{archivo_id}/descargar",
    dependencies=[Depends(CheckerPermisos("archivos:ver"))],
)
def descargar_archivo(
    servicio_id: int,
    archivo_id: int,
    db: SessionDep,
    request: Request,
    token: dict = Depends(decode_token),
):
    file_bytes, mime_type, filename = archivo_service.descargar_archivo(db, archivo_id)

    bitacora_service.registrar(
        db,
        usuario_id=int(token.get("sub")),
        usuario_nombre=token.get("username", ""),
        accion="descargar",
        modulo="archivos",
        detalle=f"Archivo '{filename}' descargado del servicio #{servicio_id}",
        ip_address=request.client.host if request.client else None,
    )

    return Response(
        content=file_bytes,
        media_type=mime_type,
        headers={"Content-Disposition": f'inline; filename="{filename}"'},
    )


@archivo_router.put(
    "/servicios/{servicio_id}/archivos/{archivo_id}",
    response_model=ServicioArchivoRead,
)
def reemplazar_archivo(
    servicio_id: int,
    archivo_id: int,
    db: SessionDep,
    request: Request,
    file: UploadFile = File(...),
    token: dict = Depends(CheckerPermisos("archivos:editar")),
):
    file_bytes = file.file.read()
    usuario_id = int(token.get("sub"))
    usuario_nombre = token.get("username", "")

    archivo = archivo_service.reemplazar_archivo(
        db,
        archivo_id,
        file_bytes,
        file.filename or "sin_nombre",
        file.content_type or "application/octet-stream",
        usuario_id,
    )

    bitacora_service.registrar(
        db,
        usuario_id=usuario_id,
        usuario_nombre=usuario_nombre,
        accion="actualizar",
        modulo="archivos",
        detalle=f"Archivo reemplazado en servicio #{servicio_id}: {file.filename}",
        ip_address=request.client.host if request.client else None,
    )

    item = ServicioArchivoRead.model_validate(archivo)
    if archivo.usuario:
        item.usuario_nombre = archivo.usuario.username
    return item


@archivo_router.delete(
    "/servicios/{servicio_id}/archivos/{archivo_id}",
    dependencies=[Depends(CheckerPermisos("archivos:eliminar"))],
)
def eliminar_archivo(
    servicio_id: int,
    archivo_id: int,
    db: SessionDep,
    request: Request,
    token: dict = Depends(decode_token),
):
    archivo = db.get(ServicioArchivo, archivo_id)
    nombre = archivo.nombre_original if archivo else "desconocido"

    resultado = archivo_service.eliminar_archivo(db, archivo_id)

    bitacora_service.registrar(
        db,
        usuario_id=int(token.get("sub")),
        usuario_nombre=token.get("username", ""),
        accion="eliminar",
        modulo="archivos",
        detalle=f"Archivo '{nombre}' eliminado del servicio #{servicio_id}",
        ip_address=request.client.host if request.client else None,
    )

    return resultado
