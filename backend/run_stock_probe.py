"""
手動跑一次 stock probe — 從 DB 抓所有 active SKU，探測庫存，寫入 DB
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app.core.database import get_db, engine
from app.models.competitor import CompetitorProduct, PriceSnapshot
from app.services.stock_prober import probe_stocks_batch
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime, timezone

async def main():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 開始 stock probe...")

    with Session(engine) as db:
        # 抓所有 active product SKUs
        products = db.execute(
            select(CompetitorProduct)
            .where(CompetitorProduct.is_active == True)
        ).scalars().all()

        skus = [p.sku for p in products if p.sku]
        print(f"找到 {len(skus)} 個 active SKUs")

        if not skus:
            print("無 SKU，退出")
            return

        # 批次探測
        results = await probe_stocks_batch(skus, concurrency=5, delay=0.3)

        # 寫入 DB
        updated = 0
        out_of_stock = 0
        errors = 0

        for product in products:
            if not product.sku:
                continue
            r = results.get(product.sku)
            if not r:
                continue

            if r.error:
                errors += 1
                print(f"  ❌ {product.sku}: {r.error}")
                continue

            if r.stock_level is not None:
                # 更新最新 snapshot
                latest_snapshot = db.execute(
                    select(PriceSnapshot)
                    .where(PriceSnapshot.competitor_product_id == product.id)
                    .order_by(PriceSnapshot.scraped_at.desc())
                    .limit(1)
                ).scalar_one_or_none()

                if latest_snapshot:
                    latest_snapshot.stock_level = r.stock_level
                    updated += 1

                    if r.stock_level == 0:
                        out_of_stock += 1
                        print(f"  🚨 缺貨: {product.sku} (stock_level=0)")
                    else:
                        print(f"  ✅ {product.sku}: stock={r.stock_level}")

        db.commit()
        print(f"\n完成！更新 {updated} 條 snapshot，缺貨 {out_of_stock} 個，錯誤 {errors} 個")

asyncio.run(main())
