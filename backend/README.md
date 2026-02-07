# Backend SaaS - Consultor Executivo Multi-Agentes

API RESTful para o sistema de análise estratégica multi-agentes.

## 🏗️ Arquitetura

```
backend/
├── api/                    # Endpoints REST
│   ├── auth.py             # Autenticação
│   ├── analyses.py         # CRUD de análises
│   ├── billing.py          # Billing/Stripe
│   ├── users.py            # Gestão de usuários
│   └── schemas.py          # Pydantic models
├── database/               # SQLAlchemy
│   ├── models.py           # Models
│   └── connection.py       # Pool de conexões
├── security/               # Auth & Security
│   ├── password.py         # bcrypt
│   ├── jwt_handler.py      # JWT
│   └── auth.py             # Middlewares
├── services/               # Business logic
│   ├── user_service.py
│   ├── analysis_service.py
│   └── billing_service.py
├── middleware/             # Rate limiting, etc
├── migrations/             # Alembic
├── config.py               # Settings (pydantic)
└── app.py                  # FastAPI app
```

## 🚀 Quick Start

### 1. Instalar dependências

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configurar ambiente

```bash
cp ../.env.example ../.env
# Edite .env com suas credenciais
```

**Variáveis obrigatórias:**
- `ANTHROPIC_API_KEY` - Chave da API Anthropic
- `JWT_SECRET_KEY` - Gere com: `openssl rand -hex 32`
- `DATABASE_URL` - URL PostgreSQL

### 3. Inicializar banco de dados

```bash
# Opção 1: Script de setup
python scripts/setup.py

# Opção 2: Alembic migrations
alembic upgrade head
```

### 4. Iniciar servidor

```bash
uvicorn backend.app:app --reload
```

API disponível em: http://localhost:8000

## 📚 Endpoints

### Autenticação

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/v1/auth/register` | Registrar nova organização |
| POST | `/api/v1/auth/login` | Login |
| POST | `/api/v1/auth/refresh` | Renovar token |
| GET | `/api/v1/auth/me` | Dados do usuário atual |

### Análises

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/v1/analyses` | Criar análise |
| GET | `/api/v1/analyses` | Listar análises |
| GET | `/api/v1/analyses/{id}` | Detalhe de análise |
| DELETE | `/api/v1/analyses/{id}` | Deletar análise |
| POST | `/api/v1/analyses/{id}/export/{format}` | Exportar (pdf/pptx/markdown) |

### Billing

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/v1/billing/status` | Status de uso |
| POST | `/api/v1/billing/checkout/{plan}` | Criar checkout Stripe |
| GET | `/api/v1/billing/portal` | Portal de billing |

### Usuários

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/v1/users/team` | Listar membros |
| POST | `/api/v1/users/invite` | Convidar usuário |
| PATCH | `/api/v1/users/{id}/role` | Alterar role |
| DELETE | `/api/v1/users/{id}` | Remover usuário |

## 🔒 Segurança

- **JWT** com access tokens (15min) e refresh tokens (30 dias)
- **bcrypt** para hash de senhas
- **Rate limiting** por IP e por plano
- **CORS** restritivo por padrão
- **RLS** (Row-Level Security) para isolamento multi-tenant

## 🗃️ Database

PostgreSQL com SQLAlchemy 2.0.

### Migrações

```bash
# Criar nova migração
alembic revision --autogenerate -m "descrição"

# Aplicar migrações
alembic upgrade head

# Rollback
alembic downgrade -1
```

## 📊 Planos e Limites

| Feature | Free | Pro | Enterprise |
|---------|------|-----|------------|
| Análises/mês | 10 | Ilimitadas | Ilimitadas |
| Usuários | 1 | 5 | Ilimitados |
| Histórico | 7 dias | 90 dias | 365 dias |
| Exports | ❌ | ✅ | ✅ |
| API | ❌ | ❌ | ✅ |

## 🧪 Testes

```bash
pytest tests/ -v
```

## 📦 Deploy

### Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Variáveis de produção

```bash
ENVIRONMENT=production
DEBUG=false
JWT_SECRET_KEY=<chave-forte-64-chars>
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
CORS_ORIGINS=https://app.seudominio.com
STRIPE_SECRET_KEY=sk_live_...
SENTRY_DSN=https://...@sentry.io/...
```
