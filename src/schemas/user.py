from pydantic import BaseModel, Field
from typing import List, Optional

# Esquema para leer la información de un rol
class RoleLeer(BaseModel):
    id: int
    nombre: str

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=30)

class UserCrear(UserBase):
    password: str = Field(min_length=6)
    role_id: int  # Ahora enviamos el ID del rol a asignar

class UserLeer(UserBase):
    id: int
    roles: List[RoleLeer] = []  # Retorna la lista de roles del usuario

    class Config:
        from_attributes = True

class UserActualizarSe(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    password: str = Field(min_length=6)

################################
class RoleCrear(BaseModel):
    nombre: str = Field(min_length=3, max_length=50)
    permisos_ids: List[int] = []  # Lista de IDs de los permisos asignados

class PermissionLeer(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str] = None

    class Config:
        from_attributes = True

class RoleDetalleLeer(BaseModel):
    id: int
    nombre: str
    permisos: List[PermissionLeer] = []

    class Config:
        from_attributes = True

class UserActualizarAdmin(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    role_id: int
    password: Optional[str] = Field(default=None, min_length=6)