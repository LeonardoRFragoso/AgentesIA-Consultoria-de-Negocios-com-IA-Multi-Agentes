
## 1️⃣ CONCEITO DE REUNIÃO EXECUTIVA

### O que é?

**Reunião executiva** é uma **simulação estruturada de uma reunião de diretoria** onde agentes com papéis definidos discutem análises, conflitos detectados e produzem uma decisão final justificada, registrada em ata.

### Diferenças Chave

#### Análise Individual
- Agente executa sozinho
- Produz output estruturado
- Sem interação
- Resultado: análise

#### Debate de Conflito
- Dois agentes em desacordo
- Múltiplos rounds
- Busca convergência
- Resultado: decisão sobre conflito específico

#### Reunião Executiva
- Múltiplos agentes com papéis
- Agenda estruturada
- Turnos de fala organizados
- Usa conflitos como pauta
- Resultado: ata executiva com decisões

### Quando Acioná-la

✅ **Acioná-la quando**:
- Há conflitos HIGH ou CRITICAL
- Múltiplos agentes têm perspectivas relevantes
- Decisão afeta toda a organização
- Necessário rastreabilidade formal

❌ **NÃO acioná-la quando**:
- Sem conflitos relevantes
- Problema é simples/óbvio
- Apenas um agente tem expertise
- Overhead não se justifica

---

## 2️⃣ PAPÉIS NA REUNIÃO

### Mapeamento de Papéis

| Agente | Papel | Sigla | Responsabilidade |
|--------|-------|-------|------------------|
| **Reviewer** | Chair (CEO) | CHAIR | Conduz reunião, toma decisão final |
| **Financial** | CFO | CFO | Visão financeira, viabilidade |
| **Commercial** | CRO | CRO | Visão comercial, vendas, cliente |
| **Market** | CMO | CMO | Visão de mercado, competição |
| **Analyst** | Analista | ANALYST | Visão analítica, contexto |

### Ordem de Fala

1. **Chair (Reviewer)**: Abre reunião, contextualiza
2. **CFO (Financial)**: Apresenta visão financeira
3. **CRO (Commercial)**: Apresenta visão comercial
4. **CMO (Market)**: Apresenta visão de mercado
5. **Analyst**: Apresenta contexto analítico

### Responsabilidades

**Chair**:
- ✅ Conduz reunião
- ✅ Contextualiza problema
- ✅ Toma decisão final
- ✅ Encerra reunião
- ❌ Não "ganha sempre"

**CFO**:
- ✅ Avalia viabilidade financeira
- ✅ Questiona ROI
- ✅ Identifica riscos financeiros
- ❌ Não bloqueia inovação

**CRO**:
- ✅ Apresenta oportunidades comerciais
- ✅ Avalia impacto em clientes
- ✅ Propõe estratégias
- ❌ Não ignora restrições financeiras

**CMO**:
- ✅ Contextualiza mercado
- ✅ Identifica tendências
- ✅ Avalia competição
- ❌ Não toma decisões sozinho

**Analyst**:
- ✅ Fornece contexto
- ✅ Questiona suposições
- ✅ Identifica riscos
- ❌ Não propõe decisões

---

## 3️⃣ AGENDA DA REUNIÃO

### Estrutura Padrão

```
1. ABERTURA (2 min)
   - Chair contextualiza problema
   - Define objetivos da reunião
   - Apresenta agenda

2. APRESENTAÇÕES (5 min)
   - Analyst: Contexto e diagnóstico
   - CFO: Visão financeira
   - CRO: Visão comercial
   - CMO: Contexto de mercado

3. DISCUSSÃO DE CONFLITOS (5 min)
   - Identifica conflitos detectados
   - Agentes envolvidos defendem posições
   - Busca convergência

4. PROPOSTAS DE DECISÃO (3 min)
   - Chair apresenta opções
   - Agentes comentam
   - Avaliam trade-offs

5. DELIBERAÇÃO (2 min)
   - Chair toma decisão final
   - Justifica escolha
   - Reconhece trade-offs

6. ENCERRAMENTO (1 min)
   - Resumo de decisões
   - Ações imediatas
   - Próximos passos
```

