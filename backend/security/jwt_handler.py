"""
JWT Token handling com segurança adequada.
Implementa access tokens (curtos) e refresh tokens (longos).
"""

import jwt
from datetime import datetime, timedelta
from typing import Optional, Literal
from pydantic import BaseModel
from uuid import uuid4


class TokenPayload(BaseModel):
    """Payload do token JWT."""
    sub: str  # user_id
    email: str
    org_id: str
    role: str  # owner, admin, member
    plan: str  # free, pro, enterprise
    token_type: Literal["access", "refresh"]
    exp: datetime
    iat: datetime
    jti: str  # Token ID único (para revogação)


class JWTHandler:
    """
    Gerenciador de tokens JWT.
    
    Segurança implementada:
    - Tokens de curta duração (15 min)
    - Refresh tokens separados
    - JTI para revogação individual
    - Validação de tipo de token
    """
    
    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        access_expire_minutes: int = 15,
        refresh_expire_days: int = 30
    ):
        if len(secret_key) < 32:
            raise ValueError("JWT secret key must be at least 32 characters")
        
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_expire_minutes = access_expire_minutes
        self.refresh_expire_days = refresh_expire_days
    
    def create_access_token(
        self,
        user_id: str,
        email: str,
        org_id: str,
        role: str = "member",
        plan: str = "free"
    ) -> str:
        """
        Cria access token de curta duração.
        
        Args:
            user_id: ID do usuário
            email: Email do usuário
            org_id: ID da organização (tenant)
            role: Papel do usuário na org
            plan: Plano da organização
            
        Returns:
            Token JWT encoded
        """
        now = datetime.utcnow()
        expire = now + timedelta(minutes=self.access_expire_minutes)
        
        payload = {
            "sub": user_id,
            "email": email,
            "org_id": org_id,
            "role": role,
            "plan": plan,
            "token_type": "access",
            "exp": expire,
            "iat": now,
            "jti": str(uuid4())  # ID único para revogação
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(self, user_id: str) -> str:
        """
        Cria refresh token de longa duração.
        
        Refresh tokens contêm apenas o user_id para minimizar
        informação sensível em tokens de longa duração.
        """
        now = datetime.utcnow()
        expire = now + timedelta(days=self.refresh_expire_days)
        
        payload = {
            "sub": user_id,
            "token_type": "refresh",
            "exp": expire,
            "iat": now,
            "jti": str(uuid4())
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def decode_token(self, token: str) -> Optional[dict]:
        """
        Decodifica e valida um token JWT.
        
        Returns:
            Payload do token ou None se inválido
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def verify_access_token(self, token: str) -> Optional[TokenPayload]:
        """
        Verifica e retorna payload de um access token.
        
        Returns:
            TokenPayload se válido, None caso contrário
        """
        payload = self.decode_token(token)
        
        if not payload:
            return None
        
        if payload.get("token_type") != "access":
            return None
        
        try:
            return TokenPayload(
                sub=payload["sub"],
                email=payload.get("email", ""),
                org_id=payload.get("org_id", ""),
                role=payload.get("role", "member"),
                plan=payload.get("plan", "free"),
                token_type="access",
                exp=datetime.fromtimestamp(payload["exp"]),
                iat=datetime.fromtimestamp(payload["iat"]),
                jti=payload.get("jti", "")
            )
        except Exception:
            return None
    
    def verify_refresh_token(self, token: str) -> Optional[str]:
        """
        Verifica refresh token e retorna user_id.
        
        Returns:
            user_id se válido, None caso contrário
        """
        payload = self.decode_token(token)
        
        if not payload:
            return None
        
        if payload.get("token_type") != "refresh":
            return None
        
        return payload.get("sub")
