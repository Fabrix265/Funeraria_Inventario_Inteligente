from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional

class Capilla(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    modelo: str = Field(nullable=False, max_length=100, index=True)
    stock: int = Field(default=0, nullable=False)
    activo: bool = Field(default=True, index=True)

    servicios: List["Servicio"] = Relationship(back_populates="capilla")
    imagenes: List["CapillaImagen"] = Relationship(
        back_populates="capilla",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class CapillaImagen(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    capilla_id: int = Field(foreign_key="capilla.id", nullable=False)
    url: str = Field(nullable=False)
    public_id: str = Field(nullable=False)

    capilla: Optional[Capilla] = Relationship(back_populates="imagenes")