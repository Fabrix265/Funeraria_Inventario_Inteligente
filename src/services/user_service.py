from sqlmodel import Session, select
from fastapi import HTTPException, status
from passlib.context import CryptContext
from src.models.user import User, Role  # Importamos los nuevos modelos dinámicos
from src.schemas.user import UserActualizarSe, UserCrear, UserActualizarAdmin

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    @classmethod
    def crear_usuario(cls, db: Session, user_data: UserCrear):
        try:
            # 1. Validar si el username ya existe
            statement = select(User).where(User.username == user_data.username)
            if db.exec(statement).first():
                raise HTTPException(status_code=400, detail="El nombre de usuario ya existe")
            
            # 2. Validar si el rol asignado existe en la BD
            rol = db.get(Role, user_data.role_id)
            if not rol:
                raise HTTPException(status_code=404, detail="El Rol especificado no existe")

            # 3. Instanciar el nuevo usuario
            nuevo_usuario = User(
                username=user_data.username,
                password=cls.hash_password(user_data.password)
            )
            
            # 4. Asignar el rol dinámicamente mediante la relación
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
    def obtener_usuarios(db: Session):
        # Retorna todos los usuarios. El control de qué endpoints ven se maneja en los Routers.
        return db.exec(select(User)).all()
    
    @staticmethod
    def obtener_roles(db: Session):
        # Consulta en la BD y trae todos los registros de la tabla Role
        return db.exec(select(Role)).all()

    @staticmethod
    def eliminar_usuario(db: Session, user_id: int):
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
    
    ##############################################
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
        if user_data.password:  # Si el admin escribió una nueva contraseña, la hasheamos
            db_user.password = cls.hash_password(user_data.password)

        db_user.roles = [nuevo_rol]
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user