from sqlmodel import Session, select, col
from fastapi import HTTPException
from typing import Optional
from src.models.ataud import Ataud, TipoAtaud
from src.schemas.ataud import AtaudCrear, AtaudModificar

class AtaudService:
    @staticmethod
    def crear(db: Session, ataud_in: AtaudCrear):
        nuevo_ataud = Ataud.model_validate(ataud_in)
        db.add(nuevo_ataud)
        db.commit()
        db.refresh(nuevo_ataud)
        return nuevo_ataud

    @staticmethod
    def obtener_todos(
        db: Session, 
        modelo: Optional[str] = None, 
        color: Optional[str] = None,
        stock_min: Optional[int] = None,
        tipo: Optional[TipoAtaud] = None
    ):
        statement = select(Ataud)
        
        if modelo:
            statement = statement.where(col(Ataud.modelo).ilike(f"%{modelo}%"))
        if color:
            statement = statement.where(col(Ataud.color).ilike(f"%{color}%"))
        if stock_min is not None:
            statement = statement.where(Ataud.stock >= stock_min)
        if tipo:
            statement = statement.where(Ataud.tipo == tipo)
            
        return db.exec(statement).all()

    @staticmethod
    def actualizar(db: Session, ataud_id: int, ataud_in: AtaudModificar):
        db_ataud = db.get(Ataud, ataud_id)
        if not db_ataud:
            raise HTTPException(status_code=404, detail="Ataud no encontrado")
        
        ataud_data = ataud_in.model_dump(exclude_unset=True)
        for key, value in ataud_data.items():
            setattr(db_ataud, key, value)
            
        db.add(db_ataud)
        db.commit()
        db.refresh(db_ataud)
        return db_ataud

    @staticmethod
    def eliminar(db: Session, ataud_id: int):
        db_ataud = db.get(Ataud, ataud_id)
        if not db_ataud:
            raise HTTPException(status_code=404, detail="Ataud no encontrado")
        db.delete(db_ataud)
        db.commit()
        return {"message": "Ataud eliminado"}
    
    @staticmethod
    def actualizar_stock(db: Session, ataud_id: int, cantidad: int):
        db_ataud = db.get(Ataud, ataud_id)
        if not db_ataud:
            raise HTTPException(status_code=404, detail="Ataud no encontrado")
        
        nuevo_stock = db_ataud.stock + cantidad
        if nuevo_stock < 0:
            raise HTTPException(status_code=400, detail="El stock resultante no puede ser negativo")
        
        db_ataud.stock = nuevo_stock
        db.add(db_ataud)
        db.commit()
        db.refresh(db_ataud)
        return db_ataud