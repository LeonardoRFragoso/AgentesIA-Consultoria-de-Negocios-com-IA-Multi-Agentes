"""
Async Analysis Service - Processamento não-bloqueante com cache

FLUXO:
1. Request chega → Verifica cache
2. Cache hit → Retorna imediatamente
3. Cache miss → Enfileira task → Retorna task_id
4. Worker processa → Salva resultado → Atualiza cache
5. Cliente faz polling ou webhook

NÃO BLOQUEIA HTTP - análises longas rodam em background.
"""

import logging
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID

from ..database import tenant_session, Analysis, AgentOutput
from ..database.models import AnalysisStatus
from ..infrastructure.cache import get_cache, CacheKeys
from ..infrastructure.queue import get_queue, TaskTypes, TaskStatus, TaskResult

logger = logging.getLogger(__name__)


# Cache TTL em segundos
CACHE_TTL_ANALYSIS_RESULT = 7200  # 2 horas
CACHE_TTL_ANALYSIS_LIST = 300    # 5 minutos


class AsyncAnalysisService:
    """
    Serviço de análise com cache e processamento assíncrono.
    
    ONDE O CACHE ENTRA:
    - Análises com mesmo problema/tipo/profundidade
    - Lista de análises por organização
    - Resultados individuais por ID
    
    QUANDO INVALIDAR:
    - Nova análise criada → invalida lista
    - Análise atualizada → invalida por ID
    - Análise deletada → invalida ID + lista
    """
    
    def __init__(self, org_id: str, user_id: str):
        self.org_id = org_id
        self.user_id = user_id
        self.cache = get_cache()
        self.queue = get_queue()
    
    def create_analysis(
        self,
        problem_description: str,
        business_type: str = "B2B",
        analysis_depth: str = "Padrão",
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Cria análise e enfileira para processamento.
        
        Args:
            problem_description: Descrição do problema
            business_type: Tipo de negócio
            analysis_depth: Profundidade
            use_cache: Se True, verifica cache primeiro
            
        Returns:
            {
                "analysis_id": str,
                "status": "pending" | "cached",
                "task_id": str | None,
                "cached": bool,
                "result": dict | None  # Se cached
            }
        """
        # 1. Verifica cache (análises repetidas)
        if use_cache:
            cache_key = CacheKeys.analysis_result(
                problem_description, business_type, analysis_depth
            )
            cached_result = self.cache.get("analysis", cache_key)
            
            if cached_result:
                logger.info(f"Cache hit para análise similar")
                return {
                    "analysis_id": cached_result.get("analysis_id"),
                    "status": "cached",
                    "task_id": None,
                    "cached": True,
                    "result": cached_result,
                }
        
        # 2. Cria registro no banco
        with tenant_session(self.org_id) as db:
            analysis = Analysis(
                problem_description=problem_description,
                business_type=business_type,
                analysis_depth=analysis_depth,
                created_by=UUID(self.user_id),
                status=AnalysisStatus.PENDING,
            )
            db.add(analysis)
            db.commit()
            analysis_id = str(analysis.id)
        
        # 3. Enfileira para processamento em background
        task_id = self.queue.enqueue(
            task_type=TaskTypes.ANALYSIS_EXECUTE,
            payload={
                "analysis_id": analysis_id,
                "problem_description": problem_description,
                "business_type": business_type,
                "analysis_depth": analysis_depth,
            },
            org_id=self.org_id,
            user_id=self.user_id,
        )
        
        # 4. Invalida cache de lista
        self.cache.delete("analysis", CacheKeys.org_analyses(self.org_id))
        
        logger.info(f"Análise criada: {analysis_id}, task: {task_id}")
        
        return {
            "analysis_id": analysis_id,
            "status": "pending",
            "task_id": task_id,
            "cached": False,
            "result": None,
        }
    
    def get_analysis(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """
        Busca análise por ID, com cache.
        """
        cache_key = CacheKeys.analysis_by_id(analysis_id)
        
        # Tenta cache
        cached = self.cache.get("analysis", cache_key)
        if cached:
            return cached
        
        # Busca no banco
        with tenant_session(self.org_id) as db:
            analysis = db.get(Analysis, UUID(analysis_id))
            
            if not analysis:
                return None
            
            result = self._serialize_analysis(analysis)
        
        # Armazena no cache apenas se completada
        if result["status"] == "completed":
            self.cache.set("analysis", cache_key, result, CACHE_TTL_ANALYSIS_RESULT)
        
        return result
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Verifica status de uma task de análise.
        
        Uso para polling:
            while True:
                status = service.get_task_status(task_id)
                if status["status"] in ["completed", "failed"]:
                    break
                await asyncio.sleep(2)
        """
        result = self.queue.get_result(task_id)
        
        if not result:
            task_info = self.queue.get_status(task_id)
            if task_info:
                return {
                    "task_id": task_id,
                    "status": task_info.status.value,
                    "created_at": task_info.created_at.isoformat() if task_info.created_at else None,
                }
            return None
        
        return {
            "task_id": task_id,
            "status": result.status.value,
            "result": result.result,
            "error": result.error,
            "duration_ms": result.duration_ms,
            "completed_at": result.completed_at.isoformat() if result.completed_at else None,
        }
    
    def list_analyses(
        self,
        limit: int = 20,
        offset: int = 0,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Lista análises da organização, com cache.
        """
        # Cache key inclui parâmetros
        cache_key = f"{CacheKeys.org_analyses(self.org_id)}:{limit}:{offset}:{status or 'all'}"
        
        # Tenta cache
        cached = self.cache.get("analysis", cache_key)
        if cached:
            return cached
        
        # Busca no banco
        with tenant_session(self.org_id) as db:
            query = db.query(Analysis).order_by(Analysis.created_at.desc())
            
            if status:
                query = query.filter(Analysis.status == status)
            
            total = query.count()
            analyses = query.limit(limit).offset(offset).all()
            
            result = {
                "items": [self._serialize_analysis(a, include_results=False) for a in analyses],
                "total": total,
                "limit": limit,
                "offset": offset,
            }
        
        # Cache por 5 minutos
        self.cache.set("analysis", cache_key, result, CACHE_TTL_ANALYSIS_LIST)
        
        return result
    
    def delete_analysis(self, analysis_id: str) -> bool:
        """
        Deleta análise e invalida caches relacionados.
        """
        with tenant_session(self.org_id) as db:
            analysis = db.get(Analysis, UUID(analysis_id))
            
            if not analysis:
                return False
            
            db.delete(analysis)
            db.commit()
        
        # Invalida caches
        self.cache.delete("analysis", CacheKeys.analysis_by_id(analysis_id))
        self.cache.delete("analysis", CacheKeys.org_analyses(self.org_id))
        
        # Invalida cache de análise similar
        # (não temos os parâmetros originais, então invalidamos por padrão)
        self.cache.invalidate_pattern("analysis", f"org:{self.org_id}:*")
        
        logger.info(f"Análise deletada: {analysis_id}")
        return True
    
    def _serialize_analysis(self, analysis: Analysis, include_results: bool = True) -> Dict[str, Any]:
        """Serializa análise para resposta."""
        data = {
            "id": str(analysis.id),
            "problem_description": analysis.problem_description,
            "business_type": analysis.business_type,
            "analysis_depth": analysis.analysis_depth,
            "status": analysis.status.value if hasattr(analysis.status, 'value') else analysis.status,
            "executive_summary": analysis.executive_summary,
            "total_tokens": analysis.total_tokens,
            "total_cost_usd": analysis.total_cost_usd,
            "total_latency_ms": analysis.total_latency_ms,
            "created_at": analysis.created_at.isoformat() if analysis.created_at else None,
            "completed_at": analysis.completed_at.isoformat() if analysis.completed_at else None,
        }
        
        if include_results and analysis.results:
            data["results"] = analysis.results
        
        if analysis.error_message:
            data["error_message"] = analysis.error_message
        
        return data


# =============================================================================
# TASK HANDLER
# =============================================================================

async def handle_analysis_task(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handler para task de análise.
    Executado pelo worker em background.
    """
    from ..database import get_db_session
    from ..database.models import AnalysisStatus
    
    analysis_id = payload["analysis_id"]
    
    logger.info(f"Iniciando análise: {analysis_id}")
    
    try:
        # Atualiza status para running
        with get_db_session() as db:
            analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
            if not analysis:
                raise ValueError(f"Análise não encontrada: {analysis_id}")
            
            analysis.status = AnalysisStatus.RUNNING
            analysis.started_at = datetime.utcnow()
            db.commit()
            
            org_id = str(analysis.org_id)
        
        # Executa orquestrador multi-agentes
        from team.business_team import BusinessTeam
        
        team = BusinessTeam()
        results = team.run_analysis(
            problem=payload["problem_description"],
            business_type=payload["business_type"],
            analysis_depth=payload["analysis_depth"],
        )
        
        # Salva resultados
        with get_db_session() as db:
            analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
            
            analysis.status = AnalysisStatus.COMPLETED
            analysis.completed_at = datetime.utcnow()
            analysis.results = results.get("results", {})
            analysis.executive_summary = results.get("executive_summary", "")
            analysis.total_tokens = results.get("total_tokens", 0)
            analysis.total_cost_usd = results.get("total_cost", 0.0)
            analysis.total_latency_ms = results.get("total_latency_ms", 0.0)
            
            db.commit()
            
            serialized = {
                "analysis_id": str(analysis.id),
                "status": "completed",
                "results": analysis.results,
                "executive_summary": analysis.executive_summary,
            }
        
        # Atualiza cache
        cache = get_cache()
        cache_key = CacheKeys.analysis_result(
            payload["problem_description"],
            payload["business_type"],
            payload["analysis_depth"],
        )
        cache.set("analysis", cache_key, serialized, CACHE_TTL_ANALYSIS_RESULT)
        cache.set("analysis", CacheKeys.analysis_by_id(analysis_id), serialized, CACHE_TTL_ANALYSIS_RESULT)
        
        logger.info(f"Análise completada: {analysis_id}")
        return serialized
        
    except Exception as e:
        logger.error(f"Erro na análise {analysis_id}: {e}")
        
        # Marca como falha
        with get_db_session() as db:
            analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
            if analysis:
                analysis.status = AnalysisStatus.FAILED
                analysis.error_message = str(e)
                analysis.completed_at = datetime.utcnow()
                db.commit()
        
        raise


def register_task_handlers():
    """Registra handlers de tasks na fila."""
    queue = get_queue()
    
    if hasattr(queue, 'register_handler'):
        queue.register_handler(TaskTypes.ANALYSIS_EXECUTE, handle_analysis_task)
        logger.info("Task handlers registrados")


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "AsyncAnalysisService",
    "handle_analysis_task",
    "register_task_handlers",
]
