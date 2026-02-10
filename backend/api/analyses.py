"""
Analysis endpoints - CRUD e execução.
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from database import get_db
from security.auth import get_tenant_context, TenantContext
from services.analysis_service import AnalysisService
from services.billing_service import BillingService
from middleware.rate_limiter import get_rate_limiter
from api.schemas import (
    AnalysisCreate, AnalysisResponse, AnalysisDetailResponse,
    AnalysisListResponse
)

router = APIRouter(prefix="/analyses", tags=["Analyses"])


def get_plan_rate_limit(plan: str) -> str:
    """Retorna rate limit baseado no plano."""
    limits = {
        "free": "10/hour",
        "pro": "60/hour",
        "enterprise": "300/hour"
    }
    return limits.get(plan, "10/hour")


@router.post("", response_model=AnalysisResponse, status_code=status.HTTP_201_CREATED)
async def create_analysis(
    data: AnalysisCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context)
):
    """
    Cria nova análise e inicia processamento em background.
    """
    # Rate limiting por plano
    limiter = get_rate_limiter()
    allowed, headers = limiter.check_rate_limit(
        identifier=tenant.org_id,
        endpoint="create_analysis",
        limit=get_plan_rate_limit(tenant.plan)
    )
    
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Limite de requisições atingido. Tente novamente mais tarde.",
            headers=headers
        )
    
    analysis_service = AnalysisService(db)
    
    try:
        analysis = analysis_service.create_analysis(
            org_id=UUID(tenant.org_id),
            user_id=UUID(tenant.user_id),
            problem_description=data.problem_description,
            business_type=data.business_type,
            analysis_depth=data.analysis_depth
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=str(e)
        )
    
    # Executa análise em background
    # Em produção: usar Celery ou similar
    background_tasks.add_task(
        run_analysis_background,
        str(analysis.id),
        db
    )
    
    return AnalysisResponse(
        id=analysis.id,
        problem_description=analysis.problem_description,
        business_type=analysis.business_type,
        analysis_depth=analysis.analysis_depth,
        status=analysis.status.value,
        executive_summary=analysis.executive_summary,
        total_tokens=analysis.total_tokens,
        total_cost_usd=analysis.total_cost_usd,
        total_latency_ms=analysis.total_latency_ms,
        created_at=analysis.created_at,
        completed_at=analysis.completed_at
    )


def run_analysis_background(analysis_id: str, db: Session):
    """
    Executa análise em background.
    
    NOTA: Em produção, usar Celery com Redis como broker.
    """
    from database.connection import get_db_session
    
    with get_db_session() as session:
        analysis_service = AnalysisService(session)
        try:
            analysis_service.execute_analysis(UUID(analysis_id))
        except Exception as e:
            # Erro já é tratado no service
            print(f"Error executing analysis {analysis_id}: {e}")


@router.get("", response_model=AnalysisListResponse)
async def list_analyses(
    limit: int = 50,
    offset: int = 0,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context)
):
    """
    Lista análises da organização com paginação.
    """
    from database.models import AnalysisStatus
    
    analysis_service = AnalysisService(db)
    
    # Converte status string para enum
    status_enum = None
    if status:
        try:
            status_enum = AnalysisStatus(status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Status inválido: {status}"
            )
    
    analyses = analysis_service.list_analyses(
        org_id=UUID(tenant.org_id),
        limit=min(limit, 100),  # Max 100
        offset=offset,
        status=status_enum
    )
    
    total = analysis_service.count_analyses(UUID(tenant.org_id))
    
    return AnalysisListResponse(
        items=[
            AnalysisResponse(
                id=a.id,
                problem_description=a.problem_description,
                business_type=a.business_type,
                analysis_depth=a.analysis_depth,
                status=a.status.value,
                executive_summary=a.executive_summary,
                total_tokens=a.total_tokens,
                total_cost_usd=a.total_cost_usd,
                total_latency_ms=a.total_latency_ms,
                created_at=a.created_at,
                completed_at=a.completed_at
            )
            for a in analyses
        ],
        total=total,
        limit=limit,
        offset=offset
    )


@router.get("/{analysis_id}", response_model=AnalysisDetailResponse)
async def get_analysis(
    analysis_id: UUID,
    db: Session = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context)
):
    """
    Retorna detalhes de uma análise.
    """
    analysis_service = AnalysisService(db)
    
    analysis = analysis_service.get_analysis(
        analysis_id=analysis_id,
        org_id=UUID(tenant.org_id)
    )
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Análise não encontrada"
        )
    
    return AnalysisDetailResponse(
        id=analysis.id,
        problem_description=analysis.problem_description,
        business_type=analysis.business_type,
        analysis_depth=analysis.analysis_depth,
        status=analysis.status.value,
        executive_summary=analysis.executive_summary,
        results=analysis.results,
        error_message=analysis.error_message,
        total_tokens=analysis.total_tokens,
        total_cost_usd=analysis.total_cost_usd,
        total_latency_ms=analysis.total_latency_ms,
        created_at=analysis.created_at,
        completed_at=analysis.completed_at
    )


@router.delete("/{analysis_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_analysis(
    analysis_id: UUID,
    db: Session = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context)
):
    """
    Deleta uma análise.
    """
    analysis_service = AnalysisService(db)
    
    deleted = analysis_service.delete_analysis(
        analysis_id=analysis_id,
        org_id=UUID(tenant.org_id)
    )
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Análise não encontrada"
        )


@router.post("/{analysis_id}/export/{format}")
async def export_analysis(
    analysis_id: UUID,
    format: str,
    db: Session = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context)
):
    """
    Exporta análise em formato específico.
    Requer plano Pro ou Enterprise.
    """
    # Verifica permissão de export
    billing_service = BillingService(db)
    can_export, error_msg = billing_service.check_can_export(UUID(tenant.org_id))
    
    if not can_export:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=error_msg
        )
    
    if format not in ["pdf", "pptx", "markdown"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato inválido. Use: pdf, pptx, markdown"
        )
    
    analysis_service = AnalysisService(db)
    analysis = analysis_service.get_analysis(analysis_id, UUID(tenant.org_id))
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Análise não encontrada"
        )
    
    # Importa exporters
    from services.exporter import AnalysisExporter
    from fastapi.responses import Response
    
    analysis_data = {
        "problem": analysis.problem_description,
        "business_type": analysis.business_type,
        "timestamp": analysis.created_at,
        "results": analysis.results or {}
    }
    
    if format == "markdown":
        content = AnalysisExporter.to_markdown(analysis_data)
        return Response(
            content=content,
            media_type="text/markdown",
            headers={"Content-Disposition": f"attachment; filename=analysis-{analysis_id}.md"}
        )
    
    elif format == "pdf":
        content = AnalysisExporter.to_pdf(analysis_data, "temp.pdf")
        return Response(
            content=content,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=analysis-{analysis_id}.pdf"}
        )
    
    elif format == "pptx":
        content = AnalysisExporter.to_ppt(analysis_data, "temp.pptx")
        return Response(
            content=content,
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            headers={"Content-Disposition": f"attachment; filename=analysis-{analysis_id}.pptx"}
        )
