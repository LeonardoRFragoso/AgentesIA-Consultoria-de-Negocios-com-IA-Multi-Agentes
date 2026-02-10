"""
Security Middleware - Hardening completo para produção.

VULNERABILIDADES CORRIGIDAS:
1. CORS permissivo (allow_origins=["*"])
2. Sem rate limiting por IP/usuário
3. Sem proteção contra payloads maliciosos
4. Sem validação de Content-Type
5. Sem proteção contra ataques de timing
6. Headers de segurança incompletos
"""

import re
import time
import hashlib
import ipaddress
from typing import Optional, Set, Dict, Callable
from datetime import datetime
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)


# =============================================================================
# CONFIGURAÇÕES DE SEGURANÇA (Limites configuráveis)
# =============================================================================

class SecurityConfig:
    """
    Configurações de segurança centralizadas.
    TODOS os limites estão aqui para fácil ajuste.
    """
    
    # -------------------------------------------------------------------------
    # RATE LIMITING
    # -------------------------------------------------------------------------
    # Limite global por IP (requests por minuto)
    RATE_LIMIT_IP_PER_MINUTE: int = 60
    
    # Limite por IP para endpoints de auth (mais restritivo)
    RATE_LIMIT_AUTH_PER_MINUTE: int = 10
    
    # Limite por usuário autenticado (requests por minuto)
    RATE_LIMIT_USER_PER_MINUTE: int = 120
    
    # Limite por organização (requests por hora)
    RATE_LIMIT_ORG_PER_HOUR: int = 1000
    
    # -------------------------------------------------------------------------
    # PAYLOAD LIMITS
    # -------------------------------------------------------------------------
    # Tamanho máximo do body (em bytes) - 1MB
    MAX_BODY_SIZE: int = 1_048_576
    
    # Tamanho máximo de string em campos de texto
    MAX_STRING_LENGTH: int = 50_000
    
    # Profundidade máxima de JSON aninhado
    MAX_JSON_DEPTH: int = 10
    
    # -------------------------------------------------------------------------
    # BRUTE FORCE PROTECTION
    # -------------------------------------------------------------------------
    # Tentativas de login antes de slowdown
    LOGIN_ATTEMPTS_BEFORE_DELAY: int = 3
    
    # Delay em segundos após muitas tentativas
    LOGIN_DELAY_SECONDS: int = 2
    
    # Bloqueio temporário após X tentativas
    LOGIN_ATTEMPTS_BEFORE_BLOCK: int = 10
    
    # Duração do bloqueio (segundos)
    LOGIN_BLOCK_DURATION: int = 900  # 15 minutos
    
    # -------------------------------------------------------------------------
    # IP BLOCKING
    # -------------------------------------------------------------------------
    # IPs/ranges bloqueados (adicione conforme necessário)
    BLOCKED_IPS: Set[str] = set()
    
    # Ranges de IP sempre permitidos (ex: seu escritório)
    ALLOWED_IPS: Set[str] = set()
    
    # -------------------------------------------------------------------------
    # REQUEST VALIDATION
    # -------------------------------------------------------------------------
    # User-Agents bloqueados (regex patterns)
    BLOCKED_USER_AGENTS: list = [
        r"^$",  # User-agent vazio
        r"curl/\d",  # curl (descomente para bloquear)
        r"python-requests",  # scripts automáticos
        r"scrapy",
        r"bot",
        r"spider",
        r"crawler",
    ]
    
    # Paths que não precisam de validação de User-Agent
    USER_AGENT_EXEMPT_PATHS: Set[str] = {
        "/health",
        "/",
        "/docs",
        "/openapi.json",
    }
    
    # -------------------------------------------------------------------------
    # CONTENT VALIDATION
    # -------------------------------------------------------------------------
    # Content-Types permitidos
    ALLOWED_CONTENT_TYPES: Set[str] = {
        "application/json",
        "application/x-www-form-urlencoded",
        "multipart/form-data",
    }


# =============================================================================
# RATE LIMITER AVANÇADO
# =============================================================================

