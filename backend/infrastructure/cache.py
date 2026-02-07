"""
Redis Cache - Distributed caching for SaaS

Features:
- Redis como cache principal
- Fallback em memória para desenvolvimento
- Cache de análises repetidas
- Invalidação inteligente
- Monitoramento de hits/misses
"""

import json
import hashlib
import logging
from typing import Optional, Any, Callable
from datetime import datetime, timedelta
from functools import wraps
import pickle

logger = logging.getLogger(__name__)


class CacheStats:
    """Estatísticas de uso do cache."""
    
    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.errors = 0
        self.invalidations = 0
    
    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0
    
    def to_dict(self) -> dict:
        return {
            "hits": self.hits,
            "misses": self.misses,
            "errors": self.errors,
            "invalidations": self.invalidations,
            "hit_rate": f"{self.hit_rate:.2%}",
        }


class RedisCache:
    """
    Cache distribuído usando Redis.
    
    ONDE O CACHE ENTRA:
    1. Análises repetidas (mesmo problema + tipo + profundidade)
    2. Resultados de agentes individuais
    3. Status de billing por organização
    4. Rate limiting counters
    
    QUANDO INVALIDAR:
    1. Análise atualizada/deletada → invalidar por ID
    2. Plano da org alterado → invalidar billing cache
    3. TTL expirado → automático
    4. Deploy de nova versão → flush geral (opcional)
    """
    
    def __init__(self, redis_url: Optional[str] = None):
        self._redis = None
        self._memory_cache: dict = {}
        self._memory_expiry: dict = {}
        self.stats = CacheStats()
        
        if redis_url:
            try:
                import redis
                self._redis = redis.from_url(
                    redis_url,
                    decode_responses=False,  # Para suportar pickle
                    socket_timeout=5,
                    socket_connect_timeout=5,
                    retry_on_timeout=True,
                )
                # Testa conexão
                self._redis.ping()
                logger.info(f"Redis conectado: {redis_url.split('@')[-1]}")
            except Exception as e:
                logger.warning(f"Redis indisponível, usando fallback em memória: {e}")
                self._redis = None
    
    @property
    def is_redis_available(self) -> bool:
        return self._redis is not None
    
    def _serialize(self, value: Any) -> bytes:
        """Serializa valor para armazenamento."""
        return pickle.dumps(value)
    
    def _deserialize(self, data: bytes) -> Any:
        """Deserializa valor do armazenamento."""
        return pickle.loads(data)
    
    def _make_key(self, namespace: str, key: str) -> str:
        """Cria chave com namespace."""
        return f"cache:{namespace}:{key}"
    
    def get(self, namespace: str, key: str) -> Optional[Any]:
        """
        Busca valor no cache.
        
        Args:
            namespace: Categoria (ex: 'analysis', 'billing')
            key: Chave única
            
        Returns:
            Valor ou None se não encontrado/expirado
        """
        full_key = self._make_key(namespace, key)
        
        try:
            if self._redis:
                data = self._redis.get(full_key)
                if data:
                    self.stats.hits += 1
                    return self._deserialize(data)
            else:
                # Fallback memória
                if full_key in self._memory_cache:
                    expiry = self._memory_expiry.get(full_key)
                    if expiry is None or datetime.utcnow() < expiry:
                        self.stats.hits += 1
                        return self._memory_cache[full_key]
                    else:
                        # Expirado
                        del self._memory_cache[full_key]
                        del self._memory_expiry[full_key]
            
            self.stats.misses += 1
            return None
            
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            self.stats.errors += 1
            return None
    
    def set(
        self,
        namespace: str,
        key: str,
        value: Any,
        ttl_seconds: int = 3600
    ) -> bool:
        """
        Armazena valor no cache.
        
        Args:
            namespace: Categoria
            key: Chave única
            value: Valor a armazenar
            ttl_seconds: Tempo de vida em segundos
            
        Returns:
            True se sucesso
        """
        full_key = self._make_key(namespace, key)
        
        try:
            if self._redis:
                data = self._serialize(value)
                self._redis.setex(full_key, ttl_seconds, data)
            else:
                self._memory_cache[full_key] = value
                self._memory_expiry[full_key] = datetime.utcnow() + timedelta(seconds=ttl_seconds)
            
            return True
            
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            self.stats.errors += 1
            return False
    
    def delete(self, namespace: str, key: str) -> bool:
        """Remove item do cache."""
        full_key = self._make_key(namespace, key)
        
        try:
            if self._redis:
                self._redis.delete(full_key)
            else:
                self._memory_cache.pop(full_key, None)
                self._memory_expiry.pop(full_key, None)
            
            self.stats.invalidations += 1
            return True
            
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            self.stats.errors += 1
            return False
    
    def invalidate_pattern(self, namespace: str, pattern: str = "*") -> int:
        """
        Invalida múltiplas chaves por padrão.
        
        Uso: cache.invalidate_pattern("analysis", "org:123:*")
        """
        full_pattern = self._make_key(namespace, pattern)
        count = 0
        
        try:
            if self._redis:
                cursor = 0
                while True:
                    cursor, keys = self._redis.scan(cursor, match=full_pattern, count=100)
                    if keys:
                        self._redis.delete(*keys)
                        count += len(keys)
                    if cursor == 0:
                        break
            else:
                # Fallback memória
                keys_to_delete = [
                    k for k in self._memory_cache.keys()
                    if k.startswith(full_pattern.replace("*", ""))
                ]
                for k in keys_to_delete:
                    del self._memory_cache[k]
                    self._memory_expiry.pop(k, None)
                count = len(keys_to_delete)
            
            self.stats.invalidations += count
            logger.info(f"Invalidated {count} keys matching {full_pattern}")
            return count
            
        except Exception as e:
            logger.error(f"Cache invalidate_pattern error: {e}")
            self.stats.errors += 1
            return 0
    
    def flush_namespace(self, namespace: str) -> int:
        """Limpa todo o namespace."""
        return self.invalidate_pattern(namespace, "*")
    
    def health_check(self) -> dict:
        """Verifica saúde do cache."""
        result = {
            "backend": "redis" if self._redis else "memory",
            "status": "unknown",
            "stats": self.stats.to_dict(),
        }
        
        try:
            if self._redis:
                self._redis.ping()
                info = self._redis.info("memory")
                result["status"] = "healthy"
                result["memory_used"] = info.get("used_memory_human", "unknown")
            else:
                result["status"] = "healthy"
                result["items"] = len(self._memory_cache)
        except Exception as e:
            result["status"] = "unhealthy"
            result["error"] = str(e)
        
        return result


