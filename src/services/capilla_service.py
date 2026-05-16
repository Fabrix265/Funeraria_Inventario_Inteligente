from sqlmodel import Session, select, col
from fastapi import HTTPException
from typing import Optional
from src.models.capilla import Capilla
from src.schemas.capilla import CapillaCrear

class CapillaService:
    @staticmethod
    def crear(db: Session, capilla_in: CapillaCrear):
        nueva_capilla = Capilla.model_validate(capilla_in)
        db.add(nueva_capilla)
        db.commit()
        db.refresh(nueva_capilla)
        return nueva_capilla

    @staticmethod
    def obtener_todas(db: Session, modelo: Optional[str] = None):
        statement = select(Capilla)
        if modelo:
            statement = statement.where(col(Capilla.modelo).ilike(f"%{modelo}%"))
        return db.exec(statement).all()

    @staticmethod
    def actualizar(db: Session, capilla_id: int, capilla_in: CapillaCrear):
        db_capilla = db.get(Capilla, capilla_id)
        if not db_capilla:
            raise HTTPException(status_code=404, detail="Capilla no encontrada")
        
        capilla_data = capilla_in.model_dump(exclude_unset=True)
        for key, value in capilla_data.items():
            setattr(db_capilla, key, value)
            
        db.add(db_capilla)
        db.commit()
        db.refresh(db_capilla)
        return db_capilla

    @staticmethod
    def eliminar(db: Session, capilla_id: int):
        db_capilla = db.get(Capilla, capilla_id)
        if not db_capilla:
            raise HTTPException(status_code=404, detail="Capilla no encontrada")
        
        db.delete(db_capilla)
        db.commit()
        return {"message": f"Capilla '{db_capilla.modelo}' eliminada correctamente"}
    
    @staticmethod
    def actualizar_stock(db: Session, capilla_id: int, cantidad: int):
        db_capilla = db.get(Capilla, capilla_id)
        if not db_capilla:
            raise HTTPException(status_code=404, detail="Capilla no encontrada")
        
        nuevo_stock = db_capilla.stock + cantidad
        if nuevo_stock < 0:
            raise HTTPException(status_code=400, detail="El stock resultante no puede ser negativo")
        
        db_capilla.stock = nuevo_stock
        db.add(db_capilla)
        db.commit()
        db.refresh(db_capilla)
        return db_capilla