from pydantic import BaseModel, Field
from typing import List, Optional

class RoleLeer(BaseModel):
    id: int
    nombre: str

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=30)

class UserCrear(UserBase):
    password: str = Field(min_length=6)
    role_id: int

class UserLeer(UserBase):
    id: int
    roles: List[RoleLeer] = []

    class Config:
        from_attributes = True

class UserActualizarSe(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    password: str = Field(min_length=6)

class RoleCrear(BaseModel):
    nombre: str = Field(min_length=3, max_length=50)
    permisos_ids: List[int] = []

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