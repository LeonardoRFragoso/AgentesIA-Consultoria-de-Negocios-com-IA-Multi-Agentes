"""
Feature Flags - Definição centralizada de features por plano
"""
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Union

from app.billing.plans import PlanTier


class Feature(str, Enum):
    """Enum de todas as features do sistema"""
    
    # Análises
    CREATE_ANALYSIS = "create_analysis"
    EXPORT_PDF = "export_pdf"
    EXPORT_DOCX = "export_docx"
    EXPORT_EXCEL = "export_excel"
    EXPORT_API = "export_api"
    
    # Agentes IA
    AGENT_MARKET = "agent_market"
    AGENT_FINANCIAL = "agent_financial"
    AGENT_MARKETING = "agent_marketing"
    AGENT_RISK = "agent_risk"
    AGENT_PLANNING = "agent_planning"
    CUSTOM_AGENTS = "custom_agents"
    
    # API & Integrações
    API_ACCESS = "api_access"
    WEBHOOKS = "webhooks"
    INTEGRATIONS = "integrations"
    
    # Relatórios
    ADVANCED_REPORTS = "advanced_reports"
    SCHEDULED_REPORTS = "scheduled_reports"
    WHITE_LABEL = "white_label"
    
    # Suporte
    PRIORITY_SUPPORT = "priority_support"
    DEDICATED_SUPPORT = "dedicated_support"
    SLA_GUARANTEE = "sla_guarantee"
    
    # Colaboração
    TEAM_MEMBERS = "team_members"
    SHARED_ANALYSES = "shared_analyses"
    COMMENTS = "comments"
    
    # Histórico
    ANALYSIS_HISTORY = "analysis_history"
    UNLIMITED_HISTORY = "unlimited_history"


@dataclass
class FeatureFlag:
    """Configuração de uma feature flag"""
    feature: Feature
    name: str
    description: str
    
    # Planos que têm acesso
    available_in: list[PlanTier]
    
    # Limites por plano (None = ilimitado, 0 = não disponível)
    limits: dict[PlanTier, Optional[int]] = field(default_factory=dict)
    
    # Feature em beta?
    is_beta: bool = False
    
    # Mensagem de upgrade
    upgrade_message: str = "Faça upgrade para desbloquear esta feature"
    
    # Plano mínimo recomendado
    min_plan_for_unlock: PlanTier = PlanTier.PRO
    
    def is_available(self, plan: PlanTier) -> bool:
        """Verifica se a feature está disponível no plano"""
        return plan in self.available_in
    
    def get_limit(self, plan: PlanTier) -> Optional[int]:
        """Retorna o limite da feature para o plano (None = ilimitado)"""
        return self.limits.get(plan)
    
    def check_limit(self, plan: PlanTier, current_usage: int) -> bool:
        """Verifica se está dentro do limite"""
        limit = self.get_limit(plan)
        if limit is None:
            return True  # Ilimitado
        return current_usage < limit


# ============================================
# DEFINIÇÃO DE TODAS AS FEATURES
# ============================================

