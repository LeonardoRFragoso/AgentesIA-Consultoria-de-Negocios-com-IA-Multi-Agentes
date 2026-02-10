"""
Task Queue - Processamento assíncrono de análises

Alternativas implementadas:
1. Redis Queue (RQ) - Simples, recomendado
2. Background Tasks (FastAPI) - Para casos simples
3. In-memory queue - Fallback para desenvolvimento

NÃO BLOQUEIA requisições HTTP - análises rodam em background.
"""

import asyncio
import logging
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, Callable, List
from concurrent.futures import ThreadPoolExecutor
import threading
import queue
import traceback

logger = logging.getLogger(__name__)


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class TaskResult:
    """Resultado de uma task."""
    task_id: str
    status: TaskStatus
    result: Optional[Any] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_ms: float = 0.0


@dataclass
class TaskInfo:
    """Informações de uma task na fila."""
    task_id: str
    task_type: str
    status: TaskStatus
    payload: Dict[str, Any]
    org_id: str
    user_id: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    retries: int = 0
    max_retries: int = 3


class TaskQueue(ABC):
    """Interface abstrata para fila de tasks."""
    
    @abstractmethod
    def enqueue(
        self,
        task_type: str,
        payload: Dict[str, Any],
        org_id: str,
        user_id: str,
        priority: int = 0
    ) -> str:
        """Adiciona task à fila. Retorna task_id."""
        pass
    
    @abstractmethod
    def get_status(self, task_id: str) -> Optional[TaskInfo]:
        """Retorna status de uma task."""
        pass
    
    @abstractmethod
    def get_result(self, task_id: str) -> Optional[TaskResult]:
        """Retorna resultado de uma task."""
        pass
    
    @abstractmethod
    def cancel(self, task_id: str) -> bool:
        """Cancela uma task pendente."""
        pass


# =============================================================================
# IN-MEMORY QUEUE (Desenvolvimento/Fallback)
# =============================================================================

class InMemoryQueue(TaskQueue):
    """
    Fila em memória para desenvolvimento.
    Tasks executam em ThreadPool para não bloquear.
    
    LIMITAÇÕES:
    - Não persiste entre restarts
    - Não distribui entre workers
    - Não escala horizontalmente
    """
    
    def __init__(self, max_workers: int = 4):
        self._tasks: Dict[str, TaskInfo] = {}
        self._handlers: Dict[str, Callable] = {}
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._lock = threading.Lock()
        logger.info(f"InMemoryQueue inicializada com {max_workers} workers")
    
    def register_handler(self, task_type: str, handler: Callable):
        """Registra handler para tipo de task."""
        self._handlers[task_type] = handler
        logger.info(f"Handler registrado: {task_type}")
    
    def enqueue(
        self,
        task_type: str,
        payload: Dict[str, Any],
        org_id: str,
        user_id: str,
        priority: int = 0
    ) -> str:
        """Adiciona task e inicia execução assíncrona."""
        task_id = str(uuid.uuid4())
        
        task_info = TaskInfo(
            task_id=task_id,
            task_type=task_type,
            status=TaskStatus.PENDING,
            payload=payload,
            org_id=org_id,
            user_id=user_id,
        )
        
        with self._lock:
            self._tasks[task_id] = task_info
        
        # Submete para execução em background
        self._executor.submit(self._execute_task, task_id)
        
        logger.info(f"Task enqueued: {task_id} ({task_type})")
        return task_id
    
    def _execute_task(self, task_id: str):
        """Executa task em thread separada."""
        task = self._tasks.get(task_id)
        if not task:
            return
        
        handler = self._handlers.get(task.task_type)
        if not handler:
            logger.error(f"No handler for task type: {task.task_type}")
            task.status = TaskStatus.FAILED
            task.error = f"Unknown task type: {task.task_type}"
            return
        
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.utcnow()
        
        try:
            # Executa handler
            if asyncio.iscoroutinefunction(handler):
                # Handler async - cria event loop
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(handler(task.payload))
                finally:
                    loop.close()
            else:
                result = handler(task.payload)
            
            task.status = TaskStatus.COMPLETED
            task.result = result
            task.completed_at = datetime.utcnow()
            
            logger.info(f"Task completed: {task_id}")
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.completed_at = datetime.utcnow()
            logger.error(f"Task failed: {task_id} - {e}\n{traceback.format_exc()}")
    
    def get_status(self, task_id: str) -> Optional[TaskInfo]:
        return self._tasks.get(task_id)
    
    def get_result(self, task_id: str) -> Optional[TaskResult]:
        task = self._tasks.get(task_id)
        if not task:
            return None
        
        duration = 0.0
        if task.started_at and task.completed_at:
            duration = (task.completed_at - task.started_at).total_seconds() * 1000
        
        return TaskResult(
            task_id=task_id,
            status=task.status,
            result=task.result,
            error=task.error,
            started_at=task.started_at,
            completed_at=task.completed_at,
            duration_ms=duration,
        )
    
    def cancel(self, task_id: str) -> bool:
        task = self._tasks.get(task_id)
        if task and task.status == TaskStatus.PENDING:
            task.status = TaskStatus.CANCELLED
            return True
        return False
    
    def get_queue_stats(self) -> dict:
        """Estatísticas da fila."""
        with self._lock:
            tasks = list(self._tasks.values())
        
        return {
            "total": len(tasks),
            "pending": sum(1 for t in tasks if t.status == TaskStatus.PENDING),
            "running": sum(1 for t in tasks if t.status == TaskStatus.RUNNING),
            "completed": sum(1 for t in tasks if t.status == TaskStatus.COMPLETED),
            "failed": sum(1 for t in tasks if t.status == TaskStatus.FAILED),
        }


