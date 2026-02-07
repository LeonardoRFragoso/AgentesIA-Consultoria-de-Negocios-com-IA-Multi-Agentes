"""
Estrutura de Planos SaaS - Mercado Pago Integration
"""
from enum import Enum
from dataclasses import dataclass
from typing import Optional
from decimal import Decimal


class PlanTier(str, Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class BillingCycle(str, Enum):
    MONTHLY = "monthly"
    YEARLY = "yearly"


@dataclass
class PlanFeatures:
    """Features disponíveis em cada plano"""
    analyses_per_month: int
    agents_available: int
    export_formats: list[str]
    priority_level: str
    api_access: bool
    custom_agents: bool
    dedicated_support: bool
    sla_guarantee: bool


@dataclass
class Plan:
    """Definição de um plano"""
    id: str
    tier: PlanTier
    name: str
    description: str
    price_monthly: Decimal
    price_yearly: Decimal
    features: PlanFeatures
    mercado_pago_plan_id_monthly: Optional[str] = None
    mercado_pago_plan_id_yearly: Optional[str] = None
    is_active: bool = True


# Definição dos planos
PLANS = {
    PlanTier.FREE: Plan(
        id="plan_free",
        tier=PlanTier.FREE,
        name="Free",
        description="Para começar a explorar",
        price_monthly=Decimal("0"),
        price_yearly=Decimal("0"),
        features=PlanFeatures(
            analyses_per_month=3,
            agents_available=3,
            export_formats=["PDF"],
            priority_level="normal",
            api_access=False,
            custom_agents=False,
            dedicated_support=False,
            sla_guarantee=False,
        ),
    ),
    PlanTier.PRO: Plan(
        id="plan_pro",
        tier=PlanTier.PRO,
        name="Pro",
        description="Para profissionais e equipes",
        price_monthly=Decimal("97"),
        price_yearly=Decimal("970"),  # ~2 meses grátis
        features=PlanFeatures(
            analyses_per_month=50,
            agents_available=5,
            export_formats=["PDF", "DOCX", "Excel"],
            priority_level="high",
            api_access=True,
            custom_agents=False,
            dedicated_support=False,
            sla_guarantee=False,
        ),
        mercado_pago_plan_id_monthly="MP_PLAN_PRO_MONTHLY",
        mercado_pago_plan_id_yearly="MP_PLAN_PRO_YEARLY",
    ),
    PlanTier.ENTERPRISE: Plan(
        id="plan_enterprise",
        tier=PlanTier.ENTERPRISE,
        name="Enterprise",
        description="Para grandes organizações",
        price_monthly=Decimal("497"),
        price_yearly=Decimal("4970"),  # ~2 meses grátis
        features=PlanFeatures(
            analyses_per_month=-1,  # Ilimitado
            agents_available=5,
            export_formats=["PDF", "DOCX", "Excel", "API"],
            priority_level="maximum",
            api_access=True,
            custom_agents=True,
            dedicated_support=True,
            sla_guarantee=True,
        ),
        mercado_pago_plan_id_monthly="MP_PLAN_ENTERPRISE_MONTHLY",
        mercado_pago_plan_id_yearly="MP_PLAN_ENTERPRISE_YEARLY",
    ),
}


def get_plan(tier: PlanTier) -> Plan:
    """Retorna o plano pelo tier"""
    return PLANS.get(tier, PLANS[PlanTier.FREE])


def get_plan_by_id(plan_id: str) -> Optional[Plan]:
    """Retorna o plano pelo ID"""
    for plan in PLANS.values():
        if plan.id == plan_id:
            return plan
    return None


def get_plan_price(tier: PlanTier, cycle: BillingCycle) -> Decimal:
    """Retorna o preço do plano pelo ciclo"""
    plan = get_plan(tier)
    if cycle == BillingCycle.YEARLY:
        return plan.price_yearly
    return plan.price_monthly


def can_upgrade(current_tier: PlanTier, target_tier: PlanTier) -> bool:
    """Verifica se pode fazer upgrade"""
    tier_order = {PlanTier.FREE: 0, PlanTier.PRO: 1, PlanTier.ENTERPRISE: 2}
    return tier_order.get(target_tier, 0) > tier_order.get(current_tier, 0)


def can_downgrade(current_tier: PlanTier, target_tier: PlanTier) -> bool:
    """Verifica se pode fazer downgrade"""
    tier_order = {PlanTier.FREE: 0, PlanTier.PRO: 1, PlanTier.ENTERPRISE: 2}
    return tier_order.get(target_tier, 0) < tier_order.get(current_tier, 0)


def get_all_plans() -> list[dict]:
    """Retorna todos os planos como dicionários"""
    return [
        {
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
        for plan in PLANS.values()
    ]
