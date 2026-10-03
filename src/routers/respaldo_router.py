from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, Response

from src.core.security import CheckerPermisos, decode_token
from src.deps.db_session import SessionDep
from src.schemas.respaldo import (
    RespaldoConfigActualizar,
    RespaldoConfigLeer,
    RespaldoCrear,
    RespaldoEstadoLeer,
    RespaldoJobLeer,
    RespaldoListaResponse,
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
