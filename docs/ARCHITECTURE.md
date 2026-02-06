# ARQUITETURA TÉCNICA - AGENTE MULTI-AGENTES DE NEGÓCIO

## Visão Geral

Este documento descreve a arquitetura técnica do sistema de agentes multi-agentes para análise estratégica de negócios. A arquitetura foi projetada para ser escalável, extensível e preparada para evolução futura.

---

## 1. CAMADAS DO SISTEMA

### 1.1 Camada de Apresentação (UI)
**Responsabilidade**: Capturar input do usuário e exibir resultados
- Streamlit (`ui/app.py`)
- Formatação de output (`ui/formatters.py`)
- **NÃO faz**: Lógica de negócio, orquestração

### 1.2 Camada de Orquestração
**Responsabilidade**: Coordenar execução de agentes respeitando dependências
- `orchestrator/orchestrator.py`: Classe principal `BusinessOrchestrator`
- `orchestrator/dag.py`: Resolução de dependências e paralelismo
- **Funcionalidades**:
  - Resolve DAG (Directed Acyclic Graph) de dependências
  - Executa agentes em paralelo quando possível
  - Trata falhas parciais
  - Coleta metadados de execução

### 1.3 Camada de Agentes
**Responsabilidade**: Executar análises específicas usando LLM
- `agents/analyst.py`: Analista de Negócio
- `agents/commercial.py`: Estrategista Comercial
- `agents/financial.py`: Analista Financeiro
- `agents/market.py`: Especialista de Mercado
- `agents/reviewer.py`: Revisor Executivo
- **Herdam de**: `core/agent.py` (BaseAgent)
- **Funcionalidades**:
  - Carregam prompts de arquivos
  - Recebem contexto compartilhado
  - Executam chamadas ao LLM
  - Retornam resultados estruturados

### 1.4 Camada de Contexto
**Responsabilidade**: Armazenar e gerenciar estado compartilhado
- `core/types.py`: `ExecutionContext`, `AgentMetadata`, `ExecutionStatus`
- **Dados armazenados**:
  - Descrição do problema
  - Outputs de cada agente
  - Metadados de execução (latência, tokens, custo)
  - Status de execução

### 1.5 Camada de LLM Provider
**Responsabilidade**: Comunicar com API de LLM
- Integração com Anthropic Claude
- Tratamento de erros e timeouts
- Contagem de tokens
- **Futuro**: Abstração para suportar múltiplos providers

---

## 2. FLUXO DE EXECUÇÃO

```
1. Usuário submete problema via Streamlit
   ↓
2. Streamlit cria ExecutionContext com problema
   ↓
3. Streamlit chama orchestrator.execute(context)
   ↓
4. Orchestrator resolve DAG:
   - Identifica agentes sem dependências
   - Executa em paralelo com asyncio
   - Aguarda conclusão
   - Executa próxima camada
   ↓
5. Cada agente (paralelo):
   - Lê contexto atual
   - Carrega prompt de arquivo
   - Constrói mensagem com contexto de predecessores
   - Chama LLM (Anthropic)
   - Escreve resultado no contexto
   ↓
6. Orchestrator coleta todos os resultados
   ↓
7. Retorna ExecutionContext completo
   ↓
8. Streamlit formata e exibe resultados
```

---

## 3. RESOLUÇÃO DE DEPENDÊNCIAS (DAG)

### 3.1 Estrutura de Dependências Atual

```
analyst (sem dependências)
  ├── commercial (depende de analyst)
  ├── market (depende de analyst)
  └── financial (depende de analyst, commercial)
       └── reviewer (depende de todos)
```

### 3.2 Camadas de Execução

```
Camada 1 (paralelo): [analyst]
Camada 2 (paralelo): [commercial, market]
Camada 3 (paralelo): [financial]
Camada 4 (sequencial): [reviewer]
```

### 3.3 Algoritmo de Resolução

A classe `DAGResolver` implementa:
1. **Validação**: Verifica se todas as dependências existem
2. **Detecção de Ciclos**: DFS para encontrar dependências circulares
3. **Topological Sort**: Organiza agentes em camadas para execução paralela

---

## 4. CLASSE BASE DE AGENTE (BaseAgent)

### 4.1 Responsabilidades

```python
class BaseAgent(ABC):
    async def execute(context: ExecutionContext) -> ExecutionContext
    def _load_prompt() -> str
    def _build_user_message(context) -> str
    def _build_context_message(context) -> str
    async def _execute_internal(context) -> str
```

### 4.2 Ciclo de Vida

1. **Inicialização**: Define nome, prompt, modelo, dependências
2. **Carregamento de Prompt**: Lê arquivo .md (com cache)
3. **Construção de Mensagem**: Monta contexto com outputs anteriores
4. **Execução**: Chama LLM com timeout
5. **Coleta de Metadados**: Registra latência, tokens, custo
6. **Tratamento de Erros**: Captura exceções e marca como failed

