from sqlmodel import Session, select
from fastapi import HTTPException, UploadFile
from typing import Optional
import uuid

from src.core.supabase_config import supabase
from src.models.vehiculo import Vehiculo, VehiculoImagen, TipoVehiculo
from src.schemas.vehiculo import VehiculoCrear

MINIMO_IMAGENES = 3
BUCKET = "vehiculos"


class VehiculoService:
    @staticmethod
    def crear(db: Session, vehiculo_in: VehiculoCrear):
        nuevo_vehiculo = Vehiculo.model_validate(vehiculo_in)
        db.add(nuevo_vehiculo)
        db.commit()
        db.refresh(nuevo_vehiculo)
        return nuevo_vehiculo

    @staticmethod
    def obtener_todos(db: Session, tipo: Optional[TipoVehiculo] = None, activo: Optional[bool] = None):
        statement = select(Vehiculo)
        if activo is not None:
            statement = statement.where(Vehiculo.activo == activo)
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

        for imagen in db_vehiculo.imagenes:
            supabase.storage.from_(BUCKET).remove([imagen.storage_path])

        db.delete(db_vehiculo)
        db.commit()
        return {"message": f"Vehículo ID {vehiculo_id} eliminado correctamente"}

    @staticmethod
    def cambiar_estado(db: Session, vehiculo_id: int, activo: bool):
        db_vehiculo = db.get(Vehiculo, vehiculo_id)
        if not db_vehiculo:
            raise HTTPException(status_code=404, detail="Vehículo no encontrado")

        if activo and len(db_vehiculo.imagenes) < MINIMO_IMAGENES:
            raise HTTPException(
                status_code=400,
                detail=f"No se puede activar el vehículo: necesita al menos {MINIMO_IMAGENES} imágenes (tiene {len(db_vehiculo.imagenes)})",
            )

        db_vehiculo.activo = activo
        db.add(db_vehiculo)
        db.commit()
        db.refresh(db_vehiculo)
        return db_vehiculo

    @staticmethod
    def agregar_imagen(db: Session, vehiculo_id: int, archivo: UploadFile):
        db_vehiculo = db.get(Vehiculo, vehiculo_id)
        if not db_vehiculo:
            raise HTTPException(status_code=404, detail="Vehículo no encontrado")

        extension = archivo.filename.split(".")[-1] if "." in archivo.filename else "jpg"
        ruta = f"{vehiculo_id}/{uuid.uuid4()}.{extension}"

        contenido = archivo.file.read()
        supabase.storage.from_(BUCKET).upload(
            ruta, contenido, {"content-type": archivo.content_type}
        )
        url_publica = supabase.storage.from_(BUCKET).get_public_url(ruta)

        nueva_imagen = VehiculoImagen(vehiculo_id=vehiculo_id, url=url_publica, storage_path=ruta)
        db.add(nueva_imagen)
        db.commit()
        db.refresh(db_vehiculo)
        return db_vehiculo

    @staticmethod
    def eliminar_imagen(db: Session, vehiculo_id: int, imagen_id: int):
        db_vehiculo = db.get(Vehiculo, vehiculo_id)
        if not db_vehiculo:
            raise HTTPException(status_code=404, detail="Vehículo no encontrado")

        db_imagen = db.get(VehiculoImagen, imagen_id)
        if not db_imagen or db_imagen.vehiculo_id != vehiculo_id:
            raise HTTPException(status_code=404, detail="Imagen no encontrada para este vehículo")

        if db_vehiculo.activo and len(db_vehiculo.imagenes) - 1 < MINIMO_IMAGENES:
            raise HTTPException(
                status_code=400,
                detail=f"No se puede eliminar: el vehículo activo necesita al menos {MINIMO_IMAGENES} imágenes",
            )

        supabase.storage.from_(BUCKET).remove([db_imagen.storage_path])
        db.delete(db_imagen)
        db.commit()
        db.refresh(db_vehiculo)
        return db_vehiculo