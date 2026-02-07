# 📊 Monitoramento dos Primeiros Usuários

## O Que Monitorar nos Primeiros 30 Dias

Este guia define as métricas críticas para acompanhar a saúde do produto e comportamento dos primeiros usuários.

---

## 🎯 Métricas de Ativação (Primeira Semana)

### Funil de Ativação

```
Visitante → Cadastro → Primeira Análise → Análise Completa
   100%   →   X%     →       X%        →       X%
```

**O que rastrear:**

| Métrica | Meta | Como Medir |
|---------|------|------------|
| Taxa de Cadastro | >5% visitantes | `cadastros / visitantes_unicos` |
| Time to First Analysis | <10 min | `timestamp_primeira_analise - timestamp_cadastro` |
| Completion Rate | >70% | `analises_completas / analises_iniciadas` |
| Onboarding Skip Rate | <30% | `onboarding_skipped / total_onboardings` |

### Eventos Críticos para Rastrear

```javascript
// PostHog / Mixpanel / GA4
track('user_signed_up', { method: 'email|google' });
track('onboarding_started');
track('onboarding_completed', { steps_completed: 4 });
track('onboarding_skipped', { step: 2 });
track('first_analysis_started');
track('first_analysis_completed', { duration_seconds: 120 });
track('feature_blocked', { feature: 'export_docx', plan: 'free' });
track('upgrade_cta_clicked', { location: 'limit_banner' });
```

---

## 💰 Métricas de Conversão (Primeiro Mês)

### Funil de Monetização

```
Free User → Viu Upgrade CTA → Iniciou Checkout → Pagou → Ativo Pro
  100%    →      X%         →       X%        →   X%  →    X%
```

**O que rastrear:**

| Métrica | Meta | Como Medir |
|---------|------|------------|
| Free to Paid | >3% | `usuarios_pagos / usuarios_free` |
| Checkout Abandon Rate | <50% | `checkouts_abandonados / checkouts_iniciados` |
| ARPU (Receita/Usuário) | >R$10 | `receita_total / usuarios_ativos` |
| Trial to Paid (se tiver trial) | >20% | `conversoes_trial / trials_iniciados` |

### Triggers de Upgrade

Monitore ONDE os usuários clicam para fazer upgrade:

```javascript
track('upgrade_initiated', {
  trigger: 'limit_reached',      // Atingiu limite de análises
  trigger: 'feature_locked',     // Tentou usar feature bloqueada
  trigger: 'usage_banner',       // Banner de uso 80%+
  trigger: 'pricing_page',       // Página de preços
  trigger: 'onboarding',         // Durante onboarding
});
```

---

## 📉 Métricas de Retenção

### Cohort Analysis

Acompanhe usuários por semana de cadastro:

| Cohort | Semana 1 | Semana 2 | Semana 3 | Semana 4 |
|--------|----------|----------|----------|----------|
| Sem 1  | 100%     | ?%       | ?%       | ?%       |
| Sem 2  | -        | 100%     | ?%       | ?%       |
| Sem 3  | -        | -        | 100%     | ?%       |

**Meta:** >40% retenção na semana 4

### Engagement Metrics

| Métrica | Meta | Alerta Se |
|---------|------|-----------|
| DAU/MAU | >20% | <10% |
| Análises/Usuário/Semana | >2 | <0.5 |
| Sessão Média | >5 min | <2 min |
| Retorno em 7 dias | >50% | <30% |

---

## 🚨 Alertas Críticos

### Configurar no Sentry/PagerDuty

```yaml
# Alertas de ERRO
- name: "High Error Rate"
  condition: error_rate > 5% em 5min
  severity: critical
  
- name: "Payment Failed"
  condition: event == "payment_failed"
  severity: high
  
- name: "OpenAI API Error"
  condition: openai_error_count > 10 em 5min
  severity: high

# Alertas de NEGÓCIO
- name: "Zero Signups"
  condition: signups == 0 em 1h (horário comercial)
  severity: medium
  
- name: "Conversion Drop"
  condition: checkout_conversion < 1% em 24h
  severity: medium
```

### Alertas por Email/Slack

1. **Erro 5xx** - Qualquer erro de servidor
2. **Pagamento falhou** - Webhook de falha do MP
3. **Usuário cancelou** - Churn
4. **Limite de API OpenAI** - Rate limit atingido
5. **Database slow** - Query > 1s