### 4.3 Extensibilidade

Subclasses podem sobrescrever:
- `_build_user_message()`: Customizar como a mensagem é construída
- `_build_context_message()`: Customizar como contexto é passado
- `_execute_internal()`: Implementar lógica completamente customizada

---

## 5. CONTEXTO COMPARTILHADO (ExecutionContext)

### 5.1 Estrutura

```python
@dataclass
class ExecutionContext:
    problem_description: str
    business_type: str
    analysis_depth: str
    results: Dict[str, str]  # {agent_name: output}
    metadata: Dict[str, AgentMetadata]  # Latência, tokens, custo
    created_at: datetime
    started_at: datetime
    completed_at: datetime
    execution_id: str
```

### 5.2 Métodos Utilitários

- `get_agent_output(agent_name)`: Recupera output de um agente
- `set_agent_output(agent_name, output, metadata)`: Define output
- `get_agent_status(agent_name)`: Recupera status
- `get_total_cost()`: Calcula custo total
- `get_total_tokens()`: Calcula tokens totais
- `get_total_latency_ms()`: Calcula latência total

---

## 6. ORQUESTRADOR (BusinessOrchestrator)

### 6.1 Responsabilidades

```python
class BusinessOrchestrator:
    async def execute(context) -> ExecutionContext
    async def _execute_layer(context, agent_names, layer_idx) -> None
    def _handle_agent_failure(context, agent_name, error) -> None
    def get_execution_plan() -> str
```

### 6.2 Características

- **Execução Assíncrona**: Usa `asyncio.gather()` para paralelismo
- **Tratamento de Erros**: Falha de um agente não quebra outros
- **Coleta de Resultados**: Agrega outputs em contexto compartilhado
- **Metadados**: Registra latência, tokens, custo por agente

### 6.3 Fluxo de Execução

```python
async def execute(context):
    context.started_at = now()
    
    for layer in execution_layers:
        # Cria tasks para todos os agentes da camada
        tasks = {agent: create_task(agent.execute(context))}
        
        # Aguarda com tratamento de erros
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Processa resultados (agentes já atualizaram contexto)
        for agent, result in zip(tasks, results):
            if isinstance(result, Exception):
                handle_failure(agent, result)
    
    context.completed_at = now()
    return context
```

---

## 7. TRATAMENTO DE ERROS

### 7.1 Hierarquia de Exceções

```
BusinessTeamException (base)
├── AgentExecutionError (falha ao executar agente)
├── DAGError (erro em dependências)
│   ├── CircularDependencyError
│   └── MissingDependencyError
├── PromptLoadError (falha ao carregar prompt)
├── LLMProviderError (erro da API)
├── TimeoutError (timeout de execução)
└── ValidationError (validação falhou)
```

### 7.2 Estratégia de Falhas Parciais

- **Agente falha**: Status marcado como FAILED, erro registrado
- **Agentes dependentes**: Recebem erro como input (podem decidir continuar)
- **Revisor**: Pode consolidar análise mesmo com falhas parciais
- **Retorno**: Contexto completo com status de cada agente

---

## 8. DECISÕES TÉCNICAS

### 8.1 Decisões Tomadas

| Decisão | Justificativa | Trade-off |
|---------|---------------|-----------|
| **Python asyncio** | Paralelismo real sem threads | Requer código async em toda cadeia |
| **BaseAgent abstrata** | Reutilização de código | Subclasses devem seguir padrão |
| **Contexto imutável durante execução** | Thread-safety | Impossível modificar contexto em paralelo |
| **DAG em memória** | Simplicidade, performance | Sem persistência de plano |
| **Prompts em arquivos .md** | Fácil edição, versionamento | Recarregamento em cada execução (mitigado com cache) |
| **Modelo fixo por agente** | Simplicidade | Sem flexibilidade de modelo |
| **Sem banco de dados neste passo** | Foco em arquitetura | Sem persistência de histórico |
| **Sem logging estruturado neste passo** | Foco em arquitetura | Sem observabilidade (preparado para adicionar) |

### 8.2 Trade-offs Aceitos

1. **Latência vs Paralelismo**: Execução sequencial de camadas é necessária para respeitar dependências
2. **Simplicidade vs Flexibilidade**: Modelo fixo por agente é simples, mas pode ser customizado no futuro
3. **Memória vs Persistência**: Contexto em memória é rápido, mas não persiste entre sessões

### 8.3 O Que Ficou Fora Propositalmente

