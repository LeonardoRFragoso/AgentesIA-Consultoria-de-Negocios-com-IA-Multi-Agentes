"""
Motor de debate estruturado para resolução de conflitos.
"""

from typing import Dict, List, Optional
from core.conflict_model import (
    Conflict, ConflictSeverity, ConsensusResult, DebateRound, AgentPosition
)
from core.types import ExecutionContext
from streamlit_infrastructure.logging import get_logger
from datetime import datetime

logger = get_logger(__name__)


class DebateEngine:
    """
    Orquestra debate estruturado entre agentes para resolver conflitos.
    
    Responsabilidades:
    - Executar rounds de debate
    - Coletar argumentos de agentes
    - Mediar discussão
    - Produzir decisão final
    
    O que NÃO faz:
    - Chamar agentes diretamente
    - Modificar outputs
    - Tomar decisões sem justificativa
    """
    
    # Configuração de debate
    MAX_ROUNDS = 3
    MIN_ROUNDS = 1
    CONFIDENCE_THRESHOLD = 0.6
    
    def __init__(self):
        """Inicializa motor de debate"""
        pass
    
    def run(
        self,
        conflict: Conflict,
        agent_outputs: Dict[str, str],
        context: ExecutionContext
    ) -> ConsensusResult:
        """
        Executa debate para resolver um conflito.
        
        Args:
            conflict: Conflito a resolver
            agent_outputs: Outputs dos agentes
            context: ExecutionContext
        
        Returns:
            ConsensusResult com decisão final
        """
        logger.info(
            event="debate_started",
            message=f"Starting debate for conflict: {conflict.topic}",
            execution_id=context.execution_id,
            conflict_id=conflict.conflict_id,
            agents=conflict.agents_involved
        )
        
        # Inicializa resultado
        result = ConsensusResult(
            execution_id=context.execution_id,
            conflict_id=conflict.conflict_id,
            final_decision="",
            supporting_agents=[],
            opposing_agents=conflict.agents_involved.copy(),
            neutral_agents=[],
            justification="",
            reasoning_summary="",
            trade_offs_acknowledged=[],
            resolver_agent="reviewer"
        )
        
        # Executa rounds de debate
        for round_num in range(1, self.MAX_ROUNDS + 1):
            logger.debug(
                event="debate_round_start",
                message=f"Starting debate round {round_num}",
                execution_id=context.execution_id,
                conflict_id=conflict.conflict_id,
                round=round_num
            )
            
            # Coleta argumentos
            arguments = self._collect_arguments(
                conflict,
                agent_outputs,
                round_num
            )
            
            # Cria round
            debate_round = DebateRound(
                round_number=round_num,
                topic=conflict.topic,
                arguments=arguments
            )
            result.debate_rounds.append(debate_round)
            
            # Avalia convergência
            convergence = self._assess_convergence(conflict, arguments)
            
            logger.debug(
                event="debate_round_convergence",
                message=f"Round {round_num} convergence: {convergence:.2f}",
                execution_id=context.execution_id,
                convergence=convergence
            )
            
            # Se convergiu, encerra debate
            if convergence >= 0.7 or round_num == self.MAX_ROUNDS:
                result.total_rounds = round_num
                break
        
        # Produz decisão final
        self._produce_decision(conflict, result, agent_outputs)
        
        logger.info(
            event="debate_completed",
            message=f"Debate completed: {result.final_decision[:50]}...",
            execution_id=context.execution_id,
            conflict_id=conflict.conflict_id,
            rounds=result.total_rounds,
            confidence=result.confidence_score
        )
        
        return result
    
    def _collect_arguments(
        self,
        conflict: Conflict,
        agent_outputs: Dict[str, str],
        round_num: int
    ) -> Dict[str, str]:
        """Coleta argumentos dos agentes envolvidos"""
        arguments = {}
        
        for agent_name in conflict.agents_involved:
            if agent_name in agent_outputs:
                # Extrai argumento relevante
                argument = self._extract_relevant_argument(
                    agent_outputs[agent_name],
                    conflict,
                    round_num
                )
                arguments[agent_name] = argument
        
        return arguments
    
    def _extract_relevant_argument(
        self,
        output: str,
        conflict: Conflict,
        round_num: int
    ) -> str:
        """Extrai argumento relevante para o conflito"""
        lines = output.split("\n")
        
        # Procura por linhas relevantes ao tópico do conflito
        relevant_lines = []
        topic_keywords = conflict.topic.lower().split()
        
        for line in lines:
            line_lower = line.lower()
            # Se linha contém palavras-chave do tópico
            if any(keyword in line_lower for keyword in topic_keywords):
                relevant_lines.append(line.strip())
        
        # Retorna linhas relevantes ou primeiras linhas
        if relevant_lines:
            return " ".join(relevant_lines[:3])
        
        return " ".join(lines[:2]) if lines else output[:200]
    
    def _assess_convergence(
        self,
        conflict: Conflict,
        arguments: Dict[str, str]
    ) -> float:
        """
        Avalia convergência entre argumentos.
        
        Retorna: 0.0 (divergência total) a 1.0 (convergência total)
        """
        if len(arguments) < 2:
            return 1.0
        
        # Heurística simples: procura por palavras-chave similares
        arg_texts = list(arguments.values())
        
        # Conta palavras compartilhadas
        words_1 = set(arg_texts[0].lower().split())
        words_2 = set(arg_texts[1].lower().split())
        
        if not words_1 or not words_2:
            return 0.0
        
        # Jaccard similarity
        intersection = len(words_1 & words_2)
        union = len(words_1 | words_2)
        
        similarity = intersection / union if union > 0 else 0.0
        
        return similarity
    
    def _produce_decision(
        self,
        conflict: Conflict,
        result: ConsensusResult,
        agent_outputs: Dict[str, str]
    ) -> None:
        """Produz decisão final do debate"""
        
        # Avalia posições
        positions = conflict.positions
        agent_names = list(positions.keys())
        
        if len(agent_names) == 0:
            result.final_decision = "Sem informação suficiente para decidir"
            result.justification = "Nenhum agente forneceu posição clara"
            result.confidence_score = 0.0
            return
        
        # Estratégia: Reviewer (ou agente mais confiante) decide
        # Prioridade: Reviewer > Financial > Commercial > outros
        decision_maker = self._select_decision_maker(agent_names, positions)
        
        if decision_maker:
            decision_position = positions[decision_maker]
            
            # Determina apoiadores e opositores
            result.supporting_agents = [decision_maker]
            result.opposing_agents = [a for a in agent_names if a != decision_maker]
            
            # Define decisão
            result.final_decision = decision_position.position
            result.justification = decision_position.reasoning
            
            # Calcula confiança
            result.confidence_score = self._calculate_confidence(
                conflict,
                result,
                positions
            )
            
            # Reconhece trade-offs
            result.trade_offs_acknowledged = self._identify_trade_offs(
                conflict,
                result
            )
        else:
            result.final_decision = "Conflito não resolvido"
            result.justification = "Não foi possível chegar a uma decisão"
            result.confidence_score = 0.0
    
    def _select_decision_maker(
        self,
        agent_names: List[str],
        positions: Dict[str, AgentPosition]
    ) -> Optional[str]:
        """Seleciona qual agente faz a decisão final"""
        
        # Prioridade: Reviewer > Financial > Commercial > Market > Analyst
        priority_order = ["reviewer", "financial", "commercial", "market", "analyst"]
        
        for agent in priority_order:
            if agent in agent_names:
                return agent
        
        # Fallback: agente com maior confiança
        if agent_names:
            return max(agent_names, key=lambda a: positions[a].confidence)
        
        return None
    
    def _calculate_confidence(
        self,
        conflict: Conflict,
        result: ConsensusResult,
        positions: Dict[str, AgentPosition]
    ) -> float:
        """Calcula confiança na decisão final"""
        
        # Fatores:
        # - Confiança do decision maker: +0.4
        # - Apoio de outros agentes: +0.3
        # - Severidade do conflito: -0.2 se crítico
        # - Evidência: +0.1
        
        confidence = 0.0
        
        # Confiança do decision maker
        if result.supporting_agents:
            decision_maker = result.supporting_agents[0]
            if decision_maker in positions:
                confidence += positions[decision_maker].confidence * 0.4
        
        # Apoio de outros agentes
        if result.supporting_agents and result.opposing_agents:
            support_ratio = len(result.supporting_agents) / (len(result.supporting_agents) + len(result.opposing_agents))
            confidence += support_ratio * 0.3
        elif not result.opposing_agents:
            confidence += 0.3  # Sem oposição
        
        # Severidade
        if conflict.severity == ConflictSeverity.CRITICAL:
            confidence -= 0.2
        
        # Evidência
        total_evidence = sum(
            len(pos.supporting_evidence)
            for pos in positions.values()
        )
        confidence += min(0.1, total_evidence * 0.02)
        
        return max(0.0, min(1.0, confidence))
    
    def _identify_trade_offs(
        self,
        conflict: Conflict,
        result: ConsensusResult
    ) -> List[str]:
        """Identifica trade-offs reconhecidos na decisão"""
        trade_offs = []
        
        # Se há agentes em oposição, há trade-off
        if result.opposing_agents:
            for opposing_agent in result.opposing_agents:
                if opposing_agent in conflict.positions:
                    position = conflict.positions[opposing_agent]
                    trade_offs.append(
                        f"Rejeitada posição de {opposing_agent}: {position.position[:100]}"
                    )
        
        # Adiciona diferenças principais
        trade_offs.extend(conflict.key_differences[:2])
        
        return trade_offs[:3]  # Máximo 3 trade-offs


class ConsensusBuilder:
    """
    Constrói consenso a partir de múltiplos debates.
    """
    
    def __init__(self):
        """Inicializa construtor de consenso"""
        self.debate_engine = DebateEngine()
    
    def build_consensus(
        self,
        conflicts: List[Conflict],
        agent_outputs: Dict[str, str],
        context: ExecutionContext
    ) -> List[ConsensusResult]:
        """
        Constrói consenso para múltiplos conflitos.
        
        Args:
            conflicts: Lista de conflitos a resolver
            agent_outputs: Outputs dos agentes
            context: ExecutionContext
        
        Returns:
            Lista de ConsensusResult
        """
        results = []
        
        for conflict in conflicts:
            if conflict.requires_debate:
                result = self.debate_engine.run(
                    conflict,
                    agent_outputs,
                    context
                )
                results.append(result)
        
        return results
