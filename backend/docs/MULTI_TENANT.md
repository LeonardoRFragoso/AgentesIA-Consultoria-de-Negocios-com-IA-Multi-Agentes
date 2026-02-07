# 🏢 Multi-Tenant Architecture

## Visão Geral

O sistema implementa isolamento multi-tenant em **duas camadas**:

1. **Aplicação**: `TenantSession` filtra queries automaticamente
2. **Banco de Dados**: Row-Level Security (PostgreSQL) como backup

## Estrutura de Dados

```
Organization (Tenant)
├── Users (org_id)
├── Analyses (org_id)
│   └── AgentOutputs (herda de Analysis)
└── RefreshTokens (via User)
```

---

## 1. Models com org_id

```python
# backend/database/models.py

class Organization(Base):
    """Tenant principal - todas as entidades pertencem a uma org."""
    __tablename__ = "organizations"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    plan = Column(SQLEnum(PlanType), default=PlanType.FREE)
    # ...

class User(Base):
    """Usuário pertence a uma organização."""
    __tablename__ = "users"
    
    id = Column(GUID(), primary_key=True)
    org_id = Column(GUID(), ForeignKey("organizations.id"), nullable=False)  # 👈 CRÍTICO
    # ...

class Analysis(Base):
    """Análise pertence a uma organização."""
    __tablename__ = "analyses"
    
    id = Column(GUID(), primary_key=True)
    org_id = Column(GUID(), ForeignKey("organizations.id"), nullable=False)  # 👈 CRÍTICO
    created_by = Column(GUID(), ForeignKey("users.id"), nullable=False)
    # ...
```

---

## 2. TenantSession (Camada de Aplicação)

### Uso Básico

```python
from backend.database import tenant_session, Analysis

# ✅ SEGURO: Sempre usar tenant_session
with tenant_session(org_id="uuid-da-org") as db:
    # Query automaticamente filtrada por org_id
    analyses = db.query(Analysis).all()
    
    # Apenas análises desta org são retornadas
    for a in analyses:
        print(a.problem_description)
```

### Adicionar Entidade

```python
with tenant_session(org_id) as db:
    # org_id é definido automaticamente
    analysis = Analysis(
        problem_description="...",
        business_type="B2B",
        created_by=user_id
    )
    db.add(analysis)  # org_id preenchido automaticamente
    db.commit()
```

### Buscar por ID (com validação)

```python
with tenant_session(org_id) as db:
    # ✅ SEGURO: Retorna None se não pertence à org
    analysis = db.get(Analysis, analysis_id)
    
    if analysis is None:
        raise HTTPException(404, "Análise não encontrada")
```

### Deletar (com validação)

```python
with tenant_session(org_id) as db:
    analysis = db.get(Analysis, analysis_id)
    
    if analysis:
        db.delete(analysis)  # Valida org_id antes de deletar
        db.commit()
```

---

## 3. TenantQueries (Helpers Prontos)

```python
from backend.database import tenant_session, TenantQueries

with tenant_session(org_id) as db:
    # Listar análises com paginação
    analyses = TenantQueries.get_user_analyses(
        db,
        user_id=None,  # Todas da org
        status="completed",
        limit=20,
        offset=0
    )
    
    # Buscar análise com outputs
    analysis = TenantQueries.get_analysis_with_outputs(db, analysis_id)
    
    # Listar usuários da org
    users = TenantQueries.get_org_users(db, include_inactive=False)
    
    # Contar análises do mês
    count = TenantQueries.count_analyses_this_month(db)
```

---

## 4. Row-Level Security (PostgreSQL)

### Por que usar RLS?

RLS adiciona **proteção no banco de dados**. Mesmo que a aplicação tenha um bug, o PostgreSQL impede acesso cross-tenant.

### SQL das Policies

```sql
-- 1. Habilita RLS nas tabelas
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_outputs ENABLE ROW LEVEL SECURITY;
ALTER TABLE refresh_tokens ENABLE ROW LEVEL SECURITY;

-- 2. Policy para USERS
CREATE POLICY users_tenant_isolation ON users
    USING (org_id::text = current_setting('app.current_org_id', true))
    WITH CHECK (org_id::text = current_setting('app.current_org_id', true));

-- 3. Policy para ANALYSES
CREATE POLICY analyses_tenant_isolation ON analyses
    USING (org_id::text = current_setting('app.current_org_id', true))
    WITH CHECK (org_id::text = current_setting('app.current_org_id', true));

-- 4. Policy para AGENT_OUTPUTS (herda de Analysis)
CREATE POLICY agent_outputs_tenant_isolation ON agent_outputs
    USING (
        EXISTS (
            SELECT 1 FROM analyses a 
            WHERE a.id = agent_outputs.analysis_id 
            AND a.org_id::text = current_setting('app.current_org_id', true)
        )
    );

-- 5. Policy para REFRESH_TOKENS (herda de User)
CREATE POLICY refresh_tokens_tenant_isolation ON refresh_tokens
    USING (
        EXISTS (
            SELECT 1 FROM users u 
            WHERE u.id = refresh_tokens.user_id 
            AND u.org_id::text = current_setting('app.current_org_id', true)
        )
    );
```