# =============================================================================
# CACHE KEYS HELPERS
# =============================================================================

class CacheKeys:
    """Helpers para gerar chaves de cache consistentes."""
    
    @staticmethod
    def analysis_result(problem: str, business_type: str, depth: str) -> str:
        """Chave para resultado de análise."""
        content = f"{problem}:{business_type}:{depth}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    @staticmethod
    def analysis_by_id(analysis_id: str) -> str:
        """Chave para análise por ID."""
        return f"id:{analysis_id}"
    
    @staticmethod
    def org_analyses(org_id: str) -> str:
        """Chave para lista de análises de uma org."""
        return f"org:{org_id}:list"
    
    @staticmethod
    def org_billing(org_id: str) -> str:
        """Chave para status de billing de uma org."""
        return f"billing:{org_id}"
    
    @staticmethod
    def agent_output(analysis_id: str, agent_name: str) -> str:
        """Chave para output de agente específico."""
        return f"agent:{analysis_id}:{agent_name}"


# =============================================================================
# DECORATORS
# =============================================================================

def cached(
    namespace: str,
    key_func: Callable[..., str],
    ttl_seconds: int = 3600
):
    """
    Decorator para cache de funções.
    
    Uso:
        @cached("analysis", lambda problem, **_: CacheKeys.analysis_result(problem), ttl=7200)
        async def run_analysis(problem: str, ...):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache = get_cache()
            key = key_func(*args, **kwargs)
            
            # Tenta cache
            cached_result = cache.get(namespace, key)
            if cached_result is not None:
                logger.debug(f"Cache hit: {namespace}:{key}")
                return cached_result
            
            # Executa função
            result = await func(*args, **kwargs)
            
            # Armazena no cache
            if result is not None:
                cache.set(namespace, key, result, ttl_seconds)
            
            return result
        return wrapper
    return decorator


# =============================================================================
# SINGLETON
# =============================================================================

_cache: Optional[RedisCache] = None


def init_cache(redis_url: Optional[str] = None) -> RedisCache:
    """Inicializa cache global."""
    global _cache
    
    if _cache is None:
        _cache = RedisCache(redis_url)
    
    return _cache


def get_cache() -> RedisCache:
    """Retorna instância do cache."""
    global _cache
    
    if _cache is None:
        from ..config import get_settings
        settings = get_settings()
        _cache = RedisCache(settings.REDIS_URL if hasattr(settings, 'REDIS_URL') else None)
    
    return _cache


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "RedisCache",
    "CacheKeys",
    "CacheStats",
    "cached",
    "init_cache",
    "get_cache",
]