# =============================================================================
# REDIS QUEUE (Produção)
# =============================================================================

class RedisQueue(TaskQueue):
    """
    Fila usando Redis para produção.
    
    Vantagens:
    - Persiste entre restarts
    - Suporta múltiplos workers
    - Escala horizontalmente
    """
    
    QUEUE_KEY = "taskqueue:pending"
    TASK_KEY_PREFIX = "taskqueue:task:"
    RESULT_KEY_PREFIX = "taskqueue:result:"
    
    def __init__(self, redis_url: str, max_workers: int = 4):
        import redis
        self._redis = redis.from_url(redis_url, decode_responses=True)
        self._handlers: Dict[str, Callable] = {}
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._running = False
        self._worker_thread: Optional[threading.Thread] = None
        logger.info("RedisQueue inicializada")
    
    def register_handler(self, task_type: str, handler: Callable):
        self._handlers[task_type] = handler
    
    def start_worker(self):
        """Inicia worker para processar tasks."""
        if self._running:
            return
        
        self._running = True
        self._worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self._worker_thread.start()
        logger.info("Redis worker started")
    
    def stop_worker(self):
        """Para o worker."""
        self._running = False
        if self._worker_thread:
            self._worker_thread.join(timeout=5)
    
    def _worker_loop(self):
        """Loop principal do worker."""
        from config import get_settings
        settings = get_settings()
        
        while self._running:
            try:
                # Blocking pop com timeout
                result = self._redis.brpop(self.QUEUE_KEY, timeout=1)
                if result:
                    _, task_id = result
                    self._executor.submit(self._process_task, task_id)
            except Exception as e:
                # Apenas log em produção - em dev, Redis é opcional
                if settings.is_production():
                    logger.error(f"Worker error: {e}")
                else:
                    logger.debug(f"Worker error (development - Redis optional): {e}")
    
    def _process_task(self, task_id: str):
        """Processa uma task."""
        task_data = self._redis.hgetall(f"{self.TASK_KEY_PREFIX}{task_id}")
        if not task_data:
            return
        
        task_type = task_data.get("task_type")
        handler = self._handlers.get(task_type)
        
        if not handler:
            self._save_result(task_id, TaskStatus.FAILED, error=f"Unknown type: {task_type}")
            return
        
        # Atualiza status
        self._redis.hset(f"{self.TASK_KEY_PREFIX}{task_id}", "status", TaskStatus.RUNNING.value)
        
        try:
            import json
            payload = json.loads(task_data.get("payload", "{}"))
            
            if asyncio.iscoroutinefunction(handler):
                loop = asyncio.new_event_loop()
                try:
                    result = loop.run_until_complete(handler(payload))
                finally:
                    loop.close()
            else:
                result = handler(payload)
            
            self._save_result(task_id, TaskStatus.COMPLETED, result=result)
            
        except Exception as e:
            self._save_result(task_id, TaskStatus.FAILED, error=str(e))
    
    def _save_result(self, task_id: str, status: TaskStatus, result=None, error=None):
        """Salva resultado da task."""
        import json
        
        self._redis.hset(f"{self.TASK_KEY_PREFIX}{task_id}", mapping={
            "status": status.value,
            "completed_at": datetime.utcnow().isoformat(),
        })
        
        result_data = {
            "status": status.value,
            "result": json.dumps(result) if result else None,
            "error": error,
        }
        self._redis.hset(f"{self.RESULT_KEY_PREFIX}{task_id}", mapping=result_data)
        self._redis.expire(f"{self.RESULT_KEY_PREFIX}{task_id}", 86400)  # 24h
    
    def enqueue(
        self,
        task_type: str,
        payload: Dict[str, Any],
        org_id: str,
        user_id: str,
        priority: int = 0
    ) -> str:
        import json
        
        task_id = str(uuid.uuid4())
        
        # Salva dados da task
        self._redis.hset(f"{self.TASK_KEY_PREFIX}{task_id}", mapping={
            "task_id": task_id,
            "task_type": task_type,
            "status": TaskStatus.PENDING.value,
            "payload": json.dumps(payload),
            "org_id": org_id,
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
        })
        
        # Adiciona à fila
        if priority > 0:
            self._redis.lpush(self.QUEUE_KEY, task_id)  # Alta prioridade no início
        else:
            self._redis.rpush(self.QUEUE_KEY, task_id)  # Normal no final
        
        logger.info(f"Task enqueued (Redis): {task_id}")
        return task_id
    
    def get_status(self, task_id: str) -> Optional[TaskInfo]:
        data = self._redis.hgetall(f"{self.TASK_KEY_PREFIX}{task_id}")
        if not data:
            return None
        
        import json
        return TaskInfo(
            task_id=data.get("task_id", task_id),
            task_type=data.get("task_type", ""),
            status=TaskStatus(data.get("status", "pending")),
            payload=json.loads(data.get("payload", "{}")),
            org_id=data.get("org_id", ""),
            user_id=data.get("user_id", ""),
        )
    
    def get_result(self, task_id: str) -> Optional[TaskResult]:
        data = self._redis.hgetall(f"{self.RESULT_KEY_PREFIX}{task_id}")
        if not data:
            return None
        
        import json
        return TaskResult(
            task_id=task_id,
            status=TaskStatus(data.get("status", "pending")),
            result=json.loads(data["result"]) if data.get("result") else None,
            error=data.get("error"),
        )
    
    def cancel(self, task_id: str) -> bool:
        status = self._redis.hget(f"{self.TASK_KEY_PREFIX}{task_id}", "status")
        if status == TaskStatus.PENDING.value:
            self._redis.hset(f"{self.TASK_KEY_PREFIX}{task_id}", "status", TaskStatus.CANCELLED.value)
            self._redis.lrem(self.QUEUE_KEY, 0, task_id)
            return True
        return False


