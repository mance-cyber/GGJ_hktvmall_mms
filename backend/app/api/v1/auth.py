from datetime import datetime, timedelta, timezone
from typing import Any
import secrets
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from google.oauth2 import id_token
from google.auth.transport import requests

from app.api import deps
from app.core import security
from app.config import settings
from app.models.database import get_db
from app.models.user import User, UserRole, RefreshToken
from app.schemas.user import Token, UserCreate, User as UserSchema, GoogleLogin, UserWithPermissions

logger = logging.getLogger(__name__)

router = APIRouter()


# =============================================
# Helpers — Refresh Token 操作
# =============================================

async def _create_token_pair(db: AsyncSession, user: User) -> dict:
    """創建 access + refresh token pair"""
    access_token = security.create_access_token(user.id, role=user.role.value)
    refresh_token_str = security.create_refresh_token()

    # 存 refresh token 到 DB
    refresh_token = RefreshToken(
        token=refresh_token_str,
        user_id=user.id,
        expires_at=datetime.now(timezone.utc).replace(tzinfo=None)
                   + timedelta(days=security.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(refresh_token)
    await db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token_str,
        "token_type": "bearer",
    }


# =============================================
# Login endpoints
# =============================================

@router.post("/login")
async def login_access_token(
    db: AsyncSession = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """OAuth2 compatible token login"""
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()

    # 統一錯誤訊息，防止 user enumeration
    if not user or not user.is_active or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return await _create_token_pair(db, user)


@router.post("/google")
async def login_google(
    login_data: GoogleLogin,
    db: AsyncSession = Depends(get_db),
    request: Any = None,
) -> Any:
    """Login with Google ID Token"""
    try:
        id_info = id_token.verify_oauth2_token(
            login_data.credential,
            requests.Request(),
            settings.google_client_id
        )
    except ValueError as e:
        # H-01: Mock mode 僅限開發環境 + 本地請求
        if (
            settings.app_env == "development"
            and settings.debug
            and login_data.credential.startswith("mock_")
        ):
            id_info = {"email": "mock@example.com", "name": "Mock User"}
            logger.warning("SECURITY: Mock authentication used in development mode")
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Google token"
            )

    email = id_info.get("email")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google token missing email"
        )

    # 檢查郵箱白名單
    if settings.google_allowed_emails:
        allowed_emails = [e.strip().lower() for e in settings.google_allowed_emails.split(",") if e.strip()]
        if email.lower() not in allowed_emails:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="此 Google 帳戶未被授權登入系統"
            )

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    # 根據郵箱分配角色
    email_lower = email.lower()
    admin_emails = [e.strip().lower() for e in settings.google_admin_emails.split(",") if e.strip()]
    operator_emails = [e.strip().lower() for e in settings.google_operator_emails.split(",") if e.strip()]

    if email_lower in admin_emails:
        expected_role = UserRole.ADMIN
    elif email_lower in operator_emails:
        expected_role = UserRole.OPERATOR
    else:
        expected_role = UserRole.VIEWER

    try:
        if not user:
            random_password = secrets.token_urlsafe(32)
            hashed_password = security.get_password_hash(random_password)
            user = User(
                email=email,
                hashed_password=hashed_password,
                full_name=id_info.get("name"),
                role=expected_role,
                is_active=True,
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
        elif not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        else:
            if user.role != expected_role:
                user.role = expected_role
                await db.commit()
                await db.refresh(user)
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error during Google login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登入過程發生錯誤，請稍後再試"
        )

    return await _create_token_pair(db, user)


# =============================================
# Refresh Token endpoint
# =============================================

class RefreshRequest(BaseModel):
    refresh_token: str


@router.post("/refresh")
async def refresh_access_token(
    body: RefreshRequest,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """用 refresh token 換取新 access + refresh token"""
    now = datetime.now(timezone.utc).replace(tzinfo=None)

    result = await db.execute(
        select(RefreshToken).where(
            and_(
                RefreshToken.token == body.refresh_token,
                RefreshToken.revoked == False,
                RefreshToken.expires_at > now,
            )
        )
    )
    rt = result.scalar_one_or_none()
    if not rt:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

    # Revoke 舊 token
    rt.revoked = True

    # 取得用戶
    user_result = await db.execute(select(User).where(User.id == rt.user_id))
    user = user_result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    return await _create_token_pair(db, user)


# =============================================
# Logout (revoke refresh tokens)
# =============================================

@router.post("/logout")
async def logout(
    body: RefreshRequest,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Revoke refresh token"""
    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token == body.refresh_token)
    )
    rt = result.scalar_one_or_none()
    if rt:
        rt.revoked = True
        await db.commit()
    return {"detail": "Logged out"}


# =============================================
# Register (admin only)
# =============================================

@router.post("/register", response_model=UserSchema)
async def register_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
    _current_admin: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """Create new user (admin only)"""
    result = await db.execute(select(User).where(User.email == user_in.email))
    user = result.scalar_one_or_none()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )

    assigned_role = user_in.role if user_in.role else UserRole.VIEWER
    user = User(
        email=user_in.email,
        hashed_password=security.get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role=assigned_role,
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


# =============================================
# Current user
# =============================================

@router.get("/me", response_model=UserWithPermissions)
async def read_users_me(
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Get current user with permissions"""
    from app.api.deps import get_user_permissions

    permissions = get_user_permissions(current_user)
    return UserWithPermissions(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        is_active=current_user.is_active,
        permissions=permissions,
    )
