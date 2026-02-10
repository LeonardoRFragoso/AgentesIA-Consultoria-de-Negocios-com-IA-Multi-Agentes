"""
Database Connection Management - PostgreSQL Production Ready

Suporta:
- PostgreSQL (produção) com connection pooling otimizado
- SQLite (desenvolvimento local)
- SSL para conexões seguras
- Health checks automáticos
- Row-Level Security context
"""

from contextlib import contextmanager
from typing import Generator, Optional
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool, StaticPool, NullPool
from sqlalchemy.engine import Engine
import logging

from database.models import Base
from config import get_settings

logger = logging.getLogger(__name__)

# Engine global (será inicializado no startup)
_engine: Optional[Engine] = None
_session_factory = None


def get_postgres_engine_config(settings) -> dict:
    """
    Configuração otimizada para PostgreSQL em produção.
    
    Pool sizing:
    - pool_size: conexões mantidas abertas
    - max_overflow: conexões extras sob demanda
    - pool_recycle: tempo máximo de vida da conexão
    """
    config = {
        "poolclass": QueuePool,
        "pool_size": settings.DATABASE_POOL_SIZE,  # Default: 5
        "max_overflow": settings.DATABASE_MAX_OVERFLOW,  # Default: 10
        "pool_pre_ping": True,  # Verifica conexão antes de usar
        "pool_recycle": 3600,  # Recicla conexões a cada 1h
        "echo": settings.DEBUG,
    }
    
    # SSL para produção
    if settings.is_production():
        # Supabase, Railway, Render usam SSL
        if "sslmode" not in settings.DATABASE_URL:
            config["connect_args"] = {"sslmode": "require"}
    
    return config


def get_sqlite_engine_config(settings) -> dict:
    """Configuração para SQLite (desenvolvimento)."""
    return {
        "connect_args": {"check_same_thread": False},
        "poolclass": StaticPool,
        "echo": settings.DEBUG,
    }


def init_db() -> Engine:
    """
    Inicializa conexão com banco de dados.
    Chamar no startup da aplicação.
    
    Returns:
        Engine SQLAlchemy configurado
    """
    global _engine, _session_factory
    
    if _engine is not None:
        return _engine
    
    settings = get_settings()
    db_url = settings.DATABASE_URL
    
    # Detecta tipo de banco
    is_sqlite = db_url.startswith("sqlite")
    is_postgres = db_url.startswith("postgresql")
    
    if is_sqlite:
        logger.info("Inicializando SQLite (desenvolvimento)")
        config = get_sqlite_engine_config(settings)
    elif is_postgres:
        logger.info("Inicializando PostgreSQL (produção)")
        config = get_postgres_engine_config(settings)
    else:
        raise ValueError(f"Database não suportado: {db_url.split(':')[0]}")
    
    # Cria engine
    _engine = create_engine(db_url, **config)
    
    # Registra eventos para logging
    @event.listens_for(_engine, "connect")
    def on_connect(dbapi_conn, connection_record):
        logger.debug("Nova conexão estabelecida")
    
    @event.listens_for(_engine, "checkout")
    def on_checkout(dbapi_conn, connection_record, connection_proxy):
        logger.debug("Conexão retirada do pool")
    
    # Session factory
    _session_factory = sessionmaker(
        bind=_engine,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,  # Evita queries extras após commit
    )
    
    # Cria tabelas automaticamente apenas em desenvolvimento com SQLite
    if settings.is_development() and is_sqlite:
        logger.info("Criando tabelas automaticamente (dev mode)")
        Base.metadata.create_all(_engine)
    
    logger.info(f"Database inicializado: {db_url.split('@')[-1] if '@' in db_url else 'local'}")
    
    return _engine


def get_engine() -> Engine:
    """Retorna engine SQLAlchemy."""
    if _engine is None:
        init_db()
    return _engine


def check_database_health() -> dict:
    """
    Verifica saúde do banco de dados.
    
    Returns:
        Dict com status e métricas
    """
    engine = get_engine()
    
    try:
        with engine.connect() as conn:
            # Query simples para verificar conexão
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
            
            # Métricas do pool (se PostgreSQL)
            pool_status = {
                "size": engine.pool.size() if hasattr(engine.pool, 'size') else 0,
                "checked_in": engine.pool.checkedin() if hasattr(engine.pool, 'checkedin') else 0,
                "checked_out": engine.pool.checkedout() if hasattr(engine.pool, 'checkedout') else 0,
                "overflow": engine.pool.overflow() if hasattr(engine.pool, 'overflow') else 0,
            }
            
            return {
                "status": "healthy",
                "pool": pool_status,
            }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
        }


def close_db() -> None:
    """
    Fecha todas as conexões.
    Chamar no shutdown da aplicação.
    """
    global _engine, _session_factory
    
    if _engine is not None:
        _engine.dispose()
        logger.info("Database connections closed")
        _engine = None
        _session_factory = None


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Context manager para sessão de banco.
    Garante commit ou rollback.
    
    Uso:
        with get_db_session() as db:
            user = db.query(User).filter_by(email=email).first()
    """
    if _session_factory is None:
        init_db()
    
    session = _session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency para FastAPI.
    
    Uso:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    """
    if _session_factory is None:
        init_db()
    
    session = _session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def set_tenant_context(session: Session, org_id: str) -> None:
    """
    Define contexto do tenant para Row-Level Security.
    
    Uso com PostgreSQL RLS:
        SET app.current_org_id = 'uuid-here';
        
    Nota: Requer políticas RLS configuradas no PostgreSQL.
    """
    session.execute(f"SET app.current_org_id = '{org_id}'")
