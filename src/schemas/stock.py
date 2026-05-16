from pydantic import BaseModel, Field

class StockUpdate(BaseModel):
    cantidad: int = Field(..., description="Cantidad a sumar (positivo) o restar (negativo)")