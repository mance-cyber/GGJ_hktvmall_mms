import sys, os, json
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(__file__))
from app.config import settings
from sqlalchemy import create_engine, text

engine = create_engine(str(settings.database_url))
with engine.connect() as conn:
    rows = conn.execute(text("""
        SELECT pa.alert_type, pa.old_value, pa.new_value, pa.change_percent,
               cp.name, c.name as competitor_name, pa.created_at
        FROM price_alerts pa
        JOIN competitor_products cp ON pa.competitor_product_id = cp.id
        JOIN competitors c ON cp.competitor_id = c.id
        WHERE pa.created_at > NOW() - INTERVAL '2 hours'
        ORDER BY pa.created_at DESC
    """)).fetchall()
    
    if not rows:
        print("NO_ALERTS")
    else:
        print(f"ALERT_COUNT: {len(rows)}")
        seen = set()
        for r in rows:
            key = (r[0], r[4], r[5])
            if key not in seen:
                seen.add(key)
                print(json.dumps({
                    "type": r[0],
                    "old": r[1],
                    "new": r[2],
                    "change_pct": str(r[3]) if r[3] else None,
                    "name": r[4][:50] if r[4] else "",
                    "competitor": r[5],
                    "at": str(r[6])
                }, ensure_ascii=False))
