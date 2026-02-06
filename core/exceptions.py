class BusinessTeamException(Exception):
    """Exceção base para o sistema de agentes"""
    pass


class AgentExecutionError(BusinessTeamException):
    """Erro durante execução de um agente"""
    def __init__(self, agent_name: str, message: str, original_error: Exception = None):
        self.agent_name = agent_name
        self.message = message
        self.original_error = original_error
        super().__init__(f"Agent '{agent_name}' failed: {message}")


class DAGError(BusinessTeamException):
    """Erro na resolução de dependências (DAG)"""
    pass


class CircularDependencyError(DAGError):
    """Dependência circular detectada"""
    def __init__(self, agents: list):
        self.agents = agents
        super().__init__(f"Circular dependency detected: {' -> '.join(agents)}")


class MissingDependencyError(DAGError):
    """Agente depende de agente inexistente"""
    def __init__(self, agent_name: str, missing_dependency: str):
        self.agent_name = agent_name
        self.missing_dependency = missing_dependency
        super().__init__(f"Agent '{agent_name}' depends on non-existent agent '{missing_dependency}'")


class PromptLoadError(BusinessTeamException):
    """Erro ao carregar prompt"""
    def __init__(self, agent_name: str, prompt_path: str):
        self.agent_name = agent_name
        self.prompt_path = prompt_path
        super().__init__(f"Failed to load prompt for agent '{agent_name}' at {prompt_path}")


class LLMProviderError(BusinessTeamException):
    """Erro ao comunicar com provider de LLM"""
    def __init__(self, message: str, status_code: int = None):
        self.message = message
        self.status_code = status_code
        super().__init__(f"LLM Provider error: {message}")


class TimeoutError(BusinessTeamException):
    """Timeout durante execução"""
    def __init__(self, agent_name: str, timeout_seconds: float):
        self.agent_name = agent_name
        self.timeout_seconds = timeout_seconds
        super().__init__(f"Agent '{agent_name}' timed out after {timeout_seconds}s")


class ValidationError(BusinessTeamException):
    """Erro de validação"""
    pass
