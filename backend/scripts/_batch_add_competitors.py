"""Batch add discovered competitors to DB"""
import sys, os, asyncio, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

from uuid import uuid4
from sqlalchemy import select
from app.models.database import async_session_maker
from app.models.competitor import Competitor
from app.connectors.hktv_api import HKTVApiClient

# Discovered competitors to add
NEW_COMPETITORS = [
    {"name": "森源屋", "tier": 1},
    {"name": "食尚煮意", "tier": 1},
    {"name": "炮台高級食材專門店", "tier": 1},
    {"name": "米之廊", "tier": 1},
    {"name": "漁信快訊", "tier": 2},
    {"name": "日本買好友站", "tier": 2},
    {"name": "Steak King Market", "tier": 2},
    {"name": "101 Gourmet Store", "tier": 2},
    {"name": "16蠔食品", "tier": 2},
    {"name": "口碑食品", "tier": 2},
    {"name": "蛋白質老爺", "tier": 2},
    {"name": "Cool Food", "tier": 2},
    {"name": "Galleon International Limited", "tier": 3},
    {"name": "四條新鮮", "tier": 3},
    {"name": "市集世界 Market Of All Nations", "tier": 3},
]


async def find_store_code(client, store_name):
    """Search for a store and extract its store code from product URLs"""
    products = await client.search_by_store(store_name, page_size=5)
    if not products:
        # Try keyword search
        products = await client.search_products(store_name, page_size=10)
        # Filter to only products from this store
        products = [p for p in products if p.store_name == store_name]
    
    if not products:
        return None, 0
    
    # Extract store code from product URL or SKU
    # HKTVmall SKU format: H{store_code}_{product_id} or similar
    sku = products[0].sku or ""
    store_code = None
    
    # Try to extract from SKU (format varies)
    if sku:
        # Common pattern: first part before underscore or dash
        parts = sku.replace('-', '_').split('_')
        if parts and parts[0].startswith('H'):
            store_code = parts[0]
    
    # If not found from SKU, try URL parsing
    if not store_code and products[0].url:
        url = products[0].url
        # /hktv/zh/main/... patterns contain store info
        # Try to find store code in URL path
        import re
        m = re.search(r'/([A-Z]\d+)/', url)
        if m:
            store_code = m.group(1)
    
    return store_code, len(products)


async def main():
    client = HKTVApiClient()
    
    print("=" * 60)
    print("批量加入競爭商戶")
    print("=" * 60)
    
    results = []
    for comp in NEW_COMPETITORS:
        store_code, product_count = await find_store_code(client, comp["name"])
        comp["store_code"] = store_code
        comp["product_count"] = product_count
        status = "OK" if store_code else "NO CODE"
        print(f"  [{status}] {comp['name']} -> store_code={store_code} ({product_count} products)")
        results.append(comp)
    
    await client.close()
    
    # Now add to DB
    print(f"\n--- 寫入 DB ---")
    async with async_session_maker() as db:
        added = 0
        skipped = 0
        no_code = 0
        
        for comp in results:
            # Check if exists
            stmt = select(Competitor).where(Competitor.name == comp["name"])
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()
            
            if existing:
                # Update tier and store_code if we found one
                if comp["store_code"] and not existing.store_code:
                    existing.store_code = comp["store_code"]
                    print(f"  UPDATE: {comp['name']} -> store_code={comp['store_code']}")
                else:
                    print(f"  SKIP: {comp['name']} (already exists)")
                skipped += 1
                continue
            
            if not comp["store_code"]:
                print(f"  WARN: {comp['name']} - no store_code found, adding anyway")
                no_code += 1
            
            competitor = Competitor(
                id=uuid4(),
                name=comp["name"],
                store_code=comp.get("store_code"),
                tier=comp["tier"],
                platform="hktvmall",
                is_active=True,
                notes=f"Auto-discovered. Products: ~{comp['product_count']}",
            )
            db.add(competitor)
            print(f"  ADD: {comp['name']} (Tier {comp['tier']}, code={comp.get('store_code')})")
            added += 1
        
        await db.commit()
    
    print(f"\n--- 完成 ---")
    print(f"  新增: {added}")
    print(f"  已存在: {skipped}")
    print(f"  無 store_code: {no_code}")


if __name__ == "__main__":
    asyncio.run(main())
