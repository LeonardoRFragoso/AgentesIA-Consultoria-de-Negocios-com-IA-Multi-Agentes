import asyncio
from core.types import ExecutionContext
from orchestrator import BusinessOrchestrator
from agents import (
    AnalystAgent,
    CommercialAgent,
    FinancialAgent,
    MarketAgent,
    ReviewerAgent,
)


class BusinessTeam:
    """Wrapper para compatibilidade com Streamlit (síncrono)"""
    
    def __init__(self):
        self.problem_description = None
        self.context = None
        self.orchestrator = None
    
    def _create_orchestrator(self) -> BusinessOrchestrator:
        """Cria orquestrador com todos os agentes"""
        agents = {
            "analyst": AnalystAgent(),
            "commercial": CommercialAgent(),
            "financial": FinancialAgent(),
            "market": MarketAgent(),
            "reviewer": ReviewerAgent(),
        }
        return BusinessOrchestrator(agents)
    
    def analyze_business_scenario(self, problem_description: str, business_type: str = "B2B") -> dict:
        """
        Executa análise de cenário de negócio.
        
        Args:
            problem_description: Descrição do problema/oportunidade
            business_type: Tipo de negócio (B2B, SaaS, Varejo, etc.)
        
        Returns:
            Dict com resultados de cada agente
        """
        self.problem_description = problem_description
        
        # Cria orquestrador
        self.orchestrator = self._create_orchestrator()
        
        # Cria contexto
        self.context = ExecutionContext(
            problem_description=problem_description,
            business_type=business_type,
            analysis_depth="Padrão"
        )
        
        # Executa análise (converte async para sync)
        print("🔍 Iniciando análise com time de especialistas...")
        
        # Verifica se já existe um event loop rodando
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None
        
        if loop and loop.is_running():
            # Se já tem loop rodando, cria novo loop em thread separada
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, self.orchestrator.execute(self.context))
                result_context = future.result()
        else:
            # Caso normal (Streamlit, scripts)
            result_context = asyncio.run(self.orchestrator.execute(self.context))
        
        print("✅ Análise concluída!")
        
        return {
            "analyst": result_context.get_agent_output("analyst") or "",
            "commercial": result_context.get_agent_output("commercial") or "",
            "financial": result_context.get_agent_output("financial") or "",
            "market": result_context.get_agent_output("market") or "",
            "executive": result_context.get_agent_output("reviewer") or "",
        }
    
    def get_results(self) -> dict:
        """Retorna resultados da última execução"""
        if self.context is None:
            return {}
        
        return {
            "analyst": self.context.get_agent_output("analyst") or "",
            "commercial": self.context.get_agent_output("commercial") or "",
            "financial": self.context.get_agent_output("financial") or "",
            "market": self.context.get_agent_output("market") or "",
            "executive": self.context.get_agent_output("reviewer") or "",
        }
