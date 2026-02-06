import os
from core.agent import BaseAgent
from core.types import ExecutionContext


class AnalystAgent(BaseAgent):
    """Agente Analista de Negócio"""
    
    def __init__(self):
        prompt_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "prompts",
            "analyst.md"
        )
        super().__init__(
            name="analyst",
            prompt_path=prompt_path,
            model="claude-3-haiku-20240307",
            dependencies=[],
            max_tokens=1024
        )
    
    def _build_user_message(self, context: ExecutionContext) -> str:
        return f"""Analise o seguinte problema de negócio:

{context.problem_description}

Forneça uma análise estruturada seguindo o formato especificado."""
