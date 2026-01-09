from datetime import timedelta
from typing import Any
import secrets
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from google.oauth2 import id_token
from google.auth.transport import requests

from app.api import deps
from app.core import security
from app.config import settings
from app.models.database import get_db
from app.models.user import User, UserRole
from app.schemas.user import Token, UserCreate, User as UserSchema, GoogleLogin

router = APIRouter()

@router.post("/login", response_model=Token)
async def login_access_token(
    db: AsyncSession = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    # Find user by email
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()
    
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
        
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, role=user.role.value
        ),
        "token_type": "bearer",
    }

@router.post("/google", response_model=Token)
async def login_google(
    login_data: GoogleLogin,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Login with Google ID Token
    """
    try:
        # Verify Google Token
        id_info = id_token.verify_oauth2_token(
            login_data.credential,
            requests.Request(),
            settings.google_client_id
        )
    except ValueError as e:
        # Development/Mock mode fallback (optional, remove in production if strict)
        if settings.app_env == "development" and login_data.credential.startswith("mock_"):
             # Mock logic for testing without real Google creds
             id_info = {"email": "mock@example.com", "name": "Mock User"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid Google token: {str(e)}"
            )

    email = id_info.get("email")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google token missing email"
        )

    # 檢查郵箱是否在白名單中
    if settings.google_allowed_emails:
        allowed_emails = [e.strip().lower() for e in settings.google_allowed_emails.split(",") if e.strip()]
        if email.lower() not in allowed_emails:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="此 Google 帳戶未被授權登入系統"
            )

    # Check if user exists
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        # Create new user
        # Generate a random password since they use Google
        random_password = secrets.token_urlsafe(32)
        hashed_password = security.get_password_hash(random_password)

        # 根據郵箱分配角色
        email_lower = email.lower()
        admin_emails = [e.strip().lower() for e in settings.google_admin_emails.split(",") if e.strip()]
        operator_emails = [e.strip().lower() for e in settings.google_operator_emails.split(",") if e.strip()]

        if email_lower in admin_emails:
            role = UserRole.ADMIN
        elif email_lower in operator_emails:
            role = UserRole.OPERATOR
        else:
            role = UserRole.VIEWER

        user = User(
            email=email,
            hashed_password=hashed_password,
            full_name=id_info.get("name"),
            role=role,
            is_active=True,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
        
    # Create token
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, role=user.role.value
        ),
        "token_type": "bearer",
    }

@router.post("/register", response_model=UserSchema)
async def register_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Create new user without the need to be logged in
    """
    result = await db.execute(select(User).where(User.email == user_in.email))
    user = result.scalar_one_or_none()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
        
    user = User(
        email=user_in.email,
        hashed_password=security.get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role=user_in.role,
        is_active=user_in.is_active,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

@router.get("/me", response_model=UserSchema)
async def read_users_me(
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user
    """
    return current_user
