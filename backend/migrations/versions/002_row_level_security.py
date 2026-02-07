"""
Row-Level Security para Multi-Tenant

Revision ID: 002
Revises: 001
Create Date: 2026-02-06

CRÍTICO: Esta migração implementa isolamento no nível do banco de dados.
Mesmo que a aplicação tenha bugs, o PostgreSQL impede acesso cross-tenant.
"""

from alembic import op
import sqlalchemy as sa


# Revision identifiers
revision = '002_rls'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Habilita Row-Level Security e cria policies de isolamento.
    """
    
    # Verifica se é PostgreSQL (RLS não existe em SQLite)
    bind = op.get_bind()
    if bind.dialect.name != 'postgresql':
        print("AVISO: RLS só funciona em PostgreSQL. Pulando migração.")
        return
    
    # ==========================================================================
    # 1. HABILITA RLS NAS TABELAS
    # ==========================================================================
    
    op.execute("ALTER TABLE users ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE analyses ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE agent_outputs ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE refresh_tokens ENABLE ROW LEVEL SECURITY;")
    
    # ==========================================================================
    # 2. POLICY: USERS
    # Usuários só veem/modificam usuários da mesma organização
    # ==========================================================================
    
    op.execute("""
        CREATE POLICY users_tenant_isolation ON users
            USING (org_id::text = current_setting('app.current_org_id', true))
            WITH CHECK (org_id::text = current_setting('app.current_org_id', true));
    """)
    
    # ==========================================================================
    # 3. POLICY: ANALYSES
    # Análises isoladas por organização
    # ==========================================================================
    
    op.execute("""
        CREATE POLICY analyses_tenant_isolation ON analyses
            USING (org_id::text = current_setting('app.current_org_id', true))
            WITH CHECK (org_id::text = current_setting('app.current_org_id', true));
    """)
    
    # ==========================================================================
    # 4. POLICY: AGENT_OUTPUTS
    # Outputs herdam tenant da análise pai (sem org_id direto)
    # ==========================================================================
    
    op.execute("""
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
    """)
    
    # ==========================================================================
    # 5. POLICY: REFRESH_TOKENS
    # Tokens visíveis apenas se user pertence à org
    # ==========================================================================
    
    op.execute("""
        CREATE POLICY refresh_tokens_tenant_isolation ON refresh_tokens
            USING (
                EXISTS (
                    SELECT 1 FROM users u 
                    WHERE u.id = refresh_tokens.user_id 
                    AND u.org_id::text = current_setting('app.current_org_id', true)
                )
            );
    """)
    
    # ==========================================================================
    # 6. ÍNDICES PARA PERFORMANCE DAS POLICIES
    # ==========================================================================
    
    # Índice para acelerar lookups de análise por org
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_analyses_org_id_lookup 
        ON analyses (org_id);
    """)
    
    # Índice para acelerar lookup de outputs por análise
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_agent_outputs_analysis_lookup 
        ON agent_outputs (analysis_id);
    """)


def downgrade() -> None:
    """
    Remove Row-Level Security.
    CUIDADO: Isso remove a proteção de isolamento!
    """
    
    bind = op.get_bind()
    if bind.dialect.name != 'postgresql':
        return
    
    # Remove policies
    op.execute("DROP POLICY IF EXISTS users_tenant_isolation ON users;")
    op.execute("DROP POLICY IF EXISTS analyses_tenant_isolation ON analyses;")
    op.execute("DROP POLICY IF EXISTS agent_outputs_tenant_isolation ON agent_outputs;")
    op.execute("DROP POLICY IF EXISTS refresh_tokens_tenant_isolation ON refresh_tokens;")
    
    # Desabilita RLS
    op.execute("ALTER TABLE users DISABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE analyses DISABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE agent_outputs DISABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE refresh_tokens DISABLE ROW LEVEL SECURITY;")
    
    # Remove índices
    op.execute("DROP INDEX IF EXISTS ix_analyses_org_id_lookup;")
    op.execute("DROP INDEX IF EXISTS ix_agent_outputs_analysis_lookup;")
