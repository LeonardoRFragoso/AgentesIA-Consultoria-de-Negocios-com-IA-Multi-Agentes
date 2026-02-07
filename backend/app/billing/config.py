"""
Billing Configuration - Environment Variables & Settings
"""
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class MercadoPagoConfig:
    """Configuração do Mercado Pago"""
    access_token: str
    public_key: str
    webhook_secret: Optional[str]
    sandbox_mode: bool
    
    @classmethod
    def from_env(cls) -> "MercadoPagoConfig":
        """Carrega configuração do ambiente"""
        return cls(
            access_token=os.getenv("MERCADO_PAGO_ACCESS_TOKEN", ""),
            public_key=os.getenv("MERCADO_PAGO_PUBLIC_KEY", ""),
            webhook_secret=os.getenv("MERCADO_PAGO_WEBHOOK_SECRET"),
            sandbox_mode=os.getenv("MERCADO_PAGO_SANDBOX", "true").lower() == "true",
        )
    
    def is_configured(self) -> bool:
        """Verifica se as credenciais estão configuradas"""
        return bool(self.access_token and self.public_key)


@dataclass
class BillingConfig:
    """Configuração geral de billing"""
    app_url: str
    success_url: str
    failure_url: str
    pending_url: str
    webhook_url: str
    
    @classmethod
    def from_env(cls) -> "BillingConfig":
        """Carrega configuração do ambiente"""
        app_url = os.getenv("APP_URL", "http://localhost:3000")
        api_url = os.getenv("API_URL", "http://localhost:8000")
        
        return cls(
            app_url=app_url,
            success_url=f"{app_url}/billing/success",
            failure_url=f"{app_url}/billing/failure",
            pending_url=f"{app_url}/billing/pending",
            webhook_url=f"{api_url}/api/webhooks/mercadopago",
        )


# Singleton instances
_mp_config: Optional[MercadoPagoConfig] = None
_billing_config: Optional[BillingConfig] = None


def get_mercado_pago_config() -> MercadoPagoConfig:
    """Retorna configuração do Mercado Pago"""
    global _mp_config
    if _mp_config is None:
        _mp_config = MercadoPagoConfig.from_env()
    return _mp_config


def get_billing_config() -> BillingConfig:
    """Retorna configuração de billing"""
    global _billing_config
    if _billing_config is None:
        _billing_config = BillingConfig.from_env()
    return _billing_config


# ==================== ENVIRONMENT TEMPLATE ====================

ENV_TEMPLATE = """
# ============================================
# MERCADO PAGO - BILLING CONFIGURATION
# ============================================

# Credenciais do Mercado Pago
# Obtenha em: https://www.mercadopago.com.br/developers/panel/app
MERCADO_PAGO_ACCESS_TOKEN=APP_USR-xxx
MERCADO_PAGO_PUBLIC_KEY=APP_USR-xxx

# Secret para validação de webhooks (opcional, mas recomendado)
# Configure em: https://www.mercadopago.com.br/developers/panel/app/{app_id}/webhooks
MERCADO_PAGO_WEBHOOK_SECRET=xxx

# Modo sandbox (desenvolvimento)
MERCADO_PAGO_SANDBOX=true

# URLs da aplicação
APP_URL=http://localhost:3000
API_URL=http://localhost:8000

# ============================================
# IDs dos Planos no Mercado Pago (após criar)
# ============================================

# Pro Plan
MP_PLAN_PRO_MONTHLY=xxx
MP_PLAN_PRO_YEARLY=xxx

# Enterprise Plan  
MP_PLAN_ENTERPRISE_MONTHLY=xxx
MP_PLAN_ENTERPRISE_YEARLY=xxx
"""


def print_env_template():
    """Imprime template de variáveis de ambiente"""
    print(ENV_TEMPLATE)


if __name__ == "__main__":
    print_env_template()
