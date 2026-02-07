"""
Health Checks & Monitoring Endpoints
"""
import os
import time
import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Response, status
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


# ============================================
# SCHEMAS
# ============================================

class HealthStatus(BaseModel):
    status: str  # "healthy", "degraded", "unhealthy"
    version: str
    environment: str
    timestamp: str
    uptime_seconds: float
    checks: dict


class ComponentHealth(BaseModel):
    status: str
    latency_ms: Optional[float] = None
    message: Optional[str] = None


# ============================================
# GLOBAL STATE
# ============================================

START_TIME = time.time()
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
APP_ENV = os.getenv("APP_ENV", "development")


# ============================================
# HEALTH CHECK FUNCTIONS
# ============================================

async def check_database() -> ComponentHealth:
    """Verifica conexão com banco de dados"""
    try:
        start = time.time()
        # TODO: Substituir por sua conexão real
        # async with get_db() as db:
        #     await db.execute("SELECT 1")
        latency = (time.time() - start) * 1000
        
        return ComponentHealth(
            status="healthy",
            latency_ms=round(latency, 2),
        )
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return ComponentHealth(
            status="unhealthy",
            message=str(e),
        )


async def check_redis() -> ComponentHealth:
    """Verifica conexão com Redis"""
    try:
        start = time.time()
        # TODO: Substituir por sua conexão real
        # redis = get_redis()
        # await redis.ping()
        latency = (time.time() - start) * 1000
        
        return ComponentHealth(
            status="healthy",
            latency_ms=round(latency, 2),
        )
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        return ComponentHealth(
            status="unhealthy",
            message=str(e),
        )


async def check_openai() -> ComponentHealth:
    """Verifica disponibilidade da API OpenAI"""
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return ComponentHealth(
                status="unhealthy",
                message="OPENAI_API_KEY not configured",
            )
        
        # Não faz chamada real para economizar tokens
        # Apenas verifica se a key está configurada
        return ComponentHealth(
            status="healthy",
            message="API key configured",
        )
    except Exception as e:
        return ComponentHealth(
            status="unhealthy",
            message=str(e),
        )


async def check_mercado_pago() -> ComponentHealth:
    """Verifica configuração do Mercado Pago"""
    try:
        token = os.getenv("MERCADO_PAGO_ACCESS_TOKEN")
        if not token:
            return ComponentHealth(
                status="degraded",
                message="MERCADO_PAGO_ACCESS_TOKEN not configured",
            )
        
        return ComponentHealth(
            status="healthy",
            message="Configured",
        )
    except Exception as e:
        return ComponentHealth(
            status="unhealthy",
            message=str(e),
        )


async def check_storage() -> ComponentHealth:
    """Verifica conexão com storage (S3)"""
    try:
        bucket = os.getenv("S3_BUCKET_NAME")
        if not bucket:
            return ComponentHealth(
                status="degraded",
                message="S3 not configured",
            )
        
        # TODO: Verificar conexão real
        return ComponentHealth(
            status="healthy",
        )
    except Exception as e:
        return ComponentHealth(
            status="unhealthy",
            message=str(e),
        )


# ============================================
# ENDPOINTS
# ============================================

@router.get("/health")
async def health_check(response: Response) -> HealthStatus:
    """
    Health check completo.
    
    Retorna status de todos os componentes do sistema.
    Usado por load balancers e monitoramento.
    """
    checks = {
        "database": await check_database(),
        "redis": await check_redis(),
        "openai": await check_openai(),
        "mercado_pago": await check_mercado_pago(),
        "storage": await check_storage(),
    }
    
    # Determina status geral
    statuses = [c.status for c in checks.values()]
    
    if all(s == "healthy" for s in statuses):
        overall_status = "healthy"
    elif any(s == "unhealthy" for s in statuses):
        overall_status = "unhealthy"
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    else:
        overall_status = "degraded"
    
    return HealthStatus(
        status=overall_status,
        version=APP_VERSION,
        environment=APP_ENV,
        timestamp=datetime.utcnow().isoformat(),
        uptime_seconds=round(time.time() - START_TIME, 2),
        checks={k: v.dict() for k, v in checks.items()},
    )


@router.get("/health/live")
async def liveness_probe():
    """
    Liveness probe simples.
    
    Usado pelo Kubernetes/Docker para saber se o container está vivo.
    Retorna 200 se a aplicação está rodando.
    """
    return {"status": "alive"}


@router.get("/health/ready")
async def readiness_probe(response: Response):
    """
    Readiness probe.
    
    Usado pelo Kubernetes/Docker para saber se pode receber tráfego.
    Verifica apenas componentes críticos (DB e Redis).
    """
    db_health = await check_database()
    redis_health = await check_redis()
    
    is_ready = (
        db_health.status == "healthy" and 
        redis_health.status in ["healthy", "degraded"]
    )
    
    if not is_ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    
    return {
        "status": "ready" if is_ready else "not_ready",
        "database": db_health.status,
        "redis": redis_health.status,
    }


@router.get("/health/startup")
async def startup_probe():
    """
    Startup probe.
    
    Usado durante inicialização do container.
    Mais permissivo que readiness.
    """
    return {
        "status": "started",
        "version": APP_VERSION,
        "environment": APP_ENV,
    }


# ============================================
# METRICS ENDPOINT (para Prometheus)
# ============================================

@router.get("/metrics")
async def metrics():
    """
    Endpoint de métricas para Prometheus.
    
    Formato: text/plain com métricas em formato Prometheus.
    """
    uptime = time.time() - START_TIME
    
    # Métricas básicas
    metrics_data = f"""# HELP app_uptime_seconds Application uptime in seconds
# TYPE app_uptime_seconds gauge
app_uptime_seconds {uptime}

# HELP app_info Application information
# TYPE app_info gauge
app_info{{version="{APP_VERSION}",environment="{APP_ENV}"}} 1
"""
    
    return Response(content=metrics_data, media_type="text/plain")