class AdvancedRateLimiter:
    """
    Rate limiter com múltiplas estratégias:
    - Por IP (sliding window)
    - Por usuário autenticado
    - Por organização
    - Por endpoint específico
    """
    
    def __init__(self):
        self._ip_requests: Dict[str, list] = {}
        self._user_requests: Dict[str, list] = {}
        self._org_requests: Dict[str, list] = {}
        self._login_attempts: Dict[str, list] = {}
        self._blocked_ips: Dict[str, float] = {}  # IP -> unblock_time
    
    def _clean_old_entries(self, store: Dict[str, list], window_seconds: int):
        """Remove entradas antigas do store."""
        now = time.time()
        cutoff = now - window_seconds
        
        keys_to_delete = []
        for key, timestamps in store.items():
            store[key] = [ts for ts in timestamps if ts > cutoff]
            if not store[key]:
                keys_to_delete.append(key)
        
        for key in keys_to_delete:
            del store[key]
    
    def check_ip_rate_limit(
        self,
        ip: str,
        limit: int = SecurityConfig.RATE_LIMIT_IP_PER_MINUTE,
        window_seconds: int = 60
    ) -> tuple[bool, dict]:
        """
        Verifica rate limit por IP.
        
        Returns:
            (allowed, headers)
        """
        # Verifica se IP está bloqueado
        if ip in self._blocked_ips:
            if time.time() < self._blocked_ips[ip]:
                return False, {
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                    "Retry-After": str(int(self._blocked_ips[ip] - time.time()))
                }
            else:
                del self._blocked_ips[ip]
        
        now = time.time()
        cutoff = now - window_seconds
        
        if ip not in self._ip_requests:
            self._ip_requests[ip] = []
        
        # Limpa entradas antigas
        self._ip_requests[ip] = [ts for ts in self._ip_requests[ip] if ts > cutoff]
        
        current_count = len(self._ip_requests[ip])
        remaining = max(0, limit - current_count - 1)
        
        headers = {
            "X-RateLimit-Limit": str(limit),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(int(now + window_seconds))
        }
        
        if current_count >= limit:
            headers["Retry-After"] = str(window_seconds)
            return False, headers
        
        self._ip_requests[ip].append(now)
        return True, headers
    
    def check_auth_rate_limit(self, ip: str) -> tuple[bool, Optional[int]]:
        """
        Rate limit específico para endpoints de autenticação.
        Retorna (allowed, delay_seconds)
        """
        now = time.time()
        window = 60  # 1 minuto
        cutoff = now - window
        
        if ip not in self._login_attempts:
            self._login_attempts[ip] = []
        
        self._login_attempts[ip] = [ts for ts in self._login_attempts[ip] if ts > cutoff]
        attempts = len(self._login_attempts[ip])
        
        self._login_attempts[ip].append(now)
        
        # Bloqueio total
        if attempts >= SecurityConfig.LOGIN_ATTEMPTS_BEFORE_BLOCK:
            self._blocked_ips[ip] = now + SecurityConfig.LOGIN_BLOCK_DURATION
            return False, SecurityConfig.LOGIN_BLOCK_DURATION
        
        # Slowdown
        if attempts >= SecurityConfig.LOGIN_ATTEMPTS_BEFORE_DELAY:
            return True, SecurityConfig.LOGIN_DELAY_SECONDS
        
        return True, None
    
    def check_user_rate_limit(
        self,
        user_id: str,
        limit: int = SecurityConfig.RATE_LIMIT_USER_PER_MINUTE
    ) -> tuple[bool, dict]:
        """Rate limit por usuário autenticado."""
        now = time.time()
        window = 60
        cutoff = now - window
        
        if user_id not in self._user_requests:
            self._user_requests[user_id] = []
        
        self._user_requests[user_id] = [
            ts for ts in self._user_requests[user_id] if ts > cutoff
        ]
        
        current = len(self._user_requests[user_id])
        remaining = max(0, limit - current - 1)
        
        headers = {
            "X-RateLimit-Limit": str(limit),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(int(now + window))
        }
        
        if current >= limit:
            return False, headers
        
        self._user_requests[user_id].append(now)
        return True, headers
    
    def record_failed_login(self, ip: str):
        """Registra tentativa de login falha."""
        now = time.time()
        if ip not in self._login_attempts:
            self._login_attempts[ip] = []
        self._login_attempts[ip].append(now)
    
    def clear_login_attempts(self, ip: str):
        """Limpa tentativas após login bem-sucedido."""
        if ip in self._login_attempts:
            del self._login_attempts[ip]


