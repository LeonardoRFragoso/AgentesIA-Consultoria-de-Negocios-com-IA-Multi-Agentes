"""Base repository class."""

from typing import TypeVar, Generic, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """Classe base para repositórios."""
    
    def __init__(self, session: Session, model_class: type):
        """
        Inicializa repositório.
        
        Args:
            session: Sessão SQLAlchemy
            model_class: Classe do modelo
        """
        self.session = session
        self.model_class = model_class
    
    def create(self, obj: T) -> T:
        """Cria novo objeto."""
        try:
            self.session.add(obj)
            self.session.commit()
            self.session.refresh(obj)
            return obj
        except SQLAlchemyError as e:
            self.session.rollback()
            raise RuntimeError(f"Erro ao criar {self.model_class.__name__}: {str(e)}")
    
    def get_by_id(self, id: any) -> Optional[T]:
        """Obtém objeto por ID."""
        try:
            return self.session.query(self.model_class).filter(
                self.model_class.id == id
            ).first()
        except SQLAlchemyError as e:
            raise RuntimeError(f"Erro ao buscar {self.model_class.__name__}: {str(e)}")
    
    def get_all(self) -> List[T]:
        """Obtém todos os objetos."""
        try:
            return self.session.query(self.model_class).all()
        except SQLAlchemyError as e:
            raise RuntimeError(f"Erro ao listar {self.model_class.__name__}: {str(e)}")
    
    def update(self, obj: T) -> T:
        """Atualiza objeto."""
        try:
            self.session.merge(obj)
            self.session.commit()
            return obj
        except SQLAlchemyError as e:
            self.session.rollback()
            raise RuntimeError(f"Erro ao atualizar {self.model_class.__name__}: {str(e)}")
    
    def delete(self, obj: T) -> None:
        """Deleta objeto."""
        try:
            self.session.delete(obj)
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise RuntimeError(f"Erro ao deletar {self.model_class.__name__}: {str(e)}")
    
    def close(self) -> None:
        """Fecha sessão."""
        if self.session:
            self.session.close()
