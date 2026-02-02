# =============================================
# 測試配置和 Fixtures
# =============================================

import os
import pytest
import pytest_asyncio
import asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import patch, MagicMock

# 設置測試環境變數（必須在 import app 之前）
os.environ["APP_ENV"] = "development"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"
os.environ["REDIS_URL"] = "redis://localhost:6379/1"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-purposes-only-32chars"

from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.dialects.sqlite.base import SQLiteTypeCompiler

# 為 SQLite 添加 JSONB 和 UUID 支持
# SQLite 不原生支持 PostgreSQL 的 JSONB 和 UUID 類型
# 這裡將它們映射為 SQLite 兼容的類型
_original_visit_JSON = SQLiteTypeCompiler.visit_JSON

def visit_JSONB(self, type_, **kw):
    """將 JSONB 編譯為 JSON"""
    return "JSON"

def visit_UUID(self, type_, **kw):
    """將 UUID 編譯為 VARCHAR(36)"""
    return "VARCHAR(36)"

SQLiteTypeCompiler.visit_JSONB = visit_JSONB
SQLiteTypeCompiler.visit_UUID = visit_UUID

from app.main import app
from app.models.database import Base, get_db
from app.models.user import User
from app.core.security import create_access_token, get_password_hash


# =============================================
# 數據庫 Fixtures
# =============================================

# 測試用的 SQLite 內存數據庫
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """創建 event loop 給整個測試 session 使用"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """為每個測試創建獨立的數據庫 session"""
    # 創建所有表
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        yield session

    # 清理表
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """創建測試用的 HTTP 客戶端"""

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


# =============================================
# 用戶和認證 Fixtures
# =============================================

@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    """創建測試用戶"""
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpassword123"),
        full_name="Test User",
        role="operator",
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def admin_user(db_session: AsyncSession) -> User:
    """創建管理員用戶"""
    user = User(
        email="admin@example.com",
        hashed_password=get_password_hash("adminpassword123"),
        full_name="Admin User",
        role="admin",
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user: User) -> dict:
    """生成認證 headers"""
    token = create_access_token(subject=str(test_user.id), role=test_user.role)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_auth_headers(admin_user: User) -> dict:
    """生成管理員認證 headers"""
    token = create_access_token(subject=str(admin_user.id), role=admin_user.role)
    return {"Authorization": f"Bearer {token}"}


# =============================================
# Mock Fixtures
# =============================================

@pytest.fixture
def mock_redis():
    """Mock Redis 客戶端"""
    with patch("app.services.rate_limiter.redis") as mock:
        mock.get = MagicMock(return_value=None)
        mock.set = MagicMock(return_value=True)
        mock.incr = MagicMock(return_value=1)
        mock.expire = MagicMock(return_value=True)
        yield mock


@pytest.fixture
def mock_ai_service():
    """Mock AI 服務"""
    with patch("app.services.ai_service.AIAnalysisService") as mock:
        instance = MagicMock()
        instance.call_ai = MagicMock(return_value={
            "success": True,
            "content": "Test AI response",
            "model": "test-model",
            "tokens_used": 100,
        })
        mock.return_value = instance
        yield instance
