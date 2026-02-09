# Deploy no Railway - Backend AgentesIA

## Pré-requisitos

1. Conta no [Railway](https://railway.app)
2. Repositório conectado ao Railway
3. Banco PostgreSQL (Railway oferece gratuitamente)
4. Redis (opcional para desenvolvimento, recomendado para produção)

## Configuração do Serviço

### 1. Configurar Root Directory

No Railway, vá em **Settings** do seu serviço e configure:

```
Root Directory: backend
```

**Isso é CRÍTICO** - o Railway precisa saber que o código está na pasta `backend`.

### 2. Variáveis de Ambiente Obrigatórias

No painel **Variables** do Railway, adicione:

```bash
# === AMBIENTE ===
ENVIRONMENT=production
DEBUG=false

# === SEGURANÇA (OBRIGATÓRIO) ===
# Gere com: openssl rand -hex 32
JWT_SECRET_KEY=sua-chave-secreta-com-pelo-menos-32-caracteres-aqui

# === DATABASE ===
# O Railway fornece automaticamente se você adicionar PostgreSQL
DATABASE_URL=${{Postgres.DATABASE_URL}}

# === CORS ===
# URLs do seu frontend (separadas por vírgula)
CORS_ORIGINS=https://seu-frontend.vercel.app,https://seu-dominio.com

# === LLM (OBRIGATÓRIO para análises) ===
ANTHROPIC_API_KEY=sk-ant-api...

# === REDIS (opcional, mas recomendado) ===
# O Railway fornece automaticamente se você adicionar Redis
REDIS_URL=${{Redis.REDIS_URL}}
```

### 3. Variáveis Opcionais

```bash
# === OBSERVABILITY ===
SENTRY_DSN=https://xxx@sentry.io/xxx
LOG_LEVEL=INFO

# === BILLING (para pagamentos) ===
STRIPE_SECRET_KEY=sk_live_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
STRIPE_PRICE_PRO_MONTHLY=price_xxx
STRIPE_PRICE_PRO_YEARLY=price_xxx
STRIPE_PRICE_ENTERPRISE_MONTHLY=price_xxx

# === RATE LIMITING ===
RATE_LIMIT_FREE=10/hour
RATE_LIMIT_PRO=100/hour
RATE_LIMIT_ENTERPRISE=1000/hour
```

## Adicionando Serviços

### PostgreSQL

1. No Railway, clique em **New** → **Database** → **PostgreSQL**
2. A variável `DATABASE_URL` será configurada automaticamente
3. Use a referência `${{Postgres.DATABASE_URL}}` nas variáveis

### Redis (Recomendado)

1. No Railway, clique em **New** → **Database** → **Redis**
2. Use a referência `${{Redis.REDIS_URL}}` nas variáveis
3. Habilita cache, rate limiting e filas de tarefas

## Deploy

### Opção 1: Deploy Automático

1. Faça push das alterações para o branch principal
2. O Railway detectará automaticamente e fará o build

### Opção 2: Deploy Manual

No dashboard do Railway:
1. Vá para o serviço
2. Clique em **Deployments**
3. Clique em **Deploy** ou **Redeploy**

## Verificação

Após o deploy, verifique:

```bash
# Health check
curl https://seu-servico.railway.app/health

# Deve retornar:
# {"status": "healthy", "version": "1.0.0", ...}
```

## Troubleshooting

### Erro: "error creating build plan with buildpacks"

**Solução:** Configure o Root Directory como `backend` nas Settings.

### Erro: "No module named 'app'"

**Solução:** Verifique se o Root Directory está configurado corretamente.

### Erro: "Connection refused" no PostgreSQL

**Solução:** 
1. Verifique se o PostgreSQL foi adicionado
2. Use `${{Postgres.DATABASE_URL}}` ao invés de copiar a URL

### Erro: "JWT_SECRET_KEY deve ter pelo menos 32 caracteres"

**Solução:** Gere uma chave forte:
```bash
openssl rand -hex 32
```

### Build muito lento

**Solução:** O primeiro build pode demorar 5-10 minutos. Builds subsequentes usam cache.

## Estrutura de Arquivos

O backend possui os seguintes arquivos de configuração:

```
backend/
├── railway.json      # Configuração do Railway
├── Procfile          # Comando de inicialização
├── runtime.txt       # Versão do Python (3.11.7)
├── nixpacks.toml     # Configuração do Nixpacks
├── requirements.txt  # Dependências Python
└── app.py           # Aplicação FastAPI
```

## Monitoramento

- **Logs:** Railway Dashboard → Service → Logs
- **Métricas:** `/metrics` endpoint (proteger em produção)
- **Health:** `/health`, `/health/live`, `/health/ready`

## Custos

Railway oferece:
- **Hobby Plan:** $5/mês com $5 de créditos inclusos
- **Pro Plan:** $20/mês para equipes
- PostgreSQL e Redis têm custos adicionais baseados em uso

## Suporte

- [Railway Docs](https://docs.railway.app)
- [Railway Discord](https://discord.gg/railway)
