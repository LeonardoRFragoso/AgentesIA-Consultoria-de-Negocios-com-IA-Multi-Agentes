"""
Feature Exceptions - Erros claros para features bloqueadas
"""
from typing import Optional
from app.billing.plans import PlanTier
from app.features.flags import Feature


class FeatureError(Exception):
    """Base exception para erros de features"""
    
    def __init__(
        self,
        message: str,
        feature: Optional[Feature] = None,
        current_plan: Optional[PlanTier] = None,
        required_plan: Optional[PlanTier] = None,
        error_code: str = "FEATURE_ERROR",
    ):
        self.message = message
        self.feature = feature
        self.current_plan = current_plan
        self.required_plan = required_plan
        self.error_code = error_code
        super().__init__(self.message)
    
    def to_dict(self) -> dict:
        """Converte erro para dicionário (para API response)"""
        return {
            "error": True,
            "error_code": self.error_code,
            "message": self.message,
            "feature": self.feature.value if self.feature else None,
            "current_plan": self.current_plan.value if self.current_plan else None,
            "required_plan": self.required_plan.value if self.required_plan else None,
            "upgrade_required": self.required_plan is not None,
        }


class FeatureNotAvailableError(FeatureError):
    """
    Erro quando usuário tenta usar feature não disponível no plano.
    
    Exemplo:
        - Usuário Free tenta exportar DOCX
        - Usuário Pro tenta usar agentes customizados
    """
    
    def __init__(
        self,
        feature: Feature,
        current_plan: PlanTier,
        required_plan: PlanTier,
        custom_message: Optional[str] = None,
    ):
        feature_name = feature.value.replace("_", " ").title()
        
        message = custom_message or (
            f"A feature '{feature_name}' não está disponível no plano {current_plan.value.upper()}. "
            f"Faça upgrade para o plano {required_plan.value.upper()} para desbloquear."
        )
        
        super().__init__(
            message=message,
            feature=feature,
            current_plan=current_plan,
            required_plan=required_plan,
            error_code="FEATURE_NOT_AVAILABLE",
        )


class FeatureLimitExceededError(FeatureError):
    """
    Erro quando usuário excede o limite de uso de uma feature.
    
    Exemplo:
        - Usuário Free tenta criar 4ª análise (limite: 3)
        - Usuário Pro excede limite de API requests
    """
    
    def __init__(
        self,
        feature: Feature,
        current_plan: PlanTier,
        limit: int,
        current_usage: int,
        custom_message: Optional[str] = None,
    ):
        self.limit = limit
        self.current_usage = current_usage
        
        feature_name = feature.value.replace("_", " ").title()
        
        message = custom_message or (
            f"Você atingiu o limite de {limit} para '{feature_name}' no plano {current_plan.value.upper()}. "
            f"Uso atual: {current_usage}/{limit}. Faça upgrade para aumentar seu limite."
        )
        
        # Determina próximo plano
        plan_order = [PlanTier.FREE, PlanTier.PRO, PlanTier.ENTERPRISE]
        current_idx = plan_order.index(current_plan)
        next_plan = plan_order[current_idx + 1] if current_idx < len(plan_order) - 1 else None
        
        super().__init__(
            message=message,
            feature=feature,
            current_plan=current_plan,
            required_plan=next_plan,
            error_code="FEATURE_LIMIT_EXCEEDED",
        )
    
    def to_dict(self) -> dict:
        """Adiciona informações de limite ao dicionário"""
        result = super().to_dict()
        result.update({
            "limit": self.limit,
            "current_usage": self.current_usage,
            "remaining": max(0, self.limit - self.current_usage),
        })
        return result


class UpgradeRequiredError(FeatureError):
    """
    Erro genérico quando upgrade é necessário.
    
    Usado quando múltiplas features requerem upgrade ou
    quando a ação específica não se encaixa em uma feature.
    """
    
    def __init__(
        self,
        current_plan: PlanTier,
        required_plan: PlanTier,
        reason: str,
        features_needed: Optional[list[Feature]] = None,
    ):
        self.reason = reason
        self.features_needed = features_needed or []
        
        message = (
            f"{reason} "
            f"Seu plano atual é {current_plan.value.upper()}. "
            f"Faça upgrade para {required_plan.value.upper()} para continuar."
        )
        
        super().__init__(
            message=message,
            feature=features_needed[0] if features_needed else None,
            current_plan=current_plan,
            required_plan=required_plan,
            error_code="UPGRADE_REQUIRED",
        )
    
    def to_dict(self) -> dict:
        """Adiciona lista de features ao dicionário"""
        result = super().to_dict()
        result.update({
            "reason": self.reason,
            "features_needed": [f.value for f in self.features_needed],
        })
        return result


class PlanExpiredError(FeatureError):
    """
    Erro quando o plano do usuário expirou.
    """
    
    def __init__(
        self,
        expired_plan: PlanTier,
        expired_at: str,
    ):
        self.expired_at = expired_at
        
        message = (
            f"Seu plano {expired_plan.value.upper()} expirou em {expired_at}. "
            f"Renove sua assinatura para continuar usando os recursos premium."
        )
        
        super().__init__(
            message=message,
            current_plan=PlanTier.FREE,  # Volta para FREE quando expira
            required_plan=expired_plan,
            error_code="PLAN_EXPIRED",
        )
    
    def to_dict(self) -> dict:
        result = super().to_dict()
        result["expired_at"] = self.expired_at
        return result


# ============================================
# HTTP STATUS CODES MAPPING
# ============================================

ERROR_STATUS_CODES = {
    "FEATURE_NOT_AVAILABLE": 403,
    "FEATURE_LIMIT_EXCEEDED": 429,
    "UPGRADE_REQUIRED": 402,  # Payment Required
    "PLAN_EXPIRED": 402,
    "FEATURE_ERROR": 400,
}


def get_status_code_for_error(error: FeatureError) -> int:
    """Retorna o HTTP status code apropriado para o erro"""
    return ERROR_STATUS_CODES.get(error.error_code, 400)
