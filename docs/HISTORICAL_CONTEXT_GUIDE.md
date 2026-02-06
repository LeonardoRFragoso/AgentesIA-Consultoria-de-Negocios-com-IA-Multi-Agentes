# GUIA DE CONTEXTO HISTÓRICO E COMPARAÇÃO

## 1️⃣ CONCEITO DE COMPARAÇÃO HISTÓRICA

### O que Significa "Comparar Análises"?

Comparação histórica é o processo de relacionar uma análise atual com análises passadas para:
- ✅ Identificar se o cenário mudou
- ✅ Detectar padrões recorrentes
- ✅ Recuperar recomendações anteriores
- ✅ Entender evolução do problema
- ✅ Informar decisões futuras

**O que NÃO é**:
- ❌ Copiar respostas antigas
- ❌ Inflar prompts com histórico bruto
- ❌ Substituir análise atual
- ❌ Aprendizado automático

### Três Tipos de Comparação

#### 1. Comparação Temporal (Antes vs Agora)
**O que compara**: Mesmo problema em momentos diferentes

**Exemplo**:
- Problema: "Vendas caíram 20%"
- Análise anterior: 3 meses atrás
- Análise atual: Hoje
- Comparação: "Problema persiste? Piorou? Melhorou?"

**Valor**:
- ✅ Detectar tendências
- ✅ Avaliar efetividade de ações anteriores
- ✅ Identificar problemas crônicos

#### 2. Comparação por Similaridade
**O que compara**: Problemas similares (mesmo tipo de negócio, tema similar)

**Exemplo**:
- Problema atual: "Queda de vendas em SaaS"
- Histórico: Outras quedas de vendas em SaaS
- Comparação: "Como resolvemos antes? O que funcionou?"

**Valor**:
- ✅ Reutilizar estratégias comprovadas
- ✅ Evitar erros passados
- ✅ Acelerar análise

#### 3. Comparação por Tendência
**O que compara**: Padrões recorrentes ao longo do tempo

**Exemplo**:
- Histórico: Últimas 10 análises de SaaS
- Padrão: "Sempre recomendamos X em Y situação"
- Comparação: "Esse padrão se aplica agora?"

**Valor**:
- ✅ Identificar best practices internas
- ✅ Detectar anti-patterns
- ✅ Informar decisões com confiança

### Casos Onde NÃO Faz Sentido Comparar

❌ **Não comparar quando**:
- Sem histórico relevante (primeira análise do tipo)
- Problema completamente novo
- Business type diferente (B2B vs Varejo)
- Histórico muito antigo (>1 ano)
- Contexto mudou radicalmente (nova legislação, crise, etc.)

---

## 2️⃣ CRITÉRIOS DE SELEÇÃO DE HISTÓRICO

### Regras Determinísticas de Seleção

#### Critério 1: Relevância de Business Type
```python
# Prioridade:
# 1. Business type exato (+100 pontos)
# 2. "Outro" se nenhum exato (+0 pontos)
# 3. Nunca misturar tipos muito diferentes
```

#### Critério 2: Similaridade de Tema
```python
# Temas detectáveis:
# - vendas: venda, vendas, queda, crescimento, pipeline
# - custo: custo, despesa, margem, lucratividade
# - cliente: cliente, churn, retenção, satisfação
# - produto: produto, feature, lançamento
# - mercado: mercado, competição, posicionamento
# - operação: operação, processo, workflow

# Prioridade:
# 1. Mesmo tema (+50 pontos)
# 2. Tema "geral" se nenhum match (+0 pontos)
```

#### Critério 3: Status de Sucesso
```python
# Prioridade:
# 1. COMPLETED (+20 pontos)
# 2. PARTIAL_FAILURE (+10 pontos)
# 3. FAILED (excluir)
```

#### Critério 4: Janela de Tempo
```python
# Prioridade:
# 1. Últimos 7 dias (+30 pontos)
# 2. Últimos 30 dias (+15 pontos)
# 3. Últimos 90 dias (+5 pontos)
# 4. Mais antigo (excluir)
```

#### Critério 5: Top-N Relevantes
```python
# Retorna top-3 a top-5 execuções com maior score
# Score = business_type_match + theme_match + recency + status
```

---

## 3️⃣ MODELO DE HISTORICALCONTEXT

### Estrutura de Dados

