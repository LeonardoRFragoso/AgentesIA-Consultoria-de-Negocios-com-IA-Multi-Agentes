from typing import Dict, List, Set
from collections import defaultdict, deque

from core.exceptions import CircularDependencyError, MissingDependencyError


class DAGResolver:
    """Resolve dependências entre agentes e identifica paralelismo"""
    
    def __init__(self, agents: Dict[str, 'BaseAgent']):
        """
        Inicializa resolver com lista de agentes.
        
        Args:
            agents: Dict com {agent_name: agent_instance}
        """
        self.agents = agents
        self.agent_names = set(agents.keys())
        self._validate_dependencies()
    
    def _validate_dependencies(self) -> None:
        """Valida se todas as dependências existem e não há ciclos"""
        # Verifica se todas as dependências existem
        for agent_name, agent in self.agents.items():
            for dep in agent.dependencies:
                if dep not in self.agent_names:
                    raise MissingDependencyError(agent_name, dep)
        
        # Detecta ciclos
        self._detect_cycles()
    
    def _detect_cycles(self) -> None:
        """Detecta dependências circulares usando DFS"""
        visited = set()
        rec_stack = set()
        path = []
        
        def dfs(node: str) -> None:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in self.agents[node].dependencies:
                if neighbor not in visited:
                    dfs(neighbor)
                elif neighbor in rec_stack:
                    # Ciclo detectado
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    raise CircularDependencyError(cycle)
            
            path.pop()
            rec_stack.remove(node)
        
        for agent_name in self.agent_names:
            if agent_name not in visited:
                dfs(agent_name)
    
    def get_execution_layers(self) -> List[List[str]]:
        """
        Retorna agentes organizados em camadas para execução paralela.
        
        Agentes na mesma camada podem ser executados em paralelo.
        Camadas são executadas sequencialmente.
        
        Returns:
            Lista de listas: [[agentes_camada_1], [agentes_camada_2], ...]
        """
        # Calcula in-degree (número de dependências)
        in_degree = {agent: len(self.agents[agent].dependencies) for agent in self.agent_names}
        
        # Cria mapa reverso de dependências (quem depende de quem)
        dependents = defaultdict(list)
        for agent_name, agent in self.agents.items():
            for dep in agent.dependencies:
                dependents[dep].append(agent_name)
        
        layers = []
        queue = deque([agent for agent in self.agent_names if in_degree[agent] == 0])
        
        while queue:
            # Todos os agentes sem dependências não satisfeitas formam uma camada
            layer = list(queue)
            layers.append(layer)
            
            # Remove agentes da camada e atualiza in-degree dos dependentes
            new_queue = deque()
            for agent in layer:
                for dependent in dependents[agent]:
                    in_degree[dependent] -= 1
                    if in_degree[dependent] == 0:
                        new_queue.append(dependent)
            
            queue = new_queue
        
        return layers
    
    def get_dependencies(self, agent_name: str) -> List[str]:
        """Retorna dependências diretas de um agente"""
        return self.agents[agent_name].dependencies
    
    def get_dependents(self, agent_name: str) -> List[str]:
        """Retorna agentes que dependem deste"""
        return [
            name for name, agent in self.agents.items()
            if agent_name in agent.dependencies
        ]
    
    def __repr__(self) -> str:
        layers = self.get_execution_layers()
        layers_str = " → ".join(
            f"[{', '.join(layer)}]" for layer in layers
        )
        return f"DAG({layers_str})"
