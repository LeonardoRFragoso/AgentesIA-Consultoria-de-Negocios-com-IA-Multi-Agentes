"""
Analisador de histórico para gerar contexto relevante de execuções passadas.
"""

from typing import List, Optional
from datetime import datetime, timedelta
import re

from core.types import ExecutionContext
from core.historical_context import HistoricalContext, PastExecution
from streamlit_infrastructure.logging import get_logger

logger = get_logger(__name__)


class HistoryAnalyzer:
    """
    Analisa histórico de execuções para gerar contexto relevante.
    
    Responsabilidades:
    - Selecionar execuções passadas relevantes
    - Detectar mudanças de cenário
    - Identificar padrões recorrentes
    - Gerar contexto para agentes
    
    O que NÃO faz:
    - Acessa banco de dados diretamente (recebe dados do repositório)
    - Modifica contexto atual
    - Toma decisões de negócio
    """
    
    # Temas detectáveis por palavras-chave
    THEMES = {
        "vendas": ["venda", "vendas", "queda", "crescimento", "pipeline", "receita"],
        "custo": ["custo", "despesa", "margem", "lucratividade", "otimização", "eficiência"],
        "cliente": ["cliente", "churn", "retenção", "satisfação", "atrito", "experiência"],
        "produto": ["produto", "feature", "lançamento", "desenvolvimento", "roadmap"],
        "mercado": ["mercado", "competição", "posicionamento", "expansão", "concorrente"],
        "operação": ["operação", "processo", "workflow", "automação", "eficiência"],
    }
    
    def __init__(self, repository=None):
        """
        Inicializa analisador.
        
        Args:
            repository: ExecutionRepository (opcional, pode ser None)
        """
        self.repository = repository
    
    def analyze(
        self,
        current_context: ExecutionContext,
        past_executions: Optional[List[dict]] = None
    ) -> HistoricalContext:
        """
        Analisa histórico e gera contexto relevante.
        
        Args:
            current_context: Contexto da execução atual
            past_executions: Lista de execuções passadas (do repositório)
        
        Returns:
            HistoricalContext com análise completa
        """
        historical_context = HistoricalContext()
        
        # Se não há histórico, retorna vazio
        if not past_executions:
            logger.debug(
                event="history_analysis_empty",
                message="No past executions available",
                execution_id=current_context.execution_id
            )
            return historical_context
        
        try:
            # Seleciona execuções relevantes
            relevant_executions = self._select_relevant_executions(
                current_context,
                past_executions
            )
            
            if not relevant_executions:
                logger.debug(
                    event="history_analysis_no_matches",
                    message="No relevant past executions found",
                    execution_id=current_context.execution_id
                )
                return historical_context
            
            # Converte para PastExecution
            historical_context.similar_executions = [
                self._to_past_execution(exec_data)
                for exec_data in relevant_executions[:3]
            ]
            
            # Detecta mudanças
            historical_context.key_differences = self._detect_changes(
                current_context,
                historical_context.similar_executions
            )
            
            # Identifica padrões
            historical_context.recurring_patterns = self._identify_patterns(
                historical_context.similar_executions
            )
            
            # Extrai recomendações anteriores
            historical_context.past_recommendations = self._extract_recommendations(
                historical_context.similar_executions
            )
            
            # Calcula confiança
            historical_context.confidence_score = self._calculate_confidence(
                current_context,
                historical_context.similar_executions
            )
            
            historical_context.total_similar_executions = len(relevant_executions)
            
            logger.info(
                event="history_analysis_complete",
                message=f"Found {len(historical_context.similar_executions)} relevant executions",
                execution_id=current_context.execution_id,
                confidence=historical_context.confidence_score,
                extra_data={
                    "similar_count": len(historical_context.similar_executions),
                    "patterns_found": len(historical_context.recurring_patterns),
                    "differences_found": len(historical_context.key_differences)
                }
            )
            
            return historical_context
            
        except Exception as e:
            logger.error(
                event="history_analysis_failed",
                message=f"Failed to analyze history: {str(e)}",
                execution_id=current_context.execution_id,
                error=str(e)
            )
            return historical_context
    
    def _select_relevant_executions(
        self,
        current_context: ExecutionContext,
        past_executions: List[dict]
    ) -> List[dict]:
        """
        Seleciona execuções passadas relevantes usando critérios determinísticos.
        
        Critérios (em ordem de importância):
        1. Business type exato
        2. Tema similar
        3. Status COMPLETED
        4. Recência (últimos 90 dias)
        5. Top-3 por score
        """
        if not past_executions:
            return []
        
        # Filtra por status COMPLETED
        completed = [e for e in past_executions if e.get("status") == "COMPLETED"]
        if not completed:
            return []
        
        # Filtra por recência (últimos 90 dias)
        cutoff = datetime.now() - timedelta(days=90)
        recent = [
            e for e in completed
            if datetime.fromisoformat(e.get("created_at", "")) > cutoff
        ]
        if not recent:
            recent = completed  # Fallback: aceita mais antigos se poucos
        
        # Detecta tema atual
        current_theme = self._detect_theme(current_context.problem_description)
        
        # Calcula score para cada execução
        scored = []
        for exec in recent:
            score = 0
            
            # Business type match: +100
            if exec.get("business_type") == current_context.business_type:
                score += 100
            
            # Theme match: +50
            exec_theme = self._detect_theme(exec.get("problem_description", ""))
            if exec_theme == current_theme and current_theme != "geral":
                score += 50
            
            # Recência (7 dias): +30
            exec_date = datetime.fromisoformat(exec.get("created_at", ""))
            if (datetime.now() - exec_date).days <= 7:
                score += 30
            
            # Status COMPLETED: +20
            if exec.get("status") == "COMPLETED":
                score += 20
            
            scored.append((exec, score))
        
        # Retorna top-5 por score
        sorted_execs = sorted(scored, key=lambda x: x[1], reverse=True)
        return [e[0] for e in sorted_execs[:5]]
    
    def _detect_theme(self, text: str) -> str:
        """Detecta tema por palavras-chave simples"""
        text_lower = text.lower()
        
        for theme, keywords in self.THEMES.items():
            if any(kw in text_lower for kw in keywords):
                return theme
        
        return "geral"
    
    def _to_past_execution(self, exec_data: dict) -> PastExecution:
        """Converte dados do banco para PastExecution"""
        return PastExecution(
            execution_id=exec_data.get("execution_id", ""),
            problem_description=exec_data.get("problem_description", ""),
            business_type=exec_data.get("business_type", ""),
            created_at=datetime.fromisoformat(exec_data.get("created_at", "")),
            status=exec_data.get("status", ""),
            analyst_summary=self._summarize_text(exec_data.get("analyst_output", "")),
            commercial_summary=self._summarize_text(exec_data.get("commercial_output", "")),
            financial_summary=self._summarize_text(exec_data.get("financial_output", "")),
            market_summary=self._summarize_text(exec_data.get("market_output", "")),
            reviewer_summary=self._summarize_text(exec_data.get("reviewer_output", "")),
            duration_ms=exec_data.get("duration_ms", 0.0),
            total_tokens=exec_data.get("total_tokens", 0),
            total_cost_usd=exec_data.get("total_cost_usd", 0.0)
        )
    
    def _summarize_text(self, text: str, max_length: int = 500) -> str:
        """Resumo simples: primeiras N caracteres + "..." se necessário"""
        if not text:
            return "[Sem resultado]"
        
        text = text.strip()
        if len(text) > max_length:
            return text[:max_length] + "..."
        return text
    
    def _detect_changes(
        self,
        current_context: ExecutionContext,
        past_executions: List[PastExecution]
    ) -> List[str]:
        """Detecta mudanças entre análise atual e passadas"""
        changes = []
        
        if not past_executions:
            return changes
        
        # Compara com execução mais recente
        most_recent = past_executions[0]
        
        # Detecta se problema persiste (mesma temática)
        current_theme = self._detect_theme(current_context.problem_description)
        past_theme = self._detect_theme(most_recent.problem_description)
        
        if current_theme == past_theme and current_theme != "geral":
            days_diff = (datetime.now() - most_recent.created_at).days
            if days_diff > 30:
                changes.append(
                    f"Problema similar persiste há {days_diff} dias "
                    f"(última análise em {most_recent.created_at.strftime('%Y-%m-%d')})"
                )
        
        # Detecta se status mudou
        if most_recent.status == "COMPLETED":
            changes.append(
                f"Análise anterior foi bem-sucedida "
                f"({most_recent.duration_ms:.0f}ms, {most_recent.total_tokens} tokens)"
            )
        
        return changes
    
    def _identify_patterns(self, past_executions: List[PastExecution]) -> List[str]:
        """Identifica padrões recorrentes"""
        patterns = []
        
        if len(past_executions) < 2:
            return patterns
        
        # Padrão: recomendações similares
        recommendations = []
        for exec in past_executions:
            # Extrai recomendações do reviewer (procura por "recomend")
            if "recomend" in exec.reviewer_summary.lower():
                recommendations.append(exec.reviewer_summary)
        
        if len(recommendations) >= 2:
            patterns.append(
                "Múltiplas análises similares recomendaram ações similares"
            )
        
        # Padrão: sucesso consistente
        successful = [e for e in past_executions if e.status == "COMPLETED"]
        if len(successful) == len(past_executions):
            patterns.append(
                f"Todas as {len(successful)} análises similares foram bem-sucedidas"
            )
        
        return patterns
    
    def _extract_recommendations(self, past_executions: List[PastExecution]) -> List[str]:
        """Extrai recomendações de análises passadas"""
        recommendations = []
        
        for exec in past_executions[:3]:
            # Procura por padrões de recomendação no reviewer
            text = exec.reviewer_summary.lower()
            
            # Palavras-chave de recomendação
            if any(word in text for word in ["recomend", "implementar", "focar", "priorizar"]):
                # Extrai primeira sentença com recomendação
                sentences = exec.reviewer_summary.split(".")
                for sentence in sentences:
                    if any(word in sentence.lower() for word in ["recomend", "implementar"]):
                        recommendations.append(sentence.strip())
                        break
        
        return recommendations[:3]  # Máximo 3
    
    def _calculate_confidence(
        self,
        current_context: ExecutionContext,
        past_executions: List[PastExecution]
    ) -> float:
        """
        Calcula confiança do contexto histórico (0.0 a 1.0).
        
        Fatores:
        - Execuções encontradas: +0.3
        - Business type exato: +0.3
        - Tema similar: +0.2
        - Recência: +0.2
        """
        confidence = 0.0
        
        if not past_executions:
            return 0.0
        
        # Execuções encontradas: +0.3
        confidence += min(0.3, len(past_executions) * 0.1)
        
        # Business type exato: +0.3
        if past_executions[0].business_type == current_context.business_type:
            confidence += 0.3
        
        # Tema similar: +0.2
        current_theme = self._detect_theme(current_context.problem_description)
        past_theme = self._detect_theme(past_executions[0].problem_description)
        if current_theme == past_theme and current_theme != "geral":
            confidence += 0.2
        
        # Recência: +0.2
        days_diff = (datetime.now() - past_executions[0].created_at).days
        if days_diff <= 7:
            confidence += 0.2
        elif days_diff <= 30:
            confidence += 0.1
        
        return min(1.0, confidence)
