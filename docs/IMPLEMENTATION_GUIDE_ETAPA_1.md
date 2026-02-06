# GUIA DE IMPLEMENTAÇÃO - ETAPA 1

**Objetivo**: Transformar MVP em SaaS escalável com persistência, cache e exportação.

---

## 🚀 INÍCIO RÁPIDO

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

Dependências adicionadas:
- `sqlalchemy==2.0.23`: ORM para persistência
- `redis==5.0.1`: Cache (opcional, usa memória local por padrão)
- `reportlab==4.0.7`: Geração de PDF
- `python-pptx==0.6.21`: Geração de PowerPoint
- `jinja2==3.1.2`: Templates para prompts dinâmicos

### 2. Executar Aplicação

```bash
streamlit run app.py
```

A aplicação criará automaticamente:
- Banco de dados SQLite em `data/analyses.db`
- Diretório de cache em memória

### 3. Testar Funcionalidades

```bash
# Teste de persistência
python -c "
from infrastructure.services import AnalysisService
service = AnalysisService()
history = service.get_analysis_history()
print(f'Análises no histórico: {len(history)}')
"
```

---

## 📁 ESTRUTURA DE ARQUIVOS CRIADOS

```
infrastructure/
├── database/
│   ├── __init__.py
│   ├── connection.py          # Gerenciamento de conexão
│   └── models.py              # Modelos SQLAlchemy
├── repositories/
│   ├── __init__.py
│   ├── base_repository.py     # Classe base
│   ├── analysis_repository.py # CRUD de análises
│   └── agent_output_repository.py # CRUD de outputs
├── cache/
│   ├── __init__.py
│   └── cache_manager.py       # Cache em memória
├── services/
│   ├── __init__.py
│   └── analysis_service.py    # Orquestração com persistência
├── exporters/
│   ├── __init__.py
│   ├── executive_exporter.py  # Exportador existente
│   └── analysis_exporter.py   # Novo exportador
└── prompts/
    ├── __init__.py
    └── prompt_manager.py      # Gerenciador de prompts

prompts/
└── analyst.md                 # Atualizado com templates Jinja2

data/
└── analyses.db               # Banco de dados SQLite (criado automaticamente)
```

---

## 🔧 CONFIGURAÇÃO

### Banco de Dados

**SQLite (Padrão - MVP)**
```python
from infrastructure.services import AnalysisService

service = AnalysisService()  # Usa SQLite local
```

**PostgreSQL (Produção)**
```python
from infrastructure.services import AnalysisService

service = AnalysisService(
    database_url="postgresql://user:password@localhost/analyses"
)
```

### Cache

**Habilitado (Padrão)**
```python
service = AnalysisService(enable_cache=True)
```

**Desabilitado**
```python
service = AnalysisService(enable_cache=False)
```

---

## 💾 PERSISTÊNCIA

### Salvar Análise

```python
from infrastructure.services import AnalysisService

service = AnalysisService()

results = service.analyze_business_scenario(
    problem_description="Queda de vendas 20%",
    business_type="SaaS",
    analysis_depth="Padrão",
    user_id="user_123",  # Para multi-tenant
    workspace_id="workspace_456"
)

# Resultado é salvo automaticamente no banco de dados
print(f"Execution ID: {results['execution_id']}")
```

### Recuperar Histórico

```python
# Últimas 10 análises do usuário
history = service.get_analysis_history(
    user_id="user_123",
    limit=10
)

for analysis in history:
    print(f"{analysis['problem_description'][:50]}... ({analysis['created_at']})")
```

### Recuperar Análise Completa

```python
analysis = service.get_analysis(execution_id="abc-123-def")

if analysis:
    print(f"Problema: {analysis['problem_description']}")
    print(f"Custo: ${analysis['total_cost_usd']:.4f}")
    print(f"Tokens: {analysis['total_tokens']}")
    
    # Acessar outputs de agentes
    for agent_name, output_data in analysis['agent_outputs'].items():
        print(f"{agent_name}: {output_data['output'][:100]}...")
```

