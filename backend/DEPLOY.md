# 🚀 Deploy Guide - PostgreSQL Production

## 1. Provedores Recomendados

| Provedor | PostgreSQL | Preço | Recomendação |
|----------|------------|-------|--------------|
| **Supabase** | Managed | Free tier | ⭐ Melhor para começar |
| **Railway** | Managed | $5/mês | Simples, integrado |
| **Render** | Managed | Free tier | Bom free tier |
| **Neon** | Serverless | Free tier | Serverless, escala bem |
| **AWS RDS** | Managed | ~$15/mês | Enterprise |

---

## 2. Setup do PostgreSQL

### Opção A: Supabase (Recomendado)

```bash
# 1. Crie conta em supabase.com
# 2. Crie novo projeto
# 3. Copie a connection string de Settings > Database

# Formato da URL:
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT].supabase.co:5432/postgres
```

### Opção B: Railway

```bash
# 1. railway.app → New Project → PostgreSQL
# 2. Copie DATABASE_URL das variáveis
```

### Opção C: Docker Local

```bash
# docker-compose.yml
version: '3.8'
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: multiagentes
      POSTGRES_PASSWORD: senha_segura_aqui
      POSTGRES_DB: multiagentes
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

```bash
docker-compose up -d
# DATABASE_URL=postgresql://multiagentes:senha_segura_aqui@localhost:5432/multiagentes
```

---

## 3. Configuração do .env

```bash
# Copie o exemplo
cp .env.example .env

# Edite com suas credenciais
```

```env
# =============================================================================
# PRODUÇÃO
# =============================================================================
ENVIRONMENT=production
DEBUG=false

# Database (sua URL do provedor)
DATABASE_URL=postgresql://user:password@host:5432/database?sslmode=require

# JWT (GERE UMA NOVA!)
JWT_SECRET_KEY=gere_com_openssl_rand_hex_64

# API Key
ANTHROPIC_API_KEY=sk-ant-...

# CORS (seu domínio frontend)
CORS_ORIGINS=["https://app.seudominio.com"]

# Stripe (opcional, para billing)
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Sentry (opcional, para erros)
SENTRY_DSN=https://...@sentry.io/...
```

### Gerar JWT Secret Seguro

```bash
# Linux/Mac
openssl rand -hex 64

# PowerShell
[System.BitConverter]::ToString((1..64 | ForEach-Object { Get-Random -Maximum 256 })).Replace('-','').ToLower()

# Python
python -c "import secrets; print(secrets.token_hex(64))"
```

---

## 4. Executar Migrações

```bash
cd backend

# Instalar dependências
pip install -r requirements.txt

# Verificar conexão
python -c "from database.connection import check_database_health; print(check_database_health())"

# Aplicar migrações
alembic upgrade head

# Verificar tabelas criadas
alembic current
```

### Output esperado:

```
INFO  [alembic.runtime.migration] Running upgrade  -> 001_initial
INFO  [alembic.runtime.migration] Running upgrade 001_initial -> 002_rls
```

---

## 5. Aplicar Row-Level Security

```bash
# Conectar ao PostgreSQL
psql $DATABASE_URL

# Verificar RLS ativo
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public';

# Deve mostrar:
#  tablename       | rowsecurity
# -----------------+-------------
#  organizations   | f
#  users           | t
#  analyses        | t
#  agent_outputs   | t
#  refresh_tokens  | t
```

---

## 6. Criar Usuário Admin

```bash
cd backend

python scripts/setup.py \
  --admin-email admin@suaempresa.com \
  --admin-password SenhaSegura123! \
  --org-name "Sua Empresa"
```

---

## 7. Deploy da API

### Opção A: Railway / Render

```bash
# Procfile
web: uvicorn backend.app:app --host 0.0.0.0 --port $PORT
```

### Opção B: Docker

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instala dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia código
COPY . .

# Expõe porta
EXPOSE 8000

# Comando de inicialização
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# Build e run
docker build -t multiagentes-api .
docker run -p 8000:8000 --env-file .env multiagentes-api
```

### Opção C: Fly.io

```toml
# fly.toml
app = "multiagentes-api"
primary_region = "gru"  # São Paulo

[build]
  dockerfile = "Dockerfile"

[env]
  PORT = "8000"

[http_service]
  internal_port = 8000
  force_https = true

[[services.ports]]
  port = 443
  handlers = ["tls", "http"]
```

```bash
fly launch
fly secrets set DATABASE_URL="..." JWT_SECRET_KEY="..."
fly deploy
```

---

## 8. Verificação Pós-Deploy

### Health Check

```bash
curl https://sua-api.com/health
```

Resposta esperada:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "production",
  "checks": {
    "database": "healthy",
    "cache": "healthy (memory)"
  }
}
```

### Teste de Registro

```bash
curl -X POST https://sua-api.com/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teste@exemplo.com",
    "password": "Senha123!",
    "organization_name": "Teste"
  }'
```

---

## 9. Monitoramento

### Logs

```bash
# Railway
railway logs

# Fly.io
fly logs

# Docker
docker logs -f container_id
```

### Métricas do Pool

```bash
curl https://sua-api.com/health | jq '.checks.database'
```

---

## 10. Backup

### Supabase
- Backups automáticos diários
- Point-in-time recovery no plano Pro

### Manual

```bash
# Backup
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql

# Restore
psql $DATABASE_URL < backup_20260206.sql
```

---

## 11. Troubleshooting

### Erro: Connection refused

```bash
# Verificar se DATABASE_URL está correta
echo $DATABASE_URL

# Testar conexão
psql $DATABASE_URL -c "SELECT 1"
```

### Erro: SSL required

```bash
# Adicionar sslmode na URL
DATABASE_URL=postgresql://...?sslmode=require
```

### Erro: Too many connections

```bash
# Reduzir pool size no config.py
DATABASE_POOL_SIZE=3
DATABASE_MAX_OVERFLOW=5
```

### Erro: Migration failed

```bash
# Ver status atual
alembic current

# Ver histórico
alembic history

# Rollback se necessário
alembic downgrade -1
```

---

## 12. Checklist de Produção

- [ ] PostgreSQL configurado e acessível
- [ ] `DATABASE_URL` com `?sslmode=require`
- [ ] `JWT_SECRET_KEY` com 64+ caracteres
- [ ] `ENVIRONMENT=production`
- [ ] `DEBUG=false`
- [ ] `CORS_ORIGINS` com domínios reais (sem `*`)
- [ ] Migrações aplicadas (`alembic upgrade head`)
- [ ] RLS verificado (`rowsecurity = t`)
- [ ] Health check respondendo 200
- [ ] HTTPS configurado
- [ ] Backups automáticos ativos
- [ ] Logs e alertas configurados