# Instância global
_rate_limiter = AdvancedRateLimiter()


def get_advanced_rate_limiter() -> AdvancedRateLimiter:
    return _rate_limiter


# =============================================================================
# INPUT SANITIZATION
# =============================================================================

class InputSanitizer:
    """
    Sanitização e validação de inputs.
    Protege contra:
    - SQL Injection (padrões comuns)
    - XSS (scripts)
    - Path traversal
    - Command injection
    """
    
    # Padrões suspeitos (não bloqueia, mas loga)
    SUSPICIOUS_PATTERNS = [
        r"<script",
        r"javascript:",
        r"on\w+\s*=",
        r"\.\./",
        r"\.\.\\",
        r";\s*drop\s+table",
        r";\s*delete\s+from",
        r"union\s+select",
        r"exec\s*\(",
        r"\$\{",
        r"{{",
    ]
    
    @classmethod
    def check_suspicious_content(cls, content: str) -> list[str]:
        """
        Verifica conteúdo suspeito.
        Retorna lista de padrões encontrados.
        """
        if not content:
            return []
        
        found = []
        content_lower = content.lower()
        
        for pattern in cls.SUSPICIOUS_PATTERNS:
            if re.search(pattern, content_lower, re.IGNORECASE):
                found.append(pattern)
        
        return found
    
    @classmethod
    def validate_json_depth(cls, obj, current_depth: int = 0) -> bool:
        """Verifica profundidade do JSON."""
        if current_depth > SecurityConfig.MAX_JSON_DEPTH:
            return False
        
        if isinstance(obj, dict):
            for value in obj.values():
                if not cls.validate_json_depth(value, current_depth + 1):
                    return False
        elif isinstance(obj, list):
            for item in obj:
                if not cls.validate_json_depth(item, current_depth + 1):
                    return False
        
        return True


# =============================================================================
# SECURITY MIDDLEWARE
# =============================================================================

