# 🚀 Checklist de Lançamento - Produção

## Pré-requisitos

### Infraestrutura
- [ ] **Servidor/Cloud** configurado (Railway, Render, Fly.io, AWS, etc.)
- [ ] **Domínio** registrado e DNS configurado
- [ ] **SSL/HTTPS** configurado (Let's Encrypt ou Cloudflare)
- [ ] **Banco de dados** PostgreSQL provisionado
- [ ] **Redis** provisionado (para cache e filas)
- [ ] **CDN** configurado (Cloudflare recomendado)

### Serviços Externos
- [ ] **OpenAI** - API key de produção obtida
- [ ] **Mercado Pago** - Conta de produção ativa, webhooks configurados
- [ ] **Email (SMTP)** - Servidor configurado (SendGrid, Mailgun, etc.)
- [ ] **Storage (S3)** - Bucket criado com permissões corretas

---

## Checklist de Segurança

### Backend
- [ ] `SECRET_KEY` gerada com `secrets.token_hex(32)`
- [ ] `JWT_SECRET_KEY` diferente do SECRET_KEY
- [ ] `DEBUG=false` em produção
- [ ] `CORS_ORIGINS` restrito ao domínio do frontend
- [ ] `ALLOWED_HOSTS` configurado corretamente
- [ ] Rate limiting ativo (60 req/min padrão)
- [ ] Headers de segurança ativos (X-Frame-Options, etc.)
- [ ] SQL Injection protegido (usar ORM/prepared statements)
- [ ] Validação de input em todos os endpoints

### Frontend
- [ ] `NEXT_PUBLIC_API_URL` apontando para API de produção
- [ ] Variáveis sensíveis NÃO expostas no client
- [ ] CSP (Content Security Policy) configurado
- [ ] HTTPS forçado

### Autenticação
- [ ] Senhas hashadas com PBKDF2/bcrypt
- [ ] Tokens JWT com expiração curta (30 min access, 7 dias refresh)
- [ ] Rate limit em login (prevenir brute force)
- [ ] Logout invalida tokens

### Dados
- [ ] Backup automático do banco configurado
- [ ] Criptografia em repouso (se dados sensíveis)
- [ ] LGPD/GDPR compliance (se aplicável)

---

## Checklist de Configuração

### Variáveis de Ambiente

```bash
# Verificar se todas estão configuradas:
APP_ENV=production
DEBUG=false
SECRET_KEY=✓
JWT_SECRET_KEY=✓
DATABASE_URL=✓
REDIS_URL=✓
OPENAI_API_KEY=✓
MERCADO_PAGO_ACCESS_TOKEN=✓
MERCADO_PAGO_WEBHOOK_SECRET=✓
SENTRY_DSN=✓
```

### Mercado Pago
- [ ] Planos criados via `setup_plans.py`
- [ ] Webhook URL configurada no painel MP
- [ ] Testar fluxo de pagamento em sandbox
- [ ] Migrar para credenciais de produção
- [ ] `MERCADO_PAGO_SANDBOX=false`

### Banco de Dados
- [ ] Migrations executadas
- [ ] Índices criados para queries frequentes
- [ ] Connection pool configurado (20 conexões)
- [ ] Backup automático ativo

---

## Checklist de Monitoramento

### Sentry (Error Tracking)
- [ ] `SENTRY_DSN` configurado no backend
- [ ] `NEXT_PUBLIC_SENTRY_DSN` configurado no frontend
- [ ] Alertas de email configurados
- [ ] Source maps uploaded (frontend)

### Health Checks
- [ ] `/health` retorna status de componentes
- [ ] `/health/live` para liveness probe
- [ ] `/health/ready` para readiness probe
- [ ] Alertas configurados para falhas

### Logs
- [ ] Logs estruturados (JSON)
- [ ] Logs enviados para serviço externo (Logtail, Papertrail)
- [ ] Log de requests com request_id
- [ ] Retenção de logs definida (30 dias mínimo)

### Métricas (Opcional)
- [ ] `/metrics` endpoint para Prometheus
- [ ] Dashboard no Grafana
- [ ] Alertas de performance

---

## Checklist de CI/CD

### GitHub Actions
- [ ] Workflow de CI configurado
- [ ] Testes rodando em PRs
- [ ] Linting ativo
- [ ] Security scan ativo
- [ ] Deploy automático para main

### Secrets do GitHub
```
VERCEL_TOKEN
VERCEL_ORG_ID
VERCEL_PROJECT_ID
API_URL
APP_URL
SENTRY_AUTH_TOKEN
```

---

## Checklist de Performance

### Backend
- [ ] Gunicorn com 4+ workers
- [ ] Timeout de 120s configurado
- [ ] Compressão gzip ativa
- [ ] Cache de queries frequentes (Redis)

### Frontend
- [ ] Build de produção (`npm run build`)
- [ ] Imagens otimizadas (next/image)
- [ ] Code splitting ativo
- [ ] Lighthouse score > 80

### Database
- [ ] Índices nas colunas de busca
- [ ] Query explain para queries lentas
- [ ] Connection pool adequado

---

## Checklist de Testes Finais

### Funcionalidade
- [ ] Cadastro de usuário
- [ ] Login/Logout
- [ ] Recuperação de senha
- [ ] Criar análise (Free)
- [ ] Limites do plano Free funcionando
- [ ] Checkout de upgrade
- [ ] Webhook de pagamento
- [ ] Upgrade automático de plano
- [ ] Exportação PDF
- [ ] Feature gates bloqueando corretamente

### Edge Cases
- [ ] Usuário tenta exceder limite
- [ ] Pagamento falha
- [ ] Token expirado
- [ ] Sessão inválida
- [ ] API OpenAI indisponível

### Mobile
- [ ] Layout responsivo
- [ ] Touch interactions
- [ ] Performance em 3G

---

## Lançamento

### Dia D-1
- [ ] Freeze de código
- [ ] Backup completo do banco
- [ ] Comunicação interna alinhada
- [ ] Plano de rollback documentado

### Dia D
- [ ] Deploy backend
- [ ] Verificar health checks
- [ ] Deploy frontend
- [ ] Smoke tests manuais
- [ ] Monitorar Sentry
- [ ] Monitorar logs

### Pós-Lançamento
- [ ] Monitorar métricas 24h
- [ ] Responder issues críticos
- [ ] Coletar feedback inicial
- [ ] Ajustar rate limits se necessário

---

## Rollback Plan

Se algo der errado:

1. **Frontend**: Reverter deploy no Vercel/Netlify
2. **Backend**: Reverter para imagem Docker anterior
3. **Database**: Restaurar backup (se necessário)
4. **Comunicar**: Notificar usuários se houver downtime

---

## Contatos de Emergência

| Serviço | Contato |
|---------|---------|
| DevOps | [email] |
| Backend | [email] |
| Frontend | [email] |
| Suporte MP | https://www.mercadopago.com.br/developers/pt/support |
| Suporte OpenAI | https://help.openai.com |

---

## Pós-Lançamento: O que Monitorar

### Primeira Semana
- Taxa de cadastro vs abandono
- Tempo médio até primeira análise
- Erros mais frequentes (Sentry)
- Feedback qualitativo

### Primeiro Mês
- Conversão Free → Pro
- Churn rate
- NPS (se implementado)
- Feature mais/menos usada

---

**✅ Quando todos os itens estiverem marcados, você está pronto para lançar!**
