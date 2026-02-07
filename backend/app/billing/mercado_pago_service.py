"""
Mercado Pago Service - Integração com API de Assinaturas
"""
import os
import hmac
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Optional, Any
from decimal import Decimal

import httpx

from .plans import Plan, PlanTier, BillingCycle, get_plan, PLANS

logger = logging.getLogger(__name__)


class MercadoPagoError(Exception):
    """Erro específico do Mercado Pago"""
    def __init__(self, message: str, status_code: int = None, response: dict = None):
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)


class MercadoPagoService:
    """
    Serviço de integração com Mercado Pago para assinaturas recorrentes.
    
    Documentação: https://www.mercadopago.com.br/developers/pt/docs/subscriptions
    """
    
    BASE_URL = "https://api.mercadopago.com"
    
    def __init__(self):
        self.access_token = os.getenv("MERCADO_PAGO_ACCESS_TOKEN")
        self.public_key = os.getenv("MERCADO_PAGO_PUBLIC_KEY")
        self.webhook_secret = os.getenv("MERCADO_PAGO_WEBHOOK_SECRET")
        
        if not self.access_token:
            logger.warning("MERCADO_PAGO_ACCESS_TOKEN não configurado")
    
    @property
    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "X-Idempotency-Key": None,  # Será preenchido por request
        }
    
    async def _request(
        self, 
        method: str, 
        endpoint: str, 
        data: dict = None,
        idempotency_key: str = None
    ) -> dict:
        """Faz requisição para API do Mercado Pago"""
        url = f"{self.BASE_URL}{endpoint}"
        headers = self._headers.copy()
        
        if idempotency_key:
            headers["X-Idempotency-Key"] = idempotency_key
        else:
            headers.pop("X-Idempotency-Key", None)
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                    timeout=30.0
                )
                
                response_data = response.json() if response.content else {}
                
                if response.status_code >= 400:
                    logger.error(f"MP API Error: {response.status_code} - {response_data}")
                    raise MercadoPagoError(
                        message=response_data.get("message", "Erro na API do Mercado Pago"),
                        status_code=response.status_code,
                        response=response_data
                    )
                
                return response_data
                
            except httpx.RequestError as e:
                logger.error(f"MP Request Error: {e}")
                raise MercadoPagoError(f"Erro de conexão: {e}")
    
    # ==================== PLANOS ====================
    
    async def create_plan(
        self,
        plan: Plan,
        cycle: BillingCycle,
        back_url: str = None
    ) -> dict:
        """
        Cria um plano de assinatura no Mercado Pago.
        
        Deve ser chamado uma vez para cada plano/ciclo durante setup.
        """
        price = plan.price_monthly if cycle == BillingCycle.MONTHLY else plan.price_yearly
        
        frequency = 1 if cycle == BillingCycle.MONTHLY else 12
        frequency_type = "months"
        
        data = {
            "reason": f"{plan.name} - {cycle.value.capitalize()}",
            "auto_recurring": {
                "frequency": frequency,
                "frequency_type": frequency_type,
                "transaction_amount": float(price),
                "currency_id": "BRL",
            },
            "back_url": back_url or os.getenv("APP_URL", "http://localhost:3000"),
        }
        
        result = await self._request("POST", "/preapproval_plan", data)
        logger.info(f"Plano criado no MP: {result.get('id')}")
        return result
    
    async def get_plan(self, plan_id: str) -> dict:
        """Busca um plano pelo ID"""
        return await self._request("GET", f"/preapproval_plan/{plan_id}")
    
    # ==================== ASSINATURAS ====================
    
    async def create_subscription(
        self,
        plan_id: str,
        payer_email: str,
        external_reference: str,
        card_token_id: str = None,
        back_url: str = None,
    ) -> dict:
        """
        Cria uma assinatura para um usuário.
        
        Args:
            plan_id: ID do plano no Mercado Pago
            payer_email: Email do pagador
            external_reference: ID do usuário/organização no sistema
            card_token_id: Token do cartão (se pagamento com cartão)
            back_url: URL de retorno após checkout
        
        Returns:
            Dados da assinatura criada, incluindo init_point para checkout
        """
        data = {
            "preapproval_plan_id": plan_id,
            "payer_email": payer_email,
            "external_reference": external_reference,
            "back_url": back_url or os.getenv("APP_URL", "http://localhost:3000") + "/billing/callback",
        }
        
        if card_token_id:
            data["card_token_id"] = card_token_id
        
        result = await self._request(
            "POST", 
            "/preapproval", 
            data,
            idempotency_key=f"sub_{external_reference}_{plan_id}"
        )
        
        logger.info(f"Assinatura criada: {result.get('id')} para {external_reference}")
        return result
    
    async def get_subscription(self, subscription_id: str) -> dict:
        """Busca uma assinatura pelo ID"""
        return await self._request("GET", f"/preapproval/{subscription_id}")
    
    async def get_subscription_by_external_reference(self, external_reference: str) -> Optional[dict]:
        """Busca assinatura pelo external_reference (user_id)"""
        result = await self._request(
            "GET", 
            f"/preapproval/search?external_reference={external_reference}"
        )
        
        results = result.get("results", [])
        if results:
            # Retorna a assinatura mais recente ativa
            active = [s for s in results if s.get("status") == "authorized"]
            return active[0] if active else results[0]
        return None
    
    async def update_subscription(
        self,
        subscription_id: str,
        data: dict
    ) -> dict:
        """Atualiza uma assinatura"""
        return await self._request("PUT", f"/preapproval/{subscription_id}", data)
    
    async def pause_subscription(self, subscription_id: str) -> dict:
        """Pausa uma assinatura"""
        return await self.update_subscription(
            subscription_id,
            {"status": "paused"}
        )
    
    async def resume_subscription(self, subscription_id: str) -> dict:
        """Retoma uma assinatura pausada"""
        return await self.update_subscription(
            subscription_id,
            {"status": "authorized"}
        )
    
    async def cancel_subscription(self, subscription_id: str) -> dict:
        """
        Cancela uma assinatura.
        O status será 'cancelled' e não poderá ser reativada.
        """
        return await self.update_subscription(
            subscription_id,
            {"status": "cancelled"}
        )
    
    # ==================== CHECKOUT ====================
    
    async def create_checkout_preference(
        self,
        plan_tier: PlanTier,
        cycle: BillingCycle,
        user_id: str,
        user_email: str,
        success_url: str = None,
        failure_url: str = None,
        pending_url: str = None,
    ) -> dict:
        """
        Cria uma preferência de checkout para upgrade de plano.
        Retorna URL de pagamento do Mercado Pago.
        """
        plan = get_plan(plan_tier)
        price = plan.price_monthly if cycle == BillingCycle.MONTHLY else plan.price_yearly
        
        base_url = os.getenv("APP_URL", "http://localhost:3000")
        
        data = {
            "items": [
                {
                    "id": plan.id,
                    "title": f"Assinatura {plan.name} ({cycle.value})",
                    "description": plan.description,
                    "quantity": 1,
                    "currency_id": "BRL",
                    "unit_price": float(price),
                }
            ],
            "payer": {
                "email": user_email,
            },
            "external_reference": f"{user_id}|{plan_tier.value}|{cycle.value}",
            "back_urls": {
                "success": success_url or f"{base_url}/billing/success",
                "failure": failure_url or f"{base_url}/billing/failure",
                "pending": pending_url or f"{base_url}/billing/pending",
            },
            "auto_return": "approved",
            "notification_url": f"{base_url}/api/webhooks/mercadopago",
        }
        
        result = await self._request("POST", "/checkout/preferences", data)
        
        return {
            "preference_id": result.get("id"),
            "init_point": result.get("init_point"),  # URL de pagamento
            "sandbox_init_point": result.get("sandbox_init_point"),  # URL sandbox
        }
    
    # ==================== WEBHOOKS ====================
    
    def verify_webhook_signature(
        self,
        x_signature: str,
        x_request_id: str,
        data_id: str,
    ) -> bool:
        """
        Verifica a assinatura do webhook do Mercado Pago.
        
        Headers necessários:
        - x-signature: assinatura HMAC
        - x-request-id: ID da requisição
        
        Query params:
        - data.id: ID do recurso
        """
        if not self.webhook_secret:
            logger.warning("MERCADO_PAGO_WEBHOOK_SECRET não configurado")
            return True  # Em dev, aceita todos
        
        # Extrai ts e v1 do header x-signature
        # Formato: ts=xxx,v1=yyy
        parts = dict(p.split("=") for p in x_signature.split(","))
        ts = parts.get("ts")
        v1 = parts.get("v1")
        
        if not ts or not v1:
            return False
        
        # Monta o manifest
        manifest = f"id:{data_id};request-id:{x_request_id};ts:{ts};"
        
        # Calcula HMAC-SHA256
        expected_signature = hmac.new(
            self.webhook_secret.encode(),
            manifest.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(v1, expected_signature)
    
    async def process_webhook(self, webhook_data: dict) -> dict:
        """
        Processa notificação de webhook do Mercado Pago.
        
        Tipos de eventos:
        - payment: pagamento realizado
        - subscription_preapproval: mudança em assinatura
        - subscription_authorized_payment: pagamento de assinatura
        """
        action = webhook_data.get("action")
        data_type = webhook_data.get("type")
        data_id = webhook_data.get("data", {}).get("id")
        
        logger.info(f"Webhook recebido: type={data_type}, action={action}, id={data_id}")
        
        result = {
            "processed": True,
            "action": action,
            "type": data_type,
            "data_id": data_id,
        }
        
        if data_type == "payment":
            # Busca detalhes do pagamento
            payment = await self._request("GET", f"/v1/payments/{data_id}")
            result["payment"] = payment
            result["status"] = payment.get("status")
            result["external_reference"] = payment.get("external_reference")
            
        elif data_type == "subscription_preapproval":
            # Busca detalhes da assinatura
            subscription = await self.get_subscription(data_id)
            result["subscription"] = subscription
            result["status"] = subscription.get("status")
            result["external_reference"] = subscription.get("external_reference")
        
        return result
    
    # ==================== PAGAMENTOS ====================
    
    async def get_payment(self, payment_id: str) -> dict:
        """Busca um pagamento pelo ID"""
        return await self._request("GET", f"/v1/payments/{payment_id}")
    
    async def refund_payment(self, payment_id: str, amount: float = None) -> dict:
        """
        Reembolsa um pagamento.
        Se amount não for especificado, reembolsa o valor total.
        """
        data = {}
        if amount:
            data["amount"] = amount
        
        return await self._request("POST", f"/v1/payments/{payment_id}/refunds", data)


# Singleton
_mp_service: Optional[MercadoPagoService] = None


def get_mercado_pago_service() -> MercadoPagoService:
    """Retorna instância singleton do serviço"""
    global _mp_service
    if _mp_service is None:
        _mp_service = MercadoPagoService()
    return _mp_service
