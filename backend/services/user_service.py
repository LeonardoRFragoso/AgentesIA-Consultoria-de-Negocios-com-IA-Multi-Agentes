"""
User and Organization management service.
"""

from datetime import datetime
from typing import Optional, Tuple
from uuid import UUID
from sqlalchemy.orm import Session

from ..database.models import User, Organization, PlanType, UserRole
from ..security.password import hash_password, verify_password


class UserService:
    """Serviço de gerenciamento de usuários e organizações."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_organization(
        self,
        name: str,
        owner_email: str,
        owner_password: str,
        owner_name: Optional[str] = None
    ) -> Tuple[Organization, User]:
        """
        Cria nova organização com usuário owner.
        
        Returns:
            Tuple[Organization, User]: Organização e usuário criados
        """
        # Verifica se email já existe
        existing = self.db.query(User).filter(User.email == owner_email).first()
        if existing:
            raise ValueError(f"Email {owner_email} já está em uso")
        
        # Cria slug a partir do nome
        slug = self._generate_slug(name)
        
        # Cria organização
        org = Organization(
            name=name,
            slug=slug,
            plan=PlanType.FREE,
        )
        self.db.add(org)
        self.db.flush()  # Gera o ID
        
        # Cria usuário owner
        user = User(
            org_id=org.id,
            email=owner_email,
            password_hash=hash_password(owner_password),
            name=owner_name,
            role=UserRole.OWNER,
        )
        self.db.add(user)
        self.db.flush()
        
        return org, user
    
    def authenticate(self, email: str, password: str) -> Optional[User]:
        """
        Autentica usuário por email e senha.
        
        Returns:
            User se autenticado, None caso contrário
        """
        user = self.db.query(User).filter(
            User.email == email,
            User.is_active == True
        ).first()
        
        if not user:
            return None
        
        # Verifica se conta está bloqueada
        if user.locked_until and user.locked_until > datetime.utcnow():
            return None
        
        # Verifica senha
        if not verify_password(password, user.password_hash):
            # Incrementa tentativas falhas
            user.failed_login_attempts += 1
            
            # Bloqueia após 5 tentativas
            if user.failed_login_attempts >= 5:
                from datetime import timedelta
                user.locked_until = datetime.utcnow() + timedelta(minutes=15)
            
            self.db.commit()
            return None
        
        # Login bem-sucedido
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login_at = datetime.utcnow()
        self.db.commit()
        
        return user
    
    def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Busca usuário por ID."""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Busca usuário por email."""
        return self.db.query(User).filter(User.email == email).first()
    
    def get_organization(self, org_id: UUID) -> Optional[Organization]:
        """Busca organização por ID."""
        return self.db.query(Organization).filter(Organization.id == org_id).first()
    
    def get_user_with_org(self, user_id: UUID) -> Optional[Tuple[User, Organization]]:
        """Busca usuário com sua organização."""
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        
        org = self.get_organization(user.org_id)
        return user, org
    
    def invite_user(
        self,
        org_id: UUID,
        email: str,
        role: UserRole = UserRole.MEMBER,
        inviter: User = None
    ) -> User:
        """
        Convida usuário para organização.
        Cria usuário com senha temporária.
        """
        # Verifica se email já existe
        existing = self.db.query(User).filter(User.email == email).first()
        if existing:
            raise ValueError(f"Email {email} já está em uso")
        
        # Verifica limite de usuários do plano
        org = self.get_organization(org_id)
        if not org:
            raise ValueError("Organização não encontrada")
        
        user_count = self.db.query(User).filter(User.org_id == org_id).count()
        
        limits = {
            PlanType.FREE: 1,
            PlanType.PRO: 5,
            PlanType.ENTERPRISE: 999,
        }
        
        if user_count >= limits.get(org.plan, 1):
            raise ValueError(f"Limite de usuários do plano {org.plan.value} atingido")
        
        # Cria usuário com senha temporária
        import secrets
        temp_password = secrets.token_urlsafe(16)
        
        user = User(
            org_id=org_id,
            email=email,
            password_hash=hash_password(temp_password),
            role=role,
            email_verified=False,
        )
        self.db.add(user)
        self.db.flush()
        
        # TODO: Enviar email de convite com link para definir senha
        
        return user
    
    def _generate_slug(self, name: str) -> str:
        """Gera slug único a partir do nome."""
        import re
        
        # Remove caracteres especiais e converte para lowercase
        slug = re.sub(r'[^a-zA-Z0-9\s-]', '', name.lower())
        slug = re.sub(r'[\s_]+', '-', slug)
        slug = slug.strip('-')
        
        # Verifica unicidade
        base_slug = slug
        counter = 1
        while self.db.query(Organization).filter(Organization.slug == slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        return slug
