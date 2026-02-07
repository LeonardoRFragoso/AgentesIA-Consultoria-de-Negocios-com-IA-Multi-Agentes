"""
Authentication endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from ..database import get_db
from ..security import JWTHandler, get_current_user
from ..security.auth import get_jwt_handler, TokenPayload
from ..services.user_service import UserService
from .schemas import (
    UserRegister, UserLogin, TokenResponse, 
    RefreshTokenRequest, UserResponse
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    data: UserRegister,
    request: Request,
    db: Session = Depends(get_db),
    jwt_handler: JWTHandler = Depends(get_jwt_handler)
):
    """
    Registra novo usuário e organização.
    Retorna tokens de acesso.
    """
    user_service = UserService(db)
    
    try:
        org, user = user_service.create_organization(
            name=data.organization_name,
            owner_email=data.email,
            owner_password=data.password,
            owner_name=data.name
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    # Gera tokens
    access_token = jwt_handler.create_access_token(
        user_id=str(user.id),
        email=user.email,
        org_id=str(org.id),
        role=user.role.value,
        plan=org.plan.value
    )
    
    refresh_token = jwt_handler.create_refresh_token(str(user.id))
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    data: UserLogin,
    request: Request,
    db: Session = Depends(get_db),
    jwt_handler: JWTHandler = Depends(get_jwt_handler)
):
    """
    Autentica usuário existente.
    """
    user_service = UserService(db)
    
    user = user_service.authenticate(data.email, data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha inválidos"
        )
    
    org = user_service.get_organization(user.org_id)
    
    if not org or not org.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organização inativa"
        )
    
    access_token = jwt_handler.create_access_token(
        user_id=str(user.id),
        email=user.email,
        org_id=str(org.id),
        role=user.role.value,
        plan=org.plan.value
    )
    
    refresh_token = jwt_handler.create_refresh_token(str(user.id))
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    data: RefreshTokenRequest,
    db: Session = Depends(get_db),
    jwt_handler: JWTHandler = Depends(get_jwt_handler)
):
    """
    Renova access token usando refresh token.
    """
    user_id = jwt_handler.verify_refresh_token(data.refresh_token)
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido ou expirado"
        )
    
    user_service = UserService(db)
    result = user_service.get_user_with_org(user_id)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    user, org = result
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo"
        )
    
    access_token = jwt_handler.create_access_token(
        user_id=str(user.id),
        email=user.email,
        org_id=str(org.id),
        role=user.role.value,
        plan=org.plan.value
    )
    
    # Gera novo refresh token (rotation)
    new_refresh_token = jwt_handler.create_refresh_token(str(user.id))
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: TokenPayload = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retorna informações do usuário autenticado.
    """
    user_service = UserService(db)
    result = user_service.get_user_with_org(current_user.sub)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    user, org = result
    
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


@router.post("/logout")
async def logout(current_user: TokenPayload = Depends(get_current_user)):
    """
    Logout do usuário.
    Em produção: adicionar JTI à blacklist no Redis.
    """
    # TODO: Adicionar token à blacklist
    return {"message": "Logout realizado com sucesso"}
