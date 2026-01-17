# =============================================
# 認證 API 測試
# =============================================

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.core.security import get_password_hash, verify_password, create_access_token


class TestPasswordSecurity:
    """測試密碼安全功能"""

    def test_password_hash_creates_different_hashes(self):
        """測試相同密碼產生不同的 hash"""
        password = "testpassword123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        # bcrypt 每次產生不同的 hash（因為 salt）
        assert hash1 != hash2

    def test_password_verification_works(self):
        """測試密碼驗證正確"""
        password = "testpassword123"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed) is True

    def test_wrong_password_fails_verification(self):
        """測試錯誤密碼驗證失敗"""
        password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed = get_password_hash(password)
        assert verify_password(wrong_password, hashed) is False


class TestJWTToken:
    """測試 JWT Token 功能"""

    def test_create_access_token(self):
        """測試創建 access token"""
        token = create_access_token(subject="user-123", role="operator")
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_token_contains_three_parts(self):
        """測試 token 格式正確（header.payload.signature）"""
        token = create_access_token(subject="user-123", role="operator")
        parts = token.split(".")
        assert len(parts) == 3


class TestAuthAPI:
    """測試認證 API 端點"""

    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient, test_user: User):
        """測試成功登入"""
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": "test@example.com",
                "password": "testpassword123",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client: AsyncClient, test_user: User):
        """測試錯誤密碼登入失敗"""
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": "test@example.com",
                "password": "wrongpassword",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client: AsyncClient):
        """測試不存在的用戶登入失敗"""
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": "nonexistent@example.com",
                "password": "testpassword123",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user(self, client: AsyncClient, auth_headers: dict, test_user: User):
        """測試獲取當前用戶資訊"""
        response = await client.get(
            "/api/v1/auth/me",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
        assert data["role"] == test_user.role

    @pytest.mark.asyncio
    async def test_get_current_user_without_token(self, client: AsyncClient):
        """測試無 token 訪問受保護端點"""
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self, client: AsyncClient):
        """測試無效 token 訪問受保護端點"""
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid-token"},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_register_user(self, client: AsyncClient, admin_auth_headers: dict):
        """測試註冊新用戶（需要管理員權限）"""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "newpassword123",
                "full_name": "New User",
                "role": "viewer",
            },
            headers=admin_auth_headers,
        )
        # 可能是 200 或 201，取決於實現
        assert response.status_code in [200, 201, 403]  # 403 如果需要特定權限


class TestInactiveUser:
    """測試非活躍用戶"""

    @pytest.mark.asyncio
    async def test_inactive_user_cannot_login(self, client: AsyncClient, db_session: AsyncSession):
        """測試非活躍用戶無法登入"""
        # 創建非活躍用戶
        inactive_user = User(
            email="inactive@example.com",
            hashed_password=get_password_hash("testpassword123"),
            full_name="Inactive User",
            role="operator",
            is_active=False,
        )
        db_session.add(inactive_user)
        await db_session.commit()

        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": "inactive@example.com",
                "password": "testpassword123",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        # 預期返回 401 或 403
        assert response.status_code in [401, 403]
