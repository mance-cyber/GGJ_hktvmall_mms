import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from app.config import settings
from sqlalchemy import create_engine, text

engine = create_engine(str(settings.DATABASE_URL))
with engine.connect() as conn:
    rows = conn.execute(text("""
        SELECT pa.alert_type, pa.old_value, pa.new_value, pa.change_percent,
               cp.product_name, cp.competitor_name, cp.url
        FROM price_alerts pa
        JOIN competitor_products cp ON pa.competitor_product_id = cp.id
        WHERE pa.created_at > NOW() - INTERVAL '1 hour'
        ORDER BY pa.created_at DESC
    """)).fetchall()
    if not rows:
        print("NO_ALERTS")
    for r in rows:
        print(f"TYPE={r[0]}|OLD={r[1]}|NEW={r[2]}|CHANGE={r[3]}|NAME={r[4]}|COMP={r[5]}|URL={r[6]}")
