import asyncio
import os
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional
import anthropic
import traceback

from .types import ExecutionContext, AgentMetadata, ExecutionStatus
from .exceptions import PromptLoadError, AgentExecutionError, TimeoutError as TeamTimeoutError
from infrastructure.logging import get_logger

logger = get_logger(__name__)


class BaseAgent(ABC):
    """Classe base para todos os agentes"""
    
    def __init__(
        self,
        name: str,
        prompt_path: str,
        model: str = "claude-3-haiku-20240307",
        dependencies: Optional[List[str]] = None,
        timeout_seconds: float = 30.0,
        max_tokens: int = 1024
    ):
        """
        Inicializa um agente.
        
        Args:
            name: Nome único do agente
            prompt_path: Caminho para arquivo .md com prompt do sistema
            model: Modelo Claude a usar
            dependencies: Lista de nomes de agentes dos quais este depende
            timeout_seconds: Timeout para execução
            max_tokens: Máximo de tokens na resposta
        """
        self.name = name
        self.prompt_path = prompt_path
        self.model = model
        self.dependencies = dependencies or []
        self.timeout_seconds = timeout_seconds
        self.max_tokens = max_tokens
        self._prompt_cache: Optional[str] = None
    
    def _load_prompt(self) -> str:
        """Carrega prompt do arquivo (com cache)"""
        if self._prompt_cache is not None:
            return self._prompt_cache
        
        try:
            with open(self.prompt_path, "r", encoding="utf-8") as f:
                self._prompt_cache = f.read()
                return self._prompt_cache
        except FileNotFoundError:
            raise PromptLoadError(self.name, self.prompt_path)
        except Exception as e:
            raise PromptLoadError(self.name, self.prompt_path) from e
    
    def _build_user_message(self, context: ExecutionContext) -> str:
        """
        Constrói mensagem do usuário com contexto.
        Pode ser sobrescrito por subclasses.
        """
        return f"Problema: {context.problem_description}"
    
    def _build_context_message(self, context: ExecutionContext) -> str:
        """
        Constrói contexto com outputs de agentes anteriores.
        Usado para passar informações entre agentes.
        """
        context_parts = []
        
        for dep in self.dependencies:
            output = context.get_agent_output(dep)
            if output:
                context_parts.append(f"\n=== Análise de {dep} ===\n{output}")
            else:
                status = context.get_agent_status(dep)
                context_parts.append(f"\n=== {dep} ===\nStatus: {status.value}")
        
        return "".join(context_parts) if context_parts else ""
    
    async def execute(self, context: ExecutionContext) -> ExecutionContext:
        """
        Executa o agente de forma assíncrona.
        
        Args:
            context: Contexto compartilhado de execução
            
        Returns:
            Contexto atualizado com resultado do agente
        """
        metadata = AgentMetadata(name=self.name)
        metadata.status = ExecutionStatus.RUNNING
        metadata.start_time = datetime.now()
        
        # Log: Início da execução do agente
        logger.info(
            event="agent_started",
            message=f"Agent {self.name} started execution",
            execution_id=context.execution_id,
            agent_name=self.name,
            extra_data={
                "model": self.model,
                "timeout_seconds": self.timeout_seconds,
                "dependencies": self.dependencies
            }
        )
        
        try:
            # Executa com timeout
            result = await asyncio.wait_for(
                self._execute_internal(context),
                timeout=self.timeout_seconds
            )
            
            metadata.status = ExecutionStatus.COMPLETED
            metadata.end_time = datetime.now()
            
            # Atualiza contexto com resultado
            context.set_agent_output(self.name, result, metadata)
            
            # Log: Sucesso da execução
            logger.info(
                event="agent_completed",
                message=f"Agent {self.name} completed successfully",
                execution_id=context.execution_id,
                agent_name=self.name,
                duration_ms=metadata.duration_seconds * 1000,
                input_tokens=metadata.input_tokens,
                output_tokens=metadata.output_tokens,
                total_tokens=metadata.total_tokens,
                cost_usd=metadata.cost_usd,
                status="COMPLETED"
            )
            
            return context
            
        except asyncio.TimeoutError:
            metadata.status = ExecutionStatus.FAILED
            metadata.end_time = datetime.now()
            metadata.error = f"Timeout after {self.timeout_seconds}s"
            context.set_agent_output(self.name, "", metadata)
            
            # Log: Timeout
            logger.error(
                event="agent_timeout",
                message=f"Agent {self.name} timed out after {self.timeout_seconds}s",
                execution_id=context.execution_id,
                agent_name=self.name,
                duration_ms=metadata.duration_seconds * 1000,
                status="TIMEOUT",
                error=metadata.error
            )
            
            raise TeamTimeoutError(self.name, self.timeout_seconds)
            
        except Exception as e:
            metadata.status = ExecutionStatus.FAILED
            metadata.end_time = datetime.now()
            metadata.error = str(e)
            context.set_agent_output(self.name, "", metadata)
            
            # Log: Falha da execução
            logger.error(
                event="agent_failed",
                message=f"Agent {self.name} failed with error: {str(e)}",
                execution_id=context.execution_id,
                agent_name=self.name,
                duration_ms=metadata.duration_seconds * 1000,
                status="FAILED",
                error=str(e),
                extra_data={
                    "exception_type": type(e).__name__,
                    "stacktrace": traceback.format_exc()
                }
            )
            
            raise AgentExecutionError(self.name, str(e), e)
    
    async def _execute_internal(self, context: ExecutionContext) -> str:
        """
        Implementação interna da execução.
        Pode ser sobrescrita por subclasses para lógica customizada.
        """
        # Carrega prompt
        system_prompt = self._load_prompt()
        
        # Constrói mensagem do usuário
        user_message = self._build_user_message(context)
        
        # Adiciona contexto de agentes anteriores
        context_message = self._build_context_message(context)
        if context_message:
            user_message += context_message
        
        # Chama LLM
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
        message = client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_message}
            ]
        )
        
        # Extrai resposta
        return message.content[0].text
    
    def __repr__(self) -> str:
        deps_str = ", ".join(self.dependencies) if self.dependencies else "none"
        return f"{self.__class__.__name__}(name={self.name}, dependencies=[{deps_str}])"
