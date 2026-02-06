# GUIA DE ARTEFATOS EXECUTIVOS

## 1️⃣ CONCEITO DE EXPORTAÇÃO EXECUTIVA

### Diferenças Chave

#### Log (Observabilidade)
- **Propósito**: Rastreamento técnico
- **Audiência**: Engenheiros, DevOps
- **Formato**: JSON estruturado
- **Conteúdo**: Eventos, timestamps, detalhes técnicos

#### Análise (Técnica)
- **Propósito**: Entender o problema
- **Audiência**: Analistas, especialistas
- **Formato**: Relatório detalhado
- **Conteúdo**: Dados, metodologia, cálculos

#### Ata Executiva (Reunião)
- **Propósito**: Registrar o que foi discutido
- **Audiência**: Participantes da reunião
- **Formato**: Estruturado (fases, falas)
- **Conteúdo**: Quem falou, o quê, quando

#### Relatório Executivo (C-Level)
- **Propósito**: Comunicar decisão e ação
- **Audiência**: CEO, CFO, Conselho, Investidores
- **Formato**: One-pager, PDF, PPT
- **Conteúdo**: Decisão, rationale, ações, riscos

### Por que a Ata NÃO é o Artefato Final para C-Level

**Ata é**:
- ❌ Registro de processo (quem falou, quando)
- ❌ Detalhada e técnica
- ❌ Focada em discussão
- ❌ Não é acionável

**Relatório Executivo é**:
- ✅ Comunicação de decisão
- ✅ Concisa e clara
- ✅ Focada em ação
- ✅ Imediatamente acionável

### Quando Usar Cada Formato

| Formato | Quando | Audiência | Duração |
|---------|--------|-----------|---------|
| **One-Pager** | Decisão rápida, comunicação interna | Executivos, gerentes | 1 página |
| **PDF** | Arquivo formal, diretoria, conselho | C-Level, investidores | 3-5 páginas |
| **PPT** | Apresentação, discussão, reunião | Executivos, board | 5-8 slides |

---

## 2️⃣ MODELO DE CONTEÚDO EXECUTIVO

### ExecutiveSummary

```python
@dataclass
class ExecutiveSummary:
    # Identificação
    execution_id: str
    title: str                   # Título da decisão
    date: datetime
    
    # Conteúdo principal
    context: str                 # Contexto em 2-3 frases
    key_decision: str            # Decisão em 1 frase
    rationale: str               # Por que em 3-4 frases
    
    # Confiança e risco
    confidence_score: float      # 0.0 a 1.0
    risks: List[ExecutiveRisk]
    
    # Ações
    action_items: List[ExecutiveAction]
    
    # Metadados
    owner: str                   # Responsável
    review_date: Optional[str]   # Quando revisar
```

### O que Entra

✅ **Deve incluir**:
- Decisão clara em 1 frase
- Contexto em 2-3 frases
- Rationale em 3-4 frases
- Ações específicas com responsável
- Riscos principais
- Confiança (0-100%)
- Responsável
- Data de revisão

❌ **Não deve incluir**:
- Detalhes técnicos
- Histórico de discussão
- Dados brutos
- Jargão técnico
- Alternativas rejeitadas
- Cálculos matemáticos

### Por que Cada Campo Existe

| Campo | Por quê |
|-------|---------|
| `title` | Identificação rápida |
| `context` | Entender situação |
| `key_decision` | Saber o quê foi decidido |
| `rationale` | Entender por quê |
| `confidence_score` | Avaliar risco |
| `risks` | Preparar mitigação |
| `action_items` | Saber o quê fazer |
| `owner` | Saber quem é responsável |
| `review_date` | Saber quando revisar |

---

## 3️⃣ MAPEAR DADOS → ARTEFATOS

### Fluxo de Transformação