### Estatísticas de Uso

```python
stats = service.get_user_statistics(user_id="user_123")

print(f"Total de análises: {stats['total_analyses']}")
print(f"Custo total: ${stats['total_cost_usd']:.2f}")
print(f"Tokens totais: {stats['total_tokens']:,}")
print(f"Latência média: {stats['avg_latency_ms']:.0f}ms")
```

---

## 🚀 CACHE

### Como Funciona

1. **Primeira execução**: Executa todos os agentes, armazena em cache
2. **Execuções subsequentes**: Retorna do cache se problema + business_type + analysis_depth forem idênticos
3. **TTL**: Cache expira após 24 horas (configurável)

### Exemplo

```python
from infrastructure.cache import get_cache_manager

cache = get_cache_manager(ttl_hours=24)

# Primeira execução
results1 = service.analyze_business_scenario(
    problem_description="Queda de vendas 20%",
    business_type="SaaS"
)
# Latência: 2.5 min, Custo: $0.15

# Segunda execução (cache hit)
results2 = service.analyze_business_scenario(
    problem_description="Queda de vendas 20%",
    business_type="SaaS"
)
# Latência: 50ms, Custo: $0.00

# Limpar cache
cache.clear()
```

---

## 📤 EXPORTAÇÃO

### Markdown (One-Pager)

```python
from infrastructure.exporters.analysis_exporter import AnalysisExporter

markdown = AnalysisExporter.to_markdown(analysis_data)

# Salvar em arquivo
with open("analise.md", "w", encoding="utf-8") as f:
    f.write(markdown)
```

### PDF

```python
pdf_bytes = AnalysisExporter.to_pdf(analysis_data, "output.pdf")

# Usar em Streamlit
st.download_button(
    label="Baixar PDF",
    data=pdf_bytes,
    file_name="analise.pdf",
    mime="application/pdf"
)
```

### PowerPoint

```python
ppt_bytes = AnalysisExporter.to_ppt(analysis_data, "output.pptx")

# Usar em Streamlit
st.download_button(
    label="Baixar PowerPoint",
    data=ppt_bytes,
    file_name="analise.pptx",
    mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
)
```

---

## 🎯 PROMPTS DINÂMICOS

### Usar Prompt Manager

```python
from infrastructure.prompts import get_prompt_manager

pm = get_prompt_manager()

# Carregar prompt com variáveis
prompt = pm.load_prompt(
    agent_name="analyst",
    business_type="SaaS",
    analysis_depth="Profunda",
    industry="FinTech"
)

print(prompt)
```

### Criar Novo Prompt com Template

Editar `prompts/novo_agente.md`:

```markdown
# Agente Novo

Você é um especialista em {{ business_type }}.

**Profundidade**: {{ depth_description }}

{% if analysis_depth == "Rápida" %}
Seja breve e conciso.
{% elif analysis_depth == "Profunda" %}
Forneça análise detalhada e abrangente.
{% endif %}
```

---

## 🧪 TESTES BÁSICOS

### Teste de Persistência

```python
from infrastructure.database import get_db_connection
from infrastructure.repositories import AnalysisRepository

db = get_db_connection()
session = db.get_session()
repo = AnalysisRepository(session)

# Verificar análises
analyses = repo.get_all()
print(f"Total de análises no banco: {len(analyses)}")

session.close()
```

### Teste de Cache

```python
from infrastructure.cache import get_cache_manager

cache = get_cache_manager()

# Adicionar ao cache
cache.set(
    problem_description="Teste",
    business_type="B2B",
    analysis_depth="Padrão",
    result={"test": "data"}
)

# Recuperar do cache
result = cache.get(
    problem_description="Teste",
    business_type="B2B",
    analysis_depth="Padrão"
)

assert result == {"test": "data"}
print("✅ Cache funcionando")
```

### Teste de Exportação

