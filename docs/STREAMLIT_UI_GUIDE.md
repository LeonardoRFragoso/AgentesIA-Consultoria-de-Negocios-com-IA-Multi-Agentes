# GUIA DE UI STREAMLIT PROFISSIONAL

## 1️⃣ UX FLOW DO USUÁRIO

### Fluxo Ideal

```
1. ENTRADA
   └─ Usuário descreve problema em text area

2. CONTEXTO
   └─ Usuário seleciona tipo de negócio (sidebar)

3. PROCESSAMENTO
   ├─ Spinner com fase atual
   ├─ Barra de progresso
   └─ Status textual

4. RESULTADO
   ├─ Decision Card (destaque)
   ├─ Confiança visual
   ├─ Ações imediatas
   └─ Métricas (3 colunas)

5. EXPLORAÇÃO
   ├─ Expander: Conflitos
   ├─ Expander: Reunião
   ├─ Expander: Histórico
   └─ Expander: Análises detalhadas

6. EXPORTAÇÃO
   ├─ One-pager (Markdown)
   ├─ PDF (formal)
   └─ PowerPoint (apresentação)
```

### O que Aparece em Cada Etapa

**Etapa 1: Entrada**
- ✅ Text area grande (120px altura)
- ✅ Placeholder orientativo
- ✅ Botão "Analisar Cenário"
- ❌ Nenhuma opção avançada

**Etapa 2: Contexto**
- ✅ Sidebar com selectbox
- ✅ Tipo de negócio
- ✅ Profundidade (opcional)
- ❌ Configurações técnicas

**Etapa 3: Processamento**
- ✅ Spinner com mensagem
- ✅ Barra de progresso (0-100%)
- ✅ Status da fase (1/4, 2/4, etc)
- ❌ Logs técnicos
- ❌ Detalhes de agentes

**Etapa 4: Resultado**
- ✅ Decision Card (gradiente roxo)
- ✅ 3 métricas (Confiança, Conflitos, Ações)
- ✅ Ações com responsável e prazo
- ✅ Botões de exportação
- ❌ Ata completa
- ❌ Logs

**Etapa 5: Exploração**
- ✅ Expanders (colapsáveis)
- ✅ Nada aberto por padrão
- ✅ Informação sob demanda
- ❌ Tudo visível

**Etapa 6: Exportação**
- ✅ 3 botões (One-Pager, PDF, PPT)
- ✅ Feedback de sucesso
- ✅ Download automático
- ❌ Opções avançadas

---

## 2️⃣ ESTRUTURA DA PÁGINA

```
┌─────────────────────────────────────────────────────────┐
│  HEADER: 🎯 Consultor Executivo Multi-Agentes          │
│  Descrição: Análise completa com decisões claras        │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ SIDEBAR                    │ MAIN CONTENT                │
│ ⚙️ Configuração           │ 📝 Descreva seu Desafio     │
│ - Tipo de Negócio         │ [Text Area]                 │
│ - Profundidade            │ [🚀 Analisar Cenário]       │
│ 📖 Sobre                  │                             │
│                           │ 📊 Resultado da Análise     │
│                           │ ┌─────────────────────────┐ │
│                           │ │ 🎯 Decision Card        │ │
│                           │ │ (Gradiente roxo)        │ │
│                           │ └─────────────────────────┘ │
│                           │                             │
│                           │ Confiança │ Conflitos │ Ações
│                           │                             │
│                           │ ✅ Ações Imediatas          │
│                           │ [Action 1]                  │
│                           │ [Action 2]                  │
│                           │ [Action 3]                  │
│                           │                             │
│                           │ 📑 Análises Detalhadas      │
│                           │ [Expander] Conflitos        │
│                           │ [Expander] Reunião          │
│                           │ [Expander] Histórico        │
│                           │ [Expander] Análises         │
│                           │                             │
│                           │ 📤 Exportar Resultado       │
│                           │ [PDF] [One-Pager] [PPT]    │
└─────────────────────────────────────────────────────────┘
```

---

## 3️⃣ COMPONENTES VISUAIS