FEATURES: dict[Feature, FeatureFlag] = {
    # === ANÁLISES ===
    Feature.CREATE_ANALYSIS: FeatureFlag(
        feature=Feature.CREATE_ANALYSIS,
        name="Criar Análises",
        description="Criar novas análises de negócio com IA",
        available_in=[PlanTier.FREE, PlanTier.PRO, PlanTier.ENTERPRISE],
        limits={
            PlanTier.FREE: 3,
            PlanTier.PRO: 50,
            PlanTier.ENTERPRISE: None,  # Ilimitado
        },
        upgrade_message="Você atingiu o limite de análises. Faça upgrade para criar mais.",
    ),
    
    Feature.EXPORT_PDF: FeatureFlag(
        feature=Feature.EXPORT_PDF,
        name="Exportar PDF",
        description="Exportar análises em formato PDF",
        available_in=[PlanTier.FREE, PlanTier.PRO, PlanTier.ENTERPRISE],
    ),
    
    Feature.EXPORT_DOCX: FeatureFlag(
        feature=Feature.EXPORT_DOCX,
        name="Exportar Word",
        description="Exportar análises em formato DOCX",
        available_in=[PlanTier.PRO, PlanTier.ENTERPRISE],
        upgrade_message="Exportação em Word disponível a partir do plano Pro.",
        min_plan_for_unlock=PlanTier.PRO,
    ),
    
    Feature.EXPORT_EXCEL: FeatureFlag(
        feature=Feature.EXPORT_EXCEL,
        name="Exportar Excel",
        description="Exportar dados em formato Excel",
        available_in=[PlanTier.PRO, PlanTier.ENTERPRISE],
        upgrade_message="Exportação em Excel disponível a partir do plano Pro.",
        min_plan_for_unlock=PlanTier.PRO,
    ),
    
    Feature.EXPORT_API: FeatureFlag(
        feature=Feature.EXPORT_API,
        name="Exportar via API",
        description="Exportar dados programaticamente via API",
        available_in=[PlanTier.ENTERPRISE],
        upgrade_message="Exportação via API disponível no plano Enterprise.",
        min_plan_for_unlock=PlanTier.ENTERPRISE,
    ),
    
    # === AGENTES IA ===
    Feature.AGENT_MARKET: FeatureFlag(
        feature=Feature.AGENT_MARKET,
        name="Agente de Mercado",
        description="Análise de mercado e competidores",
        available_in=[PlanTier.FREE, PlanTier.PRO, PlanTier.ENTERPRISE],
    ),
    
    Feature.AGENT_FINANCIAL: FeatureFlag(
        feature=Feature.AGENT_FINANCIAL,
        name="Agente Financeiro",
        description="Análise financeira e projeções",
        available_in=[PlanTier.FREE, PlanTier.PRO, PlanTier.ENTERPRISE],
    ),
    
    Feature.AGENT_MARKETING: FeatureFlag(
        feature=Feature.AGENT_MARKETING,
        name="Agente de Marketing",
        description="Estratégias e análise de marketing",
        available_in=[PlanTier.FREE, PlanTier.PRO, PlanTier.ENTERPRISE],
    ),
    
    Feature.AGENT_RISK: FeatureFlag(
        feature=Feature.AGENT_RISK,
        name="Agente de Riscos",
        description="Análise e mitigação de riscos",
        available_in=[PlanTier.PRO, PlanTier.ENTERPRISE],
        upgrade_message="Agente de Riscos disponível a partir do plano Pro.",
        min_plan_for_unlock=PlanTier.PRO,
    ),
    
    Feature.AGENT_PLANNING: FeatureFlag(
        feature=Feature.AGENT_PLANNING,
        name="Agente de Planejamento",
        description="Planejamento estratégico e roadmap",
        available_in=[PlanTier.PRO, PlanTier.ENTERPRISE],
        upgrade_message="Agente de Planejamento disponível a partir do plano Pro.",
        min_plan_for_unlock=PlanTier.PRO,
    ),
    
    Feature.CUSTOM_AGENTS: FeatureFlag(
        feature=Feature.CUSTOM_AGENTS,
        name="Agentes Customizados",
        description="Criar agentes personalizados para sua empresa",
        available_in=[PlanTier.ENTERPRISE],
        upgrade_message="Agentes customizados disponíveis no plano Enterprise.",
        min_plan_for_unlock=PlanTier.ENTERPRISE,
    ),
    
    # === API & INTEGRAÇÕES ===
    Feature.API_ACCESS: FeatureFlag(
        feature=Feature.API_ACCESS,
        name="Acesso à API",
        description="Acesso programático via REST API",
        available_in=[PlanTier.PRO, PlanTier.ENTERPRISE],
        limits={
            PlanTier.PRO: 1000,  # requests/mês
            PlanTier.ENTERPRISE: None,
        },
        upgrade_message="Acesso à API disponível a partir do plano Pro.",
        min_plan_for_unlock=PlanTier.PRO,
    ),
    
    Feature.WEBHOOKS: FeatureFlag(
        feature=Feature.WEBHOOKS,
        name="Webhooks",
        description="Receber notificações em tempo real",
        available_in=[PlanTier.PRO, PlanTier.ENTERPRISE],
        limits={
            PlanTier.PRO: 5,  # endpoints
            PlanTier.ENTERPRISE: None,
        },
        upgrade_message="Webhooks disponíveis a partir do plano Pro.",
        min_plan_for_unlock=PlanTier.PRO,
    ),
    
    Feature.INTEGRATIONS: FeatureFlag(
        feature=Feature.INTEGRATIONS,
        name="Integrações",
        description="Integrar com ferramentas externas",
        available_in=[PlanTier.ENTERPRISE],
        upgrade_message="Integrações customizadas disponíveis no plano Enterprise.",
        min_plan_for_unlock=PlanTier.ENTERPRISE,
    ),
    
    # === RELATÓRIOS ===
    Feature.ADVANCED_REPORTS: FeatureFlag(
        feature=Feature.ADVANCED_REPORTS,
        name="Relatórios Avançados",
        description="Relatórios detalhados com gráficos e métricas",
        available_in=[PlanTier.PRO, PlanTier.ENTERPRISE],
        upgrade_message="Relatórios avançados disponíveis a partir do plano Pro.",
        min_plan_for_unlock=PlanTier.PRO,
    ),
    
    Feature.SCHEDULED_REPORTS: FeatureFlag(
        feature=Feature.SCHEDULED_REPORTS,
        name="Relatórios Agendados",
        description="Agendar envio automático de relatórios",
        available_in=[PlanTier.ENTERPRISE],
        upgrade_message="Relatórios agendados disponíveis no plano Enterprise.",
        min_plan_for_unlock=PlanTier.ENTERPRISE,
    ),
    
    Feature.WHITE_LABEL: FeatureFlag(
        feature=Feature.WHITE_LABEL,
        name="White Label",
        description="Relatórios com sua marca",
        available_in=[PlanTier.ENTERPRISE],
        upgrade_message="White label disponível no plano Enterprise.",
        min_plan_for_unlock=PlanTier.ENTERPRISE,
    ),
    
    # === SUPORTE ===
    Feature.PRIORITY_SUPPORT: FeatureFlag(
        feature=Feature.PRIORITY_SUPPORT,
        name="Suporte Prioritário",
        description="Atendimento prioritário por email",
        available_in=[PlanTier.PRO, PlanTier.ENTERPRISE],
        min_plan_for_unlock=PlanTier.PRO,
    ),
    
    Feature.DEDICATED_SUPPORT: FeatureFlag(
        feature=Feature.DEDICATED_SUPPORT,
        name="Suporte Dedicado",
        description="Gerente de conta dedicado",
        available_in=[PlanTier.ENTERPRISE],
        min_plan_for_unlock=PlanTier.ENTERPRISE,
    ),
    
    Feature.SLA_GUARANTEE: FeatureFlag(
        feature=Feature.SLA_GUARANTEE,
        name="SLA Garantido",
        description="Garantia de tempo de resposta",
        available_in=[PlanTier.ENTERPRISE],
        min_plan_for_unlock=PlanTier.ENTERPRISE,
    ),
    
    # === COLABORAÇÃO ===
    Feature.TEAM_MEMBERS: FeatureFlag(
        feature=Feature.TEAM_MEMBERS,
        name="Membros da Equipe",
        description="Adicionar membros à sua organização",
        available_in=[PlanTier.FREE, PlanTier.PRO, PlanTier.ENTERPRISE],
        limits={
            PlanTier.FREE: 1,
            PlanTier.PRO: 5,
            PlanTier.ENTERPRISE: None,
        },
        upgrade_message="Adicione mais membros fazendo upgrade do seu plano.",
    ),
    
    Feature.SHARED_ANALYSES: FeatureFlag(
        feature=Feature.SHARED_ANALYSES,
        name="Análises Compartilhadas",
        description="Compartilhar análises com a equipe",
        available_in=[PlanTier.PRO, PlanTier.ENTERPRISE],
        upgrade_message="Compartilhamento de análises disponível a partir do plano Pro.",
        min_plan_for_unlock=PlanTier.PRO,
    ),
    
    Feature.COMMENTS: FeatureFlag(
        feature=Feature.COMMENTS,
        name="Comentários",
        description="Adicionar comentários em análises",
        available_in=[PlanTier.PRO, PlanTier.ENTERPRISE],
        upgrade_message="Comentários disponíveis a partir do plano Pro.",
        min_plan_for_unlock=PlanTier.PRO,
    ),
    
    # === HISTÓRICO ===
    Feature.ANALYSIS_HISTORY: FeatureFlag(
        feature=Feature.ANALYSIS_HISTORY,
        name="Histórico de Análises",
        description="Acessar análises anteriores",
        available_in=[PlanTier.FREE, PlanTier.PRO, PlanTier.ENTERPRISE],
        limits={
            PlanTier.FREE: 10,  # últimas 10
            PlanTier.PRO: 100,
            PlanTier.ENTERPRISE: None,
        },
        upgrade_message="Acesse mais histórico fazendo upgrade.",
    ),
    
    Feature.UNLIMITED_HISTORY: FeatureFlag(
        feature=Feature.UNLIMITED_HISTORY,
        name="Histórico Ilimitado",
        description="Acesso a todo histórico de análises",
        available_in=[PlanTier.ENTERPRISE],
        upgrade_message="Histórico ilimitado disponível no plano Enterprise.",
        min_plan_for_unlock=PlanTier.ENTERPRISE,
    ),
}