```
ExecutionContext (análises brutas)
    ↓
ConflictReport (conflitos detectados)
    ↓
ConsensusResult (decisão sobre conflito)
    ↓
MeetingMinutes (ata da reunião)
    ↓
ExecutiveSummary (resumo para C-Level)
    ↓
Exportação (One-Pager, PDF, PPT)
```

### Mapeamento de Dados

```python
# De MeetingMinutes para ExecutiveSummary

summary = ExecutiveSummary(
    execution_id=meeting.execution_id,
    
    # Título vem da decisão principal
    title=meeting.decisions[0].topic,
    
    # Contexto vem do problema
    context=meeting.problem_description,
    
    # Decisão vem da decisão da reunião
    key_decision=meeting.decisions[0].decision,
    
    # Rationale vem da justificativa
    rationale=meeting.decisions[0].rationale,
    
    # Confiança vem da decisão
    confidence_score=meeting.decisions[0].confidence_score,
    
    # Riscos vem de análise de risco
    risks=[...],
    
    # Ações vem da decisão
    action_items=meeting.decisions[0].action_items,
    
    # Owner vem da reunião
    owner=meeting.chair,
    
    # Review date é 30 dias depois
    review_date="30 dias"
)
```

### Regras de Transformação

✅ **Fazer**:
- Extrair dados reais do sistema
- Traduzir para linguagem executiva
- Resumir sem perder essência
- Adicionar contexto de negócio

❌ **Não fazer**:
- Inventar dados
- Reanalisar o problema
- Adicionar opiniões pessoais
- Mudar a decisão

---

## 4️⃣ IMPLEMENTAR EXPORTADORES

### OnePagerExporter

```python
exporter = OnePagerExporter()
markdown = exporter.export(summary)
# Salva em arquivo
exporter.export(summary, output_path="decisao.md")
```

**Output**:
```markdown
# Investir em Marketing Digital

**Data**: 05/02/2024
**Responsável**: CEO

## CONTEXTO
Vendas caíram 20% nos últimos 3 meses...

## DECISÃO
**Investir $100K em marketing digital**

## RATIONALE
Balanceado entre oportunidade comercial e viabilidade financeira...

## AÇÕES IMEDIATAS
- Preparar plano de marketing digital
  - Responsável: Commercial
  - Prazo: 5 dias úteis
- Monitorar ROI mensalmente
  - Responsável: Financial
  - Prazo: Contínuo

## RISCOS
- Retorno abaixo do esperado
  - Probabilidade: Medium
  - Impacto: High
  - Mitigação: Revisar em 30 dias

## PRÓXIMOS PASSOS
- Revisar em 30 dias
```

### PDFExporter

```python
exporter = PDFExporter()
exporter.export(report, output_path="relatorio.pdf")
```

**Estrutura**:
- Capa com título e data
- Sumário executivo
- Contexto
- Decisão
- Rationale
- Ações
- Riscos
- Próximos passos

### PPTExporter

```python
exporter = PPTExporter()
exporter.export(report, output_path="apresentacao.pptx")
```

**Slides**:
1. Capa (título, data, responsável)
2. Contexto (background)
3. Decisão (destacada)
4. Rationale
5. Alternativas consideradas
6. Plano de ação
7. Riscos e mitigação
8. Próximos passos

---

## 5️⃣ PADRÕES DE LINGUAGEM EXECUTIVA

### Regras de Escrita

#### 1. Frases Curtas
❌ **Ruim**: "Considerando a análise abrangente do mercado e os dados financeiros disponíveis, recomendamos que a organização proceda com a implementação de uma estratégia de marketing digital de escopo moderado."

✅ **Bom**: "Investir $100K em marketing digital."

#### 2. Verbos de Ação
❌ **Ruim**: "Seria interessante considerar a possibilidade de revisar..."

✅ **Bom**: "Revisar em 30 dias."

#### 3. Nada de Jargão Técnico
❌ **Ruim**: "Otimizar o pipeline de conversão com análise de funnel e A/B testing."

