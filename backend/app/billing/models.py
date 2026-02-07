"""
Database Models - Billing & Subscriptions

Modelos para persistência de dados de billing.
Compatível com SQLAlchemy 2.0+
"""
from datetime import datetime
from typing import Optional
from enum import Enum as PyEnum

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Enum, ForeignKey, Numeric, Text
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class PlanTierEnum(str, PyEnum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class BillingCycleEnum(str, PyEnum):
    MONTHLY = "monthly"
    YEARLY = "yearly"


class SubscriptionStatusEnum(str, PyEnum):
    ACTIVE = "active"
    PENDING = "pending"
    PAUSED = "paused"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class Organization(Base):
    """
    Organização/Empresa que possui uma assinatura.
    Um usuário pertence a uma organização.
    """
    __tablename__ = "organizations"
    
    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False)
    
    # Plano atual
    plan = Column(Enum(PlanTierEnum), default=PlanTierEnum.FREE, nullable=False)
    billing_cycle = Column(Enum(BillingCycleEnum), nullable=True)
    
    # Limites e uso
    analyses_used_this_month = Column(Integer, default=0)
    usage_reset_at = Column(DateTime, nullable=True)
    
    # Mercado Pago
    mp_subscription_id = Column(String(255), nullable=True, index=True)
    mp_customer_id = Column(String(255), nullable=True)
    mp_last_payment_id = Column(String(255), nullable=True)
    
    # Status da assinatura
    subscription_status = Column(Enum(SubscriptionStatusEnum), default=SubscriptionStatusEnum.ACTIVE)
    subscription_started_at = Column(DateTime, nullable=True)
    subscription_expires_at = Column(DateTime, nullable=True)
    
    # Cancelamento agendado
    scheduled_downgrade = Column(Boolean, default=False)
    downgrade_reason = Column(String(255), nullable=True)
    downgraded_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = relationship("User", back_populates="organization")
    payments = relationship("Payment", back_populates="organization")
    
    def is_subscription_active(self) -> bool:
        """Verifica se a assinatura está ativa"""
        if self.plan == PlanTierEnum.FREE:
            return True
        if self.subscription_expires_at and self.subscription_expires_at < datetime.utcnow():
            return False
        return self.subscription_status == SubscriptionStatusEnum.ACTIVE
    
    def can_create_analysis(self, limit: int) -> bool:
        """Verifica se pode criar análise baseado no limite"""
        if limit == -1:  # Ilimitado
            return True
        return self.analyses_used_this_month < limit


class User(Base):
    """Usuário do sistema"""
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=True)
    
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=True)
    organization = relationship("Organization", back_populates="users")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Payment(Base):
    """Histórico de pagamentos"""
    __tablename__ = "payments"
    
    id = Column(String(36), primary_key=True)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    
    # Mercado Pago
    mp_payment_id = Column(String(255), unique=True, index=True)
    mp_subscription_id = Column(String(255), nullable=True)
    
    # Detalhes do pagamento
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="BRL")
    status = Column(String(50), nullable=False)  # approved, pending, rejected, etc.
    payment_type = Column(String(50), nullable=True)  # credit_card, pix, boleto
    
    # Plano relacionado
    plan = Column(Enum(PlanTierEnum), nullable=False)
    billing_cycle = Column(Enum(BillingCycleEnum), nullable=True)
    
    # Período coberto
    period_start = Column(DateTime, nullable=True)
    period_end = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    
    # Relationship
    organization = relationship("Organization", back_populates="payments")


class SubscriptionEvent(Base):
    """
    Log de eventos de assinatura.
    Útil para auditoria e debugging.
    """
    __tablename__ = "subscription_events"
    
    id = Column(String(36), primary_key=True)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    
    event_type = Column(String(100), nullable=False)  # upgrade, downgrade, payment, cancellation, etc.
    event_data = Column(Text, nullable=True)  # JSON com dados do evento
    
    previous_plan = Column(Enum(PlanTierEnum), nullable=True)
    new_plan = Column(Enum(PlanTierEnum), nullable=True)
    
    mp_webhook_id = Column(String(255), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)


# ==================== MIGRATION HELPERS ====================

def create_tables(engine):
    """Cria todas as tabelas no banco de dados"""
    Base.metadata.create_all(engine)


def get_organization_plan_info(org: Organization) -> dict:
    """Helper para extrair info de plano da organização"""
    return {
        "plan": org.plan.value if org.plan else "free",
        "billing_cycle": org.billing_cycle.value if org.billing_cycle else None,
        "status": org.subscription_status.value if org.subscription_status else "active",
        "expires_at": org.subscription_expires_at.isoformat() if org.subscription_expires_at else None,
        "analyses_used": org.analyses_used_this_month or 0,
        "is_active": org.is_subscription_active(),
    }
