"""
Async Analysis Endpoints - Processamento não-bloqueante

Endpoints:
- POST /analyses/async    → Cria análise, retorna task_id
- GET  /analyses/task/{id} → Status da task (polling)
- GET  /analyses/{id}     → Resultado final

FLUXO RECOMENDADO:
1. POST /analyses/async → {"task_id": "...", "analysis_id": "..."}
2. Polling: GET /analyses/task/{task_id} → {"status": "running"}
3. Quando status=completed: GET /analyses/{analysis_id}
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

from ..security.auth import get_tenant_context, TenantContext
from ..services.async_analysis_service import AsyncAnalysisService

router = APIRouter(prefix="/analyses", tags=["Async Analyses"])


# =============================================================================
# SCHEMAS
# =============================================================================

class AsyncAnalysisCreate(BaseModel):
    """Request para criar análise assíncrona."""
    problem_description: str = Field(..., min_length=10, max_length=10000)
    business_type: str = Field(default="B2B")
    analysis_depth: str = Field(default="Padrão")
    use_cache: bool = Field(default=True, description="Usar cache para análises repetidas")


class AsyncAnalysisResponse(BaseModel):
    """Response da criação de análise."""
    analysis_id: str
    task_id: Optional[str]
    status: str
    cached: bool
    message: str


class TaskStatusResponse(BaseModel):
    """Response do status da task."""
    task_id: str
    status: str
    progress: Optional[int] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    duration_ms: Optional[float] = None
    created_at: Optional[str] = None
    completed_at: Optional[str] = None


class AnalysisDetailResponse(BaseModel):
    """Response com detalhes da análise."""
    id: str
    problem_description: str
    business_type: str
    analysis_depth: str
    status: str
    executive_summary: Optional[str] = None
    results: Optional[Dict[str, Any]] = None
    total_tokens: int = 0
    total_cost_usd: float = 0.0
    total_latency_ms: float = 0.0
    created_at: Optional[str] = None
    completed_at: Optional[str] = None
    error_message: Optional[str] = None


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.post("/async", response_model=AsyncAnalysisResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_async_analysis(
    data: AsyncAnalysisCreate,
    tenant: TenantContext = Depends(get_tenant_context)
):
    """
    Cria análise para processamento assíncrono.
    
    NÃO BLOQUEIA - retorna imediatamente com task_id.
    
    Se análise similar já foi processada e use_cache=True,
    retorna resultado do cache instantaneamente.
    
    Returns:
        - analysis_id: ID da análise no banco
        - task_id: ID da task na fila (para polling)
        - status: "pending" | "cached"
        - cached: Se veio do cache
    """
    service = AsyncAnalysisService(tenant.org_id, tenant.user_id)
    
    result = service.create_analysis(
        problem_description=data.problem_description,
        business_type=data.business_type,
        analysis_depth=data.analysis_depth,
        use_cache=data.use_cache,
    )
    
    if result["cached"]:
        message = "Análise similar encontrada no cache"
    else:
        message = "Análise enfileirada para processamento"
    
    return AsyncAnalysisResponse(
        analysis_id=result["analysis_id"],
        task_id=result["task_id"],
        status=result["status"],
        cached=result["cached"],
        message=message,
    )


@router.get("/task/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(
    task_id: str,
    tenant: TenantContext = Depends(get_tenant_context)
):
    """
    Verifica status de uma task de análise.
    
    Use para polling até status ser "completed" ou "failed".
    
    Statuses possíveis:
    - pending: Aguardando na fila
    - running: Em processamento
    - completed: Finalizado com sucesso
    - failed: Falhou
    - cancelled: Cancelado
    """
    service = AsyncAnalysisService(tenant.org_id, tenant.user_id)
    
    status_info = service.get_task_status(task_id)
    
    if not status_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task não encontrada"
        )
    
    return TaskStatusResponse(
        task_id=task_id,
        status=status_info["status"],
        result=status_info.get("result"),
        error=status_info.get("error"),
        duration_ms=status_info.get("duration_ms"),
        created_at=status_info.get("created_at"),
        completed_at=status_info.get("completed_at"),
    )


@router.get("/{analysis_id}", response_model=AnalysisDetailResponse)
async def get_analysis(
    analysis_id: str,
    tenant: TenantContext = Depends(get_tenant_context)
):
    """
    Busca análise por ID.
    
    Usa cache para análises completadas.
    """
    service = AsyncAnalysisService(tenant.org_id, tenant.user_id)
    
    analysis = service.get_analysis(analysis_id)
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Análise não encontrada"
        )
    
    return AnalysisDetailResponse(**analysis)


@router.get("", response_model=Dict[str, Any])
async def list_analyses(
    limit: int = 20,
    offset: int = 0,
    status_filter: Optional[str] = None,
    tenant: TenantContext = Depends(get_tenant_context)
):
    """
    Lista análises da organização.
    
    Resultados são cacheados por 5 minutos.
    """
    service = AsyncAnalysisService(tenant.org_id, tenant.user_id)
    
    return service.list_analyses(
        limit=limit,
        offset=offset,
        status=status_filter,
    )


@router.delete("/{analysis_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_analysis(
    analysis_id: str,
    tenant: TenantContext = Depends(get_tenant_context)
):
    """
    Deleta análise.
    
    Invalida caches relacionados automaticamente.
    """
    service = AsyncAnalysisService(tenant.org_id, tenant.user_id)
    
    deleted = service.delete_analysis(analysis_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Análise não encontrada"
        )


# =============================================================================
# CACHE & QUEUE STATUS
# =============================================================================

@router.get("/system/cache-stats", tags=["System"])
async def get_cache_stats(
    tenant: TenantContext = Depends(get_tenant_context)
):
    """
    Estatísticas do cache (apenas admin).
    
    MONITORAMENTO DE FALHAS:
    - hit_rate baixo = cache ineficiente
    - errors alto = problemas de conexão Redis
    """
    if not tenant.is_admin():
        raise HTTPException(status_code=403, detail="Admin required")
    
    from ..infrastructure.cache import get_cache
    cache = get_cache()
    
    return cache.health_check()


@router.get("/system/queue-stats", tags=["System"])
async def get_queue_stats(
    tenant: TenantContext = Depends(get_tenant_context)
):
    """
    Estatísticas da fila (apenas admin).
    
    MONITORAMENTO DE FALHAS:
    - pending alto = workers lentos ou parados
    - failed alto = erros nos handlers
    """
    if not tenant.is_admin():
        raise HTTPException(status_code=403, detail="Admin required")
    
    from ..infrastructure.queue import get_queue
    queue = get_queue()
    
    if hasattr(queue, 'get_queue_stats'):
        return queue.get_queue_stats()
    
    return {"message": "Queue stats not available"}