```python
@dataclass
class HistoricalContext:
    # Execuções relevantes
    similar_executions: List[PastExecution]
    
    # Análise de mudanças
    key_differences: List[str]
    # Exemplo: ["Problema persiste após 3 meses", "Novo competidor entrou"]
    
    # Padrões detectados
    recurring_patterns: List[str]
    # Exemplo: ["Sempre recomendamos X em Y situação"]
    
    # Recomendações anteriores
    past_recommendations: List[str]
    # Exemplo: ["Implementar programa de retenção"]
    
    # Efetividade de ações
    action_outcomes: List[str]
    # Exemplo: ["Retenção aumentou 15% após implementar programa"]
    
    # Metadados
    confidence_score: float  # 0.0 a 1.0
    total_similar_executions: int
    
    def is_relevant(self) -> bool:
        """Histórico é relevante para usar?"""
        return len(self.similar_executions) > 0 and self.confidence_score >= 0.5
    
    def to_prompt_context(self) -> str:
        """Converte para texto para incluir em prompt (se relevante)"""
        # Retorna string vazia se não relevante
        # Caso contrário, retorna resumo formatado
```

---

## 4️⃣ INTEGRAÇÃO COM SISTEMA

### Fluxo de Execução

```
1. Usuário submete problema
   ↓
2. Orchestrator.execute(context) é chamado
   ↓
3. HistoryAnalyzer.analyze(context, past_executions) é chamado
   ↓
4. HistoricalContext é gerado e adicionado ao context
   ↓
5. Agentes executam (com acesso opcional ao histórico)
   ↓
6. Resultados são salvos no banco
```

### Ponto de Integração

```python
# Em orchestrator.py, após criar contexto:
if self.history_analyzer:
    past_executions = self.repository.list_executions(limit=100)
    context.historical_context = self.history_analyzer.analyze(
        context,
        past_executions
    )
```

### Acesso pelos Agentes

```python
# Em BaseAgent._build_user_message():
user_message = f"Problema: {context.problem_description}"

# Adicionar contexto histórico se relevante
if context.historical_context and context.historical_context.is_relevant():
    user_message += "\n\n" + context.historical_context.to_prompt_context()
```

---

## 5️⃣ CÁLCULO DE CONFIANÇA

### Fatores de Confiança

```python
confidence = 0.0

# Execuções encontradas: +0.3
confidence += min(0.3, len(similar_executions) * 0.1)

# Business type exato: +0.3
if similar_executions[0].business_type == current.business_type:
    confidence += 0.3

# Tema similar: +0.2
if detect_theme(similar_executions[0]) == detect_theme(current):
    confidence += 0.2

# Recência: +0.2
if days_since_execution <= 7:
    confidence += 0.2
elif days_since_execution <= 30:
    confidence += 0.1

# Máximo: 1.0
confidence = min(1.0, confidence)
```

### Interpretação

- **0.0 - 0.4**: Não relevante (não incluir no prompt)
- **0.4 - 0.7**: Moderadamente relevante (incluir com cautela)
- **0.7 - 1.0**: Altamente relevante (incluir com confiança)

---

## 6️⃣ EXEMPLOS PRÁTICOS

### Exemplo 1: Queda de Vendas Recorrente

**Situação**:
- Problema atual: "Vendas caíram 20% este mês"
- Histórico: Análise similar 3 meses atrás
- Business type: SaaS (exato)
- Tema: vendas (exato)

**Seleção**:
- ✅ Execução anterior encontrada
- ✅ Business type exato: +100
- ✅ Tema exato: +50
- ✅ Recência 90 dias: +5
- ✅ Status COMPLETED: +20
- **Total Score: 175**

**Histórico Gerado**:
```
## Contexto Histórico Relevante
Encontramos 1 análise similar:

### Análise 1 (2025-11-05)
Problema: Vendas caíram 15% no mês anterior...
Status: COMPLETED
Duração: 18234ms | Tokens: 1450

## Mudanças Detectadas
- Problema similar persiste há 90 dias (última análise em 2025-11-05)
- Análise anterior foi bem-sucedida (18234ms, 1450 tokens)

## Padrões Recorrentes
- Múltiplas análises similares recomendaram ações similares

## Resultados de Ações Anteriores
- Implementar programa de retenção aumentou retenção em 15%

**Confiança do contexto histórico: 85%**
```

**Impacto no Agente**:
- Revisor vê que problema persiste
- Pode avaliar se ações anteriores foram implementadas
- Pode ajustar recomendações baseado em resultados anteriores

