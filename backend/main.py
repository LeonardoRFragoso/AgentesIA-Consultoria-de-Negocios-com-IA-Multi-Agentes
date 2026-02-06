"""
Backend SaaS FastAPI - Camada de Plataforma
Responsável por: Autenticação, Multi-tenant, Billing, API
NÃO contém lógica de decisão (isso fica no core)
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from typing import Optional
import jwt
import os
from dotenv import load_dotenv

load_dotenv()

# ============================================================================
# CONFIGURAÇÃO
# ============================================================================

app = FastAPI(
    title="Consultor Executivo Multi-Agentes - API",
    version="1.0.0",
    description="API SaaS para análise estratégica com múltiplos agentes"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção: ["https://app.example.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurações
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 30

security = HTTPBearer()

# ============================================================================
# MODELOS
# ============================================================================

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    organization_name: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    user_id: str
    email: str
    tenant_id: str
    organization_name: str
    created_at: datetime


class ExecutionRequest(BaseModel):
    problem_description: str
    business_type: str = "B2B"
    analysis_depth: str = "Padrão"


class ExecutionResponse(BaseModel):
    execution_id: str
    status: str
    created_at: datetime
    estimated_duration_seconds: int = 30


class BillingStatus(BaseModel):
    plan: str  # free, pro, enterprise
    executions_used: int
    executions_limit: Optional[int]
    tokens_used_today: int
    tokens_limit_today: Optional[int]
    billing_status: str  # active, past_due, cancelled
    next_billing_date: Optional[datetime]


# ============================================================================
# AUTENTICAÇÃO
# ============================================================================

def create_access_token(user_id: str, email: str, tenant_id: str) -> str:
    """Cria JWT access token"""
    payload = {
        "sub": user_id,
        "email": email,
        "tenant_id": tenant_id,
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        "iat": datetime.utcnow(),
        "type": "access"
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(user_id: str) -> str:
    """Cria JWT refresh token"""
    payload = {
        "sub": user_id,
        "exp": datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        "iat": datetime.utcnow(),
        "type": "refresh"
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> dict:
    """Valida e decodifica JWT"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )


async def get_current_user(credentials: HTTPAuthCredentials = Depends(security)) -> dict:
    """Middleware de autenticação"""
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )
    
    return payload


# ============================================================================
# TENANT CONTEXT
# ============================================================================

class TenantContext:
    """Contexto do tenant extraído do token"""
    def __init__(self, tenant_id: str, user_id: str, email: str):
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.email = email


async def get_tenant_context(current_user: dict = Depends(get_current_user)) -> TenantContext:
    """Extrai contexto do tenant do token"""
    return TenantContext(
        tenant_id=current_user["tenant_id"],
        user_id=current_user["sub"],
        email=current_user["email"]
    )


# ============================================================================
# BILLING CONTROL
# ============================================================================

class BillingService:
    """Serviço de billing (mock para MVP)"""
    
    # Em produção: seria um banco de dados
    tenants = {
        "org_123": {
            "plan": "pro",
            "executions_this_month": 5,
            "tokens_today": 45000,
            "billing_status": "active"
        }
    }
    
    @staticmethod
    def check_execution_allowed(tenant_id: str) -> tuple[bool, Optional[str]]:
        """Verifica se tenant pode executar análise"""
        tenant = BillingService.tenants.get(tenant_id)
        
        if not tenant:
            # Novo tenant: começa em free
            tenant = {
                "plan": "free",
                "executions_this_month": 0,
                "tokens_today": 0,
                "billing_status": "active"
            }
            BillingService.tenants[tenant_id] = tenant
        
        # Verifica status
        if tenant["billing_status"] != "active":
            return False, f"Assinatura {tenant['billing_status']}"
        
        # Verifica limite de execuções
        if tenant["plan"] == "free":
            if tenant["executions_this_month"] >= 10:
                return False, "Limite de execuções atingido. Upgrade para Pro"
        
        # Verifica limite de tokens (Pro)
        if tenant["plan"] == "pro":
            if tenant["tokens_today"] >= 100000:
                return False, "Limite diário de tokens atingido"
        
        return True, None
    
    @staticmethod
    def record_execution(tenant_id: str, tokens_used: int) -> None:
        """Registra execução para billing"""
        tenant = BillingService.tenants.get(tenant_id)
        if tenant:
            tenant["executions_this_month"] += 1
            tenant["tokens_today"] += tokens_used
    
    @staticmethod
    def get_status(tenant_id: str) -> BillingStatus:
        """Retorna status de billing do tenant"""
        tenant = BillingService.tenants.get(tenant_id, {
            "plan": "free",
            "executions_this_month": 0,
            "tokens_today": 0,
            "billing_status": "active"
        })
        
        limits = {
            "free": {"executions": 10, "tokens": None},
            "pro": {"executions": None, "tokens": 100000},
            "enterprise": {"executions": None, "tokens": None}
        }
        
        plan_limits = limits.get(tenant["plan"], {})
        
        return BillingStatus(
            plan=tenant["plan"],
            executions_used=tenant["executions_this_month"],
            executions_limit=plan_limits.get("executions"),
            tokens_used_today=tenant["tokens_today"],
            tokens_limit_today=plan_limits.get("tokens"),
            billing_status=tenant["billing_status"],
            next_billing_date=datetime.utcnow() + timedelta(days=30)
        )


