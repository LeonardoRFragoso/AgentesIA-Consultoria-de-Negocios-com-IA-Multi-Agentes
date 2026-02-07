# 🔒 Security Hardening - Backend SaaS

## Vulnerabilidades Corrigidas

### 1. CORS Permissivo ❌ → ✅

**ANTES (Vulnerável):**
```python
allow_origins=["*"]  # Permitia qualquer origem
```

**DEPOIS (Seguro):**
```python
# backend/app.py
def get_cors_origins():
    origins = settings.CORS_ORIGINS
    if settings.is_production():
        if "*" in origins:
            origins = []  # Bloqueia wildcard em produção
    return [o for o in origins if o != "*"]

allow_origins=get_cors_origins()  # Apenas origens explícitas
```

**Arquivo:** `backend/app.py` linhas 92-106

---

### 2. Sem Rate Limiting ❌ → ✅

**ANTES:**
- Nenhum limite de requests por IP
- Sem proteção contra brute force

**DEPOIS:**
```python
# backend/middleware/security.py
class SecurityConfig:
    RATE_LIMIT_IP_PER_MINUTE: int = 60
    RATE_LIMIT_AUTH_PER_MINUTE: int = 10  # Mais restritivo para auth
    RATE_LIMIT_USER_PER_MINUTE: int = 120
    LOGIN_ATTEMPTS_BEFORE_BLOCK: int = 10
    LOGIN_BLOCK_DURATION: int = 900  # 15 min
```

**Arquivo:** `backend/middleware/security.py` linhas 35-90

---

### 3. Validação de Input Fraca ❌ → ✅

**ANTES:**
```python
password: str = Field(...)  # Sem validação de força
organization_name: str  # Sem sanitização
```

**DEPOIS:**
```python
# backend/api/schemas.py
@field_validator("password")
def validate_password_strength(cls, v):
    if not re.search(r"[a-zA-Z]", v):
        raise ValueError("Senha deve conter letra")
    if not re.search(r"\d", v):
        raise ValueError("Senha deve conter número")
    return v

@field_validator("organization_name", "name")
def sanitize_text(cls, v):
    v = validate_no_script_tags(v)  # Anti-XSS
    return v
```

**Arquivo:** `backend/api/schemas.py` linhas 23-64, 107-127

---

### 4. Sem Proteção Contra Abuso ❌ → ✅

**ANTES:**
- Sem validação de Content-Type
- Sem limite de tamanho de payload
- Sem detecção de padrões maliciosos

**DEPOIS:**
```python
# backend/middleware/security.py
class SecurityConfig:
    MAX_BODY_SIZE: int = 1_048_576  # 1MB
    MAX_JSON_DEPTH: int = 10
    BLOCKED_USER_AGENTS: list = [
        r"scrapy", r"bot", r"spider", r"crawler"
    ]
```

**Arquivo:** `backend/middleware/security.py` linhas 95-125

---

### 5. Headers de Segurança Incompletos ❌ → ✅

**ANTES:**
- Apenas headers básicos

**DEPOIS:**
```python
# SecurityMiddleware adiciona:
headers = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Cache-Control": "no-store, no-cache, must-revalidate, private",
    "Content-Security-Policy": "default-src 'self'; frame-ancestors 'none'",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
}
```

**Arquivo:** `backend/middleware/security.py` linhas 380-410

---

### 6. Healthcheck Básico ❌ → ✅

**ANTES:**
```python
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

**DEPOIS:**
```python
# backend/app.py
@app.get("/health")
async def health_check():
    checks = {"database": "unknown", "cache": "unknown"}
    # Verifica database
    # Verifica cache
    return {
        "status": "healthy/unhealthy",
        "checks": checks,
        "version": "...",
    }

@app.get("/health/live")   # Liveness probe
@app.get("/health/ready")  # Readiness probe
```

**Arquivo:** `backend/app.py` linhas 177-249

---

## Limites Configuráveis

Todos os limites estão em **`backend/middleware/security.py`** na classe `SecurityConfig`:

| Configuração | Valor Default | Descrição |
|--------------|---------------|-----------|
| `RATE_LIMIT_IP_PER_MINUTE` | 60 | Requests por IP/minuto |
| `RATE_LIMIT_AUTH_PER_MINUTE` | 10 | Requests em /auth por IP/minuto |
| `RATE_LIMIT_USER_PER_MINUTE` | 120 | Requests por usuário autenticado |
| `RATE_LIMIT_ORG_PER_HOUR` | 1000 | Requests por organização/hora |
| `MAX_BODY_SIZE` | 1MB | Tamanho máximo do body |
| `MAX_STRING_LENGTH` | 50000 | Tamanho máximo de strings |
| `MAX_JSON_DEPTH` | 10 | Profundidade máxima de JSON |
| `LOGIN_ATTEMPTS_BEFORE_DELAY` | 3 | Tentativas antes de slowdown |
| `LOGIN_DELAY_SECONDS` | 2 | Delay após muitas tentativas |
| `LOGIN_ATTEMPTS_BEFORE_BLOCK` | 10 | Tentativas antes de bloqueio |
| `LOGIN_BLOCK_DURATION` | 900s | Duração do bloqueio (15 min) |

### Personalização

Para alterar limites, edite `backend/middleware/security.py`:

```python
class SecurityConfig:
    RATE_LIMIT_IP_PER_MINUTE: int = 100  # Aumentado
    LOGIN_ATTEMPTS_BEFORE_BLOCK: int = 5  # Mais restritivo
```

Ou via subclasse:

```python
class MySecurityConfig(SecurityConfig):
    RATE_LIMIT_IP_PER_MINUTE = 200

app.add_middleware(SecurityMiddleware, config=MySecurityConfig())
```

---

## Arquivos Alterados

| Arquivo | Mudança |
|---------|---------|
| `backend/middleware/security.py` | **NOVO** - Middleware de segurança completo |
| `backend/middleware/__init__.py` | Exports atualizados |
| `backend/app.py` | CORS restritivo, SecurityMiddleware, healthcheck |
| `backend/api/schemas.py` | Validação rigorosa de inputs |

---

## Testes

### 1. Rate Limiting

```bash
# Teste de rate limit (deve bloquear após 60 requests)
for i in {1..70}; do 
  curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8000/health
done
# Últimos devem retornar 429
```

### 2. CORS

```bash
# Origem não permitida (deve falhar)
curl -H "Origin: https://malicious.com" \
     -H "Access-Control-Request-Method: GET" \
     -X OPTIONS http://localhost:8000/api/v1/auth/me

# Origem permitida (deve funcionar)
curl -H "Origin: http://localhost:3000" \
     -H "Access-Control-Request-Method: GET" \
     -X OPTIONS http://localhost:8000/api/v1/auth/me
```

### 3. Validação de Input

```bash
# Password fraca (deve falhar)
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@test.com", "password": "weak", "organization_name": "Test"}'

# XSS attempt (deve falhar)
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@test.com", "password": "Strong123!", "organization_name": "<script>alert(1)</script>"}'
```

### 4. Healthcheck

```bash
curl http://localhost:8000/health
curl http://localhost:8000/health/live
curl http://localhost:8000/health/ready
```

---

## Checklist de Produção

- [ ] Configurar `CORS_ORIGINS` com domínios reais
- [ ] Configurar `JWT_SECRET_KEY` forte (64+ chars)
- [ ] Ativar HTTPS (HSTS será adicionado automaticamente)
- [ ] Configurar Redis para rate limiting distribuído
- [ ] Monitorar logs de segurança
- [ ] Configurar alertas para bloqueios de IP
