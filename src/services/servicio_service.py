from sqlmodel import Session, delete, select, or_, func
from sqlalchemy.orm import selectinload
from fastapi import HTTPException

from src.models.servicio import Servicio
from src.models.servicio_vehiculo import ServicioVehiculo
from src.models.fallecido import Fallecido
from src.models.contratante import Contratante
from src.models.ataud import Ataud
from src.models.capilla import Capilla
from src.schemas.servicio import ServicioCrear

def _get_servicio_completo(session: Session, servicio_id: int) -> Servicio:
    statement = (
        select(Servicio)
        .where(Servicio.id == servicio_id)
        .options(
            selectinload(Servicio.fallecido),
            selectinload(Servicio.contratante),
            selectinload(Servicio.ataud),
            selectinload(Servicio.capilla),
            selectinload(Servicio.vehiculos_asignados).selectinload(ServicioVehiculo.vehiculo),
        )
    )
    servicio = session.exec(statement).first()
    if not servicio:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    return servicio

def listar_servicios(session: Session, fecha=None, nombre=None, dni=None, telefono=None, offset=0, limit=20):
    base_query = select(Servicio).join(Contratante, Servicio.id_contratante == Contratante.id).join(Fallecido, Servicio.id_fallecido == Fallecido.id)
    if fecha: base_query = base_query.where(Servicio.fecha == fecha)
    if nombre:
        n_l = f"%{nombre}%"
        base_query = base_query.where(or_(Contratante.nombre.ilike(n_l), Fallecido.nombre.ilike(n_l)))
    if dni: base_query = base_query.where(or_(Contratante.dni == dni, Fallecido.dni == dni))
    if telefono: base_query = base_query.where(Contratante.telefono == telefono)

    total = session.exec(select(func.count()).select_from(base_query.subquery())).one()
    statement = base_query.options(
        selectinload(Servicio.fallecido), selectinload(Servicio.contratante),
        selectinload(Servicio.ataud), selectinload(Servicio.capilla),
        selectinload(Servicio.vehiculos_asignados).selectinload(ServicioVehiculo.vehiculo)
    ).offset(offset).limit(limit)
    
    return {"total": total, "offset": offset, "limit": limit, "data": session.exec(statement).all()}

def obtener_servicio(session: Session, servicio_id: int):
    return _get_servicio_completo(session, servicio_id)

def crear_servicio(session: Session, datos: ServicioCrear, id_usuario: int):
    capilla = session.get(Capilla, datos.id_capilla)
    if not capilla or capilla.stock <= 0: 
        raise HTTPException(status_code=400, detail="Capilla no disponible")

    ataud = None
    if datos.id_ataud:
        ataud = session.get(Ataud, datos.id_ataud)
        if not ataud or ataud.stock <= 0: 
            raise HTTPException(status_code=400, detail="Ataúd no disponible")

    contratante = session.exec(select(Contratante).where(Contratante.dni == datos.contratante.dni)).first()
    if not contratante:
        contratante = Contratante(**datos.contratante.model_dump())
        session.add(contratante); session.flush()

    fallecido = session.exec(select(Fallecido).where(Fallecido.dni == datos.fallecido.dni)).first()
    if fallecido:
        existente = session.exec(select(Servicio).where(Servicio.id_fallecido == fallecido.id)).first()
        if existente: raise HTTPException(status_code=400, detail="El fallecido ya tiene un servicio registrado")
    else:
        fallecido = Fallecido(**datos.fallecido.model_dump())
        session.add(fallecido); session.flush()

    servicio = Servicio(
        id_usuario=id_usuario, id_ataud=datos.id_ataud, id_capilla=datos.id_capilla,
        id_contratante=contratante.id, id_fallecido=fallecido.id,
        direccion_velacion=datos.direccion_velacion, tipo_pago=datos.tipo_pago,
        costo=datos.costo, fecha=datos.fecha, arreglo_flora=datos.arreglo_flora,
        cantidad_cargadores=datos.cantidad_cargadores, director_sepelio=datos.director_sepelio
    )
    session.add(servicio); session.flush()

    for v_id in datos.ids_vehiculos:
        session.add(ServicioVehiculo(id_servicio=servicio.id, id_vehiculo=v_id))

    capilla.stock -= 1
    if ataud: ataud.stock -= 1
        
    session.commit()
    return _get_servicio_completo(session, servicio.id)

def modificar_servicio(session: Session, servicio_id: int, datos: dict):
    servicio = _get_servicio_completo(session, servicio_id)

    f_data = datos.pop("fallecido", None)
    c_data = datos.pop("contratante", None)
    v_ids = datos.pop("ids_vehiculos", None)
    nueva_capilla_id = datos.pop("id_capilla", None)
    nuevo_ataud_id = datos.pop("id_ataud", None)

    if f_data:
        for k, v in f_data.items():
            if hasattr(servicio.fallecido, k) and k != "id":
                setattr(servicio.fallecido, k, v)
    
    if c_data:
        for k, v in c_data.items():
            if hasattr(servicio.contratante, k) and k != "id":
                setattr(servicio.contratante, k, v)

    if v_ids is not None:
        session.exec(delete(ServicioVehiculo).where(ServicioVehiculo.id_servicio == servicio_id))
        session.expire(servicio, ["vehiculos_asignados"])
        for vid in v_ids:
            session.add(ServicioVehiculo(id_servicio=servicio_id, id_vehiculo=vid))

    if nueva_capilla_id is not None and int(nueva_capilla_id) != servicio.id_capilla:
        nueva = session.get(Capilla, int(nueva_capilla_id))
        if not nueva or nueva.stock <= 0:
            raise HTTPException(status_code=400, detail="Capilla sin stock")
        vieja = session.get(Capilla, servicio.id_capilla)
        if vieja: vieja.stock += 1
        nueva.stock -= 1
        servicio.id_capilla = int(nueva_capilla_id)

    if nuevo_ataud_id != servicio.id_ataud:
        if servicio.id_ataud:
            at_viejo = session.get(Ataud, servicio.id_ataud)
            if at_viejo: at_viejo.stock += 1
        if nuevo_ataud_id:
            at_nuevo = session.get(Ataud, int(nuevo_ataud_id))
            if not at_nuevo or at_nuevo.stock <= 0:
                raise HTTPException(status_code=400, detail="Ataúd sin stock")
            at_nuevo.stock -= 1
        servicio.id_ataud = nuevo_ataud_id

    for k, v in datos.items():
        if hasattr(servicio, k):
            setattr(servicio, k, v)

    try:
        session.add(servicio)
        session.commit()
        return _get_servicio_completo(session, servicio.id)
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))

def eliminar_servicio(session: Session, servicio_id: int):
    servicio = session.get(Servicio, servicio_id)
    if not servicio: raise HTTPException(status_code=404, detail="No encontrado")
    
    capilla = session.get(Capilla, servicio.id_capilla)
    if capilla: capilla.stock += 1
    if servicio.id_ataud:
        ataud = session.get(Ataud, servicio.id_ataud)
        if ataud: ataud.stock += 1

    fid, cid = servicio.id_fallecido, servicio.id_contratante
    session.exec(delete(ServicioVehiculo).where(ServicioVehiculo.id_servicio == servicio_id))
    session.delete(servicio); session.flush()
    
    fallecido = session.get(Fallecido, fid)
    if fallecido: session.delete(fallecido)
    
    if not session.exec(select(Servicio).where(Servicio.id_contratante == cid)).first():
        contratante = session.get(Contratante, cid)
        if contratante: session.delete(contratante)
        
    session.commit()
    return {"message": "Eliminado"}