### Objetivo de Cada Fase

| Fase | Objetivo |
|------|----------|
| **OPENING** | Contextualizar e alinhar |
| **PRESENTATIONS** | Apresentar perspectivas |
| **DISCUSSION** | Debater conflitos |
| **PROPOSALS** | Propor soluções |
| **DELIBERATION** | Tomar decisão |
| **CLOSING** | Registrar e encerrar |

---

## 4️⃣ MODELO DE DADOS

### MeetingMinutes (Ata Executiva)

```python
@dataclass
class MeetingMinutes:
    execution_id: str           # ID da execução
    meeting_id: str             # ID da reunião
    
    # Contexto
    problem_description: str
    business_type: str
    
    # Participantes
    participants: List[ExecutiveParticipant]
    chair: str                  # Quem conduziu
    
    # Agenda e execução
    agenda: List[MeetingAgendaItem]
    statements: List[MeetingStatement]
    total_rounds: int
    
    # Decisões
    decisions: List[MeetingDecision]
    final_decision: str
    final_rationale: str
    
    # Ações
    action_items: List[str]
    unresolved_topics: List[str]
    
    # Metadados
    started_at: datetime
    ended_at: datetime
    duration_seconds: int
    confidence_score: float
```

### MeetingDecision (Decisão)

```python
@dataclass
class MeetingDecision:
    topic: str                  # Tema da decisão
    decision: str               # O que foi decidido
    rationale: str              # Por que
    supporting_agents: List[str]  # Quem apoiou
    opposing_agents: List[str]  # Quem se opôs
    confidence_score: float     # Confiança (0-1)
    action_items: List[str]     # Ações decorrentes
    owner: str                  # Responsável
```

### MeetingStatement (Fala)

```python
@dataclass
class MeetingStatement:
    speaker: str                # Quem falou
    role: ExecutiveRole         # Papel
    round_number: int           # Qual rodada
    phase: MeetingPhase         # Qual fase
    statement: str              # O que foi dito
    supporting_evidence: List[str]  # Evidências
    timestamp: datetime
```

---

## 5️⃣ FLUXO DE EXECUÇÃO

```
1. ConflictDetector.detect(context)
   ↓
2. MeetingOrchestrator.run_if_needed()
   ├─ should_hold_meeting()?
   │  ├─ Há conflitos HIGH+?
   │  └─ Múltiplos agentes?
   │
   ├─ SIM: MeetingEngine.run()
   │  ├─ Cria participantes
   │  ├─ Cria agenda
   │  ├─ Executa fases:
   │  │  ├─ OPENING
   │  │  ├─ PRESENTATIONS
   │  │  ├─ DISCUSSION
   │  │  ├─ PROPOSALS
   │  │  ├─ DELIBERATION
   │  │  └─ CLOSING
   │  ├─ Produz decisões
   │  └─ Retorna MeetingMinutes
   │
   └─ NÃO: Retorna None
   
3. context.meeting_minutes = MeetingMinutes
4. Execução continua
```

---

## 6️⃣ ORQUESTRAÇÃO DE TURNOS

### Ordem de Fala

```
Fase: PRESENTATIONS
├─ Round 1:
│  ├─ Chair: Contextualiza
│  ├─ Analyst: Diagnóstico
│  ├─ CFO: Viabilidade
│  ├─ CRO: Oportunidade
│  └─ CMO: Mercado

Fase: DISCUSSION
├─ Round 1:
│  ├─ Agente 1: Defende posição
│  └─ Agente 2: Contra-argumenta
├─ Round 2:
│  ├─ Agente 1: Refina argumento
│  └─ Agente 2: Refina contra-argumento
└─ Round 3:
   ├─ Agente 1: Argumento final
   └─ Agente 2: Argumento final

Fase: DELIBERATION
└─ Chair: Toma decisão
```

