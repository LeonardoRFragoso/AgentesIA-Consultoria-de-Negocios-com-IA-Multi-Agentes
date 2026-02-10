"""
Analysis service - Execução e gerenciamento de análises.
"""

import asyncio
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session

from database.models import Analysis, AgentOutput, AnalysisStatus, Organization
from services.billing_service import BillingService


class AnalysisService:
    """
    Serviço de análise multi-agentes.
    
    Responsabilidades:
    - Criar análises
    - Executar orquestrador
    - Salvar resultados
    - Listar histórico com filtros
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.billing = BillingService(db)
    
    def create_analysis(
        self,
        org_id: UUID,
        user_id: UUID,
        problem_description: str,
        business_type: str = "B2B",
        analysis_depth: str = "Padrão"
    ) -> Analysis:
        """
        Cria nova análise.
        
        Não executa a análise - isso é feito em background.
        """
        # Verifica billing
        can_execute, error_msg = self.billing.check_can_execute(org_id)
        if not can_execute:
            raise ValueError(error_msg)
        
        # Cria análise
        analysis = Analysis(
            org_id=org_id,
            created_by=user_id,
            problem_description=problem_description,
            business_type=business_type,
            analysis_depth=analysis_depth,
            status=AnalysisStatus.PENDING,
        )
        self.db.add(analysis)
        self.db.commit()
        self.db.refresh(analysis)
        
        return analysis
    
    def execute_analysis(self, analysis_id: UUID) -> Analysis:
        """
        Executa análise usando o orquestrador multi-agentes.
        
        Em produção, isso seria um job assíncrono (Celery/RQ).
        """
        analysis = self.db.query(Analysis).filter(Analysis.id == analysis_id).first()
        
        if not analysis:
            raise ValueError("Análise não encontrada")
        
        if analysis.status != AnalysisStatus.PENDING:
            raise ValueError(f"Análise em status inválido: {analysis.status}")
        
        # Atualiza status
        analysis.status = AnalysisStatus.RUNNING
        analysis.started_at = datetime.utcnow()
        self.db.commit()
        
        try:
            # Importa o core
            from core.types import ExecutionContext
            from orchestrator import BusinessOrchestrator
            from agents import (
                AnalystAgent, CommercialAgent, FinancialAgent,
                MarketAgent, ReviewerAgent
            )
            
            # Cria orquestrador
            agents = {
                "analyst": AnalystAgent(),
                "commercial": CommercialAgent(),
                "financial": FinancialAgent(),
                "market": MarketAgent(),
                "reviewer": ReviewerAgent(),
            }
            orchestrator = BusinessOrchestrator(agents)
            
            # Cria contexto
            context = ExecutionContext(
                problem_description=analysis.problem_description,
                business_type=analysis.business_type,
                analysis_depth=analysis.analysis_depth,
            )
            
            # Executa
            result_context = asyncio.run(orchestrator.execute(context))
            
            # Salva resultados
            analysis.status = AnalysisStatus.COMPLETED
            analysis.completed_at = datetime.utcnow()
            analysis.results = result_context.results
            analysis.executive_summary = result_context.get_agent_output("reviewer")
            analysis.total_tokens = result_context.get_total_tokens()
            analysis.total_cost_usd = result_context.get_total_cost()
            analysis.total_latency_ms = result_context.get_total_latency_ms()
            
            # Salva outputs individuais
            for agent_name, metadata in result_context.metadata.items():
                agent_output = AgentOutput(
                    analysis_id=analysis.id,
                    agent_name=agent_name,
                    output=result_context.get_agent_output(agent_name),
                    status=metadata.status.value,
                    latency_ms=metadata.duration_seconds * 1000,
                    input_tokens=metadata.input_tokens,
                    output_tokens=metadata.output_tokens,
                    cost_usd=metadata.cost_usd,
                    started_at=metadata.start_time,
                    completed_at=metadata.end_time,
                    error_message=metadata.error,
                )
                self.db.add(agent_output)
            
            # Registra uso para billing
            self.billing.record_execution(
                analysis.org_id,
                analysis.total_tokens,
                analysis.total_cost_usd
            )
            
            self.db.commit()
            
        except Exception as e:
            analysis.status = AnalysisStatus.FAILED
            analysis.error_message = str(e)
            analysis.completed_at = datetime.utcnow()
            self.db.commit()
            raise
        
        return analysis
    
    def get_analysis(self, analysis_id: UUID, org_id: UUID) -> Optional[Analysis]:
        """
        Busca análise por ID.
        Filtra por org_id para isolamento multi-tenant.
        """
        return self.db.query(Analysis).filter(
            Analysis.id == analysis_id,
            Analysis.org_id == org_id
        ).first()
    
    def list_analyses(
        self,
        org_id: UUID,
        limit: int = 50,
        offset: int = 0,
        status: Optional[AnalysisStatus] = None
    ) -> List[Analysis]:
        """Lista análises da organização com paginação."""
        query = self.db.query(Analysis).filter(Analysis.org_id == org_id)
        
        if status:
            query = query.filter(Analysis.status == status)
        
        return query.order_by(Analysis.created_at.desc()).offset(offset).limit(limit).all()
    
    def count_analyses(self, org_id: UUID) -> int:
        """Conta total de análises da organização."""
        return self.db.query(Analysis).filter(Analysis.org_id == org_id).count()
    
    def delete_analysis(self, analysis_id: UUID, org_id: UUID) -> bool:
        """
        Deleta análise.
        Retorna True se deletou, False se não encontrou.
        """
        result = self.db.query(Analysis).filter(
            Analysis.id == analysis_id,
            Analysis.org_id == org_id
        ).delete()
        
        self.db.commit()
        return result > 0
