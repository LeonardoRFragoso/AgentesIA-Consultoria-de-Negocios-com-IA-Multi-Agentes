"""Initial schema - Multi-tenant SaaS

Revision ID: 001
Create Date: 2026-02-06

Schema multi-tenant completo com:
- Organizations (tenants)
- Users (com roles)
- Analyses (execuções)
- Agent Outputs (resultados por agente)
- Refresh Tokens (para JWT)
- Índices otimizados
- Constraints de integridade
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# Revision identifiers
revision = '001_initial'
down_revision = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Detecta dialect para usar tipos corretos
    bind = op.get_bind()
    is_postgres = bind.dialect.name == 'postgresql'

    # Organizations (Tenants)
    op.create_table(
        'organizations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(100), unique=True, nullable=False),
        sa.Column('plan', sa.String(20), nullable=False, server_default='free'),
        sa.Column('stripe_customer_id', sa.String(255), nullable=True),
        sa.Column('stripe_subscription_id', sa.String(255), nullable=True),
        sa.Column('executions_this_month', sa.Integer, server_default='0'),
        sa.Column('tokens_used_today', sa.Integer, server_default='0'),
        sa.Column('tokens_reset_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index('ix_organizations_slug', 'organizations', ['slug'])
    op.create_index('ix_organizations_stripe_customer', 'organizations', ['stripe_customer_id'])

    # Users
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('org_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id'), nullable=False),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('name', sa.String(255), nullable=True),
        sa.Column('role', sa.String(20), nullable=False, server_default='member'),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('email_verified', sa.Boolean, server_default='false'),
        sa.Column('last_login_at', sa.DateTime, nullable=True),
        sa.Column('failed_login_attempts', sa.Integer, server_default='0'),
        sa.Column('locked_until', sa.DateTime, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index('ix_users_email', 'users', ['email'])
    op.create_index('ix_users_org_id', 'users', ['org_id'])
    op.create_index('ix_users_org_email', 'users', ['org_id', 'email'])

    # Analyses
    op.create_table(
        'analyses',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('org_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id'), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('problem_description', sa.Text, nullable=False),
        sa.Column('business_type', sa.String(100), nullable=False, server_default='B2B'),
        sa.Column('analysis_depth', sa.String(50), nullable=False, server_default='Padrão'),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('error_message', sa.Text, nullable=True),
        sa.Column('executive_summary', sa.Text, nullable=True),
        sa.Column('results', postgresql.JSONB, nullable=True),
        sa.Column('total_latency_ms', sa.Float, server_default='0'),
        sa.Column('total_tokens', sa.Integer, server_default='0'),
        sa.Column('total_cost_usd', sa.Float, server_default='0'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('started_at', sa.DateTime, nullable=True),
        sa.Column('completed_at', sa.DateTime, nullable=True),
    )
    op.create_index('ix_analyses_org_id', 'analyses', ['org_id'])
    op.create_index('ix_analyses_created_at', 'analyses', ['created_at'])
    op.create_index('ix_analyses_org_created', 'analyses', ['org_id', 'created_at'])
    op.create_index('ix_analyses_org_status', 'analyses', ['org_id', 'status'])

    # Agent Outputs
    op.create_table(
        'agent_outputs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('analysis_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('analyses.id'), nullable=False),
        sa.Column('agent_name', sa.String(100), nullable=False),
        sa.Column('output', sa.Text, nullable=True),
        sa.Column('status', sa.String(50), server_default='pending'),
        sa.Column('error_message', sa.Text, nullable=True),
        sa.Column('latency_ms', sa.Float, server_default='0'),
        sa.Column('input_tokens', sa.Integer, server_default='0'),
        sa.Column('output_tokens', sa.Integer, server_default='0'),
        sa.Column('cost_usd', sa.Float, server_default='0'),
        sa.Column('started_at', sa.DateTime, nullable=True),
        sa.Column('completed_at', sa.DateTime, nullable=True),
    )
    op.create_index('ix_agent_outputs_analysis_id', 'agent_outputs', ['analysis_id'])
    op.create_index('ix_agent_outputs_agent_name', 'agent_outputs', ['agent_name'])

    # Refresh Tokens (for revocation)
    op.create_table(
        'refresh_tokens',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('jti', sa.String(255), unique=True, nullable=False),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('is_revoked', sa.Boolean, server_default='false'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('expires_at', sa.DateTime, nullable=False),
        sa.Column('revoked_at', sa.DateTime, nullable=True),
    )
    op.create_index('ix_refresh_tokens_user_id', 'refresh_tokens', ['user_id'])
    op.create_index('ix_refresh_tokens_jti', 'refresh_tokens', ['jti'])


def downgrade() -> None:
    op.drop_table('refresh_tokens')
    op.drop_table('agent_outputs')
    op.drop_table('analyses')
    op.drop_table('users')
    op.drop_table('organizations')
