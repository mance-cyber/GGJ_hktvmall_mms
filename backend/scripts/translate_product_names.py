"""
Batch translate product names to English using OpenClaw Gateway API.
SYNC version using psycopg2 + requests.
Supports --offset N --limit N for batch mode (used by wrapper for crash recovery).
"""
import os
import sys
import time
import traceback
import datetime
import argparse

# Fix Windows console encoding
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass
try:
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

# Load .env
env_path = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.env'))
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
    sys.exit(1)

GATEWAY_URL = os.environ.get("GATEWAY_URL", "http://localhost:18789/v1/chat/completions")
GATEWAY_TOKEN = os.environ.get("OPENCLAW_GATEWAY_TOKEN", "")

log_path = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logs', 'translate_error.log')
)
os.makedirs(os.path.dirname(log_path), exist_ok=True)


def log(msg):
    ts = datetime.datetime.now().strftime('%H:%M:%S')
    line = f"[{ts}] {msg}"
    try:
        print(line, flush=True)
    except Exception:
        pass
    try:
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(line + '\n')
    except Exception:
        pass


def parse_db_url(url):
    import urllib.parse
    url = url.replace('+asyncpg', '').replace('postgresql+psycopg2://', 'postgresql://')
    parsed = urllib.parse.urlparse(url)
    kwargs = {
        'host': parsed.hostname,
        'port': parsed.port or 5432,
        'dbname': parsed.path.lstrip('/'),
        'user': parsed.username,
        'password': parsed.password,
        'sslmode': 'require',
        'connect_timeout': 30,
    }
    qs = urllib.parse.parse_qs(parsed.query)
    if 'sslmode' in qs:
        kwargs['sslmode'] = qs['sslmode'][0]
    return kwargs


def get_conn():
    import psycopg2
    kwargs = parse_db_url(DATABASE_URL)
    for attempt in range(3):
        try:
            conn = psycopg2.connect(**kwargs)
            conn.autocommit = True
            return conn
        except Exception as e:
            log(f"  [DB connect attempt {attempt+1}/3 failed: {e}]")
            if attempt < 2:
                time.sleep(5)
    raise RuntimeError("Failed to connect to DB after 3 attempts")


def translate_name(name: str, retries: int = 3) -> str:
    import requests
    headers = {'Content-Type': 'application/json'}
    if GATEWAY_TOKEN:
        headers['Authorization'] = f"Bearer {GATEWAY_TOKEN}"

    for attempt in range(retries):
        try:
            resp = requests.post(GATEWAY_URL, headers=headers, json={
                "model": "anthropic/claude-sonnet-4-6",
                "messages": [{"role": "user", "content": (
                    f"Translate this HKTVmall product name to concise English. "
                    f"Keep brand names, weights, and specs. Return ONLY the English name:\n{name}"
                )}],
                "max_tokens": 150,
            }, timeout=60)

            if resp.status_code == 200:
                try:
                    return resp.json()["choices"][0]["message"]["content"].strip().strip('"')
                except (KeyError, IndexError, ValueError) as e:
                    log(f"  Unexpected API response structure: {e}")
                    return None
            elif resp.status_code in (502, 503, 429):
                wait = (attempt + 1) * 5
                log(f"  API {resp.status_code}, retry {attempt+1}/{retries} in {wait}s")
                time.sleep(wait)
            else:
                log(f"  API error {resp.status_code}: {resp.text[:100]}")
                return None
        except Exception as e:
            log(f"  Translate error (attempt {attempt+1}): {e}")
            if attempt < retries - 1:
                time.sleep(10)  # longer backoff to avoid Gateway overload
    return None


_ALLOWED_TABLES = frozenset({"competitor_products", "products"})


def db_write(table, item_id, name_en):
    """Fresh connection per write — sidesteps any idle timeout."""
    if table not in _ALLOWED_TABLES:
        log(f"  Rejected invalid table name: {table}")
        return False
    for attempt in range(3):
        conn = None
        try:
            conn = get_conn()
            cur = conn.cursor()
            cur.execute(f"UPDATE {table} SET name_en = %s WHERE id = %s", (name_en, item_id))
            cur.close()
            conn.close()
            return True
        except Exception as e:
            log(f"  DB write attempt {attempt+1}/3 failed: {e}")
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass
            if attempt < 2:
                time.sleep(2)
    return False


def fetch_todo():
    """Fetch all items that still need translation."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, name FROM competitor_products WHERE name_en IS NULL AND is_active = true ORDER BY id"
    )
    cp_rows = cur.fetchall()
    cur.execute(
        "SELECT id, name FROM products WHERE name_en IS NULL AND status = 'active' ORDER BY id"
    )
    own_rows = cur.fetchall()
    cur.close()
    conn.close()
    return [('competitor_products', r) for r in cp_rows] + [('products', r) for r in own_rows]


import threading

class RateLimiter:
    """線程安全的令牌桶限速器。"""
    def __init__(self, max_per_second: float):
        self._interval = 1.0 / max_per_second
        self._lock = threading.Lock()
        self._last = 0.0

    def acquire(self):
        with self._lock:
            now = time.time()
            wait = self._last + self._interval - now
            if wait > 0:
                time.sleep(wait)
            self._last = time.time()

_rate_limiter = RateLimiter(max_per_second=2)  # 每秒最多 2 個請求


def _translate_one(idx, batch_total, table, item_id, name):
    """翻譯單個商品（供並行調用，含限速）。"""
    _rate_limiter.acquire()
    done = idx + 1
    try:
        name_en = translate_name(name)
    except Exception as e:
        log(f"  [{done}/{batch_total}] translate exception: {e}")
        return False

    if name_en:
        saved = db_write(table, item_id, name_en)
        if saved:
            try:
                log(f"  [{done}/{batch_total}] {name} → {name_en}")
            except Exception:
                log(f"  [{done}/{batch_total}] [saved to {table} id={item_id}]")
            return True
        else:
            log(f"  [{done}/{batch_total}] WRITE FAILED for id={item_id}")
    else:
        log(f"  [{done}/{batch_total}] SKIP (no translation) for id={item_id}")
    return False


def main():
    from concurrent.futures import ThreadPoolExecutor, as_completed

    parser = argparse.ArgumentParser()
    parser.add_argument('--offset', type=int, default=0, help='Start from item N (0-indexed)')
    parser.add_argument('--limit', type=int, default=0, help='Process at most N items (0=all)')
    parser.add_argument('--workers', type=int, default=5, help='Parallel worker threads (default 5)')
    args = parser.parse_args()

    log(f"Fetching items to translate (offset={args.offset}, limit={args.limit}, workers={args.workers})...")
    all_items = fetch_todo()
    total_remaining = len(all_items)
    log(f"Total remaining: {total_remaining}")

    # Slice to batch
    items = all_items[args.offset:]
    if args.limit > 0:
        items = items[:args.limit]

    batch_total = len(items)
    log(f"This batch: {batch_total} items (parallel={args.workers})")

    if batch_total == 0:
        log("Nothing to do!")
        return

    translated = 0
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {
            pool.submit(_translate_one, idx, batch_total, table, item_id, name): idx
            for idx, (table, (item_id, name)) in enumerate(items)
        }
        for future in as_completed(futures):
            if future.result():
                translated += 1

    log(f"Batch done: translated {translated}/{batch_total}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("Interrupted by user.")
        sys.exit(0)
    except Exception as e:
        log(f"FATAL ({type(e).__name__}): {e}\n{traceback.format_exc()}")
        sys.exit(1)
