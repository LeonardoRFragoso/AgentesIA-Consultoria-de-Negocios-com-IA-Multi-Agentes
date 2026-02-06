# GUIA DE CONFLITO E CONSENSO ENTRE AGENTES

## 1️⃣ CONCEITO DE CONFLITO

### O que é um Conflito?

**Conflito** é uma **divergência estrutural** entre recomendações de dois ou mais agentes sobre a mesma questão, onde as posições são **mutuamente exclusivas ou significativamente contraditórias**.

### Tipos de Conflito

#### 1. Conflito Estratégico
**Natureza**: Direções fundamentalmente opostas
**Exemplo**: "Expandir agressivamente" vs "Consolidar operações"
**Severidade**: ALTA
**Requer debate**: SIM

#### 2. Conflito Tático
**Natureza**: Prioridades diferentes para mesma direção
**Exemplo**: "Priorizar retenção" vs "Priorizar aquisição"
**Severidade**: MÉDIA
**Requer debate**: SIM

#### 3. Conflito Financeiro
**Natureza**: Custo vs retorno esperado
**Exemplo**: "Investir $500K" vs "Retorno é apenas $300K"
**Severidade**: ALTA
**Requer debate**: SIM

#### 4. Conflito de Risco
**Natureza**: Postura conservadora vs agressiva
**Exemplo**: "Mercado incerto, cautela" vs "Oportunidade clara, ação rápida"
**Severidade**: MÉDIA
**Requer debate**: SIM

#### 5. Conflito de Prioridade
**Natureza**: Sequenciamento diferente
**Exemplo**: "Fazer A depois B" vs "Fazer B depois A"
**Severidade**: BAIXA
**Requer debate**: NÃO

### O que NÃO é Conflito

❌ **Complementação**: Um agente detalha o outro
❌ **Diferentes perspectivas**: Sobre o mesmo ponto
❌ **Variação de ênfase**: Mesma direção, ênfase diferente
❌ **Sequenciamento**: Mesma direção, ordem diferente

---

## 2️⃣ MODELO DE DADOS

### Estrutura Conflict

```python
@dataclass
class Conflict:
    conflict_id: str                    # UUID único
    conflict_type: ConflictType         # STRATEGIC, TACTICAL, FINANCIAL, RISK, PRIORITY
    severity: ConflictSeverity          # LOW, MEDIUM, HIGH, CRITICAL
    topic: str                          # Tema do conflito
    agents_involved: List[str]          # Nomes dos agentes
    positions: Dict[str, AgentPosition] # Posições por agente
    description: str                    # Descrição legível
    key_differences: List[str]          # Diferenças principais
    mutual_exclusivity: bool            # Posições mutuamente exclusivas?
    requires_debate: bool               # Deve entrar em debate?
```

### Estrutura ConflictReport

```python
@dataclass
class ConflictReport:
    execution_id: str
    total_conflicts: int
    conflicts: List[Conflict]
    has_low_severity: bool
    has_medium_severity: bool
    has_high_severity: bool
    has_critical_severity: bool
    requires_debate: bool
    debate_topics: List[str]
```

### Estrutura ConsensusResult

```python
@dataclass
class ConsensusResult:
    execution_id: str
    conflict_id: str
    final_decision: str              # Decisão final
    supporting_agents: List[str]     # Agentes que apoiam
    opposing_agents: List[str]       # Agentes que se opõem
    neutral_agents: List[str]        # Agentes neutros
    justification: str               # Por que essa decisão
    reasoning_summary: str           # Resumo do raciocínio
    trade_offs_acknowledged: List[str]  # Trade-offs reconhecidos
    debate_rounds: List[DebateRound] # Histórico de debate
    total_rounds: int                # Número de rounds
    unresolved_aspects: List[str]    # Aspectos não resolvidos
    confidence_score: float          # Confiança (0.0 a 1.0)
    resolver_agent: str              # Qual agente resolveu
```

---

## 3️⃣ DETECÇÃO DE CONFLITOS

### Algoritmo Determinístico

