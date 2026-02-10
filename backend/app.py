"""
FastAPI Application - Backend SaaS
Versão de produção com segurança e multi-tenant.

HARDENING APLICADO:
- CORS restritivo (sem wildcard)
- Rate limiting por IP e usuário
- Validação rigorosa de inputs
- Headers de segurança
- Proteção contra abuso
"""

from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging
import platform

from config import get_settings
from database import init_db
from api import auth_router, analyses_router, async_analyses_router, billing_router, users_router
from api.schemas import HealthResponse
from middleware.security import SecurityMiddleware, SecurityConfig
from infrastructure.observability import (
    setup_logging,
    get_logger,
    get_metrics,
    init_sentry,
    ObservabilityMiddleware,
)

# Configuração de logging estruturado
settings = get_settings()
setup_logging(
    level=getattr(settings, 'LOG_LEVEL', 'INFO'),
    json_format=settings.is_production(),  # JSON em produção, legível em dev
)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle hooks - startup e shutdown."""
    # Startup
    logger.info("Starting application...")
    settings = get_settings()
    
    # Inicializa banco de dados
    init_db()
    logger.info(f"Database initialized: {settings.DATABASE_URL.split('@')[-1]}")
    
    # Inicializa Cache (Redis ou memória)
    from infrastructure.cache import init_cache
    redis_url = getattr(settings, 'REDIS_URL', None)
    cache = init_cache(redis_url)
    logger.info(f"Cache initialized: {'Redis' if cache.is_redis_available else 'Memory'}")
    
    # Inicializa Fila de Tasks
    from infrastructure.queue import init_queue
    from services.async_analysis_service import register_task_handlers
    queue = init_queue(redis_url, start_worker=True)
    register_task_handlers()
    logger.info("Task queue initialized")
    
    # Inicializa Sentry se configurado
    if settings.SENTRY_DSN:
        init_sentry(
            dsn=settings.SENTRY_DSN,
            environment=settings.ENVIRONMENT,
            release=settings.APP_VERSION,
            traces_sample_rate=0.1,
        )
        logger.info("Sentry initialized")
    
    logger.info(f"Application started in {settings.ENVIRONMENT} mode")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    from database.connection import close_db
    close_db()


# Cria aplicação
settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API SaaS para análise estratégica com múltiplos agentes de IA",
    docs_url="/docs" if not settings.is_production() else None,
    redoc_url="/redoc" if not settings.is_production() else None,
    lifespan=lifespan
)


# =============================================================================
# MIDDLEWARE (ordem importa - último adicionado executa primeiro)
# =============================================================================

# 0. Observability Middleware (logs estruturados, métricas, request_id)
app.add_middleware(ObservabilityMiddleware)

# 1. Security Middleware (rate limiting, headers, proteção)
# VULNERABILIDADE CORRIGIDA: Antes não havia rate limiting por IP
app.add_middleware(SecurityMiddleware, config=SecurityConfig())

# 2. CORS - Configuração RESTRITIVA
# VULNERABILIDADE CORRIGIDA: allow_origins=["*"] era possível
# Agora: apenas origens explícitas são permitidas
def get_cors_origins():
    """Retorna origens CORS validadas - NUNCA permite wildcard."""
    origins = list(settings.CORS_ORIGINS) if settings.CORS_ORIGINS else []
    
    # Domínios conhecidos que devem sempre ser permitidos em produção
    KNOWN_PRODUCTION_ORIGINS = [
        "https://agentes-ia-consultoria-de-negocios.vercel.app",
    ]
    
    # Adiciona domínios conhecidos se não estiverem na lista
    for known_origin in KNOWN_PRODUCTION_ORIGINS:
        if known_origin not in origins:
            origins.append(known_origin)
    
    # DEBUG: Log das origens configuradas
    logger.info(f"CORS_ORIGINS configured: {origins}")
    
    # CRÍTICO: Bloqueia wildcard em produção
    if settings.is_production():
        if "*" in origins:
            logger.error("SECURITY: Wildcard CORS não permitido em produção!")
            origins = [o for o in origins if o != "*"]
    
    final_origins = [o for o in origins if o != "*"]
    logger.info(f"CORS_ORIGINS final: {final_origins}")
    return final_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    # RESTRITIVO: apenas métodos necessários
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    # RESTRITIVO: apenas headers necessários
    allow_headers=[
        "Authorization",
        "Content-Type",
        "X-Request-ID",
        "Accept",
        "Accept-Language",
    ],
    expose_headers=[
        "X-RateLimit-Limit",
        "X-RateLimit-Remaining",
        "X-RateLimit-Reset",
        "Retry-After",
    ],
    max_age=600,  # Cache preflight por 10 min
)


# =============================================================================
# EXCEPTION HANDLERS
# =============================================================================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handler para erros de validação."""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "errors": errors
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handler global para exceções não tratadas."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    # Headers CORS para garantir que erros também tenham headers corretos
    origin = request.headers.get("origin", "")
    cors_headers = {}
    allowed_origins = get_cors_origins()
    if origin in allowed_origins:
        cors_headers = {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Credentials": "true",
        }
    
    # Em produção, não expor detalhes do erro
    if settings.is_production():
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
            headers=cors_headers
        )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": str(exc),
            "type": type(exc).__name__
        },
        headers=cors_headers
    )