### Limite de Rodadas

- **Máximo 3 rounds** por fase
- **Máximo 5 participantes** por reunião
- **Máximo 3 conflitos** na agenda

### Evitar Repetição

```python
# Cada agente tem speaking_count
# Se já falou nesta rodada, passa a vez
# Se todos já falaram, encerra rodada
```

---

## 7️⃣ ATA EXECUTIVA

### Estrutura

```markdown
# ATA EXECUTIVA

**Data**: 2024-02-05 20:30:00
**Duração**: 18 minutos
**Presidente**: Reviewer

## CONTEXTO
**Problema**: Vendas caíram 20% nos últimos 3 meses
**Tipo de Negócio**: SaaS

## PARTICIPANTES
- **reviewer** (Chair)
- **financial** (CFO)
- **commercial** (CRO)
- **market** (CMO)
- **analyst** (Analyst)

## DECISÕES

### Conflito: Investir vs Cortar Custos
**Decisão**: Implementar investimento moderado em marketing digital ($100K)
**Rationale**: Balanceado entre oportunidade comercial e viabilidade financeira
**Confiança**: 82%
**Ações**:
- Implementar campanha de marketing digital
- Monitorar ROI mensalmente
- Revisar em 30 dias

## AÇÕES IMEDIATAS
- Preparar plano de marketing digital ($100K)
- Designar responsável: Commercial
- Prazo: 5 dias úteis

## TÓPICOS NÃO RESOLVIDOS
- Expansão para novo mercado (adiado para próxima reunião)
```

### Linguagem Executiva

- ✅ Claro e conciso
- ✅ Sem jargão técnico
- ✅ Decisões explícitas
- ✅ Ações com responsáveis
- ❌ Sem chat/conversa
- ❌ Sem detalhes desnecessários

### Exportação

```python
# Markdown
minutes.to_markdown()

# JSON (futuro)
minutes.to_json()

# PDF (futuro)
minutes.to_pdf()
```

---

## 8️⃣ INTEGRAÇÃO COM FLUXO EXISTENTE

### Ponto de Integração

```python
# Em orchestrator.py, após debate de conflitos:

# 1. Detecta conflitos
conflict_detector = ConflictDetector()
conflict_report = conflict_detector.detect(context)

# 2. Se há conflitos, executa debate
if conflict_report.requires_debate:
    consensus_results = ConsensusBuilder().build_consensus(...)
    context.consensus_results = consensus_results

# 3. Se há conflitos HIGH+, executa reunião
meeting_orchestrator = MeetingOrchestrator()
meeting_minutes = meeting_orchestrator.run_if_needed(
    context,
    conflict_report,
    context.results
)

if meeting_minutes:
    context.meeting_minutes = meeting_minutes
    logger.info("Meeting held", decisions=len(meeting_minutes.decisions))
```

### O que Acontece se Não Há Conflitos

```
1. ConflictDetector retorna vazio
2. MeetingOrchestrator.run_if_needed() retorna None
3. context.meeting_minutes = None
4. Execução continua normalmente
5. Zero overhead
```

### Compatibilidade Total

- ✅ Sem mudança em contratos públicos
- ✅ Campo `meeting_minutes` é opcional
- ✅ Sistema funciona sem reunião
- ✅ Integração limpa

---

## 9️⃣ CONTROLE DE RISCO

### Limites de Segurança

```python
# Reunião só se:
MIN_SEVERITY_FOR_MEETING = ConflictSeverity.HIGH

# Máximo de rounds
MAX_ROUNDS = 3

# Máximo de participantes
MAX_PARTICIPANTS = 5

# Máximo de conflitos na agenda
MAX_CONFLICTS_IN_AGENDA = 3
```

### Proteções

1. **Reuniões Desnecessárias**
   - Só se conflitos HIGH+
   - Múltiplos agentes envolvidos
   - Decisão afeta organização