```
1. Extrai outputs de todos os agentes
2. Para cada par de agentes:
   a. Procura por palavras-chave opostas
   b. Se encontra, classifica tipo de conflito
   c. Avalia severidade
   d. Cria objeto Conflict
3. Retorna ConflictReport com todos os conflitos
```

### Palavras-Chave Opostas

```python
OPPOSING_KEYWORDS = {
    "investir": ["cortar", "reduzir", "diminuir", "economizar"],
    "expandir": ["consolidar", "manter", "estabilizar", "preservar"],
    "agressivo": ["conservador", "cauteloso", "prudente", "seguro"],
    "rápido": ["lento", "gradual", "incremental", "faseado"],
    "crescimento": ["lucro", "margem", "eficiência", "custo"],
    "inovação": ["estabilidade", "risco", "segurança", "conformidade"],
}
```

### Classificação de Tipo

- **Financial + Commercial** com "investir/custo" → FINANCIAL
- **Analyst + Market** com "agressivo/conservador" → RISK
- Qualquer com "expandir/crescimento" → STRATEGIC
- Padrão → TACTICAL

### Avaliação de Severidade

- **FINANCIAL**: Sempre HIGH
- **STRATEGIC**: Sempre HIGH
- **RISK**: Sempre MEDIUM
- **TACTICAL**: Sempre LOW
- **PRIORITY**: Sempre LOW

---

## 4️⃣ PROCESSO DE DEBATE

### Fluxo

```
1. Conflito detectado
   ↓
2. Severidade avaliada
   ↓
3. Se requer debate (MEDIUM+):
   ├─ Round 1: Coleta argumentos iniciais
   ├─ Round 2: Coleta argumentos refinados (se necessário)
   ├─ Round 3: Argumentos finais (se necessário)
   └─ Máximo 3 rounds
   ↓
4. Avalia convergência após cada round
   ├─ Se convergência >= 70%: Encerra debate
   └─ Se round == 3: Encerra debate
   ↓
5. Produz decisão final
   ├─ Seleciona decision maker (Reviewer > Financial > Commercial > ...)
   ├─ Calcula confiança
   ├─ Identifica trade-offs
   └─ Retorna ConsensusResult
```

### Convergência

**Métrica**: Jaccard similarity entre argumentos
- 0.0 = Divergência total
- 1.0 = Convergência total
- >= 0.7 = Encerra debate

### Confiança na Decisão

```
confidence = 0.0

# Confiança do decision maker: +0.4
confidence += decision_maker_confidence * 0.4

# Apoio de outros agentes: +0.3
confidence += (support_ratio) * 0.3

# Severidade: -0.2 se CRITICAL
if severity == CRITICAL:
    confidence -= 0.2

# Evidência: +0.1
confidence += min(0.1, evidence_count * 0.02)

# Clamp entre 0.0 e 1.0
confidence = max(0.0, min(1.0, confidence))
```

---

## 5️⃣ PAPEL DO AGENTE REVISOR

### Responsabilidades

1. **Recebe relatório de conflitos**
   - Lista de conflitos detectados
   - Severidades
   - Posições dos agentes

2. **Avalia argumentos**
   - Lê posições de cada agente
   - Avalia força dos argumentos
   - Considera evidências

3. **Usa contexto histórico**
   - Se disponível, consulta análises passadas
   - Identifica padrões
   - Aprende com histórico

4. **Produz decisão final**
   - Escolhe posição
   - Justifica escolha
   - Reconhece trade-offs

5. **Justifica escolhas**
   - Explica por que essa decisão
   - Reconhece pontos válidos da oposição
   - Documenta trade-offs

### O Revisor NÃO

❌ "Ganha sempre"
❌ Ignora argumentos válidos
❌ Força consenso artificial
❌ Toma decisão sem justificativa

---

## 6️⃣ INTEGRAÇÃO COM ORCHESTRATOR

### Ponto de Integração

