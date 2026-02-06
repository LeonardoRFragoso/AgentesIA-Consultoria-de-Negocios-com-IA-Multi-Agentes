"""Database connection management."""

import os
import warnings
from typing import Optional
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Suprimir aviso de typing do SQLAlchemy
warnings.filterwarnings("ignore", category=DeprecationWarning)

from .models import Base


class DatabaseConnection:
    """Gerencia conexão com banco de dados."""
    
    _instance: Optional["DatabaseConnection"] = None
    _engine: Optional[Engine] = None
    _session_factory: Optional[sessionmaker] = None
    
    def __init__(self, database_url: Optional[str] = None):
        """
        Inicializa conexão com banco de dados.
        
        Args:
            database_url: URL de conexão (default: SQLite local)
        """
        if database_url is None:
            # SQLite local para MVP
            db_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "analyses.db")
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            database_url = f"sqlite:///{db_path}"
        
        self.database_url = database_url
        self._init_engine()
        self._create_tables()
    
    def _init_engine(self):
        """Inicializa engine SQLAlchemy."""
        if "sqlite" in self.database_url:
            # SQLite: usar StaticPool para evitar problemas de thread
            self._engine = create_engine(
                self.database_url,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
                echo=False
            )
        else:
            # PostgreSQL ou outro
            self._engine = create_engine(
                self.database_url,
                pool_pre_ping=True,
                echo=False
            )
        
        self._session_factory = sessionmaker(bind=self._engine)
    
    def _create_tables(self):
        """Cria tabelas se não existirem."""
        Base.metadata.create_all(self._engine)
    
    def get_session(self) -> Session:
        """Retorna nova sessão."""
        if self._session_factory is None:
            raise RuntimeError("Database not initialized")
        return self._session_factory()
    
    def close(self):
        """Fecha conexão."""
        if self._engine:
            self._engine.dispose()
    
    @classmethod
    def get_instance(cls, database_url: Optional[str] = None) -> "DatabaseConnection":
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = cls(database_url)
        return cls._instance


def get_db_connection(database_url: Optional[str] = None) -> DatabaseConnection:
    """Factory function para obter instância de conexão."""
    return DatabaseConnection.get_instance(database_url)
