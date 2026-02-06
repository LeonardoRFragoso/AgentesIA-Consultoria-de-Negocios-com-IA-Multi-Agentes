# OBSERVABILIDADE - LOGGING ESTRUTURADO

## 1️⃣ PADRÃO DE LOGGING

### Formato JSON

Todos os logs são emitidos em formato JSON estruturado para fácil parsing e análise:

```json
{
  "timestamp": "2024-02-05T20:30:00.123Z",
  "level": "INFO",
  "logger": "orchestrator.orchestrator",
  "message": "Starting business analysis execution",
  "execution_id": "1707084600.123456",
  "event": "execution_started",
  "extra_data": {
    "problem_length": 150,
    "business_type": "SaaS",
    "analysis_depth": "Padrão",
    "total_agents": 5,
    "total_layers": 4
  }
}
```

### Campos Obrigatórios

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `timestamp` | string (ISO 8601) | Timestamp UTC do evento |
| `level` | string | DEBUG, INFO, WARNING, ERROR, CRITICAL |
| `logger` | string | Nome do logger (módulo) |
| `message` | string | Descrição legível do evento |
| `execution_id` | string | ID único da execução |
| `event` | string | Tipo de evento (execution_started, agent_completed, etc.) |

### Campos Condicionais

| Campo | Tipo | Quando Presente |
|-------|------|-----------------|
| `agent_name` | string | Eventos relacionados a agentes |
| `duration_ms` | float | Eventos com duração medida |
| `input_tokens` | int | Eventos de agentes (entrada LLM) |
| `output_tokens` | int | Eventos de agentes (saída LLM) |
| `total_tokens` | int | Eventos de agentes (total) |
| `cost_usd` | float | Eventos de agentes (custo estimado) |
| `status` | string | Status final (COMPLETED, FAILED, TIMEOUT) |
| `error` | string | Mensagem de erro (se houver) |
| `layer` | int | Número da camada (eventos do orquestrador) |
| `agents` | list | Lista de agentes (eventos do orquestrador) |
| `extra_data` | object | Dados adicionais contextuais |

---

## 2️⃣ EVENTOS DE LOG MAPEADOS

### Execução Global

#### `execution_started`
**Quando**: Início da execução de análise
**Nível**: INFO
**Campos**:
- `execution_id`
- `extra_data`: problem_length, business_type, analysis_depth, total_agents, total_layers

```json
{
  "timestamp": "2024-02-05T20:30:00.123Z",
  "level": "INFO",
  "event": "execution_started",
  "message": "Starting business analysis execution",
  "execution_id": "1707084600.123456",
  "extra_data": {
    "problem_length": 150,
    "business_type": "SaaS",
    "analysis_depth": "Padrão",
    "total_agents": 5,
    "total_layers": 4
  }
}
```

#### `execution_plan`
**Quando**: Plano de execução gerado
**Nível**: DEBUG
**Campos**:
- `execution_id`
- `extra_data`: layers (array com layer, agents, count)

```json
{
  "timestamp": "2024-02-05T20:30:00.124Z",
  "level": "DEBUG",
  "event": "execution_plan",
  "message": "Execution plan generated",
  "execution_id": "1707084600.123456",
  "extra_data": {
    "layers": [
      {"layer": 1, "agents": ["analyst"], "count": 1},
      {"layer": 2, "agents": ["commercial", "market"], "count": 2},
      {"layer": 3, "agents": ["financial"], "count": 1},
      {"layer": 4, "agents": ["reviewer"], "count": 1}
    ]
  }
}
```

#### `execution_completed`
**Quando**: Execução concluída com sucesso (todos os agentes)
**Nível**: INFO
**Campos**:
- `execution_id`
- `duration_ms`
- `total_tokens`
- `cost_usd`
- `status`: "COMPLETED"

```json
{
  "timestamp": "2024-02-05T20:30:20.456Z",
  "level": "INFO",
  "event": "execution_completed",
  "message": "Business analysis execution completed successfully",
  "execution_id": "1707084600.123456",
  "duration_ms": 20123,
  "total_tokens": 1560,
  "cost_usd": 0.0187,
  "status": "COMPLETED"
}
```

