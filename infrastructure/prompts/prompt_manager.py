"""Gerenciador de prompts dinâmicos com templates."""

import os
from typing import Optional, Dict
from jinja2 import Template, TemplateError


class PromptManager:
    """
    Gerencia prompts dinâmicos com suporte a templates.
    
    Permite customizar prompts baseado em:
    - business_type
    - analysis_depth
    - industry
    - custom_variables
    """
    
    def __init__(self, prompts_dir: str = "prompts"):
        """
        Inicializa gerenciador de prompts.
        
        Args:
            prompts_dir: Diretório com arquivos de prompt
        """
        self.prompts_dir = prompts_dir
        self._cache: Dict[str, str] = {}
    
    def load_prompt(
        self,
        agent_name: str,
        business_type: str = "B2B",
        analysis_depth: str = "Padrão",
        industry: Optional[str] = None,
        **custom_vars
    ) -> str:
        """
        Carrega prompt com variáveis substituídas.
        
        Args:
            agent_name: Nome do agente (ex: "analyst", "commercial")
            business_type: Tipo de negócio (B2B, SaaS, Varejo, etc.)
            analysis_depth: Profundidade (Rápida, Padrão, Profunda)
            industry: Indústria específica (opcional)
            **custom_vars: Variáveis customizadas adicionais
        
        Returns:
            Prompt renderizado com variáveis substituídas
        """
        # Carrega arquivo base
        prompt_path = os.path.join(self.prompts_dir, f"{agent_name}.md")
        
        if not os.path.exists(prompt_path):
            raise FileNotFoundError(f"Prompt não encontrado: {prompt_path}")
        
        with open(prompt_path, 'r', encoding='utf-8') as f:
            template_str = f.read()
        
        # Prepara variáveis
        variables = {
            'business_type': business_type,
            'analysis_depth': analysis_depth,
            'industry': industry or business_type,
            'depth_description': self._get_depth_description(analysis_depth),
            **custom_vars
        }
        
        # Renderiza template
        try:
            template = Template(template_str)
            return template.render(**variables)
        except TemplateError as e:
            raise RuntimeError(f"Erro ao renderizar prompt {agent_name}: {str(e)}")
    
    def _get_depth_description(self, depth: str) -> str:
        """
        Retorna descrição da profundidade de análise.
        
        Args:
            depth: Profundidade (Rápida, Padrão, Profunda)
        
        Returns:
            Descrição textual
        """
        descriptions = {
            "Rápida": "análise rápida e resumida, focando nos pontos principais",
            "Padrão": "análise equilibrada com profundidade moderada",
            "Profunda": "análise detalhada e abrangente, considerando múltiplas perspectivas",
        }
        return descriptions.get(depth, "análise padrão")
    
    def get_system_prompt_for_agent(
        self,
        agent_name: str,
        business_type: str = "B2B",
        analysis_depth: str = "Padrão",
    ) -> str:
        """
        Obtém prompt de sistema para um agente.
        
        Compatível com BaseAgent._load_prompt().
        
        Args:
            agent_name: Nome do agente
            business_type: Tipo de negócio
            analysis_depth: Profundidade da análise
        
        Returns:
            Prompt de sistema renderizado
        """
        return self.load_prompt(
            agent_name,
            business_type=business_type,
            analysis_depth=analysis_depth
        )
    
    def clear_cache(self) -> None:
        """Limpa cache de prompts."""
        self._cache.clear()


_instance: Optional[PromptManager] = None


def get_prompt_manager(prompts_dir: str = "prompts") -> PromptManager:
    """
    Factory function para obter instância de PromptManager.
    
    Args:
        prompts_dir: Diretório com prompts
    
    Returns:
        Instância de PromptManager
    """
    global _instance
    if _instance is None:
        _instance = PromptManager(prompts_dir)
    return _instance
