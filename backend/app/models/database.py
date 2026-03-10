# =============================================
# 數據庫連接設定
# =============================================

import logging
import ssl
from datetime import datetime, timezone
from typing import AsyncGenerator
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings

logger = logging.getLogger(__name__)


# =============================================
# UTC 時間工具函數
# =============================================

def utcnow() -> datetime:
    """
    獲取 UTC 時間（返回 naive datetime 以兼容 TIMESTAMP WITHOUT TIME ZONE）

    注意：返回的是 UTC 時間，但不帶 tzinfo
    這樣可以直接存入 PostgreSQL 的 TIMESTAMP WITHOUT TIME ZONE 欄位
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Base(DeclarativeBase):
    """SQLAlchemy 基礎類"""
    pass


# 創建異步引擎
settings = get_settings()


def _prepare_async_url(url: str) -> tuple[str, dict]:
    """
    將 DATABASE_URL 轉為 asyncpg 兼容格式

    asyncpg 不認 sslmode / channel_binding 等 libpq 參數，
    需要從 URL 中剝離，改用 connect_args 傳入 SSL 上下文。
    """
    async_url = url.replace("postgresql://", "postgresql+asyncpg://")
    parsed = urlparse(async_url)
    params = parse_qs(parsed.query)

    # 檢測是否需要 SSL
    needs_ssl = "sslmode" in params and params["sslmode"][0] in ("require", "verify-ca", "verify-full")

    # 移除 asyncpg 不認識的 libpq 參數
    for key in ("sslmode", "channel_binding"):
        params.pop(key, None)

    clean_url = urlunparse(parsed._replace(query=urlencode(params, doseq=True)))

    connect_args = {
        # Neon 用 pgbouncer 連接池，不支援 prepared statements；
        # 禁用 asyncpg 客戶端快取避免 schema 變更後 InvalidCachedStatementError
        "statement_cache_size": 0,
        "prepared_statement_cache_size": 0,
    }
    if needs_ssl:
        ssl_ctx = ssl.create_default_context()
        # 使用系統 CA 驗證 Neon DB 的 SSL 憑證（正規 CA-signed cert）
        connect_args["ssl"] = ssl_ctx

    return clean_url, connect_args


db_url, connect_args = _prepare_async_url(settings.database_url)

engine = create_async_engine(
    db_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    pool_recycle=120,  # Neon serverless: recycle connections every 2 min
    connect_args=connect_args,
)

# 創建異步 session 工廠
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def run_migrations(conn):
    """
    啟動時 Schema 補丁（僅處理 Alembic 未覆蓋的基礎設施）。
    所有業務欄位變更應使用 alembic/versions/ 管理。
    """
    try:
        # 僅保留 pg_trgm extension（Alembic 不方便處理 CREATE EXTENSION）
        infra_statements = [
            "CREATE EXTENSION IF NOT EXISTS pg_trgm;",
            "CREATE INDEX IF NOT EXISTS idx_cp_name_trgm ON competitor_products USING GIN (name gin_trgm_ops);",
        ]
        for stmt in infra_statements:
            try:
                await conn.execute(text(stmt))
            except Exception as e:
                logger.warning(f"Migration infra warning: {e}")
    except Exception as e:
        logger.error(f"Migration failed: {e}", exc_info=True)


async def init_db():
    """初始化數據庫（創建表 + 遷移）"""
    from app.models import (
        competitor,
        product,
        notification,
        scrape_config,
        import_job,
        analytics,
        content,
        category,
        system,
        pricing,
        order,
        inbox,
        finance,
        promotion,
        user,
        seo,
        seo_ranking,
        pipeline_task,
    )
    
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all, checkfirst=True)
            await run_migrations(conn)
            
    except Exception as e:
        logger.warning(f"Database initialization error (ignored): {e}")
        pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """獲取數據庫 session（依賴注入）"""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
