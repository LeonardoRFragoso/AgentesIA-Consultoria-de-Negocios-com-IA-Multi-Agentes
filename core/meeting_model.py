"""
Modelo de dados para reunião executiva estruturada.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum
from datetime import datetime


class ExecutiveRole(str, Enum):
    """Papéis executivos na reunião"""
    CHAIR = "chair"              # CEO/Reviewer - conduz reunião
    CFO = "cfo"                  # Financial - visão financeira
    CRO = "cro"                  # Commercial - visão comercial
    CMO = "cmo"                  # Market - visão de mercado
    ANALYST = "analyst"          # Analyst - visão analítica
    OBSERVER = "observer"        # Histórico/risco


class MeetingPhase(str, Enum):
    """Fases da reunião"""
    OPENING = "opening"          # Abertura e contexto
    PRESENTATIONS = "presentations"  # Apresentação de análises
    DISCUSSION = "discussion"    # Discussão de conflitos
    PROPOSALS = "proposals"      # Propostas de decisão
    DELIBERATION = "deliberation"  # Deliberação final
    CLOSING = "closing"          # Encerramento


@dataclass
class ExecutiveParticipant:
    """Participante da reunião com papel definido"""
    agent_name: str
    role: ExecutiveRole
    expertise: List[str]         # Áreas de expertise
    speaking_order: int          # Ordem de fala (1-5)
    has_spoken: bool = False     # Já falou nesta rodada?
    speaking_count: int = 0      # Quantas vezes falou


@dataclass
class MeetingAgendaItem:
    """Item da agenda da reunião"""
    phase: MeetingPhase
    topic: str
    objective: str
    participants: List[str]      # Agentes que devem participar
    duration_estimate_seconds: int = 60
    completed: bool = False


@dataclass
class MeetingStatement:
    """Fala de um agente durante a reunião"""
    speaker: str
    role: ExecutiveRole
    round_number: int
    phase: MeetingPhase
    statement: str               # O que foi dito
    supporting_evidence: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class MeetingDecision:
    """Decisão tomada durante a reunião"""
    topic: str
    decision: str
    rationale: str               # Por que essa decisão
    supporting_agents: List[str]
    opposing_agents: List[str]
    confidence_score: float      # 0.0 a 1.0
    action_items: List[str] = field(default_factory=list)
    owner: str = "chair"         # Quem é responsável


@dataclass
class MeetingMinutes:
    """Ata executiva da reunião"""
    execution_id: str
    meeting_id: str
    
    # Contexto
    problem_description: str
    business_type: str
    analysis_depth: str
    
    # Participantes
    participants: List[ExecutiveParticipant]
    chair: str                   # Quem conduziu
    
    # Agenda e execução
    agenda: List[MeetingAgendaItem]
    statements: List[MeetingStatement] = field(default_factory=list)
    total_rounds: int = 0
    
    # Decisões
    decisions: List[MeetingDecision] = field(default_factory=list)
    final_decision: Optional[str] = None
    final_rationale: Optional[str] = None
    
    # Ações
    action_items: List[str] = field(default_factory=list)
    unresolved_topics: List[str] = field(default_factory=list)
    
    # Metadados
    started_at: datetime = field(default_factory=datetime.now)
    ended_at: Optional[datetime] = None
    duration_seconds: int = 0
    confidence_score: float = 0.0
    
    def get_statements_by_phase(self, phase: MeetingPhase) -> List[MeetingStatement]:
        """Retorna falas de uma fase específica"""
        return [s for s in self.statements if s.phase == phase]
    
    def get_statements_by_speaker(self, speaker: str) -> List[MeetingStatement]:
        """Retorna falas de um agente específico"""
        return [s for s in self.statements if s.speaker == speaker]
    
    def to_markdown(self) -> str:
        """Converte ata para formato Markdown"""
        lines = []
        
        # Cabeçalho
        lines.append("# ATA EXECUTIVA")
        lines.append("")
        lines.append(f"**Data**: {self.started_at.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**Duração**: {self.duration_seconds}s")
        lines.append(f"**Presidente**: {self.chair}")
        lines.append("")
        
        # Contexto
        lines.append("## CONTEXTO")
        lines.append(f"**Problema**: {self.problem_description}")
        lines.append(f"**Tipo de Negócio**: {self.business_type}")
        lines.append("")
        
        # Participantes
        lines.append("## PARTICIPANTES")
        for participant in self.participants:
            lines.append(f"- **{participant.agent_name}** ({participant.role.value})")
        lines.append("")
        
        # Decisões
        lines.append("## DECISÕES")
        for decision in self.decisions:
            lines.append(f"### {decision.topic}")
            lines.append(f"**Decisão**: {decision.decision}")
            lines.append(f"**Rationale**: {decision.rationale}")
            lines.append(f"**Confiança**: {decision.confidence_score:.0%}")
            if decision.action_items:
                lines.append("**Ações**:")
                for action in decision.action_items:
                    lines.append(f"- {action}")
            lines.append("")
        
        # Ações
        if self.action_items:
            lines.append("## AÇÕES IMEDIATAS")
            for action in self.action_items:
                lines.append(f"- {action}")
            lines.append("")
        
        # Tópicos não resolvidos
        if self.unresolved_topics:
            lines.append("## TÓPICOS NÃO RESOLVIDOS")
            for topic in self.unresolved_topics:
                lines.append(f"- {topic}")
            lines.append("")
        
        return "\n".join(lines)
    
    def __repr__(self) -> str:
        return (
            f"MeetingMinutes("
            f"decisions={len(self.decisions)}, "
            f"actions={len(self.action_items)}, "
            f"confidence={self.confidence_score:.2f}"
            f")"
        )
