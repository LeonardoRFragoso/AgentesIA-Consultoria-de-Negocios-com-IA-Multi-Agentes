"""
API Routes - Billing & Subscriptions
"""
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Request, Depends, Query, Header
from pydantic import BaseModel, EmailStr

from .plans import PlanTier, BillingCycle, get_all_plans, get_plan
from .subscription_service import get_subscription_service, SubscriptionService
from .mercado_pago_service import get_mercado_pago_service, MercadoPagoError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/billing", tags=["billing"])


# ==================== SCHEMAS ====================

class CheckoutRequest(BaseModel):
    plan_tier: str  # "pro" ou "enterprise"
    cycle: str = "monthly"  # "monthly" ou "yearly"


class CheckoutResponse(BaseModel):
    checkout_url: str
    sandbox_url: Optional[str] = None
    preference_id: str
    plan: dict


class SubscriptionStatusResponse(BaseModel):
    tier: str
    status: str
    cycle: Optional[str] = None
    expires_at: Optional[str] = None
    usage: dict


class CancelRequest(BaseModel):
    immediate: bool = False
    reason: Optional[str] = None


# ==================== DEPENDENCIES ====================

async def get_current_user(request: Request) -> dict:
    """
    Dependency para obter usuário atual.
    Substitua pela sua lógica de autenticação.
    """
    # TODO: Implementar autenticação real
    # Exemplo com JWT:
    # token = request.headers.get("Authorization")
    # user = await verify_jwt(token)
    
    # Mock para desenvolvimento
    return {
        "id": "user_123",
        "email": "user@example.com",
        "organization": {
            "id": "org_123",
            "plan": "free",
            "billing_cycle": None,
            "mp_subscription_id": None,
            "analyses_used_this_month": 0,
        }
    }


def get_service() -> SubscriptionService:
    """Dependency para obter serviço de assinaturas"""
    return get_subscription_service()


# ==================== ROUTES ====================

@router.get("/plans")
async def list_plans():
    """
    Lista todos os planos disponíveis.
    
    Retorna detalhes de cada plano incluindo preços e features.
    """
    return {
        "plans": get_all_plans(),
        "currency": "BRL",
        "default_cycle": "monthly",
    }


@router.get("/plans/{tier}")
async def get_plan_details(tier: str):
    """Retorna detalhes de um plano específico"""
    try:
        plan_tier = PlanTier(tier)
    except ValueError:
        raise HTTPException(status_code=404, detail="Plano não encontrado")
    
    plan = get_plan(plan_tier)
    return {
        "id": plan.id,
        "tier": plan.tier.value,
        "name": plan.name,
        "description": plan.description,
        "price_monthly": float(plan.price_monthly),
        "price_yearly": float(plan.price_yearly),
        "features": {
            "analyses_per_month": plan.features.analyses_per_month,
            "agents_available": plan.features.agents_available,
            "export_formats": plan.features.export_formats,
            "priority_level": plan.features.priority_level,
            "api_access": plan.features.api_access,
            "custom_agents": plan.features.custom_agents,
            "dedicated_support": plan.features.dedicated_support,
            "sla_guarantee": plan.features.sla_guarantee,
        },
    }


@router.post("/checkout", response_model=CheckoutResponse)
async def create_checkout(
    request: CheckoutRequest,
    user: dict = Depends(get_current_user),
    service: SubscriptionService = Depends(get_service),
):
    """
    Cria sessão de checkout para upgrade de plano.
    
    Retorna URL do Mercado Pago para pagamento.
    """
    try:
        plan_tier = PlanTier(request.plan_tier)
    except ValueError:
        raise HTTPException(status_code=400, detail="Plano inválido")
    
    try:
        cycle = BillingCycle(request.cycle)
    except ValueError:
        raise HTTPException(status_code=400, detail="Ciclo inválido. Use 'monthly' ou 'yearly'")
    
    current_tier = PlanTier(user["organization"]["plan"])
    
    if plan_tier == PlanTier.FREE:
        raise HTTPException(status_code=400, detail="Não é possível assinar o plano Free")
    
    if plan_tier == current_tier:
        raise HTTPException(status_code=400, detail="Você já está neste plano")
    
    try:
        result = await service.create_checkout(
            user_id=user["id"],
            user_email=user["email"],
            target_tier=plan_tier,
            cycle=cycle,
            current_tier=current_tier,
        )
        return result
    except MercadoPagoError as e:
        logger.error(f"MP Error creating checkout: {e}")
        raise HTTPException(status_code=502, detail="Erro ao criar checkout")


