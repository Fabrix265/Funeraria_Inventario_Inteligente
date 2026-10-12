from sqlmodel import Session, select, col
from fastapi import HTTPException, UploadFile
from typing import Optional
import uuid

from src.core.supabase_config import supabase
from src.models.ataud import Ataud, AtaudImagen
from src.schemas.ataud import AtaudCrear, AtaudModificar

MINIMO_IMAGENES = 3
BUCKET = "ataudes"


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
        activo: Optional[bool] = None,
    ):
        statement = select(Ataud)

        if activo is not None:
            statement = statement.where(Ataud.activo == activo)
        if modelo:
            statement = statement.where(col(Ataud.modelo).ilike(f"%{modelo}%"))
        if color:
            statement = statement.where(col(Ataud.color).ilike(f"%{color}%"))
        if stock_min is not None:
            statement = statement.where(Ataud.stock >= stock_min)

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

        for imagen in db_ataud.imagenes:
            supabase.storage.from_(BUCKET).remove([imagen.storage_path])

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

    @staticmethod
    def cambiar_estado(db: Session, ataud_id: int, activo: bool):
        db_ataud = db.get(Ataud, ataud_id)
        if not db_ataud:
            raise HTTPException(status_code=404, detail="Ataud no encontrado")

        if activo and len(db_ataud.imagenes) < MINIMO_IMAGENES:
            raise HTTPException(
                status_code=400,
                detail=f"No se puede activar el ataúd: necesita al menos {MINIMO_IMAGENES} imágenes (tiene {len(db_ataud.imagenes)})",
            )

        db_ataud.activo = activo
        db.add(db_ataud)
        db.commit()
        db.refresh(db_ataud)
        return db_ataud

    @staticmethod
    def agregar_imagen(db: Session, ataud_id: int, archivo: UploadFile):
        db_ataud = db.get(Ataud, ataud_id)
        if not db_ataud:
            raise HTTPException(status_code=404, detail="Ataud no encontrado")

        extension = archivo.filename.split(".")[-1] if "." in archivo.filename else "jpg"
        ruta = f"{ataud_id}/{uuid.uuid4()}.{extension}"

        contenido = archivo.file.read()
        supabase.storage.from_(BUCKET).upload(
            ruta, contenido, {"content-type": archivo.content_type}
        )
        url_publica = supabase.storage.from_(BUCKET).get_public_url(ruta)

        nueva_imagen = AtaudImagen(ataud_id=ataud_id, url=url_publica, storage_path=ruta)
        db.add(nueva_imagen)
        db.commit()
        db.refresh(db_ataud)
        return db_ataud

    @staticmethod
    def eliminar_imagen(db: Session, ataud_id: int, imagen_id: int):
        db_ataud = db.get(Ataud, ataud_id)
        if not db_ataud:
            raise HTTPException(status_code=404, detail="Ataud no encontrado")

        db_imagen = db.get(AtaudImagen, imagen_id)
        if not db_imagen or db_imagen.ataud_id != ataud_id:
            raise HTTPException(status_code=404, detail="Imagen no encontrada para este ataúd")

        if db_ataud.activo and len(db_ataud.imagenes) - 1 < MINIMO_IMAGENES:
            raise HTTPException(
                status_code=400,
                detail=f"No se puede eliminar: el ataúd activo necesita al menos {MINIMO_IMAGENES} imágenes",
            )

        supabase.storage.from_(BUCKET).remove([db_imagen.storage_path])
        db.delete(db_imagen)
        db.commit()
        db.refresh(db_ataud)
        return db_ataud