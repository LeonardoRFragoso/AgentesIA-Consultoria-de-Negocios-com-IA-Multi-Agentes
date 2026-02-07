"""
Exemplo de execução do sistema de agentes.
Demonstra o fluxo completo com diferentes cenários.
"""

import asyncio
from core.types import ExecutionContext
from orchestrator import BusinessOrchestrator
from agents import (
    AnalystAgent,
    CommercialAgent,
    FinancialAgent,
    MarketAgent,
    ReviewerAgent,
)


async def example_1_sales_decline():
    """Exemplo 1: Queda de vendas"""
    print("\n" + "="*80)
    print("EXEMPLO 1: QUEDA DE VENDAS")
    print("="*80)
    
    agents = {
        "analyst": AnalystAgent(),
        "commercial": CommercialAgent(),
        "financial": FinancialAgent(),
        "market": MarketAgent(),
        "reviewer": ReviewerAgent(),
    }
    
    orchestrator = BusinessOrchestrator(agents)
    
    context = ExecutionContext(
        problem_description="Nossas vendas caíram 20% nos últimos 3 meses. Qual pode ser a causa e como devemos responder?",
        business_type="SaaS",
        analysis_depth="Padrão"
    )
    
    print("\n📊 Plano de Execução:")
    print(orchestrator.get_execution_plan())
    
    print("\n⏳ Executando análise...")
    result_context = await orchestrator.execute(context)
    
    print("\n✓ Análise concluída!")
    print(f"Latência total: {result_context.get_total_latency_ms():.0f}ms")
    print(f"Custo total: ${result_context.get_total_cost():.4f}")
    
    # Exibe resultado do revisor
    if "reviewer" in result_context.results:
        print("\n" + "-"*80)
        print("DIAGNÓSTICO EXECUTIVO:")
        print("-"*80)
        print(result_context.results["reviewer"][:500] + "...")


async def example_2_market_expansion():
    """Exemplo 2: Expansão de mercado"""
    print("\n" + "="*80)
    print("EXEMPLO 2: EXPANSÃO PARA NOVO MERCADO")
    print("="*80)
    
    agents = {
        "analyst": AnalystAgent(),
        "commercial": CommercialAgent(),
        "financial": FinancialAgent(),
        "market": MarketAgent(),
        "reviewer": ReviewerAgent(),
    }
    
    orchestrator = BusinessOrchestrator(agents)
    
    context = ExecutionContext(
        problem_description="Estamos considerando expandir para o mercado europeu. Quais são os principais riscos e oportunidades?",
        business_type="B2B",
        analysis_depth="Profunda"
    )
    
    print("\n📊 Plano de Execução:")
    print(orchestrator.get_execution_plan())
    
    print("\n⏳ Executando análise...")
    result_context = await orchestrator.execute(context)
    
    print("\n✓ Análise concluída!")
    print(f"Latência total: {result_context.get_total_latency_ms():.0f}ms")
    print(f"Custo total: ${result_context.get_total_cost():.4f}")


async def example_3_partial_execution():
    """Exemplo 3: Execução com falha parcial (demonstração)"""
    print("\n" + "="*80)
    print("EXEMPLO 3: DEMONSTRAÇÃO DE TRATAMENTO DE ERROS")
    print("="*80)
    
    agents = {
        "analyst": AnalystAgent(),
        "commercial": CommercialAgent(),
        "financial": FinancialAgent(),
        "market": MarketAgent(),
        "reviewer": ReviewerAgent(),
    }
    
    orchestrator = BusinessOrchestrator(agents)
    
    print("\n📊 Plano de Execução:")
    print(orchestrator.get_execution_plan())
    print("\nNota: Este exemplo mostra como o sistema trata falhas parciais.")
    print("Se um agente falha, outros continuam e o revisor recebe um erro como input.")


async def main():
    """Executa exemplos"""
    try:
        # Exemplo 1
        await example_1_sales_decline()
        
        # Exemplo 2
        await example_2_market_expansion()
        
        # Exemplo 3
        await example_3_partial_execution()
        
        print("\n" + "="*80)
        print("✓ TODOS OS EXEMPLOS COMPLETADOS COM SUCESSO")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
