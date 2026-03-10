import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from app.config import settings
from sqlalchemy import create_engine, text

engine = create_engine(str(settings.database_url))
with engine.connect() as conn:
    # Get column names first
    cols = conn.execute(text(
        "SELECT column_name FROM information_schema.columns WHERE table_name='competitor_products' ORDER BY ordinal_position"
    )).fetchall()
    print("COLUMNS:", [c[0] for c in cols])
    
    # Get recent alerts - join with competitors for merchant name
    rows = conn.execute(text("""
        SELECT pa.alert_type, pa.old_value, pa.new_value, pa.change_percent,
               cp.name, c.name as competitor_name
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
        for r in rows:
            print(f"TYPE={r[0]}|OLD={r[1]}|NEW={r[2]}|CHANGE={r[3]}|NAME={r[4]}|COMP={r[5]}")
