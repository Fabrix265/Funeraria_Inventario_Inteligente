import os
import stripe
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Request
from src.deps.db_session import SessionDep
from src.schemas.pago import PagoCrear, PagoResponse
from src.services.pago_service import PagoService
from src.models.pago import EstadoPago
from src.schemas.pago import PagoCrear, PagoResponse, PagoLeer

load_dotenv()
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

pago_router = APIRouter()


@pago_router.post("/crear-intent", response_model=PagoResponse)
def crear_payment_intent(data: PagoCrear, db: SessionDep):
    try:
        pago, client_secret = PagoService.crear_pago(db, data)
        return {**pago.dict(), "client_secret": client_secret}
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@pago_router.post("/webhook")
async def stripe_webhook(request: Request, db: SessionDep):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Payload inválido")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Firma inválida")

    if event["type"] == "payment_intent.succeeded":
        intent = event["data"]["object"]
        PagoService.actualizar_estado(db, intent["id"], EstadoPago.completado)

    elif event["type"] == "payment_intent.payment_failed":
        intent = event["data"]["object"]
        PagoService.actualizar_estado(db, intent["id"], EstadoPago.fallido)

    return {"status": "ok"}

@pago_router.get("/servicio/{id_servicio}", response_model=list[PagoLeer])
def pagos_por_servicio(id_servicio: int, db: SessionDep):
    return PagoService.obtener_por_servicio(db, id_servicio)

@pago_router.get("/{pago_id}", response_model=PagoLeer)
def obtener_pago(pago_id: int, db: SessionDep):
    return PagoService.obtener_por_id(db, pago_id)