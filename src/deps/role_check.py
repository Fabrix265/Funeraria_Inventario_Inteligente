from fastapi import Depends, HTTPException, status
from sqlmodel import select
from src.core.security import decode_token
from src.deps.db_session import SessionDep
from src.models.user import Role, UserRoleLink

def get_current_user(token: dict = Depends(decode_token)):
    return token

def get_current_admin(db: SessionDep, token: dict = Depends(decode_token)):
    user_id = int(token.get("sub"))
    
    statement = (
        select(Role)
        .join(UserRoleLink, UserRoleLink.role_id == Role.id)
        .where(UserRoleLink.user_id == user_id)
        .where(Role.nombre == "Administrador")
    )
    es_admin = db.exec(statement).first()
    
    if not es_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Acceso denegado: Se requiere el rol de Administrador"
        )
    return token