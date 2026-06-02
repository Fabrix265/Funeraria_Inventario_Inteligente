from sqlmodel import Session, delete, select, or_, func
from sqlalchemy.orm import selectinload
from fastapi import HTTPException

from src.models.servicio import Servicio
from src.models.servicio_vehiculo import ServicioVehiculo
from src.models.fallecido import Fallecido
from src.models.contratante import Contratante
from src.models.ataud import Ataud
from src.models.capilla import Capilla
from src.models.vehiculo import Vehiculo, TipoVehiculo
from src.models.pasajero import Pasajero
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
            selectinload(Servicio.pasajeros),
        )
    )
    servicio = session.exec(statement).first()
    if not servicio:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    return servicio


def _vehiculos_tienen_auto_microbus(session: Session, ids_vehiculos: list[int]) -> bool:
    if not ids_vehiculos:
        return False
    vehiculos = session.exec(
        select(Vehiculo).where(Vehiculo.id.in_(ids_vehiculos))
    ).all()
    tipos_permitidos = {TipoVehiculo.auto, TipoVehiculo.microbus}
    return any(v.tipo in tipos_permitidos for v in vehiculos)


def _validar_vehiculos_activos(session: Session, ids_vehiculos: list[int]):
    if not ids_vehiculos:
        return
    vehiculos = session.exec(
        select(Vehiculo).where(Vehiculo.id.in_(ids_vehiculos))
    ).all()
    encontrados_ids = {v.id for v in vehiculos}
    for vid in ids_vehiculos:
        if vid not in encontrados_ids:
            raise HTTPException(status_code=400, detail=f"Vehículo con ID {vid} no encontrado")
    inactivos = [v for v in vehiculos if not v.activo]
    if inactivos:
        nombres = ", ".join(f"ID {v.id} ({v.tipo.value})" for v in inactivos)
        raise HTTPException(
            status_code=400,
            detail=f"Los siguientes vehículos están inactivos y no pueden asignarse: {nombres}"
        )


def listar_servicios(
    session: Session,
    fecha=None,
    nombre=None,
    dni=None,
    dni_fallecido=None,
    telefono=None,
    offset=0,
    limit=20,
):
    base_query = (
        select(Servicio)
        .join(Contratante, Servicio.id_contratante == Contratante.id)
        .join(Fallecido, Servicio.id_fallecido == Fallecido.id)
    )
    if fecha: base_query = base_query.where(Servicio.fecha == fecha)
    if nombre:
        n_l = f"%{nombre}%"
        base_query = base_query.where(or_(Contratante.nombre.ilike(n_l), Fallecido.nombre.ilike(n_l)))
    if dni: base_query = base_query.where(Contratante.dni == dni)
    if dni_fallecido: base_query = base_query.where(Fallecido.dni_fallecido == dni_fallecido)
    if telefono: base_query = base_query.where(Contratante.telefono == telefono)

    count_query = (
        select(func.count(Servicio.id))
        .join(Contratante, Servicio.id_contratante == Contratante.id)
        .join(Fallecido, Servicio.id_fallecido == Fallecido.id)
    )
    if fecha: count_query = count_query.where(Servicio.fecha == fecha)
    if nombre:
        n_l = f"%{nombre}%"
        count_query = count_query.where(or_(Contratante.nombre.ilike(n_l), Fallecido.nombre.ilike(n_l)))
    if dni: count_query = count_query.where(Contratante.dni == dni)
    if dni_fallecido: count_query = count_query.where(Fallecido.dni_fallecido == dni_fallecido)
    if telefono: count_query = count_query.where(Contratante.telefono == telefono)

    total = session.exec(count_query).one()

    statement = base_query.options(
        selectinload(Servicio.fallecido),
        selectinload(Servicio.contratante),
        selectinload(Servicio.ataud),
        selectinload(Servicio.capilla),
        selectinload(Servicio.vehiculos_asignados).selectinload(ServicioVehiculo.vehiculo),
        selectinload(Servicio.pasajeros),
    ).offset(offset).limit(limit)

    return {"total": total, "offset": offset, "limit": limit, "data": session.exec(statement).all()}


def obtener_servicio(session: Session, servicio_id: int):
    return _get_servicio_completo(session, servicio_id)


