from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional, TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    from .servicio import Servicio

class UserRoleLink(SQLModel, table=True):
    user_id: Optional[int] = Field(default=None, foreign_key="user.id", primary_key=True)
    role_id: Optional[int] = Field(default=None, foreign_key="role.id", primary_key=True)

class RolePermissionLink(SQLModel, table=True):
    role_id: Optional[int] = Field(default=None, foreign_key="role.id", primary_key=True)
    permission_id: Optional[int] = Field(default=None, foreign_key="permission.id", primary_key=True)

class Permission(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(nullable=False, unique=True, index=True)  # Identificador único del permiso
    descripcion: Optional[str] = Field(default=None)

    roles: List["Role"] = Relationship(back_populates="permisos", link_model=RolePermissionLink)


class Role(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(nullable=False, unique=True, index=True)

    usuarios: List["User"] = Relationship(back_populates="roles", link_model=UserRoleLink)
    permisos: List[Permission] = Relationship(back_populates="roles", link_model=RolePermissionLink)


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(nullable=False, unique=True, index=True, max_length=30)
    password: str = Field(nullable=False)
    activo: bool = Field(default=True, index=True)
    roles: List[Role] = Relationship(back_populates="usuarios", link_model=UserRoleLink)
    servicios: List["Servicio"] = Relationship(back_populates="usuario")