@router.get("/status", response_model=SubscriptionStatusResponse)
async def get_subscription_status(
    user: dict = Depends(get_current_user),
    service: SubscriptionService = Depends(get_service),
):
    """
    Retorna status atual da assinatura do usuário.
    
    Inclui:
    - Plano atual
    - Status da assinatura
    - Uso atual vs limites
    """
    org = user["organization"]
    current_tier = PlanTier(org["plan"])
    
    usage = await service.check_usage_limits(
        user_id=user["id"],
        current_tier=current_tier,
        analyses_used=org.get("analyses_used_this_month", 0),
    )
    
    return {
        "tier": current_tier.value,
        "status": "active" if current_tier != PlanTier.FREE else "free",
        "cycle": org.get("billing_cycle"),
        "expires_at": org.get("subscription_expires_at"),
        "usage": usage,
    }


@router.post("/cancel")
async def cancel_subscription(
    request: CancelRequest,
    user: dict = Depends(get_current_user),
    service: SubscriptionService = Depends(get_service),
):
    """
    Cancela a assinatura do usuário.
    
    Se `immediate=true`, faz downgrade imediato para Free.
    Caso contrário, mantém acesso até fim do período pago.
    """
    org = user["organization"]
    
    if org["plan"] == "free":
        raise HTTPException(status_code=400, detail="Você já está no plano Free")
    
    mp_subscription_id = org.get("mp_subscription_id")
    
    result = await service.cancel_subscription(
        user_id=user["id"],
        mp_subscription_id=mp_subscription_id,
        immediate=request.immediate,
    )
    
    return result


@router.post("/pause")
async def pause_subscription(
    user: dict = Depends(get_current_user),
    service: SubscriptionService = Depends(get_service),
):
    """Pausa temporariamente a assinatura"""
    org = user["organization"]
    
    if org["plan"] == "free":
        raise HTTPException(status_code=400, detail="Plano Free não pode ser pausado")
    
    mp_subscription_id = org.get("mp_subscription_id")
    if not mp_subscription_id:
        raise HTTPException(status_code=400, detail="Nenhuma assinatura ativa encontrada")
    
    return await service.pause_subscription(
        user_id=user["id"],
        mp_subscription_id=mp_subscription_id,
    )


@router.post("/resume")
async def resume_subscription(
    user: dict = Depends(get_current_user),
    service: SubscriptionService = Depends(get_service),
):
    """Retoma uma assinatura pausada"""
    org = user["organization"]
    mp_subscription_id = org.get("mp_subscription_id")
    
    if not mp_subscription_id:
        raise HTTPException(status_code=400, detail="Nenhuma assinatura encontrada")
    
    return await service.resume_subscription(
        user_id=user["id"],
        mp_subscription_id=mp_subscription_id,
    )


@router.get("/usage")
async def get_usage(
    user: dict = Depends(get_current_user),
    service: SubscriptionService = Depends(get_service),
):
    """
    Retorna uso atual do plano.
    
    Útil para mostrar barra de progresso e alertas de limite.
    """
    org = user["organization"]
    current_tier = PlanTier(org["plan"])
    
    return await service.check_usage_limits(
        user_id=user["id"],
        current_tier=current_tier,
        analyses_used=org.get("analyses_used_this_month", 0),
    )


# ==================== CALLBACKS ====================

@router.get("/callback/success")
async def payment_success(
    collection_id: Optional[str] = Query(None),
    collection_status: Optional[str] = Query(None),
    payment_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    external_reference: Optional[str] = Query(None),
    payment_type: Optional[str] = Query(None),
    merchant_order_id: Optional[str] = Query(None),
    preference_id: Optional[str] = Query(None),
    service: SubscriptionService = Depends(get_service),
):
    """
    Callback de pagamento aprovado.
    
    Mercado Pago redireciona aqui após pagamento bem-sucedido.
    """
    logger.info(f"Payment success callback: status={status}, ref={external_reference}")
    
    if external_reference:
        result = await service.process_payment_callback(
            external_reference=external_reference,
            payment_status="approved",
            payment_id=payment_id or collection_id,
        )
        return {
            "status": "success",
            "message": "Pagamento aprovado! Seu plano foi atualizado.",
            "details": result,
        }
    
    return {
        "status": "success",
        "message": "Pagamento aprovado!",
    }


@router.get("/callback/failure")
async def payment_failure(
    collection_id: Optional[str] = Query(None),
    collection_status: Optional[str] = Query(None),
    external_reference: Optional[str] = Query(None),
):
    """Callback de pagamento rejeitado"""
    logger.warning(f"Payment failure callback: ref={external_reference}")
    
    return {
        "status": "failure",
        "message": "Pagamento não aprovado. Tente novamente.",
    }


@router.get("/callback/pending")
async def payment_pending(
    collection_id: Optional[str] = Query(None),
    external_reference: Optional[str] = Query(None),
):
    """Callback de pagamento pendente"""
    logger.info(f"Payment pending callback: ref={external_reference}")
    
    return {
        "status": "pending",
        "message": "Pagamento em processamento. Você receberá uma confirmação em breve.",
    }
