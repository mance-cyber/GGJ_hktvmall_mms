import asyncio
from sqlalchemy import select, func, text
from app.models.database import async_session_maker
from app.models.competitor import PriceSnapshot

async def check():
    async with async_session_maker() as db:
        total = (await db.execute(select(func.count(PriceSnapshot.id)))).scalar()
        with_stock = (await db.execute(
            select(func.count(PriceSnapshot.id)).where(PriceSnapshot.stock_level.isnot(None))
        )).scalar()
        
        recent_sql = text(
            "SELECT stock_level, stock_status, count(*) "
            "FROM price_snapshots "
            "WHERE scraped_at > NOW() - INTERVAL '10 minutes' "
            "GROUP BY stock_level, stock_status"
        )
        recent = (await db.execute(recent_sql)).fetchall()
        
        # Sample some with stock
        sample_sql = text(
            "SELECT ps.stock_level, ps.stock_status, cp.name, cp.sku "
            "FROM price_snapshots ps "
            "JOIN competitor_products cp ON cp.id = ps.competitor_product_id "
            "WHERE ps.stock_level IS NOT NULL "
            "ORDER BY ps.scraped_at DESC LIMIT 10"
        )
        samples = (await db.execute(sample_sql)).fetchall()
        
        print(f"Total snapshots: {total}")
        print(f"With stock_level: {with_stock}")
        print(f"\nRecent batch (last 10 min):")
        for row in recent:
            print(f"  stock_level={row[0]}, status={row[1]}: {row[2]} rows")
        
        if samples:
            print(f"\nSample products with stock data:")
            for s in samples:
                print(f"  {s[2]} ({s[3]}): stock={s[0]}, status={s[1]}")
        else:
            print("\nNo products have stock_level data yet.")

asyncio.run(check())
