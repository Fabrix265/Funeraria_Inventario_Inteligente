from pydantic import BaseModel, Field
from src.models.user import CargoEnum

class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    cargo: CargoEnum

class UserCrear(UserBase):
    password: str = Field(min_length=6)

class UserLeer(UserBase):
    id: int

class UserActualizarSe(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    password: str = Field(min_length=6)