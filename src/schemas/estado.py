from pydantic import BaseModel

class EstadoUpdate(BaseModel):
    activo: bool
