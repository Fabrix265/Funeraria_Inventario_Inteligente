from sqlmodel import Session, select
from fastapi import HTTPException, status
from passlib.context import CryptContext
from src.models.user import User, CargoEnum
from src.schemas.user import UserActualizarSe, UserCrear

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
            
            nuevo_usuario = User(
                username=user_data.username,
                password=cls.hash_password(user_data.password),
                cargo=user_data.cargo
            )

            db.add(nuevo_usuario)
            db.commit()
            db.refresh(nuevo_usuario)
            return nuevo_usuario

        except Exception as e:
            print("ERROR REAL:", e)
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    def obtener_usuarios(db: Session, es_admin: bool):
        if es_admin:
            return db.exec(select(User)).all()
        
        statement = select(User).where(User.cargo == CargoEnum.trabajador)
        return db.exec(statement).all()

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