def crear_servicio(session: Session, datos: ServicioCrear, id_usuario: int):
    id_ataud_final = datos.id_ataud
    if not id_ataud_final and datos.ataud_modelo_nuevo:
        stmt_at = select(Ataud).where(Ataud.modelo == datos.ataud_modelo_nuevo.strip())
        ataud_existente = session.exec(stmt_at).first()
        if ataud_existente:
            id_ataud_final = ataud_existente.id
        else:
            nuevo_ataud = Ataud(
                modelo=datos.ataud_modelo_nuevo.strip(),
                color=datos.color_ataud_nuevo.strip() if datos.color_ataud_nuevo else "Por definir",
                stock=1
            )
            session.add(nuevo_ataud)
            session.flush()
            id_ataud_final = nuevo_ataud.id

    ataud = None
    if id_ataud_final:
        ataud = session.get(Ataud, id_ataud_final)
        if not ataud or ataud.stock <= 0:
            raise HTTPException(status_code=400, detail="Ataúd no disponible")
        if not ataud.activo:
            raise HTTPException(status_code=400, detail="El ataúd seleccionado está inactivo")

    id_capilla_final = datos.id_capilla
    if not id_capilla_final and datos.capilla_modelo_nuevo:
        stmt_cp = select(Capilla).where(Capilla.modelo == datos.capilla_modelo_nuevo.strip())
        capilla_existente = session.exec(stmt_cp).first()
        if capilla_existente:
            id_capilla_final = capilla_existente.id
        else:
            nueva_capilla = Capilla(
                modelo=datos.capilla_modelo_nuevo.strip(),
                stock=1
            )
            session.add(nueva_capilla)
            session.flush()
            id_capilla_final = nueva_capilla.id

    if not id_capilla_final:
        raise HTTPException(status_code=400, detail="Debe asignar una capilla del catálogo o ingresar un modelo nuevo")

    capilla = session.get(Capilla, id_capilla_final)
    if not capilla or capilla.stock <= 0:
        raise HTTPException(status_code=400, detail="Capilla no disponible")
    if not capilla.activo:
        raise HTTPException(status_code=400, detail="La capilla seleccionada está inactiva")

    contratante = session.exec(select(Contratante).where(Contratante.dni == datos.contratante.dni)).first()
    if not contratante:
        contratante = Contratante(**datos.contratante.model_dump())
        session.add(contratante)
        session.flush()

    fallecido = Fallecido(**datos.fallecido.model_dump())
    session.add(fallecido)
    session.flush()

    servicio = Servicio(
        id_usuario=id_usuario,
        id_ataud=id_ataud_final,
        id_capilla=id_capilla_final,
        id_contratante=contratante.id,
        id_fallecido=fallecido.id,
        direccion_velacion=datos.direccion_velacion,
        tipo_pago=datos.tipo_pago,
        costo=datos.costo,
        fecha=datos.fecha,
        cantidad_cargadores=datos.cantidad_cargadores
    )
    session.add(servicio)
    session.flush()

    for v_id in datos.ids_vehiculos:
        session.add(ServicioVehiculo(id_servicio=servicio.id, id_vehiculo=v_id))

    _validar_vehiculos_activos(session, datos.ids_vehiculos)

    capilla.stock -= 1
    if ataud:
        ataud.stock -= 1

    if datos.pasajeros:
        tiene_auto_microbus = _vehiculos_tienen_auto_microbus(session, datos.ids_vehiculos)
        if not tiene_auto_microbus:
            raise HTTPException(
                status_code=400,
                detail="Solo se pueden agregar pasajeros a servicios con vehículo tipo auto o microbús"
            )
        for p_data in datos.pasajeros:
            pasajero = Pasajero(id_servicio=servicio.id, **p_data.model_dump())
            session.add(pasajero)

    session.commit()
    return _get_servicio_completo(session, servicio.id)


def modificar_servicio(session: Session, servicio_id: int, datos: dict):
    servicio = _get_servicio_completo(session, servicio_id)

    f_data = datos.pop("fallecido", None)
    c_data = datos.pop("contratante", None)
    v_ids = datos.pop("ids_vehiculos", None)
    nueva_capilla_id = datos.pop("id_capilla", None)
    nuevo_ataud_id = datos.pop("id_ataud", None)

    datos.pop("ataud_modelo_nuevo", None)
    datos.pop("color_ataud_nuevo", None)
    datos.pop("capilla_modelo_nuevo", None)
    datos.pop("pasajeros", None)

    if f_data:
        for k, v in f_data.items():
            if hasattr(servicio.fallecido, k) and k != "id":
                setattr(servicio.fallecido, k, v)
    
    if c_data:
        for k, v in c_data.items():
            if hasattr(servicio.contratante, k) and k != "id":
                setattr(servicio.contratante, k, v)

    if v_ids is not None:
        _validar_vehiculos_activos(session, v_ids)
        session.exec(delete(ServicioVehiculo).where(ServicioVehiculo.id_servicio == servicio_id))
        session.expire(servicio, ["vehiculos_asignados"])
        for vid in v_ids:
            session.add(ServicioVehiculo(id_servicio=servicio_id, id_vehiculo=vid))

    if nueva_capilla_id is not None and int(nueva_capilla_id) != servicio.id_capilla:
        nueva = session.get(Capilla, int(nueva_capilla_id))
        if not nueva or nueva.stock <= 0:
            raise HTTPException(status_code=400, detail="Capilla sin stock")
        if not nueva.activo:
            raise HTTPException(status_code=400, detail="La capilla seleccionada está inactiva")
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
            if not at_nuevo.activo:
                raise HTTPException(status_code=400, detail="El ataúd seleccionado está inactivo")
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
    session.exec(delete(Pasajero).where(Pasajero.id_servicio == servicio_id))
    session.exec(delete(ServicioVehiculo).where(ServicioVehiculo.id_servicio == servicio_id))
    session.delete(servicio); session.flush()
    
    fallecido = session.get(Fallecido, fid)
    if fallecido: session.delete(fallecido)
    
    if not session.exec(select(Servicio).where(Servicio.id_contratante == cid)).first():
        contratante = session.get(Contratante, cid)
        if contratante: session.delete(contratante)
        
    session.commit()
    return {"message": "Eliminado"}
