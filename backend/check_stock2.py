import asyncio
from sqlalchemy import select, func, desc
from app.models.database import async_session_maker
from app.models.competitor import PriceSnapshot

async def check():
    async with async_session_maker() as db:
        # Get the latest batch's scraped_at
        latest_time = (await db.execute(
            select(func.max(PriceSnapshot.scraped_at))
        )).scalar()
        print(f"Latest scraped_at: {latest_time}")
        
        # Count snapshots in latest batch (same scraped_at minute)
        from datetime import timedelta
        cutoff = latest_time - timedelta(minutes=5) if latest_time else None
        
        if cutoff:
            # Stats for latest batch
            result = await db.execute(
                select(
                    PriceSnapshot.stock_level,
                    func.count(PriceSnapshot.id)
                )
                .where(PriceSnapshot.scraped_at > cutoff)
                .group_by(PriceSnapshot.stock_level)
            )
            rows = result.fetchall()
            print(f"\nLatest batch (after {cutoff}):")
            for stock_level, count in rows:
                print(f"  stock_level={stock_level}: {count} rows")
            
            # Sample some with stock_level set
            result2 = await db.execute(
                select(PriceSnapshot)
                .where(PriceSnapshot.scraped_at > cutoff)
                .where(PriceSnapshot.stock_level.isnot(None))
                .limit(5)
            )
            samples = result2.scalars().all()
            if samples:
                print(f"\nSamples with stock_level:")
                for s in samples:
                    print(f"  id={s.id}, stock={s.stock_level}, status={s.stock_status}")
            
            # Total with stock_level ever
            total_with = (await db.execute(
                select(func.count(PriceSnapshot.id))
                .where(PriceSnapshot.stock_level.isnot(None))
            )).scalar()
            print(f"\nTotal snapshots with stock_level (all time): {total_with}")

asyncio.run(check())
