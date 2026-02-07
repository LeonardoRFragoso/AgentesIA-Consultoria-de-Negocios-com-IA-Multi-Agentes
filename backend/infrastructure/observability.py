"""
Observability - Logs, Métricas e Error Tracking para Produção

Features:
- Logs estruturados em JSON
- Métricas de requests (count, duration, errors)
- Integração com Sentry
- Identificação por tenant em todos os logs
- Context propagation
"""

import json
import logging
import sys
import time
import traceback
from contextvars import ContextVar
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional, Dict, Any, Callable
from functools import wraps
import uuid

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


# =============================================================================
# CONTEXT VARS (Thread-safe context propagation)
# =============================================================================

# Contexto atual da request
request_context: ContextVar[Dict[str, Any]] = ContextVar("request_context", default={})


def set_context(**kwargs):
    """Define contexto para a request atual."""
    ctx = request_context.get().copy()
    ctx.update(kwargs)
    request_context.set(ctx)


def get_context() -> Dict[str, Any]:
    """Retorna contexto atual."""
    return request_context.get()


def clear_context():
    """Limpa contexto."""
    request_context.set({})


# =============================================================================
# STRUCTURED JSON LOGGER
# =============================================================================

class JSONFormatter(logging.Formatter):
    """
    Formatter que gera logs em JSON estruturado.
    
    Exemplo de output:
    {
        "timestamp": "2026-02-06T21:52:00.123Z",
        "level": "INFO",
        "logger": "backend.api.auth",
        "message": "User logged in",
        "request_id": "abc123",
        "tenant_id": "org-456",
        "user_id": "user-789",
        "duration_ms": 45.2,
        "extra": {"email": "user@example.com"}
    }
    """
    
    def format(self, record: logging.LogRecord) -> str:
        # Base log entry
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Adiciona contexto da request
        ctx = get_context()
        if ctx:
            log_entry.update({
                "request_id": ctx.get("request_id"),
                "tenant_id": ctx.get("org_id"),
                "user_id": ctx.get("user_id"),
            })
        
        # Adiciona extras do record
        if hasattr(record, "extra") and record.extra:
            log_entry["extra"] = record.extra
        
        # Adiciona exception info se presente
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": traceback.format_exception(*record.exc_info),
            }
        
        # Remove valores None
        log_entry = {k: v for k, v in log_entry.items() if v is not None}
        
        return json.dumps(log_entry, default=str, ensure_ascii=False)


class TenantLogger(logging.LoggerAdapter):
    """
    Logger adapter que adiciona contexto de tenant automaticamente.
    
    Uso:
        logger = get_logger(__name__)
        logger.info("User action", extra={"action": "login"})
    """
    
    def process(self, msg, kwargs):
        # Injeta contexto nos extras
        extra = kwargs.get("extra", {})
        ctx = get_context()
        
        if ctx:
            extra.update({
                "request_id": ctx.get("request_id"),
                "tenant_id": ctx.get("org_id"),
                "user_id": ctx.get("user_id"),
            })
        
        kwargs["extra"] = extra
        return msg, kwargs


