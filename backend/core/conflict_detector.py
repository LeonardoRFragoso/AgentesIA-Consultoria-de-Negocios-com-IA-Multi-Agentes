"""
Detector de conflitos entre agentes usando regras determinísticas.
"""

from typing import Dict, List, Tuple
from core.types import ExecutionContext
from core.conflict_model import (
    Conflict, ConflictReport, ConflictType, ConflictSeverity,
    AgentPosition
)
from streamlit_infrastructure.logging import get_logger
import uuid
from datetime import datetime

logger = get_logger(__name__)


class ConflictDetector:
    """
    Detecta conflitos entre agentes usando regras determinísticas.
    
    Responsabilidades:
    - Analisar outputs de agentes
    - Detectar contradições
    - Classificar conflitos por tipo e severidade
    - Gerar relatório de conflitos
    
    O que NÃO faz:
    - Resolver conflitos
    - Usar ML ou embeddings
    - Modificar outputs
    """
    
    # Palavras-chave para detecção de conflito
    OPPOSING_KEYWORDS = {
        "investir": ["cortar", "reduzir", "diminuir", "economizar"],
        "expandir": ["consolidar", "manter", "estabilizar", "preservar"],
        "agressivo": ["conservador", "cauteloso", "prudente", "seguro"],
        "rápido": ["lento", "gradual", "incremental", "faseado"],
        "crescimento": ["lucro", "margem", "eficiência", "custo"],
        "inovação": ["estabilidade", "risco", "segurança", "conformidade"],
    }
    
    # Mapeamento de agentes para temas de especialidade
    AGENT_THEMES = {
        "analyst": ["análise", "diagnóstico", "problema", "contexto"],
        "commercial": ["vendas", "cliente", "mercado", "estratégia"],
        "financial": ["custo", "investimento", "retorno", "viabilidade"],
        "market": ["mercado", "competição", "tendência", "oportunidade"],
        "reviewer": ["decisão", "síntese", "recomendação", "ação"],
    }
    
    def __init__(self):
        """Inicializa detector"""
        pass
    
    def detect(
        self,
        context: ExecutionContext
    ) -> ConflictReport:
        """
        Detecta conflitos entre agentes.
        
        Args:
            context: ExecutionContext com outputs de agentes
        
        Returns:
            ConflictReport com todos os conflitos detectados
        """
        report = ConflictReport(
            execution_id=context.execution_id,
            total_conflicts=0
        )
        
        # Obtém outputs de agentes
        agent_outputs = self._extract_agent_outputs(context)
        
        if len(agent_outputs) < 2:
            logger.debug(
                event="conflict_detection_skip",
                message="Less than 2 agents with output, skipping conflict detection",
                execution_id=context.execution_id
            )
            return report
        
        # Detecta conflitos entre pares de agentes
        detected_conflicts = []
        agent_names = list(agent_outputs.keys())
        
        for i, agent1 in enumerate(agent_names):
            for agent2 in agent_names[i+1:]:
                conflict = self._detect_pairwise_conflict(
                    agent1, agent_outputs[agent1],
                    agent2, agent_outputs[agent2],
                    context
                )
                
                if conflict:
                    detected_conflicts.append(conflict)
        
        # Popula relatório
        report.conflicts = detected_conflicts
        report.total_conflicts = len(detected_conflicts)
        
        # Analisa severidades
        for conflict in detected_conflicts:
            if conflict.severity == ConflictSeverity.LOW:
                report.has_low_severity = True
            elif conflict.severity == ConflictSeverity.MEDIUM:
                report.has_medium_severity = True
            elif conflict.severity == ConflictSeverity.HIGH:
                report.has_high_severity = True
            elif conflict.severity == ConflictSeverity.CRITICAL:
                report.has_critical_severity = True
            
            if conflict.requires_debate:
                report.requires_debate = True
                report.debate_topics.append(conflict.topic)
        
        # Log
        logger.info(
            event="conflict_detection_complete",
            message=f"Detected {report.total_conflicts} conflicts",
            execution_id=context.execution_id,
            total_conflicts=report.total_conflicts,
            requires_debate=report.requires_debate,
            extra_data={
                "high_severity": report.has_high_severity,
                "critical": report.has_critical_severity
            }
        )
        
        return report
    
    def _extract_agent_outputs(self, context: ExecutionContext) -> Dict[str, str]:
        """Extrai outputs de agentes do contexto"""
        outputs = {}
        
        for agent_name in ["analyst", "commercial", "financial", "market", "reviewer"]:
            output = context.get_agent_output(agent_name)
            if output:
                outputs[agent_name] = output
        
        return outputs
    
    def _detect_pairwise_conflict(
        self,
        agent1: str,
        output1: str,
        agent2: str,
        output2: str,
        context: ExecutionContext
    ) -> Tuple[Conflict, None]:
        """Detecta conflito entre dois agentes"""
        
        # Normaliza textos
        text1 = output1.lower()
        text2 = output2.lower()
        
        # Detecta palavras-chave opostas
        opposing_pairs = self._find_opposing_keywords(text1, text2)
        
        if not opposing_pairs:
            return None
        
        # Detecta tipo de conflito
        conflict_type = self._classify_conflict_type(agent1, agent2, opposing_pairs)
        
        # Detecta severidade
        severity = self._assess_severity(agent1, agent2, conflict_type, opposing_pairs)
        
        # Cria posições
        positions = {
            agent1: AgentPosition(
                agent_name=agent1,
                position=self._extract_position(output1),
                reasoning=self._extract_reasoning(output1),
                confidence=self._estimate_confidence(output1),
                supporting_evidence=self._extract_evidence(output1)
            ),
            agent2: AgentPosition(
                agent_name=agent2,
                position=self._extract_position(output2),
                reasoning=self._extract_reasoning(output2),
                confidence=self._estimate_confidence(output2),
                supporting_evidence=self._extract_evidence(output2)
            )
        }
        
        # Cria conflito
        conflict = Conflict(
            conflict_id=str(uuid.uuid4()),
            conflict_type=conflict_type,
            severity=severity,
            topic=self._generate_topic(agent1, agent2, opposing_pairs),
            agents_involved=[agent1, agent2],
            positions=positions,
            description=self._generate_description(agent1, agent2, opposing_pairs),
            key_differences=opposing_pairs,
            mutual_exclusivity=self._assess_mutual_exclusivity(agent1, agent2, opposing_pairs)
        )
        
        # Determina se requer debate
        conflict.requires_debate = severity in [ConflictSeverity.MEDIUM, ConflictSeverity.HIGH, ConflictSeverity.CRITICAL]
        
        return conflict
    
    def _find_opposing_keywords(self, text1: str, text2: str) -> List[str]:
        """Encontra palavras-chave opostas entre dois textos"""
        opposing_pairs = []
        
        for keyword, opposites in self.OPPOSING_KEYWORDS.items():
            keyword_in_1 = keyword in text1
            keyword_in_2 = keyword in text2
            
            # Se keyword está em um texto
            if keyword_in_1 or keyword_in_2:
                # Procura por opostos no outro texto
                for opposite in opposites:
                    if keyword_in_1 and opposite in text2:
                        opposing_pairs.append(f"{keyword} vs {opposite}")
                    elif keyword_in_2 and opposite in text1:
                        opposing_pairs.append(f"{opposite} vs {keyword}")
        
        return opposing_pairs
    
    def _classify_conflict_type(
        self,
        agent1: str,
        agent2: str,
        opposing_pairs: List[str]
    ) -> ConflictType:
        """Classifica tipo de conflito"""
        
        # Financial vs Commercial = conflito financeiro
        if (agent1 == "financial" and agent2 == "commercial") or \
           (agent1 == "commercial" and agent2 == "financial"):
            if any("investir" in pair or "custo" in pair for pair in opposing_pairs):
                return ConflictType.FINANCIAL
        
        # Analyst vs Market = conflito de risco
        if (agent1 == "analyst" and agent2 == "market") or \
           (agent1 == "market" and agent2 == "analyst"):
            if any("agressivo" in pair or "conservador" in pair for pair in opposing_pairs):
                return ConflictType.RISK
        
        # Commercial vs Financial = conflito estratégico
        if any("expandir" in pair or "crescimento" in pair for pair in opposing_pairs):
            return ConflictType.STRATEGIC
        
        # Padrão: tático
        return ConflictType.TACTICAL
    
    def _assess_severity(
        self,
        agent1: str,
        agent2: str,
        conflict_type: ConflictType,
        opposing_pairs: List[str]
    ) -> ConflictSeverity:
        """Avalia severidade do conflito"""
        
        # Conflitos financeiros são sempre altos
        if conflict_type == ConflictType.FINANCIAL:
            return ConflictSeverity.HIGH
        
        # Conflitos estratégicos são altos
        if conflict_type == ConflictType.STRATEGIC:
            return ConflictSeverity.HIGH
        
        # Conflitos de risco são médios
        if conflict_type == ConflictType.RISK:
            return ConflictSeverity.MEDIUM
        
        # Padrão: baixo
        return ConflictSeverity.LOW
    
    def _assess_mutual_exclusivity(
        self,
        agent1: str,
        agent2: str,
        opposing_pairs: List[str]
    ) -> bool:
        """Avalia se posições são mutuamente exclusivas"""
        # Se há múltiplos pares opostos, provavelmente são mutuamente exclusivas
        return len(opposing_pairs) > 1
    
    def _extract_position(self, output: str) -> str:
        """Extrai posição/recomendação principal"""
        lines = output.split("\n")
        
        # Procura por linhas com palavras-chave de recomendação
        for line in lines:
            if any(word in line.lower() for word in ["recomend", "suger", "dever", "precis"]):
                return line.strip()[:200]
        
        # Fallback: primeira linha não vazia
        for line in lines:
            if line.strip():
                return line.strip()[:200]
        
        return output[:200]
    
    def _extract_reasoning(self, output: str) -> str:
        """Extrai justificativa"""
        lines = output.split("\n")
        
        # Procura por linhas com "porque", "pois", "motivo"
        for line in lines:
            if any(word in line.lower() for word in ["porque", "pois", "motivo", "razão"]):
                return line.strip()[:300]
        
        # Fallback: segunda linha
        if len(lines) > 1:
            return lines[1].strip()[:300]
        
        return output[:300]
    
    def _estimate_confidence(self, output: str) -> float:
        """Estima confiança do agente (heurística)"""
        text_lower = output.lower()
        
        # Palavras que indicam alta confiança
        high_confidence_words = ["certamente", "definitivamente", "claro", "óbvio", "evidente"]
        if any(word in text_lower for word in high_confidence_words):
            return 0.9
        
        # Palavras que indicam baixa confiança
        low_confidence_words = ["talvez", "pode ser", "incerto", "dúvida", "questionável"]
        if any(word in text_lower for word in low_confidence_words):
            return 0.5
        
        # Padrão: confiança média
        return 0.7
    
    def _extract_evidence(self, output: str) -> List[str]:
        """Extrai evidências/suporte"""
        evidence = []
        
        lines = output.split("\n")
        for line in lines:
            # Procura por linhas com números, dados, percentuais
            if any(char.isdigit() for char in line):
                evidence.append(line.strip())
        
        return evidence[:3]  # Máximo 3 evidências
    
    def _generate_topic(self, agent1: str, agent2: str, opposing_pairs: List[str]) -> str:
        """Gera tópico do conflito"""
        if opposing_pairs:
            return f"Conflito: {opposing_pairs[0]}"
        return f"Conflito entre {agent1} e {agent2}"
    
    def _generate_description(self, agent1: str, agent2: str, opposing_pairs: List[str]) -> str:
        """Gera descrição do conflito"""
        return f"{agent1.capitalize()} e {agent2.capitalize()} têm posições opostas sobre: {', '.join(opposing_pairs[:2])}"
    
    def _find_opposing_keywords(self, text1: str, text2: str) -> List[str]:
        """Encontra palavras-chave opostas entre dois textos"""
        opposing_pairs = []
        
        for keyword, opposites in self.OPPOSING_KEYWORDS.items():
            keyword_in_1 = keyword in text1
            keyword_in_2 = keyword in text2
            
            if keyword_in_1 or keyword_in_2:
                for opposite in opposites:
                    if keyword_in_1 and opposite in text2:
                        opposing_pairs.append(f"{keyword} vs {opposite}")
                    elif keyword_in_2 and opposite in text1:
                        opposing_pairs.append(f"{opposite} vs {keyword}")
        
        return opposing_pairs
