"""
Feature Service - Serviço centralizado para gerenciamento de features
"""
import logging
from typing import Optional, Union
from datetime import datetime

from app.billing.plans import PlanTier, get_plan
from app.features.flags import (
    Feature,
    FeatureFlag,
    FEATURES,
    get_feature,
    get_features_for_plan,
    is_feature_enabled,
    get_feature_limit,
    get_all_features_status,
)
from app.features.exceptions import (
    FeatureNotAvailableError,
    FeatureLimitExceededError,
    UpgradeRequiredError,
)

logger = logging.getLogger(__name__)


class FeatureService:
    """
    Serviço centralizado para gerenciamento de features.
    
    Integra com billing para verificar planos e limites.
    Pode ser usado tanto no backend quanto exposto via API.
    """
    
    def __init__(self, db_session=None):
        self.db = db_session
    
    # ==================== VERIFICAÇÕES ====================
    
    def is_enabled(
        self,
        feature: Union[Feature, str],
        plan: PlanTier,
    ) -> bool:
        """Verifica se feature está habilitada para o plano"""
        return is_feature_enabled(feature, plan)
    
    def check_access(
        self,
        feature: Union[Feature, str],
        plan: PlanTier,
        raise_exception: bool = True,
    ) -> bool:
        """
        Verifica acesso a uma feature.
        
        Args:
            feature: Feature a verificar
            plan: Plano do usuário
            raise_exception: Se True, levanta exceção se não tiver acesso
        
        Returns:
            True se tem acesso, False caso contrário
        
        Raises:
            FeatureNotAvailableError: Se não tem acesso e raise_exception=True
        """
        flag = get_feature(feature)
        if flag is None:
            if raise_exception:
                raise ValueError(f"Feature desconhecida: {feature}")
            return False
        
        has_access = flag.is_available(plan)
        
        if not has_access and raise_exception:
            raise FeatureNotAvailableError(
                feature=flag.feature,
                current_plan=plan,
                required_plan=flag.min_plan_for_unlock,
                custom_message=flag.upgrade_message,
            )
        
        return has_access
    
    def check_limit(
        self,
        feature: Union[Feature, str],
        plan: PlanTier,
        current_usage: int,
        raise_exception: bool = True,
    ) -> bool:
        """
        Verifica se está dentro do limite de uso.
        
        Args:
            feature: Feature a verificar
            plan: Plano do usuário
            current_usage: Uso atual
            raise_exception: Se True, levanta exceção se exceder limite
        
        Returns:
            True se dentro do limite, False caso contrário
        
        Raises:
            FeatureLimitExceededError: Se exceder limite e raise_exception=True
        """
        flag = get_feature(feature)
        if flag is None:
            return False
        
        limit = flag.get_limit(plan)
        
        # Sem limite definido = ilimitado
        if limit is None:
            return True
        
        within_limit = current_usage < limit
        
        if not within_limit and raise_exception:
            raise FeatureLimitExceededError(
                feature=flag.feature,
                current_plan=plan,
                limit=limit,
                current_usage=current_usage,
                custom_message=flag.upgrade_message,
            )
        
        return within_limit
    
    # ==================== INFORMAÇÕES ====================
    
    def get_feature_info(
        self,
        feature: Union[Feature, str],
        plan: PlanTier,
        current_usage: Optional[int] = None,
    ) -> dict:
        """
        Retorna informações completas sobre uma feature para o plano.
        """
        flag = get_feature(feature)
        if flag is None:
            return {"error": "Feature não encontrada"}
        
        limit = flag.get_limit(plan)
        is_available = flag.is_available(plan)
        
        result = {
            "feature": flag.feature.value,
            "name": flag.name,
            "description": flag.description,
            "enabled": is_available,
            "limit": limit,
            "is_unlimited": limit is None and is_available,
            "min_plan": flag.min_plan_for_unlock.value,
        }
        
        if current_usage is not None and limit is not None:
            result.update({
                "current_usage": current_usage,
                "remaining": max(0, limit - current_usage),
                "usage_percent": min(100, (current_usage / limit) * 100) if limit > 0 else 0,
                "is_at_limit": current_usage >= limit,
            })
        
        if not is_available:
            result["upgrade_message"] = flag.upgrade_message
        
        return result
    
    def get_all_features(self, plan: PlanTier) -> dict:
        """Retorna status de todas as features para um plano"""
        return get_all_features_status(plan)
    
    def get_available_features(self, plan: PlanTier) -> list[dict]:
        """Retorna lista de features disponíveis para o plano"""
        available = get_features_for_plan(plan)
        return [
            {
                "feature": f.feature.value,
                "name": f.name,
                "description": f.description,
                "limit": f.get_limit(plan),
            }
            for f in available
        ]
    
    def get_locked_features(self, plan: PlanTier) -> list[dict]:
        """Retorna lista de features bloqueadas para o plano"""
        all_features = list(FEATURES.values())
        available = get_features_for_plan(plan)
        locked = [f for f in all_features if f not in available]
        
        return [
            {
                "feature": f.feature.value,
                "name": f.name,
                "description": f.description,
                "min_plan": f.min_plan_for_unlock.value,
                "upgrade_message": f.upgrade_message,
            }
            for f in locked
        ]
    
    # ==================== COMPARAÇÃO DE PLANOS ====================
    
    def compare_plans(self, current_plan: PlanTier, target_plan: PlanTier) -> dict:
        """
        Compara features entre dois planos.
        Útil para mostrar o que o usuário ganha com upgrade.
        """
        current_features = set(f.feature for f in get_features_for_plan(current_plan))
        target_features = set(f.feature for f in get_features_for_plan(target_plan))
        
        # Features que ganha com upgrade
        new_features = target_features - current_features
        
        # Features com limites melhorados
        improved_limits = []
        for feature in current_features:
            flag = get_feature(feature)
            current_limit = flag.get_limit(current_plan)
            target_limit = flag.get_limit(target_plan)
            
            if current_limit is not None:
                if target_limit is None:
                    improved_limits.append({
                        "feature": feature.value,
                        "name": flag.name,
                        "current_limit": current_limit,
                        "new_limit": "Ilimitado",
                    })
                elif target_limit > current_limit:
                    improved_limits.append({
                        "feature": feature.value,
                        "name": flag.name,
                        "current_limit": current_limit,
                        "new_limit": target_limit,
                    })
        
        return {
            "current_plan": current_plan.value,
            "target_plan": target_plan.value,
            "new_features": [
                {
                    "feature": f.value,
                    "name": get_feature(f).name,
                    "description": get_feature(f).description,
                }
                for f in new_features
            ],
            "improved_limits": improved_limits,
            "total_new_features": len(new_features),
            "total_improved_limits": len(improved_limits),
        }
    
    # ==================== USAGE TRACKING ====================
    
    async def increment_usage(
        self,
        user_id: str,
        feature: Union[Feature, str],
        amount: int = 1,
    ) -> dict:
        """
        Incrementa uso de uma feature.
        Deve ser chamado após uso bem-sucedido da feature.
        
        Retorna novo estado de uso.
        """
        # TODO: Implementar persistência real
        # Exemplo:
        # await self.db.usage.upsert(
        #     where={"user_id_feature": {"user_id": user_id, "feature": feature.value}},
        #     update={"count": {"increment": amount}},
        #     create={"user_id": user_id, "feature": feature.value, "count": amount},
        # )
        
        logger.info(f"Usage incremented: user={user_id}, feature={feature}, amount={amount}")
        
        return {
            "user_id": user_id,
            "feature": feature.value if isinstance(feature, Feature) else feature,
            "incremented_by": amount,
        }
    
    async def get_usage(
        self,
        user_id: str,
        feature: Optional[Union[Feature, str]] = None,
    ) -> dict:
        """
        Retorna uso de features do usuário.
        Se feature não especificada, retorna todas.
        """
        # TODO: Implementar busca real do banco
        # Exemplo:
        # if feature:
        #     usage = await self.db.usage.find_first(
        #         where={"user_id": user_id, "feature": feature.value}
        #     )
        #     return {"feature": feature.value, "count": usage.count if usage else 0}
        # else:
        #     usages = await self.db.usage.find_many(where={"user_id": user_id})
        #     return {u.feature: u.count for u in usages}
        
        # Mock
        return {
            "analyses_used": 2,
            "api_requests": 0,
            "team_members": 1,
        }
    
    async def reset_monthly_usage(self, user_id: str) -> None:
        """
        Reseta uso mensal do usuário.
        Deve ser chamado no início de cada período de billing.
        """
        # TODO: Implementar reset real
        logger.info(f"Monthly usage reset for user={user_id}")


# Singleton
_feature_service: Optional[FeatureService] = None


def get_feature_service(db_session=None) -> FeatureService:
    """Retorna instância do serviço de features"""
    global _feature_service
    if _feature_service is None:
        _feature_service = FeatureService(db_session=db_session)
    return _feature_service