✅ **Bom**: "Melhorar taxa de conversão de leads em clientes."

#### 4. Decisão Antes da Explicação
❌ **Ruim**: "Porque o mercado está crescendo e temos oportunidade, devemos investir."

✅ **Bom**: "Investir em marketing. Mercado está crescendo e temos oportunidade."

#### 5. Máximo 5 Bullets por Seção
❌ **Ruim**: 10 bullets em uma seção

✅ **Bom**: 3-5 bullets, bem selecionados

### Estrutura de Parágrafo

```
CONTEXTO (2-3 frases):
[Situação] [Problema] [Urgência]

DECISÃO (1 frase):
[Verbo] [O quê] [Quanto/Como]

RATIONALE (3-4 frases):
[Razão 1] [Razão 2] [Benefício] [Mitigação]

AÇÃO (Bullets):
- [Ação específica]
  - Responsável: [Nome]
  - Prazo: [Quando]
```

---

## 6️⃣ CONTROLE DE RISCO

### Validações Obrigatórias

```python
def validate_summary(summary: ExecutiveSummary):
    # Título é obrigatório
    assert summary.title, "Título é obrigatório"
    
    # Decisão é obrigatória
    assert summary.key_decision, "Decisão é obrigatória"
    
    # Rationale é obrigatória
    assert summary.rationale, "Rationale é obrigatória"
    
    # Confiança entre 0-100%
    assert 0.0 <= summary.confidence_score <= 1.0
    
    # Pelo menos uma ação
    assert len(summary.action_items) > 0, "Pelo menos uma ação"
    
    # Cada ação tem responsável
    for action in summary.action_items:
        assert action.owner, "Ação sem responsável"
    
    # Cada risco tem mitigação
    for risk in summary.risks:
        assert risk.mitigation, "Risco sem mitigação"
```

### Proteções

#### 1. Relatórios Longos Demais
- One-pager: máximo 1 página
- PDF: máximo 5 páginas
- PPT: máximo 8 slides

#### 2. Linguagem Ambígua
- Decisão deve ser clara
- Ações devem ser específicas
- Responsáveis devem ser nomeados

#### 3. Falta de Responsável
- Cada ação tem owner
- Owner é pessoa específica
- Owner tem prazo

#### 4. Decisão Sem Ação
- Mínimo 1 ação
- Ações são específicas
- Ações têm prazo

---

## 7️⃣ EXEMPLOS PRÁTICOS

### Exemplo 1: One-Pager

**Título**: Investir em Marketing Digital

**Contexto**: Vendas caíram 20% nos últimos 3 meses. Análise mostra falta de leads. Mercado está em crescimento.

**Decisão**: Investir $100K em marketing digital.

**Rationale**: Balanceado entre oportunidade comercial (recuperar market share) e viabilidade financeira (ROI esperado 150%). Reduz risco de perda de clientes.

**Confiança**: 82%

**Ações**:
- Preparar plano de marketing digital (Commercial, 5 dias)
- Monitorar ROI mensalmente (Financial, contínuo)
- Revisar em 30 dias (CEO, 30 dias)

**Riscos**:
- Retorno abaixo do esperado (Medium/High) → Revisar em 30 dias
- Implementação atrasada (Low/Medium) → Designar PM dedicado

**Responsável**: CEO

**Revisar em**: 30 dias

### Exemplo 2: Estrutura de PDF

**Capa**:
- Título: "Investir em Marketing Digital"
- Data: 05/02/2024
- Responsável: CEO

**Sumário Executivo**:
"Recomendamos investimento de $100K em marketing digital para recuperar leads e crescimento. Decisão balanceada entre oportunidade e viabilidade."

**Contexto**:
"Vendas caíram 20% nos últimos 3 meses. Análise de mercado mostra oportunidade clara. Competidores estão investindo em digital. Timing é crítico."

**Decisão**:
"Investir $100K em marketing digital com ROI esperado de 150%."

