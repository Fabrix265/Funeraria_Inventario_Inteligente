from sqlmodel import Session, select
from fastapi import HTTPException, status
from src.models.user import Role, Permission
from src.schemas.user import RoleCrear

class RoleService:
    @staticmethod
    def listar_roles(db: Session):
        return db.exec(select(Role)).all()
    
    @staticmethod
    def listar_permisos(db: Session):
        return db.exec(select(Permission)).all()

    @staticmethod
    def crear_rol(db: Session, rol_data: RoleCrear):
        statement = select(Role).where(Role.nombre == rol_data.nombre)
        if db.exec(statement).first():
            raise HTTPException(status_code=400, detail="El nombre de este rol ya existe")

        nuevo_rol = Role(nombre=rol_data.nombre)

        for perm_id in rol_data.permisos_ids:
            permiso = db.get(Permission, perm_id)
            if permiso:
                nuevo_rol.permisos.append(permiso)
            else:
                raise HTTPException(
                    status_code=404, 
                    detail=f"El permiso con ID {perm_id} no existe"
                )

        db.add(nuevo_rol)
        db.commit()
        db.refresh(nuevo_rol)
        return nuevo_rol

    @staticmethod
    def eliminar_rol(db: Session, role_id: int):
        rol = db.get(Role, role_id)
        if not rol:
            raise HTTPException(status_code=404, detail="El rol especificado no existe")
        
        if rol.nombre.lower() in ["administrador", "superadmin"]:
            raise HTTPException(status_code=400, detail="No puedes eliminar los roles base del sistema")

        db.delete(rol)
        db.commit()
        return {"message": f"Rol '{rol.nombre}' eliminado correctamente"}