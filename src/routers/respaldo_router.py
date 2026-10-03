from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, Response

from src.core.security import CheckerPermisos, decode_token
from src.deps.db_session import SessionDep
from src.deps.limiter import limiter
from src.schemas.respaldo import (
    RespaldoConfigActualizar,
    RespaldoConfigLeer,
    RespaldoCrear,
    RespaldoEstadoLeer,
    RespaldoJobLeer,
    RespaldoListaResponse,
    RestaurarRespaldo,
    TokenRestauracionLeer,
)
from src.services import backup_jobs, bitacora_service, respaldo_service

respaldo_router = APIRouter()


@respaldo_router.get(
    "/estado",
    response_model=RespaldoEstadoLeer,
    dependencies=[Depends(CheckerPermisos("respaldos:listar"))],
)
def obtener_estado(db: SessionDep):
    """Todo lo que la pantalla de respaldos necesita al abrirse."""
    return respaldo_service.estado(db)


@respaldo_router.get(
    "/config",
    response_model=RespaldoConfigLeer,
    dependencies=[Depends(CheckerPermisos("respaldos:listar"))],
)
def obtener_config(db: SessionDep):
    return respaldo_service.obtener_config(db)


@respaldo_router.put(
    "/config",
    response_model=RespaldoConfigLeer,
    dependencies=[Depends(CheckerPermisos("respaldos:crear"))],
)
def actualizar_config(
    datos: RespaldoConfigActualizar,
    db: SessionDep,
    request: Request,
    token: dict = Depends(decode_token),
):
    config = respaldo_service.actualizar_config(
        db, datos.model_dump(exclude_unset=True)
    )
    bitacora_service.registrar(
        db,
        usuario_id=int(token.get("sub")),
        usuario_nombre=token.get("username", ""),
        accion="actualizar",
        modulo="respaldos",
        detalle=(
            f"Política de respaldos ajustada (frecuencia cada {config.frecuencia_dias} día(s), "
            f"máximo {config.maximo_respaldos} respaldos)"
        ),
        ip_address=request.client.host if request.client else None,
    )
    return config


@respaldo_router.get(
    "/jobs/{job_id}",
    response_model=RespaldoJobLeer,
    dependencies=[Depends(CheckerPermisos("respaldos:listar"))],
)
def obtener_job(job_id: str):
    job = backup_jobs.obtener(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"No existe el trabajo '{job_id}'")
    return job.a_dict()


@respaldo_router.get(
    "/",
    response_model=RespaldoListaResponse,
    dependencies=[Depends(CheckerPermisos("respaldos:listar"))],
)
def listar_respaldos(db: SessionDep):
    respaldos = respaldo_service.listar(db)
    items = [respaldo_service.a_respaldo_leer(r) for r in respaldos]
    return RespaldoListaResponse(items=items, total=len(items))


@respaldo_router.post(
    "/resincronizar",
    dependencies=[Depends(CheckerPermisos("respaldos:listar"))],
)
def resincronizar(db: SessionDep, request: Request, token: dict = Depends(decode_token)):
    """Vuelve a armar la lista de respaldos a partir de los manifiestos de Drive."""
    return respaldo_service.resincronizar(
        db,
        usuario_id=int(token.get("sub")),
        usuario_nombre=token.get("username", ""),
        ip_address=request.client.host if request.client else None,
    )


@respaldo_router.delete(
    "/{respaldo_id}",
    dependencies=[Depends(CheckerPermisos("respaldos:eliminar"))],
)
def eliminar_respaldo(
    respaldo_id: int,
    db: SessionDep,
    request: Request,
    token: dict = Depends(decode_token),
):
    return respaldo_service.eliminar(
        db,
        respaldo_id,
        usuario_id=int(token.get("sub")),
        usuario_nombre=token.get("username", ""),
        ip_address=request.client.host if request.client else None,
    )


@respaldo_router.post(
    "/",
    status_code=202,
    dependencies=[Depends(CheckerPermisos("respaldos:crear"))],
)
def generar_respaldo(
    background_tasks: BackgroundTasks,
    request: Request,
    datos: Optional[RespaldoCrear] = None,
    token: dict = Depends(decode_token),
):
    """Lanza el respaldo completo (base de datos + documentos) y responde de
    inmediato con el id del trabajo, para que la interfaz pueda ir siguiéndolo."""
    if backup_jobs.en_ejecucion():
        raise HTTPException(
            status_code=409,
            detail="Ya hay un respaldo o una restauración en curso. Espera a que termine.",
        )

    job = respaldo_service.crear_job()
    background_tasks.add_task(
        respaldo_service.tarea_crear,
        job.job_id,
        int(token.get("sub")),
        token.get("username", ""),
        datos.observacion if datos else None,
        request.client.host if request.client else None,
    )
    return job.a_dict()


