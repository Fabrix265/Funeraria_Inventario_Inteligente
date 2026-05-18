from sqlmodel import Session, select
from fastapi import HTTPException
from typing import Optional
from src.models.vehiculo import Vehiculo, TipoVehiculo
from src.schemas.vehiculo import VehiculoCrear

class VehiculoService:
    @staticmethod
    def crear(db: Session, vehiculo_in: VehiculoCrear):
        nuevo_vehiculo = Vehiculo.model_validate(vehiculo_in)
        db.add(nuevo_vehiculo)
        db.commit()
        db.refresh(nuevo_vehiculo)
        return nuevo_vehiculo

    @staticmethod
    def obtener_todos(db: Session, tipo: Optional[TipoVehiculo] = None):
        statement = select(Vehiculo)
        if tipo:
            statement = statement.where(Vehiculo.tipo == tipo)
        return db.exec(statement).all()

    @staticmethod
    def actualizar(db: Session, vehiculo_id: int, vehiculo_in: VehiculoCrear):
        db_vehiculo = db.get(Vehiculo, vehiculo_id)
        if not db_vehiculo:
            raise HTTPException(status_code=404, detail="Vehículo no encontrado")
        
        vehiculo_data = vehiculo_in.model_dump(exclude_unset=True)
        for key, value in vehiculo_data.items():
            setattr(db_vehiculo, key, value)
            
        db.add(db_vehiculo)
        db.commit()
        db.refresh(db_vehiculo)
        return db_vehiculo

    @staticmethod
    def eliminar(db: Session, vehiculo_id: int):
        db_vehiculo = db.get(Vehiculo, vehiculo_id)
        if not db_vehiculo:
            raise HTTPException(status_code=404, detail="Vehículo no encontrado")
        
        db.delete(db_vehiculo)
        db.commit()
        return {"message": f"Vehículo ID {vehiculo_id} eliminado correctamente"}