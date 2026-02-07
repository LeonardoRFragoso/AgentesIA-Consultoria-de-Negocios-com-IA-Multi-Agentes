"""
Feature Flags Module - Controle de features por plano
"""
from .flags import (
    Feature,
    FeatureFlag,
    FEATURES,
    get_feature,
    get_features_for_plan,
    is_feature_enabled,
    get_feature_limit,
)
from .exceptions import (
    FeatureNotAvailableError,
    FeatureLimitExceededError,
    UpgradeRequiredError,
)
from .middleware import (
    require_feature,
    require_plan,
    check_usage_limit,
    FeatureGate,
)
from .service import FeatureService, get_feature_service

__all__ = [
    # Flags
    "Feature",
    "FeatureFlag", 
    "FEATURES",
    "get_feature",
    "get_features_for_plan",
    "is_feature_enabled",
    "get_feature_limit",
    # Exceptions
    "FeatureNotAvailableError",
    "FeatureLimitExceededError",
    "UpgradeRequiredError",
    # Middleware
    "require_feature",
    "require_plan",
    "check_usage_limit",
    "FeatureGate",
    # Service
    "FeatureService",
    "get_feature_service",
]
