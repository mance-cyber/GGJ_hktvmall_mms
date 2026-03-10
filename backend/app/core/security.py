# =============================================
# 安全工具 (Hash/JWT)
# =============================================

import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Union
from jose import jwt
from passlib.context import CryptContext
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 小時
REFRESH_TOKEN_EXPIRE_DAYS = 30   # Refresh token 30 天


def create_access_token(subject: Union[str, Any], role: str) -> str:
    """創建 JWT access token（短壽命）"""
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(subject), "role": role, "type": "access"}
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token() -> str:
    """創建 opaque refresh token（長壽命，存 DB 可 revoke）"""
    return secrets.token_urlsafe(64)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