- ❌ Banco de dados (será adicionado em Fase 2)
- ❌ Logging estruturado (será adicionado em Fase 2)
- ❌ Autenticação (será adicionado em Fase 3)
- ❌ Cache de resultados (será adicionado em Fase 2)
- ❌ Mecanismo de conflito entre agentes (será adicionado em Fase 3)
- ❌ Simulação de reuniões (será adicionado em Fase 3)
- ❌ Integração com dados reais (será adicionado em Fase 3)

---

## 9. PRÓXIMOS PASSOS (ROADMAP)

### Fase 2: Observabilidade e Persistência
- [ ] Logging estruturado (JSON)
- [ ] Dashboard de métricas
- [ ] Banco de dados (PostgreSQL)
- [ ] Cache de resultados (Redis)
- [ ] Histórico de análises

### Fase 3: Inteligência Avançada
- [ ] Mecanismo de conflito entre agentes
- [ ] Simulação de reuniões
- [ ] Integração com dados reais
- [ ] Fine-tuning de prompts baseado em feedback

### Fase 4: Produto SaaS
- [ ] Autenticação e multi-tenant
- [ ] API REST
- [ ] Dashboard de usuário
- [ ] Planos de pagamento
- [ ] Deploy em produção

---

## 10. COMO ESTENDER

### 10.1 Adicionar Novo Agente

```python
# 1. Criar classe em agents/novo_agente.py
class NovoAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="novo",
            prompt_path="prompts/novo.md",
            dependencies=["analyst"]  # Define dependências
        )

# 2. Adicionar prompt em prompts/novo.md

# 3. Registrar em main.py
agents = {
    ...
    "novo": NovoAgent(),
}
```

### 10.2 Customizar Comportamento de Agente

```python
class CustomAgent(BaseAgent):
    def _build_user_message(self, context):
        # Customizar como mensagem é construída
        return f"Custom: {context.problem_description}"
    
    def _build_context_message(self, context):
        # Customizar como contexto é passado
        return f"Contexto: {context.get_agent_output('analyst')}"
```

### 10.3 Adicionar Logging

```python
# Em orchestrator.py, adicionar:
import logging

logger = logging.getLogger(__name__)

async def _execute_layer(self, context, agent_names, layer_idx):
    logger.info(f"Executando camada {layer_idx}: {agent_names}")
    # ... resto do código
```

---

## 11. ESTRUTURA DE PASTAS FINAL

```
agente-multi-agentes/
├── core/
│   ├── __init__.py
│   ├── agent.py              # BaseAgent
│   ├── context.py            # ExecutionContext
│   ├── types.py              # Tipos e dataclasses
│   └── exceptions.py         # Exceções customizadas
│
├── orchestrator/
│   ├── __init__.py
│   ├── orchestrator.py       # BusinessOrchestrator
│   └── dag.py                # DAGResolver
│
├── agents/
│   ├── __init__.py
│   ├── analyst.py
│   ├── commercial.py
│   ├── financial.py
│   ├── market.py
│   └── reviewer.py
│
├── prompts/
│   ├── analyst.md
│   ├── commercial.md
│   ├── financial.md
│   ├── market.md
│   └── reviewer.md
│
├── ui/
│   ├── __init__.py
│   ├── app.py                # Streamlit app
│   └── formatters.py         # Formatação
│
├── main.py                   # Entry point
├── example_execution.py      # Exemplos
├── ARCHITECTURE.md           # Este arquivo
├── requirements.txt
├── .env.example
└── README.md
```

---

## 12. COMO EXECUTAR

### Execução Direta (sem UI)

```bash
python main.py
```

### Execução com Exemplos

```bash
python example_execution.py
```

### Execução com Streamlit

```bash
streamlit run ui/app.py
```

---

## 13. MÉTRICAS E OBSERVABILIDADE

### Métricas Coletadas

- **Latência**: Tempo total de execução por agente
- **Tokens**: Input + output tokens por agente
- **Custo**: Custo em USD por agente (baseado em modelo)
- **Status**: PENDING, RUNNING, COMPLETED, FAILED, SKIPPED
- **Erros**: Mensagem de erro se falhar

### Como Acessar

```python
result_context = await orchestrator.execute(context)

# Metadados por agente
for agent_name, metadata in result_context.metadata.items():
    print(f"{agent_name}: {metadata.duration_seconds}s, {metadata.total_tokens} tokens")

# Totais
print(f"Latência total: {result_context.get_total_latency_ms()}ms")
print(f"Custo total: ${result_context.get_total_cost()}")
```

---

## Conclusão

Esta arquitetura fornece uma base sólida para:
- ✅ Execução paralela eficiente
- ✅ Fácil adição de novos agentes
- ✅ Tratamento robusto de erros
- ✅ Observabilidade futura
- ✅ Evolução para SaaS

O código está pronto para os próximos passos: logging, banco de dados, mecanismos avançados de inteligência.
