"""
Configuração centralizada e segura para o backend SaaS.
Todas as configurações sensíveis vêm de variáveis de ambiente.
"""

import os
import json
from functools import lru_cache
from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Configurações da aplicação.
    Usa pydantic-settings para validação e carregamento de .env
    """
    
    # ==========================================================================
    # APP
    # ==========================================================================
    APP_NAME: str = "Consultor Executivo Multi-Agentes"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = Field(default="development", pattern="^(development|staging|production)$")
    
    # ==========================================================================
    # SECURITY - CRÍTICO: Nunca usar defaults em produção
    # ==========================================================================
    JWT_SECRET_KEY: str = Field(
        default="dev-secret-key-change-in-production-must-be-32-chars-minimum",
        min_length=32,
        description="Gere com: openssl rand -hex 32"
    )
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    
    # Bcrypt
    BCRYPT_ROUNDS: int = 12  # Produção: 12-14
    
    # ==========================================================================
    # CORS - Restritivo por padrão
    # ==========================================================================
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8501"],
        description="Lista de origens permitidas. Em produção: seu domínio real"
    )
    CORS_ALLOW_CREDENTIALS: bool = True
    
    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS_ORIGINS se vir como string JSON."""
        if isinstance(v, str):
            try:
                return json.loads(v)
            except (json.JSONDecodeError, TypeError):
                # Se não for JSON válido, trata como lista com um item
                return [v]
        return v
    
    # ==========================================================================
    # DATABASE
    # ==========================================================================
    DATABASE_URL: str = Field(
        default="postgresql://localhost:5432/multiagentes",
        description="URL de conexão PostgreSQL"
    )
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10
    
    # ==========================================================================
    # REDIS (Cache + Rate Limiting)
    # ==========================================================================
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="URL de conexão Redis"
    )
    CACHE_TTL_SECONDS: int = 3600  # 1 hora
    
    # ==========================================================================
    # RATE LIMITING
    # ==========================================================================
    RATE_LIMIT_FREE: str = "10/hour"
    RATE_LIMIT_PRO: str = "100/hour"
    RATE_LIMIT_ENTERPRISE: str = "1000/hour"
    
    # ==========================================================================
    # LLM PROVIDERS
    # ==========================================================================
    ANTHROPIC_API_KEY: Optional[str] = Field(
        default=None,
        description="Chave da API Anthropic (obrigatório para análises)"
    )
    
    # ==========================================================================
    # BILLING (Stripe)
    # ==========================================================================
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    STRIPE_PRICE_PRO_MONTHLY: Optional[str] = None
    STRIPE_PRICE_PRO_YEARLY: Optional[str] = None
    STRIPE_PRICE_ENTERPRISE_MONTHLY: Optional[str] = None
    
    # ==========================================================================
    # OBSERVABILITY
    # ==========================================================================
    SENTRY_DSN: Optional[str] = None
    LOG_LEVEL: str = "INFO"
    
    # ==========================================================================
    # PLANS CONFIGURATION
    # ==========================================================================
    PLAN_FREE_EXECUTIONS_MONTH: int = 10
    PLAN_FREE_USERS: int = 1
    PLAN_PRO_USERS: int = 5
    PLAN_PRO_TOKENS_DAY: int = 100000
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"
    
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"
    
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"
    
    def validate_production_settings(self) -> None:
        """Valida configurações críticas para produção."""
        if self.is_production():
            # JWT secret deve ser forte
            if len(self.JWT_SECRET_KEY) < 32:
                raise ValueError("JWT_SECRET_KEY deve ter pelo menos 32 caracteres em produção")
            
            # Debug deve estar desligado
            if self.DEBUG:
                raise ValueError("DEBUG deve ser False em produção")
            
            # CORS não pode ser wildcard
            if "*" in self.CORS_ORIGINS:
                raise ValueError("CORS_ORIGINS não pode conter '*' em produção")
            
            # Stripe é opcional inicialmente (warning apenas)
            # if not self.STRIPE_SECRET_KEY:
            #     raise ValueError("STRIPE_SECRET_KEY é obrigatório em produção")


@lru_cache()
def get_settings() -> Settings:
    """
    Singleton para configurações.
    Cached para evitar re-leitura do .env a cada request.
    """
    settings = Settings()
    settings.validate_production_settings()
    return settings