```python
from infrastructure.exporters.analysis_exporter import AnalysisExporter

test_data = {
    "problem": "Teste",
    "business_type": "SaaS",
    "results": {
        "analyst": "Análise teste",
        "executive": "Decisão teste"
    }
}

# Markdown
md = AnalysisExporter.to_markdown(test_data)
assert "Teste" in md
print("✅ Markdown OK")

# PDF
pdf = AnalysisExporter.to_pdf(test_data, "test.pdf")
assert len(pdf) > 0
print("✅ PDF OK")

# PowerPoint
ppt = AnalysisExporter.to_ppt(test_data, "test.pptx")
assert len(ppt) > 0
print("✅ PowerPoint OK")
```

---

## 🔍 DEBUGGING

### Logs Estruturados

A aplicação usa logging estruturado. Para ver logs:

```python
import logging
from infrastructure.logging import configure_logging

configure_logging(level=logging.DEBUG)
```

### Verificar Banco de Dados

```bash
# SQLite
sqlite3 data/analyses.db

# Ver tabelas
.tables

# Ver análises
SELECT execution_id, problem_description, created_at FROM analyses LIMIT 5;
```

### Verificar Cache

```python
from infrastructure.cache import get_cache_manager

cache = get_cache_manager()
stats = cache.get_stats()
print(f"Entradas em cache: {stats['total_entries']}")
print(f"TTL: {stats['ttl_hours']} horas")
```

---

## 🚨 TROUBLESHOOTING

### Erro: "Database not initialized"

```python
# Solução: Inicializar conexão
from infrastructure.database import get_db_connection
db = get_db_connection()
```

### Erro: "reportlab não está instalado"

```bash
pip install reportlab
```

### Erro: "python-pptx não está instalado"

```bash
pip install python-pptx
```

### Banco de dados corrompido

```bash
# Remover banco de dados
rm data/analyses.db

# Será recriado automaticamente na próxima execução
```

---

## 📊 MONITORAMENTO

### Métricas por Usuário

```python
service = AnalysisService()

stats = service.get_user_statistics(user_id="user_123")

print(f"""
Usuário: user_123
- Análises: {stats['total_analyses']}
- Custo: ${stats['total_cost_usd']:.2f}
- Tokens: {stats['total_tokens']:,}
- Latência média: {stats['avg_latency_ms']:.0f}ms
""")
```

### Métricas por Agente

```python
from infrastructure.repositories import AgentOutputRepository

session = db.get_session()
repo = AgentOutputRepository(session)

stats = repo.get_agent_statistics("analyst")

print(f"""
Agente: analyst
- Execuções: {stats['total_executions']}
- Sucesso: {stats['successful']}
- Falhas: {stats['failed']}
- Latência média: {stats['avg_latency_ms']:.0f}ms
- Tokens médios: {stats['avg_tokens']:.0f}
- Custo total: ${stats['total_cost_usd']:.4f}
""")

session.close()
```

---

## 🔐 SEGURANÇA

### Multi-tenant

Sempre especificar `user_id` e `workspace_id`:

```python
results = service.analyze_business_scenario(
    problem_description="...",
    user_id="user_123",        # Obrigatório
    workspace_id="workspace_456" # Obrigatório
)
```

### Isolamento de Dados

```python
# Usuário A não vê análises de Usuário B
history_a = service.get_analysis_history(user_id="user_a")
history_b = service.get_analysis_history(user_id="user_b")

assert len(history_a) != len(history_b)  # Isolamento garantido
```

---

## 🎯 PRÓXIMOS PASSOS

1. **Streaming**: Implementar respostas incrementais
2. **Integração com Dados**: Google Sheets, CSV
3. **Fila de Jobs**: Celery para múltiplos usuários
4. **Autenticação**: OAuth2, JWT

---

## 📞 SUPORTE

Para dúvidas ou problemas:
1. Verificar logs em `infrastructure/logging/`
2. Consultar documentação em `docs/`
3. Executar testes básicos acima