# =============================================================================
# ROUTES
# =============================================================================

# Health check (público) - NÃO requer autenticação
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint para load balancers e monitoramento.
    
    Retorna:
    - status: healthy/unhealthy
    - version: versão da API
    - environment: ambiente atual
    - checks: status de dependências
    """
    checks = {
        "database": "unknown",
        "cache": "unknown",
    }
    
    # Verifica database
    try:
        from database import get_db_session
        from sqlalchemy import text
        with get_db_session() as db:
            db.execute(text("SELECT 1"))
            checks["database"] = "healthy"
    except Exception as e:
        checks["database"] = f"unhealthy: {str(e)[:50]}"
    
    # Verifica Redis (se configurado)
    try:
        from middleware.security import get_advanced_rate_limiter
        limiter = get_advanced_rate_limiter()
        if limiter:
            checks["cache"] = "healthy (memory)" 
    except Exception:
        checks["cache"] = "unavailable"
    
    # Status geral
    is_healthy = checks["database"] == "healthy"
    
    response = {
        "status": "healthy" if is_healthy else "unhealthy",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.utcnow().isoformat(),
        "checks": checks,
    }
    
    # Em produção, não expor detalhes de erro
    if settings.is_production() and not is_healthy:
        response["checks"] = {"status": "degraded"}
    
    status_code = 200 if is_healthy else 503
    return JSONResponse(content=response, status_code=status_code)


@app.get("/health/live", tags=["Health"])
async def liveness_check():
    """Liveness probe - apenas verifica se app está rodando."""
    return {"status": "alive"}


@app.get("/health/ready", tags=["Health"])
async def readiness_check():
    """Readiness probe - verifica se app está pronta para receber tráfego."""
    try:
        from database import get_db_session
        with get_db_session() as db:
            db.execute("SELECT 1")
        return {"status": "ready"}
    except Exception:
        return JSONResponse(
            content={"status": "not ready"},
            status_code=503
        )


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs" if not settings.is_production() else None,
        "health": "/health"
    }


@app.get("/metrics", tags=["Observability"])
async def metrics():
    """
    Métricas da aplicação.
    
    Em produção, proteja este endpoint ou integre com Prometheus.
    """
    metrics_data = get_metrics().get_summary()
    
    return {
        "application": {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
        },
        "metrics": metrics_data,
    }


@app.get("/metrics/errors", tags=["Observability"])
async def recent_errors():
    """Erros recentes (últimos 20)."""
    if settings.is_production():
        # Em produção, requer autenticação
        return {"message": "Use Sentry dashboard in production"}
    
    return get_metrics().get_recent_errors(limit=20)


# API Routes
app.include_router(auth_router, prefix="/api/v1")
app.include_router(analyses_router, prefix="/api/v1")
app.include_router(async_analyses_router, prefix="/api/v1/async")  # Processamento assíncrono
app.include_router(billing_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.is_development(),
        log_level="info"
    )