#### `execution_partial_failure`
**Quando**: Execução concluída mas com falhas parciais
**Nível**: WARNING
**Campos**:
- `execution_id`
- `duration_ms`
- `total_tokens`
- `cost_usd`
- `status`: "PARTIAL_FAILURE"
- `extra_data`: failed_agents (array)

```json
{
  "timestamp": "2024-02-05T20:30:20.456Z",
  "level": "WARNING",
  "event": "execution_partial_failure",
  "message": "Business analysis execution completed with partial failures",
  "execution_id": "1707084600.123456",
  "duration_ms": 20123,
  "total_tokens": 1200,
  "cost_usd": 0.0145,
  "status": "PARTIAL_FAILURE",
  "extra_data": {
    "failed_agents": ["commercial"]
  }
}
```

#### `execution_failed`
**Quando**: Execução falhou completamente
**Nível**: ERROR
**Campos**:
- `execution_id`
- `duration_ms`
- `status`: "FAILED"
- `error`: mensagem de erro

```json
{
  "timestamp": "2024-02-05T20:30:15.789Z",
  "level": "ERROR",
  "event": "execution_failed",
  "message": "Business analysis execution failed: API key not found",
  "execution_id": "1707084600.123456",
  "duration_ms": 5123,
  "status": "FAILED",
  "error": "API key not found"
}
```

### Orquestrador - Camadas

#### `layer_started`
**Quando**: Início da execução de uma camada
**Nível**: INFO
**Campos**:
- `execution_id`
- `layer`: número da camada
- `agents`: lista de agentes
- `extra_data`: agent_count

```json
{
  "timestamp": "2024-02-05T20:30:00.200Z",
  "level": "INFO",
  "event": "layer_started",
  "message": "Starting execution of layer 2",
  "execution_id": "1707084600.123456",
  "layer": 2,
  "agents": ["commercial", "market"],
  "extra_data": {"agent_count": 2}
}
```

#### `layer_completed`
**Quando**: Camada concluída com sucesso
**Nível**: INFO
**Campos**:
- `execution_id`
- `layer`: número da camada
- `agents`: lista de agentes
- `duration_ms`

```json
{
  "timestamp": "2024-02-05T20:30:05.234Z",
  "level": "INFO",
  "event": "layer_completed",
  "message": "Layer 2 completed successfully",
  "execution_id": "1707084600.123456",
  "layer": 2,
  "agents": ["commercial", "market"],
  "duration_ms": 5034
}
```

#### `layer_completed_with_failures`
**Quando**: Camada concluída com falhas parciais
**Nível**: WARNING
**Campos**:
- `execution_id`
- `layer`: número da camada
- `duration_ms`
- `extra_data`: failed_agents, successful_agents

```json
{
  "timestamp": "2024-02-05T20:30:05.234Z",
  "level": "WARNING",
  "event": "layer_completed_with_failures",
  "message": "Layer 2 completed with 1 failure(s)",
  "execution_id": "1707084600.123456",
  "layer": 2,
  "duration_ms": 5034,
  "extra_data": {
    "failed_agents": ["commercial"],
    "successful_agents": ["market"]
  }
}
```

### Agentes

#### `agent_started`
**Quando**: Agente inicia execução
**Nível**: INFO
**Campos**:
- `execution_id`
- `agent_name`
- `extra_data`: model, timeout_seconds, dependencies

```json
{
  "timestamp": "2024-02-05T20:30:00.300Z",
  "level": "INFO",
  "event": "agent_started",
  "message": "Agent analyst started execution",
  "execution_id": "1707084600.123456",
  "agent_name": "analyst",
  "extra_data": {
    "model": "claude-3-haiku-20240307",
    "timeout_seconds": 30.0,
    "dependencies": []
  }
}
```

#### `agent_completed`
**Quando**: Agente concluído com sucesso
**Nível**: INFO
**Campos**:
- `execution_id`
- `agent_name`
- `duration_ms`
- `input_tokens`
- `output_tokens`
- `total_tokens`
- `cost_usd`
- `status`: "COMPLETED"

