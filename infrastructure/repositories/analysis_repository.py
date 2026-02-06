"""Repository para análises."""

from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc

from infrastructure.database.models import Analysis, AgentOutput
from .base_repository import BaseRepository


class AnalysisRepository(BaseRepository[Analysis]):
    """Repositório para gerenciar análises."""
    
    def __init__(self, session: Session):
        """Inicializa repositório de análises."""
        super().__init__(session, Analysis)
    
    def get_by_execution_id(self, execution_id: str) -> Optional[Analysis]:
        """Obtém análise por execution_id."""
        return self.session.query(Analysis).filter(
            Analysis.execution_id == execution_id
        ).first()
    
    def get_by_user(self, user_id: str, limit: int = 50) -> List[Analysis]:
        """Obtém análises de um usuário, ordenadas por data (mais recentes primeiro)."""
        return self.session.query(Analysis).filter(
            Analysis.user_id == user_id
        ).order_by(desc(Analysis.created_at)).limit(limit).all()
    
    def get_by_workspace(self, workspace_id: str, limit: int = 50) -> List[Analysis]:
        """Obtém análises de um workspace."""
        return self.session.query(Analysis).filter(
            Analysis.workspace_id == workspace_id
        ).order_by(desc(Analysis.created_at)).limit(limit).all()
    
    def get_recent(self, days: int = 30, limit: int = 100) -> List[Analysis]:
        """Obtém análises recentes."""
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return self.session.query(Analysis).filter(
            Analysis.created_at >= cutoff_date
        ).order_by(desc(Analysis.created_at)).limit(limit).all()
    
    def search_by_problem(self, keyword: str, limit: int = 20) -> List[Analysis]:
        """Busca análises por palavra-chave no problema."""
        return self.session.query(Analysis).filter(
            Analysis.problem_description.ilike(f"%{keyword}%")
        ).order_by(desc(Analysis.created_at)).limit(limit).all()
    
    def get_statistics(self, user_id: str) -> dict:
        """Retorna estatísticas de análises do usuário."""
        analyses = self.session.query(Analysis).filter(
            Analysis.user_id == user_id
        ).all()
        
        if not analyses:
            return {
                "total_analyses": 0,
                "total_cost_usd": 0.0,
                "total_tokens": 0,
                "avg_latency_ms": 0.0,
            }
        
        total_cost = sum(a.total_cost_usd for a in analyses)
        total_tokens = sum(a.total_tokens for a in analyses)
        avg_latency = sum(a.total_latency_ms for a in analyses) / len(analyses)
        
        return {
            "total_analyses": len(analyses),
            "total_cost_usd": round(total_cost, 4),
            "total_tokens": total_tokens,
            "avg_latency_ms": round(avg_latency, 2),
        }
    
    def save_from_context(self, context, user_id: str = "default", workspace_id: str = "default") -> Analysis:
        """
        Salva análise a partir de ExecutionContext.
        
        Args:
            context: ExecutionContext com resultados
            user_id: ID do usuário
            workspace_id: ID do workspace
        
        Returns:
            Analysis persistida
        """
        analysis = Analysis(
            execution_id=context.execution_id,
            user_id=user_id,
            workspace_id=workspace_id,
            problem_description=context.problem_description,
            business_type=context.business_type,
            analysis_depth=context.analysis_depth,
            total_latency_ms=context.get_total_latency_ms(),
            total_tokens=context.get_total_tokens(),
            total_cost_usd=context.get_total_cost(),
            status="completed",
        )
        
        # Salva análise
        analysis = self.create(analysis)
        
        # Salva outputs de agentes
        for agent_name, metadata in context.metadata.items():
            agent_output = AgentOutput(
                execution_id=analysis.execution_id,
                agent_name=agent_name,
                output=context.get_agent_output(agent_name) or "",
                latency_ms=metadata.latency_ms,
                input_tokens=metadata.input_tokens,
                output_tokens=metadata.output_tokens,
                total_tokens=metadata.total_tokens,
                cost_usd=metadata.cost_usd,
                status=metadata.status.value,
                error_message=metadata.error,
                started_at=metadata.start_time,
                completed_at=metadata.end_time,
            )
            self.session.add(agent_output)
        
        self.session.commit()
        return analysis
