"""
Feature Middleware - Decorators e middleware para bloqueio de features
"""
import functools
import logging
from typing import Callable, Optional, Union, Any

from fastapi import Request, HTTPException, Depends
from fastapi.responses import JSONResponse

from ..billing.plans import PlanTier
from .flags import Feature, get_feature, is_feature_enabled, get_feature_limit, FEATURES
from .exceptions import (
    FeatureNotAvailableError,
    FeatureLimitExceededError,
    UpgradeRequiredError,
    FeatureError,
    get_status_code_for_error,
)

logger = logging.getLogger(__name__)


# ============================================
# DEPENDENCY INJECTION - GET USER PLAN
# ============================================

async def get_current_user_plan(request: Request) -> tuple[str, PlanTier, dict]:
    """
    Dependency para obter o plano do usuário atual.
    Retorna (user_id, plan_tier, usage_data)
    
    IMPORTANTE: Substitua pela sua lógica de autenticação real.
    """
    # TODO: Implementar autenticação real
    # Exemplo:
    # user = await get_current_user(request)
    # org = await get_organization(user.organization_id)
    # return user.id, PlanTier(org.plan), org.get_usage_data()
    
    # Mock para desenvolvimento
    return (
        "user_123",
        PlanTier.FREE,
        {
            "analyses_used": 2,
            "api_requests": 0,
            "team_members": 1,
        }
    )


# ============================================
# FEATURE GATE CLASS
# ============================================

class FeatureGate:
    """
    Classe para verificação de features.
    Pode ser usada como dependency injection ou diretamente.
    """
    
    def __init__(
        self,
        user_id: str,
        plan: PlanTier,
        usage_data: Optional[dict] = None,
    ):
        self.user_id = user_id
        self.plan = plan
        self.usage_data = usage_data or {}
    
    def check(self, feature: Union[Feature, str]) -> bool:
        """Verifica se feature está disponível (não levanta exceção)"""
        return is_feature_enabled(feature, self.plan)
    
    def require(self, feature: Union[Feature, str]) -> None:
        """Requer que feature esteja disponível (levanta exceção se não)"""
        flag = get_feature(feature)
        if flag is None:
            raise FeatureError(f"Feature desconhecida: {feature}")
        
        if not flag.is_available(self.plan):
            raise FeatureNotAvailableError(
                feature=flag.feature,
                current_plan=self.plan,
                required_plan=flag.min_plan_for_unlock,
                custom_message=flag.upgrade_message,
            )
    
    def check_limit(
        self,
        feature: Union[Feature, str],
        usage_key: Optional[str] = None,
        current_usage: Optional[int] = None,
    ) -> bool:
        """Verifica se está dentro do limite (não levanta exceção)"""
        flag = get_feature(feature)
        if flag is None:
            return False
        
        # Se não tem limite definido, está ok
        limit = flag.get_limit(self.plan)
        if limit is None:
            return True
        
        # Obtém uso atual
        if current_usage is None:
            key = usage_key or feature.value if isinstance(feature, Feature) else feature
            current_usage = self.usage_data.get(key, 0)
        
        return current_usage < limit
    
    def require_limit(
        self,
        feature: Union[Feature, str],
        usage_key: Optional[str] = None,
        current_usage: Optional[int] = None,
    ) -> None:
        """Requer que esteja dentro do limite (levanta exceção se não)"""
        flag = get_feature(feature)
        if flag is None:
            raise FeatureError(f"Feature desconhecida: {feature}")
        
        limit = flag.get_limit(self.plan)
        if limit is None:
            return  # Sem limite
        
        # Obtém uso atual
        if current_usage is None:
            key = usage_key or flag.feature.value
            current_usage = self.usage_data.get(key, 0)
        
        if current_usage >= limit:
            raise FeatureLimitExceededError(
                feature=flag.feature,
                current_plan=self.plan,
                limit=limit,
                current_usage=current_usage,
                custom_message=flag.upgrade_message,
            )
    
    def get_limit(self, feature: Union[Feature, str]) -> Optional[int]:
        """Retorna o limite da feature para o plano atual"""
        return get_feature_limit(feature, self.plan)
    
    def get_remaining(
        self,
        feature: Union[Feature, str],
        usage_key: Optional[str] = None,
    ) -> Optional[int]:
        """Retorna quantos usos restam da feature"""
        limit = self.get_limit(feature)
        if limit is None:
            return None  # Ilimitado
        
        key = usage_key or (feature.value if isinstance(feature, Feature) else feature)
        current_usage = self.usage_data.get(key, 0)
        return max(0, limit - current_usage)


