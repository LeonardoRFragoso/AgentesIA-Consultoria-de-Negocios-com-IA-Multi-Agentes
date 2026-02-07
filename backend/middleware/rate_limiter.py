"""
Rate limiting middleware usando Redis.
Protege contra abuso de API.
"""

import time
from typing import Optional, Tuple
from fastapi import Request, HTTPException, status


class RateLimiter:
    """
    Rate limiter baseado em sliding window com Redis.
    
    Implementa limites por:
    - IP (para endpoints públicos)
    - User ID (para endpoints autenticados)
    - Org ID (para limites de plano)
    """
    
    def __init__(self, redis_client=None):
        """
        Args:
            redis_client: Cliente Redis. Se None, usa fallback em memória.
        """
        self.redis = redis_client
        self._memory_store = {}  # Fallback se Redis não disponível
    
    def _get_key(self, identifier: str, endpoint: str) -> str:
        """Gera chave para o rate limiter."""
        return f"ratelimit:{endpoint}:{identifier}"
    
    def _parse_limit(self, limit_str: str) -> Tuple[int, int]:
        """
        Parseia string de limite.
        
        Args:
            limit_str: Ex: "10/minute", "100/hour", "1000/day"
            
        Returns:
            Tuple[requests, seconds]
        """
        parts = limit_str.split("/")
        count = int(parts[0])
        
        period_map = {
            "second": 1,
            "minute": 60,
            "hour": 3600,
            "day": 86400,
        }
        
        period = period_map.get(parts[1], 60)
        return count, period
    
    def check_rate_limit(
        self,
        identifier: str,
        endpoint: str,
        limit: str
    ) -> Tuple[bool, dict]:
        """
        Verifica se request está dentro do limite.
        
        Args:
            identifier: IP, user_id ou org_id
            endpoint: Nome do endpoint
            limit: Limite em formato "X/period"
            
        Returns:
            Tuple[allowed, headers]
            headers contém X-RateLimit-* para resposta
        """
        max_requests, window_seconds = self._parse_limit(limit)
        key = self._get_key(identifier, endpoint)
        now = time.time()
        
        if self.redis:
            return self._check_redis(key, max_requests, window_seconds, now)
        else:
            return self._check_memory(key, max_requests, window_seconds, now)
    
    def _check_memory(
        self,
        key: str,
        max_requests: int,
        window_seconds: int,
        now: float
    ) -> Tuple[bool, dict]:
        """Fallback em memória para desenvolvimento."""
        # Limpa entradas antigas
        window_start = now - window_seconds
        
        if key not in self._memory_store:
            self._memory_store[key] = []
        
        # Remove timestamps fora da janela
        self._memory_store[key] = [
            ts for ts in self._memory_store[key]
            if ts > window_start
        ]
        
        current_count = len(self._memory_store[key])
        remaining = max(0, max_requests - current_count - 1)
        
        headers = {
            "X-RateLimit-Limit": str(max_requests),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(int(now + window_seconds)),
        }
        
        if current_count >= max_requests:
            headers["Retry-After"] = str(window_seconds)
            return False, headers
        
        # Registra request
        self._memory_store[key].append(now)
        
        return True, headers
    
    def _check_redis(
        self,
        key: str,
        max_requests: int,
        window_seconds: int,
        now: float
    ) -> Tuple[bool, dict]:
        """Rate limiting com Redis usando sliding window."""
        window_start = now - window_seconds
        
        pipe = self.redis.pipeline()
        
        # Remove timestamps antigos
        pipe.zremrangebyscore(key, 0, window_start)
        
        # Conta requests na janela
        pipe.zcard(key)
        
        # Adiciona timestamp atual
        pipe.zadd(key, {str(now): now})
        
        # Define TTL
        pipe.expire(key, window_seconds)
        
        results = pipe.execute()
        current_count = results[1]
        
        remaining = max(0, max_requests - current_count - 1)
        
        headers = {
            "X-RateLimit-Limit": str(max_requests),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(int(now + window_seconds)),
        }
        
        if current_count >= max_requests:
            # Remove o timestamp que acabamos de adicionar
            self.redis.zrem(key, str(now))
            headers["Retry-After"] = str(window_seconds)
            return False, headers
        
        return True, headers


# Instância global
_rate_limiter: Optional[RateLimiter] = None


def get_rate_limiter() -> RateLimiter:
    """Factory para rate limiter."""
    global _rate_limiter
    
    if _rate_limiter is None:
        # Tenta conectar ao Redis
        try:
            import redis
            from ..config import get_settings
            
            settings = get_settings()
            client = redis.from_url(settings.REDIS_URL)
            client.ping()  # Testa conexão
            _rate_limiter = RateLimiter(redis_client=client)
        except Exception:
            # Fallback para memória
            _rate_limiter = RateLimiter(redis_client=None)
    
    return _rate_limiter


async def rate_limit_dependency(
    request: Request,
    limit: str = "60/minute"
):
    """
    Dependency para rate limiting por IP.
    
    Uso:
        @app.get("/public-endpoint")
        async def endpoint(
            _: None = Depends(lambda r: rate_limit_dependency(r, "10/minute"))
        ):
            ...
    """
    limiter = get_rate_limiter()
    
    # Usa IP do request
    client_ip = request.client.host if request.client else "unknown"
    
    # Verifica headers de proxy
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        client_ip = forwarded.split(",")[0].strip()
    
    allowed, headers = limiter.check_rate_limit(
        identifier=client_ip,
        endpoint=request.url.path,
        limit=limit
    )
    
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later.",
            headers=headers
        )
