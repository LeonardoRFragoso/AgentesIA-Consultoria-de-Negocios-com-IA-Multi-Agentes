"""SQLAlchemy models for persistence."""

from __future__ import annotations
from datetime import datetime
from sqlalchemy import Column, String, Text, Float, Integer, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Analysis(Base):
    """Modelo para análises executadas."""
    
    __tablename__ = "analyses"
    
    # Identificação
    execution_id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(255), index=True, default="default")  # Para multi-tenant futuro
    workspace_id = Column(String(255), index=True, default="default")
    
    # Conteúdo
    problem_description = Column(Text, nullable=False)
    business_type = Column(String(100), nullable=False)
    analysis_depth = Column(String(50), nullable=False)
    
    # Resultados consolidados
    executive_summary = Column(Text, nullable=True)
    
    # Metadados
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Métricas
    total_latency_ms = Column(Float, default=0.0)
    total_tokens = Column(Integer, default=0)
    total_cost_usd = Column(Float, default=0.0)
    
    # Status
    status = Column(String(50), default="completed")  # completed, failed, partial
    error_message = Column(Text, nullable=True)
    
    # Relacionamento
    agent_outputs = relationship("AgentOutput", back_populates="analysis", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Analysis(execution_id={self.execution_id}, problem_length={len(self.problem_description)})>"


class AgentOutput(Base):
    """Modelo para outputs de agentes."""
    
    __tablename__ = "agent_outputs"
    
    # Identificação
    id = Column(Integer, primary_key=True, autoincrement=True)
    execution_id = Column(String(36), ForeignKey("analyses.execution_id"), index=True)
    agent_name = Column(String(100), nullable=False, index=True)
    
    # Conteúdo
    output = Column(Text, nullable=False)
    
    # Metadados
    latency_ms = Column(Float, default=0.0)
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    cost_usd = Column(Float, default=0.0)
    
    # Status
    status = Column(String(50), default="completed")  # completed, failed, timeout
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Relacionamento
    analysis = relationship("Analysis", back_populates="agent_outputs")
    
    def __repr__(self):
        return f"<AgentOutput(execution_id={self.execution_id}, agent={self.agent_name})>"
