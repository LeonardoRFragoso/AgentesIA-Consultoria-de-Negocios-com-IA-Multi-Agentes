import os
from core.agent import BaseAgent
from core.types import ExecutionContext


class FinancialAgent(BaseAgent):
    """Agente Analista Financeiro"""
    
    def __init__(self):
        prompt_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "prompts",
            "financial.md"
        )
        super().__init__(
            name="financial",
            prompt_path=prompt_path,
            model="claude-3-haiku-20240307",
            dependencies=["analyst", "commercial"],
            max_tokens=2048
        )
    
    def _build_user_message(self, context: ExecutionContext) -> str:
        analyst_output = context.get_agent_output("analyst") or "Análise não disponível"
        commercial_output = context.get_agent_output("commercial") or "Estratégia não disponível"
        
        return f"""Com base na seguinte análise de negócio:

{analyst_output}

E na seguinte estratégia comercial:

{commercial_output}

Considerando o problema original:

{context.problem_description}

Forneça uma avaliação financeira detalhada seguindo o formato especificado."""