### Decision Card
- **Estilo**: Gradiente roxo (#667eea → #764ba2)
- **Conteúdo**: Título + Problema + Perspectivas
- **Quando aparece**: Após análise completa
- **Destaque**: Sim (card principal)

### Confidence Indicator
- **Formato**: 3 métricas em colunas
- **Campos**: Confiança, Conflitos, Ações
- **Cores**: Verde (alta), Amarelo (média), Vermelho (baixa)
- **Quando aparece**: Após análise

### Action Items
- **Estilo**: Card cinza com borda azul
- **Conteúdo**: Descrição + Responsável + Prazo
- **Quando aparece**: Após análise
- **Máximo**: 5 ações

### Expanders
- **Padrão**: Colapsados (expanded=False)
- **Conteúdo**: Conflitos, Reunião, Histórico, Análises
- **Quando aparecem**: Após análise
- **Ordem**: Conflitos → Reunião → Histórico → Análises

### Export Buttons
- **Formato**: 3 botões em colunas
- **Tipos**: One-Pager, PDF, PPT
- **Quando aparecem**: Após análise
- **Ação**: Download automático

---

## 4️⃣ ESTADOS DA APLICAÇÃO

### Estado: Idle
```
- Mostrar: Input area + Botão Analisar
- Ocultar: Resultados
- Ação: Aguardar entrada do usuário
```

### Estado: Running
```
- Mostrar: Spinner + Progress bar + Status
- Ocultar: Input area, Resultados
- Ação: Bloquear interação
```

### Estado: Completed
```
- Mostrar: Decision Card + Métricas + Ações + Expanders + Export
- Ocultar: Spinner, Progress bar
- Ação: Permitir exploração
```

### Estado: Partial Failure
```
- Mostrar: Warning + Resultados parciais
- Ocultar: Componentes indisponíveis
- Ação: Permitir exportação de parcial
```

### Estado: Error
```
- Mostrar: Error message + Botão Tentar Novamente
- Ocultar: Resultados
- Ação: Permitir nova tentativa
```

---

## 5️⃣ PADRÕES VISUAIS E UX

### Máx. 2 Níveis de Informação
- ✅ Nível 1: Decision Card (destaque)
- ✅ Nível 2: Ações + Métricas
- ❌ Nível 3+: Expanders (sob demanda)

### Uso Moderado de Cores
- ✅ Roxo para Decision Card (destaque)
- ✅ Cinza para Action Items (secundário)
- ✅ Verde/Amarelo/Vermelho para Confiança
- ❌ Cores demais

### Destaque Visual Só para Decisão
- ✅ Decision Card com gradiente
- ✅ Tamanho grande (28px)
- ✅ Posição: Topo dos resultados
- ❌ Múltiplos destaques

### Feedback Claro de Carregamento
- ✅ Spinner com mensagem
- ✅ Barra de progresso
- ✅ Status textual (Fase X/4)
- ❌ Carregamento silencioso

### Linguagem Não Técnica
- ✅ "Desafio" em vez de "Problema"
- ✅ "Ações Imediatas" em vez de "Tarefas"
- ✅ "Decisão Recomendada" em vez de "Output"
- ❌ Jargão técnico

---

## 6️⃣ CONTROLE DE RISCO (UX)

### Evitar Interface Poluída
- ✅ Uma coisa por vez
- ✅ Informação progressiva
- ✅ Expanders para detalhes
- ❌ Tudo visível

### Evitar Usuário Perdido
- ✅ Títulos claros
- ✅ Seções bem delimitadas
- ✅ Ordem lógica
- ❌ Navegação confusa

### Evitar Excesso de Opções
- ✅ 2-3 opções por seção
- ✅ Padrões sensatos
- ✅ Menos é mais
- ❌ 10+ opções

### Evitar Exposição de Complexidade
- ✅ Ocultar logs
- ✅ Ocultar detalhes técnicos
- ✅ Ocultar nomes de agentes
- ❌ Mostrar implementação

---

## 7️⃣ EXEMPLO: RESULTADO SIMPLES

```
📊 Resultado da Análise

🎯 Decisão Recomendada
┌─────────────────────────────────────────┐
│ 🎯 Investir em Marketing Digital        │
│ Vendas caíram 20%...                    │
│ ✓ Análise baseada em 5 perspectivas     │
└─────────────────────────────────────────┘

Confiança: 82% | Conflitos: 0 | Ações: 3

✅ Ações Imediatas
┌─────────────────────────────────────────┐
│ ✓ Preparar plano de implementação       │
│   👤 Commercial | ⏰ 5 dias              │
└─────────────────────────────────────────┘

📑 Análises Detalhadas
[Expander] Conflitos (collapsed)
[Expander] Reunião (collapsed)
[Expander] Histórico (collapsed)
[Expander] Análises (collapsed)

📤 Exportar Resultado
[📄 One-Pager] [📋 PDF] [🎯 PPT]
```

---

## 8️⃣ EXEMPLO: RESULTADO COM CONFLITOS

```
📊 Resultado da Análise

🎯 Decisão Recomendada
┌─────────────────────────────────────────┐
│ 🎯 Investimento Moderado em Marketing   │
│ Vendas caíram 20%...                    │
│ ✓ Análise baseada em 5 perspectivas     │
└─────────────────────────────────────────┘

Confiança: 82% | Conflitos: 1 ⚠️ | Ações: 3

✅ Ações Imediatas
[Action 1]
[Action 2]
[Action 3]

📑 Análises Detalhadas
[Expander] ⚡ Conflitos Detectados (collapsed)
  └─ Conflito Financeiro: Investir vs Cortar
     Commercial: $500K | Financial: Não viável
     Resolução: $100K com ROI 150%
[Expander] Reunião (collapsed)
[Expander] Histórico (collapsed)
[Expander] Análises (collapsed)

📤 Exportar Resultado
[📄 One-Pager] [📋 PDF] [🎯 PPT]
```

---

## 9️⃣ DECISÕES TÉCNICAS

### Tomadas
- ✅ Layout wide (máximo espaço)
- ✅ Sidebar expandido por padrão
- ✅ Session state para persistência
- ✅ Expanders para exploração
- ✅ Custom CSS para Decision Card

### Trade-offs
- Streamlit é limitado em design gráfico (aceitável)
- Sem animações avançadas (foco em conteúdo)
- Sem temas customizáveis (genérico)

### Fora Propositalmente
- ❌ Filtros avançados
- ❌ Múltiplas análises simultâneas
- ❌ Histórico visual
- ❌ Comparação lado a lado
- ❌ Customização de cores

---

## Conclusão

A UI Streamlit:
- ✅ É clara e profissional
- ✅ Guia o usuário
- ✅ Torna decisões visíveis
- ✅ Permite exploração
- ✅ Funciona para não técnicos

**Pronto para usuários reais (Founders, Diretores, Consultores)**
