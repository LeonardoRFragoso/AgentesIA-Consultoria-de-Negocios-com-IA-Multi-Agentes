"""
Pydantic schemas para request/response validation.

HARDENING: Validação rigorosa de todos os inputs.
Cada campo tem:
- Tipo explícito
- Limites de tamanho
- Patterns quando aplicável
- Sanitização implícita via Pydantic
"""

import re
from datetime import datetime
from typing import Optional, List, Dict, Any, Annotated
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from uuid import UUID


# =============================================================================
# VALIDATORS CUSTOMIZADOS
# =============================================================================

def validate_no_script_tags(v: str) -> str:
    """Remove/bloqueia tags de script e padrões perigosos."""
    if not v:
        return v
    
    # Padrões perigosos
    dangerous_patterns = [
        r"<script[^>]*>",
        r"</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe",
        r"<object",
        r"<embed",
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, v, re.IGNORECASE):
            raise ValueError(f"Conteúdo não permitido detectado")
    
    return v


def validate_no_sql_injection(v: str) -> str:
    """Detecta padrões básicos de SQL injection."""
    if not v:
        return v
    
    sql_patterns = [
        r";\s*drop\s+",
        r";\s*delete\s+",
        r";\s*update\s+",
        r";\s*insert\s+",
        r"union\s+select",
        r"--\s*$",
    ]
    
    for pattern in sql_patterns:
        if re.search(pattern, v, re.IGNORECASE):
            raise ValueError("Padrão não permitido detectado")
    
    return v


# =============================================================================
# AUTH
# =============================================================================

class UserRegister(BaseModel):
    """
    Schema de registro de usuário.
    
    Validações:
    - Email: formato válido, max 255 chars
    - Password: 8-128 chars, complexidade mínima
    - Organization: 2-100 chars, sem caracteres especiais perigosos
    - Name: opcional, max 100 chars
    """
    model_config = ConfigDict(str_strip_whitespace=True)
    
    email: EmailStr = Field(
        ...,
        max_length=255,
        description="Email válido do usuário"
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Senha com mínimo 8 caracteres"
    )
    organization_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        pattern=r"^[\w\s\-\.áéíóúàèìòùâêîôûãõç]+$",
        description="Nome da organização (letras, números, espaços, hífens)"
    )
    name: Optional[str] = Field(
        None,
        max_length=100,
        description="Nome do usuário"
    )
    
    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Valida força da senha."""
        if len(v) < 8:
            raise ValueError("Senha deve ter pelo menos 8 caracteres")
        
        # Pelo menos uma letra e um número
        if not re.search(r"[a-zA-Z]", v):
            raise ValueError("Senha deve conter pelo menos uma letra")
        if not re.search(r"\d", v):
            raise ValueError("Senha deve conter pelo menos um número")
        
        return v
    
    @field_validator("organization_name", "name")
    @classmethod
    def sanitize_text(cls, v: str) -> str:
        if v:
            v = validate_no_script_tags(v)
        return v


class UserLogin(BaseModel):
    """Schema de login."""
    model_config = ConfigDict(str_strip_whitespace=True)
    
    email: EmailStr = Field(..., max_length=255)
    password: str = Field(..., min_length=1, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 900  # 15 minutes


class RefreshTokenRequest(BaseModel):
    refresh_token: str


# =============================================================================
# USER
# =============================================================================

class UserResponse(BaseModel):
    id: UUID
    email: str
    name: Optional[str]
    role: str
    org_id: UUID
    organization_name: str
    plan: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserInvite(BaseModel):
    email: EmailStr
    role: str = Field(default="member", pattern="^(admin|member)$")


# =============================================================================
# ORGANIZATION
# =============================================================================

class OrganizationResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    plan: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# =============================================================================
# ANALYSIS
# =============================================================================

class AnalysisCreate(BaseModel):
    """
    Schema para criação de análise.
    
    Validações:
    - problem_description: 10-10000 chars, sanitizado
    - business_type: valores permitidos específicos
    - analysis_depth: enum restrito
    """
    model_config = ConfigDict(str_strip_whitespace=True)
    
    problem_description: str = Field(
        ...,
        min_length=10,
        max_length=10000,
        description="Descrição do problema de negócio"
    )
    business_type: str = Field(
        default="B2B",
        max_length=50,
        pattern=r"^(B2B|B2C|B2B2C|D2C|SaaS|Marketplace|E-commerce|Outro)$",
        description="Tipo de negócio"
    )
    analysis_depth: str = Field(
        default="Padrão",
        pattern=r"^(Rápida|Padrão|Profunda)$",
        description="Profundidade da análise"
    )
    
    @field_validator("problem_description")
    @classmethod
    def validate_problem(cls, v: str) -> str:
        """Sanitiza descrição do problema."""
        v = validate_no_script_tags(v)
        v = validate_no_sql_injection(v)
        return v


class AnalysisResponse(BaseModel):
    id: UUID
    problem_description: str
    business_type: str
    analysis_depth: str
    status: str
    executive_summary: Optional[str]
    total_tokens: int
    total_cost_usd: float
    total_latency_ms: float
    created_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class AnalysisDetailResponse(AnalysisResponse):
    results: Optional[Dict[str, Any]]
    error_message: Optional[str]


class AnalysisListResponse(BaseModel):
    items: List[AnalysisResponse]
    total: int
    limit: int
    offset: int


# =============================================================================
# BILLING
# =============================================================================

class BillingStatusResponse(BaseModel):
    plan: str
    executions_this_month: int
    executions_limit: Optional[int]
    tokens_used_today: int
    tokens_limit_today: Optional[int]
    exports_enabled: bool
    history_days: int
    users_limit: int


class CheckoutSessionResponse(BaseModel):
    checkout_url: str
    session_id: str


# =============================================================================
# HEALTH
# =============================================================================

class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str
    timestamp: datetime
