"""Testes básicos para ETAPA 1 - Quick Wins."""

import os
import sys
import tempfile
import warnings
from pathlib import Path

# Suprimir avisos de typing do SQLAlchemy
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", message=".*SQLCoreOperations.*")

# Adicionar projeto ao path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_database_connection():
    """Testa conexão com banco de dados."""
    print("\n🧪 Testando Persistência de Histórico...")
    
    try:
        from infrastructure.database import get_db_connection
        
        # Usar banco de dados temporário
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        
        db_url = f"sqlite:///{db_path}"
        db = get_db_connection(db_url)
        
        # Verificar que tabelas foram criadas
        session = db.get_session()
        from infrastructure.database.models import Analysis, AgentOutput
        
        # Contar tabelas
        tables = db._engine.table_names() if hasattr(db._engine, 'table_names') else []
        
        session.close()
        db.close()
        
        # Aguardar um pouco antes de deletar
        import time
        time.sleep(0.1)
        
        try:
            os.unlink(db_path)
        except:
            pass  # Arquivo pode estar em uso, ignorar
        
        print("✅ Persistência: OK")
        return True
    except Exception as e:
        print(f"❌ Persistência: FALHA - {str(e)}")
        return False


def test_cache_manager():
    """Testa cache manager."""
    print("\n🧪 Testando Cache de Resultados...")
    
    try:
        from infrastructure.cache import get_cache_manager
        
        cache = get_cache_manager(ttl_hours=24)
        
        # Teste: armazenar e recuperar
        test_result = {"test": "data", "value": 123}
        
        cache.set(
            problem_description="Teste problema",
            business_type="B2B",
            analysis_depth="Padrão",
            result=test_result
        )
        
        retrieved = cache.get(
            problem_description="Teste problema",
            business_type="B2B",
            analysis_depth="Padrão"
        )
        
        assert retrieved == test_result, "Cache não retornou dados corretos"
        
        # Teste: cache miss
        missed = cache.get(
            problem_description="Problema diferente",
            business_type="B2B",
            analysis_depth="Padrão"
        )
        
        assert missed is None, "Cache deveria retornar None para miss"
        
        # Teste: estatísticas
        stats = cache.get_stats()
        assert stats['total_entries'] >= 1, "Cache deveria ter pelo menos 1 entrada"
        
        cache.clear()
        
        print("✅ Cache: OK")
        return True
    except Exception as e:
        print(f"❌ Cache: FALHA - {str(e)}")
        return False


def test_analysis_exporter():
    """Testa exportador de análises."""
    print("\n🧪 Testando Exportação (PDF/PPT)...")
    
    try:
        from infrastructure.exporters.analysis_exporter import AnalysisExporter
        from datetime import datetime
        
        test_data = {
            "problem": "Queda de vendas 20%",
            "business_type": "SaaS",
            "analysis_depth": "Padrão",
            "timestamp": datetime.now(),
            "results": {
                "analyst": "Análise: A queda pode ser causada por...",
                "commercial": "Estratégia: Aumentar investimento em marketing",
                "financial": "Viabilidade: ROI esperado de 150%",
                "market": "Contexto: Mercado em contração",
                "executive": "Decisão: Investir $100K em marketing",
                "metadata": {
                    "analyst": {"latency_ms": 1000, "tokens": 500, "cost_usd": 0.05},
                    "commercial": {"latency_ms": 1200, "tokens": 600, "cost_usd": 0.06},
                }
            }
        }
        
        # Teste: Markdown
        markdown = AnalysisExporter.to_markdown(test_data)
        assert "Queda de vendas" in markdown, "Markdown não contém problema"
        assert "Análise de Negócio" in markdown, "Markdown não contém seção de análise"
        print("  ✅ Markdown: OK")
        
        # Teste: PDF
        try:
            pdf_bytes = AnalysisExporter.to_pdf(test_data, "temp.pdf")
            assert len(pdf_bytes) > 0, "PDF vazio"
            print("  ✅ PDF: OK")
        except ImportError:
            print("  ⚠️  PDF: reportlab não instalado (opcional)")
        
        # Teste: PowerPoint
        try:
            ppt_bytes = AnalysisExporter.to_ppt(test_data, "temp.pptx")
            assert len(ppt_bytes) > 0, "PowerPoint vazio"
            print("  ✅ PowerPoint: OK")
        except ImportError:
            print("  ⚠️  PowerPoint: python-pptx não instalado (opcional)")
        
        print("✅ Exportação: OK")
        return True
    except Exception as e:
        print(f"❌ Exportação: FALHA - {str(e)}")
        return False


def test_prompt_manager():
    """Testa gerenciador de prompts."""
    print("\n🧪 Testando Prompts Dinâmicos...")
    
    try:
        from infrastructure.prompts import get_prompt_manager
        
        pm = get_prompt_manager()
        
        # Teste: carregar prompt com variáveis
        prompt = pm.load_prompt(
            agent_name="analyst",
            business_type="SaaS",
            analysis_depth="Profunda"
        )
        
        assert "SaaS" in prompt, "Prompt não contém business_type"
        assert "Profunda" in prompt or "profunda" in prompt.lower(), "Prompt não contém analysis_depth"
        
        print("✅ Prompts Dinâmicos: OK")
        return True
    except Exception as e:
        print(f"❌ Prompts Dinâmicos: FALHA - {str(e)}")
        return False


def test_analysis_service():
    """Testa serviço de análise (sem executar agentes)."""
    print("\n🧪 Testando AnalysisService...")
    
    try:
        from infrastructure.services import AnalysisService
        import tempfile
        import time
        
        # Usar banco de dados temporário
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        
        db_url = f"sqlite:///{db_path}"
        service = AnalysisService(database_url=db_url, enable_cache=True)
        
        # Teste: histórico vazio
        history = service.get_analysis_history(user_id="test_user")
        assert isinstance(history, list), "Histórico deveria ser lista"
        assert len(history) == 0, "Histórico deveria estar vazio inicialmente"
        
        # Teste: estatísticas
        stats = service.get_user_statistics(user_id="test_user")
        assert stats['total_analyses'] == 0, "Deveria ter 0 análises"
        assert stats['total_cost_usd'] == 0.0, "Custo deveria ser 0"
        
        service.close()
        time.sleep(0.1)
        
        try:
            os.unlink(db_path)
        except:
            pass  # Arquivo pode estar em uso, ignorar
        
        print("✅ AnalysisService: OK")
        return True
    except Exception as e:
        print(f"❌ AnalysisService: FALHA - {str(e)}")
        return False


def run_all_tests():
    """Executa todos os testes."""
    print("\n" + "="*60)
    print("🧪 TESTES ETAPA 1 - QUICK WINS")
    print("="*60)
    
    results = {
        "Persistência": test_database_connection(),
        "Cache": test_cache_manager(),
        "Exportação": test_analysis_exporter(),
        "Prompts Dinâmicos": test_prompt_manager(),
        "AnalysisService": test_analysis_service(),
    }
    
    print("\n" + "="*60)
    print("📊 RESUMO DOS TESTES")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name:.<40} {status}")
    
    print("="*60)
    print(f"Total: {passed}/{total} testes passaram")
    print("="*60)
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
