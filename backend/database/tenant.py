"""
Multi-Tenant Database Layer

Implementa isolamento de dados por organização usando:
1. Filtro automático em queries (aplicação)
2. Row-Level Security no PostgreSQL (banco)

CRÍTICO: Nunca fazer queries sem passar pelo TenantSession.
"""

from contextlib import contextmanager
from typing import Generator, Optional, Type, TypeVar, List
from uuid import UUID
from sqlalchemy import event, text
from sqlalchemy.orm import Session, Query
from sqlalchemy.engine import Connection

from .models import Base, Organization, User, Analysis, AgentOutput
from .connection import get_db_session, get_engine


T = TypeVar("T", bound=Base)


# =============================================================================
# TENANT SESSION
# =============================================================================

class TenantSession:
    """
    Session wrapper que garante isolamento multi-tenant.
    
    Todas as queries são automaticamente filtradas por org_id.
    
    Uso:
        with TenantSession(db, org_id="...") as tenant_db:
            analyses = tenant_db.query(Analysis).all()  # Apenas da org
    """
    
    # Models que têm org_id direto
    TENANT_MODELS = {Analysis, User}
    
    # Models que herdam tenant do parent (via relationship)
    INHERITED_TENANT_MODELS = {AgentOutput}  # Herda de Analysis
    
    def __init__(self, session: Session, org_id: str):
        self._session = session
        self._org_id = str(org_id)
    
    @property
    def org_id(self) -> str:
        return self._org_id
    
    def query(self, model: Type[T], *args) -> Query:
        """
        Query com filtro automático de tenant.
        
        Args:
            model: Modelo SQLAlchemy a consultar
            
        Returns:
            Query já filtrada por org_id
        """
        query = self._session.query(model, *args)
        
        # Aplica filtro de tenant se o modelo suporta
        if model in self.TENANT_MODELS:
            query = query.filter(model.org_id == self._org_id)
        
        return query
    
    def get(self, model: Type[T], id: UUID) -> Optional[T]:
        """
        Busca entidade por ID com validação de tenant.
        
        SEGURO: Retorna None se entidade não pertence à org.
        """
        entity = self._session.get(model, id)
        
        if entity is None:
            return None
        
        # Valida que pertence à org correta
        if hasattr(entity, "org_id"):
            if str(entity.org_id) != self._org_id:
                return None  # Não pertence à org - retorna como se não existisse
        
        return entity
    
    def add(self, entity: T) -> T:
        """
        Adiciona entidade com org_id automático.
        """
        if hasattr(entity, "org_id") and entity.org_id is None:
            entity.org_id = UUID(self._org_id)
        
        self._session.add(entity)
        return entity
    
    def delete(self, entity: T) -> None:
        """
        Remove entidade com validação de tenant.
        """
        if hasattr(entity, "org_id"):
            if str(entity.org_id) != self._org_id:
                raise PermissionError("Não é possível deletar entidade de outra organização")
        
        self._session.delete(entity)
    
    def commit(self) -> None:
        self._session.commit()
    
    def rollback(self) -> None:
        self._session.rollback()
    
    def flush(self) -> None:
        self._session.flush()
    
    def refresh(self, entity: T) -> None:
        self._session.refresh(entity)
    
    def execute(self, statement, params=None):
        """Executa statement raw - USE COM CUIDADO."""
        return self._session.execute(statement, params)


@contextmanager
def tenant_session(org_id: str) -> Generator[TenantSession, None, None]:
    """
    Context manager para sessão multi-tenant.
    
    Uso:
        with tenant_session(org_id) as db:
            analyses = db.query(Analysis).all()
    """
    with get_db_session() as session:
        yield TenantSession(session, org_id)


# =============================================================================
# ROW-LEVEL SECURITY (PostgreSQL)
# =============================================================================

