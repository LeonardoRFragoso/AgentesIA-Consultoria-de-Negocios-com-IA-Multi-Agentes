"""
Subscription Service - Gerenciamento de assinaturas e billing
"""
import logging
from datetime import datetime, timedelta
from typing import Optional
from enum import Enum

from .plans import PlanTier, BillingCycle, get_plan, can_upgrade, can_downgrade
from .mercado_pago_service import MercadoPagoService, get_mercado_pago_service

logger = logging.getLogger(__name__)


class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    PENDING = "pending"
    PAUSED = "paused"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class SubscriptionService:
    """
    Serviço para gerenciar assinaturas de usuários/organizações.
    
    Responsabilidades:
    - Criar checkout para upgrade
    - Processar callbacks de pagamento
    - Atualizar plano após pagamento
    - Downgrade ao cancelar
    - Verificar limites do plano
    """
    
    def __init__(self, db_session=None):
        self.mp_service = get_mercado_pago_service()
        self.db = db_session
    
    # ==================== CHECKOUT ====================
    
    async def create_checkout(
        self,
        user_id: str,
        user_email: str,
        target_tier: PlanTier,
        cycle: BillingCycle,
        current_tier: PlanTier = PlanTier.FREE,
    ) -> dict:
        """
        Cria checkout para upgrade/mudança de plano.
        
        Returns:
            {
                "checkout_url": str,  # URL para redirecionar usuário
                "preference_id": str,
                "plan": dict,
            }
        """
        # Valida se é upgrade válido
        if target_tier == PlanTier.FREE:
            raise ValueError("Não é possível fazer checkout para plano Free")
        
        if current_tier == target_tier:
            raise ValueError("Usuário já está neste plano")
        
        # Cria preferência de checkout no Mercado Pago
        checkout = await self.mp_service.create_checkout_preference(
            plan_tier=target_tier,
            cycle=cycle,
            user_id=user_id,
            user_email=user_email,
        )
        
        plan = get_plan(target_tier)
        
        return {
            "checkout_url": checkout.get("init_point"),
            "sandbox_url": checkout.get("sandbox_init_point"),
            "preference_id": checkout.get("preference_id"),
            "plan": {
                "tier": target_tier.value,
                "name": plan.name,
                "price": float(plan.price_monthly if cycle == BillingCycle.MONTHLY else plan.price_yearly),
                "cycle": cycle.value,
            }
        }
    
    # ==================== CALLBACKS ====================
    
    async def process_payment_callback(
        self,
        external_reference: str,
        payment_status: str,
        payment_id: str = None,
    ) -> dict:
        """
        Processa callback de pagamento (success/failure/pending).
        
        Args:
            external_reference: formato "user_id|plan_tier|cycle"
            payment_status: "approved", "pending", "rejected", etc.
            payment_id: ID do pagamento no MP
        """
        # Parse external reference
        parts = external_reference.split("|")
        if len(parts) != 3:
            raise ValueError(f"External reference inválido: {external_reference}")
        
        user_id, plan_tier_str, cycle_str = parts
        
        try:
            target_tier = PlanTier(plan_tier_str)
            cycle = BillingCycle(cycle_str)
        except ValueError as e:
            raise ValueError(f"Plano ou ciclo inválido: {e}")
        
        result = {
            "user_id": user_id,
            "target_tier": target_tier.value,
            "cycle": cycle.value,
            "payment_status": payment_status,
            "payment_id": payment_id,
            "action_taken": None,
        }
        
        if payment_status == "approved":
            # Atualiza plano do usuário
            await self.upgrade_user_plan(
                user_id=user_id,
                new_tier=target_tier,
                cycle=cycle,
                payment_id=payment_id,
            )
            result["action_taken"] = "plan_upgraded"
            
        elif payment_status == "pending":
            # Marca como pendente, aguarda webhook
            result["action_taken"] = "awaiting_confirmation"
            
        else:
            # Pagamento falhou
            result["action_taken"] = "payment_failed"
        
        logger.info(f"Payment callback processed: {result}")
        return result
    
    # ==================== PLAN MANAGEMENT ====================
    
    async def upgrade_user_plan(
        self,
        user_id: str,
        new_tier: PlanTier,
        cycle: BillingCycle,
        payment_id: str = None,
        subscription_id: str = None,
    ) -> dict:
        """
        Atualiza o plano do usuário para um tier superior.
        
        Deve ser chamado após confirmação de pagamento.
        """
        plan = get_plan(new_tier)
        
        # Calcula data de expiração
        if cycle == BillingCycle.MONTHLY:
            expires_at = datetime.utcnow() + timedelta(days=30)
        else:
            expires_at = datetime.utcnow() + timedelta(days=365)
        
        # Aqui você atualizaria o banco de dados
        # Exemplo com SQLAlchemy/Prisma:
        # 
        # user = await self.db.users.find_unique(where={"id": user_id})
        # org = await self.db.organizations.update(
        #     where={"id": user.organization_id},
        #     data={
        #         "plan": new_tier.value,
        #         "billing_cycle": cycle.value,
        #         "subscription_expires_at": expires_at,
        #         "mp_subscription_id": subscription_id,
        #         "mp_last_payment_id": payment_id,
        #     }
        # )
        
        logger.info(f"User {user_id} upgraded to {new_tier.value} ({cycle.value})")
        
        return {
            "user_id": user_id,
            "new_tier": new_tier.value,
            "cycle": cycle.value,
            "expires_at": expires_at.isoformat(),
            "features": {
                "analyses_per_month": plan.features.analyses_per_month,
                "agents_available": plan.features.agents_available,
                "export_formats": plan.features.export_formats,
                "api_access": plan.features.api_access,
            }
        }
    
    async def downgrade_user_plan(
        self,
        user_id: str,
        reason: str = "subscription_cancelled",
    ) -> dict:
        """
        Faz downgrade do usuário para o plano Free.
        
        Chamado quando:
        - Assinatura é cancelada
        - Pagamento falha após retentativas
        - Assinatura expira
        """
        free_plan = get_plan(PlanTier.FREE)
        
        # Aqui você atualizaria o banco de dados
        # Exemplo:
        # 
        # user = await self.db.users.find_unique(where={"id": user_id})
        # org = await self.db.organizations.update(
        #     where={"id": user.organization_id},
        #     data={
        #         "plan": PlanTier.FREE.value,
        #         "billing_cycle": None,
        #         "subscription_expires_at": None,
        #         "mp_subscription_id": None,
        #         "downgrade_reason": reason,
        #         "downgraded_at": datetime.utcnow(),
        #     }
        # )
        
        logger.info(f"User {user_id} downgraded to FREE. Reason: {reason}")
        
        return {
            "user_id": user_id,
            "new_tier": PlanTier.FREE.value,
            "reason": reason,
            "features": {
                "analyses_per_month": free_plan.features.analyses_per_month,
                "agents_available": free_plan.features.agents_available,
            }
        }
    
    # ==================== SUBSCRIPTION ACTIONS ====================
    
    async def cancel_subscription(
        self,
        user_id: str,
        mp_subscription_id: str,
        immediate: bool = False,
    ) -> dict:
        """
        Cancela a assinatura do usuário.
        
        Args:
            immediate: Se True, faz downgrade imediato.
                      Se False, mantém acesso até fim do período.
        """
        # Cancela no Mercado Pago
        if mp_subscription_id:
            await self.mp_service.cancel_subscription(mp_subscription_id)
        
        if immediate:
            await self.downgrade_user_plan(user_id, "user_cancelled_immediate")
        else:
            # Marca para downgrade no fim do período
            # await self.db.organizations.update(
            #     where={"id": org_id},
            #     data={"scheduled_downgrade": True}
            # )
            pass
        
        logger.info(f"Subscription cancelled for user {user_id}")
        
        return {
            "user_id": user_id,
            "cancelled": True,
            "immediate": immediate,
            "message": "Assinatura cancelada" + (" imediatamente" if immediate else " ao fim do período"),
        }
    
    async def pause_subscription(
        self,
        user_id: str,
        mp_subscription_id: str,
    ) -> dict:
        """Pausa temporariamente a assinatura"""
        if mp_subscription_id:
            await self.mp_service.pause_subscription(mp_subscription_id)
        
        return {
            "user_id": user_id,
            "status": SubscriptionStatus.PAUSED.value,
        }
    
    async def resume_subscription(
        self,
        user_id: str,
        mp_subscription_id: str,
    ) -> dict:
        """Retoma uma assinatura pausada"""
        if mp_subscription_id:
            await self.mp_service.resume_subscription(mp_subscription_id)
        
        return {
            "user_id": user_id,
            "status": SubscriptionStatus.ACTIVE.value,
        }
    
    # ==================== USAGE & LIMITS ====================
    
    async def check_usage_limits(
        self,
        user_id: str,
        current_tier: PlanTier,
        analyses_used: int,
    ) -> dict:
        """
        Verifica se usuário está dentro dos limites do plano.
        """
        plan = get_plan(current_tier)
        limit = plan.features.analyses_per_month
        
        # -1 significa ilimitado
        if limit == -1:
            return {
                "within_limits": True,
                "usage_percent": 0,
                "remaining": -1,
                "should_show_upgrade": False,
            }
        
        remaining = max(0, limit - analyses_used)
        usage_percent = (analyses_used / limit) * 100 if limit > 0 else 100
        
        return {
            "within_limits": analyses_used < limit,
            "usage_percent": min(usage_percent, 100),
            "used": analyses_used,
            "limit": limit,
            "remaining": remaining,
            "should_show_upgrade": usage_percent >= 80,
            "is_at_limit": analyses_used >= limit,
        }
    
    async def can_create_analysis(
        self,
        user_id: str,
        current_tier: PlanTier,
        analyses_used: int,
    ) -> bool:
        """Verifica se usuário pode criar nova análise"""
        usage = await self.check_usage_limits(user_id, current_tier, analyses_used)
        return usage["within_limits"]
    
    # ==================== WEBHOOK PROCESSING ====================
    
    async def process_webhook_event(self, webhook_data: dict) -> dict:
        """
        Processa eventos de webhook do Mercado Pago.
        
        Eventos tratados:
        - payment.created / payment.updated
        - subscription_preapproval (mudança de status)
        """
        processed = await self.mp_service.process_webhook(webhook_data)
        
        status = processed.get("status")
        external_ref = processed.get("external_reference")
        
        if not external_ref:
            return {"processed": False, "reason": "no_external_reference"}
        
        data_type = processed.get("type")
        
        if data_type == "payment":
            # Pagamento aprovado = upgrade
            if status == "approved":
                return await self.process_payment_callback(
                    external_reference=external_ref,
                    payment_status="approved",
                    payment_id=processed.get("data_id"),
                )
            elif status in ["rejected", "cancelled"]:
                return await self.process_payment_callback(
                    external_reference=external_ref,
                    payment_status="rejected",
                    payment_id=processed.get("data_id"),
                )
        
        elif data_type == "subscription_preapproval":
            subscription = processed.get("subscription", {})
            
            # Assinatura cancelada = downgrade
            if status == "cancelled":
                user_id = external_ref.split("|")[0] if "|" in external_ref else external_ref
                return await self.downgrade_user_plan(
                    user_id=user_id,
                    reason="subscription_cancelled_by_mp",
                )
            
            # Assinatura pausada
            elif status == "paused":
                pass  # Opcional: notificar usuário
        
        return processed


# Factory function
def get_subscription_service(db_session=None) -> SubscriptionService:
    """Cria instância do serviço de assinaturas"""
    return SubscriptionService(db_session=db_session)
