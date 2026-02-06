"""
Modelo de dados para detecção e resolução de conflitos entre agentes.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum
from datetime import datetime


class ConflictType(str, Enum):
    """Tipos de conflito entre agentes"""
    STRATEGIC = "strategic"      # Direções opostas
    TACTICAL = "tactical"        # Prioridades diferentes
    FINANCIAL = "financial"      # Custo vs retorno
    RISK = "risk"               # Conservador vs agressivo
    PRIORITY = "priority"        # Sequenciamento diferente
    UNKNOWN = "unknown"          # Tipo não identificado


class ConflictSeverity(str, Enum):
    """Severidade do conflito"""
    LOW = "low"          # Ignorável, complementação
    MEDIUM = "medium"    # Requer atenção, pode impactar
    HIGH = "high"        # Crítico, afeta decisão fundamental
    CRITICAL = "critical"  # Impossível resolver, precisa escalação


@dataclass
class AgentPosition:
    """Posição de um agente em um conflito"""
    agent_name: str
    position: str          # Recomendação/posição do agente
    reasoning: str         # Justificativa
    confidence: float      # Confiança (0.0 a 1.0)
    supporting_evidence: List[str] = field(default_factory=list)


@dataclass
class Conflict:
    """Representa um conflito entre agentes"""
    conflict_id: str
    conflict_type: ConflictType
    severity: ConflictSeverity
    topic: str                      # Tema do conflito
    agents_involved: List[str]      # Nomes dos agentes
    positions: Dict[str, AgentPosition]  # Posições por agente
    
    # Análise
    description: str                # Descrição do conflito
    key_differences: List[str]      # Diferenças principais
    mutual_exclusivity: bool        # Posições são mutuamente exclusivas?
    
    # Metadados
    detected_at: datetime = field(default_factory=datetime.now)
    requires_debate: bool = True    # Deve entrar em debate?
    
    def get_opposing_agents(self) -> tuple[List[str], List[str]]:
        """Retorna agentes em lados opostos do conflito"""
        if len(self.agents_involved) == 2:
            return [self.agents_involved[0]], [self.agents_involved[1]]
        
        # Para múltiplos agentes, agrupa por similaridade de posição
        # Simplificado: retorna primeiro vs resto
        return [self.agents_involved[0]], self.agents_involved[1:]


@dataclass
class ConflictReport:
    """Relatório de todos os conflitos detectados"""
    execution_id: str
    total_conflicts: int
    conflicts: List[Conflict] = field(default_factory=list)
    
    # Análise
    has_low_severity: bool = False
    has_medium_severity: bool = False
    has_high_severity: bool = False
    has_critical_severity: bool = False
    
    # Decisão
    requires_debate: bool = False
    debate_topics: List[str] = field(default_factory=list)
    
    def get_conflicts_by_severity(self, severity: ConflictSeverity) -> List[Conflict]:
        """Retorna conflitos de uma severidade específica"""
        return [c for c in self.conflicts if c.severity == severity]
    
    def get_critical_conflicts(self) -> List[Conflict]:
        """Retorna conflitos críticos que precisam resolução"""
        return [c for c in self.conflicts if c.requires_debate and c.severity in [ConflictSeverity.HIGH, ConflictSeverity.CRITICAL]]
    
    def __repr__(self) -> str:
        return (
            f"ConflictReport("
            f"total={self.total_conflicts}, "
            f"requires_debate={self.requires_debate}, "
            f"critical={len(self.get_critical_conflicts())}"
            f")"
        )


@dataclass
class DebateRound:
    """Um round de debate entre agentes"""
    round_number: int
    topic: str
    arguments: Dict[str, str]  # {agent_name: argument}
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ConsensusResult:
    """Resultado final do debate e consenso"""
    execution_id: str
    conflict_id: str
    
    # Decisão
    final_decision: str              # Decisão final
    supporting_agents: List[str]     # Agentes que apoiam
    opposing_agents: List[str]       # Agentes que se opõem
    neutral_agents: List[str]        # Agentes neutros
    
    # Justificativa
    justification: str               # Por que essa decisão
    reasoning_summary: str           # Resumo do raciocínio
    trade_offs_acknowledged: List[str]  # Trade-offs reconhecidos
    
    # Debate
    debate_rounds: List[DebateRound] = field(default_factory=list)
    total_rounds: int = 0
    
    # Resolução
    unresolved_aspects: List[str] = field(default_factory=list)
    confidence_score: float = 0.0    # Confiança na decisão (0.0 a 1.0)
    
    # Metadados
    resolved_at: datetime = field(default_factory=datetime.now)
    resolver_agent: str = "reviewer"  # Qual agente resolveu
    
    def is_unanimous(self) -> bool:
        """Decisão é unânime?"""
        return len(self.opposing_agents) == 0
    
    def is_consensus(self) -> bool:
        """Há consenso (maioria + justificativa)?"""
        total_agents = len(self.supporting_agents) + len(self.opposing_agents)
        if total_agents == 0:
            return False
        support_ratio = len(self.supporting_agents) / total_agents
        return support_ratio >= 0.66  # 2/3 de apoio
    
    def __repr__(self) -> str:
        return (
            f"ConsensusResult("
            f"decision='{self.final_decision[:30]}...', "
            f"support={len(self.supporting_agents)}, "
            f"oppose={len(self.opposing_agents)}, "
            f"confidence={self.confidence_score:.2f}"
            f")"
        )
