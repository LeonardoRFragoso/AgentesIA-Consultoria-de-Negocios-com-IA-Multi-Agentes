import logging
import json
import sys
from datetime import datetime
from typing import Any, Dict, Optional


class JSONFormatter(logging.Formatter):
    """Formatter que emite logs em formato JSON estruturado"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Formata record de log como JSON"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Adiciona campos extras do record
        if hasattr(record, "execution_id"):
            log_data["execution_id"] = record.execution_id
        
        if hasattr(record, "event"):
            log_data["event"] = record.event
        
        if hasattr(record, "agent_name"):
            log_data["agent_name"] = record.agent_name
        
        if hasattr(record, "duration_ms"):
            log_data["duration_ms"] = record.duration_ms
        
        if hasattr(record, "input_tokens"):
            log_data["input_tokens"] = record.input_tokens
        
        if hasattr(record, "output_tokens"):
            log_data["output_tokens"] = record.output_tokens
        
        if hasattr(record, "total_tokens"):
            log_data["total_tokens"] = record.total_tokens
        
        if hasattr(record, "cost_usd"):
            log_data["cost_usd"] = record.cost_usd
        
        if hasattr(record, "status"):
            log_data["status"] = record.status
        
        if hasattr(record, "error"):
            log_data["error"] = record.error
        
        if hasattr(record, "layer"):
            log_data["layer"] = record.layer
        
        if hasattr(record, "agents"):
            log_data["agents"] = record.agents
        
        if hasattr(record, "extra_data"):
            log_data.update(record.extra_data)
        
        # Adiciona exception se houver
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data, ensure_ascii=False)


class StructuredLogger:
    """Logger estruturado que facilita emissão de logs com campos específicos"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
    
    def log_event(
        self,
        level: int,
        event: str,
        message: str,
        execution_id: Optional[str] = None,
        agent_name: Optional[str] = None,
        duration_ms: Optional[float] = None,
        input_tokens: Optional[int] = None,
        output_tokens: Optional[int] = None,
        total_tokens: Optional[int] = None,
        cost_usd: Optional[float] = None,
        status: Optional[str] = None,
        error: Optional[str] = None,
        layer: Optional[int] = None,
        agents: Optional[list] = None,
        extra_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Emite um log estruturado com campos específicos.
        
        Args:
            level: Nível de log (logging.INFO, logging.ERROR, etc.)
            event: Tipo de evento
            message: Mensagem descritiva
            execution_id: ID da execução
            agent_name: Nome do agente (se aplicável)
            duration_ms: Duração em milissegundos
            input_tokens: Tokens de entrada
            output_tokens: Tokens de saída
            total_tokens: Total de tokens
            cost_usd: Custo em USD
            status: Status final
            error: Mensagem de erro
            layer: Número da camada
            agents: Lista de agentes
            extra_data: Dados extras para incluir
        """
        record = self.logger.makeRecord(
            name=self.logger.name,
            level=level,
            fn="",
            lno=0,
            msg=message,
            args=(),
            exc_info=None,
        )
        
        # Adiciona campos estruturados
        if execution_id:
            record.execution_id = execution_id
        if event:
            record.event = event
        if agent_name:
            record.agent_name = agent_name
        if duration_ms is not None:
            record.duration_ms = duration_ms
        if input_tokens is not None:
            record.input_tokens = input_tokens
        if output_tokens is not None:
            record.output_tokens = output_tokens
        if total_tokens is not None:
            record.total_tokens = total_tokens
        if cost_usd is not None:
            record.cost_usd = cost_usd
        if status:
            record.status = status
        if error:
            record.error = error
        if layer is not None:
            record.layer = layer
        if agents:
            record.agents = agents
        if extra_data:
            record.extra_data = extra_data
        
        self.logger.handle(record)
    
    def debug(self, event: str, message: str, **kwargs) -> None:
        """Log em nível DEBUG"""
        self.log_event(logging.DEBUG, event, message, **kwargs)
    
    def info(self, event: str, message: str, **kwargs) -> None:
        """Log em nível INFO"""
        self.log_event(logging.INFO, event, message, **kwargs)
    
    def warning(self, event: str, message: str, **kwargs) -> None:
        """Log em nível WARNING"""
        self.log_event(logging.WARNING, event, message, **kwargs)
    
    def error(self, event: str, message: str, **kwargs) -> None:
        """Log em nível ERROR"""
        self.log_event(logging.ERROR, event, message, **kwargs)
    
    def critical(self, event: str, message: str, **kwargs) -> None:
        """Log em nível CRITICAL"""
        self.log_event(logging.CRITICAL, event, message, **kwargs)


def configure_logging(level: int = logging.INFO) -> None:
    """
    Configura logging global com formato JSON.
    
    Args:
        level: Nível de log (padrão: INFO)
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Remove handlers existentes
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Cria handler para stdout
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    
    # Define formatter JSON
    formatter = JSONFormatter()
    handler.setFormatter(formatter)
    
    # Adiciona handler ao root logger
    root_logger.addHandler(handler)


def get_logger(name: str) -> StructuredLogger:
    """
    Obtém um logger estruturado.
    
    Args:
        name: Nome do logger (geralmente __name__)
    
    Returns:
        StructuredLogger configurado
    """
    return StructuredLogger(name)
