# =============================================
# 用戶 Schema
# =============================================

from pydantic import BaseModel, EmailStr, field_validator
from pydantic_core import PydanticCustomError
from typing import Optional
from uuid import UUID
from app.models.user import UserRole
import re

# Shared properties
class UserBase(BaseModel):
    email: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = UserRole.VIEWER
    is_active: Optional[bool] = True

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        # 簡單的郵箱格式驗證，允許 .local 等開發域名
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, v):
            raise PydanticCustomError(
                'value_error',
                'Invalid email format',
            )
        return v

# Properties to receive via API on creation
class UserCreate(UserBase):
    email: str
    password: str
    role: UserRole = UserRole.VIEWER

# Properties to receive via API on update
class UserUpdate(UserBase):
    password: Optional[str] = None

class UserInDBBase(UserBase):
    id: UUID
    
    class Config:
        from_attributes = True

# Additional properties to return via API
class User(UserInDBBase):
    pass


# User with permissions (for /me endpoint)
class UserWithPermissions(UserInDBBase):
    permissions: list[str] = []

# Additional properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[str] = None
    role: Optional[str] = None

class GoogleLogin(BaseModel):
    credential: str