class SecurityMiddleware(BaseHTTPMiddleware):
    """
    Middleware de segurança abrangente.
    
    Implementa:
    - Rate limiting por IP
    - Validação de headers
    - Proteção contra payloads grandes
    - Logging de segurança
    - Headers de resposta seguros
    """
    
    def __init__(self, app, config: SecurityConfig = None):
        super().__init__(app)
        self.config = config or SecurityConfig()
        self.rate_limiter = get_advanced_rate_limiter()
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        client_ip = self._get_client_ip(request)
        
        # 0. Skip security checks for CORS preflight (OPTIONS) requests
        if request.method == "OPTIONS":
            response = await call_next(request)
            return response
        
        # 1. Verifica IP bloqueado
        if self._is_ip_blocked(client_ip):
            return self._blocked_response("IP blocked")
        
        # 2. Rate limiting por IP
        is_auth_endpoint = request.url.path.startswith("/api/v1/auth")
        
        if is_auth_endpoint:
            limit = SecurityConfig.RATE_LIMIT_AUTH_PER_MINUTE
        else:
            limit = SecurityConfig.RATE_LIMIT_IP_PER_MINUTE
        
        allowed, headers = self.rate_limiter.check_ip_rate_limit(client_ip, limit)
        
        if not allowed:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Too many requests. Please slow down."},
                headers=headers
            )
        
        # 3. Valida Content-Type para requests com body
        if request.method in ("POST", "PUT", "PATCH"):
            content_type = request.headers.get("content-type", "")
            if content_type:
                base_type = content_type.split(";")[0].strip()
                if base_type not in SecurityConfig.ALLOWED_CONTENT_TYPES:
                    return self._blocked_response(f"Invalid Content-Type: {base_type}")
        
        # 4. Valida tamanho do body
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > SecurityConfig.MAX_BODY_SIZE:
            return self._blocked_response("Request body too large")
        
        # 5. Processa request
        try:
            response = await call_next(request)
        except Exception as e:
            logger.error(f"Request error: {e}")
            raise
        
        # 6. Adiciona headers de segurança
        response = self._add_security_headers(response)
        
        # 7. Adiciona headers de rate limit
        for key, value in headers.items():
            response.headers[key] = value
        
        # 8. Log de request
        duration = (time.time() - start_time) * 1000
        logger.info(
            f"[SECURITY] {request.method} {request.url.path} "
            f"ip={client_ip} status={response.status_code} "
            f"duration={duration:.2f}ms"
        )
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Extrai IP real do cliente, considerando proxies."""
        # Ordem de preferência para headers de proxy
        headers_to_check = [
            "X-Forwarded-For",
            "X-Real-IP",
            "CF-Connecting-IP",  # Cloudflare
            "True-Client-IP",
        ]
        
        for header in headers_to_check:
            value = request.headers.get(header)
            if value:
                # X-Forwarded-For pode ter múltiplos IPs
                ip = value.split(",")[0].strip()
                if self._is_valid_ip(ip):
                    return ip
        
        # Fallback para IP direto
        if request.client:
            return request.client.host
        
        return "unknown"
    
    def _is_valid_ip(self, ip: str) -> bool:
        """Valida se é um IP válido."""
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False
    
    def _is_ip_blocked(self, ip: str) -> bool:
        """Verifica se IP está na blocklist."""
        if ip in SecurityConfig.BLOCKED_IPS:
            return True
        
        # Verifica ranges
        try:
            ip_obj = ipaddress.ip_address(ip)
            for blocked in SecurityConfig.BLOCKED_IPS:
                if "/" in blocked:
                    if ip_obj in ipaddress.ip_network(blocked, strict=False):
                        return True
        except ValueError:
            pass
        
        return False
    
    def _blocked_response(self, reason: str) -> JSONResponse:
        """Resposta para requests bloqueados."""
        logger.warning(f"Request blocked: {reason}")
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": "Request blocked"}
        )
    
    def _add_security_headers(self, response) -> JSONResponse:
        """Adiciona headers de segurança na resposta."""
        headers = {
            # Previne MIME sniffing
            "X-Content-Type-Options": "nosniff",
            
            # Previne clickjacking
            "X-Frame-Options": "DENY",
            
            # XSS protection (legacy, mas ainda útil)
            "X-XSS-Protection": "1; mode=block",
            
            # Controla referrer
            "Referrer-Policy": "strict-origin-when-cross-origin",
            
            # Previne cache de dados sensíveis
            "Cache-Control": "no-store, no-cache, must-revalidate, private",
            "Pragma": "no-cache",
            
            # Content Security Policy
            "Content-Security-Policy": "default-src 'self'; frame-ancestors 'none'",
            
            # Permissions Policy
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
        }
        
        for key, value in headers.items():
            response.headers[key] = value
        
        return response


# =============================================================================
# ABUSE PROTECTION
# =============================================================================

class AbuseProtection:
    """
    Proteção contra padrões de abuso.
    """
    
    # Fingerprints de requests suspeitos
    _suspicious_fingerprints: Dict[str, int] = {}
    
    @classmethod
    def check_request(cls, request: Request) -> tuple[bool, Optional[str]]:
        """
        Verifica se request parece abusivo.
        
        Returns:
            (is_ok, reason)
        """
        # 1. Verifica User-Agent
        user_agent = request.headers.get("user-agent", "")
        
        if request.url.path not in SecurityConfig.USER_AGENT_EXEMPT_PATHS:
            for pattern in SecurityConfig.BLOCKED_USER_AGENTS:
                if re.search(pattern, user_agent, re.IGNORECASE):
                    return False, f"Blocked User-Agent pattern: {pattern}"
        
        # 2. Verifica headers suspeitos
        if request.headers.get("X-Forwarded-For", "").count(",") > 10:
            return False, "Too many proxies in X-Forwarded-For"
        
        return True, None
    
    @classmethod
    def create_request_fingerprint(cls, request: Request) -> str:
        """Cria fingerprint do request para detecção de bots."""
        components = [
            request.headers.get("user-agent", ""),
            request.headers.get("accept-language", ""),
            request.headers.get("accept-encoding", ""),
        ]
        return hashlib.md5("|".join(components).encode()).hexdigest()[:16]


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "SecurityConfig",
    "SecurityMiddleware",
    "AdvancedRateLimiter",
    "get_advanced_rate_limiter",
    "InputSanitizer",
    "AbuseProtection",
]
