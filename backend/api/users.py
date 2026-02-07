"""
User management endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from ..database import get_db
from ..database.models import User, UserRole
from ..security.auth import get_tenant_context, TenantContext
from ..services.user_service import UserService
from .schemas import UserResponse, UserInvite

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/team", response_model=List[UserResponse])
async def list_team_members(
    db: Session = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context)
):
    """
    Lista membros da organização.
    """
    users = db.query(User).filter(
        User.org_id == UUID(tenant.org_id),
        User.is_active == True
    ).all()
    
    user_service = UserService(db)
    org = user_service.get_organization(UUID(tenant.org_id))
    
    return [
        UserResponse(
            id=u.id,
            email=u.email,
            name=u.name,
            role=u.role.value,
            org_id=org.id,
            organization_name=org.name,
            plan=org.plan.value,
            created_at=u.created_at
        )
        for u in users
    ]


@router.post("/invite", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def invite_user(
    data: UserInvite,
    db: Session = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context)
):
    """
    Convida novo usuário para a organização.
    Requer role admin ou owner.
    """
    if not tenant.can_manage_team():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas admins podem convidar usuários"
        )
    
    user_service = UserService(db)
    
    try:
        role = UserRole(data.role)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role inválido"
        )
    
    try:
        user = user_service.invite_user(
            org_id=UUID(tenant.org_id),
            email=data.email,
            role=role
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    org = user_service.get_organization(UUID(tenant.org_id))
    
    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        role=user.role.value,
        org_id=org.id,
        organization_name=org.name,
        plan=org.plan.value,
        created_at=user.created_at
    )


@router.patch("/{user_id}/role")
async def update_user_role(
    user_id: UUID,
    role: str,
    db: Session = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context)
):
    """
    Atualiza role de um usuário.
    Requer role owner.
    """
    if not tenant.is_owner():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas o owner pode alterar roles"
        )
    
    try:
        new_role = UserRole(role)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role inválido"
        )
    
    # Não permite alterar o próprio owner
    if str(user_id) == tenant.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível alterar seu próprio role"
        )
    
    user = db.query(User).filter(
        User.id == user_id,
        User.org_id == UUID(tenant.org_id)
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Não permite promover a owner
    if new_role == UserRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível promover a owner"
        )
    
    user.role = new_role
    db.commit()
    
    return {"message": f"Role atualizado para {role}"}


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context)
):
    """
    Remove usuário da organização.
    Requer role admin ou owner.
    """
    if not tenant.can_manage_team():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas admins podem remover usuários"
        )
    
    # Não permite remover a si mesmo
    if str(user_id) == tenant.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível remover a si mesmo"
        )
    
    user = db.query(User).filter(
        User.id == user_id,
        User.org_id == UUID(tenant.org_id)
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Não permite remover owner
    if user.role == UserRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível remover o owner"
        )
    
    user.is_active = False
    db.commit()
