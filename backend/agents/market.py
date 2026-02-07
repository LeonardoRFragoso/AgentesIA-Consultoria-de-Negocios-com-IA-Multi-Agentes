import os
from core.agent import BaseAgent
from core.types import ExecutionContext


class MarketAgent(BaseAgent):
    """Agente Especialista de Mercado"""
    
    def __init__(self):
        prompt_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "prompts",
            "market.md"
        )
        super().__init__(
            name="market",
            prompt_path=prompt_path,
            model="claude-3-haiku-20240307",
            dependencies=["analyst"],
            max_tokens=2048
        )
    
    def _build_user_message(self, context: ExecutionContext) -> str:
        analyst_output = context.get_agent_output("analyst") or "Análise não disponível"
        return f"""Com base na seguinte análise de negócio:

{analyst_output}

E considerando o problema original:

{context.problem_description}

Forneça uma validação de contexto de mercado seguindo o formato especificado."""
