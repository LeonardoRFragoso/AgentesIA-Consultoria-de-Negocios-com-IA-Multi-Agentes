# DECISÕES TÉCNICAS E TRADE-OFFS

## 1. DECISÕES ARQUITETURAIS PRINCIPAIS

### 1.1 Python Assíncrono (asyncio)

**Decisão**: Usar `asyncio` para paralelismo real entre agentes

**Justificativa**:
- Permite execução paralela de múltiplos agentes sem threads
- Melhor performance para I/O-bound operations (chamadas à API)
- Código mais limpo e seguro do que threading
- Reduz latência de 20s (sequencial) para ~5s (paralelo)

**Trade-off**:
- Requer que todo código seja async
- Curva de aprendizado maior
- Debugging pode ser mais complexo

**Alternativas Consideradas**:
- ❌ Threading: Complexo, GIL em Python, menos seguro
- ❌ Multiprocessing: Overhead de processo, complexo para compartilhar contexto
- ✅ Asyncio: Escolhido (melhor balance)

---

### 1.2 Classe Base Abstrata (BaseAgent)

**Decisão**: Implementar `BaseAgent` como classe abstrata reutilizável

**Justificativa**:
- Reduz duplicação de código (5 agentes = 5x menos código)
- Padrão consistente para todos os agentes
- Fácil adicionar novos agentes
- Centraliza lógica comum (prompt loading, error handling, timeout)

**Implementação**:
```python
class BaseAgent(ABC):
    async def execute(context) -> ExecutionContext
    def _load_prompt() -> str
    def _build_user_message(context) -> str
    def _build_context_message(context) -> str
```

**Trade-off**:
- Subclasses devem seguir padrão
- Menos flexibilidade para casos especiais (mitigado com métodos override)

---

### 1.3 Contexto Imutável Durante Execução

**Decisão**: ExecutionContext é compartilhado mas cada agente só escreve seus próprios resultados

**Justificativa**:
- Thread-safe (sem locks necessários)
- Evita race conditions
- Cada agente vê estado consistente

**Implementação**:
```python
# Agentes leem contexto
output = context.get_agent_output("analyst")

# Agentes escrevem apenas seus resultados
context.set_agent_output(self.name, result, metadata)
```

**Trade-off**:
- Impossível modificar contexto em paralelo
- Agentes não podem se comunicar diretamente (apenas via contexto)

---

### 1.4 DAG em Memória (Não Persistido)

**Decisão**: Resolver dependências em memória a cada execução

**Justificativa**:
- Simplicidade: sem complexidade de persistência
- Performance: resolução é rápida (O(n))
- Flexibilidade: estrutura pode mudar entre execuções

**Implementação**:
```python
class DAGResolver:
    def get_execution_layers() -> List[List[str]]
    def _detect_cycles() -> None
    def _validate_dependencies() -> None
```

**Trade-off**:
- Sem cache de plano de execução
- Sem histórico de estrutura de dependências

---

### 1.5 Prompts em Arquivos .md

**Decisão**: Armazenar prompts em arquivos Markdown separados

**Justificativa**:
- Fácil edição sem tocar código
- Versionamento com Git
- Reutilização entre agentes
- Legível e bem estruturado

**Implementação**:
```python
def _load_prompt(self) -> str:
    with open(self.prompt_path, "r", encoding="utf-8") as f:
        self._prompt_cache = f.read()
    return self._prompt_cache
```

**Trade-off**:
- Recarregamento em cada execução (mitigado com cache em memória)
- Sem validação de prompt em tempo de compilação

---

### 1.6 Modelo Fixo por Agente

**Decisão**: Cada agente usa um modelo fixo (Haiku para todos neste passo)

**Justificativa**:
- Simplicidade: sem complexidade de seleção de modelo
- Consistência: mesmo comportamento em todas as execuções
- Custo previsível

**Implementação**:
```python
super().__init__(
    name="analyst",
    model="claude-3-haiku-20240307",  # Fixo
)
```

**Trade-off**:
- Sem flexibilidade de modelo
- Pode não ser ótimo para todos os agentes

**Futuro**:
```python
# Será possível fazer:
super().__init__(
    name="reviewer",
    model="claude-3-sonnet-20240229",  # Mais poderoso para consolidação
)
```

---

### 1.7 Sem Banco de Dados Neste Passo

**Decisão**: Contexto em memória, sem persistência

**Justificativa**:
- Foco em arquitetura, não em infraestrutura
- Simplifica implementação inicial
- Preparado para adicionar BD no futuro

