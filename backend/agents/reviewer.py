import os
from core.agent import BaseAgent
from core.types import ExecutionContext


class ReviewerAgent(BaseAgent):
    """Agente Revisor Executivo (CEO/Board)"""
    
    def __init__(self, available_agents: list = None):
        """
        Inicializa o ReviewerAgent com dependências dinâmicas.
        
        Args:
            available_agents: Lista de agentes disponíveis no plano.
                             Se None, assume todos os agentes (Pro/Enterprise).
        """
        prompt_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "prompts",
            "reviewer.md"
        )
        
        # Dependências dinâmicas baseadas no plano
        all_dependencies = ["analyst", "commercial", "financial", "market"]
        if available_agents:
            # Filtra apenas agentes disponíveis (exclui o próprio reviewer)
            dependencies = [a for a in all_dependencies if a in available_agents]
        else:
            dependencies = all_dependencies
        
        super().__init__(
            name="reviewer",
            prompt_path=prompt_path,
            model="claude-3-haiku-20240307",
            dependencies=dependencies,
            max_tokens=4096
        )
    
    def _build_user_message(self, context: ExecutionContext) -> str:
        # Constrói mensagem dinamicamente baseada nos agentes disponíveis
        sections = []
        
        sections.append(f"PROBLEMA ORIGINAL:\n{context.problem_description}")
        
        analyst_output = context.get_agent_output("analyst")
        if analyst_output:
            sections.append(f"ANÁLISE DO ANALISTA DE NEGÓCIO:\n{analyst_output}")
        
        commercial_output = context.get_agent_output("commercial")
        if commercial_output:
            sections.append(f"ESTRATÉGIA COMERCIAL:\n{commercial_output}")
        
        financial_output = context.get_agent_output("financial")
        if financial_output:
            sections.append(f"ANÁLISE FINANCEIRA:\n{financial_output}")
        
        market_output = context.get_agent_output("market")
        if market_output:
            sections.append(f"CONTEXTO DE MERCADO:\n{market_output}")
        
        analyses_text = "\n\n".join(sections)
        
        return f"""Você recebeu as seguintes análises de um time de especialistas:

{analyses_text}

Consolide todas essas análises em um diagnóstico executivo coerente, seguindo o formato especificado."""
