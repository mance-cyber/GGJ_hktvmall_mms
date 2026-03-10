import sqlite3

conn = sqlite3.connect('gogojap.db')
cur = conn.cursor()

# List tables
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cur.fetchall()]
print("Tables:", tables)

# Show schema for relevant tables
for t in tables:
    cur.execute(f"SELECT sql FROM sqlite_master WHERE name='{t}'")
    sql = cur.fetchone()[0]
    if sql and ('stock' in sql.lower() or 'competitor' in sql.lower() or 'price' in sql.lower() or 'product' in sql.lower() or 'merchant' in sql.lower()):
        print(f"\n--- {t} ---")
        print(sql[:500])

# Find stock data
for t in tables:
    try:
        cur.execute(f"PRAGMA table_info({t})")
        cols = [r[1] for r in cur.fetchall()]
        if 'stock_level' in cols:
            print(f"\n=== {t} has stock_level ===")
            cur.execute(f"SELECT count(*) FROM {t} WHERE stock_level IS NOT NULL")
            print(f"  Non-null stock_level rows: {cur.fetchone()[0]}")
            cur.execute(f"SELECT * FROM {t} WHERE stock_level IS NOT NULL LIMIT 5")
            rows = cur.fetchall()
            print(f"  Columns: {cols}")
            for r in rows:
                print(f"  {r}")
    except Exception as e:
        print(f"  Error on {t}: {e}")

conn.close()
