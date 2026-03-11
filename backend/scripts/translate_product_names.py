"""
Batch translate product names to English using OpenClaw Gateway API.
Usage: python backend/scripts/translate_product_names.py
"""
import asyncio
import httpx
import time
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

# Use the same DB config as the app
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from app.models.competitor import CompetitorProduct
from app.models.product import Product
from app.models.database import Base

DATABASE_URL = os.environ.get("DATABASE_URL", "")
if not DATABASE_URL:
    # Try to load from .env
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if line.startswith('DATABASE_URL='):
                    DATABASE_URL = line.split('=', 1)[1].strip().strip('"').strip("'")
                    break

if not DATABASE_URL:
    print("ERROR: DATABASE_URL not set")
    sys.exit(1)

# Ensure async driver
if 'postgresql://' in DATABASE_URL and '+asyncpg' not in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace('postgresql://', 'postgresql+asyncpg://')

GATEWAY_URL = "http://localhost:3377/v1/chat/completions"
BATCH_SIZE = 5
DELAY_BETWEEN_BATCHES = 1.0  # seconds


async def translate_name(client: httpx.AsyncClient, name: str) -> str:
    """Translate a single product name to English."""
    try:
        resp = await client.post(GATEWAY_URL, json={
            "model": "anthropic/claude-sonnet-4-5",
            "messages": [{"role": "user", "content": (
                f"Translate this HKTVmall product name to concise English. "
                f"Keep brand names, weights, and specs. Return ONLY the English name:\n{name}"
            )}],
            "max_tokens": 150,
        }, timeout=30.0)
        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"].strip().strip('"')
        else:
            print(f"  API error {resp.status_code}: {resp.text[:100]}")
            return None
    except Exception as e:
        print(f"  Translation error: {e}")
        return None


async def main():
    engine = create_async_engine(DATABASE_URL, echo=False)
    Session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with Session() as session:
        # 1. Competitor products without name_en
        result = await session.execute(
            select(CompetitorProduct)
            .where(CompetitorProduct.name_en.is_(None))
            .where(CompetitorProduct.is_active == True)
            .order_by(CompetitorProduct.created_at)
        )
        cp_products = result.scalars().all()
        print(f"Competitor products to translate: {len(cp_products)}")

        # 2. Own products without name_en
        result2 = await session.execute(
            select(Product)
            .where(Product.name_en.is_(None))
            .where(Product.status == "active")
        )
        own_products = result2.scalars().all()
        print(f"Own products to translate: {len(own_products)}")

        total = len(cp_products) + len(own_products)
        done = 0

        async with httpx.AsyncClient() as client:
            # Translate competitor products
            for i in range(0, len(cp_products), BATCH_SIZE):
                batch = cp_products[i:i+BATCH_SIZE]
                for cp in batch:
                    name_en = await translate_name(client, cp.name)
                    if name_en:
                        cp.name_en = name_en
                        done += 1
                        print(f"  [{done}/{total}] {cp.name} → {name_en}")
                    else:
                        done += 1
                        print(f"  [{done}/{total}] SKIP: {cp.name}")
                await session.commit()
                if i + BATCH_SIZE < len(cp_products):
                    time.sleep(DELAY_BETWEEN_BATCHES)

            # Translate own products
            for i in range(0, len(own_products), BATCH_SIZE):
                batch = own_products[i:i+BATCH_SIZE]
                for p in batch:
                    name_en = await translate_name(client, p.name)
                    if name_en:
                        p.name_en = name_en
                        done += 1
                        print(f"  [{done}/{total}] {p.name} → {name_en}")
                    else:
                        done += 1
                        print(f"  [{done}/{total}] SKIP: {p.name}")
                await session.commit()
                if i + BATCH_SIZE < len(own_products):
                    time.sleep(DELAY_BETWEEN_BATCHES)

    print(f"\nDone! Translated {done}/{total} products.")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
