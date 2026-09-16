from sqlmodel import Session, select, col
from fastapi import HTTPException, UploadFile
from typing import Optional
import cloudinary.uploader

from src.core import cloudinary_config
from src.models.capilla import Capilla, CapillaImagen
from src.schemas.capilla import CapillaCrear

MINIMO_IMAGENES = 3

class CapillaService:
    @staticmethod
    def crear(db: Session, capilla_in: CapillaCrear):
        nueva_capilla = Capilla.model_validate(capilla_in)
        db.add(nueva_capilla)
        db.commit()
        db.refresh(nueva_capilla)
        return nueva_capilla

    @staticmethod
    def obtener_todas(db: Session, modelo: Optional[str] = None, activo: Optional[bool] = None):
        statement = select(Capilla)
        if activo is not None:
            statement = statement.where(Capilla.activo == activo)
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

        for imagen in db_capilla.imagenes:
            cloudinary.uploader.destroy(imagen.public_id)

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

    @staticmethod
    def cambiar_estado(db: Session, capilla_id: int, activo: bool):
        db_capilla = db.get(Capilla, capilla_id)
        if not db_capilla:
            raise HTTPException(status_code=404, detail="Capilla no encontrada")

        if activo and len(db_capilla.imagenes) < MINIMO_IMAGENES:
            raise HTTPException(
                status_code=400,
                detail=f"No se puede activar la capilla: necesita al menos {MINIMO_IMAGENES} imágenes (tiene {len(db_capilla.imagenes)})",
            )

        db_capilla.activo = activo
        db.add(db_capilla)
        db.commit()
        db.refresh(db_capilla)
        return db_capilla

    @staticmethod
    def agregar_imagen(db: Session, capilla_id: int, archivo: UploadFile):
        db_capilla = db.get(Capilla, capilla_id)
        if not db_capilla:
            raise HTTPException(status_code=404, detail="Capilla no encontrada")

        resultado = cloudinary.uploader.upload(
            archivo.file,
            folder="capillas",
        )

        nueva_imagen = CapillaImagen(
            capilla_id=capilla_id,
            url=resultado["secure_url"],
            public_id=resultado["public_id"],
        )
        db.add(nueva_imagen)
        db.commit()
        db.refresh(db_capilla)
        return db_capilla

    @staticmethod
    def eliminar_imagen(db: Session, capilla_id: int, imagen_id: int):
        db_capilla = db.get(Capilla, capilla_id)
        if not db_capilla:
            raise HTTPException(status_code=404, detail="Capilla no encontrada")

        db_imagen = db.get(CapillaImagen, imagen_id)
        if not db_imagen or db_imagen.capilla_id != capilla_id:
            raise HTTPException(status_code=404, detail="Imagen no encontrada para esta capilla")

        if db_capilla.activo and len(db_capilla.imagenes) - 1 < MINIMO_IMAGENES:
            raise HTTPException(
                status_code=400,
                detail=f"No se puede eliminar: la capilla activa necesita al menos {MINIMO_IMAGENES} imágenes",
            )

        cloudinary.uploader.destroy(db_imagen.public_id)
        db.delete(db_imagen)
        db.commit()
        db.refresh(db_capilla)
        return db_capilla