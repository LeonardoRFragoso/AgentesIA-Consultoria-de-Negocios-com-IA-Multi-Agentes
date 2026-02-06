# ARQUITETURA SAAS - CONSULTOR EXECUTIVO MULTI-AGENTES

## 1️⃣ VISÃO GERAL DA ARQUITETURA

```
┌─────────────────────────────────────────────────────────┐
│ CLIENTS (Apresentação)                                  │
├─────────────────────────────────────────────────────────┤
│ - Streamlit UI (Web)                                    │
│ - API REST Consumers                                    │
│ - Mobile (futuro)                                       │
└─────────────────────────────────────────────────────────┘
                            ↓ HTTP/REST
┌─────────────────────────────────────────────────────────┐
│ API GATEWAY / BACKEND SAAS (FastAPI)                    │
├─────────────────────────────────────────────────────────┤
│ - Autenticação (JWT)                                    │
│ - Tenant Resolution                                     │
│ - Rate Limiting                                         │
│ - Billing Control                                       │
│ - Request/Response Transformation                       │
└─────────────────────────────────────────────────────────┘
                            ↓ Python Import
┌─────────────────────────────────────────────────────────┐
│ CORE ENGINE (Lógica de Negócio)                         │
├─────────────────────────────────────────────────────────┤
│ - BusinessOrchestrator                                  │
│ - Agents (Analyst, Commercial, Financial, etc)         │
│ - Conflict Detection & Resolution                       │
│ - Meeting Simulation                                    │
│ - Executive Artifacts                                   │
│ - NO knowledge of users/tenants/billing                 │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│ INFRASTRUCTURE (Dados e Externos)                       │
├─────────────────────────────────────────────────────────┤
│ - Persistence (SQLite/PostgreSQL)                       │
│ - LLM Providers (Anthropic)                             │
│ - Stripe (Billing)                                      │
│ - Logging & Monitoring                                  │
└─────────────────────────────────────────────────────────┘
```

## 2️⃣ SEPARAÇÃO DE RESPONSABILIDADES

### Core Engine
- ✅ Análise multi-agente
- ✅ Detecção de conflitos
- ✅ Reunião executiva
- ✅ Exportação
- ❌ Conhecimento de usuários
- ❌ Conhecimento de billing
- ❌ Conhecimento de tenants

### Backend SaaS (FastAPI)
- ✅ Autenticação (JWT)
- ✅ Tenant resolution
- ✅ Rate limiting
- ✅ Billing check
- ✅ Request/Response transformation
- ❌ Lógica de decisão

### Clients (Streamlit/Web)
- ✅ Apresentação
- ✅ Coleta de input
- ✅ Armazenamento de token
- ❌ Lógica de negócio

---

## 3️⃣ AUTENTICAÇÃO (JWT)

### Fluxo de Login

```
1. Cliente submete email + senha
   ↓
2. Backend valida credenciais
   ↓
3. Backend gera JWT (access_token + refresh_token)
   ↓
4. Cliente armazena tokens localmente
   ↓
5. Cliente envia access_token em cada requisição
   ↓
6. Middleware valida token
   ↓
7. Se expirado, cliente usa refresh_token para renovar
```

### Estrutura do JWT

**Access Token** (15 minutos):
```json
{
    "sub": "user_id",
    "email": "user@example.com",
    "tenant_id": "org_123",
    "exp": 1707090900,
    "iat": 1707090300,
    "type": "access"
}
```

**Refresh Token** (30 dias):
```json
{
    "sub": "user_id",
    "exp": 1709682900,
    "iat": 1707090300,
    "type": "refresh"
}
```

### Proteção de Endpoints

```
GET /api/v1/executions
  ↓
Middleware: Valida JWT
  ↓
Middleware: Extrai tenant_id do token
  ↓
Handler: Retorna execuções do tenant
```

---

## 4️⃣ MULTI-TENANT

### Modelo de Dados

```
User
├─ user_id (PK)
├─ email
├─ password_hash
├─ tenant_id (FK)
└─ created_at

Organization (Tenant)
├─ tenant_id (PK)
├─ name
├─ plan (free, pro, enterprise)
├─ billing_status (active, past_due, cancelled)
└─ created_at

Execution
├─ execution_id (PK)
├─ tenant_id (FK) ← ISOLAMENTO
├─ user_id (FK)
├─ problem_description
├─ results
├─ created_at
└─ ...
```

### Estratégia: Shared DB + tenant_id

**Por quê**:
- ✅ Simples de implementar
- ✅ Fácil de escalar
- ✅ Custo baixo
- ✅ Backup centralizado

**Isolamento**:
- Todas as queries filtram por `tenant_id`
- Índices em `(tenant_id, field)`
- Middleware injeta `tenant_id` em cada request

---

## 5️⃣ BILLING

### Planos

| Plano | Execuções/mês | Preço | Limite Justo |
|-------|---------------|-------|--------------|
| **Free** | 10 | $0 | 10 análises |
| **Pro** | Ilimitado | $99/mês | 100K tokens/dia |
| **Enterprise** | Ilimitado | Custom | Sem limite |

### Métrica de Cobrança

**Primária**: Execuções (análises completas)
**Secundária**: Tokens (para limite justo)

### Verificação Antes de Executar

```python
if tenant.plan == "free":
    if tenant.executions_this_month >= 10:
        return {"error": "Limite atingido. Upgrade para Pro"}

if tenant.plan == "pro":
    if tenant.tokens_today >= 100000:
        return {"error": "Limite diário de tokens atingido"}
```

