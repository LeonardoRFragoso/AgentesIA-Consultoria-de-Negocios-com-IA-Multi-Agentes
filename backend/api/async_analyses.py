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

from security.auth import get_tenant_context, TenantContext
from services.async_analysis_service import AsyncAnalysisService

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
    selected_agents: Optional[list] = Field(
        default=None,
        description="Agentes a usar (Free: escolhe 2, Pro/Enterprise: todos). Opções: analyst, commercial, financial, market"
    )


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

@router.post("", response_model=AsyncAnalysisResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_async_analysis(
    data: AsyncAnalysisCreate,
    tenant: TenantContext = Depends(get_tenant_context)
):
    """
    Cria análise para processamento assíncrono.
    
    NÃO BLOQUEIA - retorna imediatamente com task_id.
    
    Se análise similar já foi processada e use_cache=True,
    retorna resultado do cache instantaneamente.
    
    **Agentes por plano:**
    - Free: escolhe até 2 agentes (+ reviewer automático)
    - Pro/Enterprise: todos os 5 agentes
    
    Returns:
        - analysis_id: ID da análise no banco
        - task_id: ID da task na fila (para polling)
        - status: "pending" | "cached"
        - cached: Se veio do cache
    """
    from database import get_db_session
    from services.billing_service import BillingService
    from uuid import UUID
    
    # Valida agentes selecionados baseado no plano
    with get_db_session() as db:
        billing = BillingService(db)
        selected = data.selected_agents or ["analyst", "commercial"]  # Default para Free
        
        valid, error_msg, agents_to_use = billing.validate_agents(
            UUID(tenant.org_id), 
            selected
        )
        
        if not valid:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=error_msg
            )
    
    service = AsyncAnalysisService(tenant.org_id, tenant.user_id)
    
    result = service.create_analysis(
        problem_description=data.problem_description,
        business_type=data.business_type,
        analysis_depth=data.analysis_depth,
        use_cache=data.use_cache,
        selected_agents=agents_to_use,
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
    
    from infrastructure.cache import get_cache
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
    
    from infrastructure.queue import get_queue
    queue = get_queue()
    
    if hasattr(queue, 'get_queue_stats'):
        return queue.get_queue_stats()
    
    return {"message": "Queue stats not available"}


# =============================================================================
# REFINE ENDPOINT
# =============================================================================

class RefineRequest(BaseModel):
    """Request para refinar análise."""
    analysis_id: str
    message: str
    context: dict = {}


@router.post("/refine")
async def refine_analysis(
    request: RefineRequest,
    tenant: TenantContext = Depends(get_tenant_context)
):
    """
    Refina análise com perguntas de follow-up.
    
    Limites por plano:
    - Free: 3 perguntas por análise
    - Pro: 20 perguntas por análise
    - Enterprise: Ilimitado
    """
    import os
    
    service = AsyncAnalysisService(tenant.org_id, tenant.user_id)
    analysis = service.get_analysis(request.analysis_id)
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Análise não encontrada"
        )
    
    # TODO: Implementar verificação de limite de refino por plano
    # Por ora, permite refino sem limite
    
    try:
        import anthropic
        
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="API key não configurada"
            )
        
        client = anthropic.Anthropic(api_key=api_key)
        
        # Monta contexto da análise anterior
        context_text = ""
        if analysis.get("results"):
            for agent, content in analysis["results"].items():
                if content:
                    context_text += f"\n\n### {agent.upper()}:\n{content}"
        
        if analysis.get("executive_summary"):
            context_text += f"\n\n### SUMÁRIO EXECUTIVO:\n{analysis['executive_summary']}"
        
        # Chama API
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[
                {
                    "role": "user",
                    "content": f"""Com base na análise anterior, responda à seguinte pergunta de follow-up.

CONTEXTO DA ANÁLISE:
{context_text}

PERGUNTA DO USUÁRIO:
{request.message}

Responda de forma clara, objetiva e acionável."""
                }
            ]
        )
        
        response_text = message.content[0].text if message.content else "Não foi possível gerar resposta."
        
        return {
            "response": response_text,
            "usage": {
                "used": 1,
                "limit": 3,  # TODO: buscar do plano
                "remaining": 2
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar pergunta: {str(e)}"
        )


# =============================================================================
# EXPORT ENDPOINT
# =============================================================================

@router.get("/{analysis_id}/export/{format}")
async def export_analysis(
    analysis_id: str,
    format: str,
    tenant: TenantContext = Depends(get_tenant_context)
):
    """
    Exporta análise em formato específico.
    
    Formatos disponíveis por plano:
    - Free: markdown
    - Pro: markdown, pdf, pptx
    - Enterprise: markdown, pdf, pptx, xlsx, docx
    """
    from database import get_db_session
    from services.billing_service import BillingService
    from uuid import UUID
    
    # Verifica permissão de export
    with get_db_session() as db:
        billing_service = BillingService(db)
        can_export, error_msg = billing_service.check_can_export(UUID(tenant.org_id))
        
        if not can_export:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=error_msg
            )
    
    # Busca análise
    service = AsyncAnalysisService(tenant.org_id, tenant.user_id)
    analysis = service.get_analysis(analysis_id)
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Análise não encontrada"
        )
    
    # Importa exporters
    from services.exporter import AnalysisExporter
    from fastapi.responses import Response
    
    analysis_data = {
        "problem_description": analysis.get("problem_description", ""),
        "executive_summary": analysis.get("executive_summary", ""),
        "results": analysis.get("results", {}),
    }
    
    if format == "markdown":
        content = AnalysisExporter.to_markdown(analysis_data)
        return Response(
            content=content,
            media_type="text/markdown",
            headers={"Content-Disposition": f"attachment; filename=analise-{analysis_id}.md"}
        )
    
    elif format == "pdf":
        content = AnalysisExporter.to_pdf(analysis_data, "temp.pdf")
        return Response(
            content=content,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=analise-{analysis_id}.pdf"}
        )
    
    elif format == "pptx":
        content = AnalysisExporter.to_ppt(analysis_data, "temp.pptx")
        return Response(
            content=content,
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            headers={"Content-Disposition": f"attachment; filename=analise-{analysis_id}.pptx"}
        )
    
    elif format == "docx":
        content = AnalysisExporter.to_docx(analysis_data, "temp.docx")
        return Response(
            content=content,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f"attachment; filename=analise-{analysis_id}.docx"}
        )
    
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Formato não suportado: {format}"
        )
