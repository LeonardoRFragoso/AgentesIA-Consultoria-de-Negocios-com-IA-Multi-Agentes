"""
Tipos e estruturas para contexto histórico.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class PastExecution:
    """Referência a uma execução passada relevante"""
    execution_id: str
    problem_description: str
    business_type: str
    created_at: datetime
    status: str
    
    # Resumos de outputs (primeiras 500 caracteres)
    analyst_summary: str
    commercial_summary: str
    financial_summary: str
    market_summary: str
    reviewer_summary: str
    
    # Metadados
    duration_ms: float
    total_tokens: int
    total_cost_usd: float
    
    def get_all_summaries(self) -> str:
        """Retorna todos os resumos concatenados"""
        return f"""
Análise de Negócio:
{self.analyst_summary}

Estratégia Comercial:
{self.commercial_summary}

Análise Financeira:
{self.financial_summary}

Contexto de Mercado:
{self.market_summary}

Diagnóstico Executivo:
{self.reviewer_summary}
"""


@dataclass
class HistoricalContext:
    """Contexto histórico para informar análise atual"""
    
    # Execuções relevantes
    similar_executions: List[PastExecution] = field(default_factory=list)
    
    # Análise de mudanças
    key_differences: List[str] = field(default_factory=list)
    
    # Padrões detectados
    recurring_patterns: List[str] = field(default_factory=list)
    
    # Recomendações anteriores
    past_recommendations: List[str] = field(default_factory=list)
    
    # Efetividade de ações
    action_outcomes: List[str] = field(default_factory=list)
    
    # Metadados
    analysis_timestamp: datetime = field(default_factory=datetime.now)
    total_similar_executions: int = 0
    confidence_score: float = 0.0  # 0.0 a 1.0
    
    def is_relevant(self) -> bool:
        """Histórico é relevante para usar?"""
        return (
            len(self.similar_executions) > 0 and
            self.confidence_score >= 0.5
        )
    
    def to_prompt_context(self) -> str:
        """Converte para texto para incluir em prompt (se relevante)"""
        if not self.is_relevant():
            return ""
        
        parts = []
        
        if self.similar_executions:
            parts.append("## Contexto Histórico Relevante")
            parts.append(f"Encontramos {len(self.similar_executions)} análises similares:")
            
            for i, exec in enumerate(self.similar_executions[:3], 1):
                parts.append(f"\n### Análise {i} ({exec.created_at.strftime('%Y-%m-%d')})")
                parts.append(f"Problema: {exec.problem_description[:200]}...")
                parts.append(f"Status: {exec.status}")
                parts.append(f"Duração: {exec.duration_ms:.0f}ms | Tokens: {exec.total_tokens}")
        
        if self.key_differences:
            parts.append("\n## Mudanças Detectadas")
            for diff in self.key_differences:
                parts.append(f"- {diff}")
        
        if self.recurring_patterns:
            parts.append("\n## Padrões Recorrentes")
            for pattern in self.recurring_patterns:
                parts.append(f"- {pattern}")
        
        if self.action_outcomes:
            parts.append("\n## Resultados de Ações Anteriores")
            for outcome in self.action_outcomes:
                parts.append(f"- {outcome}")
        
        parts.append(f"\n**Confiança do contexto histórico: {self.confidence_score:.0%}**")
        
        return "\n".join(parts)
    
    def __repr__(self) -> str:
        return (
            f"HistoricalContext("
            f"executions={len(self.similar_executions)}, "
            f"confidence={self.confidence_score:.2f}, "
            f"relevant={self.is_relevant()}"
            f")"
        )
