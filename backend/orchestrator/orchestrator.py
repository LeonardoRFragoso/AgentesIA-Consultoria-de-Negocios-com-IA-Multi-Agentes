import asyncio
from typing import Dict, List, Optional
from datetime import datetime

from core.agent import BaseAgent
from core.types import ExecutionContext, ExecutionStatus
from core.exceptions import AgentExecutionError, BusinessTeamException
from infrastructure.logging import get_logger
from .dag import DAGResolver

logger = get_logger(__name__)


class BusinessOrchestrator:
    """Orquestrador principal para execução de múltiplos agentes"""
    
    def __init__(self, agents: Dict[str, BaseAgent]):
        """
        Inicializa orquestrador com agentes.
        
        Args:
            agents: Dict com {agent_name: agent_instance}
        """
        self.agents = agents
        self.dag = DAGResolver(agents)
        self.execution_layers = self.dag.get_execution_layers()
    
    async def execute(self, context: ExecutionContext) -> ExecutionContext:
        """
        Executa análise completa com todos os agentes.
        
        Executa agentes em camadas respeitando dependências.
        Agentes na mesma camada rodam em paralelo.
        
        Args:
            context: Contexto inicial com problema
            
        Returns:
            Contexto completo com resultados de todos os agentes
        """
        context.started_at = datetime.now()
        
        # Log: Início da execução
        print(f"[ORCHESTRATOR] Starting execution with {len(self.agents)} agents, {len(self.execution_layers)} layers")
        
        # Log: Plano de execução
        print(f"[ORCHESTRATOR] Execution plan: {self.execution_layers}")
        
        try:
            # Executa cada camada sequencialmente
            for layer_idx, layer in enumerate(self.execution_layers):
                await self._execute_layer(context, layer, layer_idx)
            
            context.completed_at = datetime.now()
            
            # Log: Execução concluída com sucesso
            all_completed = all(
                meta.status == ExecutionStatus.COMPLETED
                for meta in context.metadata.values()
            )
            
            if all_completed:
                print(f"[ORCHESTRATOR] Execution completed successfully in {context.get_total_latency_ms():.0f}ms")
            else:
                failed = [name for name, meta in context.metadata.items() if meta.status != ExecutionStatus.COMPLETED]
                print(f"[ORCHESTRATOR] Execution completed with failures: {failed}")
            
            return context
            
        except Exception as e:
            context.completed_at = datetime.now()
            
            # Log: Erro durante execução
            print(f"[ORCHESTRATOR] Execution failed: {str(e)}")
            raise
    
    async def _execute_layer(
        self,
        context: ExecutionContext,
        agent_names: List[str],
        layer_idx: int
    ) -> None:
        """
        Executa uma camada de agentes em paralelo.
        
        Args:
            context: Contexto compartilhado
            agent_names: Nomes dos agentes nesta camada
            layer_idx: Índice da camada (para logging)
        """
        layer_num = layer_idx + 1
        
        # Log: Início da camada
        print(f"[ORCHESTRATOR] Starting layer {layer_num} with agents: {agent_names}")
        
        layer_start_time = datetime.now()
        
        # Cria tasks para todos os agentes da camada
        tasks = {
            agent_name: asyncio.create_task(
                self.agents[agent_name].execute(context)
            )
            for agent_name in agent_names
        }
        
        # Aguarda conclusão de todos (com tratamento de erros)
        results = await asyncio.gather(
            *tasks.values(),
            return_exceptions=True
        )
        
        # Processa resultados
        failed_agents = []
        for agent_name, result in zip(tasks.keys(), results):
            if isinstance(result, Exception):
                # Agente falhou, mas continuamos
                self._handle_agent_failure(context, agent_name, result)
                failed_agents.append(agent_name)
            else:
                # Agente completou com sucesso
                pass  # Contexto já foi atualizado pelo agente
        
        layer_duration = (datetime.now() - layer_start_time).total_seconds() * 1000
        
        # Log: Fim da camada
        if failed_agents:
            print(f"[ORCHESTRATOR] Layer {layer_num} completed with failures: {failed_agents}")
        else:
            print(f"[ORCHESTRATOR] Layer {layer_num} completed in {layer_duration:.0f}ms")
    
    def _handle_agent_failure(
        self,
        context: ExecutionContext,
        agent_name: str,
        error: Exception
    ) -> None:
        """
        Trata falha de um agente.
        
        Marca agente como failed e registra erro.
        Agentes dependentes receberão erro como input.
        """
        if agent_name in context.metadata:
            context.metadata[agent_name].status = ExecutionStatus.FAILED
            context.metadata[agent_name].error = str(error)
    
    def get_execution_plan(self) -> str:
        """Retorna plano de execução em formato legível"""
        plan_lines = ["Plano de Execução:"]
        
        for layer_idx, layer in enumerate(self.execution_layers, 1):
            agents_str = ", ".join(layer)
            plan_lines.append(f"  Camada {layer_idx} (paralelo): {agents_str}")
        
        return "\n".join(plan_lines)
    
    def __repr__(self) -> str:
        return f"BusinessOrchestrator({len(self.agents)} agents, {len(self.execution_layers)} layers)"


class ExecutionResult:
    """Resultado de uma execução"""
    
    def __init__(self, context: ExecutionContext):
        self.context = context
    
    @property
    def problem(self) -> str:
        return self.context.problem_description
    
    @property
    def results(self) -> Dict[str, str]:
        return self.context.results
    
    @property
    def metadata(self) -> Dict[str, any]:
        return {
            name: {
                "status": meta.status.value,
                "latency_ms": meta.latency_ms,
                "tokens": meta.total_tokens,
                "cost_usd": meta.cost_usd,
                "error": meta.error
            }
            for name, meta in self.context.metadata.items()
        }
    
    @property
    def total_cost(self) -> float:
        return self.context.get_total_cost()
    
    @property
    def total_tokens(self) -> int:
        return self.context.get_total_tokens()
    
    @property
    def total_latency_ms(self) -> float:
        return self.context.get_total_latency_ms()
    
    @property
    def success(self) -> bool:
        """Retorna True se todos os agentes completaram com sucesso"""
        return all(
            meta.status == ExecutionStatus.COMPLETED
            for meta in self.context.metadata.values()
        )
    
    def get_agent_output(self, agent_name: str) -> Optional[str]:
        return self.context.get_agent_output(agent_name)
    
    def __repr__(self) -> str:
        status = "✓ Success" if self.success else "✗ Partial Failure"
        return (
            f"ExecutionResult({status}, "
            f"latency={self.total_latency_ms:.0f}ms, "
            f"cost=${self.total_cost:.4f})"
        )
