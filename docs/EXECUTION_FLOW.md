# FLUXO DE EXECUÇÃO - EXEMPLO PRÁTICO

## 1. FLUXO COMPLETO DE EXECUÇÃO

### 1.1 Entrada: Problema de Negócio

```python
problem_description = """
Nossas vendas caíram 20% nos últimos 3 meses. 
Qual pode ser a causa e como devemos responder?
"""
```

### 1.2 Passo 1: Criar Contexto Inicial

```python
context = ExecutionContext(
    problem_description=problem_description,
    business_type="SaaS",
    analysis_depth="Padrão"
)

# Estado do contexto:
# - problem_description: "Nossas vendas caíram..."
# - results: {}  (vazio)
# - metadata: {}  (vazio)
# - execution_id: "1707084600.123456"
# - created_at: 2024-02-05 20:30:00
```

### 1.3 Passo 2: Criar Orquestrador

```python
agents = {
    "analyst": AnalystAgent(),
    "commercial": CommercialAgent(),
    "financial": FinancialAgent(),
    "market": MarketAgent(),
    "reviewer": ReviewerAgent(),
}

orchestrator = BusinessOrchestrator(agents)

# DAG Resolver identifica:
# Camada 1: [analyst]
# Camada 2: [commercial, market]
# Camada 3: [financial]
# Camada 4: [reviewer]
```

### 1.4 Passo 3: Executar Análise

```python
result_context = await orchestrator.execute(context)
```

---

## 2. EXECUÇÃO DETALHADA POR CAMADA

### 2.1 CAMADA 1: Analyst (Paralelo)

**Tempo**: T=0s

```
┌─────────────────────────────────────────┐
│ ANALYST AGENT                           │
├─────────────────────────────────────────┤
│ Status: RUNNING                         │
│ Dependências: []                        │
│ Timeout: 30s                            │
└─────────────────────────────────────────┘
```

**Execução Interna**:

```python
# 1. Carrega prompt
system_prompt = """
Você é um analista de negócio sênior com 15 anos de experiência...
"""

# 2. Constrói mensagem do usuário
user_message = """
Analise o seguinte problema de negócio:

Nossas vendas caíram 20% nos últimos 3 meses. 
Qual pode ser a causa e como devemos responder?

Forneça uma análise estruturada seguindo o formato especificado.
"""

# 3. Chama LLM
message = client.messages.create(
    model="claude-3-haiku-20240307",
    max_tokens=1024,
    system=system_prompt,
    messages=[{"role": "user", "content": user_message}]
)

# 4. Retorna resultado
analyst_output = """
## Síntese do Problema
Queda significativa de vendas em período curto, sugerindo causa aguda.

## Hipóteses Principais
1. Mudança no comportamento do cliente (churn)
2. Problema competitivo (novo concorrente, preço)
3. Problema operacional (qualidade, entrega)
4. Problema de marketing (redução de leads)
5. Sazonalidade ou fatores externos

## Variáveis Críticas
- Taxa de churn por segmento
- Novos leads vs conversão
- Feedback de clientes
- Atividade competitiva

## Próximos Passos
Validar hipóteses com dados de churn, leads e feedback.
"""
```

**Resultado no Contexto**:

```python
context.results["analyst"] = analyst_output
context.metadata["analyst"] = AgentMetadata(
    name="analyst",
    status=ExecutionStatus.COMPLETED,
    start_time=datetime(2024-02-05 20:30:00),
    end_time=datetime(2024-02-05 20:30:05),
    latency_ms=5000,
    input_tokens=150,
    output_tokens=200,
    total_tokens=350,
    cost_usd=0.0035
)
```

**Tempo**: T=5s ✓

---

### 2.2 CAMADA 2: Commercial + Market (Paralelo)

**Tempo**: T=5s

```
┌──────────────────────┐  ┌──────────────────────┐
│ COMMERCIAL AGENT     │  │ MARKET AGENT         │
├──────────────────────┤  ├──────────────────────┤
│ Status: RUNNING      │  │ Status: RUNNING      │
│ Depende de: analyst  │  │ Depende de: analyst  │
│ Timeout: 30s         │  │ Timeout: 30s         │
└──────────────────────┘  └──────────────────────┘
```

