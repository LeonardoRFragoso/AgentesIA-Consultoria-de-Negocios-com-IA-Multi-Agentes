"""
SQLAlchemy models para o SaaS multi-tenant.
Estrutura projetada para isolamento por organização.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column, String, Text, Float, Integer, DateTime, 
    ForeignKey, Boolean, JSON, Enum as SQLEnum, Index, TypeDecorator
)
from sqlalchemy.orm import declarative_base, relationship
import uuid
import enum


Base = declarative_base()


class GUID(TypeDecorator):
    """
    Platform-independent GUID type.
    Uses PostgreSQL's UUID type or String(36) for SQLite.
    """
    impl = String(36)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            if isinstance(value, uuid.UUID):
                return str(value)
            return str(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            if not isinstance(value, uuid.UUID):
                return uuid.UUID(value)
        return value


class PlanType(str, enum.Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class UserRole(str, enum.Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


class AnalysisStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


# =============================================================================
# ORGANIZATION (Tenant)
# =============================================================================

class Organization(Base):
    """
    Organização = Tenant.
    Todas as outras entidades pertencem a uma organização.
    """
    
    __tablename__ = "organizations"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    
    # Billing
    plan = Column(SQLEnum(PlanType), default=PlanType.FREE, nullable=False)
    stripe_customer_id = Column(String(255), nullable=True, index=True)
    stripe_subscription_id = Column(String(255), nullable=True)
    
    # Usage tracking
    executions_this_month = Column(Integer, default=0)
    tokens_used_today = Column(Integer, default=0)
    tokens_reset_at = Column(DateTime, default=datetime.utcnow)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")
    analyses = relationship("Analysis", back_populates="organization", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Organization(id={self.id}, name={self.name}, plan={self.plan})>"
    
    def can_execute_analysis(self) -> tuple[bool, Optional[str]]:
        """Verifica se a org pode executar mais análises."""
        if not self.is_active:
            return False, "Organização inativa"
        
        if self.plan == PlanType.FREE:
            if self.executions_this_month >= 10:
                return False, "Limite de 10 análises/mês atingido. Faça upgrade para Pro."
        
        return True, None


# =============================================================================
# USER
# =============================================================================

class User(Base):
    """
    Usuário pertence a uma organização.
    Email é único globalmente.
    """
    
    __tablename__ = "users"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    org_id = Column(GUID(), ForeignKey("organizations.id"), nullable=False, index=True)
    
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # Profile
    name = Column(String(255), nullable=True)
    role = Column(SQLEnum(UserRole), default=UserRole.MEMBER, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    email_verified = Column(Boolean, default=False)
    
    # Auth tracking
    last_login_at = Column(DateTime, nullable=True)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organization = relationship("Organization", back_populates="users")
    analyses = relationship("Analysis", back_populates="created_by_user")
    
    # Indexes
    __table_args__ = (
        Index("ix_users_org_email", "org_id", "email"),
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
    
    def is_owner(self) -> bool:
        return self.role == UserRole.OWNER
    
    def is_admin(self) -> bool:
        return self.role in (UserRole.OWNER, UserRole.ADMIN)


# =============================================================================
# ANALYSIS
# =============================================================================

class Analysis(Base):
    """
    Análise executada pelo sistema multi-agentes.
    Pertence a uma organização (isolamento multi-tenant).
    """
    
    __tablename__ = "analyses"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    org_id = Column(GUID(), ForeignKey("organizations.id"), nullable=False, index=True)
    created_by = Column(GUID(), ForeignKey("users.id"), nullable=False)
    
    # Input
    problem_description = Column(Text, nullable=False)
    business_type = Column(String(100), nullable=False, default="B2B")
    analysis_depth = Column(String(50), nullable=False, default="Padrão")
    
    # Status
    status = Column(SQLEnum(AnalysisStatus), default=AnalysisStatus.PENDING, nullable=False)
    error_message = Column(Text, nullable=True)
    
    # Results (JSON para flexibilidade)
    executive_summary = Column(Text, nullable=True)
    results = Column(JSON, nullable=True)  # {agent_name: output}
    
    # Metrics
    total_latency_ms = Column(Float, default=0.0)
    total_tokens = Column(Integer, default=0)
    total_cost_usd = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="analyses")
    created_by_user = relationship("User", back_populates="analyses")
    agent_outputs = relationship("AgentOutput", back_populates="analysis", cascade="all, delete-orphan")
    
    # Indexes para queries comuns
    __table_args__ = (
        Index("ix_analyses_org_created", "org_id", "created_at"),
        Index("ix_analyses_org_status", "org_id", "status"),
    )
    
    def __repr__(self):
        return f"<Analysis(id={self.id}, status={self.status})>"


# =============================================================================
# AGENT OUTPUT
# =============================================================================

class AgentOutput(Base):
    """
    Output individual de cada agente.
    Permite análise granular de performance por agente.
    """
    
    __tablename__ = "agent_outputs"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    analysis_id = Column(GUID(), ForeignKey("analyses.id"), nullable=False, index=True)
    
    agent_name = Column(String(100), nullable=False, index=True)
    output = Column(Text, nullable=True)
    
    # Status
    status = Column(String(50), default="pending")  # pending, running, completed, failed
    error_message = Column(Text, nullable=True)
    
    # Metrics
    latency_ms = Column(Float, default=0.0)
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    cost_usd = Column(Float, default=0.0)
    
    # Timestamps
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    analysis = relationship("Analysis", back_populates="agent_outputs")
    
    def __repr__(self):
        return f"<AgentOutput(analysis_id={self.analysis_id}, agent={self.agent_name})>"


# =============================================================================
# REFRESH TOKEN (para revogação)
# =============================================================================

class RefreshToken(Base):
    """
    Armazena refresh tokens para permitir revogação.
    JTI (JWT ID) é único por token.
    """
    
    __tablename__ = "refresh_tokens"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False, index=True)
    
    jti = Column(String(255), unique=True, nullable=False, index=True)
    
    # Metadata
    user_agent = Column(String(500), nullable=True)
    ip_address = Column(String(45), nullable=True)
    
    # Status
    is_revoked = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    revoked_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<RefreshToken(user_id={self.user_id}, revoked={self.is_revoked})>"
