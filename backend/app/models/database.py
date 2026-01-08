# =============================================
# 數據庫連接設定
# =============================================

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text

from app.config import get_settings


class Base(DeclarativeBase):
    """SQLAlchemy 基礎類"""
    pass


# 創建異步引擎
settings = get_settings()

# 將 postgresql:// 轉換為 postgresql+asyncpg://
db_url = settings.database_url.replace("postgresql://", "postgresql+asyncpg://")

engine = create_async_engine(
    db_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
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
    """手動執行 Schema 遷移 (MVP 簡易版)"""
    try:
        # Add columns to products table if they don't exist
        # We use IF NOT EXISTS logic via checking information_schema or just ignoring errors
        
        # PostgreSQL specific: Add columns if not exist
        # This is a bit hacky but works for MVP without Alembic
        alter_statements = [
            "ALTER TABLE products ADD COLUMN IF NOT EXISTS min_price NUMERIC(10, 2);",
            "ALTER TABLE products ADD COLUMN IF NOT EXISTS max_price NUMERIC(10, 2);",
            "ALTER TABLE products ADD COLUMN IF NOT EXISTS auto_pricing_enabled BOOLEAN DEFAULT FALSE;",
            "ALTER TABLE products ADD COLUMN IF NOT EXISTS cost NUMERIC(10, 2);"
        ]
        
        for stmt in alter_statements:
            try:
                await conn.execute(text(stmt))
            except Exception as e:
                # Column might already exist or other issue
                print(f"Migration warning: {e}")
                
    except Exception as e:
        print(f"Migration failed: {e}")


async def init_db():
    """初始化數據庫（創建表 + 遷移）"""
    # Import all models here so Alembic/create_all can find them
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
        pricing
    )
    
    try:
        async with engine.begin() as conn:
            # 1. Create new tables (like price_proposals)
            await conn.run_sync(Base.metadata.create_all, checkfirst=True)
            
            # 2. Migrate existing tables (add columns to products)
            await run_migrations(conn)
            
    except Exception as e:
        print(f"Database initialization error (ignored): {e}")
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
