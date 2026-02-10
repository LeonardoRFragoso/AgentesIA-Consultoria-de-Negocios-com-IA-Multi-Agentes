"""
Middlewares e dependencies de autenticação para FastAPI.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from functools import wraps
from typing import Optional, List

from security.jwt_handler import JWTHandler, TokenPayload
from config import get_settings


class HTTPAuthCredentials(BaseModel):
    """HTTP Authentication Credentials model."""
    scheme: str
    credentials: str


# Security scheme
security = HTTPBearer()


def get_jwt_handler() -> JWTHandler:
    """Factory para JWTHandler com configurações."""
    settings = get_settings()
    return JWTHandler(
        secret_key=settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
        access_expire_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        refresh_expire_days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )


async def get_current_user(
    credentials: HTTPAuthCredentials = Depends(security),
    jwt_handler: JWTHandler = Depends(get_jwt_handler)
) -> TokenPayload:
    """
    Dependency que extrai e valida o usuário do token.
    
    Raises:
        HTTPException 401 se token inválido ou expirado
    """
    token = credentials.credentials
    payload = jwt_handler.verify_access_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return payload


async def get_current_active_user(
    current_user: TokenPayload = Depends(get_current_user)
) -> TokenPayload:
    """
    Dependency que verifica se usuário está ativo.
    Pode ser estendida para verificar status no banco.
    """
    # TODO: Verificar se usuário/org está ativo no banco
    # Por ora, se o token é válido, o usuário está ativo
    return current_user


class TenantContext:
    """
    Contexto do tenant para isolamento multi-tenant.
    Usado em queries e operações.
    """
    
    def __init__(
        self,
        user_id: str,
        org_id: str,
        email: str,
        role: str,
        plan: str
    ):
        self.user_id = user_id
        self.org_id = org_id
        self.email = email
        self.role = role
        self.plan = plan
    
    def is_owner(self) -> bool:
        return self.role == "owner"
    
    def is_admin(self) -> bool:
        return self.role in ("owner", "admin")
    
    def can_manage_team(self) -> bool:
        return self.is_admin()
    
    def can_manage_billing(self) -> bool:
        return self.is_owner()


async def get_tenant_context(
    current_user: TokenPayload = Depends(get_current_active_user)
) -> TenantContext:
    """
    Extrai contexto do tenant do token.
    Use isso em endpoints que precisam de isolamento multi-tenant.
    """
    return TenantContext(
        user_id=current_user.sub,
        org_id=current_user.org_id,
        email=current_user.email,
        role=current_user.role,
        plan=current_user.plan
    )


def require_plan(allowed_plans: List[str]):
    """
    Decorator para restringir endpoints por plano.
    
    Uso:
        @app.get("/api/v1/export")
        @require_plan(["pro", "enterprise"])
        async def export_analysis(...):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extrai tenant do kwargs (injetado pelo FastAPI)
            tenant: TenantContext = kwargs.get("tenant")
            
            if not tenant:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="TenantContext não encontrado"
                )
            
            if tenant.plan not in allowed_plans:
                raise HTTPException(
                    status_code=status.HTTP_402_PAYMENT_REQUIRED,
                    detail=f"Este recurso requer plano: {', '.join(allowed_plans)}. "
                           f"Seu plano atual: {tenant.plan}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_role(allowed_roles: List[str]):
    """
    Decorator para restringir endpoints por role.
    
    Uso:
        @app.delete("/api/v1/team/{user_id}")
        @require_role(["owner", "admin"])
        async def remove_team_member(...):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            tenant: TenantContext = kwargs.get("tenant")
            
            if not tenant:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="TenantContext não encontrado"
                )
            
            if tenant.role not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Este recurso requer permissão: {', '.join(allowed_roles)}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator
