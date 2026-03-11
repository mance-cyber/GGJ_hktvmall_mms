"""
Batch translate product names to English using OpenClaw Gateway API.
Usage: python backend/scripts/translate_product_names.py
"""
import asyncio
import httpx
import time
import os
import ssl
import sys

# Fix Windows console encoding + unbuffered output
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')
os.environ['PYTHONUNBUFFERED'] = '1'

# Load .env
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
if os.path.exists(env_path):
    with open(env_path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                k, v = line.split('=', 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

DATABASE_URL = os.environ.get("DATABASE_URL", "")
if not DATABASE_URL:
    print("ERROR: DATABASE_URL not set")
    exit(1)

GATEWAY_URL = os.environ.get("GATEWAY_URL", "http://localhost:18789/v1/chat/completions")
GATEWAY_TOKEN = os.environ.get("OPENCLAW_GATEWAY_TOKEN", "")
BATCH_SIZE = 5
DELAY = 1.0


async def translate_name(client: httpx.AsyncClient, name: str, retries: int = 3) -> str:
    headers = {}
    if GATEWAY_TOKEN:
        headers["Authorization"] = f"Bearer {GATEWAY_TOKEN}"
    for attempt in range(retries):
        try:
            resp = await client.post(GATEWAY_URL, headers=headers, json={
                "model": "anthropic/claude-sonnet-4-6",
                "messages": [{"role": "user", "content": (
                    f"Translate this HKTVmall product name to concise English. "
                    f"Keep brand names, weights, and specs. Return ONLY the English name:\n{name}"
                )}],
                "max_tokens": 150,
            }, timeout=30.0)
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"].strip().strip('"')
            elif resp.status_code in (502, 503, 429):
                wait = (attempt + 1) * 3
                print(f"  Retry {attempt+1}/{retries} after {resp.status_code}, waiting {wait}s...")
                await asyncio.sleep(wait)
                continue
            else:
                print(f"  API error {resp.status_code}")
                return None
        except Exception as e:
            if attempt < retries - 1:
                await asyncio.sleep(3)
                continue
            print(f"  Error: {e}")
            return None
    return None


async def main():
    import asyncpg

    # Parse URL for asyncpg (handle sslmode)
    url = DATABASE_URL.replace('+asyncpg', '')
    if url.startswith('postgresql://'):
        url = url.replace('postgresql://', 'postgres://')

    # Connect with SSL
    ssl_ctx = ssl.create_default_context()
    ssl_ctx.check_hostname = False
    ssl_ctx.verify_mode = ssl.CERT_NONE

    # Remove sslmode from URL if present
    if '?sslmode=' in url:
        url = url.split('?sslmode=')[0]

    print("Connecting to database...")
    conn = await asyncio.wait_for(asyncpg.connect(url, ssl=ssl_ctx), timeout=30)
    print("Connected!")

    # Get competitor products without name_en
    cp_rows = await conn.fetch(
        "SELECT id, name FROM competitor_products WHERE name_en IS NULL AND is_active = true ORDER BY created_at"
    )
    print(f"Competitor products to translate: {len(cp_rows)}")

    # Get own products without name_en
    own_rows = await conn.fetch(
        "SELECT id, name FROM products WHERE name_en IS NULL AND status = 'active' ORDER BY created_at"
    )
    print(f"Own products to translate: {len(own_rows)}")

    total = len(cp_rows) + len(own_rows)
    done = 0
    translated = 0

    async with httpx.AsyncClient() as client:
        # Competitor products
        for i in range(0, len(cp_rows), BATCH_SIZE):
            batch = cp_rows[i:i+BATCH_SIZE]
            for row in batch:
                try:
                    name_en = await translate_name(client, row['name'])
                    done += 1
                    if name_en:
                        await conn.execute(
                            "UPDATE competitor_products SET name_en = $1 WHERE id = $2",
                            name_en, row['id']
                        )
                        translated += 1
                        try:
                            print(f"  [{done}/{total}] {row['name']} → {name_en}", flush=True)
                        except Exception:
                            print(f"  [{done}/{total}] [name_en saved]", flush=True)
                    else:
                        print(f"  [{done}/{total}] SKIP", flush=True)
                except Exception as e:
                    done += 1
                    print(f"  [{done}/{total}] ERROR: {e}", flush=True)
            if i + BATCH_SIZE < len(cp_rows):
                await asyncio.sleep(DELAY)

        # Own products
        for i in range(0, len(own_rows), BATCH_SIZE):
            batch = own_rows[i:i+BATCH_SIZE]
            for row in batch:
                try:
                    name_en = await translate_name(client, row['name'])
                    done += 1
                    if name_en:
                        await conn.execute(
                            "UPDATE products SET name_en = $1 WHERE id = $2",
                            name_en, row['id']
                        )
                        translated += 1
                        try:
                            print(f"  [{done}/{total}] {row['name']} → {name_en}", flush=True)
                        except Exception:
                            print(f"  [{done}/{total}] [own name_en saved]", flush=True)
                    else:
                        print(f"  [{done}/{total}] SKIP", flush=True)
                except Exception as e:
                    done += 1
                    print(f"  [{done}/{total}] ERROR: {e}", flush=True)
            if i + BATCH_SIZE < len(own_rows):
                await asyncio.sleep(DELAY)

    await conn.close()
    print(f"\nDone! Translated {translated}/{total} products.")

if __name__ == "__main__":
    asyncio.run(main())
