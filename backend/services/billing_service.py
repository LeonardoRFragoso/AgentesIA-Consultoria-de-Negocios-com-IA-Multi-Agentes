"""
Billing service - Controle de planos, limites e uso.
"""

from datetime import datetime, timedelta
from typing import Optional, Tuple
from uuid import UUID
from sqlalchemy.orm import Session

from database.models import Organization, PlanType, Analysis


class BillingService:
    """
    Serviço de billing e controle de uso.
    
    Responsabilidades:
    - Verificar limites de plano
    - Registrar uso
    - Integrar com Stripe (futuro)
    """
    
    # Limites por plano
    # Agentes disponíveis
    ALL_AGENTS = ["analyst", "commercial", "financial", "market", "reviewer"]
    
    PLAN_LIMITS = {
        PlanType.FREE: {
            "executions_per_month": 5,
            "tokens_per_day": None,  # Sem limite diário
            "users": 1,
            "history_days": 7,
            "exports": False,
            "max_agents": 2,  # Usuário escolhe 2 agentes
            "agents_allowed": ALL_AGENTS,  # Pode escolher qualquer um
        },
        PlanType.PRO: {
            "executions_per_month": 50,
            "tokens_per_day": 100000,
            "users": 5,
            "history_days": 90,
            "exports": True,
            "max_agents": 5,  # Todos os agentes
            "agents_allowed": ALL_AGENTS,
        },
        PlanType.ENTERPRISE: {
            "executions_per_month": None,  # Ilimitado
            "tokens_per_day": None,
            "users": 999,
            "history_days": 365,
            "exports": True,
            "max_agents": 5,
            "agents_allowed": ALL_AGENTS,
        },
    }
    
    def __init__(self, db: Session):
        self.db = db
    
    def check_can_execute(self, org_id: UUID) -> Tuple[bool, Optional[str]]:
        """
        Verifica se organização pode executar análise.
        
        Returns:
            Tuple[bool, Optional[str]]: (pode_executar, mensagem_erro)
        """
        org = self.db.query(Organization).filter(Organization.id == org_id).first()
        
        if not org:
            return False, "Organização não encontrada"
        
        if not org.is_active:
            return False, "Organização inativa. Entre em contato com suporte."
        
        limits = self.PLAN_LIMITS.get(org.plan, self.PLAN_LIMITS[PlanType.FREE])
        
        # Verifica limite de execuções mensais
        if limits["executions_per_month"]:
            if org.executions_this_month >= limits["executions_per_month"]:
                return False, f"Limite de {limits['executions_per_month']} análises/mês atingido. Faça upgrade para Pro."
        
        # Verifica limite de tokens diários
        if limits["tokens_per_day"]:
            # Reset diário
            if org.tokens_reset_at.date() < datetime.utcnow().date():
                org.tokens_used_today = 0
                org.tokens_reset_at = datetime.utcnow()
                self.db.commit()
            
            if org.tokens_used_today >= limits["tokens_per_day"]:
                return False, "Limite diário de tokens atingido. Tente novamente amanhã."
        
        return True, None
    
    def validate_agents(self, org_id: UUID, selected_agents: list) -> Tuple[bool, Optional[str], list]:
        """
        Valida seleção de agentes baseado no plano.
        
        Returns:
            Tuple[bool, Optional[str], list]: (válido, mensagem_erro, agentes_a_usar)
        """
        org = self.db.query(Organization).filter(Organization.id == org_id).first()
        
        if not org:
            return False, "Organização não encontrada", []
        
        limits = self.PLAN_LIMITS.get(org.plan, self.PLAN_LIMITS[PlanType.FREE])
        max_agents = limits.get("max_agents", 2)
        allowed_agents = limits.get("agents_allowed", self.ALL_AGENTS)
        
        # Se plano permite todos os agentes, usa todos
        if max_agents >= 5:
            return True, None, self.ALL_AGENTS
        
        # Valida que agentes selecionados existem
        invalid_agents = [a for a in selected_agents if a not in allowed_agents]
        if invalid_agents:
            return False, f"Agentes inválidos: {invalid_agents}", []
        
        # Valida quantidade de agentes
        if len(selected_agents) > max_agents:
            return False, f"Plano Free permite no máximo {max_agents} agentes. Faça upgrade para Pro.", []
        
        if len(selected_agents) < 1:
            return False, "Selecione pelo menos 1 agente.", []
        
        # Sempre inclui reviewer para gerar resumo executivo
        agents_to_use = list(selected_agents)
        if "reviewer" not in agents_to_use:
            agents_to_use.append("reviewer")
        
        return True, None, agents_to_use
    
    def get_agent_limits(self, org_id: UUID) -> dict:
        """Retorna limites de agentes para o plano da organização."""
        org = self.db.query(Organization).filter(Organization.id == org_id).first()
        
        if not org:
            return {"max_agents": 2, "agents_allowed": self.ALL_AGENTS}
        
        limits = self.PLAN_LIMITS.get(org.plan, self.PLAN_LIMITS[PlanType.FREE])
        return {
            "max_agents": limits.get("max_agents", 2),
            "agents_allowed": limits.get("agents_allowed", self.ALL_AGENTS),
            "plan": org.plan.value
        }
    
    def check_can_export(self, org_id: UUID) -> Tuple[bool, Optional[str]]:
        """Verifica se organização pode exportar análises."""
        org = self.db.query(Organization).filter(Organization.id == org_id).first()
        
        if not org:
            return False, "Organização não encontrada"
        
        limits = self.PLAN_LIMITS.get(org.plan, self.PLAN_LIMITS[PlanType.FREE])
        
        if not limits["exports"]:
            return False, "Exportação disponível apenas nos planos Pro e Enterprise."
        
        return True, None
    
    def record_execution(
        self,
        org_id: UUID,
        tokens_used: int,
        cost_usd: float = 0.0
    ) -> None:
        """
        Registra execução para billing.
        
        Args:
            org_id: ID da organização
            tokens_used: Tokens consumidos
            cost_usd: Custo em USD
        """
        org = self.db.query(Organization).filter(Organization.id == org_id).first()
        
        if not org:
            return
        
        org.executions_this_month += 1
        org.tokens_used_today += tokens_used
        
        self.db.commit()
    
    def get_usage_stats(self, org_id: UUID) -> dict:
        """Retorna estatísticas de uso da organização."""
        org = self.db.query(Organization).filter(Organization.id == org_id).first()
        
        if not org:
            return {}
        
        limits = self.PLAN_LIMITS.get(org.plan, self.PLAN_LIMITS[PlanType.FREE])
        
        # Conta análises do mês
        start_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0)
        analyses_count = self.db.query(Analysis).filter(
            Analysis.org_id == org_id,
            Analysis.created_at >= start_of_month
        ).count()
        
        return {
            "plan": org.plan.value,
            "executions_this_month": org.executions_this_month,
            "executions_limit": limits["executions_per_month"],
            "tokens_used_today": org.tokens_used_today,
            "tokens_limit_today": limits["tokens_per_day"],
            "exports_enabled": limits["exports"],
            "history_days": limits["history_days"],
            "users_limit": limits["users"],
        }
    
    def reset_monthly_usage(self) -> int:
        """
        Reseta contadores mensais.
        Deve ser chamado por um job no início de cada mês.
        
        Returns:
            Número de organizações resetadas
        """
        count = self.db.query(Organization).update({"executions_this_month": 0})
        self.db.commit()
        return count
    
    def upgrade_plan(self, org_id: UUID, new_plan: PlanType) -> Organization:
        """
        Atualiza plano da organização.
        
        Em produção, isso seria chamado pelo webhook do Stripe.
        """
        org = self.db.query(Organization).filter(Organization.id == org_id).first()
        
        if not org:
            raise ValueError("Organização não encontrada")
        
        org.plan = new_plan
        self.db.commit()
        
        return org
    
    def downgrade_to_free(self, org_id: UUID) -> Organization:
        """
        Downgrades organização para plano free.
        Chamado quando assinatura é cancelada.
        """
        return self.upgrade_plan(org_id, PlanType.FREE)
