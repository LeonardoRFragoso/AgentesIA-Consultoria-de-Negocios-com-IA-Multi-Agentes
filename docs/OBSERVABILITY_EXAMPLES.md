# EXEMPLOS DE LOGS JSON GERADOS

## 1️⃣ EXECUÇÃO BEM-SUCEDIDA COMPLETA

### Logs Gerados (em ordem)

```json
{
  "timestamp": "2024-02-05T20:30:00.000Z",
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

```json
{
  "timestamp": "2024-02-05T20:30:00.050Z",
  "level": "DEBUG",
  "logger": "orchestrator.orchestrator",
  "message": "Execution plan generated",
  "execution_id": "1707084600.123456",
  "event": "execution_plan",
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

```json
{
  "timestamp": "2024-02-05T20:30:00.100Z",
  "level": "INFO",
  "logger": "orchestrator.orchestrator",
  "message": "Starting execution of layer 1",
  "execution_id": "1707084600.123456",
  "event": "layer_started",
  "layer": 1,
  "agents": ["analyst"],
  "extra_data": {"agent_count": 1}
}
```

```json
{
  "timestamp": "2024-02-05T20:30:00.150Z",
  "level": "INFO",
  "logger": "core.agent",
  "message": "Agent analyst started execution",
  "execution_id": "1707084600.123456",
  "event": "agent_started",
  "agent_name": "analyst",
  "extra_data": {
    "model": "claude-3-haiku-20240307",
    "timeout_seconds": 30.0,
    "dependencies": []
  }
}
```

```json
{
  "timestamp": "2024-02-05T20:30:05.234Z",
  "level": "INFO",
  "logger": "core.agent",
  "message": "Agent analyst completed successfully",
  "execution_id": "1707084600.123456",
  "event": "agent_completed",
  "agent_name": "analyst",
  "duration_ms": 5084,
  "input_tokens": 150,
  "output_tokens": 200,
  "total_tokens": 350,
  "cost_usd": 0.0035,
  "status": "COMPLETED"
}
```

```json
{
  "timestamp": "2024-02-05T20:30:05.250Z",
  "level": "INFO",
  "logger": "orchestrator.orchestrator",
  "message": "Layer 1 completed successfully",
  "execution_id": "1707084600.123456",
  "event": "layer_completed",
  "layer": 1,
  "agents": ["analyst"],
  "duration_ms": 5150
}
```

```json
{
  "timestamp": "2024-02-05T20:30:05.300Z",
  "level": "INFO",
  "logger": "orchestrator.orchestrator",
  "message": "Starting execution of layer 2",
  "execution_id": "1707084600.123456",
  "event": "layer_started",
  "layer": 2,
  "agents": ["commercial", "market"],
  "extra_data": {"agent_count": 2}
}
```

```json
{
  "timestamp": "2024-02-05T20:30:05.350Z",
  "level": "INFO",
  "logger": "core.agent",
  "message": "Agent commercial started execution",
  "execution_id": "1707084600.123456",
  "event": "agent_started",
  "agent_name": "commercial",
  "extra_data": {
    "model": "claude-3-haiku-20240307",
    "timeout_seconds": 30.0,
    "dependencies": ["analyst"]
  }
}
```

```json
{
  "timestamp": "2024-02-05T20:30:05.400Z",
  "level": "INFO",
  "logger": "core.agent",
  "message": "Agent market started execution",
  "execution_id": "1707084600.123456",
  "event": "agent_started",
  "agent_name": "market",
  "extra_data": {
    "model": "claude-3-haiku-20240307",
    "timeout_seconds": 30.0,
    "dependencies": ["analyst"]
  }
}
```

```json
{
  "timestamp": "2024-02-05T20:30:10.456Z",
  "level": "INFO",
  "logger": "core.agent",
  "message": "Agent commercial completed successfully",
  "execution_id": "1707084600.123456",
  "event": "agent_completed",
  "agent_name": "commercial",
  "duration_ms": 5106,
  "input_tokens": 180,
  "output_tokens": 220,
  "total_tokens": 400,
  "cost_usd": 0.0040,
  "status": "COMPLETED"
}
```

```json
{
  "timestamp": "2024-02-05T20:30:10.567Z",
  "level": "INFO",
  "logger": "core.agent",
  "message": "Agent market completed successfully",
  "execution_id": "1707084600.123456",
  "event": "agent_completed",
  "agent_name": "market",
  "duration_ms": 5167,
  "input_tokens": 170,
  "output_tokens": 210,
  "total_tokens": 380,
  "cost_usd": 0.0038,
  "status": "COMPLETED"
}
```

```json
{
  "timestamp": "2024-02-05T20:30:10.600Z",
  "level": "INFO",
  "logger": "orchestrator.orchestrator",
  "message": "Layer 2 completed successfully",
  "execution_id": "1707084600.123456",
  "event": "layer_completed",
  "layer": 2,
  "agents": ["commercial", "market"],
  "duration_ms": 5300
}
```

```json
{
  "timestamp": "2024-02-05T20:30:10.650Z",
  "level": "INFO",
  "logger": "orchestrator.orchestrator",
  "message": "Starting execution of layer 3",
  "execution_id": "1707084600.123456",
  "event": "layer_started",
  "layer": 3,
  "agents": ["financial"],
  "extra_data": {"agent_count": 1}
}
```

```json
{
  "timestamp": "2024-02-05T20:30:10.700Z",
  "level": "INFO",
  "logger": "core.agent",
  "message": "Agent financial started execution",
  "execution_id": "1707084600.123456",
  "event": "agent_started",
  "agent_name": "financial",
  "extra_data": {
    "model": "claude-3-haiku-20240307",
    "timeout_seconds": 30.0,
    "dependencies": ["analyst", "commercial"]
  }
}
```

```json
{
  "timestamp": "2024-02-05T20:30:15.789Z",
  "level": "INFO",
  "logger": "core.agent",
  "message": "Agent financial completed successfully",
  "execution_id": "1707084600.123456",
  "event": "agent_completed",
  "agent_name": "financial",
  "duration_ms": 5089,
  "input_tokens": 200,
  "output_tokens": 240,
  "total_tokens": 440,
  "cost_usd": 0.0044,
  "status": "COMPLETED"
}
```

```json
{
  "timestamp": "2024-02-05T20:30:15.820Z",
  "level": "INFO",
  "logger": "orchestrator.orchestrator",
  "message": "Layer 3 completed successfully",
  "execution_id": "1707084600.123456",
  "event": "layer_completed",
  "layer": 3,
  "agents": ["financial"],
  "duration_ms": 5170
}
```

```json
{
  "timestamp": "2024-02-05T20:30:15.870Z",
  "level": "INFO",
  "logger": "orchestrator.orchestrator",
  "message": "Starting execution of layer 4",
  "execution_id": "1707084600.123456",
  "event": "layer_started",
  "layer": 4,
  "agents": ["reviewer"],
  "extra_data": {"agent_count": 1}
}
```

```json
{
  "timestamp": "2024-02-05T20:30:15.920Z",
  "level": "INFO",
  "logger": "core.agent",
  "message": "Agent reviewer started execution",
  "execution_id": "1707084600.123456",
  "event": "agent_started",
  "agent_name": "reviewer",
  "extra_data": {
    "model": "claude-3-haiku-20240307",
    "timeout_seconds": 30.0,
    "dependencies": ["analyst", "commercial", "financial", "market"]
  }
}
```

```json
{
  "timestamp": "2024-02-05T20:30:20.987Z",
  "level": "INFO",
  "logger": "core.agent",
  "message": "Agent reviewer completed successfully",
  "execution_id": "1707084600.123456",
  "event": "agent_completed",
  "agent_name": "reviewer",
  "duration_ms": 5067,
  "input_tokens": 250,
  "output_tokens": 300,
  "total_tokens": 550,
  "cost_usd": 0.0055,
  "status": "COMPLETED"
}
```

```json
{
  "timestamp": "2024-02-05T20:30:21.020Z",
  "level": "INFO",
  "logger": "orchestrator.orchestrator",
  "message": "Layer 4 completed successfully",
  "execution_id": "1707084600.123456",
  "event": "layer_completed",
  "layer": 4,
  "agents": ["reviewer"],
  "duration_ms": 5150
}
```

```json
{
  "timestamp": "2024-02-05T20:30:21.050Z",
  "level": "INFO",
  "logger": "orchestrator.orchestrator",
  "message": "Business analysis execution completed successfully",
  "execution_id": "1707084600.123456",
  "event": "execution_completed",
  "duration_ms": 21050,
  "total_tokens": 2120,
  "cost_usd": 0.0212,
  "status": "COMPLETED"
}
```

---

## 2️⃣ EXECUÇÃO COM FALHA PARCIAL

### Cenário: Commercial Agent Timeout

```json
{
  "timestamp": "2024-02-05T20:30:00.000Z",
  "level": "INFO",
  "logger": "orchestrator.orchestrator",
  "message": "Starting business analysis execution",
  "execution_id": "1707084600.654321",
  "event": "execution_started",
  "extra_data": {
    "problem_length": 150,
    "business_type": "B2B",
    "analysis_depth": "Profunda",
    "total_agents": 5,
    "total_layers": 4
  }
}
```

```json
{
  "timestamp": "2024-02-05T20:30:05.234Z",
  "level": "INFO",
  "logger": "core.agent",
  "message": "Agent analyst completed successfully",
  "execution_id": "1707084600.654321",
  "event": "agent_completed",
  "agent_name": "analyst",
  "duration_ms": 5084,
  "input_tokens": 150,
  "output_tokens": 200,
  "total_tokens": 350,
  "cost_usd": 0.0035,
  "status": "COMPLETED"
}
```

```json
{
  "timestamp": "2024-02-05T20:30:05.350Z",
  "level": "INFO",
  "logger": "core.agent",
  "message": "Agent commercial started execution",
  "execution_id": "1707084600.654321",
  "event": "agent_started",
  "agent_name": "commercial",
  "extra_data": {
    "model": "claude-3-haiku-20240307",
    "timeout_seconds": 30.0,
    "dependencies": ["analyst"]
  }
}
```

```json
{
  "timestamp": "2024-02-05T20:30:05.400Z",
  "level": "INFO",
  "logger": "core.agent",
  "message": "Agent market started execution",
  "execution_id": "1707084600.654321",
  "event": "agent_started",
  "agent_name": "market",
  "extra_data": {
    "model": "claude-3-haiku-20240307",
    "timeout_seconds": 30.0,
    "dependencies": ["analyst"]
  }
}
```

```json
{
  "timestamp": "2024-02-05T20:30:10.567Z",
  "level": "INFO",
  "logger": "core.agent",
  "message": "Agent market completed successfully",
  "execution_id": "1707084600.654321",
  "event": "agent_completed",
  "agent_name": "market",
  "duration_ms": 5167,
  "input_tokens": 170,
  "output_tokens": 210,
  "total_tokens": 380,
  "cost_usd": 0.0038,
  "status": "COMPLETED"
}
```

```json
{
  "timestamp": "2024-02-05T20:30:35.456Z",
  "level": "ERROR",
  "logger": "core.agent",
  "message": "Agent commercial timed out after 30.0s",
  "execution_id": "1707084600.654321",
  "event": "agent_timeout",
  "agent_name": "commercial",
  "duration_ms": 30012,
  "status": "TIMEOUT",
  "error": "Timeout after 30.0s"
}
```

```json
{
  "timestamp": "2024-02-05T20:30:35.500Z",
  "level": "WARNING",
  "logger": "orchestrator.orchestrator",
  "message": "Layer 2 completed with 1 failure(s)",
  "execution_id": "1707084600.654321",
  "event": "layer_completed_with_failures",
  "layer": 2,
  "duration_ms": 30150,
  "extra_data": {
    "failed_agents": ["commercial"],
    "successful_agents": ["market"]
  }
}
```

```json
{
  "timestamp": "2024-02-05T20:30:35.550Z",
  "level": "INFO",
  "logger": "core.agent",
  "message": "Agent financial started execution",
  "execution_id": "1707084600.654321",
  "event": "agent_started",
  "agent_name": "financial",
  "extra_data": {
    "model": "claude-3-haiku-20240307",
    "timeout_seconds": 30.0,
    "dependencies": ["analyst", "commercial"]
  }
}
```

```json
{
  "timestamp": "2024-02-05T20:30:40.678Z",
  "level": "INFO",
  "logger": "core.agent",
  "message": "Agent financial completed successfully",
  "execution_id": "1707084600.654321",
  "event": "agent_completed",
  "agent_name": "financial",
  "duration_ms": 5128,
  "input_tokens": 200,
  "output_tokens": 240,
  "total_tokens": 440,
  "cost_usd": 0.0044,
  "status": "COMPLETED"
}
```

```json
{
  "timestamp": "2024-02-05T20:30:40.789Z",
  "level": "INFO",
  "logger": "core.agent",
  "message": "Agent reviewer started execution",
  "execution_id": "1707084600.654321",
  "event": "agent_started",
  "agent_name": "reviewer",
  "extra_data": {
    "model": "claude-3-haiku-20240307",
    "timeout_seconds": 30.0,
    "dependencies": ["analyst", "commercial", "financial", "market"]
  }
}
```

```json
{
  "timestamp": "2024-02-05T20:30:45.890Z",
  "level": "INFO",
  "logger": "core.agent",
  "message": "Agent reviewer completed successfully",
  "execution_id": "1707084600.654321",
  "event": "agent_completed",
  "agent_name": "reviewer",
  "duration_ms": 5101,
  "input_tokens": 250,
  "output_tokens": 300,
  "total_tokens": 550,
  "cost_usd": 0.0055,
  "status": "COMPLETED"
}
```

```json
{
  "timestamp": "2024-02-05T20:30:45.950Z",
  "level": "WARNING",
  "logger": "orchestrator.orchestrator",
  "message": "Business analysis execution completed with partial failures",
  "execution_id": "1707084600.654321",
  "event": "execution_partial_failure",
  "duration_ms": 45950,
  "total_tokens": 1720,
  "cost_usd": 0.0172,
  "status": "PARTIAL_FAILURE",
  "extra_data": {
    "failed_agents": ["commercial"]
  }
}
```

---

## 3️⃣ EXECUÇÃO COM ERRO CRÍTICO

### Cenário: API Key não configurada

```json
{
  "timestamp": "2024-02-05T20:30:00.000Z",
  "level": "INFO",
  "logger": "orchestrator.orchestrator",
  "message": "Starting business analysis execution",
  "execution_id": "1707084600.999999",
  "event": "execution_started",
  "extra_data": {
    "problem_length": 150,
    "business_type": "Varejo",
    "analysis_depth": "Rápida",
    "total_agents": 5,
    "total_layers": 4
  }
}
```

```json
{
  "timestamp": "2024-02-05T20:30:00.100Z",
  "level": "INFO",
  "logger": "core.agent",
  "message": "Agent analyst started execution",
  "execution_id": "1707084600.999999",
  "event": "agent_started",
  "agent_name": "analyst",
  "extra_data": {
    "model": "claude-3-haiku-20240307",
    "timeout_seconds": 30.0,
    "dependencies": []
  }
}
```

```json
{
  "timestamp": "2024-02-05T20:30:00.150Z",
  "level": "ERROR",
  "logger": "core.agent",
  "message": "Agent analyst failed with error: ANTHROPIC_API_KEY not found",
  "execution_id": "1707084600.999999",
  "event": "agent_failed",
  "agent_name": "analyst",
  "duration_ms": 50,
  "status": "FAILED",
  "error": "ANTHROPIC_API_KEY not found",
  "extra_data": {
    "exception_type": "ValueError",
    "stacktrace": "Traceback (most recent call last):\n  File \"core/agent.py\", line 145, in _execute_internal\n    client = anthropic.Anthropic(api_key=os.getenv(\"ANTHROPIC_API_KEY\"))\n  File \"anthropic/__init__.py\", line 123, in __init__\n    raise ValueError(\"ANTHROPIC_API_KEY not found\")\nValueError: ANTHROPIC_API_KEY not found"
  }
}
```

```json
{
  "timestamp": "2024-02-05T20:30:00.200Z",
  "level": "ERROR",
  "logger": "orchestrator.orchestrator",
  "message": "Business analysis execution failed: Agent 'analyst' failed: ANTHROPIC_API_KEY not found",
  "execution_id": "1707084600.999999",
  "event": "execution_failed",
  "duration_ms": 200,
  "status": "FAILED",
  "error": "Agent 'analyst' failed: ANTHROPIC_API_KEY not found"
}
```

---

## 4️⃣ ANÁLISE DE LOGS

### Encontrar Todas as Execuções Falhadas

```bash
python main.py 2>&1 | jq 'select(.event == "execution_failed")'
```

### Calcular Custo Total por Execução

```bash
python main.py 2>&1 | jq 'select(.event == "execution_completed") | {execution_id, cost: .cost_usd}'
```

### Encontrar Agentes Lentos (> 5 segundos)

```bash
python main.py 2>&1 | jq 'select(.event == "agent_completed" and .duration_ms > 5000) | {agent: .agent_name, duration: .duration_ms}'
```

### Contar Timeouts por Agente

```bash
python main.py 2>&1 | jq 'select(.event == "agent_timeout") | .agent_name' | sort | uniq -c
```

### Calcular Tokens Médios por Agente

```bash
python main.py 2>&1 | jq 'select(.event == "agent_completed") | {agent: .agent_name, tokens: .total_tokens}' | jq -s 'group_by(.agent) | map({agent: .[0].agent, avg_tokens: (map(.tokens) | add / length)})'
```

### Rastrear Execução Específica

```bash
python main.py 2>&1 | jq 'select(.execution_id == "1707084600.123456")'
```

---

## 5️⃣ MÉTRICAS EXTRAÍDAS

### Latência Total por Execução

```bash
python main.py 2>&1 | jq 'select(.event == "execution_completed") | {execution_id, latency_ms: .duration_ms}'
```

### Custo Total por Agente

```bash
python main.py 2>&1 | jq 'select(.event == "agent_completed") | {agent: .agent_name, cost: .cost_usd}' | jq -s 'group_by(.agent) | map({agent: .[0].agent, total_cost: (map(.cost) | add)})'
```

### Taxa de Sucesso

```bash
python main.py 2>&1 | jq 'select(.event == "execution_completed" or .event == "execution_partial_failure" or .event == "execution_failed") | .status' | sort | uniq -c
```

### Distribuição de Tokens

```bash
python main.py 2>&1 | jq 'select(.event == "agent_completed") | .total_tokens' | jq -s '{min: min, max: max, avg: (add / length)}'
```

---

## Conclusão

Os exemplos acima mostram:
- ✅ Logs estruturados em JSON
- ✅ Rastreamento completo via execution_id
- ✅ Métricas detalhadas por agente
- ✅ Tratamento de falhas e timeouts
- ✅ Fácil análise com jq

Próximo passo: Persistência e integração com ferramentas (Fase 2)