@limiter.limit("5/minute")
@respaldo_router.post(
    "/{respaldo_id}/codigo",
    response_model=TokenRestauracionLeer,
    dependencies=[Depends(CheckerPermisos("respaldos:restaurar"))],
)
def solicitar_codigo(
    respaldo_id: int,
    request: Request,
    db: SessionDep,
    token: dict = Depends(decode_token),
):
    """Primer paso de la restauración: emite el código de confirmación.

    Se muestra una sola vez en la interfaz y caduca en unos minutos.
    """
    return respaldo_service.generar_codigo(
        db,
        respaldo_id,
        usuario_id=int(token.get("sub")),
        usuario_nombre=token.get("username", ""),
        ip_address=request.client.host if request.client else None,
    )


@respaldo_router.post(
    "/{respaldo_id}/restaurar",
    status_code=202,
    dependencies=[Depends(CheckerPermisos("respaldos:restaurar"))],
)
def restaurar_respaldo(
    respaldo_id: int,
    datos: RestaurarRespaldo,
    background_tasks: BackgroundTasks,
    request: Request,
    db: SessionDep,
    token: dict = Depends(decode_token),
):
    """Segundo paso: valida la doble confirmación y lanza la restauración."""
    if datos.confirmacion != str(respaldo_id):
        raise HTTPException(
            status_code=400,
            detail=f"La confirmación no coincide. Debes escribir {respaldo_id}.",
        )

    respaldo_service.validar_codigo(
        db, respaldo_id, datos.token, int(token.get("sub"))
    )

    if backup_jobs.en_ejecucion():
        raise HTTPException(
            status_code=409,
            detail="Ya hay un respaldo o una restauración en curso. Espera a que termine.",
        )

    bitacora_service.registrar(
        db,
        usuario_id=int(token.get("sub")),
        usuario_nombre=token.get("username", ""),
        accion="restaurar",
        modulo="respaldos",
        detalle=f"Solicitud de restauración del respaldo #{respaldo_id}",
        ip_address=request.client.host if request.client else None,
    )
    # Liberamos la sesión antes de reconstruir las tablas: una transacción
    # abierta bloquearía el DROP TABLE de la restauración.
    db.close()

    job = respaldo_service.crear_job_restauracion(respaldo_id)
    background_tasks.add_task(
        respaldo_service.tarea_restaurar,
        job.job_id,
        respaldo_id,
        int(token.get("sub")),
        token.get("username", ""),
        token.get("ver"),
        datos.restaurar_archivos,
        request.client.host if request.client else None,
    )
    return job.a_dict()


@respaldo_router.post(
    "/{respaldo_id}/recuperar-archivos",
    status_code=202,
    dependencies=[Depends(CheckerPermisos("respaldos:restaurar"))],
)
def recuperar_archivos(
    respaldo_id: int,
    background_tasks: BackgroundTasks,
    request: Request,
    db: SessionDep,
    token: dict = Depends(decode_token),
):
    """Repite solo el snapshot de documentos, sin tocar la base de datos."""
    respaldo_service.obtener(db, respaldo_id)
    if backup_jobs.en_ejecucion():
        raise HTTPException(
            status_code=409,
            detail="Ya hay un respaldo o una restauración en curso. Espera a que termine.",
        )

    job = respaldo_service.crear_job_recuperacion(respaldo_id)
    background_tasks.add_task(
        respaldo_service.tarea_recuperar,
        job.job_id,
        respaldo_id,
        int(token.get("sub")),
        token.get("username", ""),
        request.client.host if request.client else None,
    )
    return job.a_dict()


@respaldo_router.get(
    "/{respaldo_id}/descargar",
    dependencies=[Depends(CheckerPermisos("respaldos:listar"))],
)
def descargar_respaldo(
    respaldo_id: int,
    db: SessionDep,
    request: Request,
    token: dict = Depends(decode_token),
):
    datos, nombre = respaldo_service.descargar(db, respaldo_id)

    bitacora_service.registrar(
        db,
        usuario_id=int(token.get("sub")),
        usuario_nombre=token.get("username", ""),
        accion="descargar",
        modulo="respaldos",
        detalle=f"Respaldo #{respaldo_id} descargado ({nombre})",
        ip_address=request.client.host if request.client else None,
    )

    return Response(
        content=datos,
        media_type="application/sql",
        headers={"Content-Disposition": f'attachment; filename="{nombre}"'},
    )
