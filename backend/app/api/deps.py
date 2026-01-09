# =============================================
# API 依賴注入 - 認證與權限檢查
# =============================================

from typing import List
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.database import get_db
from app.models.user import User, UserRole
from app.schemas.user import TokenPayload
from app.core.security import ALGORITHM
from app.config import settings


# =============================================
# 權限定義矩陣
# =============================================

# 各角色權限映射
ROLE_PERMISSIONS = {
    UserRole.ADMIN: {
        # 系統管理
        "system:settings:read",
        "system:settings:write",
        "system:users:read",
        "system:users:write",
        "system:users:delete",
        # 競品監測
        "competitors:read",
        "competitors:write",
        "competitors:delete",
        # 價格調整
        "prices:read",
        "prices:write",
        "prices:approve",
        # 訂單管理
        "orders:read",
        "orders:write",
        # AI Agent
        "agent:read",
        "agent:execute",
        "agent:admin",
        # 報表
        "reports:read",
        "reports:export",
        # 通知
        "notifications:read",
        "notifications:write",
        "notifications:settings",
    },
    UserRole.OPERATOR: {
        # 競品監測
        "competitors:read",
        "competitors:write",
        # 價格調整
        "prices:read",
        "prices:write",
        # 訂單管理
        "orders:read",
        "orders:write",
        # AI Agent
        "agent:read",
        "agent:execute",
        # 報表
        "reports:read",
        "reports:export",
        # 通知
        "notifications:read",
    },
    UserRole.VIEWER: {
        # 競品監測 (只讀)
        "competitors:read",
        # 價格調整 (只讀)
        "prices:read",
        # 訂單管理 (只讀)
        "orders:read",
        # AI Agent (只讀)
        "agent:read",
        # 報表 (只讀)
        "reports:read",
        # 通知 (只讀)
        "notifications:read",
    },
}


# =============================================
# OAuth2 設定
# =============================================

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"/api/v1/auth/login"
)


# =============================================
# 基本認證依賴
# =============================================

async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(reusable_oauth2)
) -> User:
    """獲取當前登入用戶"""
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )

    result = await db.execute(select(User).where(User.id == token_data.sub))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """獲取當前活躍用戶"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# =============================================
# 角色檢查依賴
# =============================================

def get_current_active_superuser(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """要求管理員權限"""
    if not current_user.is_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理員權限"
        )
    return current_user


def require_roles(*allowed_roles: UserRole):
    """
    工廠函數：生成角色檢查依賴

    使用方式:
        @router.get("/endpoint")
        async def endpoint(user: User = Depends(require_roles(UserRole.ADMIN, UserRole.OPERATOR))):
            ...
    """
    async def role_checker(
        current_user: User = Depends(get_current_active_user)
    ) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"需要以下角色之一: {', '.join(r.value for r in allowed_roles)}"
            )
        return current_user
    return role_checker


# =============================================
# 權限檢查依賴
# =============================================

def has_permission(user: User, permission: str) -> bool:
    """檢查用戶是否擁有指定權限"""
    user_permissions = ROLE_PERMISSIONS.get(user.role, set())
    return permission in user_permissions


def require_permissions(*permissions: str):
    """
    工廠函數：生成權限檢查依賴

    使用方式:
        @router.post("/prices/approve")
        async def approve_price(user: User = Depends(require_permissions("prices:approve"))):
            ...
    """
    async def permission_checker(
        current_user: User = Depends(get_current_active_user)
    ) -> User:
        user_permissions = ROLE_PERMISSIONS.get(current_user.role, set())
        missing_permissions = [p for p in permissions if p not in user_permissions]

        if missing_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"缺少權限: {', '.join(missing_permissions)}"
            )
        return current_user
    return permission_checker


def require_any_permission(*permissions: str):
    """
    工廠函數：生成權限檢查依賴（滿足任一權限即可）

    使用方式:
        @router.get("/data")
        async def get_data(user: User = Depends(require_any_permission("data:read", "data:admin"))):
            ...
    """
    async def permission_checker(
        current_user: User = Depends(get_current_active_user)
    ) -> User:
        user_permissions = ROLE_PERMISSIONS.get(current_user.role, set())

        if not any(p in user_permissions for p in permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"需要以下權限之一: {', '.join(permissions)}"
            )
        return current_user
    return permission_checker


# =============================================
# 便捷依賴別名
# =============================================

# 管理員專用
AdminRequired = Depends(require_roles(UserRole.ADMIN))

# 操作員及以上
OperatorRequired = Depends(require_roles(UserRole.ADMIN, UserRole.OPERATOR))

# 所有已登入用戶
ViewerRequired = Depends(get_current_active_user)


# =============================================
# API 返回用戶權限
# =============================================

def get_user_permissions(user: User) -> List[str]:
    """獲取用戶的所有權限列表"""
    return list(ROLE_PERMISSIONS.get(user.role, set()))