# ============================================
# DEPENDENCY - GET FEATURE GATE
# ============================================

async def get_feature_gate(
    user_data: tuple = Depends(get_current_user_plan)
) -> FeatureGate:
    """Dependency que retorna um FeatureGate configurado"""
    user_id, plan, usage_data = user_data
    return FeatureGate(user_id=user_id, plan=plan, usage_data=usage_data)


# ============================================
# DECORATORS PARA ROTAS
# ============================================

def require_feature(feature: Union[Feature, str]):
    """
    Decorator para exigir uma feature em uma rota.
    
    Uso:
        @router.post("/export/docx")
        @require_feature(Feature.EXPORT_DOCX)
        async def export_docx(...):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Tenta obter o gate dos kwargs (injetado como dependency)
            gate: Optional[FeatureGate] = kwargs.get("gate")
            
            if gate is None:
                # Tenta obter do request
                request: Optional[Request] = kwargs.get("request")
                if request:
                    user_id, plan, usage = await get_current_user_plan(request)
                    gate = FeatureGate(user_id, plan, usage)
            
            if gate:
                try:
                    gate.require(feature)
                except FeatureError as e:
                    raise HTTPException(
                        status_code=get_status_code_for_error(e),
                        detail=e.to_dict(),
                    )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_plan(min_plan: PlanTier):
    """
    Decorator para exigir um plano mínimo.
    
    Uso:
        @router.get("/advanced-reports")
        @require_plan(PlanTier.PRO)
        async def get_advanced_reports(...):
            ...
    """
    plan_order = {PlanTier.FREE: 0, PlanTier.PRO: 1, PlanTier.ENTERPRISE: 2}
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            gate: Optional[FeatureGate] = kwargs.get("gate")
            
            if gate is None:
                request: Optional[Request] = kwargs.get("request")
                if request:
                    user_id, plan, usage = await get_current_user_plan(request)
                    gate = FeatureGate(user_id, plan, usage)
            
            if gate:
                current_level = plan_order.get(gate.plan, 0)
                required_level = plan_order.get(min_plan, 0)
                
                if current_level < required_level:
                    error = UpgradeRequiredError(
                        current_plan=gate.plan,
                        required_plan=min_plan,
                        reason=f"Esta funcionalidade requer o plano {min_plan.value.upper()} ou superior.",
                    )
                    raise HTTPException(
                        status_code=get_status_code_for_error(error),
                        detail=error.to_dict(),
                    )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def check_usage_limit(feature: Union[Feature, str], usage_key: Optional[str] = None):
    """
    Decorator para verificar limite de uso de uma feature.
    
    Uso:
        @router.post("/analyses")
        @check_usage_limit(Feature.CREATE_ANALYSIS, usage_key="analyses_used")
        async def create_analysis(...):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            gate: Optional[FeatureGate] = kwargs.get("gate")
            
            if gate is None:
                request: Optional[Request] = kwargs.get("request")
                if request:
                    user_id, plan, usage = await get_current_user_plan(request)
                    gate = FeatureGate(user_id, plan, usage)
            
            if gate:
                try:
                    gate.require_limit(feature, usage_key=usage_key)
                except FeatureError as e:
                    raise HTTPException(
                        status_code=get_status_code_for_error(e),
                        detail=e.to_dict(),
                    )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


# ============================================
# EXCEPTION HANDLER PARA FASTAPI
# ============================================

async def feature_exception_handler(request: Request, exc: FeatureError) -> JSONResponse:
    """
    Exception handler global para erros de feature.
    
    Registre no app FastAPI:
        app.add_exception_handler(FeatureError, feature_exception_handler)
    """
    return JSONResponse(
        status_code=get_status_code_for_error(exc),
        content=exc.to_dict(),
    )


# ============================================
# MIDDLEWARE FASTAPI
# ============================================

class FeatureMiddleware:
    """
    Middleware para adicionar feature gate ao request state.
    
    Uso:
        app.add_middleware(FeatureMiddleware)
    """
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            # Adiciona o feature gate ao scope para acesso posterior
            request = Request(scope, receive, send)
            
            try:
                user_id, plan, usage = await get_current_user_plan(request)
                scope["state"] = scope.get("state", {})
                scope["state"]["feature_gate"] = FeatureGate(user_id, plan, usage)
            except Exception as e:
                logger.warning(f"Could not create feature gate: {e}")
        
        await self.app(scope, receive, send)
