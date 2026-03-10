"""
Resolve real store names for placeholder competitors using HKTVApiClient.
Run from backend/ directory.
"""
import sys, os, asyncio
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv; load_dotenv()
import sqlalchemy
from app.connectors.hktv_api import get_hktv_api_client

engine = sqlalchemy.create_engine(os.environ['DATABASE_URL'].replace('postgresql+asyncpg://', 'postgresql://'))
DRY_RUN = '--dry-run' in sys.argv

async def main():
    client = get_hktv_api_client()
    
    with engine.begin() as conn:
        r = conn.execute(sqlalchemy.text(
            "SELECT id, name, store_code FROM competitors WHERE name LIKE 'Store %' ORDER BY store_code"
        ))
        placeholders = r.fetchall()
        print(f"Resolving {len(placeholders)} placeholder competitors...\n")
        
        resolved = 0
        failed = []
        
        for cid, current_name, store_code in placeholders:
            try:
                products = await client.search_by_store_code(store_code, page_size=1)
            except Exception as e:
                print(f"  ❌ {store_code}: search error — {e}")
                failed.append(store_code)
                continue
            
            store_name = None
            if products:
                p = products[0]
                # Try various attrs for store name
                for attr in ['store_name', 'storeName', 'merchant_name', 'merchantName']:
                    store_name = getattr(p, attr, None)
                    if store_name:
                        break
                if not store_name:
                    # Try raw dict
                    raw = getattr(p, 'raw', {}) or {}
                    for key in ['storeName', 'store_name', 'merchantName', 'merchant_name']:
                        store_name = raw.get(key)
                        if store_name:
                            break
                if not store_name:
                    # Last resort: use category path or brand
                    store_name = getattr(p, 'brand', None)
            
            if store_name:
                if not DRY_RUN:
                    conn.execute(sqlalchemy.text(
                        "UPDATE competitors SET name = :name, updated_at = NOW() WHERE id = :id"
                    ), {'name': store_name, 'id': str(cid)})
                resolved += 1
                action = '→' if not DRY_RUN else '(would set)'
                print(f"  ✅ {store_code}: {current_name} {action} {store_name}")
            else:
                failed.append(store_code)
                hint = f"[{products[0].name[:40]}]" if products else "[no products found]"
                print(f"  ❌ {store_code}: no store name attr {hint}")
        
        print(f"\n{'='*50}")
        print(f"✅ Resolved: {resolved}/{len(placeholders)}")
        if failed:
            print(f"❌ Still missing: {', '.join(failed)}")
        if DRY_RUN:
            print("⚠️ DRY RUN — run without --dry-run to apply")
    
    if hasattr(client, 'aclose'):
        await client.aclose()
    elif hasattr(client, 'close'):
        await client.close()

asyncio.run(main())
