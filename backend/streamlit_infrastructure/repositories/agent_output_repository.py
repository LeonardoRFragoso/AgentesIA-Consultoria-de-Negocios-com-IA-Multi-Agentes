"""Repository para outputs de agentes."""

from typing import List, Optional
from sqlalchemy.orm import Session

from streamlit_infrastructure.database.models import AgentOutput
from .base_repository import BaseRepository


class AgentOutputRepository(BaseRepository[AgentOutput]):
    """Repositório para gerenciar outputs de agentes."""
    
    def __init__(self, session: Session):
        """Inicializa repositório de outputs."""
        super().__init__(session, AgentOutput)
    
    def get_by_execution_id(self, execution_id: str) -> List[AgentOutput]:
        """Obtém todos os outputs de uma execução."""
        return self.session.query(AgentOutput).filter(
            AgentOutput.execution_id == execution_id
        ).all()
    
    def get_by_agent_name(self, agent_name: str, limit: int = 100) -> List[AgentOutput]:
        """Obtém outputs de um agente específico."""
        return self.session.query(AgentOutput).filter(
            AgentOutput.agent_name == agent_name
        ).limit(limit).all()
    
    def get_by_execution_and_agent(self, execution_id: str, agent_name: str) -> Optional[AgentOutput]:
        """Obtém output específico de um agente em uma execução."""
        return self.session.query(AgentOutput).filter(
            AgentOutput.execution_id == execution_id,
            AgentOutput.agent_name == agent_name
        ).first()
    
    def get_failed_outputs(self, limit: int = 50) -> List[AgentOutput]:
        """Obtém outputs que falharam."""
        return self.session.query(AgentOutput).filter(
            AgentOutput.status == "failed"
        ).limit(limit).all()
    
    def get_agent_statistics(self, agent_name: str) -> dict:
        """Retorna estatísticas de um agente."""
        outputs = self.session.query(AgentOutput).filter(
            AgentOutput.agent_name == agent_name
        ).all()
        
        if not outputs:
            return {
                "total_executions": 0,
                "successful": 0,
                "failed": 0,
                "avg_latency_ms": 0.0,
                "avg_tokens": 0,
                "total_cost_usd": 0.0,
            }
        
        successful = len([o for o in outputs if o.status == "completed"])
        failed = len([o for o in outputs if o.status == "failed"])
        avg_latency = sum(o.latency_ms for o in outputs) / len(outputs)
        avg_tokens = sum(o.total_tokens for o in outputs) / len(outputs)
        total_cost = sum(o.cost_usd for o in outputs)
        
        return {
            "total_executions": len(outputs),
            "successful": successful,
            "failed": failed,
            "avg_latency_ms": round(avg_latency, 2),
            "avg_tokens": round(avg_tokens, 0),
            "total_cost_usd": round(total_cost, 4),
        }
