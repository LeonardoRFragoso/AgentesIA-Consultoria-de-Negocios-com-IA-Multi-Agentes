"""Cache manager for analysis results."""

import hashlib
import json
from typing import Optional, Dict, Any
from datetime import datetime, timedelta


class CacheManager:
    """
    Gerencia cache de resultados de análises.
    
    Implementação local em memória (pode ser estendida para Redis).
    """
    
    _instance: Optional["CacheManager"] = None
    
    def __init__(self, ttl_hours: int = 24):
        """
        Inicializa cache manager.
        
        Args:
            ttl_hours: Time-to-live em horas
        """
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl_hours = ttl_hours
    
    @staticmethod
    def _generate_key(problem_description: str, business_type: str, analysis_depth: str) -> str:
        """
        Gera chave de cache baseada em hash dos parâmetros.
        
        Args:
            problem_description: Descrição do problema
            business_type: Tipo de negócio
            analysis_depth: Profundidade da análise
        
        Returns:
            Chave de cache (hash)
        """
        key_str = f"{problem_description}:{business_type}:{analysis_depth}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(
        self,
        problem_description: str,
        business_type: str,
        analysis_depth: str
    ) -> Optional[Dict]:
        """
        Recupera resultado do cache se existir e não expirou.
        
        Args:
            problem_description: Descrição do problema
            business_type: Tipo de negócio
            analysis_depth: Profundidade da análise
        
        Returns:
            Dicionário com resultado ou None
        """
        key = self._generate_key(problem_description, business_type, analysis_depth)
        
        if key not in self.cache:
            return None
        
        cached = self.cache[key]
        
        # Verifica se expirou
        created_at = datetime.fromisoformat(cached['created_at'])
        if datetime.utcnow() - created_at > timedelta(hours=self.ttl_hours):
            del self.cache[key]
            return None
        
        return cached['result']
    
    def set(
        self,
        problem_description: str,
        business_type: str,
        analysis_depth: str,
        result: Dict
    ) -> None:
        """
        Armazena resultado em cache.
        
        Args:
            problem_description: Descrição do problema
            business_type: Tipo de negócio
            analysis_depth: Profundidade da análise
            result: Resultado a cachear
        """
        key = self._generate_key(problem_description, business_type, analysis_depth)
        
        self.cache[key] = {
            'result': result,
            'created_at': datetime.utcnow().isoformat(),
        }
    
    def clear(self) -> None:
        """Limpa todo o cache."""
        self.cache.clear()
    
    def get_stats(self) -> Dict:
        """Retorna estatísticas do cache."""
        return {
            'total_entries': len(self.cache),
            'ttl_hours': self.ttl_hours,
        }
    
    @classmethod
    def get_instance(cls, ttl_hours: int = 24) -> "CacheManager":
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = cls(ttl_hours)
        return cls._instance


def get_cache_manager(ttl_hours: int = 24) -> CacheManager:
    """Factory function para obter instância de cache manager."""
    return CacheManager.get_instance(ttl_hours)
