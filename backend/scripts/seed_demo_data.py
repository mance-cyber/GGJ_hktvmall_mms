# =============================================
# 插入測試數據腳本
# 用於 AI Agent 測試，所有數據標記為 source="demo"
# 清理：DELETE FROM products WHERE source = 'demo';
# =============================================

import asyncio
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
import random

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

# 添加項目路徑
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models.database import async_session_maker
from app.models.product import Product
from app.models.competitor import Competitor, CompetitorProduct, PriceSnapshot


# =============================================
# 測試數據定義
# =============================================

DEMO_PRODUCTS = [
    # 和牛
    {
        "sku": "DEMO-WAGYU-001",
        "name": "[測試] 日本 A5 和牛西冷 (200g)",
        "name_zh": "日本 A5 和牛西冷",
        "name_ja": "A5黒毛和牛サーロイン",
        "category": "和牛",
        "category_main": "急凍",
        "category_sub": "和牛",
        "brand": "鹿兒島黑毛和牛",
        "price": Decimal("688.00"),
        "cost": Decimal("450.00"),
        "stock_quantity": 50,
        "status": "active",
    },
    {
        "sku": "DEMO-WAGYU-002",
        "name": "[測試] 澳洲 M9 和牛肉眼扒 (250g)",
        "name_zh": "澳洲 M9 和牛肉眼扒",
        "name_ja": "M9和牛リブアイ",
        "category": "和牛",
        "category_main": "急凍",
        "category_sub": "和牛",
        "brand": "Blackmore",
        "price": Decimal("458.00"),
        "cost": Decimal("320.00"),
        "stock_quantity": 35,
        "status": "active",
    },
    {
        "sku": "DEMO-WAGYU-003",
        "name": "[測試] 日本 A4 和牛燒肉片 (300g)",
        "name_zh": "日本 A4 和牛燒肉片",
        "name_ja": "A4和牛焼肉用",
        "category": "和牛",
        "category_main": "急凍",
        "category_sub": "和牛",
        "brand": "宮崎牛",
        "price": Decimal("388.00"),
        "cost": Decimal("260.00"),
        "stock_quantity": 20,
        "status": "active",
    },
    # 海膽
    {
        "sku": "DEMO-UNI-001",
        "name": "[測試] 北海道馬糞海膽 (100g)",
        "name_zh": "北海道馬糞海膽",
        "name_ja": "北海道バフンウニ",
        "category": "海膽",
        "category_main": "飛機貨",
        "category_sub": "海膽",
        "brand": "北海道直送",
        "price": Decimal("288.00"),
        "cost": Decimal("180.00"),
        "stock_quantity": 25,
        "status": "active",
    },
    {
        "sku": "DEMO-UNI-002",
        "name": "[測試] 紫海膽刺身 (80g)",
        "name_zh": "紫海膽刺身",
        "name_ja": "ムラサキウニ刺身",
        "category": "海膽",
        "category_main": "飛機貨",
        "category_sub": "海膽",
        "brand": "利尻島",
        "price": Decimal("198.00"),
        "cost": Decimal("120.00"),
        "stock_quantity": 15,
        "status": "active",
    },
    # 三文魚
    {
        "sku": "DEMO-SALMON-001",
        "name": "[測試] 挪威三文魚刺身 (250g)",
        "name_zh": "挪威三文魚刺身",
        "name_ja": "ノルウェーサーモン刺身",
        "category": "三文魚",
        "category_main": "急凍",
        "category_sub": "鮮魚",
        "brand": "MOWI",
        "price": Decimal("128.00"),
        "cost": Decimal("75.00"),
        "stock_quantity": 80,
        "status": "active",
    },
    {
        "sku": "DEMO-SALMON-002",
        "name": "[測試] 蘇格蘭煙燻三文魚 (200g)",
        "name_zh": "蘇格蘭煙燻三文魚",
        "name_ja": "スコットランドスモークサーモン",
        "category": "三文魚",
        "category_main": "急凍",
        "category_sub": "鮮魚",
        "brand": "Loch Duart",
        "price": Decimal("98.00"),
        "cost": Decimal("55.00"),
        "stock_quantity": 60,
        "status": "active",
    },
    # 日本零食
    {
        "sku": "DEMO-SNACK-001",
        "name": "[測試] Royce 生巧克力 (20片)",
        "name_zh": "Royce 生巧克力",
        "name_ja": "ロイズ生チョコレート",
        "category": "日本零食",
        "category_main": "乾貨",
        "category_sub": "零食",
        "brand": "Royce'",
        "price": Decimal("128.00"),
        "cost": Decimal("72.00"),
        "stock_quantity": 100,
        "status": "active",
    },
    {
        "sku": "DEMO-SNACK-002",
        "name": "[測試] 白色戀人餅乾 (24枚)",
        "name_zh": "白色戀人餅乾",
        "name_ja": "白い恋人",
        "category": "日本零食",
        "category_main": "乾貨",
        "category_sub": "零食",
        "brand": "石屋製菓",
        "price": Decimal("168.00"),
        "cost": Decimal("95.00"),
        "stock_quantity": 75,
        "status": "active",
    },
    {
        "sku": "DEMO-SNACK-003",
        "name": "[測試] 東京香蕉蛋糕 (8個)",
        "name_zh": "東京香蕉蛋糕",
        "name_ja": "東京ばな奈",
        "category": "日本零食",
        "category_main": "乾貨",
        "category_sub": "零食",
        "brand": "東京ばな奈",
        "price": Decimal("98.00"),
        "cost": Decimal("55.00"),
        "stock_quantity": 45,
        "status": "active",
    },
]