### Definir Contexto RLS

```python
from backend.database import RLSManager

# Antes de cada request
with engine.connect() as conn:
    RLSManager.set_tenant_context(conn, org_id)
    
    # Agora todas as queries respeitam RLS
    result = conn.execute("SELECT * FROM analyses")
    # Apenas análises da org são retornadas
```

### Aplicar Migração

```bash
cd backend
alembic upgrade head
# Isso executa 002_row_level_security.py
```

---

## 5. Integração com FastAPI

### Middleware de Tenant

```python
# backend/security/auth.py

class TenantContext:
    def __init__(self, user_id, org_id, email, role, plan):
        self.user_id = user_id
        self.org_id = org_id
        self.email = email
        self.role = role
        self.plan = plan

async def get_tenant_context(
    current_user: TokenPayload = Depends(get_current_active_user)
) -> TenantContext:
    return TenantContext(
        user_id=current_user.sub,
        org_id=current_user.org_id,  # 👈 Extraído do JWT
        email=current_user.email,
        role=current_user.role,
        plan=current_user.plan
    )
```

### Uso em Endpoints

```python
from backend.security.auth import get_tenant_context, TenantContext
from backend.database import tenant_session, Analysis

@router.get("/analyses")
async def list_analyses(
    tenant: TenantContext = Depends(get_tenant_context)
):
    with tenant_session(tenant.org_id) as db:
        # ✅ SEGURO: Apenas análises desta org
        return db.query(Analysis).all()


@router.get("/analyses/{analysis_id}")
async def get_analysis(
    analysis_id: str,
    tenant: TenantContext = Depends(get_tenant_context)
):
    with tenant_session(tenant.org_id) as db:
        # ✅ SEGURO: Retorna None se não pertence à org
        analysis = db.get(Analysis, UUID(analysis_id))
        
        if not analysis:
            raise HTTPException(404, "Análise não encontrada")
        
        return analysis
```

---

## 6. ❌ O que NÃO fazer

### Query sem filtro de tenant

```python
# ❌ INSEGURO: Expõe dados de todas as orgs!
def get_all_analyses(db: Session):
    return db.query(Analysis).all()
```

### Usar ID sem validar org

```python
# ❌ INSEGURO: Usuário pode acessar análise de outra org!
@router.get("/analyses/{id}")
async def get_analysis(id: str, db: Session = Depends(get_db)):
    return db.query(Analysis).filter(Analysis.id == id).first()
```

### Confiar apenas na aplicação

```python
# ⚠️ RISCO: Se tiver bug na app, dados vazam
# SEMPRE use RLS como backup no PostgreSQL
```

---

## 7. Checklist de Segurança

- [ ] Todos os models críticos têm `org_id`
- [ ] Todas as queries usam `TenantSession`
- [ ] RLS habilitado no PostgreSQL
- [ ] Policies criadas para todas as tabelas
- [ ] `TenantContext` injetado em todos os endpoints
- [ ] Testes verificam isolamento cross-tenant

---

## 8. Testando Isolamento

```python
def test_tenant_isolation():
    """Verifica que org A não vê dados da org B."""
    
    # Cria duas orgs
    org_a = create_org("Org A")
    org_b = create_org("Org B")
    
    # Cria análise na org A
    with tenant_session(org_a.id) as db:
        analysis = Analysis(problem_description="Teste A")
        db.add(analysis)
        db.commit()
        analysis_id = analysis.id
    
    # Tenta acessar da org B
    with tenant_session(org_b.id) as db:
        # DEVE retornar None (não encontra)
        result = db.get(Analysis, analysis_id)
        assert result is None, "FALHA: Org B acessou dados da Org A!"
    
    # Acessa da org A (deve funcionar)
    with tenant_session(org_a.id) as db:
        result = db.get(Analysis, analysis_id)
        assert result is not None
```
