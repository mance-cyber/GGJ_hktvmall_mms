import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.config import settings
from sqlalchemy import create_engine, text

engine = create_engine(str(settings.database_url))
with engine.connect() as conn:
    rows = conn.execute(text("""
        SELECT pa.alert_type, pa.old_value, pa.new_value, pa.change_percent,
               cp.name, c.name as competitor_name
        FROM price_alerts pa
        JOIN competitor_products cp ON pa.competitor_product_id = cp.id
        JOIN competitors c ON cp.competitor_id = c.id
        WHERE pa.created_at > NOW() - INTERVAL '2 hours'
        ORDER BY pa.alert_type, pa.change_percent DESC NULLS LAST
    """)).fetchall()
    print(f"TOTAL: {len(rows)}")
    for r in rows:
        chg = f"{r[3]:.1f}%" if r[3] else "N/A"
        name = r[4][:40] if r[4] else "?"
        print(f"{r[0]}|{r[1]}|{r[2]}|{chg}|{name}|{r[5]}")
