# Variáveis de Ambiente para Railway

## Variáveis Automáticas do PostgreSQL

Estas variáveis são criadas automaticamente pelo Railway quando você conecta o PostgreSQL:

```
DATABASE_PUBLIC_URL=postgresql://${{PGUSER}}:${{POSTGRES_PASSWORD}}@${{RAILWAY_TCP_PROXY_DOMAIN}}:${{RAILWAY_TCP_PROXY_PORT}}/${{PGDATABASE}}
DATABASE_URL=postgresql://${{PGUSER}}:${{POSTGRES_PASSWORD}}@${{RAILWAY_PRIVATE_DOMAIN}}:5432/${{PGDATABASE}}
PGDATA=/var/lib/postgresql/data/pgdata
PGDATABASE=${{POSTGRES_DB}}
PGHOST=${{RAILWAY_PRIVATE_DOMAIN}}
PGPASSWORD=${{POSTGRES_PASSWORD}}
PGPORT=5432
PGUSER=${{POSTGRES_USER}}
POSTGRES_DB=railway
POSTGRES_PASSWORD=EagpNjxltlPbhJaMOLorKYzoSoQJVUPN
POSTGRES_USER=postgres
RAILWAY_DEPLOYMENT_DRAINING_SECONDS=60
SSL_CERT_DAYS=820
```

---

## Variáveis Obrigatórias a Adicionar

### 1. ENVIRONMENT
**Valor:** `production`
**Descrição:** Define o ambiente de execução

### 2. DEBUG
**Valor:** `false`
**Descrição:** Desativa modo debug em produção

### 3. JWT_SECRET_KEY
**Valor:** Gere com: `openssl rand -hex 32`
**Exemplo:** `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2`
**Descrição:** Chave secreta para assinar tokens JWT (mínimo 32 caracteres)

### 4. CORS_ORIGINS
**Valor:** `["https://seu-frontend.vercel.app"]`
**Exemplo:** `["https://agentesia.vercel.app"]`
**Descrição:** Lista de domínios permitidos para requisições CORS

### 5. ANTHROPIC_API_KEY
**Valor:** `sk-ant-api-...` (sua chave da API Anthropic)
**Descrição:** Chave para usar o modelo Claude da Anthropic

### 6. LOG_LEVEL
**Valor:** `INFO`
**Opções:** `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
**Descrição:** Nível de logging da aplicação

---

## Variáveis Opcionais (Recomendadas)

### 8. REDIS_URL
**Valor:** `${{Redis.REDIS_URL}}` (se tiver Redis configurado)
**Descrição:** URL de conexão Redis para cache e rate limiting
**Nota:** Opcional em desenvolvimento, recomendado em produção

### 9. STRIPE_SECRET_KEY
**Valor:** `sk_live_...` (sua chave Stripe)
**Descrição:** Chave secreta Stripe para pagamentos
**Nota:** Opcional se não usar billing

### 10. STRIPE_WEBHOOK_SECRET
**Valor:** `whsec_...` (seu webhook secret Stripe)
**Descrição:** Secret para validar webhooks do Stripe
**Nota:** Opcional se não usar billing

### 11. SENTRY_DSN
**Valor:** `https://...@sentry.io/...`
**Descrição:** URL para rastreamento de erros com Sentry
**Nota:** Opcional

---

## Resumo Rápido para Copiar/Colar

```
ENVIRONMENT=production
DEBUG=false
JWT_SECRET_KEY=<gere com: openssl rand -hex 32>
CORS_ORIGINS=["https://seu-frontend.vercel.app"]
ANTHROPIC_API_KEY=sk-ant-api-...
LOG_LEVEL=INFO
```

---

## Passos para Adicionar no Railway

1. Vá para a aba **Variables** do seu serviço
2. Clique em **New Variable** para cada variável
3. Preencha **Name** e **Value**
4. Clique em **Add**
5. Após adicionar todas, clique em **Redeploy**

---

## Gerador de JWT_SECRET_KEY

Execute no seu terminal:
```bash
openssl rand -hex 32
```

Copie o resultado e cole em `JWT_SECRET_KEY` no Railway.

---

## Checklist de Configuração

- [ ] DATABASE_URL (automático)
- [ ] ENVIRONMENT = production
- [ ] DEBUG = false
- [ ] JWT_SECRET_KEY (gerado)
- [ ] CORS_ORIGINS (seu domínio)
- [ ] ANTHROPIC_API_KEY (sua chave)
- [ ] LOG_LEVEL = INFO
- [ ] Clicou em Redeploy

Após completar, o backend deve iniciar sem erros!
