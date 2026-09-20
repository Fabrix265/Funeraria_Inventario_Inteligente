from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional

class Ataud(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    modelo: str = Field(nullable=False, max_length=100, index=True)
    color: str = Field(nullable=False, max_length=50)
    stock: int = Field(default=0, nullable=False, ge=0)
    activo: bool = Field(default=True, index=True)

    servicios: List["Servicio"] = Relationship(back_populates="ataud")
    imagenes: List["AtaudImagen"] = Relationship(
        back_populates="ataud",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )

class AtaudImagen(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    ataud_id: int = Field(foreign_key="ataud.id", nullable=False)
    url: str = Field(nullable=False)
    storage_path: str = Field(nullable=False)

    ataud: Optional[Ataud] = Relationship(back_populates="imagenes")