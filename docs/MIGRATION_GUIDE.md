# GUIA DE MIGRAÇÃO - API ANTIGA PARA NOVA ARQUITETURA

## Problema Encontrado

O código em `app.py` e `team/business_team.py` estava usando a API antiga (funções síncronas):

```python
# Antiga (não funciona mais)
from agents import analyst, commercial, financial, market, reviewer

analyst.analyze_business_problem(problem_description)
commercial.develop_commercial_strategy(problem_description, analyst_insights)
```

Mas os agentes foram refatorados para usar classes com execução assíncrona:

```python
# Nova (correta)
from agents import AnalystAgent, CommercialAgent, FinancialAgent, MarketAgent, ReviewerAgent
from orchestrator import BusinessOrchestrator
from core.types import ExecutionContext

orchestrator = BusinessOrchestrator(agents)
context = ExecutionContext(problem_description=problem_description)
result = await orchestrator.execute(context)
```

## Solução Implementada

### 1. Atualizar `team/business_team.py`

Convertido de API antiga para nova:

```python
# Antes
from agents import analyst, commercial, financial, market, reviewer

class BusinessTeam:
    def analyze_business_scenario(self, problem_description: str) -> dict:
        self.analyst_insights = analyst.analyze_business_problem(problem_description)
        # ... mais chamadas de função

# Depois
from orchestrator import BusinessOrchestrator
from agents import AnalystAgent, CommercialAgent, FinancialAgent, MarketAgent, ReviewerAgent
from core.types import ExecutionContext

class BusinessTeam:
    def analyze_business_scenario(self, problem_description: str, business_type: str = "B2B") -> dict:
        orchestrator = self._create_orchestrator()
        context = ExecutionContext(problem_description=problem_description, business_type=business_type)
        result_context = asyncio.run(orchestrator.execute(context))
        return {
            "analyst": result_context.get_agent_output("analyst"),
            "commercial": result_context.get_agent_output("commercial"),
            # ...
        }
```

**Benefícios**:
- ✅ Usa nova arquitetura com DAG e paralelismo
- ✅ Execução assíncrona (mais rápida)
- ✅ Logging estruturado automático
- ✅ Tratamento de falhas parciais
- ✅ Metadados de execução

### 2. Atualizar `app.py`

Adicionado:
- Configuração de logging
- Carregamento de variáveis de ambiente
- Passagem de `business_type` para o orquestrador

```python
from infrastructure.logging import configure_logging
from dotenv import load_dotenv

load_dotenv()
configure_logging(level=logging.INFO)

# Usar business_type
results = team.analyze_business_scenario(
    problem_description, 
    business_type=business_type
)
```

## Compatibilidade

### Streamlit (Síncrono)
O `BusinessTeam` usa `asyncio.run()` para converter a execução assíncrona para síncrona, permitindo uso em Streamlit:

```python
# Streamlit é síncrono
with st.spinner("Analisando..."):
    results = team.analyze_business_scenario(problem)  # Funciona!
```

### Logging
Logs estruturados em JSON são emitidos automaticamente durante a execução:

```json
{
  "timestamp": "2024-02-05T20:30:00.123Z",
  "level": "INFO",
  "event": "execution_started",
  "execution_id": "1707084600.123456"
}
```

## Arquivos Modificados

- ✅ `team/business_team.py`: Refatorado para nova arquitetura
- ✅ `app.py`: Adicionado logging e business_type

## Arquivos Não Modificados

- ✅ `core/agent.py`: Mantém BaseAgent
- ✅ `core/types.py`: Mantém ExecutionContext
- ✅ `orchestrator/orchestrator.py`: Mantém BusinessOrchestrator
- ✅ `agents/*.py`: Mantêm classes de agentes
- ✅ `prompts/*.md`: Mantêm instruções

## Como Usar

### Executar com Streamlit
```bash
streamlit run app.py
```

### Executar com Main
```bash
python main.py
```

### Executar com Exemplos
```bash
python example_execution.py
```

## Próximos Passos

Se houver outros arquivos usando a API antiga, eles precisam ser atualizados:

1. Procurar por imports da forma antiga:
   ```bash
   grep -r "from agents import analyst" .
   grep -r "analyst.analyze_business_problem" .
   ```

2. Atualizar para nova forma:
   ```python
   from agents import AnalystAgent
   from orchestrator import BusinessOrchestrator
   from core.types import ExecutionContext
   
   orchestrator = BusinessOrchestrator({"analyst": AnalystAgent()})
   context = ExecutionContext(problem_description="...")
   result = asyncio.run(orchestrator.execute(context))
   ```

## Conclusão

A migração está completa. O sistema agora usa:
- ✅ Nova arquitetura com DAG e paralelismo
- ✅ Logging estruturado em JSON
- ✅ Execução assíncrona eficiente
- ✅ Compatibilidade com Streamlit
