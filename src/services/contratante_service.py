from typing import Optional
from sqlmodel import Session, select
from fastapi import HTTPException, status
from src.models.contratante import Contratante
from src.models.servicio import Servicio

class ContratanteService:
    @staticmethod
    def listar_todos(
        session: Session, 
        nombre: Optional[str] = None, 
        dni: Optional[str] = None
    ) -> list[Contratante]:
        query = select(Contratante)
        if nombre:
            query = query.where(Contratante.nombre.contains(nombre))
        if dni:
            query = query.where(Contratante.dni == dni)
        return session.exec(query).all()

    @staticmethod
    def obtener_por_id(session: Session, id: int) -> Contratante:
        contratante = session.get(Contratante, id)
        if not contratante:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Contratante con ID {id} no encontrado"
            )
        return contratante

    @staticmethod
    def actualizar(session: Session, id: int, datos: dict) -> Contratante:
        contratante = ContratanteService.obtener_por_id(session, id)
        
        if "dni" in datos and datos["dni"] != contratante.dni:
            dni_existente = session.exec(
                select(Contratante).where(Contratante.dni == datos["dni"])
            ).first()
            if dni_existente:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"El DNI {datos['dni']} ya pertenece a otro contratante"
                )

        for key, value in datos.items():
            setattr(contratante, key, value)
            
        session.add(contratante)
        session.commit()
        session.refresh(contratante)
        return contratante
    
    @staticmethod
    def eliminar(session: Session, id: int):
        contratante = ContratanteService.obtener_por_id(session, id)
        
        servicios_asociados = session.exec(
            select(Servicio).where(Servicio.id_contratante == id)
        ).first()
        
        if servicios_asociados:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede eliminar: el contratante tiene servicios registrados"
            )
            
        session.delete(contratante)
        session.commit()
        return {"message": "Contratante eliminado exitosamente"}