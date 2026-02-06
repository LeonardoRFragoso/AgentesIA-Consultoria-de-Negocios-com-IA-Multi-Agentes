# DECISÕES TÉCNICAS - OBSERVABILIDADE

## 1️⃣ POR QUE JSON LOGGING

### Decisão
Usar JSON como formato estruturado para todos os logs.

### Justificativa

| Aspecto | JSON | Texto Plano |
|---------|------|-----------|
| **Parseabilidade** | Estruturado, fácil parse | Requer regex complexo |
| **Busca** | Campo específico (`.event`) | Busca em string |
| **Agregação** | Trivial (group by event) | Difícil |
| **Integração** | Nativa em ferramentas | Requer processamento |
| **Escalabilidade** | Pronto para big data | Não escalável |
| **Debugging** | Contexto completo | Informação perdida |

### Exemplo Comparativo

**Texto Plano**:
```
2024-02-05 20:30:05 INFO Agent analyst completed in 5021ms with 350 tokens
```

**JSON**:
```json
{
  "timestamp": "2024-02-05T20:30:05.234Z",
  "level": "INFO",
  "event": "agent_completed",
  "agent_name": "analyst",
  "duration_ms": 5021,
  "total_tokens": 350,
  "cost_usd": 0.0035,
  "execution_id": "1707084600.123456"
}
```

**Vantagens JSON**:
- ✅ Buscar por `event == "agent_completed"` é trivial
- ✅ Agrupar por `agent_name` é direto
- ✅ Calcular custo total é uma soma simples
- ✅ Correlacionar por `execution_id` é automático

---

## 2️⃣ POR QUE LOGS CENTRALIZADOS

### Decisão
Criar módulo central `infrastructure/logging/` com `StructuredLogger`.

### Justificativa

| Aspecto | Centralizado | Distribuído |
|---------|-------------|------------|
| **Consistência** | Garantida | Pode variar |
| **Manutenção** | Um lugar | Múltiplos lugares |
| **Mudanças** | Simples | Complexo |
| **Testes** | Fácil mockar | Difícil |
| **Evolução** | Pronto para novos formatos | Refatoração necessária |

### Estrutura Implementada

```
infrastructure/
  logging/
    __init__.py          # Exports
    logger.py            # JSONFormatter, StructuredLogger, configure_logging
```

### Benefícios

1. **Reutilização**: `get_logger(__name__)` em qualquer módulo
2. **Consistência**: Mesmo formato em todo o código
3. **Evolução**: Mudar para Datadog = uma mudança em um lugar
4. **Testing**: Mockar logger é trivial

---

## 3️⃣ COMO ISSO PREPARA PARA FERRAMENTAS

### Datadog

```python
# Fase 2: Integração com Datadog
from datadog import initialize, api

# Logs JSON são ingeridos diretamente
# Campos estruturados mapeiam para tags Datadog
# execution_id → trace_id
# agent_name → service
# event → event_type
```

**Benefício**: Rastreamento distribuído automático

### ELK Stack

```python
# Fase 2: Integração com Elasticsearch
# Logs JSON são indexados em Elasticsearch
# Kibana pode visualizar automaticamente
# Campos estruturados = índices automáticos
```

**Benefício**: Busca e análise em tempo real

### CloudWatch (AWS)

```python
# Fase 2: Integração com CloudWatch
# Logs JSON são enviados para CloudWatch
# Insights pode fazer queries estruturadas
# Métricas extraídas automaticamente
```

**Benefício**: Integração nativa com AWS

### Splunk

```python
# Fase 2: Integração com Splunk
# Logs JSON são parseados automaticamente
# Campos estruturados = sourcetype automático
# Dashboards pré-configurados possíveis
```

**Benefício**: Análise avançada de logs

---

## 4️⃣ DECISÕES DE DESIGN

### 4.1 StructuredLogger vs logging.Logger

**Decisão**: Criar `StructuredLogger` que encapsula `logging.Logger`

**Justificativa**:
- ✅ API simples: `logger.info(event="...", message="...", **kwargs)`
- ✅ Type hints: Todos os campos documentados
- ✅ Validação: Possível adicionar validação de campos
- ✅ Evolução: Fácil mudar implementação interna

**Alternativa Rejeitada**:
- ❌ Usar `logging.Logger` diretamente: API confusa (positional args)
- ❌ Usar `logging.LogRecord` diretamente: Muito baixo nível

### 4.2 JSONFormatter vs json.dumps()

**Decisão**: Criar `JSONFormatter` que estende `logging.Formatter`

**Justificativa**:
- ✅ Integra com logging padrão do Python
- ✅ Funciona com handlers existentes
- ✅ Suporta exception info automaticamente
- ✅ Fácil adicionar novos handlers (arquivo, syslog, etc.)

**Alternativa Rejeitada**:
- ❌ json.dumps() direto: Perde contexto do logging
- ❌ Logging padrão: Não estruturado

### 4.3 execution_id como Correlação

**Decisão**: Usar `execution_id` para correlacionar todos os logs de uma execução

