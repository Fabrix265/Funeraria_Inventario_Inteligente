from typing import Optional
from sqlmodel import Session, select
from fastapi import HTTPException, status
from src.models.fallecido import Fallecido
from src.models.servicio import Servicio

class FallecidoService:
    @staticmethod
    def listar_todos(
        session: Session, 
        nombre: Optional[str] = None, 
        dni: Optional[str] = None
    ) -> list[Fallecido]:
        query = select(Fallecido)
        if nombre:
            query = query.where(Fallecido.nombre.contains(nombre))
        if dni:
            query = query.where(Fallecido.dni == dni)
        return session.exec(query).all()

    @staticmethod
    def obtener_por_id(session: Session, id: int) -> Fallecido:
        fallecido = session.get(Fallecido, id)
        if not fallecido:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Fallecido con ID {id} no encontrado"
            )
        return fallecido

    @staticmethod
    def actualizar(session: Session, id: int, datos: dict) -> Fallecido:
        fallecido = FallecidoService.obtener_por_id(session, id)
        
        if "dni" in datos and datos["dni"] != fallecido.dni:
            dni_existente = session.exec(
                select(Fallecido).where(Fallecido.dni == datos["dni"])
            ).first()
            if dni_existente:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"El DNI {datos['dni']} ya pertenece a otro fallecido"
                )

        for key, value in datos.items():
            setattr(fallecido, key, value)
        
        session.add(fallecido)
        session.commit()
        session.refresh(fallecido)
        return fallecido
    
    @staticmethod
    def eliminar(session: Session, id: int):
        fallecido = FallecidoService.obtener_por_id(session, id)
        
        servicio_asociado = session.exec(
            select(Servicio).where(Servicio.id_fallecido == id)
        ).first()
        
        if servicio_asociado:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede eliminar: el fallecido está vinculado a un servicio activo"
            )
            
        session.delete(fallecido)
        session.commit()
        return {"message": "Registro de fallecido eliminado"}