#### 2.2.1 Commercial Agent

**Execução**:

```python
# 1. Carrega prompt
system_prompt = """
Você é um estrategista comercial sênior...
"""

# 2. Constrói mensagem com contexto
analyst_output = context.get_agent_output("analyst")
user_message = f"""
Com base na seguinte análise de negócio:

{analyst_output}

E considerando o problema original:

Nossas vendas caíram 20%...

Desenvolva uma estratégia comercial detalhada.
"""

# 3. Chama LLM
commercial_output = """
## Estratégia Geral
Investigar causa raiz + ações imediatas de retenção

## Ações Curto Prazo (0-3 meses)
1. Análise de churn por segmento
2. Campanha de retenção para clientes em risco
3. Revisão de preço e ofertas

## Ações Médio Prazo (3-12 meses)
1. Novo produto/feature
2. Expansão de segmento
3. Parcerias estratégicas

## Métricas de Sucesso
- Redução de churn
- Aumento de NRR
- Recuperação de vendas
"""
```

**Resultado**:
```python
context.results["commercial"] = commercial_output
context.metadata["commercial"] = AgentMetadata(
    name="commercial",
    status=ExecutionStatus.COMPLETED,
    latency_ms=4800,
    total_tokens=320,
    cost_usd=0.0032
)
```

#### 2.2.2 Market Agent

**Execução**: Similar ao Commercial, mas com foco em mercado

```python
market_output = """
## Contexto de Mercado
Mercado SaaS em consolidação, competição aumentando

## Benchmarks Relevantes
- Churn médio: 5-8% ao mês
- CAC payback: 12-18 meses
- NRR: 110-120%

## Validação de Hipóteses
Hipótese 1 (churn): VALIDADA - padrão observado em mercado
Hipótese 2 (competição): POSSÍVEL - novos players entrando

## Tendências Aplicáveis
- Consolidação de mercado
- Aumento de preço
- Foco em retenção

## Riscos Competitivos
- Novos concorrentes com preço agressivo
- Consolidação de players maiores

## Oportunidades
- Nicho específico menos competitivo
- Integração com ferramentas populares
"""
```

**Tempo**: T=10s ✓

---

### 2.3 CAMADA 3: Financial (Paralelo)

**Tempo**: T=10s

```
┌──────────────────────────────────────┐
│ FINANCIAL AGENT                      │
├──────────────────────────────────────┤
│ Status: RUNNING                      │
│ Depende de: analyst, commercial      │
│ Timeout: 30s                         │
└──────────────────────────────────────┘
```

**Execução**:

```python
# 1. Carrega prompt
system_prompt = """
Você é um analista financeiro sênior...
"""

# 2. Constrói mensagem com contexto de 2 predecessores
analyst_output = context.get_agent_output("analyst")
commercial_output = context.get_agent_output("commercial")

user_message = f"""
Com base na análise:
{analyst_output}

E na estratégia comercial:
{commercial_output}

Forneça avaliação financeira detalhada.
"""

# 3. Chama LLM
financial_output = """
## Análise de Viabilidade
Estratégia é financeiramente viável com ROI positivo

## Estimativa de Investimento
- Retenção: $50K-100K
- Novo produto: $200K-300K
- Total: $250K-400K

## Estimativa de Retorno
- Redução de churn: +$500K/ano
- Aumento de NRR: +$300K/ano
- Total: +$800K/ano

## Riscos Financeiros
- Cenário pessimista: ROI negativo em 6 meses
- Cenário otimista: ROI positivo em 3 meses

## Priorização
1. Retenção (melhor ROI)
2. Novo produto
3. Parcerias

## Premissas
- Churn reduz 2% com retenção
- Novo produto gera 20% de upsell
"""
```

**Tempo**: T=15s ✓

---

### 2.4 CAMADA 4: Reviewer (Sequencial)

**Tempo**: T=15s

