"""
Interface para agentes acessarem contexto histórico de forma segura.
"""

from typing import Optional
from core.types import ExecutionContext
from core.historical_context import HistoricalContext


class HistoryInterface:
    """
    Interface segura para agentes acessarem contexto histórico.
    
    Responsabilidades:
    - Fornecer acesso controlado ao histórico
    - Evitar acesso direto ao banco
    - Permitir decisão do agente sobre uso
    
    O que NÃO faz:
    - Acessa banco de dados
    - Modifica contexto
    - Toma decisões de negócio
    """
    
    def __init__(self, context: ExecutionContext):
        """
        Inicializa interface com contexto de execução.
        
        Args:
            context: ExecutionContext com histórico opcional
        """
        self.context = context
    
    def has_historical_context(self) -> bool:
        """Verifica se há contexto histórico disponível"""
        return (
            self.context.historical_context is not None and
            self.context.historical_context.is_relevant()
        )
    
    def get_historical_summary(self) -> str:
        """
        Retorna resumo do histórico para incluir em prompt.
        
        Returns:
            String vazia se não há histórico relevante
            Caso contrário, retorna contexto formatado
        """
        if not self.has_historical_context():
            return ""
        
        return self.context.historical_context.to_prompt_context()
    
    def get_similar_executions_count(self) -> int:
        """Retorna número de execuções similares encontradas"""
        if not self.context.historical_context:
            return 0
        return len(self.context.historical_context.similar_executions)
    
    def get_confidence_score(self) -> float:
        """Retorna confiança do contexto histórico (0.0 a 1.0)"""
        if not self.context.historical_context:
            return 0.0
        return self.context.historical_context.confidence_score
    
    def get_key_differences(self) -> list[str]:
        """Retorna mudanças detectadas desde análises anteriores"""
        if not self.context.historical_context:
            return []
        return self.context.historical_context.key_differences
    
    def get_recurring_patterns(self) -> list[str]:
        """Retorna padrões recorrentes identificados"""
        if not self.context.historical_context:
            return []
        return self.context.historical_context.recurring_patterns
    
    def get_past_recommendations(self) -> list[str]:
        """Retorna recomendações de análises anteriores"""
        if not self.context.historical_context:
            return []
        return self.context.historical_context.past_recommendations
    
    def should_include_in_prompt(self) -> bool:
        """
        Determina se histórico deve ser incluído no prompt.
        
        Critérios:
        - Há contexto relevante (confidence >= 0.5)
        - Há execuções similares
        
        Returns:
            True se histórico deve ser incluído
        """
        return self.has_historical_context()


def create_history_aware_message(
    base_message: str,
    context: ExecutionContext,
    include_history: bool = True
) -> str:
    """
    Cria mensagem para agente com contexto histórico opcional.
    
    Args:
        base_message: Mensagem base do agente
        context: ExecutionContext com histórico
        include_history: Se deve incluir histórico
    
    Returns:
        Mensagem com histórico adicionado (se relevante)
    """
    if not include_history:
        return base_message
    
    history_interface = HistoryInterface(context)
    
    if not history_interface.should_include_in_prompt():
        return base_message
    
    historical_summary = history_interface.get_historical_summary()
    
    if not historical_summary:
        return base_message
    
    return f"{base_message}\n\n{historical_summary}"