**Rationale**:
"1. Oportunidade: Mercado em crescimento, timing crítico
2. Viabilidade: ROI de 150% justifica investimento
3. Risco: Mitigado com revisão em 30 dias
4. Ação: Plano pronto em 5 dias"

**Ações**:
- Preparar plano (Commercial, 5 dias)
- Monitorar ROI (Financial, mensal)
- Revisar (CEO, 30 dias)

**Riscos**:
- Retorno abaixo do esperado → Revisar em 30 dias
- Implementação atrasada → PM dedicado

**Próximos Passos**:
- Plano em 5 dias
- Revisão em 30 dias

### Exemplo 3: Estrutura de PPT

**Slide 1: Capa**
- Título: "Investir em Marketing Digital"
- Data: 05/02/2024
- Responsável: CEO

**Slide 2: Contexto**
- Vendas caíram 20%
- Falta de leads
- Mercado em crescimento
- Timing crítico

**Slide 3: Decisão**
- **Investir $100K em Marketing Digital**
- Confiança: 82%

**Slide 4: Rationale**
- Oportunidade: Mercado em crescimento
- Viabilidade: ROI 150%
- Risco: Mitigado com revisão
- Ação: Plano em 5 dias

**Slide 5: Alternativas**
- Cortar custos (rejeitado: perderemos market share)
- Investir $500K (rejeitado: ROI insuficiente)
- Investir $100K (aprovado: balanceado)

**Slide 6: Plano de Ação**
- Preparar plano (Commercial, 5 dias)
- Monitorar ROI (Financial, mensal)
- Revisar (CEO, 30 dias)

**Slide 7: Riscos**
- Retorno abaixo do esperado (Medium/High)
- Implementação atrasada (Low/Medium)

**Slide 8: Próximos Passos**
- Plano em 5 dias
- Revisão em 30 dias

---

## 8️⃣ INTEGRAÇÃO COM O SISTEMA

### Ponto de Integração

```python
# Em orchestrator.py, após reunião:

# 1. Executa reunião
meeting_minutes = meeting_orchestrator.run_if_needed(...)

# 2. Transforma em resumo executivo
summary = ExecutiveSummaryBuilder.from_meeting(meeting_minutes)

# 3. Exporta em formato desejado
exporter = ExecutiveExporterFactory.create(ExecutiveFormat.PDF)
exporter.export(summary, output_path="decisao.pdf")
```

### Como o Usuário Escolhe o Formato

```python
# Via API
export_format = request.query_params.get("format", "one_pager")
exporter = ExecutiveExporterFactory.create(ExecutiveFormat[export_format.upper()])

# Via UI (futuro)
# Dropdown: One-Pager | PDF | PowerPoint
```

### Manter Opcional

- Exportação é opcional
- Sistema funciona sem exportação
- Não impacta performance
- Sem dependências obrigatórias

---

## 9️⃣ DECISÕES TÉCNICAS

### Tomadas

| Decisão | Justificativa | Trade-off |
|---------|---------------|-----------|
| **Separar análise de comunicação** | Clareza de responsabilidades | Mais classes |
| **Usar reportlab para PDF** | Sem dependências pesadas | Menos design gráfico |
| **Usar python-pptx para PPT** | Estrutura, não design | Sem animações |
| **Validação obrigatória** | Evitar artefatos ruins | Mais código |
| **Factory pattern** | Extensível | Mais abstração |

### Fora Propositalmente

- ❌ Design gráfico avançado
- ❌ Branding corporativo
- ❌ Temas customizáveis
- ❌ Integração com Word
- ❌ Assinatura digital

---

## Conclusão

O sistema de artefatos executivos:
- ✅ Transforma decisões em comunicação clara
- ✅ Separa análise de comunicação
- ✅ Suporta múltiplos formatos
- ✅ Pronto para C-Level
- ✅ Não quebra fluxo atual

**Próximo passo**: Integração com Orchestrator