DEMO_COMPETITORS = [
    {
        "name": "百佳",
        "platform": "parknshop",
        "base_url": "https://www.parknshop.com",
        "price_multiplier": 1.08,  # 比我們貴 8%
    },
    {
        "name": "惠康",
        "platform": "wellcome",
        "base_url": "https://www.wellcome.com.hk",
        "price_multiplier": 1.05,  # 比我們貴 5%
    },
    {
        "name": "AEON",
        "platform": "aeon",
        "base_url": "https://www.aeonstores.com.hk",
        "price_multiplier": 0.95,  # 比我們平 5%
    },
]


async def seed_demo_data():
    """插入測試數據"""
    async with async_session_maker() as db:
        print("=" * 50)
        print("開始插入測試數據...")
        print("=" * 50)

        # 1. 先清理舊的測試數據
        print("\n🗑️  清理舊測試數據...")
        await db.execute(text("DELETE FROM products WHERE source = 'demo'"))
        await db.execute(text("DELETE FROM competitors WHERE name IN ('百佳', '惠康', 'AEON') AND platform LIKE '%demo%' OR notes LIKE '%測試%'"))
        await db.commit()

        # 2. 插入自家商品
        print("\n📦 插入自家商品...")
        product_map = {}  # sku -> product
        for p_data in DEMO_PRODUCTS:
            product = Product(
                sku=p_data["sku"],
                name=p_data["name"],
                name_zh=p_data.get("name_zh"),
                name_ja=p_data.get("name_ja"),
                category=p_data["category"],
                category_main=p_data.get("category_main"),
                category_sub=p_data.get("category_sub"),
                brand=p_data.get("brand"),
                price=p_data["price"],
                cost=p_data.get("cost"),
                stock_quantity=p_data.get("stock_quantity", 0),
                status=p_data.get("status", "active"),
                source="demo",  # 標記為測試數據
            )
            db.add(product)
            product_map[p_data["sku"]] = product
            print(f"   ✓ {p_data['name']}")

        await db.commit()

        # 3. 插入競爭對手
        print("\n🏪 插入競爭對手...")
        competitor_map = {}
        for c_data in DEMO_COMPETITORS:
            competitor = Competitor(
                name=c_data["name"],
                platform=c_data["platform"],
                base_url=c_data["base_url"],
                notes="[測試數據] 用於 AI Agent 測試",
                is_active=True,
            )
            db.add(competitor)
            competitor_map[c_data["name"]] = (competitor, c_data["price_multiplier"])
            print(f"   ✓ {c_data['name']}")

        await db.commit()

        # 4. 插入競品商品和價格快照
        print("\n💰 插入競品價格數據...")
        for p_data in DEMO_PRODUCTS:
            our_price = float(p_data["price"])

            for comp_name, (competitor, multiplier) in competitor_map.items():
                comp_price = round(our_price * multiplier, 2)

                # 創建競品商品
                comp_product = CompetitorProduct(
                    competitor_id=competitor.id,
                    name=f"[競品] {p_data['name_zh']}",
                    url=f"https://demo.example.com/{p_data['sku']}/{comp_name}",
                    sku=f"{comp_name}-{p_data['sku']}",
                    category=p_data["category"],
                    brand=p_data.get("brand"),
                    is_active=True,
                )
                db.add(comp_product)
                await db.flush()

                # 創建價格歷史（過去 30 天）
                for days_ago in range(30, 0, -1):
                    # 加入一些隨機波動
                    daily_variation = random.uniform(-0.05, 0.05)
                    snapshot_price = round(comp_price * (1 + daily_variation), 2)

                    snapshot = PriceSnapshot(
                        competitor_product_id=comp_product.id,
                        price=Decimal(str(snapshot_price)),
                        original_price=Decimal(str(round(snapshot_price * 1.15, 2))),
                        discount_percent=Decimal("13.0"),
                        stock_status="in_stock" if random.random() > 0.1 else "low_stock",
                        rating=Decimal(str(round(random.uniform(4.0, 5.0), 1))),
                        review_count=random.randint(50, 500),
                        scraped_at=datetime.utcnow() - timedelta(days=days_ago),
                    )
                    db.add(snapshot)

                print(f"   ✓ {comp_name} - {p_data['category']}")

        await db.commit()

        # 5. 統計
        print("\n" + "=" * 50)
        print("✅ 測試數據插入完成！")
        print("=" * 50)
        print(f"   • 自家商品: {len(DEMO_PRODUCTS)} 個")
        print(f"   • 競爭對手: {len(DEMO_COMPETITORS)} 個")
        print(f"   • 競品商品: {len(DEMO_PRODUCTS) * len(DEMO_COMPETITORS)} 個")
        print(f"   • 價格快照: {len(DEMO_PRODUCTS) * len(DEMO_COMPETITORS) * 30} 個")
        print("\n📋 清理方式:")
        print("   DELETE FROM products WHERE source = 'demo';")
        print("   DELETE FROM competitors WHERE notes LIKE '%測試%';")


async def clean_demo_data():
    """清理測試數據"""
    async with async_session_maker() as db:
        print("🗑️  清理所有測試數據...")

        # 先刪除有外鍵依賴的表
        result1 = await db.execute(text("""
            DELETE FROM price_snapshots
            WHERE competitor_product_id IN (
                SELECT id FROM competitor_products
                WHERE name LIKE '%[競品]%'
            )
        """))

        result2 = await db.execute(text("""
            DELETE FROM competitor_products WHERE name LIKE '%[競品]%'
        """))

        result3 = await db.execute(text("""
            DELETE FROM competitors WHERE notes LIKE '%測試%'
        """))

        result4 = await db.execute(text("""
            DELETE FROM products WHERE source = 'demo'
        """))

        await db.commit()

        print("✅ 清理完成！")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="管理測試數據")
    parser.add_argument("action", choices=["seed", "clean"], help="seed=插入測試數據, clean=清理測試數據")
    args = parser.parse_args()

    if args.action == "seed":
        asyncio.run(seed_demo_data())
    else:
        asyncio.run(clean_demo_data())
