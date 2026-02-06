import os
from core.agent import BaseAgent
from core.types import ExecutionContext


class ReviewerAgent(BaseAgent):
    """Agente Revisor Executivo (CEO/Board)"""
    
    def __init__(self):
        prompt_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "prompts",
            "reviewer.md"
        )
        super().__init__(
            name="reviewer",
            prompt_path=prompt_path,
            model="claude-3-haiku-20240307",
            dependencies=["analyst", "commercial", "financial", "market"],
            max_tokens=2048
        )
    
    def _build_user_message(self, context: ExecutionContext) -> str:
        analyst_output = context.get_agent_output("analyst") or "Análise não disponível"
        commercial_output = context.get_agent_output("commercial") or "Estratégia não disponível"
        financial_output = context.get_agent_output("financial") or "Análise financeira não disponível"
        market_output = context.get_agent_output("market") or "Contexto de mercado não disponível"
        
        return f"""Você recebeu as seguintes análises de um time de especialistas:

PROBLEMA ORIGINAL:
{context.problem_description}

ANÁLISE DO ANALISTA DE NEGÓCIO:
{analyst_output}

ESTRATÉGIA COMERCIAL:
{commercial_output}

ANÁLISE FINANCEIRA:
{financial_output}

CONTEXTO DE MERCADO:
{market_output}

Consolide todas essas análises em um diagnóstico executivo coerente, seguindo o formato especificado."""
