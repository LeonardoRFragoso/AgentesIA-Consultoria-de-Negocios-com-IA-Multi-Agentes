from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, TYPE_CHECKING
from datetime import datetime
from enum import Enum

if TYPE_CHECKING:
    from core.historical_context import HistoricalContext


class ExecutionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class AgentMetadata:
    """Metadados de execução de um agente"""
    name: str
    status: ExecutionStatus = ExecutionStatus.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    latency_ms: float = 0.0
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    cost_usd: float = 0.0
    error: Optional[str] = None
    
    @property
    def duration_seconds(self) -> float:
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0


@dataclass
class ExecutionContext:
    """Contexto compartilhado durante execução de análise"""
    problem_description: str
    business_type: str = "B2B"
    analysis_depth: str = "Padrão"
    
    # Resultados dos agentes
    results: Dict[str, str] = field(default_factory=dict)
    
    # Metadados de execução
    metadata: Dict[str, AgentMetadata] = field(default_factory=dict)
    
    # Contexto histórico (opcional)
    historical_context: Optional['HistoricalContext'] = None
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Estado de execução
    execution_id: str = field(default_factory=lambda: str(datetime.now().timestamp()))
    
    def get_agent_output(self, agent_name: str) -> Optional[str]:
        """Recupera output de um agente"""
        return self.results.get(agent_name)
    
    def set_agent_output(self, agent_name: str, output: str, metadata: AgentMetadata) -> None:
        """Define output de um agente e atualiza metadados"""
        self.results[agent_name] = output
        self.metadata[agent_name] = metadata
    
    def get_agent_status(self, agent_name: str) -> ExecutionStatus:
        """Recupera status de um agente"""
        meta = self.metadata.get(agent_name)
        return meta.status if meta else ExecutionStatus.PENDING
    
    def get_total_cost(self) -> float:
        """Calcula custo total de execução"""
        return sum(m.cost_usd for m in self.metadata.values())
    
    def get_total_tokens(self) -> int:
        """Calcula total de tokens usados"""
        return sum(m.total_tokens for m in self.metadata.values())
    
    def get_total_latency_ms(self) -> float:
        """Calcula latência total"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds() * 1000
        return 0.0