```json
{
  "timestamp": "2024-02-05T20:30:05.234Z",
  "level": "INFO",
  "event": "agent_completed",
  "message": "Agent analyst completed successfully",
  "execution_id": "1707084600.123456",
  "agent_name": "analyst",
  "duration_ms": 5021,
  "input_tokens": 150,
  "output_tokens": 200,
  "total_tokens": 350,
  "cost_usd": 0.0035,
  "status": "COMPLETED"
}
```

#### `agent_timeout`
**Quando**: Agente excede timeout
**Nível**: ERROR
**Campos**:
- `execution_id`
- `agent_name`
- `duration_ms`
- `status`: "TIMEOUT"
- `error`: mensagem de timeout

```json
{
  "timestamp": "2024-02-05T20:30:30.456Z",
  "level": "ERROR",
  "event": "agent_timeout",
  "message": "Agent commercial timed out after 30.0s",
  "execution_id": "1707084600.123456",
  "agent_name": "commercial",
  "duration_ms": 30012,
  "status": "TIMEOUT",
  "error": "Timeout after 30.0s"
}
```

#### `agent_failed`
**Quando**: Agente falha com exceção
**Nível**: ERROR
**Campos**:
- `execution_id`
- `agent_name`
- `duration_ms`
- `status`: "FAILED"
- `error`: mensagem de erro
- `extra_data`: exception_type, stacktrace

```json
{
  "timestamp": "2024-02-05T20:30:10.567Z",
  "level": "ERROR",
  "event": "agent_failed",
  "message": "Agent financial failed with error: API rate limit exceeded",
  "execution_id": "1707084600.123456",
  "agent_name": "financial",
  "duration_ms": 10234,
  "status": "FAILED",
  "error": "API rate limit exceeded",
  "extra_data": {
    "exception_type": "LLMProviderError",
    "stacktrace": "Traceback (most recent call last):\n  File \"...\", line 147, in _execute_internal\n    message = client.messages.create(...)\nLLMProviderError: API rate limit exceeded"
  }
}
```

---

## 3️⃣ FLUXO COMPLETO DE LOGS

### Execução Bem-Sucedida

```
1. execution_started (INFO)
2. execution_plan (DEBUG)
3. layer_started (INFO) - Camada 1
4. agent_started (INFO) - analyst
5. agent_completed (INFO) - analyst
6. layer_completed (INFO) - Camada 1
7. layer_started (INFO) - Camada 2
8. agent_started (INFO) - commercial
9. agent_started (INFO) - market
10. agent_completed (INFO) - commercial
11. agent_completed (INFO) - market
12. layer_completed (INFO) - Camada 2
13. layer_started (INFO) - Camada 3
14. agent_started (INFO) - financial
15. agent_completed (INFO) - financial
16. layer_completed (INFO) - Camada 3
17. layer_started (INFO) - Camada 4
18. agent_started (INFO) - reviewer
19. agent_completed (INFO) - reviewer
20. layer_completed (INFO) - Camada 4
21. execution_completed (INFO)
```

### Execução com Falha Parcial

```
1. execution_started (INFO)
2. execution_plan (DEBUG)
3. layer_started (INFO) - Camada 1
4. agent_started (INFO) - analyst
5. agent_completed (INFO) - analyst
6. layer_completed (INFO) - Camada 1
7. layer_started (INFO) - Camada 2
8. agent_started (INFO) - commercial
9. agent_started (INFO) - market
10. agent_timeout (ERROR) - commercial
11. agent_completed (INFO) - market
12. layer_completed_with_failures (WARNING) - Camada 2
13. layer_started (INFO) - Camada 3
14. agent_started (INFO) - financial
15. agent_completed (INFO) - financial (com dados parciais)
16. layer_completed (INFO) - Camada 3
17. layer_started (INFO) - Camada 4
18. agent_started (INFO) - reviewer
19. agent_completed (INFO) - reviewer (com análise parcial)
20. layer_completed (INFO) - Camada 4
21. execution_partial_failure (WARNING)
```

---

## 4️⃣ COMO USAR