### Exemplo 2: Novo Tipo de Problema

**Situação**:
- Problema atual: "Expandir para novo mercado europeu"
- Histórico: Nenhuma análise de expansão
- Business type: SaaS
- Tema: mercado (novo)

**Seleção**:
- ❌ Nenhuma execução com tema "expansão"
- ❌ Histórico vazio

**Histórico Gerado**:
```
# (vazio)
```

**Impacto no Agente**:
- Nenhum histórico incluído
- Análise procede normalmente
- Resultado será salvo para futuras análises similares

### Exemplo 3: Problema com Histórico Antigo

**Situação**:
- Problema atual: "Queda de vendas"
- Histórico: Análise similar 18 meses atrás
- Business type: SaaS
- Tema: vendas

**Seleção**:
- ❌ Histórico > 90 dias (excluído)
- ❌ Contexto pode ter mudado radicalmente

**Histórico Gerado**:
```
# (vazio - histórico muito antigo)
```

**Impacto no Agente**:
- Nenhum histórico incluído
- Análise procede normalmente
- Evita contexto obsoleto

---

## 7️⃣ DECISÕES TÉCNICAS

### Decisões Tomadas

| Decisão | Justificativa | Trade-off |
|---------|---------------|-----------|
| **Seleção determinística** | Reproduzível, sem ML | Menos sofisticado que embeddings |
| **Top-3 execuções** | Evita prompt stuffing | Pode perder contexto relevante |
| **Confiança >= 0.5** | Threshold conservador | Pode excluir contexto útil |
| **Resumos de 500 chars** | Controla tamanho | Pode perder detalhes |
| **Sem acesso direto ao BD** | Desacoplamento | Requer passar dados ao analisador |
| **Contexto opcional** | Zero impacto se vazio | Mais complexo que sempre incluir |

### Trade-offs Aceitos

1. **Simplicidade vs Sofisticação**
   - ✅ Palavras-chave em vez de embeddings
   - ✅ Scoring simples em vez de ML
   - ✅ Fácil de entender e debugar

2. **Controle vs Automação**
   - ✅ Agentes decidem se usam histórico
   - ✅ Sem modificação automática de prompts
   - ✅ Máximo controle sobre o que entra

3. **Completude vs Brevidade**
   - ✅ Resumos em vez de textos completos
   - ✅ Top-3 em vez de todos os resultados
   - ✅ Evita prompt stuffing

### O Que Ficou Fora Propositalmente

❌ **Não implementado neste passo**:
- Embeddings para similaridade semântica (Fase 3)
- Aprendizado automático de padrões (Fase 4)
- Resumo automático de análises (Fase 3)
- Detecção de anomalias (Fase 4)
- Recomendações baseadas em ML (Fase 4)

---

## 8️⃣ LIMITAÇÕES CONHECIDAS

1. **Detecção de Tema por Palavras-Chave**
   - ✅ Funciona bem para temas óbvios
   - ❌ Falha em temas implícitos
   - 🔄 Será melhorado com embeddings em Fase 3

2. **Confiança Baseada em Heurísticas**
   - ✅ Simples e reproduzível
   - ❌ Pode não refletir relevância real
   - 🔄 Será melhorado com feedback em Fase 4

3. **Sem Contexto de Mudança Radical**
   - ✅ Evita contexto obsoleto
   - ❌ Pode perder insights valiosos
   - 🔄 Será melhorado com detecção de eventos em Fase 3

---

## 9️⃣ PRÓXIMOS PASSOS (FASE 3)

### Melhorias Planejadas
- [ ] Embeddings para similaridade semântica
- [ ] Resumo automático de análises
- [ ] Detecção de mudanças de contexto
- [ ] Recomendações baseadas em padrões
- [ ] Dashboard de histórico

### Evolução Natural
```
Fase 2: Seleção determinística (atual)
   ↓
Fase 3: Seleção com embeddings
   ↓
Fase 4: Aprendizado automático
   ↓
Fase 5: Recomendações preditivas
```

---

## Conclusão

O sistema de contexto histórico:
- ✅ É **consultivo**, não obrigatório
- ✅ Usa critérios **determinísticos** e reproduzíveis
- ✅ Evita **prompt stuffing** com seleção inteligente
- ✅ Está pronto para **evolução** com ML
- ✅ Não quebra **fluxo atual** do sistema

Próximo passo: Implementar integração com Orchestrator e testes.
