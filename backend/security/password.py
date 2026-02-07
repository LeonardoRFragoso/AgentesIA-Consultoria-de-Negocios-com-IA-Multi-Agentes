"""
Password hashing usando bcrypt.
CRÍTICO: Nunca armazene senhas em texto plano.
"""

import bcrypt
from typing import Union


class PasswordHasher:
    """
    Classe para hash e verificação de senhas usando bcrypt.
    
    bcrypt é preferível a SHA/MD5 porque:
    1. É deliberadamente lento (resistente a brute force)
    2. Inclui salt automaticamente
    3. É resistente a ataques de GPU
    """
    
    def __init__(self, rounds: int = 12):
        """
        Args:
            rounds: Número de rounds de hashing. 
                    Maior = mais seguro, mais lento.
                    Produção: 12-14
        """
        self.rounds = rounds
    
    def hash(self, password: str) -> str:
        """
        Gera hash de uma senha.
        
        Args:
            password: Senha em texto plano
            
        Returns:
            Hash da senha (inclui salt)
        """
        if not password:
            raise ValueError("Password cannot be empty")
        
        # Encode para bytes
        password_bytes = password.encode("utf-8")
        
        # Gera salt e hash
        salt = bcrypt.gensalt(rounds=self.rounds)
        hashed = bcrypt.hashpw(password_bytes, salt)
        
        # Retorna como string
        return hashed.decode("utf-8")
    
    def verify(self, password: str, hashed: str) -> bool:
        """
        Verifica se uma senha corresponde ao hash.
        
        Args:
            password: Senha em texto plano
            hashed: Hash armazenado
            
        Returns:
            True se corresponde, False caso contrário
        """
        if not password or not hashed:
            return False
        
        try:
            password_bytes = password.encode("utf-8")
            hashed_bytes = hashed.encode("utf-8")
            return bcrypt.checkpw(password_bytes, hashed_bytes)
        except Exception:
            # Qualquer erro = senha inválida
            return False


# Instância global para uso conveniente
_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    """Função utilitária para hash de senha."""
    return _hasher.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    """Função utilitária para verificação de senha."""
    return _hasher.verify(password, hashed)
