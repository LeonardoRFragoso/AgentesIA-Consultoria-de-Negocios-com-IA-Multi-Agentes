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
    """Wrapper síncrono para orquestração de agentes de negócio"""
    
    # Mapeamento de nomes para classes de agentes
    AGENT_CLASSES = {
        "analyst": AnalystAgent,
        "commercial": CommercialAgent,
        "financial": FinancialAgent,
        "market": MarketAgent,
        "reviewer": ReviewerAgent,
    }
    
    def __init__(self, selected_agents: list = None):
        """
        Inicializa o time de agentes.
        
        Args:
            selected_agents: Lista de agentes a usar. Se None, usa todos.
                           Opções: analyst, commercial, financial, market, reviewer
        """
        self.problem_description = None
        self.context = None
        self.orchestrator = None
        self.selected_agents = selected_agents or list(self.AGENT_CLASSES.keys())
    
    def _create_orchestrator(self) -> BusinessOrchestrator:
        """Cria orquestrador apenas com agentes selecionados"""
        agents = {}
        
        # Agentes de análise (excluindo reviewer)
        analysis_agents = [a for a in self.selected_agents if a != "reviewer"]
        
        for agent_name in analysis_agents:
            if agent_name in self.AGENT_CLASSES:
                agents[agent_name] = self.AGENT_CLASSES[agent_name]()
        
        # Sempre inclui reviewer com dependências corretas
        # Passa os agentes disponíveis para que ele saiba quais dependências usar
        agents["reviewer"] = ReviewerAgent(available_agents=analysis_agents)
        
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
            # Caso normal (scripts standalone)
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