2. **Overhead Excessivo**
   - Máximo 3 conflitos na agenda
   - Máximo 3 rounds por fase
   - Máximo 5 participantes

3. **Decisões Pouco Claras**
   - Sempre com justificativa
   - Sempre com ações
   - Sempre com responsável

4. **Ata Verbosa**
   - Resumida e executiva
   - Sem chat/conversa
   - Máximo 1 página

---

## 🔟 EXEMPLOS PRÁTICOS

### Exemplo 1: Reunião com Conflito Financeiro

**Cenário**:
```
Problema: Vendas caíram 20%, como responder?
Conflito: Commercial quer investir $500K
         Financial quer cortar custos
Severidade: HIGH
```

**Agenda Criada**:
```
1. OPENING (2 min)
2. PRESENTATIONS (5 min)
3. DISCUSSION: Investir vs Cortar (5 min)
4. PROPOSALS (3 min)
5. DELIBERATION (2 min)
6. CLOSING (1 min)
```

**Turnos de Fala**:
```
OPENING:
- Chair: "Vendas caíram 20%. Precisamos decidir como responder."

PRESENTATIONS:
- Analyst: "Problema é falta de leads. Mercado está competitivo."
- CFO: "Investimento de $500K resultaria em $300K de retorno. Não viável."
- CRO: "Sem investimento, perderemos market share. Oportunidade clara."
- CMO: "Mercado está em crescimento. Timing é crítico."

DISCUSSION:
Round 1:
- CRO: "Investimento é necessário para recuperar leads"
- CFO: "Retorno não justifica investimento"

Round 2:
- CRO: "Sem investimento, perderemos clientes"
- CFO: "Sem lucro, não temos capital para investir"

Round 3:
- CRO: "Investimento moderado $100K em marketing digital"
- CFO: "Retorno esperado seria $150K. Viável."

PROPOSALS:
- Chair: "Proposta: Investimento de $100K em marketing digital"

DELIBERATION:
- Chair: "Decisão: Implementar investimento de $100K com monitoramento mensal"

CLOSING:
- Chair: "Ações: Preparar plano em 5 dias. Revisar em 30 dias."
```

**Ata Final**:
```
# ATA EXECUTIVA

**Decisão**: Investimento de $100K em marketing digital
**Rationale**: Balanceado entre oportunidade e viabilidade
**Confiança**: 82%
**Ações**:
- Preparar plano de marketing digital
- Monitorar ROI mensalmente
- Revisar em 30 dias
```

### Exemplo 2: Sem Reunião

**Cenário**:
```
Problema: Como melhorar retenção de clientes?
Conflitos: NENHUM
Análises: Todas alinham em programa de fidelidade
```

**Resultado**:
```
1. ConflictDetector retorna vazio
2. MeetingOrchestrator.run_if_needed() retorna None
3. Sistema pula reunião
4. Execução continua normalmente
5. Sem overhead
```

---

## 1️⃣1️⃣ DECISÕES TÉCNICAS

### Tomadas

| Decisão | Justificativa | Trade-off |
|---------|---------------|-----------|
| **Reunião só se HIGH+** | Evita overhead | Pode perder contexto |
| **Máximo 3 rounds** | Evita infinito | Pode não convergir |
| **Máximo 5 participantes** | Mantém foco | Pode excluir perspectivas |
| **Ata sem chat** | Executiva e clara | Perde detalhes |
| **Chair decide** | Reproduzível | Pode não ser ideal |

### Fora Propositalmente

- ❌ Votação formal (Fase 5)
- ❌ Aprendizado automático (Fase 6)
- ❌ Simulação de debate com LLM (Fase 6)
- ❌ Histórico de reuniões (Fase 5)

---

## Conclusão

O sistema de reunião executiva:
- ✅ Simula reunião **estruturada**
- ✅ Organiza falas por **papel**
- ✅ Usa conflitos como **pauta**
- ✅ Produz ata **clara**
- ✅ Torna decisões **rastreáveis**

**Próximo passo**: Integração com Orchestrator e testes
