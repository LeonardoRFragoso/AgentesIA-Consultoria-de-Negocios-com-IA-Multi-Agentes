"""
Feature Routes - API endpoints para features
"""
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from ..billing.plans import PlanTier
from .flags import Feature, get_all_features_status
from .service import FeatureService, get_feature_service
from .middleware import (
    FeatureGate,
    get_feature_gate,
    require_feature,
    require_plan,
    check_usage_limit,
)
from .exceptions import FeatureError, get_status_code_for_error

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/features", tags=["features"])


# ==================== SCHEMAS ====================

class FeatureCheckRequest(BaseModel):
    feature: str


class FeatureCheckResponse(BaseModel):
    feature: str
    enabled: bool
    limit: Optional[int] = None
    current_usage: Optional[int] = None
    remaining: Optional[int] = None
    upgrade_message: Optional[str] = None


class FeatureListResponse(BaseModel):
    plan: str
    features: dict


# ==================== ROUTES ====================

@router.get("/")
async def list_all_features(
    gate: FeatureGate = Depends(get_feature_gate),
):
    """
    Lista todas as features e seu status para o plano atual.
    """
    return {
        "plan": gate.plan.value,
        "features": get_all_features_status(gate.plan),
    }


@router.get("/available")
async def list_available_features(
    gate: FeatureGate = Depends(get_feature_gate),
    service: FeatureService = Depends(get_feature_service),
):
    """
    Lista apenas features disponíveis no plano atual.
    """
    return {
        "plan": gate.plan.value,
        "features": service.get_available_features(gate.plan),
    }


@router.get("/locked")
async def list_locked_features(
    gate: FeatureGate = Depends(get_feature_gate),
    service: FeatureService = Depends(get_feature_service),
):
    """
    Lista features bloqueadas (requerem upgrade).
    """
    return {
        "plan": gate.plan.value,
        "locked_features": service.get_locked_features(gate.plan),
    }


@router.get("/check/{feature}")
async def check_feature(
    feature: str,
    gate: FeatureGate = Depends(get_feature_gate),
    service: FeatureService = Depends(get_feature_service),
):
    """
    Verifica se uma feature específica está disponível.
    """
    try:
        feature_enum = Feature(feature)
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Feature não encontrada: {feature}")
    
    # Obtém uso atual (mock - substituir por dados reais)
    usage_data = await service.get_usage(gate.user_id)
    current_usage = usage_data.get(feature, 0)
    
    info = service.get_feature_info(feature_enum, gate.plan, current_usage)
    return info


@router.post("/check")
async def check_feature_access(
    request: FeatureCheckRequest,
    gate: FeatureGate = Depends(get_feature_gate),
    service: FeatureService = Depends(get_feature_service),
):
    """
    Verifica acesso a uma feature (POST para maior segurança).
    Não levanta exceção, apenas retorna status.
    """
    try:
        feature_enum = Feature(request.feature)
    except ValueError:
        return {"feature": request.feature, "enabled": False, "error": "Feature não encontrada"}
    
    has_access = service.check_access(feature_enum, gate.plan, raise_exception=False)
    
    usage_data = await service.get_usage(gate.user_id)
    current_usage = usage_data.get(request.feature, 0)
    
    return service.get_feature_info(feature_enum, gate.plan, current_usage)


@router.get("/compare")
async def compare_plans(
    target_plan: str = Query(..., description="Plano alvo para comparação"),
    gate: FeatureGate = Depends(get_feature_gate),
    service: FeatureService = Depends(get_feature_service),
):
    """
    Compara features entre plano atual e plano alvo.
    Útil para mostrar benefícios de upgrade.
    """
    try:
        target = PlanTier(target_plan)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Plano inválido: {target_plan}")
    
    return service.compare_plans(gate.plan, target)


@router.get("/usage")
async def get_usage(
    gate: FeatureGate = Depends(get_feature_gate),
    service: FeatureService = Depends(get_feature_service),
):
    """
    Retorna uso atual de todas as features com limite.
    """
    usage_data = await service.get_usage(gate.user_id)
    
    result = {
        "plan": gate.plan.value,
        "usage": {},
    }
    
    for feature in Feature:
        info = service.get_feature_info(feature, gate.plan, usage_data.get(feature.value, 0))
        if info.get("limit") is not None:
            result["usage"][feature.value] = {
                "name": info["name"],
                "current": usage_data.get(feature.value, 0),
                "limit": info["limit"],
                "remaining": info.get("remaining"),
                "percent": info.get("usage_percent", 0),
            }
    
    return result


# ==================== EXEMPLO DE ROTAS PROTEGIDAS ====================

@router.get("/examples/pro-only")
@require_plan(PlanTier.PRO)
async def pro_only_endpoint(
    gate: FeatureGate = Depends(get_feature_gate),
):
    """
    Exemplo de endpoint que requer plano Pro ou superior.
    """
    return {
        "message": "Você tem acesso ao plano Pro!",
        "plan": gate.plan.value,
    }


@router.get("/examples/enterprise-only")
@require_plan(PlanTier.ENTERPRISE)
async def enterprise_only_endpoint(
    gate: FeatureGate = Depends(get_feature_gate),
):
    """
    Exemplo de endpoint que requer plano Enterprise.
    """
    return {
        "message": "Você tem acesso ao plano Enterprise!",
        "plan": gate.plan.value,
    }


@router.post("/examples/export-docx")
@require_feature(Feature.EXPORT_DOCX)
async def export_docx_example(
    gate: FeatureGate = Depends(get_feature_gate),
):
    """
    Exemplo de endpoint que requer feature específica (Export DOCX).
    """
    return {
        "message": "Exportação DOCX disponível!",
        "feature": "export_docx",
    }


@router.post("/examples/create-analysis")
@check_usage_limit(Feature.CREATE_ANALYSIS, usage_key="analyses_used")
async def create_analysis_example(
    gate: FeatureGate = Depends(get_feature_gate),
):
    """
    Exemplo de endpoint com verificação de limite de uso.
    """
    return {
        "message": "Análise criada com sucesso!",
        "remaining": gate.get_remaining(Feature.CREATE_ANALYSIS, "analyses_used"),
    }
