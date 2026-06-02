import os
import stripe
from sqlmodel import select
from datetime import datetime
from dotenv import load_dotenv
from src.models.pago import Pago, EstadoPago
from src.schemas.pago import PagoCrear
from src.deps.db_session import SessionDep
from fastapi import HTTPException, status

load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


class PagoService:

    @staticmethod
    def crear_pago(db: SessionDep, data: PagoCrear) -> tuple[Pago, str]:
        intent = stripe.PaymentIntent.create(
            amount=data.monto,
            currency=data.moneda,
            description=data.descripcion,
            metadata={"id_servicio": data.id_servicio}
        )

        pago = Pago(
            id_servicio=data.id_servicio,
            stripe_payment_intent_id=intent.id,
            monto=data.monto,
            moneda=data.moneda,
            descripcion=data.descripcion,
            estado=EstadoPago.pendiente,
        )
        db.add(pago)
        db.commit()
        db.refresh(pago)

        return pago, intent.client_secret

    @staticmethod
    def actualizar_estado(db: SessionDep, stripe_payment_intent_id: str, nuevo_estado: EstadoPago) -> Pago:
        pago = db.exec(
            select(Pago).where(Pago.stripe_payment_intent_id == stripe_payment_intent_id)
        ).first()

        if not pago:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pago no encontrado")

        pago.estado = nuevo_estado
        pago.fecha_actualizacion = datetime.utcnow()
        db.add(pago)
        db.commit()
        db.refresh(pago)

        return pago

    @staticmethod
    def obtener_por_servicio(db: SessionDep, id_servicio: int) -> list[Pago]:
        return db.exec(
            select(Pago).where(Pago.id_servicio == id_servicio)
        ).all()

    @staticmethod
    def obtener_por_id(db: SessionDep, pago_id: int) -> Pago:
        pago = db.get(Pago, pago_id)
        if not pago:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pago no encontrado")
        return pago