# =============================================================================
# SINGLETON E FACTORY
# =============================================================================

_queue: Optional[TaskQueue] = None


def init_queue(redis_url: Optional[str] = None, start_worker: bool = True) -> TaskQueue:
    """Inicializa fila global."""
    global _queue
    
    if _queue is not None:
        return _queue
    
    if redis_url:
        try:
            _queue = RedisQueue(redis_url)
            if start_worker:
                _queue.start_worker()
        except Exception as e:
            logger.warning(f"Redis Queue indisponível, usando InMemory: {e}")
            _queue = InMemoryQueue()
    else:
        _queue = InMemoryQueue()
    
    return _queue


def get_queue() -> TaskQueue:
    """Retorna instância da fila."""
    global _queue
    
    if _queue is None:
        _queue = InMemoryQueue()
    
    return _queue


# =============================================================================
# TASK TYPES
# =============================================================================

class TaskTypes:
    """Tipos de tasks disponíveis."""
    ANALYSIS_EXECUTE = "analysis:execute"
    ANALYSIS_EXPORT = "analysis:export"
    REPORT_GENERATE = "report:generate"
    EMAIL_SEND = "email:send"


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "TaskQueue",
    "InMemoryQueue",
    "RedisQueue",
    "TaskInfo",
    "TaskResult",
    "TaskStatus",
    "TaskTypes",
    "init_queue",
    "get_queue",
]
