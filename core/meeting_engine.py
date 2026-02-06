"""
Motor de reunião executiva estruturada.
"""

from typing import Dict, List, Optional
from datetime import datetime
import uuid

from core.types import ExecutionContext
from core.conflict_model import ConflictReport, Conflict, ConflictSeverity
from core.meeting_model import (
    MeetingMinutes, ExecutiveParticipant, ExecutiveRole, MeetingPhase,
    MeetingAgendaItem, MeetingStatement, MeetingDecision
)
from infrastructure.logging import get_logger

logger = get_logger(__name__)


class MeetingEngine:
    """
    Orquestra reunião executiva estruturada.
    
    Responsabilidades:
    - Criar agenda baseada em conflitos
    - Orquestrar turnos de fala
    - Registrar transcrições
    - Solicitar decisão ao Chair
    - Produzir ata final
    
    O que NÃO faz:
    - Chamar agentes diretamente
    - Gerar chat caótico
    - Tomar decisões sem justificativa
    """
    
    # Configuração
    MAX_ROUNDS = 3
    MIN_SEVERITY_FOR_MEETING = ConflictSeverity.HIGH
    MAX_PARTICIPANTS = 5
    
    def __init__(self):
        """Inicializa motor de reunião"""
        self.role_mapping = {
            "analyst": ExecutiveRole.ANALYST,
            "commercial": ExecutiveRole.CRO,
            "financial": ExecutiveRole.CFO,
            "market": ExecutiveRole.CMO,
            "reviewer": ExecutiveRole.CHAIR,
        }
    
    def should_hold_meeting(self, conflict_report: ConflictReport) -> bool:
        """
        Determina se reunião deve ser realizada.
        
        Critérios:
        - Há conflitos HIGH ou CRITICAL
        - Múltiplos agentes envolvidos
        """
        if not conflict_report.requires_debate:
            return False
        
        # Verifica se há conflitos de alta severidade
        critical_conflicts = conflict_report.get_critical_conflicts()
        
        return len(critical_conflicts) > 0
    
    def run(
        self,
        context: ExecutionContext,
        conflict_report: ConflictReport,
        agent_outputs: Dict[str, str]
    ) -> MeetingMinutes:
        """
        Executa reunião executiva.
        
        Args:
            context: ExecutionContext
            conflict_report: Relatório de conflitos
            agent_outputs: Outputs dos agentes
        
        Returns:
            MeetingMinutes com ata executiva
        """
        logger.info(
            event="meeting_started",
            message="Starting executive meeting",
            execution_id=context.execution_id,
            conflicts=conflict_report.total_conflicts
        )
        
        # Inicializa ata
        meeting_id = str(uuid.uuid4())
        minutes = MeetingMinutes(
            execution_id=context.execution_id,
            meeting_id=meeting_id,
            problem_description=context.problem_description,
            business_type=context.business_type,
            analysis_depth=context.analysis_depth,
            participants=[],
            chair="reviewer"
        )
        
        # Cria participantes
        minutes.participants = self._create_participants(agent_outputs)
        
        # Cria agenda
        minutes.agenda = self._create_agenda(conflict_report)
        
        # Executa reunião por fase
        for phase in [MeetingPhase.OPENING, MeetingPhase.PRESENTATIONS, 
                      MeetingPhase.DISCUSSION, MeetingPhase.PROPOSALS, 
                      MeetingPhase.DELIBERATION, MeetingPhase.CLOSING]:
            
            self._execute_phase(
                minutes,
                phase,
                conflict_report,
                agent_outputs
            )
        
        # Finaliza
        minutes.ended_at = datetime.now()
        minutes.duration_seconds = int(
            (minutes.ended_at - minutes.started_at).total_seconds()
        )
        
        # Calcula confiança
        minutes.confidence_score = self._calculate_meeting_confidence(minutes)
        
        logger.info(
            event="meeting_completed",
            message="Executive meeting completed",
            execution_id=context.execution_id,
            decisions=len(minutes.decisions),
            confidence=minutes.confidence_score
        )
        
        return minutes
    
    def _create_participants(self, agent_outputs: Dict[str, str]) -> List[ExecutiveParticipant]:
        """Cria lista de participantes com papéis"""
        participants = []
        speaking_order = 1
        
        # Ordem de fala: Reviewer (Chair) primeiro, depois Financial, Commercial, Market, Analyst
        agent_order = ["reviewer", "financial", "commercial", "market", "analyst"]
        
        for agent_name in agent_order:
            if agent_name in agent_outputs:
                role = self.role_mapping.get(agent_name, ExecutiveRole.OBSERVER)
                
                # Define expertise por papel
                expertise = self._get_expertise_for_role(role)
                
                participant = ExecutiveParticipant(
                    agent_name=agent_name,
                    role=role,
                    expertise=expertise,
                    speaking_order=speaking_order
                )
                participants.append(participant)
                speaking_order += 1
        
        return participants
    
    def _get_expertise_for_role(self, role: ExecutiveRole) -> List[str]:
        """Retorna áreas de expertise para cada papel"""
        expertise_map = {
            ExecutiveRole.CHAIR: ["decisão", "síntese", "estratégia"],
            ExecutiveRole.CFO: ["financeiro", "viabilidade", "custo"],
            ExecutiveRole.CRO: ["comercial", "vendas", "cliente"],
            ExecutiveRole.CMO: ["mercado", "competição", "tendência"],
            ExecutiveRole.ANALYST: ["análise", "diagnóstico", "contexto"],
            ExecutiveRole.OBSERVER: ["histórico", "risco", "padrão"],
        }
        return expertise_map.get(role, [])
    
    def _create_agenda(self, conflict_report: ConflictReport) -> List[MeetingAgendaItem]:
        """Cria agenda baseada em conflitos"""
        agenda = []
        
        # Abertura
        agenda.append(MeetingAgendaItem(
            phase=MeetingPhase.OPENING,
            topic="Contexto e Objetivos",
            objective="Apresentar problema e objetivos da reunião",
            participants=["reviewer"],
            duration_estimate_seconds=120
        ))
        
        # Apresentações
        agenda.append(MeetingAgendaItem(
            phase=MeetingPhase.PRESENTATIONS,
            topic="Análises-Chave",
            objective="Apresentar análises de cada agente",
            participants=["analyst", "commercial", "financial", "market"],
            duration_estimate_seconds=300
        ))
        
        # Discussão de conflitos
        if conflict_report.conflicts:
            for conflict in conflict_report.conflicts[:3]:  # Máximo 3 conflitos
                agenda.append(MeetingAgendaItem(
                    phase=MeetingPhase.DISCUSSION,
                    topic=conflict.topic,
                    objective=f"Discutir conflito: {conflict.description}",
                    participants=conflict.agents_involved,
                    duration_estimate_seconds=180
                ))
        
        # Propostas
        agenda.append(MeetingAgendaItem(
            phase=MeetingPhase.PROPOSALS,
            topic="Propostas de Decisão",
            objective="Apresentar propostas de resolução",
            participants=["reviewer", "financial", "commercial"],
            duration_estimate_seconds=180
        ))
        
        # Deliberação
        agenda.append(MeetingAgendaItem(
            phase=MeetingPhase.DELIBERATION,
            topic="Deliberação Final",
            objective="Tomar decisão final",
            participants=["reviewer"],
            duration_estimate_seconds=120
        ))
        
        # Encerramento
        agenda.append(MeetingAgendaItem(
            phase=MeetingPhase.CLOSING,
            topic="Encerramento",
            objective="Resumir decisões e ações",
            participants=["reviewer"],
            duration_estimate_seconds=60
        ))
        
        return agenda
    
    def _execute_phase(
        self,
        minutes: MeetingMinutes,
        phase: MeetingPhase,
        conflict_report: ConflictReport,
        agent_outputs: Dict[str, str]
    ) -> None:
        """Executa uma fase da reunião"""
        
        logger.debug(
            event="meeting_phase_start",
            message=f"Starting phase: {phase.value}",
            execution_id=minutes.execution_id,
            phase=phase.value
        )
        
        # Obtém agenda items para esta fase
        phase_items = [item for item in minutes.agenda if item.phase == phase]
        
        for item in phase_items:
            self._execute_agenda_item(
                minutes,
                item,
                conflict_report,
                agent_outputs
            )
            item.completed = True
    
    def _execute_agenda_item(
        self,
        minutes: MeetingMinutes,
        item: MeetingAgendaItem,
        conflict_report: ConflictReport,
        agent_outputs: Dict[str, str]
    ) -> None:
        """Executa um item da agenda"""
        
        # Determina quem fala
        speakers = [p for p in minutes.participants if p.agent_name in item.participants]
        
        # Ordena por speaking_order
        speakers.sort(key=lambda p: p.speaking_order)
        
        # Coleta falas
        round_num = 1
        for speaker in speakers:
            # Extrai statement relevante
            if speaker.agent_name in agent_outputs:
                statement_text = self._extract_relevant_statement(
                    agent_outputs[speaker.agent_name],
                    item.topic
                )
                
                # Cria statement
                statement = MeetingStatement(
                    speaker=speaker.agent_name,
                    role=speaker.role,
                    round_number=round_num,
                    phase=item.phase,
                    statement=statement_text,
                    supporting_evidence=self._extract_evidence(
                        agent_outputs[speaker.agent_name]
                    )
                )
                
                minutes.statements.append(statement)
                speaker.has_spoken = True
                speaker.speaking_count += 1
        
        # Se é fase de deliberação, produz decisão
        if item.phase == MeetingPhase.DELIBERATION:
            decision = self._produce_decision(
                minutes,
                item,
                conflict_report,
                agent_outputs
            )
            if decision:
                minutes.decisions.append(decision)
    
    def _extract_relevant_statement(self, output: str, topic: str) -> str:
        """Extrai statement relevante para o tópico"""
        lines = output.split("\n")
        
        # Procura por linhas relevantes
        topic_keywords = topic.lower().split()
        relevant_lines = []
        
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in topic_keywords):
                relevant_lines.append(line.strip())
        
        # Retorna linhas relevantes ou primeiras linhas
        if relevant_lines:
            return " ".join(relevant_lines[:3])
        
        return " ".join(lines[:2]) if lines else output[:300]
    
    def _extract_evidence(self, output: str) -> List[str]:
        """Extrai evidências do output"""
        evidence = []
        lines = output.split("\n")
        
        for line in lines:
            # Procura por linhas com números/dados
            if any(char.isdigit() for char in line):
                evidence.append(line.strip())
        
        return evidence[:3]
    
    def _produce_decision(
        self,
        minutes: MeetingMinutes,
        item: MeetingAgendaItem,
        conflict_report: ConflictReport,
        agent_outputs: Dict[str, str]
    ) -> Optional[MeetingDecision]:
        """Produz decisão final"""
        
        if not conflict_report.conflicts:
            return None
        
        # Usa primeiro conflito como base
        conflict = conflict_report.conflicts[0]
        
        # Chair (Reviewer) decide
        chair = next((p for p in minutes.participants if p.role == ExecutiveRole.CHAIR), None)
        if not chair:
            return None
        
        # Extrai posição do chair
        if chair.agent_name in agent_outputs:
            position = self._extract_relevant_statement(
                agent_outputs[chair.agent_name],
                conflict.topic
            )
        else:
            position = "Decisão pendente de análise adicional"
        
        # Cria decisão
        decision = MeetingDecision(
            topic=conflict.topic,
            decision=position,
            rationale=f"Baseado em análise de {len(conflict_report.conflicts)} conflito(s)",
            supporting_agents=conflict.agents_involved[:2],
            opposing_agents=conflict.agents_involved[2:] if len(conflict.agents_involved) > 2 else [],
            confidence_score=0.75,
            action_items=[
                f"Monitorar implementação de {conflict.topic}",
                f"Revisar em 30 dias"
            ],
            owner=chair.agent_name
        )
        
        return decision
    
    def _calculate_meeting_confidence(self, minutes: MeetingMinutes) -> float:
        """Calcula confiança geral da reunião"""
        confidence = 0.0
        
        # Participação: +0.3
        if minutes.participants:
            participation_ratio = sum(1 for p in minutes.participants if p.speaking_count > 0) / len(minutes.participants)
            confidence += participation_ratio * 0.3
        
        # Decisões: +0.4
        if minutes.decisions:
            avg_decision_confidence = sum(d.confidence_score for d in minutes.decisions) / len(minutes.decisions)
            confidence += avg_decision_confidence * 0.4
        
        # Agenda completa: +0.3
        completed_items = sum(1 for item in minutes.agenda if item.completed)
        if minutes.agenda:
            completion_ratio = completed_items / len(minutes.agenda)
            confidence += completion_ratio * 0.3
        
        return min(1.0, confidence)


class MeetingOrchestrator:
    """
    Orquestra reuniões executivas no fluxo geral.
    """
    
    def __init__(self):
        """Inicializa orquestrador"""
        self.engine = MeetingEngine()
    
    def run_if_needed(
        self,
        context: ExecutionContext,
        conflict_report: ConflictReport,
        agent_outputs: Dict[str, str]
    ) -> Optional[MeetingMinutes]:
        """
        Executa reunião se necessário.
        
        Args:
            context: ExecutionContext
            conflict_report: Relatório de conflitos
            agent_outputs: Outputs dos agentes
        
        Returns:
            MeetingMinutes se reunião foi realizada, None caso contrário
        """
        
        if not self.engine.should_hold_meeting(conflict_report):
            logger.debug(
                event="meeting_skipped",
                message="Meeting not needed",
                execution_id=context.execution_id
            )
            return None
        
        return self.engine.run(context, conflict_report, agent_outputs)