```python
# Em orchestrator.py, após todos os agentes executarem:

# 1. Detecta conflitos
conflict_detector = ConflictDetector()
conflict_report = conflict_detector.detect(context)

# 2. Se há conflitos que requerem debate
if conflict_report.requires_debate:
    # 3. Executa debate
    consensus_builder = ConsensusBuilder()
    consensus_results = consensus_builder.build_consensus(
        conflict_report.conflicts,
        context.results,
        context
    )
    
    # 4. Adiciona resultados ao contexto
    context.conflict_report = conflict_report
    context.consensus_results = consensus_results
    
    # 5. Log
    logger.info("Conflicts resolved", consensus_count=len(consensus_results))
```

### O que Acontece se Não Há Conflitos

```
1. ConflictDetector retorna ConflictReport vazio
2. requires_debate = False
3. Sistema pula debate
4. Execução continua normalmente
5. Zero overhead
```

### Compatibilidade Total

- ✅ Sem mudança em contratos públicos
- ✅ Campo `conflict_report` é opcional
- ✅ Campo `consensus_results` é opcional
- ✅ Sistema funciona sem debate

---

## 7️⃣ CONTROLE DE RISCO

### Limites de Segurança

```python
# Máximo de conflitos por execução
MAX_CONFLICTS_PER_EXECUTION = 10

# Máximo de rounds de debate
MAX_DEBATE_ROUNDS = 3

# Severidade mínima para debate
MIN_SEVERITY_FOR_DEBATE = ConflictSeverity.MEDIUM

# Confiança mínima para aceitar decisão
MIN_CONFIDENCE_FOR_DECISION = 0.4

# Timeout por debate
DEBATE_TIMEOUT_SECONDS = 30
```

### Proteções

1. **Conflitos Artificiais**
   - Apenas palavras-chave opostas detectam
   - Sem ML, sem falsos positivos
   - Threshold conservador

2. **Debate Infinito**
   - Máximo 3 rounds
   - Convergência >= 70% encerra
   - Timeout de segurança

3. **Viés de Agente Dominante**
   - Decision maker selecionado por prioridade (não por força)
   - Reviewer tem prioridade (mediador)
   - Argumentos de todos considerados

4. **Overhead Excessivo**
   - Detecção é rápida (palavras-chave)
   - Debate é limitado (3 rounds max)
   - Sem chamadas ao LLM

---

## 8️⃣ EXEMPLOS PRÁTICOS

### Exemplo 1: Conflito Financeiro

**Cenário**: Queda de vendas, como responder?

**Outputs**:
```
Commercial:
"Recomendo aumentar investimento em marketing em $500K
para recuperar leads e crescimento de vendas."

Financial:
"Análise de viabilidade: investimento de $500K
resultaria em retorno esperado de apenas $300K.
Recomendo cortar custos imediatamente para manter margem."
```

**Detecção**:
```
Palavras-chave opostas encontradas:
- "investir" vs "cortar"
- "crescimento" vs "margem"

Tipo: FINANCIAL
Severidade: HIGH
Requer debate: SIM
```

**Debate**:
```
Round 1:
- Commercial: "Investimento é necessário para recuperar mercado"
- Financial: "Retorno não justifica investimento"

Convergência: 0.3 (baixa)

Round 2:
- Commercial: "Sem investimento, perderemos market share"
- Financial: "Sem lucro, não temos capital para investir"

Convergência: 0.4 (ainda baixa)

Round 3:
- Commercial: "Investimento pequeno em marketing digital, $100K"
- Financial: "Retorno esperado seria $150K, viável"

Convergência: 0.7 (encerra)
```

**Decisão Final**:
```
Decision Maker: Financial (prioridade)

Final Decision:
"Implementar investimento moderado em marketing digital ($100K)
com retorno esperado de $150K. Monitorar performance
e ajustar se necessário."

Supporting Agents: [financial, commercial]
Opposing Agents: []

Confidence: 0.82

Trade-offs Acknowledged:
- Rejeitado investimento de $500K (muito agressivo)
- Aceito investimento de $100K (balanceado)
- Reconhecido risco de market share
- Reconhecida necessidade de lucratividade
```

### Exemplo 2: Sem Conflito

**Cenário**: Como melhorar retenção de clientes?