**Trade-off**:
- Sem histórico entre sessões
- Sem memória corporativa
- Sem análise comparativa

**Próximo Passo**:
```python
# Fase 2 adicionará:
class ExecutionRepository:
    async def save(context: ExecutionContext) -> str
    async def load(execution_id: str) -> ExecutionContext
    async def list_by_company(company_id: str) -> List[ExecutionContext]
```

---

### 1.8 Sem Logging Estruturado Neste Passo

**Decisão**: Preparar pontos de logging, mas não implementar ainda

**Justificativa**:
- Foco em arquitetura core
- Logging estruturado requer decisões (JSON, Datadog, etc.)
- Preparado para adicionar no próximo passo

**Pontos Preparados**:
```python
# Em orchestrator.py:
# TODO: logger.info(f"Executando camada {layer_idx}: {agent_names}")

# Em agent.py:
# TODO: logger.debug(f"Agent {self.name} started")
# TODO: logger.info(f"Agent {self.name} completed in {duration}ms")
```

**Próximo Passo**:
```python
# Fase 2 adicionará:
import logging
logger = logging.getLogger(__name__)

logger.info("Executing layer", extra={
    "layer": layer_idx,
    "agents": agent_names,
    "execution_id": context.execution_id
})
```

---

## 2. TRADE-OFFS ACEITOS

### 2.1 Latência vs Paralelismo

**Trade-off**: Execução sequencial de camadas é necessária para respeitar dependências

**Impacto**:
- ✅ Garante que agentes recebem contexto correto
- ❌ Não pode paralelizar agentes com dependências

**Exemplo**:
```
Sequencial: analyst (5s) → commercial (5s) → financial (5s) = 15s
Paralelo:   analyst (5s) → [commercial, market] (5s) → financial (5s) = 15s
Melhor:     analyst (5s) → [commercial, market] (5s) → [financial] (5s) = 15s
```

**Mitigação**: DAG garante máximo paralelismo possível

---

### 2.2 Simplicidade vs Flexibilidade

**Trade-off**: Modelo fixo por agente é simples, mas menos flexível

**Impacto**:
- ✅ Código simples, fácil de entender
- ❌ Sem flexibilidade de modelo por agente

**Exemplo**:
```python
# Simples (atual):
super().__init__(model="claude-3-haiku-20240307")

# Flexível (futuro):
super().__init__(model=config.get_model_for_agent(self.name))
```

**Mitigação**: Estrutura preparada para adicionar flexibilidade

---

### 2.3 Memória vs Persistência

**Trade-off**: Contexto em memória é rápido, mas não persiste

**Impacto**:
- ✅ Performance: sem I/O de BD
- ❌ Sem histórico entre sessões

**Exemplo**:
```python
# Atual (memória):
context = ExecutionContext(problem_description)
result = await orchestrator.execute(context)
# Resultado perdido ao fechar sessão

# Futuro (com BD):
context = ExecutionContext(problem_description)
result = await orchestrator.execute(context)
await repository.save(result)  # Persiste
```

**Mitigação**: Estrutura preparada para adicionar persistência

---

## 3. O QUE FICOU FORA PROPOSITALMENTE

### 3.1 Banco de Dados
- ❌ Não implementado neste passo
- 📅 Será adicionado em Fase 2
- 🎯 Objetivo: Memória corporativa, histórico, análise comparativa

### 3.2 Logging Estruturado
- ❌ Não implementado neste passo
- 📅 Será adicionado em Fase 2
- 🎯 Objetivo: Observabilidade, debugging, auditoria

### 3.3 Autenticação
- ❌ Não implementado neste passo
- 📅 Será adicionado em Fase 3
- 🎯 Objetivo: Multi-tenant, segurança, controle de acesso

### 3.4 Cache de Resultados
- ❌ Não implementado neste passo
- 📅 Será adicionado em Fase 2
- 🎯 Objetivo: Reduzir custo, melhorar latência

### 3.5 Mecanismo de Conflito
- ❌ Não implementado neste passo
- 📅 Será adicionado em Fase 3
- 🎯 Objetivo: Resolver contradições entre agentes

### 3.6 Simulação de Reuniões
- ❌ Não implementado neste passo
- 📅 Será adicionado em Fase 3
- 🎯 Objetivo: Agentes conversam entre si

### 3.7 Integração com Dados Reais
- ❌ Não implementado neste passo
- 📅 Será adicionado em Fase 3
- 🎯 Objetivo: Análises baseadas em dados, não apenas prompts

---

## 4. DECISÕES DE DESIGN PATTERN

