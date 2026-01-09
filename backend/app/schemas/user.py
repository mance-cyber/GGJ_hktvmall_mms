# =============================================
# 用戶 Schema
# =============================================

from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID
from app.models.user import UserRole

# Shared properties
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = UserRole.VIEWER
    is_active: Optional[bool] = True

# Properties to receive via API on creation
class UserCreate(UserBase):
    email: EmailStr
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