**Justificativa**:
- ✅ Rastreamento completo de uma análise
- ✅ Agregar métricas por execução
- ✅ Debugging: Ver toda a sequência de eventos
- ✅ Pronto para trace_id em sistemas distribuídos

**Exemplo**:
```bash
# Encontrar todos os logs de uma execução
jq 'select(.execution_id == "1707084600.123456")'
```

---

## 5️⃣ TRADE-OFFS ACEITOS

### 5.1 Verbosidade vs Informação

**Trade-off**: Logs JSON são mais verbosos que texto plano

**Impacto**:
- ✅ Mais informação disponível
- ❌ Mais espaço em disco
- ✅ Estrutura compensa tamanho

**Mitigação**: Compressão de logs antigos (Fase 2)

### 5.2 Sem Logging Persistido Neste Passo

**Trade-off**: Logs vão apenas para stdout, não persistem

**Impacto**:
- ✅ Simples, sem dependências
- ❌ Logs perdidos ao fechar terminal
- ✅ Pronto para adicionar persistência

**Mitigação**: Redirecionar stdout para arquivo
```bash
python main.py > logs.jsonl 2>&1
```

### 5.3 Sem Sampling ou Filtering

**Trade-off**: Todos os logs são emitidos (sem sampling)

**Impacto**:
- ✅ Informação completa
- ❌ Pode ser verboso em produção
- ✅ Fácil adicionar filtering

**Mitigação**: Configurar nível de log
```python
configure_logging(level=logging.WARNING)  # Menos logs
```

---

## 6️⃣ PADRÕES DE DESIGN APLICADOS

### 6.1 Padrão: Formatter

```python
class JSONFormatter(logging.Formatter):
    """Transforma LogRecord em JSON"""
    def format(self, record):
        # Extrai campos estruturados
        # Retorna JSON string
```

**Benefício**: Separação de responsabilidades

### 6.2 Padrão: Facade

```python
class StructuredLogger:
    """Simplifica API de logging"""
    def info(self, event, message, **kwargs):
        # Chama logger.log() com campos estruturados
```

**Benefício**: API simples, implementação flexível

### 6.3 Padrão: Factory

```python
def get_logger(name: str) -> StructuredLogger:
    """Factory para criar loggers"""
    return StructuredLogger(name)
```

**Benefício**: Centraliza criação, fácil mockar

---

## 7️⃣ INTEGRAÇÃO COM CÓDIGO EXISTENTE

### Sem Alterações em Contratos Públicos

```python
# Antes
async def execute(self, context: ExecutionContext) -> ExecutionContext:
    # Lógica

# Depois (mesma assinatura)
async def execute(self, context: ExecutionContext) -> ExecutionContext:
    # Logging adicionado
    logger.info(...)
    # Lógica (inalterada)
    logger.info(...)
```

### Sem Refatoração de Arquitetura

- ✅ Logging adicionado em camadas existentes
- ✅ Sem mudança em estrutura de pastas
- ✅ Sem mudança em dependências entre módulos
- ✅ Sem mudança em tipos de dados

---

## 8️⃣ COMO EVOLUIR

### Fase 2: Persistência

```python
# Adicionar handler para arquivo
handler = logging.FileHandler("logs/execution.jsonl")
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)
```

### Fase 3: Integração com Datadog

```python
# Adicionar handler para Datadog
from datadog_logger import DatadogHandler
handler = DatadogHandler(api_key="...", service="business-agents")
logger.addHandler(handler)
```

### Fase 4: Dashboards

```python
# Queries em Datadog
# Latência média por agente
# Custo total por dia
# Taxa de sucesso
```

### Fase 5: Alertas

```python
# Alertas em Datadog
# Se execution_failed > 5 em 1 hora
# Se duration_ms > 30000
# Se cost_usd > 1.0
```

---

## 9️⃣ EXEMPLOS DE EVOLUÇÃO

### Adicionar Novo Evento

```python
# Antes: Sem logging
def _handle_agent_failure(self, context, agent_name, error):
    context.metadata[agent_name].status = ExecutionStatus.FAILED

# Depois: Com logging
def _handle_agent_failure(self, context, agent_name, error):
    context.metadata[agent_name].status = ExecutionStatus.FAILED
    logger.warning(
        event="agent_failure_handled",
        message=f"Handled failure for {agent_name}",
        execution_id=context.execution_id,
        agent_name=agent_name,
        error=str(error)
    )
```

### Adicionar Métrica

```python
# Antes: Sem logging de custo
logger.info(event="agent_completed", ...)

# Depois: Com custo
logger.info(
    event="agent_completed",
    ...,
    cost_usd=metadata.cost_usd  # Novo campo
)
```

---

## 🔟 CONCLUSÃO

A implementação de observabilidade:

✅ **É não-invasiva**: Logging adicionado sem refatoração
✅ **É extensível**: Fácil adicionar novos eventos
✅ **É preparada**: Pronta para ferramentas profissionais
✅ **É estruturada**: JSON facilita análise
✅ **É rastreável**: execution_id correlaciona tudo

**Próximo passo**: Persistência e integração com ferramentas (Fase 2)