# ============================================================================
# ENDPOINTS: AUTENTICAÇÃO
# ============================================================================

@app.post("/api/v1/auth/register", response_model=TokenResponse)
async def register(user: UserRegister):
    """Registra novo usuário e organização"""
    # Em produção: validar email único, hash password, salvar BD
    user_id = f"user_{hash(user.email) % 10000}"
    tenant_id = f"org_{hash(user.organization_name) % 10000}"
    
    access_token = create_access_token(user_id, user.email, tenant_id)
    refresh_token = create_refresh_token(user_id)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )


@app.post("/api/v1/auth/login", response_model=TokenResponse)
async def login(user: UserLogin):
    """Login de usuário existente"""
    # Em produção: validar credenciais contra BD
    user_id = f"user_{hash(user.email) % 10000}"
    tenant_id = f"org_{hash(user.email) % 10000}"
    
    access_token = create_access_token(user_id, user.email, tenant_id)
    refresh_token = create_refresh_token(user_id)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )


@app.post("/api/v1/auth/refresh", response_model=TokenResponse)
async def refresh(refresh_token: str):
    """Renova access token usando refresh token"""
    payload = verify_token(refresh_token)
    
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido"
        )
    
    user_id = payload["sub"]
    # Em produção: recuperar email e tenant_id do BD
    email = "user@example.com"
    tenant_id = "org_123"
    
    access_token = create_access_token(user_id, email, tenant_id)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )


# ============================================================================
# ENDPOINTS: USUÁRIO
# ============================================================================

@app.get("/api/v1/me", response_model=UserResponse)
async def get_current_user_info(tenant: TenantContext = Depends(get_tenant_context)):
    """Retorna informações do usuário atual"""
    return UserResponse(
        user_id=tenant.user_id,
        email=tenant.email,
        tenant_id=tenant.tenant_id,
        organization_name="Acme Corp",  # Em produção: do BD
        created_at=datetime.utcnow()
    )


# ============================================================================
# ENDPOINTS: EXECUÇÕES
# ============================================================================

@app.post("/api/v1/executions", response_model=ExecutionResponse, status_code=201)
async def create_execution(
    request: ExecutionRequest,
    tenant: TenantContext = Depends(get_tenant_context)
):
    """Cria nova execução (análise)"""
    
    # 1. Verifica billing
    allowed, error_msg = BillingService.check_execution_allowed(tenant.tenant_id)
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=error_msg
        )
    
    # 2. Chama core engine
    # Em produção: seria uma chamada real ao BusinessOrchestrator
    execution_id = f"exec_{hash(request.problem_description) % 100000}"
    
    # 3. Registra para billing
    BillingService.record_execution(tenant.tenant_id, tokens_used=500)
    
    return ExecutionResponse(
        execution_id=execution_id,
        status="running",
        created_at=datetime.utcnow(),
        estimated_duration_seconds=30
    )


@app.get("/api/v1/executions")
async def list_executions(tenant: TenantContext = Depends(get_tenant_context)):
    """Lista execuções do tenant"""
    # Em produção: query BD com WHERE tenant_id = ?
    return {
        "executions": [
            {
                "execution_id": "exec_123",
                "status": "completed",
                "created_at": datetime.utcnow().isoformat(),
                "problem": "Vendas caíram 20%..."
            }
        ]
    }


@app.get("/api/v1/executions/{execution_id}")
async def get_execution(
    execution_id: str,
    tenant: TenantContext = Depends(get_tenant_context)
):
    """Retorna detalhe de uma execução"""
    # Em produção: query BD com WHERE execution_id = ? AND tenant_id = ?
    return {
        "execution_id": execution_id,
        "status": "completed",
        "decision": "Investir em marketing digital",
        "confidence": 0.82,
        "actions": [
            {"description": "Preparar plano", "owner": "Commercial", "due": "5 dias"}
        ]
    }


# ============================================================================
# ENDPOINTS: BILLING
# ============================================================================

@app.get("/api/v1/billing/status", response_model=BillingStatus)
async def get_billing_status(tenant: TenantContext = Depends(get_tenant_context)):
    """Retorna status de billing do tenant"""
    return BillingService.get_status(tenant.tenant_id)


# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check para monitoramento"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