```
┌──────────────────────────────────────────┐
│ REVIEWER AGENT                           │
├──────────────────────────────────────────┤
│ Status: RUNNING                          │
│ Depende de: analyst, commercial,         │
│             financial, market            │
│ Timeout: 30s                             │
└──────────────────────────────────────────┘
```

**Execução**:

```python
# 1. Carrega prompt
system_prompt = """
Você é um executivo sênior (CEO/Board Member)...
"""

# 2. Constrói mensagem com TODOS os outputs anteriores
analyst_output = context.get_agent_output("analyst")
commercial_output = context.get_agent_output("commercial")
financial_output = context.get_agent_output("financial")
market_output = context.get_agent_output("market")

user_message = f"""
Você recebeu as seguintes análises:

PROBLEMA ORIGINAL:
Nossas vendas caíram 20%...

ANÁLISE DO ANALISTA:
{analyst_output}

ESTRATÉGIA COMERCIAL:
{commercial_output}

ANÁLISE FINANCEIRA:
{financial_output}

CONTEXTO DE MERCADO:
{market_output}

Consolide em diagnóstico executivo coerente.
"""

# 3. Chama LLM
reviewer_output = """
## Diagnóstico Executivo
Queda de vendas causada por aumento de churn em segmento principal.
Mercado está consolidando, competição aumentando.
Oportunidade de resposta rápida com foco em retenção.

## Análise de Coerência
✓ Todas as análises apontam para churn como causa principal
✓ Estratégia comercial alinhada com diagnóstico
✓ Viabilidade financeira confirmada
✓ Contexto de mercado valida hipóteses

## Recomendação Estratégica
Implementar programa de retenção agressivo + novo produto
Investimento: $250K-400K
Retorno esperado: $800K/ano

## Plano de Ação Consolidado
IMEDIATO (próximos 30 dias):
1. Análise de churn por segmento (1 semana)
2. Campanha de retenção (2 semanas)
3. Revisão de preço (1 semana)

CURTO PRAZO (1-3 meses):
1. Desenvolvimento de novo produto
2. Parcerias estratégicas
3. Expansão de segmento

## Métricas de Sucesso
- Redução de churn para <5% ao mês
- Aumento de NRR para 115%
- Recuperação de vendas em 3 meses

## Riscos Críticos
- Competição agressiva de novos players
- Possível consolidação do mercado
- Risco de perda de clientes-chave

## Próximos Passos (30 dias)
1. Kick-off com time de retenção
2. Análise detalhada de churn
3. Prototipagem de novo produto
4. Revisão de pricing
"""
```

**Tempo**: T=20s ✓

---

## 3. RESULTADO FINAL

### 3.1 Estado do Contexto

```python
result_context = ExecutionContext(
    problem_description="Nossas vendas caíram 20%...",
    business_type="SaaS",
    analysis_depth="Padrão",
    results={
        "analyst": "## Síntese do Problema...",
        "commercial": "## Estratégia Geral...",
        "financial": "## Análise de Viabilidade...",
        "market": "## Contexto de Mercado...",
        "reviewer": "## Diagnóstico Executivo..."
    },
    metadata={
        "analyst": AgentMetadata(..., latency_ms=5000, cost_usd=0.0035),
        "commercial": AgentMetadata(..., latency_ms=4800, cost_usd=0.0032),
        "financial": AgentMetadata(..., latency_ms=5200, cost_usd=0.0035),
        "market": AgentMetadata(..., latency_ms=4900, cost_usd=0.0033),
        "reviewer": AgentMetadata(..., latency_ms=5100, cost_usd=0.0052)
    },
    created_at=datetime(2024-02-05 20:30:00),
    started_at=datetime(2024-02-05 20:30:00),
    completed_at=datetime(2024-02-05 20:30:20),
    execution_id="1707084600.123456"
)
```

### 3.2 Metadados de Execução

