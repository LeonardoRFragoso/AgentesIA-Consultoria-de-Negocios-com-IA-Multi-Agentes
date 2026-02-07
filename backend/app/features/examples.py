"""
Exemplos de Uso - Feature Flags System

Este arquivo demonstra como usar o sistema de feature flags em diferentes cenários.
"""
from fastapi import APIRouter, Depends, HTTPException

from ..billing.plans import PlanTier
from .flags import Feature, is_feature_enabled, get_feature_limit
from .exceptions import FeatureNotAvailableError, FeatureLimitExceededError
from .middleware import (
    FeatureGate,
    get_feature_gate,
    require_feature,
    require_plan,
    check_usage_limit,
)
from .service import FeatureService, get_feature_service

router = APIRouter(prefix="/examples", tags=["examples"])


# ============================================
# EXEMPLO 1: Verificação simples inline
# ============================================

@router.post("/analysis/export")
async def export_analysis(
    format: str,  # "pdf", "docx", "excel"
    gate: FeatureGate = Depends(get_feature_gate),
):
    """
    Exemplo de verificação inline de feature.
    Útil quando a verificação depende de parâmetros da request.
    """
    # Mapeia formato para feature
    format_features = {
        "pdf": Feature.EXPORT_PDF,
        "docx": Feature.EXPORT_DOCX,
        "excel": Feature.EXPORT_EXCEL,
    }
    
    feature = format_features.get(format)
    if not feature:
        raise HTTPException(status_code=400, detail="Formato inválido")
    
    # Verifica se tem acesso à feature
    if not gate.check(feature):
        config = gate.get_limit(feature)
        raise HTTPException(
            status_code=403,
            detail={
                "error": "feature_not_available",
                "message": f"Exportação em {format.upper()} requer upgrade",
                "required_plan": "pro" if format in ["docx", "excel"] else "enterprise",
            }
        )
    
    # Processa exportação...
    return {"status": "success", "format": format}


# ============================================
# EXEMPLO 2: Decorator @require_feature
# ============================================

@router.get("/reports/advanced")
@require_feature(Feature.ADVANCED_REPORTS)
async def get_advanced_reports(
    gate: FeatureGate = Depends(get_feature_gate),
):
    """
    Exemplo usando decorator @require_feature.
    Bloqueia toda a rota se a feature não estiver disponível.
    
    Se o usuário não tiver acesso, retorna automaticamente:
    {
        "error": true,
        "error_code": "FEATURE_NOT_AVAILABLE",
        "message": "Relatórios avançados disponíveis a partir do plano Pro.",
        "feature": "advanced_reports",
        "current_plan": "free",
        "required_plan": "pro",
        "upgrade_required": true
    }
    """
    return {
        "reports": [
            {"id": 1, "name": "Relatório Detalhado", "type": "advanced"},
            {"id": 2, "name": "Análise Profunda", "type": "advanced"},
        ]
    }


# ============================================
# EXEMPLO 3: Decorator @require_plan
# ============================================

@router.get("/api/keys")
@require_plan(PlanTier.PRO)
async def get_api_keys(
    gate: FeatureGate = Depends(get_feature_gate),
):
    """
    Exemplo usando decorator @require_plan.
    Bloqueia toda a rota se o plano for inferior ao requerido.
    """
    return {
        "keys": [
            {"id": "key_123", "name": "Production", "created_at": "2024-01-01"},
        ]
    }


# ============================================
# EXEMPLO 4: Verificação de limite de uso
# ============================================

@router.post("/analyses")
@check_usage_limit(Feature.CREATE_ANALYSIS, usage_key="analyses_used")
async def create_analysis(
    gate: FeatureGate = Depends(get_feature_gate),
    service: FeatureService = Depends(get_feature_service),
):
    """
    Exemplo com verificação de limite de uso.
    
    Se o usuário atingiu o limite, retorna:
    {
        "error": true,
        "error_code": "FEATURE_LIMIT_EXCEEDED",
        "message": "Você atingiu o limite de 3 para 'Create Analysis'...",
        "limit": 3,
        "current_usage": 3,
        "remaining": 0
    }
    """
    # Cria análise...
    
    # Incrementa uso após sucesso
    await service.increment_usage(gate.user_id, Feature.CREATE_ANALYSIS)
    
    remaining = gate.get_remaining(Feature.CREATE_ANALYSIS, "analyses_used")
    
    return {
        "id": "analysis_new",
        "status": "created",
        "remaining_this_month": remaining,
    }


# ============================================
# EXEMPLO 5: Verificação manual com try/except
# ============================================

@router.post("/team/invite")
async def invite_team_member(
    email: str,
    gate: FeatureGate = Depends(get_feature_gate),
):
    """
    Exemplo de verificação manual com tratamento de exceção.
    Útil quando você quer personalizar a resposta de erro.
    """
    try:
        # Verifica se pode adicionar mais membros
        gate.require(Feature.TEAM_MEMBERS)
        gate.require_limit(Feature.TEAM_MEMBERS, usage_key="team_members")
        
    except FeatureNotAvailableError as e:
        return {
            "success": False,
            "error": "upgrade_required",
            "message": "Adicionar membros à equipe requer upgrade.",
            "upgrade_url": "/billing?highlight=team_members",
        }
    
    except FeatureLimitExceededError as e:
        return {
            "success": False,
            "error": "limit_reached",
            "message": f"Você atingiu o limite de {e.limit} membros no seu plano.",
            "current": e.current_usage,
            "limit": e.limit,
            "upgrade_url": "/billing?highlight=team_members",
        }
    
    # Convida membro...
    return {
        "success": True,
        "message": f"Convite enviado para {email}",
    }