---

## 📈 Dashboard Recomendado

### Métricas em Tempo Real

```
┌─────────────────────────────────────────────────────────┐
│  HOJE                                                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐│
│  │ Cadastros│  │ Análises │  │ Upgrades │  │  Receita │ │
│  │    12    │  │    45    │  │    2     │  │ R$ 194   │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘ │
├─────────────────────────────────────────────────────────┤
│  SAÚDE DO SISTEMA                                        │
│  API: ✅ 99.9%    DB: ✅ 45ms    Redis: ✅ 2ms          │
│  OpenAI: ✅ OK    MP: ✅ OK      Errors: ⚠️ 3          │
├─────────────────────────────────────────────────────────┤
│  FUNIL HOJE                                              │
│  Visitas → Cadastros → 1ª Análise → Upgrade             │
│   1,234  →    12     →     8      →    2                │
│          │   0.97%   │   66.7%    │  25.0%              │
└─────────────────────────────────────────────────────────┘
```

### Ferramentas Recomendadas

| Propósito | Ferramenta | Custo |
|-----------|------------|-------|
| Product Analytics | PostHog | Free até 1M eventos |
| Error Tracking | Sentry | Free até 5K erros |
| Logs | Logtail | Free até 1GB/mês |
| Uptime | UptimeRobot | Free até 50 monitors |
| Dashboard | Grafana Cloud | Free tier disponível |

---

## 🔍 Investigações Comuns

### "Por que usuários não completam cadastro?"

1. Verificar taxa de erro no formulário
2. Analisar drop-off por campo (qual campo para?)
3. Checar tempo de carregamento da página
4. Verificar se email de confirmação está chegando

### "Por que análises não são completadas?"

1. Tempo médio de análise (se muito longo, otimizar)
2. Erros durante análise (API OpenAI?)
3. Usuário fechou aba (análise muito demorada?)
4. Erro de validação de input

### "Por que upgrade não converte?"

1. Usuários estão vendo o CTA?
2. Checkout está funcionando?
3. Preço está claro?
4. Erro no Mercado Pago?

---

## 📋 Checklist de Monitoramento Diário

### Manhã (5 min)
- [ ] Verificar uptime overnight
- [ ] Checar erros no Sentry
- [ ] Ver cadastros das últimas 24h
- [ ] Checar receita/upgrades

### Tarde (5 min)
- [ ] Verificar métricas de engagement
- [ ] Responder feedbacks/tickets
- [ ] Checar performance da API

### Semanal (30 min)
- [ ] Análise de cohort
- [ ] Revisão de funil
- [ ] Top erros da semana
- [ ] Feedback qualitativo dos usuários

---

## 🎤 Coletando Feedback Qualitativo

### Momentos para Pedir Feedback

1. **Após primeira análise** - "Como foi sua experiência?"
2. **Após upgrade** - "O que te fez decidir?"
3. **Ao atingir limite** - "O que você faria se tivesse mais?"
4. **Após 7 dias** - NPS simplificado

### Template de Pesquisa Rápida

```
Em uma escala de 0-10, qual a chance de você 
recomendar o AgentesIA para um colega?

[0] [1] [2] [3] [4] [5] [6] [7] [8] [9] [10]

O que podemos melhorar? (opcional)
[_________________________________]
```

### Canais de Feedback

- Widget in-app (Canny, Intercom)
- Email após marcos importantes
- Chat de suporte
- Entrevistas 1:1 com early adopters

---

## 📊 Relatório Semanal Template

```markdown
# Relatório Semana X

## Resumo
- Novos usuários: XX (+X% vs semana anterior)
- Análises criadas: XX
- Receita: R$ XX
- Churn: X usuários

## Destaques
- ✅ [Coisa boa que aconteceu]
- ⚠️ [Ponto de atenção]
- 🐛 [Bug importante corrigido]

## Métricas de Funil
- Cadastro: X%
- Ativação: X%
- Conversão: X%

## Próximas Ações
1. [Ação baseada em dados]
2. [Experimento a rodar]
3. [Bug a corrigir]

## Feedback dos Usuários
- "Quote interessante de usuário"
- Pedido mais comum: [feature]
```

---

**💡 Dica Final:** Nos primeiros 30 dias, priorize CONVERSAS com usuários sobre MÉTRICAS. 
Números dizem O QUE está acontecendo. Usuários dizem POR QUÊ.