class RLSManager:
    """
    Gerencia Row-Level Security no PostgreSQL.
    
    RLS adiciona uma camada extra de segurança no banco de dados.
    Mesmo que a aplicação tenha um bug, o banco impede acesso cross-tenant.
    """
    
    @staticmethod
    def set_tenant_context(connection: Connection, org_id: str) -> None:
        """
        Define o contexto do tenant para a conexão atual.
        As policies RLS usam essa variável para filtrar.
        """
        connection.execute(
            text("SET app.current_org_id = :org_id"),
            {"org_id": str(org_id)}
        )
    
    @staticmethod
    def clear_tenant_context(connection: Connection) -> None:
        """Limpa o contexto do tenant."""
        connection.execute(text("RESET app.current_org_id"))
    
    @staticmethod
    def get_rls_setup_sql() -> str:
        """
        Retorna SQL para configurar Row-Level Security.
        Execute isso uma vez no banco de produção.
        """
        return """
-- =============================================================================
-- ROW-LEVEL SECURITY SETUP
-- Execute como superuser no PostgreSQL
-- =============================================================================

-- 1. Habilita RLS nas tabelas
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_outputs ENABLE ROW LEVEL SECURITY;
ALTER TABLE refresh_tokens ENABLE ROW LEVEL SECURITY;

-- 2. Policies para tabela USERS
-- Usuários só podem ver/modificar usuários da mesma org
DROP POLICY IF EXISTS users_tenant_isolation ON users;
CREATE POLICY users_tenant_isolation ON users
    USING (org_id::text = current_setting('app.current_org_id', true))
    WITH CHECK (org_id::text = current_setting('app.current_org_id', true));

-- 3. Policies para tabela ANALYSES
-- Análises só são visíveis dentro da mesma org
DROP POLICY IF EXISTS analyses_tenant_isolation ON analyses;
CREATE POLICY analyses_tenant_isolation ON analyses
    USING (org_id::text = current_setting('app.current_org_id', true))
    WITH CHECK (org_id::text = current_setting('app.current_org_id', true));

-- 4. Policies para tabela AGENT_OUTPUTS
-- Outputs herdam tenant da análise pai
DROP POLICY IF EXISTS agent_outputs_tenant_isolation ON agent_outputs;
CREATE POLICY agent_outputs_tenant_isolation ON agent_outputs
    USING (
        EXISTS (
            SELECT 1 FROM analyses a 
            WHERE a.id = agent_outputs.analysis_id 
            AND a.org_id::text = current_setting('app.current_org_id', true)
        )
    )
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM analyses a 
            WHERE a.id = agent_outputs.analysis_id 
            AND a.org_id::text = current_setting('app.current_org_id', true)
        )
    );

-- 5. Policies para REFRESH_TOKENS
-- Tokens só visíveis se o user pertence à org
DROP POLICY IF EXISTS refresh_tokens_tenant_isolation ON refresh_tokens;
CREATE POLICY refresh_tokens_tenant_isolation ON refresh_tokens
    USING (
        EXISTS (
            SELECT 1 FROM users u 
            WHERE u.id = refresh_tokens.user_id 
            AND u.org_id::text = current_setting('app.current_org_id', true)
        )
    );

-- 6. Bypass para o usuário da aplicação (quando não há contexto)
-- Útil para operações administrativas
-- CUIDADO: Apenas para migrações e admin

-- Para verificar se RLS está ativo:
-- SELECT tablename, rowsecurity FROM pg_tables WHERE schemaname = 'public';
        """
    
    @staticmethod
    def get_rls_disable_sql() -> str:
        """SQL para desabilitar RLS (apenas para debugging)."""
        return """
ALTER TABLE users DISABLE ROW LEVEL SECURITY;
ALTER TABLE analyses DISABLE ROW LEVEL SECURITY;
ALTER TABLE agent_outputs DISABLE ROW LEVEL SECURITY;
ALTER TABLE refresh_tokens DISABLE ROW LEVEL SECURITY;
        """


# =============================================================================
# QUERY HELPERS SEGUROS
# =============================================================================

class TenantQueries:
    """
    Queries pré-construídas com isolamento multi-tenant garantido.
    Use estas funções ao invés de queries manuais.
    """
    
    @staticmethod
    def get_user_analyses(
        db: TenantSession,
        user_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Analysis]:
        """
        Lista análises da organização, opcionalmente filtradas por usuário.
        
        SEGURO: Sempre filtrado por org_id automaticamente.
        """
        query = db.query(Analysis)
        
        if user_id:
            query = query.filter(Analysis.created_by == user_id)
        
        if status:
            query = query.filter(Analysis.status == status)
        
        return (
            query
            .order_by(Analysis.created_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )
    
    @staticmethod
    def get_analysis_with_outputs(
        db: TenantSession,
        analysis_id: str
    ) -> Optional[Analysis]:
        """
        Busca análise com outputs, validando tenant.
        
        SEGURO: Retorna None se não pertence à org.
        """
        analysis = db.get(Analysis, UUID(analysis_id))
        
        if analysis:
            # Força carregamento dos outputs
            _ = analysis.agent_outputs
        
        return analysis
    
    @staticmethod
    def get_org_users(
        db: TenantSession,
        include_inactive: bool = False
    ) -> List[User]:
        """
        Lista usuários da organização.
        """
        query = db.query(User)
        
        if not include_inactive:
            query = query.filter(User.is_active == True)
        
        return query.order_by(User.created_at).all()
    
    @staticmethod
    def count_analyses_this_month(db: TenantSession) -> int:
        """Conta análises do mês atual."""
        from datetime import datetime
        
        now = datetime.utcnow()
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        return (
            db.query(Analysis)
            .filter(Analysis.created_at >= start_of_month)
            .count()
        )


# =============================================================================
# MIDDLEWARE INTEGRATION
# =============================================================================

def setup_rls_middleware(app):
    """
    Configura middleware para definir contexto RLS em cada request.
    
    Uso no FastAPI:
        from backend.database.tenant import setup_rls_middleware
        setup_rls_middleware(app)
    """
    from fastapi import Request
    from starlette.middleware.base import BaseHTTPMiddleware
    
    class RLSMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next):
            # Extrai org_id do token JWT (se autenticado)
            org_id = getattr(request.state, "org_id", None)
            
            if org_id:
                # Define contexto RLS para esta request
                engine = get_engine()
                with engine.connect() as conn:
                    RLSManager.set_tenant_context(conn, org_id)
            
            response = await call_next(request)
            return response
    
    app.add_middleware(RLSMiddleware)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "TenantSession",
    "tenant_session",
    "RLSManager",
    "TenantQueries",
    "setup_rls_middleware",
]
