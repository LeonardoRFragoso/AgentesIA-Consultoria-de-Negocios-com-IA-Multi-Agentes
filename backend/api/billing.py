"""
Billing endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from uuid import UUID

from database import get_db
from security.auth import get_tenant_context, TenantContext
from services.billing_service import BillingService
from config import get_settings
from api.schemas import BillingStatusResponse, CheckoutSessionResponse

router = APIRouter(prefix="/billing", tags=["Billing"])


@router.get("/plans")
async def get_plans():
    """
    Retorna lista de planos disponíveis.
    Endpoint público (não requer autenticação).
    """
    return {
        "plans": [
            {
                "id": "free",
                "name": "Free",
                "price": 0,
                "currency": "BRL",
                "interval": "month",
                "features": [
                    "5 análises por mês",
                    "Agentes básicos",
                    "Exportação Markdown",
                    "Suporte por email"
                ],
                "limits": {
                    "analyses_per_month": 5,
                    "export_formats": ["markdown"],
                    "priority_support": False,
                    "max_agents": 2,
                    "agents_note": "Escolha 2 agentes por análise"
                }
            },
            {
                "id": "pro",
                "name": "Pro",
                "price": 97,
                "currency": "BRL",
                "interval": "month",
                "features": [
                    "50 análises por mês",
                    "Todos os agentes",
                    "Exportação PDF e PowerPoint",
                    "Suporte prioritário",
                    "Histórico completo"
                ],
                "limits": {
                    "analyses_per_month": 50,
                    "export_formats": ["markdown", "pdf", "pptx"],
                    "priority_support": True,
                    "max_agents": 5,
                    "agents_note": "Todos os 5 agentes especializados"
                }
            },
            {
                "id": "enterprise",
                "name": "Enterprise",
                "price": 297,
                "currency": "BRL",
                "interval": "month",
                "features": [
                    "Análises ilimitadas",
                    "Todos os agentes",
                    "Todos os formatos de exportação",
                    "Suporte dedicado",
                    "API access",
                    "White-label"
                ],
                "limits": {
                    "analyses_per_month": -1,
                    "export_formats": ["markdown", "pdf", "pptx", "xlsx"],
                    "priority_support": True,
                    "api_access": True,
                    "max_agents": 5,
                    "agents_note": "Todos os 5 agentes especializados"
                }
            }
        ]
    }


@router.get("/status", response_model=BillingStatusResponse)
async def get_billing_status(
    db: Session = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context)
):
    """
    Retorna status de billing da organização.
    """
    billing_service = BillingService(db)
    stats = billing_service.get_usage_stats(UUID(tenant.org_id))
    
    return BillingStatusResponse(**stats)


@router.get("/agent-limits")
async def get_agent_limits(
    db: Session = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context)
):
    """
    Retorna limites de agentes para o plano do usuário.
    
    Returns:
        - max_agents: Número máximo de agentes que podem ser selecionados
        - agents_allowed: Lista de agentes disponíveis para seleção
        - plan: Plano atual (free, pro, enterprise)
    """
    billing_service = BillingService(db)
    limits = billing_service.get_agent_limits(UUID(tenant.org_id))
    
    # Adiciona descrições dos agentes
    agent_descriptions = {
        "analyst": {
            "id": "analyst",
            "name": "Analista de Negócios",
            "description": "Análise estratégica do problema e oportunidades",
            "emoji": "📊"
        },
        "commercial": {
            "id": "commercial",
            "name": "Especialista Comercial",
            "description": "Estratégias de vendas e relacionamento com clientes",
            "emoji": "💼"
        },
        "financial": {
            "id": "financial",
            "name": "Especialista Financeiro",
            "description": "Análise de custos, ROI e viabilidade financeira",
            "emoji": "💰"
        },
        "market": {
            "id": "market",
            "name": "Especialista de Mercado",
            "description": "Análise competitiva e tendências de mercado",
            "emoji": "📈"
        },
    }
    
    return {
        "max_agents": limits["max_agents"],
        "plan": limits["plan"],
        "agents": [agent_descriptions[a] for a in limits["agents_allowed"] if a in agent_descriptions],
        "note": "O Revisor Executivo é incluído automaticamente para gerar o resumo."
    }


@router.post("/checkout/{plan}", response_model=CheckoutSessionResponse)
async def create_checkout_session(
    plan: str,
    request: Request,
    db: Session = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context)
):
    """
    Cria sessão de checkout no Stripe.
    """
    if plan not in ["pro_monthly", "pro_yearly", "enterprise_monthly", "enterprise_yearly"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Plano inválido"
        )
    
    # Verifica se é owner
    if not tenant.is_owner():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas o owner pode gerenciar billing"
        )
    
    settings = get_settings()
    
    if not settings.STRIPE_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Stripe não configurado"
        )
    
    try:
        import stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        # Mapeamento de planos para prices
        price_map = {
            "pro_monthly": settings.STRIPE_PRICE_PRO_MONTHLY,
            "pro_yearly": settings.STRIPE_PRICE_PRO_YEARLY,
            "enterprise_monthly": settings.STRIPE_PRICE_ENTERPRISE_MONTHLY,
        }
        
        price_id = price_map.get(plan)
        if not price_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Plano não disponível"
            )
        
        # Cria sessão de checkout
        base_url = str(request.base_url).rstrip("/")
        
        session = stripe.checkout.Session.create(
            mode="subscription",
            line_items=[{"price": price_id, "quantity": 1}],
            success_url=f"{base_url}/settings/billing?success=true",
            cancel_url=f"{base_url}/settings/billing?canceled=true",
            metadata={
                "org_id": tenant.org_id,
                "user_id": tenant.user_id
            }
        )
        
        return CheckoutSessionResponse(
            checkout_url=session.url,
            session_id=session.id
        )
        
    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Stripe SDK não instalado"
        )


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Webhook para eventos do Stripe.
    """
    settings = get_settings()
    
    if not settings.STRIPE_WEBHOOK_SECRET:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Webhook não configurado"
        )
    
    try:
        import stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        payload = await request.body()
        sig_header = request.headers.get("stripe-signature")
        
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
        
        billing_service = BillingService(db)
        
        if event.type == "checkout.session.completed":
            session = event.data.object
            org_id = session.metadata.get("org_id")
            
            if org_id:
                from database.models import PlanType
                # Determina plano pelo price
                # TODO: Mapear price_id para plano
                billing_service.upgrade_plan(UUID(org_id), PlanType.PRO)
        
        elif event.type == "customer.subscription.deleted":
            # Downgrade para free
            subscription = event.data.object
            # TODO: Recuperar org_id do customer
            pass
        
        elif event.type == "invoice.payment_failed":
            # Notificar usuário
            pass
        
        return {"status": "ok"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/portal")
async def get_billing_portal(
    request: Request,
    db: Session = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context)
):
    """
    Retorna URL do portal de billing do Stripe.
    """
    if not tenant.is_owner():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas o owner pode acessar o portal de billing"
        )
    
    settings = get_settings()
    
    if not settings.STRIPE_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Stripe não configurado"
        )
    
    try:
        import stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        # Busca customer_id da organização
        from services.user_service import UserService
        user_service = UserService(db)
        org = user_service.get_organization(UUID(tenant.org_id))
        
        if not org or not org.stripe_customer_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nenhuma assinatura encontrada"
            )
        
        base_url = str(request.base_url).rstrip("/")
        
        session = stripe.billing_portal.Session.create(
            customer=org.stripe_customer_id,
            return_url=f"{base_url}/settings/billing"
        )
        
        return {"portal_url": session.url}
        
    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Stripe SDK não instalado"
        )