### Configurar Logging

```python
from infrastructure.logging import configure_logging
import logging

# Configurar logging global
configure_logging(level=logging.INFO)
```

### Obter Logger

```python
from infrastructure.logging import get_logger

logger = get_logger(__name__)

# Emitir log
logger.info(
    event="meu_evento",
    message="Descrição do evento",
    execution_id="123456",
    agent_name="analyst",
    duration_ms=1234.5,
    status="COMPLETED"
)
```

### Capturar Logs

Os logs são emitidos para stdout em formato JSON, um por linha:

```bash
python main.py 2>&1 | grep "execution_completed"
```

### Processar Logs com jq

```bash
python main.py 2>&1 | jq 'select(.event == "agent_completed")'
```

---

## 5️⃣ INTEGRAÇÃO COM FERRAMENTAS

### Datadog

```python
# Será implementado em próximo passo
# Logs JSON podem ser ingeridos diretamente pelo Datadog
```

### ELK Stack (Elasticsearch, Logstash, Kibana)

```python
# Logs JSON são compatíveis com Logstash
# Podem ser indexados em Elasticsearch
# Visualizados em Kibana
```

### CloudWatch (AWS)

```python
# Logs JSON podem ser enviados para CloudWatch
# Estrutura JSON facilita parsing
```

### Splunk

```python
# Logs JSON são compatíveis com Splunk
# Campos estruturados facilitam busca e análise
```

---

## 6️⃣ EXEMPLOS DE QUERIES

### Encontrar Execuções Falhadas

```bash
python main.py 2>&1 | jq 'select(.event == "execution_failed")'
```

### Encontrar Agentes Lentos

```bash
python main.py 2>&1 | jq 'select(.event == "agent_completed" and .duration_ms > 10000)'
```

### Calcular Custo Total

```bash
python main.py 2>&1 | jq 'select(.event == "execution_completed") | .cost_usd' | awk '{sum+=$1} END {print "Total: $" sum}'
```

### Encontrar Timeouts

```bash
python main.py 2>&1 | jq 'select(.event == "agent_timeout")'
```

### Analisar Distribuição de Tokens

```bash
python main.py 2>&1 | jq 'select(.event == "agent_completed") | {agent: .agent_name, tokens: .total_tokens}'
```

---

## 7️⃣ MÉTRICAS DISPONÍVEIS

### Por Execução
- `duration_ms`: Latência total
- `total_tokens`: Tokens consumidos
- `cost_usd`: Custo total
- Status: COMPLETED, PARTIAL_FAILURE, FAILED

### Por Agente
- `duration_ms`: Latência do agente
- `input_tokens`: Tokens de entrada
- `output_tokens`: Tokens de saída
- `total_tokens`: Total de tokens
- `cost_usd`: Custo do agente
- Status: COMPLETED, FAILED, TIMEOUT

### Por Camada
- `duration_ms`: Latência da camada
- `agent_count`: Número de agentes
- Agentes bem-sucedidos vs falhados

---

## 8️⃣ PRÓXIMOS PASSOS

### Fase 2: Persistência de Logs
- [ ] Salvar logs em arquivo
- [ ] Rotação de logs
- [ ] Compressão de logs antigos

### Fase 3: Integração com Ferramentas
- [ ] Datadog
- [ ] ELK Stack
- [ ] CloudWatch
- [ ] Splunk

### Fase 4: Dashboards
- [ ] Dashboard de execuções
- [ ] Dashboard de agentes
- [ ] Dashboard de custos
- [ ] Dashboard de performance

### Fase 5: Alertas
- [ ] Alerta de execução falhada
- [ ] Alerta de timeout
- [ ] Alerta de custo alto
- [ ] Alerta de latência alta

---

## Conclusão

O sistema agora emite logs estruturados em JSON que:
- ✅ São fáceis de parsear
- ✅ Contêm contexto completo (execution_id)
- ✅ Rastreiam métricas importantes
- ✅ Permitem debugging detalhado
- ✅ Estão prontos para integração com ferramentas

Próximo passo: Implementar persistência e integração com ferramentas de observabilidade.
