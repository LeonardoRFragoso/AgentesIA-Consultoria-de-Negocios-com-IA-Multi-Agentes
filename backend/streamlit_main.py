"""
Arquivo principal para execução do sistema de agentes.
Demonstra o fluxo completo de orquestração.
"""

import asyncio
import os
from dotenv import load_dotenv

from core.types import ExecutionContext
from orchestrator import BusinessOrchestrator
from agents import (
    AnalystAgent,
    CommercialAgent,
    FinancialAgent,
    MarketAgent,
    ReviewerAgent,
)

load_dotenv()


def create_orchestrator() -> BusinessOrchestrator:
    """Cria e configura o orquestrador com todos os agentes"""
    agents = {
        "analyst": AnalystAgent(),
        "commercial": CommercialAgent(),
        "financial": FinancialAgent(),
        "market": MarketAgent(),
        "reviewer": ReviewerAgent(),
    }
    
    return BusinessOrchestrator(agents)


async def run_analysis(problem_description: str, business_type: str = "B2B") -> None:
    """
    Executa análise completa de um problema de negócio.
    
    Args:
        problem_description: Descrição do problema/oportunidade
        business_type: Tipo de negócio (B2B, SaaS, Varejo, etc.)
    """
    # Cria orquestrador
    orchestrator = create_orchestrator()
    
    # Exibe plano de execução
    print("\n" + "="*70)
    print("PLANO DE EXECUÇÃO")
    print("="*70)
    print(orchestrator.get_execution_plan())
    
    # Cria contexto inicial
    context = ExecutionContext(
        problem_description=problem_description,
        business_type=business_type,
        analysis_depth="Padrão"
    )
    
    print("\n" + "="*70)
    print("INICIANDO ANÁLISE")
    print("="*70)
    print(f"Problema: {problem_description[:100]}...")
    print(f"Tipo de Negócio: {business_type}")
    print()
    
    # Executa análise
    try:
        result_context = await orchestrator.execute(context)
        
        # Exibe resultados
        print("\n" + "="*70)
        print("RESULTADOS")
        print("="*70)
        
        # Diagnóstico executivo
        if "reviewer" in result_context.results:
            print("\n📋 DIAGNÓSTICO EXECUTIVO:")
            print("-" * 70)
            print(result_context.results["reviewer"])
        
        # Metadados de execução
        print("\n" + "="*70)
        print("METADADOS DE EXECUÇÃO")
        print("="*70)
        
        for agent_name, metadata in result_context.metadata.items():
            status_icon = "✓" if metadata.status.value == "completed" else "✗"
            print(f"{status_icon} {agent_name.upper()}")
            print(f"   Status: {metadata.status.value}")
            print(f"   Latência: {metadata.duration_seconds:.2f}s")
            if metadata.error:
                print(f"   Erro: {metadata.error}")
        
        print(f"\n📊 RESUMO:")
        print(f"   Latência Total: {result_context.get_total_latency_ms():.0f}ms")
        print(f"   Tokens Totais: {result_context.get_total_tokens()}")
        print(f"   Custo Total: ${result_context.get_total_cost():.4f}")
        
    except Exception as e:
        print(f"\n❌ Erro durante execução: {e}")
        raise


def main():
    """Entry point principal"""
    # Exemplo de problema de negócio
    problem = """
    Nossas vendas caíram 20% nos últimos 3 meses. 
    Qual pode ser a causa raiz e como devemos responder?
    """
    
    # Executa análise
    asyncio.run(run_analysis(problem, business_type="SaaS"))


if __name__ == "__main__":
    main()