def setup_logging(
    level: str = "INFO",
    json_format: bool = True,
    include_timestamp: bool = True
):
    """
    Configura logging para produção.
    
    Args:
        level: Nível de log (DEBUG, INFO, WARNING, ERROR)
        json_format: Se True, usa JSON. Se False, usa formato legível.
        include_timestamp: Inclui timestamp nos logs
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # Remove handlers existentes
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Handler para stdout
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, level.upper()))
    
    if json_format:
        handler.setFormatter(JSONFormatter())
    else:
        format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        handler.setFormatter(logging.Formatter(format_str))
    
    root_logger.addHandler(handler)
    
    # Silencia logs verbosos de bibliotecas
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name: str) -> TenantLogger:
    """
    Retorna logger com suporte a tenant context.
    
    Uso:
        logger = get_logger(__name__)
        logger.info("Something happened", extra={"key": "value"})
    """
    logger = logging.getLogger(name)
    return TenantLogger(logger, {})


# =============================================================================
# METRICS COLLECTOR
# =============================================================================

@dataclass
class RequestMetrics:
    """Métricas de uma request."""
    method: str
    path: str
    status_code: int
    duration_ms: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    tenant_id: Optional[str] = None
    user_id: Optional[str] = None
    error: Optional[str] = None


class MetricsCollector:
    """
    Coletor de métricas em memória.
    
    Em produção, integre com:
    - Prometheus
    - DataDog
    - CloudWatch
    - New Relic
    """
    
    def __init__(self, max_entries: int = 10000):
        self._requests: list = []
        self._max_entries = max_entries
        self._counters: Dict[str, int] = {
            "requests_total": 0,
            "requests_success": 0,
            "requests_error": 0,
            "requests_4xx": 0,
            "requests_5xx": 0,
        }
        self._histograms: Dict[str, list] = {
            "request_duration_ms": [],
        }
    
    def record_request(self, metrics: RequestMetrics):
        """Registra métricas de uma request."""
        self._counters["requests_total"] += 1
        
        if 200 <= metrics.status_code < 400:
            self._counters["requests_success"] += 1
        elif 400 <= metrics.status_code < 500:
            self._counters["requests_4xx"] += 1
        elif metrics.status_code >= 500:
            self._counters["requests_5xx"] += 1
            self._counters["requests_error"] += 1
        
        # Histogram de duração
        self._histograms["request_duration_ms"].append(metrics.duration_ms)
        if len(self._histograms["request_duration_ms"]) > self._max_entries:
            self._histograms["request_duration_ms"] = self._histograms["request_duration_ms"][-self._max_entries:]
        
        # Armazena request
        self._requests.append(asdict(metrics))
        if len(self._requests) > self._max_entries:
            self._requests = self._requests[-self._max_entries:]
    
    def get_summary(self) -> Dict[str, Any]:
        """Retorna resumo das métricas."""
        durations = self._histograms["request_duration_ms"]
        
        summary = {
            "counters": self._counters.copy(),
            "duration_stats": {},
        }
        
        if durations:
            sorted_durations = sorted(durations)
            summary["duration_stats"] = {
                "count": len(durations),
                "avg_ms": sum(durations) / len(durations),
                "min_ms": min(durations),
                "max_ms": max(durations),
                "p50_ms": sorted_durations[len(sorted_durations) // 2],
                "p95_ms": sorted_durations[int(len(sorted_durations) * 0.95)],
                "p99_ms": sorted_durations[int(len(sorted_durations) * 0.99)],
            }
        
        # Error rate
        total = self._counters["requests_total"]
        if total > 0:
            summary["error_rate"] = self._counters["requests_error"] / total
        else:
            summary["error_rate"] = 0.0
        
        return summary
    
    def get_recent_errors(self, limit: int = 20) -> list:
        """Retorna erros recentes."""
        errors = [r for r in self._requests if r.get("error")]
        return errors[-limit:]


# Instância global
_metrics = MetricsCollector()


def get_metrics() -> MetricsCollector:
    return _metrics


# =============================================================================
# SENTRY INTEGRATION
# =============================================================================

def init_sentry(
    dsn: str,
    environment: str = "production",
    release: Optional[str] = None,
    traces_sample_rate: float = 0.1
):
    """
    Inicializa Sentry para error tracking.
    
    Args:
        dsn: Sentry DSN (de SENTRY_DSN env var)
        environment: production, staging, development
        release: Versão do app (ex: "1.0.0")
        traces_sample_rate: % de requests para tracing (0.0 a 1.0)
    """
    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
        from sentry_sdk.integrations.redis import RedisIntegration
        from sentry_sdk.integrations.logging import LoggingIntegration
        
        sentry_sdk.init(
            dsn=dsn,
            environment=environment,
            release=release,
            traces_sample_rate=traces_sample_rate,
            integrations=[
                FastApiIntegration(transaction_style="endpoint"),
                SqlalchemyIntegration(),
                RedisIntegration(),
                LoggingIntegration(
                    level=logging.WARNING,
                    event_level=logging.ERROR,
                ),
            ],
            # Filtra dados sensíveis
            before_send=_filter_sensitive_data,
        )
        
        logging.getLogger(__name__).info("Sentry initialized", extra={
            "environment": environment,
            "traces_sample_rate": traces_sample_rate,
        })
        
    except ImportError:
        logging.getLogger(__name__).warning("Sentry SDK not installed")
    except Exception as e:
        logging.getLogger(__name__).error(f"Failed to init Sentry: {e}")


def _filter_sensitive_data(event, hint):
    """Remove dados sensíveis antes de enviar ao Sentry."""
    # Remove passwords
    if "request" in event and "data" in event["request"]:
        data = event["request"]["data"]
        if isinstance(data, dict):
            for key in ["password", "password_hash", "token", "api_key", "secret"]:
                if key in data:
                    data[key] = "[FILTERED]"
    
    # Remove headers sensíveis
    if "request" in event and "headers" in event["request"]:
        headers = event["request"]["headers"]
        if isinstance(headers, dict):
            for key in ["authorization", "cookie", "x-api-key"]:
                if key in headers:
                    headers[key] = "[FILTERED]"
    
    return event


def capture_exception(error: Exception, extra: Optional[Dict] = None):
    """
    Captura exceção no Sentry com contexto.
    
    Uso:
        try:
            ...
        except Exception as e:
            capture_exception(e, extra={"user_id": "123"})
            raise
    """
    try:
        import sentry_sdk
        
        # Adiciona contexto
        ctx = get_context()
        with sentry_sdk.push_scope() as scope:
            if ctx:
                scope.set_tag("tenant_id", ctx.get("org_id"))
                scope.set_user({"id": ctx.get("user_id")})
            
            if extra:
                for key, value in extra.items():
                    scope.set_extra(key, value)
            
            sentry_sdk.capture_exception(error)
            
    except ImportError:
        pass


def set_sentry_user(user_id: str, email: Optional[str] = None, org_id: Optional[str] = None):
    """Define usuário atual no Sentry."""
    try:
        import sentry_sdk
        sentry_sdk.set_user({
            "id": user_id,
            "email": email,
            "org_id": org_id,
        })
        sentry_sdk.set_tag("tenant_id", org_id)
    except ImportError:
        pass


# =============================================================================
# OBSERVABILITY MIDDLEWARE
# =============================================================================

class ObservabilityMiddleware(BaseHTTPMiddleware):
    """
    Middleware que adiciona observabilidade completa.
    
    - Gera request_id único
    - Extrai tenant do token JWT
    - Mede duração
    - Registra métricas
    - Loga requests
    """
    
    def __init__(self, app, logger_name: str = "backend.requests"):
        super().__init__(app)
        self.logger = get_logger(logger_name)
    
    async def dispatch(self, request: Request, call_next) -> Response:
        # 1. Gera request ID
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())[:8]
        
        # 2. Extrai tenant do token (se presente)
        org_id = None
        user_id = None
        
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            try:
                import jwt
                token = auth_header.split(" ")[1]
                # Decode sem verificar (só para extrair claims)
                payload = jwt.decode(token, options={"verify_signature": False})
                org_id = payload.get("org_id")
                user_id = payload.get("sub")
            except Exception:
                pass
        
        # 3. Define contexto
        set_context(
            request_id=request_id,
            org_id=org_id,
            user_id=user_id,
            path=request.url.path,
            method=request.method,
        )
        
        # 4. Define user no Sentry
        if user_id:
            set_sentry_user(user_id, org_id=org_id)
        
        # 5. Mede duração
        start_time = time.perf_counter()
        error_msg = None
        status_code = 500
        
        try:
            response = await call_next(request)
            status_code = response.status_code
            
            # Adiciona request_id no header de resposta
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            error_msg = str(e)
            capture_exception(e)
            raise
            
        finally:
            duration_ms = (time.perf_counter() - start_time) * 1000
            
            # 6. Registra métricas
            metrics = RequestMetrics(
                method=request.method,
                path=request.url.path,
                status_code=status_code,
                duration_ms=duration_ms,
                tenant_id=org_id,
                user_id=user_id,
                error=error_msg,
            )
            get_metrics().record_request(metrics)
            
            # 7. Log estruturado
            log_level = logging.INFO if status_code < 400 else logging.WARNING
            if status_code >= 500:
                log_level = logging.ERROR
            
            self.logger.log(
                log_level,
                f"{request.method} {request.url.path} {status_code}",
                extra={
                    "http": {
                        "method": request.method,
                        "path": request.url.path,
                        "status_code": status_code,
                        "duration_ms": round(duration_ms, 2),
                        "client_ip": request.client.host if request.client else None,
                    },
                    "error": error_msg,
                }
            )
            
            # 8. Limpa contexto
            clear_context()


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Context
    "set_context",
    "get_context",
    "clear_context",
    # Logging
    "setup_logging",
    "get_logger",
    "JSONFormatter",
    "TenantLogger",
    # Metrics
    "MetricsCollector",
    "RequestMetrics",
    "get_metrics",
    # Sentry
    "init_sentry",
    "capture_exception",
    "set_sentry_user",
    # Middleware
    "ObservabilityMiddleware",
]