# ============================================
# FUNÇÕES AUXILIARES
# ============================================

def get_feature(feature: Union[Feature, str]) -> Optional[FeatureFlag]:
    """Retorna a configuração de uma feature"""
    if isinstance(feature, str):
        try:
            feature = Feature(feature)
        except ValueError:
            return None
    return FEATURES.get(feature)


def get_features_for_plan(plan: PlanTier) -> list[FeatureFlag]:
    """Retorna todas as features disponíveis para um plano"""
    return [f for f in FEATURES.values() if f.is_available(plan)]


def is_feature_enabled(feature: Union[Feature, str], plan: PlanTier) -> bool:
    """Verifica se uma feature está habilitada para o plano"""
    flag = get_feature(feature)
    if flag is None:
        return False
    return flag.is_available(plan)


def get_feature_limit(feature: Union[Feature, str], plan: PlanTier) -> Optional[int]:
    """Retorna o limite de uma feature para o plano"""
    flag = get_feature(feature)
    if flag is None:
        return 0
    return flag.get_limit(plan)


def get_all_features_status(plan: PlanTier) -> dict[str, dict]:
    """Retorna status de todas as features para um plano"""
    result = {}
    for feature, flag in FEATURES.items():
        result[feature.value] = {
            "name": flag.name,
            "description": flag.description,
            "enabled": flag.is_available(plan),
            "limit": flag.get_limit(plan),
            "upgrade_message": flag.upgrade_message if not flag.is_available(plan) else None,
            "min_plan": flag.min_plan_for_unlock.value,
        }
    return result