# ============================================
# EXEMPLO 6: Múltiplas features
# ============================================

@router.post("/reports/schedule")
async def schedule_report(
    report_id: str,
    schedule: str,
    gate: FeatureGate = Depends(get_feature_gate),
):
    """
    Exemplo verificando múltiplas features.
    """
    # Precisa de relatórios avançados E agendamento
    required_features = [
        Feature.ADVANCED_REPORTS,
        Feature.SCHEDULED_REPORTS,
    ]
    
    missing_features = []
    for feature in required_features:
        if not gate.check(feature):
            missing_features.append(feature.value)
    
    if missing_features:
        return {
            "success": False,
            "error": "features_required",
            "missing_features": missing_features,
            "message": "Esta funcionalidade requer recursos premium.",
            "upgrade_url": "/billing",
        }
    
    # Agenda relatório...
    return {
        "success": True,
        "report_id": report_id,
        "schedule": schedule,
    }


# ============================================
# EXEMPLO 7: Feature flags em lógica de negócio
# ============================================

class AnalysisService:
    """Exemplo de uso de feature flags em serviço de negócio."""
    
    def __init__(self, gate: FeatureGate):
        self.gate = gate
    
    def get_available_agents(self) -> list[str]:
        """Retorna agentes disponíveis baseado no plano."""
        agents = []
        
        # Agentes básicos (todos os planos)
        if self.gate.check(Feature.AGENT_MARKET):
            agents.append("market")
        if self.gate.check(Feature.AGENT_FINANCIAL):
            agents.append("financial")
        if self.gate.check(Feature.AGENT_MARKETING):
            agents.append("marketing")
        
        # Agentes Pro
        if self.gate.check(Feature.AGENT_RISK):
            agents.append("risk")
        if self.gate.check(Feature.AGENT_PLANNING):
            agents.append("planning")
        
        # Agentes Enterprise
        if self.gate.check(Feature.CUSTOM_AGENTS):
            agents.append("custom")
        
        return agents
    
    def get_export_formats(self) -> list[str]:
        """Retorna formatos de exportação disponíveis."""
        formats = []
        
        if self.gate.check(Feature.EXPORT_PDF):
            formats.append("pdf")
        if self.gate.check(Feature.EXPORT_DOCX):
            formats.append("docx")
        if self.gate.check(Feature.EXPORT_EXCEL):
            formats.append("excel")
        if self.gate.check(Feature.EXPORT_API):
            formats.append("api")
        
        return formats


@router.get("/analysis/config")
async def get_analysis_config(
    gate: FeatureGate = Depends(get_feature_gate),
):
    """
    Endpoint que retorna configuração baseada no plano.
    Útil para o frontend saber o que mostrar/esconder.
    """
    service = AnalysisService(gate)
    
    return {
        "plan": gate.plan.value,
        "available_agents": service.get_available_agents(),
        "export_formats": service.get_export_formats(),
        "limits": {
            "analyses_per_month": gate.get_limit(Feature.CREATE_ANALYSIS),
            "team_members": gate.get_limit(Feature.TEAM_MEMBERS),
            "api_requests": gate.get_limit(Feature.API_ACCESS),
            "history_items": gate.get_limit(Feature.ANALYSIS_HISTORY),
        },
        "features": {
            "advanced_reports": gate.check(Feature.ADVANCED_REPORTS),
            "scheduled_reports": gate.check(Feature.SCHEDULED_REPORTS),
            "white_label": gate.check(Feature.WHITE_LABEL),
            "shared_analyses": gate.check(Feature.SHARED_ANALYSES),
            "comments": gate.check(Feature.COMMENTS),
        }
    }


# ============================================
# EXEMPLO 8: Soft blocking (mostrar mas desabilitar)
# ============================================

@router.get("/analysis/{id}")
async def get_analysis(
    id: str,
    gate: FeatureGate = Depends(get_feature_gate),
):
    """
    Exemplo de soft blocking - retorna dados mas indica features bloqueadas.
    O frontend pode mostrar elementos desabilitados com CTA de upgrade.
    """
    # Busca análise...
    analysis = {
        "id": id,
        "title": "Análise de Mercado",
        "content": "...",
    }
    
    # Adiciona informações de features disponíveis
    analysis["available_actions"] = {
        "export_pdf": {
            "enabled": gate.check(Feature.EXPORT_PDF),
            "min_plan": "free",
        },
        "export_docx": {
            "enabled": gate.check(Feature.EXPORT_DOCX),
            "min_plan": "pro",
        },
        "export_excel": {
            "enabled": gate.check(Feature.EXPORT_EXCEL),
            "min_plan": "pro",
        },
        "share": {
            "enabled": gate.check(Feature.SHARED_ANALYSES),
            "min_plan": "pro",
        },
        "comment": {
            "enabled": gate.check(Feature.COMMENTS),
            "min_plan": "pro",
        },
    }
    
    return analysis