```python
print(f"✓ Análise concluída!")
print(f"Latência total: {result_context.get_total_latency_ms():.0f}ms")  # ~20000ms
print(f"Tokens totais: {result_context.get_total_tokens()}")  # ~1500
print(f"Custo total: ${result_context.get_total_cost():.4f}")  # ~$0.0187

# Por agente:
for agent_name, metadata in result_context.metadata.items():
    print(f"{agent_name}: {metadata.duration_seconds:.1f}s, {metadata.total_tokens} tokens, ${metadata.cost_usd:.4f}")
```

**Output**:
```
✓ Análise concluída!
Latência total: 20000ms
Tokens totais: 1500
Custo total: $0.0187

analyst: 5.0s, 350 tokens, $0.0035
commercial: 4.8s, 320 tokens, $0.0032
financial: 5.2s, 340 tokens, $0.0035
market: 4.9s, 330 tokens, $0.0033
reviewer: 5.1s, 420 tokens, $0.0052
```

---

## 4. FLUXO COM FALHA PARCIAL

### 4.1 Cenário: Commercial Agent Falha

```
Camada 1: [analyst] ✓ OK
Camada 2: [commercial] ✗ FALHA, [market] ✓ OK
Camada 3: [financial] ? (depende de commercial)
Camada 4: [reviewer] ? (depende de financial)
```

### 4.2 Execução

```python
# Commercial falha com timeout
context.metadata["commercial"].status = ExecutionStatus.FAILED
context.metadata["commercial"].error = "Timeout after 30s"
context.results["commercial"] = ""

# Financial continua, mas recebe erro
financial_input = f"""
Análise: {analyst_output}
Estratégia: FALHA - Estratégia não disponível
...
"""

# Financial pode:
# Opção 1: Falhar também (propagar erro)
# Opção 2: Continuar com análise parcial

# Reviewer recebe estado parcial
reviewer_input = f"""
Análise: OK
Estratégia: FALHA
Financeiro: OK (parcial)
Mercado: OK
"""

# Reviewer consolida mesmo com falhas
reviewer_output = """
## Diagnóstico Executivo
Análise incompleta devido a falha na estratégia comercial.
Recomendação: Revisar e reexecutar estratégia comercial.

Baseado em análise disponível:
- Causa raiz: Aumento de churn
- Contexto: Mercado em consolidação
- Próximos passos: Análise de retenção
"""
```

### 4.3 Resultado

```python
result_context.metadata["commercial"].status = ExecutionStatus.FAILED
result_context.metadata["financial"].status = ExecutionStatus.COMPLETED
result_context.metadata["reviewer"].status = ExecutionStatus.COMPLETED

# Mas com aviso de falha parcial
success = all(
    meta.status == ExecutionStatus.COMPLETED
    for meta in result_context.metadata.values()
)
print(f"Sucesso: {success}")  # False
```

---

## 5. INTEGRAÇÃO COM STREAMLIT

### 5.1 Fluxo na UI

```python
# app.py
if st.button("🚀 Analisar Cenário"):
    problem_description = st.text_area(...)
    business_type = st.selectbox(...)
    
    with st.spinner("🤔 Analisando..."):
        # Cria contexto
        context = ExecutionContext(
            problem_description=problem_description,
            business_type=business_type
        )
        
        # Executa orquestrador
        orchestrator = create_orchestrator()
        result_context = await orchestrator.execute(context)
    
    # Exibe resultados
    st.success("✅ Análise concluída!")
    
    # Diagnóstico executivo
    st.markdown("## 👔 Diagnóstico Executivo")
    st.markdown(result_context.results["reviewer"])
    
    # Análises detalhadas
    with st.expander("🔍 Análise de Negócio"):
        st.markdown(result_context.results["analyst"])
    
    # Metadados
    st.metric("Latência", f"{result_context.get_total_latency_ms():.0f}ms")
    st.metric("Custo", f"${result_context.get_total_cost():.4f}")
```

---

## Conclusão

Este fluxo demonstra:
- ✅ Execução paralela eficiente (20s vs 25s sequencial)
- ✅ Contexto compartilhado entre agentes
- ✅ Tratamento de dependências
- ✅ Coleta de metadados
- ✅ Tratamento de falhas parciais
- ✅ Integração com UI

O sistema está pronto para produção e evolução futura.