### Integração com Stripe

```
1. Usuário seleciona plano
   ↓
2. Backend cria Stripe Checkout Session
   ↓
3. Cliente é redirecionado para Stripe
   ↓
4. Stripe envia webhook (payment_intent.succeeded)
   ↓
5. Backend atualiza tenant.plan
   ↓
6. Usuário tem acesso
```

---

## 6️⃣ API PÚBLICA REST

### Endpoints

```http
# Autenticação
POST   /api/v1/auth/register
POST   /api/v1/auth/login
POST   /api/v1/auth/refresh
POST   /api/v1/auth/logout

# Usuário
GET    /api/v1/me
PUT    /api/v1/me

# Execuções
POST   /api/v1/executions          # Criar análise
GET    /api/v1/executions          # Listar análises
GET    /api/v1/executions/{id}     # Detalhe
DELETE /api/v1/executions/{id}     # Deletar

# Exportação
POST   /api/v1/executions/{id}/export  # Gerar export
GET    /api/v1/executions/{id}/export  # Baixar

# Billing
GET    /api/v1/billing/status      # Status da assinatura
POST   /api/v1/billing/checkout    # Iniciar checkout
GET    /api/v1/billing/usage       # Uso atual
```

### Exemplo: POST /api/v1/executions

**Request**:
```json
{
    "problem_description": "Vendas caíram 20%...",
    "business_type": "SaaS",
    "analysis_depth": "Padrão"
}
```

**Response (201 Created)**:
```json
{
    "execution_id": "exec_123",
    "status": "running",
    "created_at": "2024-02-05T20:30:00Z",
    "estimated_duration_seconds": 30
}
```

**Response (402 Payment Required)**:
```json
{
    "error": "Limite de execuções atingido",
    "plan": "free",
    "executions_used": 10,
    "executions_limit": 10,
    "upgrade_url": "https://..."
}
```

---

## 7️⃣ STREAMLIT COMO CLIENTE DA API

### Fluxo de Autenticação

```python
# 1. Login
response = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    json={"email": "user@example.com", "password": "..."}
)
tokens = response.json()
st.session_state.access_token = tokens["access_token"]
st.session_state.refresh_token = tokens["refresh_token"]

# 2. Requisição com Token
headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
response = requests.get(
    "http://localhost:8000/api/v1/executions",
    headers=headers
)

# 3. Renovação de Token
if response.status_code == 401:
    refresh_response = requests.post(
        "http://localhost:8000/api/v1/auth/refresh",
        json={"refresh_token": st.session_state.refresh_token}
    )
    st.session_state.access_token = refresh_response.json()["access_token"]
```

### Armazenamento de Token

```python
# Em st.session_state (memória da sessão)
st.session_state.access_token = "..."
st.session_state.refresh_token = "..."

# Em produção: considerar armazenamento seguro
# - localStorage (web)
# - Keychain (mobile)
# - Secure storage (desktop)
```

---

## 8️⃣ SEGURANÇA E LIMITES

### Rate Limiting

```python
# Por tenant
max_requests_per_minute = 60

# Por plano
free_plan_max_concurrent = 1
pro_plan_max_concurrent = 5
```

### Isolamento de Dados

```python
# Sempre filtrar por tenant_id
executions = db.query(Execution).filter(
    Execution.tenant_id == current_tenant.tenant_id
).all()
```

### Proteção de Custos

```python
# Bloquear antes de chamar LLM
if not billing_allowed(tenant):
    raise HTTPException(status_code=402)

# Registrar uso
record_execution(tenant_id, tokens_used)
```

### Logs por Tenant

```python
logger.info(
    "Execution started",
    execution_id=execution_id,
    tenant_id=tenant_id,  # ← Sempre incluir
    user_id=user_id
)
```

---

## 9️⃣ DECISÕES TÉCNICAS

### Tomadas

| Decisão | Justificativa | Trade-off |
|---------|---------------|-----------|
| **JWT** | Stateless, escalável | Sem revogação imediata |
| **Shared DB + tenant_id** | Simples, barato | Requer disciplina |
| **FastAPI** | Moderno, rápido | Menos maduro que Django |
| **Stripe** | Padrão da indústria | Custo de integração |
| **Free tier** | Aquisição de usuários | Suporte a free users |

### Fora Propositalmente

- ❌ OAuth social (Fase 2)
- ❌ RBAC avançado (Fase 2)
- ❌ SSO corporativo (Fase 3)
- ❌ Audit logs (Fase 2)
- ❌ API keys (Fase 2)

---

## 🔟 PRÓXIMOS PASSOS

### Fase 2 (1-2 meses)
- [ ] Implementar persistência real (PostgreSQL)
- [ ] Integração com Stripe (webhooks)
- [ ] Rate limiting real
- [ ] Audit logs
- [ ] API keys para integração

### Fase 3 (2-3 meses)
- [ ] OAuth social
- [ ] RBAC avançado
- [ ] SSO corporativo
- [ ] Compliance (GDPR, SOC2)
- [ ] Monitoring e alertas

---

## CONCLUSÃO

Arquitetura SaaS:
- ✅ Core isolado (sem conhecimento de SaaS)
- ✅ API clara e bem definida
- ✅ Autenticação segura (JWT)
- ✅ Multi-tenant por isolamento lógico
- ✅ Billing integrado (sem bloquear core)
- ✅ Pronta para escalar
