"""Service para orquestrar análises com persistência, cache e prompts dinâmicos."""

import asyncio
from typing import Dict, Optional

from core.types import ExecutionContext
from orchestrator import BusinessOrchestrator
from agents import (
    AnalystAgent,
    CommercialAgent,
    FinancialAgent,
    MarketAgent,
    ReviewerAgent,
)
from infrastructure.database import get_db_connection
from infrastructure.repositories import AnalysisRepository
from infrastructure.cache import get_cache_manager
from infrastructure.logging import get_logger

logger = get_logger(__name__)


class AnalysisService:
    """
    Serviço de análise que orquestra agentes e persiste resultados.
    
    Responsabilidades:
    - Executar análise com BusinessOrchestrator
    - Persistir resultados em banco de dados
    - Recuperar análises do histórico
    """
    
    def __init__(self, database_url: Optional[str] = None, enable_cache: bool = True):
        """
        Inicializa serviço.
        
        Args:
            database_url: URL de conexão (default: SQLite local)
            enable_cache: Habilitar cache de resultados
        """
        self.db_connection = get_db_connection(database_url)
        self.orchestrator = self._create_orchestrator()
        self.cache_manager = get_cache_manager() if enable_cache else None
        self.enable_cache = enable_cache
    
    def _create_orchestrator(self) -> BusinessOrchestrator:
        """Cria orquestrador com todos os agentes."""
        agents = {
            "analyst": AnalystAgent(),
            "commercial": CommercialAgent(),
            "financial": FinancialAgent(),
            "market": MarketAgent(),
            "reviewer": ReviewerAgent(),
        }
        return BusinessOrchestrator(agents)
    
    def analyze_business_scenario(
        self,
        problem_description: str,
        business_type: str = "B2B",
        analysis_depth: str = "Padrão",
        user_id: str = "default",
        workspace_id: str = "default",
    ) -> Dict:
        """
        Executa análise de cenário de negócio com cache e persistência.
        
        Args:
            problem_description: Descrição do problema/oportunidade
            business_type: Tipo de negócio (B2B, SaaS, Varejo, etc.)
            analysis_depth: Profundidade (Rápida, Padrão, Profunda)
            user_id: ID do usuário (para multi-tenant)
            workspace_id: ID do workspace
        
        Returns:
            Dict com resultados de cada agente
        """
        # Verifica cache
        if self.enable_cache and self.cache_manager:
            cached_result = self.cache_manager.get(
                problem_description,
                business_type,
                analysis_depth
            )
            if cached_result:
                logger.info(
                    event="cache_hit",
                    message="Resultado encontrado em cache",
                    problem_length=len(problem_description)
                )
                return cached_result
        
        logger.info(
            event="analysis_started",
            message="Iniciando análise de cenário",
            problem_length=len(problem_description),
            business_type=business_type,
            analysis_depth=analysis_depth
        )
        
        # Cria contexto
        context = ExecutionContext(
            problem_description=problem_description,
            business_type=business_type,
            analysis_depth=analysis_depth
        )
        
        # Executa análise (converte async para sync)
        result_context = asyncio.run(self.orchestrator.execute(context))
        
        # Prepara resultado
        result = {
            "execution_id": result_context.execution_id,
            "analyst": result_context.get_agent_output("analyst") or "",
            "commercial": result_context.get_agent_output("commercial") or "",
            "financial": result_context.get_agent_output("financial") or "",
            "market": result_context.get_agent_output("market") or "",
            "executive": result_context.get_agent_output("reviewer") or "",
            "metadata": {
                name: {
                    "status": meta.status.value,
                    "latency_ms": meta.latency_ms,
                    "tokens": meta.total_tokens,
                    "cost_usd": meta.cost_usd,
                }
                for name, meta in result_context.metadata.items()
            }
        }
        
        # Armazena em cache
        if self.enable_cache and self.cache_manager:
            self.cache_manager.set(
                problem_description,
                business_type,
                analysis_depth,
                result
            )
        
        # Persiste resultado
        session = self.db_connection.get_session()
        try:
            repo = AnalysisRepository(session)
            analysis = repo.save_from_context(result_context, user_id, workspace_id)
            logger.info(
                event="analysis_persisted",
                message="Análise persistida no banco de dados",
                execution_id=result_context.execution_id,
                total_cost=result_context.get_total_cost()
            )
        finally:
            session.close()
        
        return result
    
    def get_analysis_history(
        self,
        user_id: str = "default",
        limit: int = 50
    ) -> list:
        """
        Recupera histórico de análises do usuário.
        
        Args:
            user_id: ID do usuário
            limit: Número máximo de análises
        
        Returns:
            Lista de análises
        """
        session = self.db_connection.get_session()
        try:
            repo = AnalysisRepository(session)
            analyses = repo.get_by_user(user_id, limit)
            return [
                {
                    "execution_id": a.execution_id,
                    "problem_description": a.problem_description,
                    "business_type": a.business_type,
                    "created_at": a.created_at.isoformat(),
                    "total_cost_usd": a.total_cost_usd,
                    "total_tokens": a.total_tokens,
                }
                for a in analyses
            ]
        finally:
            session.close()
    
    def get_analysis(self, execution_id: str) -> Optional[Dict]:
        """
        Recupera análise específica com todos os detalhes.
        
        Args:
            execution_id: ID da execução
        
        Returns:
            Dicionário com análise completa ou None
        """
        session = self.db_connection.get_session()
        try:
            repo = AnalysisRepository(session)
            analysis = repo.get_by_execution_id(execution_id)
            
            if not analysis:
                return None
            
            return {
                "execution_id": analysis.execution_id,
                "problem_description": analysis.problem_description,
                "business_type": analysis.business_type,
                "analysis_depth": analysis.analysis_depth,
                "created_at": analysis.created_at.isoformat(),
                "total_cost_usd": analysis.total_cost_usd,
                "total_tokens": analysis.total_tokens,
                "total_latency_ms": analysis.total_latency_ms,
                "agent_outputs": {
                    output.agent_name: {
                        "output": output.output,
                        "latency_ms": output.latency_ms,
                        "tokens": output.total_tokens,
                        "cost_usd": output.cost_usd,
                        "status": output.status,
                    }
                    for output in analysis.agent_outputs
                }
            }
        finally:
            session.close()
    
    def get_user_statistics(self, user_id: str = "default") -> Dict:
        """
        Retorna estatísticas de uso do usuário.
        
        Args:
            user_id: ID do usuário
        
        Returns:
            Dicionário com estatísticas
        """
        session = self.db_connection.get_session()
        try:
            repo = AnalysisRepository(session)
            return repo.get_statistics(user_id)
        finally:
            session.close()
    
    def close(self):
        """Fecha conexão com banco de dados."""
        self.db_connection.close()
