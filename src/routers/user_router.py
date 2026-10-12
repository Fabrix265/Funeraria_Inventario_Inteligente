from fastapi import APIRouter, Depends, Query, Request
from typing import List, Optional
from src.deps.db_session import SessionDep
from src.core.security import decode_token, CheckerPermisos
from src.services.user_service import UserService
from src.schemas.user import UserLeer, UserCrear, UserActualizarSe, RoleLeer, UserActualizarAdmin, CambioEmailSolicitar, CambioEmailConfirmar
from src.schemas.estado import EstadoUpdate
from src.services import bitacora_service
from src.deps.limiter import limiter
from src.services.email_change_service import EmailChangeService

user_router = APIRouter()

@user_router.get("/roles", response_model=List[RoleLeer], dependencies=[Depends(decode_token)])
def listar_roles(db: SessionDep):
    return UserService.obtener_roles(db)

@user_router.post("/", response_model=UserLeer, dependencies=[Depends(CheckerPermisos("usuarios:crear"))])
def crear_usuario(
    request: Request,
    user_in: UserCrear, db: SessionDep,
    token: dict = Depends(CheckerPermisos("usuarios:crear")),
):
    resultado = UserService.crear_usuario(db, user_in)
    bitacora_service.registrar(
        db,
        usuario_id=int(token.get("sub")),
        usuario_nombre=token.get("username", ""),
        accion="crear",
        modulo="usuarios",
        detalle=f"Usuario '{user_in.username}' creado",
        ip_address=request.client.host if request.client else None,
    )
    return resultado

@user_router.get("/", response_model=List[UserLeer], dependencies=[Depends(CheckerPermisos("usuarios:listar"))])
def listar_usuarios(
    db: SessionDep,
    activo: Optional[bool] = Query(None),
):
    return UserService.obtener_usuarios(db, activo=activo)

@user_router.delete("/{user_id}", dependencies=[Depends(CheckerPermisos("usuarios:eliminar"))])
def eliminar_usuario(
    request: Request,
    user_id: int, db: SessionDep, token: dict = Depends(decode_token),
):
    current_user_id = int(token.get("sub"))
    resultado = UserService.eliminar_usuario(db, user_id, current_user_id)
    bitacora_service.registrar(
        db,
        usuario_id=current_user_id,
        usuario_nombre=token.get("username", ""),
        accion="eliminar",
        modulo="usuarios",
        detalle=f"Usuario #{user_id} eliminado",
        ip_address=request.client.host if request.client else None,
    )
    return resultado

@user_router.get("/me", response_model=UserLeer, dependencies=[Depends(decode_token)])
def obtener_mi_perfil(db: SessionDep, token: dict = Depends(decode_token)):
    return UserService.obtener_usuario(db, int(token.get("sub")))

@user_router.put("/me", response_model=UserLeer)
def editar_mi_perfil(
    request: Request,
    user_in: UserActualizarSe, db: SessionDep, token: dict = Depends(decode_token),
):
    user_id = int(token.get("sub"))
    antes = UserService.snapshot(UserService.obtener_usuario(db, user_id))
    resultado = UserService.actualizar_perfil(db, user_id, user_in)
    detalle = UserService.describir_cambios(antes, UserService.snapshot(resultado))
    bitacora_service.registrar(
        db,
        usuario_id=user_id,
        usuario_nombre=token.get("username", ""),
        accion="actualizar",
        modulo="usuarios",
        detalle=f"Perfil actualizado ({detalle})",
        ip_address=request.client.host if request.client else None,
    )
    return resultado

@limiter.limit("5/10minutes")
@user_router.post("/me/email-change")
def solicitar_cambio_email(
    request: Request,
    datos: CambioEmailSolicitar, db: SessionDep, token: dict = Depends(decode_token),
):
    user_id = int(token.get("sub"))
    EmailChangeService.solicitar(db, user_id, datos.email_nuevo, datos.password_actual)
    bitacora_service.registrar(
        db,
        usuario_id=user_id,
        usuario_nombre=token.get("username", ""),
        accion="email_cambio_solicitado",
        modulo="usuarios",
        detalle=f"Código de confirmación enviado para el correo {datos.email_nuevo.lower()}",
        ip_address=request.client.host if request.client else None,
    )
    return {"message": "Si los datos son correctos, recibirás un código en el nuevo correo."}

@limiter.limit("10/10minutes")
@user_router.post("/me/email-change/confirm", response_model=UserLeer)
def confirmar_cambio_email(
    request: Request,
    datos: CambioEmailConfirmar, db: SessionDep, token: dict = Depends(decode_token),
):
    user_id = int(token.get("sub"))
    usuario, email_anterior = EmailChangeService.confirmar(
        db, user_id, datos.email_nuevo, datos.codigo
    )
    bitacora_service.registrar(
        db,
        usuario_id=user_id,
        usuario_nombre=token.get("username", ""),
        accion="email_cambio_confirmado",
        modulo="usuarios",
        detalle=f"Correo cambiado: {email_anterior} → {usuario.email}",
        ip_address=request.client.host if request.client else None,
    )
    return usuario

@user_router.delete("/me/email-change")
def cancelar_cambio_email(
    request: Request, db: SessionDep, token: dict = Depends(decode_token),
):
    user_id = int(token.get("sub"))
    EmailChangeService.cancelar(db, user_id)
    bitacora_service.registrar(
        db,
        usuario_id=user_id,
        usuario_nombre=token.get("username", ""),
        accion="email_cambio_cancelado",
        modulo="usuarios",
        detalle="Cambio de correo pendiente cancelado",
        ip_address=request.client.host if request.client else None,
    )
    return {"message": "Cambio de correo cancelado"}

@user_router.put("/{user_id}", response_model=UserLeer, dependencies=[Depends(CheckerPermisos("usuarios:crear"))])
def actualizar_usuario_como_administrador(
    request: Request,
    user_id: int, user_in: UserActualizarAdmin, db: SessionDep,
    token: dict = Depends(CheckerPermisos("usuarios:crear")),
):
    antes = UserService.snapshot(UserService.obtener_usuario(db, user_id))
    resultado = UserService.actualizar_usuario_por_admin(db, user_id, user_in)
    detalle = UserService.describir_cambios(antes, UserService.snapshot(resultado))
    bitacora_service.registrar(
        db,
        usuario_id=int(token.get("sub")),
        usuario_nombre=token.get("username", ""),
        accion="actualizar",
        modulo="usuarios",
        detalle=f"Usuario #{user_id} actualizado por administrador ({detalle})",
        ip_address=request.client.host if request.client else None,
    )
    return resultado

@user_router.patch("/{user_id}/status", response_model=UserLeer, dependencies=[Depends(CheckerPermisos("usuarios:crear"))])
def cambiar_estado_usuario(
    request: Request,
    user_id: int, datos: EstadoUpdate, db: SessionDep, token: dict = Depends(decode_token),
):
    current_user_id = int(token.get("sub"))
    resultado = UserService.cambiar_estado(db, user_id, datos.activo, current_user_id)
    estado = "activado" if datos.activo else "desactivado"
    bitacora_service.registrar(
        db,
        usuario_id=current_user_id,
        usuario_nombre=token.get("username", ""),
        accion="cambiar_estado",
        modulo="usuarios",
        detalle=f"Usuario #{user_id} {estado}",
        ip_address=request.client.host if request.client else None,
    )
    return resultado
