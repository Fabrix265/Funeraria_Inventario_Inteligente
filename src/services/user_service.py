from sqlmodel import Session, select, func
from typing import Optional
from fastapi import HTTPException, status
from passlib.context import CryptContext
from src.models.user import User, Role, UserRoleLink
from src.schemas.user import UserActualizarSe, UserCrear, UserActualizarAdmin

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    @classmethod
    def crear_usuario(cls, db: Session, user_data: UserCrear):
        try:
            statement = select(User).where(User.username == user_data.username)
            if db.exec(statement).first():
                raise HTTPException(status_code=400, detail="El nombre de usuario ya existe")
            
            rol = db.get(Role, user_data.role_id)
            if not rol:
                raise HTTPException(status_code=404, detail="El Rol especificado no existe")

            nuevo_usuario = User(
                username=user_data.username,
                password=cls.hash_password(user_data.password)
            )
            
            nuevo_usuario.roles.append(rol)

            db.add(nuevo_usuario)
            db.commit()
            db.refresh(nuevo_usuario)
            return nuevo_usuario

        except HTTPException as he:
            raise he
        except Exception as e:
            print("ERROR REAL:", e)
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    def obtener_usuarios(db: Session, activo: Optional[bool] = None):
        query = select(User)
        if activo is not None:
            query = query.where(User.activo == activo)
        return db.exec(query).all()
    
    @staticmethod
    def obtener_roles(db: Session):
        return db.exec(select(Role)).all()

    @staticmethod
    def eliminar_usuario(db: Session, user_id: int, current_user_id: int):
        if user_id == current_user_id:
            raise HTTPException(status_code=400, detail="No puedes eliminar tu propia cuenta")
        db_user = db.get(User, user_id)
        if not db_user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        db.delete(db_user)
        db.commit()
        return {"message": "Usuario eliminado"}
    
    @classmethod
    def actualizar_perfil(cls, db: Session, user_id: int, user_data: UserActualizarSe):
        db_user = db.get(User, user_id)
        if not db_user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        statement = select(User).where(User.username == user_data.username).where(User.id != user_id)
        if db.exec(statement).first():
            raise HTTPException(status_code=400, detail="El nombre de usuario ya está en uso")

        db_user.username = user_data.username
        db_user.password = cls.hash_password(user_data.password)
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def cambiar_estado(db: Session, user_id: int, activo: bool, current_user_id: int) -> User:
        if user_id == current_user_id:
            raise HTTPException(status_code=400, detail="No puedes desactivar tu propia cuenta")

        db_user = db.get(User, user_id)
        if not db_user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        if not activo:
            admin_role = db.exec(select(Role).where(Role.nombre == "Administrador")).first()
            if admin_role:
                count = db.exec(
                    select(func.count()).select_from(User)
                    .join(UserRoleLink)
                    .where(UserRoleLink.role_id == admin_role.id)
                    .where(User.activo == True)
                    .where(User.id != user_id)
                ).one()
                if count == 0:
                    raise HTTPException(status_code=400, detail="No puedes desactivar el último administrador activo")

        db_user.activo = activo
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @classmethod
    def actualizar_usuario_por_admin(cls, db: Session, user_id: int, user_data: UserActualizarAdmin):
        db_user = db.get(User, user_id)
        if not db_user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        statement = select(User).where(User.username == user_data.username).where(User.id != user_id)
        if db.exec(statement).first():
            raise HTTPException(status_code=400, detail="El nombre de usuario ya está en uso")

        nuevo_rol = db.get(Role, user_data.role_id)
        if not nuevo_rol:
            raise HTTPException(status_code=404, detail="El Rol especificado no existe")

        db_user.username = user_data.username
        if user_data.password:
            db_user.password = cls.hash_password(user_data.password)

        db_user.roles = [nuevo_rol]
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user