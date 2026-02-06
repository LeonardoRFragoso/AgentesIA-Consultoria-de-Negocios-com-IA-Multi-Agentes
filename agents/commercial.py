import os
from core.agent import BaseAgent
from core.types import ExecutionContext


class CommercialAgent(BaseAgent):
    """Agente Estrategista Comercial"""
    
    def __init__(self):
        prompt_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "prompts",
            "commercial.md"
        )
        super().__init__(
            name="commercial",
            prompt_path=prompt_path,
            model="claude-3-haiku-20240307",
            dependencies=["analyst"],
            max_tokens=1024
        )
    
    def _build_user_message(self, context: ExecutionContext) -> str:
        analyst_output = context.get_agent_output("analyst") or "Análise não disponível"
        return f"""Com base na seguinte análise de negócio:

{analyst_output}

E considerando o problema original:

{context.problem_description}

Desenvolva uma estratégia comercial detalhada seguindo o formato especificado."""
