from typing import Optional, List
from sqlmodel import Session, select
from fastapi import HTTPException, status

from src.models.pasajero import Pasajero
from src.models.servicio import Servicio
from src.models.servicio_vehiculo import ServicioVehiculo
from src.models.vehiculo import Vehiculo, TipoVehiculo


def _validar_vehiculos_permitidos(session: Session, servicio_id: int):
    vehiculos_ids = [
        sv.id_vehiculo
        for sv in session.exec(
            select(ServicioVehiculo).where(ServicioVehiculo.id_servicio == servicio_id)
        ).all()
    ]
    if not vehiculos_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El servicio no tiene vehículos asignados"
        )
    vehiculos = session.exec(
        select(Vehiculo).where(Vehiculo.id.in_(vehiculos_ids))
    ).all()
    tipos_permitidos = {TipoVehiculo.auto, TipoVehiculo.microbus}
    if not any(v.tipo in tipos_permitidos for v in vehiculos):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se pueden agregar pasajeros a servicios con vehículo tipo auto o microbús"
        )


class PasajeroService:
    @staticmethod
    def listar_por_servicio(session: Session, servicio_id: int) -> List[Pasajero]:
        servicio = session.get(Servicio, servicio_id)
        if not servicio:
            raise HTTPException(status_code=404, detail="Servicio no encontrado")
        return session.exec(
            select(Pasajero).where(Pasajero.id_servicio == servicio_id)
        ).all()

    @staticmethod
    def obtener_por_id(session: Session, id: int) -> Pasajero:
        pasajero = session.get(Pasajero, id)
        if not pasajero:
            raise HTTPException(status_code=404, detail="Pasajero no encontrado")
        return pasajero

    @staticmethod
    def agregar_pasajero(session: Session, servicio_id: int, datos: dict) -> Pasajero:
        servicio = session.get(Servicio, servicio_id)
        if not servicio:
            raise HTTPException(status_code=404, detail="Servicio no encontrado")
        _validar_vehiculos_permitidos(session, servicio_id)
        pasajero = Pasajero(id_servicio=servicio_id, **datos)
        session.add(pasajero)
        session.commit()
        session.refresh(pasajero)
        return pasajero

    @staticmethod
    def agregar_pasajeros(session: Session, servicio_id: int, lista_datos: List[dict]) -> List[Pasajero]:
        _validar_vehiculos_permitidos(session, servicio_id)
        pasajeros_creados = []
        for datos in lista_datos:
            pasajero = Pasajero(id_servicio=servicio_id, **datos)
            session.add(pasajero)
            session.flush()
            pasajeros_creados.append(pasajero)
        return pasajeros_creados

    @staticmethod
    def actualizar(session: Session, id: int, datos: dict) -> Pasajero:
        pasajero = PasajeroService.obtener_por_id(session, id)
        for key, value in datos.items():
            setattr(pasajero, key, value)
        session.add(pasajero)
        session.commit()
        session.refresh(pasajero)
        return pasajero

    @staticmethod
    def eliminar(session: Session, id: int):
        pasajero = PasajeroService.obtener_por_id(session, id)
        session.delete(pasajero)
        session.commit()
        return {"message": "Pasajero eliminado"}
