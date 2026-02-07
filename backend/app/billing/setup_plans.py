"""
Setup Script - Create Plans in Mercado Pago

Execute este script uma vez para criar os planos de assinatura no Mercado Pago.
Os IDs gerados devem ser salvos nas variáveis de ambiente.

Usage:
    python -m app.billing.setup_plans
"""
import asyncio
import os
from dotenv import load_dotenv

from .plans import PLANS, PlanTier, BillingCycle
from .mercado_pago_service import get_mercado_pago_service

load_dotenv()


async def setup_plans():
    """Cria os planos no Mercado Pago"""
    mp_service = get_mercado_pago_service()
    
    if not mp_service.access_token:
        print("❌ MERCADO_PAGO_ACCESS_TOKEN não configurado!")
        print("Configure a variável de ambiente e tente novamente.")
        return
    
    print("🚀 Criando planos no Mercado Pago...\n")
    
    created_plans = {}
    
    for tier in [PlanTier.PRO, PlanTier.ENTERPRISE]:
        plan = PLANS[tier]
        print(f"📦 Criando plano: {plan.name}")
        
        for cycle in [BillingCycle.MONTHLY, BillingCycle.YEARLY]:
            try:
                result = await mp_service.create_plan(
                    plan=plan,
                    cycle=cycle,
                    back_url=os.getenv("APP_URL", "http://localhost:3000"),
                )
                
                plan_id = result.get("id")
                key = f"MP_PLAN_{tier.value.upper()}_{cycle.value.upper()}"
                created_plans[key] = plan_id
                
                print(f"  ✅ {cycle.value}: {plan_id}")
                
            except Exception as e:
                print(f"  ❌ {cycle.value}: Erro - {e}")
    
    print("\n" + "=" * 50)
    print("📋 Adicione ao seu .env:")
    print("=" * 50 + "\n")
    
    for key, value in created_plans.items():
        print(f"{key}={value}")
    
    print("\n" + "=" * 50)
    print("✅ Setup concluído!")
    print("=" * 50)
    
    return created_plans


async def list_existing_plans():
    """Lista planos existentes no Mercado Pago"""
    mp_service = get_mercado_pago_service()
    
    print("📋 Buscando planos existentes...\n")
    
    # MP não tem endpoint para listar todos os planos
    # Verifica os IDs configurados
    plan_ids = [
        ("MP_PLAN_PRO_MONTHLY", os.getenv("MP_PLAN_PRO_MONTHLY")),
        ("MP_PLAN_PRO_YEARLY", os.getenv("MP_PLAN_PRO_YEARLY")),
        ("MP_PLAN_ENTERPRISE_MONTHLY", os.getenv("MP_PLAN_ENTERPRISE_MONTHLY")),
        ("MP_PLAN_ENTERPRISE_YEARLY", os.getenv("MP_PLAN_ENTERPRISE_YEARLY")),
    ]
    
    for name, plan_id in plan_ids:
        if plan_id:
            try:
                plan = await mp_service.get_plan(plan_id)
                status = plan.get("status", "unknown")
                reason = plan.get("reason", "N/A")
                print(f"✅ {name}: {plan_id}")
                print(f"   Status: {status} | Nome: {reason}")
            except Exception as e:
                print(f"❌ {name}: {plan_id} - Erro: {e}")
        else:
            print(f"⚠️  {name}: Não configurado")


async def main():
    """Menu principal"""
    print("\n" + "=" * 50)
    print("🔧 Mercado Pago - Plan Setup")
    print("=" * 50 + "\n")
    
    print("Opções:")
    print("1. Criar novos planos")
    print("2. Listar planos existentes")
    print("3. Sair")
    
    choice = input("\nEscolha uma opção: ").strip()
    
    if choice == "1":
        await setup_plans()
    elif choice == "2":
        await list_existing_plans()
    else:
        print("Saindo...")


if __name__ == "__main__":
    asyncio.run(main())
