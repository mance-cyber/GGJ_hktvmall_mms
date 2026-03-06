import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

DATABASE_URL = "postgresql+asyncpg://neondb_owner:npg_6TXrmNOqePM4@ep-ancient-brook-a1zdi9wo-pooler.ap-southeast-1.aws.neon.tech/neondb?ssl=require"
engine = create_async_engine(DATABASE_URL)

async def check():
    async with engine.connect() as conn:
        # When were inactive NULL-last_seen products created?
        r = await conn.execute(text(
            "SELECT date_trunc('day', created_at) as d, count(*) "
            "FROM competitor_products "
            "WHERE is_active = false AND last_seen_at IS NULL "
            "GROUP BY d ORDER BY d"
        ))
        print("=== Inactive + NULL last_seen_at by creation date ===")
        for row in r:
            print(row[0], row[1])

        # Also check: were there any DB migrations that bulk-set is_active?
        print("\n=== Inactive + HAS last_seen_at (monitor delisted) ===")
        r = await conn.execute(text(
            "SELECT date_trunc('day', last_seen_at) as d, count(*) "
            "FROM competitor_products "
            "WHERE is_active = false AND last_seen_at IS NOT NULL "
            "GROUP BY d ORDER BY d"
        ))
        for row in r:
            print(row[0], row[1])

        # Check the DB default
        print("\n=== Column default check ===")
        r = await conn.execute(text(
            "SELECT column_name, column_default "
            "FROM information_schema.columns "
            "WHERE table_name = 'competitor_products' AND column_name = 'is_active'"
        ))
        for row in r:
            print(f"column: {row[0]}, default: {row[1]}")

asyncio.run(check())