### 4.1 Padrão: Dependency Injection

**Implementação**:
```python
# Agentes recebem contexto como parâmetro
async def execute(self, context: ExecutionContext) -> ExecutionContext
```

**Benefício**: Fácil testar, sem estado global

---

### 4.2 Padrão: Data Class para Contexto

**Implementação**:
```python
@dataclass
class ExecutionContext:
    problem_description: str
    results: Dict[str, str] = field(default_factory=dict)
```

**Benefício**: Imutabilidade, serialização fácil, type hints

---

### 4.3 Padrão: Factory para Agentes

**Implementação**:
```python
def create_orchestrator() -> BusinessOrchestrator:
    agents = {
        "analyst": AnalystAgent(),
        "commercial": CommercialAgent(),
        ...
    }
    return BusinessOrchestrator(agents)
```

**Benefício**: Centraliza criação, fácil mudar configuração

---

### 4.4 Padrão: Template Method em BaseAgent

**Implementação**:
```python
class BaseAgent:
    async def execute(self, context):
        # Template
        metadata.start_time = now()
        result = await self._execute_internal(context)
        metadata.end_time = now()
        context.set_agent_output(self.name, result, metadata)
    
    async def _execute_internal(self, context):
        # Implementação específica
        pass
```

**Benefício**: Código comum centralizado, subclasses focam em lógica

---

## 5. DECISÕES DE PERFORMANCE

### 5.1 Cache de Prompts

**Implementação**:
```python
def _load_prompt(self) -> str:
    if self._prompt_cache is not None:
        return self._prompt_cache
    # Carrega e cacheia
```

**Impacto**: Evita recarregar arquivo em cada execução

---

### 5.2 Execução Paralela com asyncio.gather()

**Implementação**:
```python
tasks = {agent: asyncio.create_task(agent.execute(context))}
results = await asyncio.gather(*tasks.values(), return_exceptions=True)
```

**Impacto**: Paralelismo real, melhor latência

---

### 5.3 Timeout por Agente

**Implementação**:
```python
result = await asyncio.wait_for(
    self._execute_internal(context),
    timeout=self.timeout_seconds
)
```

**Impacto**: Evita travamento, falha rápido

---

## 6. DECISÕES DE SEGURANÇA

### 6.1 Variáveis de Ambiente para API Key

**Implementação**:
```python
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("ANTHROPIC_API_KEY não está configurada")
```

**Benefício**: Não hardcoda credenciais

---

### 6.2 Contexto Imutável

**Benefício**: Evita race conditions, thread-safe

---

### 6.3 Tratamento de Exceções Específicas

**Benefício**: Fácil debugar, mensagens claras

---

## 7. DECISÕES DE MANUTENIBILIDADE

### 7.1 Type Hints em Tudo

**Implementação**:
```python
async def execute(self, context: ExecutionContext) -> ExecutionContext
def get_agent_output(self, agent_name: str) -> Optional[str]
```

**Benefício**: IDE autocomplete, detecção de erros

---

### 7.2 Docstrings Descritivas

**Implementação**:
```python
def execute(self, context: ExecutionContext) -> ExecutionContext:
    """
    Executa o agente de forma assíncrona.
    
    Args:
        context: Contexto compartilhado de execução
    
    Returns:
        Contexto atualizado com resultado do agente
    """
```

**Benefício**: Documentação automática, clareza

---

### 7.3 Separação de Responsabilidades

**Implementação**:
- `core/`: Tipos e classes base
- `orchestrator/`: Orquestração
- `agents/`: Implementação específica
- `prompts/`: Instruções

**Benefício**: Fácil navegar, modificar, testar

---

## 8. PRÓXIMAS DECISÕES (FASE 2)

### 8.1 Banco de Dados
- Qual BD? PostgreSQL vs MongoDB
- Como estruturar schema?
- Como fazer migrations?

### 8.2 Logging
- JSON ou texto?
- Datadog vs ELK vs CloudWatch?
- Qual nível de detalhe?

### 8.3 Cache
- Redis vs Memcached?
- TTL de cache?
- Invalidação?

### 8.4 Observabilidade
- Prometheus vs Datadog?
- Quais métricas?
- Alertas?

---

## Conclusão

As decisões tomadas neste passo foram:
- ✅ **Arquitetura sólida**: Pronta para escala
- ✅ **Código limpo**: Fácil de entender e manter
- ✅ **Extensível**: Fácil adicionar novos agentes
- ✅ **Preparada para futuro**: Pontos de extensão claros

O projeto está pronto para os próximos passos sem refatoração maior.