**Outputs**:
```
Commercial:
"Implementar programa de fidelidade com rewards
para aumentar retenção de clientes."

Market:
"Programa de fidelidade é tendência no mercado.
Recomendo implementar para competir com concorrentes."
```

**Detecção**:
```
Palavras-chave opostas: NENHUMA

Conflito detectado: NÃO

Sistema pula debate
Execução continua normalmente
```

### Exemplo 3: Conflito de Risco

**Cenário**: Expandir para novo mercado?

**Outputs**:
```
Analyst:
"Mercado europeu é incerto. Recomendo cautela
e estudo aprofundado antes de expandir."

Market:
"Oportunidade clara no mercado europeu.
Recomendo ação rápida para ganhar market share."
```

**Detecção**:
```
Palavras-chave opostas encontradas:
- "cautela" vs "ação rápida"
- "incerto" vs "claro"

Tipo: RISK
Severidade: MEDIUM
Requer debate: SIM
```

**Decisão Final**:
```
Decision Maker: Reviewer (mediador)

Final Decision:
"Implementar expansão faseada para Europa:
Fase 1 (3 meses): Estudo de mercado aprofundado
Fase 2 (6 meses): Piloto em mercado selecionado
Fase 3 (12 meses): Expansão completa se piloto bem-sucedido"

Supporting Agents: [analyst, market, reviewer]
Opposing Agents: []

Confidence: 0.78

Trade-offs Acknowledged:
- Balanceado cautela (Analyst) com oportunidade (Market)
- Faseamento reduz risco
- Permite aprendizado antes de expansão completa
```

---

## 9️⃣ DECISÕES TÉCNICAS

### Tomadas

| Decisão | Justificativa | Trade-off |
|---------|---------------|-----------|
| **Detecção por palavras-chave** | Determinístico, sem ML | Menos sofisticado que embeddings |
| **Máximo 3 rounds** | Evita debate infinito | Pode não convergir |
| **Decision maker por prioridade** | Reproduzível, sem viés | Pode não ser ideal em todos casos |
| **Confiança heurística** | Simples, explicável | Pode não refletir realidade |
| **Sem chamadas ao LLM** | Rápido, sem overhead | Menos inteligente que debate real |

### Trade-offs Aceitos

1. **Simplicidade vs Sofisticação**
   - ✅ Palavras-chave em vez de embeddings
   - ✅ Heurísticas em vez de ML
   - ✅ Fácil de entender e debugar

2. **Velocidade vs Inteligência**
   - ✅ Sem chamadas ao LLM
   - ✅ Processamento local
   - ✅ Overhead mínimo

3. **Completude vs Brevidade**
   - ✅ Máximo 3 rounds
   - ✅ Encerra se convergir
   - ✅ Evita debate infinito

### Fora Propositalmente

❌ **Não implementado neste passo**:
- Embeddings para similaridade semântica (Fase 4)
- Aprendizado automático de padrões (Fase 5)
- Votação ponderada (Fase 4)
- Debate com chamadas ao LLM (Fase 5)
- Histórico de conflitos (Fase 4)

---

## 🔟 LIMITAÇÕES CONHECIDAS

1. **Detecção por Palavras-Chave**
   - ✅ Funciona bem para conflitos óbvios
   - ❌ Falha em conflitos implícitos
   - 🔄 Será melhorado com embeddings em Fase 4

2. **Decision Maker por Prioridade**
   - ✅ Reproduzível
   - ❌ Pode não ser ideal
   - 🔄 Será melhorado com votação em Fase 4

3. **Sem Contexto de Histórico**
   - ✅ Simples
   - ❌ Perde aprendizado
   - 🔄 Será integrado em Fase 4

---

## Conclusão

O sistema de conflito e consenso:
- ✅ Detecta conflitos **deterministicamente**
- ✅ Promove debate **estruturado**
- ✅ Produz decisão **justificada**
- ✅ Reconhece **trade-offs**
- ✅ Não quebra **fluxo atual**

**Próximo passo**: Integração com Orchestrator e testes
