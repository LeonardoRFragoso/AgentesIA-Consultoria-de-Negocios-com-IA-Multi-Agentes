"""
Security Hardening - Configurações de segurança para produção
"""
import os
import time
import hashlib
import secrets
import logging
from datetime import datetime, timedelta
from typing import Optional, Callable
from functools import wraps

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = logging.getLogger(__name__)


# ============================================
# RATE LIMITING
# ============================================

class RateLimiter:
    """
    Rate limiter simples baseado em memória.
    Para produção, use Redis.
    """
    
    def __init__(self):
        self.requests: dict[str, list[float]] = {}
    
    def is_allowed(
        self,
        key: str,
        limit: int,
        window_seconds: int,
    ) -> tuple[bool, int]:
        """
        Verifica se a requisição é permitida.
        Retorna (is_allowed, remaining_requests)
        """
        now = time.time()
        window_start = now - window_seconds
        
        # Limpa requests antigas
        if key in self.requests:
            self.requests[key] = [
                t for t in self.requests[key] 
                if t > window_start
            ]
        else:
            self.requests[key] = []
        
        # Verifica limite
        current_count = len(self.requests[key])
        remaining = max(0, limit - current_count)
        
        if current_count >= limit:
            return False, 0
        
        # Registra request
        self.requests[key].append(now)
        return True, remaining - 1


# Instância global
rate_limiter = RateLimiter()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware de rate limiting"""
    
    def __init__(
        self,
        app,
        limit_per_minute: int = 60,
        limit_per_hour: int = 1000,
    ):
        super().__init__(app)
        self.limit_per_minute = limit_per_minute
        self.limit_per_hour = limit_per_hour
    
    async def dispatch(self, request: Request, call_next):
        # Identifica cliente (IP ou user_id)
        client_ip = self._get_client_ip(request)
        
        # Verifica limite por minuto
        minute_key = f"rate:minute:{client_ip}"
        allowed, remaining = rate_limiter.is_allowed(
            minute_key, 
            self.limit_per_minute, 
            60
        )
        
        if not allowed:
            return Response(
                content='{"error": "Rate limit exceeded. Try again later."}',
                status_code=429,
                headers={
                    "Retry-After": "60",
                    "X-RateLimit-Limit": str(self.limit_per_minute),
                    "X-RateLimit-Remaining": "0",
                },
                media_type="application/json",
            )
        
        # Processa request
        response = await call_next(request)
        
        # Adiciona headers de rate limit
        response.headers["X-RateLimit-Limit"] = str(self.limit_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        # Verifica headers de proxy
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"


# ============================================
# SECURITY HEADERS
# ============================================

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Adiciona headers de segurança em todas as respostas"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Previne clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        
        # Previne MIME sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Habilita XSS filter do browser
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Referrer policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Content Security Policy (ajuste conforme necessário)
        # response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        # Permissions Policy
        response.headers["Permissions-Policy"] = (
            "accelerometer=(), camera=(), geolocation=(), "
            "gyroscope=(), magnetometer=(), microphone=(), "
            "payment=(), usb=()"
        )
        
        # Remove header que expõe tecnologia
        if "Server" in response.headers:
            del response.headers["Server"]
        
        return response


# ============================================
# REQUEST LOGGING
# ============================================

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log de todas as requisições para auditoria"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Gera request ID
        request_id = secrets.token_hex(8)
        request.state.request_id = request_id
        
        # Log da request
        logger.info(
            f"[{request_id}] {request.method} {request.url.path} "
            f"client={self._get_client_ip(request)}"
        )
        
        # Processa
        response = await call_next(request)
        
        # Log da response
        duration = time.time() - start_time
        logger.info(
            f"[{request_id}] {response.status_code} "
            f"duration={duration:.3f}s"
        )
        
        # Adiciona request ID na response
        response.headers["X-Request-ID"] = request_id
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"


# ============================================
# INPUT VALIDATION
# ============================================

def sanitize_input(value: str, max_length: int = 10000) -> str:
    """Sanitiza input do usuário"""
    if not value:
        return value
    
    # Limita tamanho
    value = value[:max_length]
    
    # Remove caracteres de controle (exceto newlines e tabs)
    value = ''.join(
        char for char in value 
        if char.isprintable() or char in '\n\r\t'
    )
    
    return value.strip()


def validate_email(email: str) -> bool:
    """Validação básica de email"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


# ============================================
# PASSWORD SECURITY
# ============================================

def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    """
    Hash de senha com PBKDF2.
    Retorna (hash, salt)
    """
    if salt is None:
        salt = secrets.token_hex(32)
    
    hash_value = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode(),
        salt.encode(),
        iterations=100000,
    )
    
    return hash_value.hex(), salt


def verify_password(password: str, hash_value: str, salt: str) -> bool:
    """Verifica senha contra hash"""
    new_hash, _ = hash_password(password, salt)
    return secrets.compare_digest(new_hash, hash_value)


def check_password_strength(password: str) -> tuple[bool, list[str]]:
    """
    Verifica força da senha.
    Retorna (is_strong, list_of_issues)
    """
    issues = []
    
    if len(password) < 8:
        issues.append("Mínimo 8 caracteres")
    
    if not any(c.isupper() for c in password):
        issues.append("Pelo menos uma letra maiúscula")
    
    if not any(c.islower() for c in password):
        issues.append("Pelo menos uma letra minúscula")
    
    if not any(c.isdigit() for c in password):
        issues.append("Pelo menos um número")
    
    if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
        issues.append("Pelo menos um caractere especial")
    
    return len(issues) == 0, issues


# ============================================
# API KEY MANAGEMENT
# ============================================

def generate_api_key() -> str:
    """Gera API key segura"""
    return f"sk_{secrets.token_urlsafe(32)}"


def hash_api_key(api_key: str) -> str:
    """Hash de API key para storage"""
    return hashlib.sha256(api_key.encode()).hexdigest()


# ============================================
# SETUP FUNCTION
# ============================================

def setup_security(app: FastAPI) -> None:
    """
    Configura todos os middlewares de segurança.
    Chame esta função ao inicializar o app.
    """
    env = os.getenv("APP_ENV", "development")
    is_production = env == "production"
    
    # CORS
    allowed_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins if is_production else ["*"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID", "X-RateLimit-Remaining"],
    )
    
    # Trusted hosts (apenas em produção)
    if is_production:
        allowed_hosts = os.getenv("ALLOWED_HOSTS", "localhost").split(",")
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)
    
    # Rate limiting
    rate_limit = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    app.add_middleware(RateLimitMiddleware, limit_per_minute=rate_limit)
    
    # Security headers
    app.add_middleware(SecurityHeadersMiddleware)
    
    # Request logging
    app.add_middleware(RequestLoggingMiddleware)
    
    logger.info(f"Security configured for {env} environment")


# ============================================
# DECORATOR PARA ROTAS SENSÍVEIS
# ============================================

def require_secure(func: Callable) -> Callable:
    """
    Decorator para rotas que requerem segurança adicional.
    Verifica HTTPS em produção.
    """
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        env = os.getenv("APP_ENV", "development")
        
        if env == "production":
            # Verifica HTTPS
            if request.url.scheme != "https":
                forwarded_proto = request.headers.get("X-Forwarded-Proto")
                if forwarded_proto != "https":
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="HTTPS required"
                    )
        
        return await func(request, *args, **kwargs)
    
    return wrapper
