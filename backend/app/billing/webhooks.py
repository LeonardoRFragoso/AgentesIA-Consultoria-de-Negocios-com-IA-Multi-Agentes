"""
Webhook Handler - Mercado Pago Notifications
"""
import logging
from typing import Optional

from fastapi import APIRouter, Request, HTTPException, Header, Query
from pydantic import BaseModel

from .mercado_pago_service import get_mercado_pago_service
from .subscription_service import get_subscription_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


class WebhookPayload(BaseModel):
    """Schema do payload de webhook do Mercado Pago"""
    id: Optional[str] = None
    live_mode: Optional[bool] = None
    type: Optional[str] = None
    date_created: Optional[str] = None
    user_id: Optional[str] = None
    api_version: Optional[str] = None
    action: Optional[str] = None
    data: Optional[dict] = None


@router.post("/mercadopago")
async def mercadopago_webhook(
    request: Request,
    # Query params enviados pelo MP
    data_id: Optional[str] = Query(None, alias="data.id"),
    webhook_type: Optional[str] = Query(None, alias="type"),
    # Headers de segurança
    x_signature: Optional[str] = Header(None),
    x_request_id: Optional[str] = Header(None),
):
    """
    Endpoint para receber webhooks do Mercado Pago.
    
    Eventos tratados:
    - payment: Notificações de pagamento
    - subscription_preapproval: Mudanças em assinaturas
    - subscription_authorized_payment: Pagamentos de assinatura
    
    Documentação: https://www.mercadopago.com.br/developers/pt/docs/subscriptions/webhooks
    """
    mp_service = get_mercado_pago_service()
    subscription_service = get_subscription_service()
    
    # Tenta ler o body (pode vir vazio em notificações IPN)
    try:
        body = await request.json()
    except:
        body = {}
    
    logger.info(f"Webhook received: type={webhook_type}, data_id={data_id}")
    logger.debug(f"Webhook body: {body}")
    logger.debug(f"Webhook headers: x-signature={x_signature}, x-request-id={x_request_id}")
    
    # Verifica assinatura (em produção)
    if x_signature and data_id:
        is_valid = mp_service.verify_webhook_signature(
            x_signature=x_signature,
            x_request_id=x_request_id or "",
            data_id=data_id,
        )
        if not is_valid:
            logger.warning(f"Invalid webhook signature for data_id={data_id}")
            raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Monta dados do webhook
    webhook_data = {
        "type": webhook_type or body.get("type"),
        "action": body.get("action"),
        "data": body.get("data", {"id": data_id}),
    }
    
    if not webhook_data["data"].get("id") and data_id:
        webhook_data["data"]["id"] = data_id
    
    # Processa o evento
    try:
        result = await subscription_service.process_webhook_event(webhook_data)
        logger.info(f"Webhook processed: {result}")
        return {"status": "ok", "processed": True}
        
    except Exception as e:
        logger.error(f"Error processing webhook: {e}", exc_info=True)
        # Retorna 200 para evitar retry infinito do MP
        return {"status": "error", "message": str(e)}


@router.post("/mercadopago/ipn")
async def mercadopago_ipn(
    request: Request,
    topic: Optional[str] = Query(None),
    id: Optional[str] = Query(None),
):
    """
    Endpoint alternativo para IPN (Instant Payment Notification).
    
    Alguns eventos do MP usam IPN ao invés de webhooks.
    """
    mp_service = get_mercado_pago_service()
    subscription_service = get_subscription_service()
    
    logger.info(f"IPN received: topic={topic}, id={id}")
    
    if not topic or not id:
        return {"status": "ok", "message": "No data to process"}
    
    # Mapeia topic para type
    type_mapping = {
        "payment": "payment",
        "merchant_order": "merchant_order",
        "preapproval": "subscription_preapproval",
    }
    
    webhook_data = {
        "type": type_mapping.get(topic, topic),
        "action": "notification",
        "data": {"id": id},
    }
    
    try:
        result = await subscription_service.process_webhook_event(webhook_data)
        return {"status": "ok", "processed": True}
    except Exception as e:
        logger.error(f"Error processing IPN: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}


@router.get("/mercadopago/test")
async def test_webhook():
    """
    Endpoint de teste para verificar se webhooks estão configurados.
    
    Use para configurar a URL no painel do Mercado Pago.
    """
    return {
        "status": "ok",
        "message": "Webhook endpoint is working",
        "endpoints": {
            "webhook": "/api/webhooks/mercadopago",
            "ipn": "/api/webhooks/mercadopago/ipn",
        }
    }
