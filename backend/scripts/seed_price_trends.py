# -*- coding: utf-8 -*-
# =============================================
# 價格趨勢 Mock 數據 Seed 腳本
# =============================================
#
# 使用方法：
#   cd backend
#   python scripts/seed_price_trends.py          # 插入 mock 數據
#   python scripts/seed_price_trends.py --cleanup  # 清除 mock 數據
#
# Mock 數據特徵：
#   - 產品 SKU 使用 MOCK- 前綴
#   - 競爭對手名稱使用 [Mock] 前綴
#   - 可通過 --cleanup 一鍵清除，不影響正式數據

import sys
import os
import random
import argparse
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

# 設置 stdout 編碼
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# 添加 app 到路徑
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.config import get_settings
from app.models import (
    Product,
    Competitor,
    CompetitorProduct,
    PriceSnapshot,
    ProductCompetitorMapping,
    OwnPriceSnapshot,
)

settings = get_settings()

# =============================================
# Mock 數據定義
# =============================================

MOCK_PREFIX = "MOCK-"
MOCK_COMPETITOR_PREFIX = "[Mock] "

# 10 個自家產品（日本食材主題）
OWN_PRODUCTS = [
    {"sku": "WAGYU-A5-001", "name": "A5和牛肩胛肉", "base_price": 388, "category": "肉類"},
    {"sku": "SALMON-NO-001", "name": "挪威三文魚柳", "base_price": 128, "category": "海鮮"},
    {"sku": "UNI-HOK-001", "name": "北海道馬糞海膽", "base_price": 268, "category": "海鮮"},
    {"sku": "SCALLOP-HOK-001", "name": "北海道帆立貝", "base_price": 198, "category": "海鮮"},
    {"sku": "TUNA-JP-001", "name": "日本藍鰭吞拿魚", "base_price": 458, "category": "海鮮"},
    {"sku": "MISO-JP-001", "name": "京都白味噌", "base_price": 68, "category": "調味料"},
    {"sku": "SOY-JP-001", "name": "龜甲萬醬油", "base_price": 45, "category": "調味料"},
    {"sku": "RICE-JP-001", "name": "新潟越光米", "base_price": 158, "category": "米糧"},
    {"sku": "MATCHA-KYO-001", "name": "宇治抹茶粉", "base_price": 128, "category": "飲品"},
    {"sku": "WAGASHI-001", "name": "京都和菓子禮盒", "base_price": 188, "category": "甜點"},
]

# 競爭對手定義
COMPETITORS = [
    {"name": "Donki", "platform": "donki"},
    {"name": "759阿信屋", "platform": "759"},
    {"name": "百佳", "platform": "parknshop"},
    {"name": "惠康", "platform": "wellcome"},
    {"name": "AEON", "platform": "aeon"},
]

# 每個產品的競爭對手價格係數（相對於自家價格）
COMPETITOR_PRICE_FACTORS = {
    "donki": (0.85, 0.95),      # Donki 通常便宜 5-15%
    "759": (0.90, 1.00),        # 759 便宜 0-10%
    "parknshop": (0.95, 1.05),  # 百佳 差不多
    "wellcome": (0.95, 1.05),   # 惠康 差不多
    "aeon": (0.92, 1.02),       # AEON 略便宜
}

PROMOTION_TEXTS = [
    "限時特價",
    "會員專享",
    "買二送一",
    "滿$300減$30",
    "新品優惠",
    "清貨大減價",
    None, None, None, None, None,  # 大部分時間沒有促銷
]


def generate_price_history(base_price: float, days: int = 90) -> list:
    """
    生成價格歷史數據

    模擬真實價格波動：
    - 基礎波動 ±5%
    - 週末促銷（-10% ~ -15%）
    - 隨機缺貨（5% 機率）
    - 隨機促銷標籤（15% 機率）
    """
    prices = []
    start_date = datetime.utcnow() - timedelta(days=days)
    current_price = base_price

    for day in range(days + 1):
        date = start_date + timedelta(days=day)

        # 基礎波動 ±3%（比較平滑的變化）
        daily_variation = random.uniform(-0.03, 0.03)

        # 週末促銷（週六日有 30% 機率降價 10-15%）
        is_weekend = date.weekday() in [5, 6]
        if is_weekend and random.random() < 0.3:
            daily_variation -= random.uniform(0.10, 0.15)

        # 價格不會偏離基礎價太遠（±20%）
        new_price = current_price * (1 + daily_variation)
        new_price = max(base_price * 0.8, min(base_price * 1.2, new_price))
        current_price = new_price

        # 計算折扣
        original_price = base_price * 1.1 if random.random() < 0.2 else None
        discount_pct = None
        if original_price:
            discount_pct = round((1 - current_price / original_price) * 100, 1)

        # 隨機缺貨（5% 機率）
        stock_status = "out_of_stock" if random.random() < 0.05 else "in_stock"

        # 隨機促銷標籤（15% 機率）
        promotion = random.choice(PROMOTION_TEXTS) if random.random() < 0.15 else None

        prices.append({
            "date": date,
            "price": round(current_price, 1),
            "original_price": round(original_price, 1) if original_price else None,
            "discount_percent": discount_pct,
            "stock_status": stock_status,
            "promotion_text": promotion,
        })

    return prices


def seed_data(session):
    """插入 mock 數據"""
    print("\n=== 開始插入 Mock 數據 ===\n")

    # 1. 創建競爭對手
    print("1. 創建競爭對手...")
    competitor_map = {}
    for comp_data in COMPETITORS:
        competitor = Competitor(
            name=f"{MOCK_COMPETITOR_PREFIX}{comp_data['name']}",
            platform=comp_data["platform"],
            is_active=True,
        )
        session.add(competitor)
        session.flush()
        competitor_map[comp_data["platform"]] = competitor
        print(f"   - {competitor.name} ({competitor.platform})")

    # 2. 創建自家產品和競品
    print("\n2. 創建產品和價格歷史...")
    total_own_snapshots = 0
    total_competitor_snapshots = 0

    for prod_data in OWN_PRODUCTS:
        # 創建自家產品
        product = Product(
            sku=f"{MOCK_PREFIX}{prod_data['sku']}",
            name=prod_data["name"],
            price=Decimal(str(prod_data["base_price"])),
            category=prod_data["category"],
            status="active",
            source="mock",
        )
        session.add(product)
        session.flush()
        print(f"\n   [自家] {product.sku} - {product.name}")

        # 生成自家產品價格歷史
        own_prices = generate_price_history(prod_data["base_price"], days=90)
        for price_data in own_prices:
            snapshot = OwnPriceSnapshot(
                product_id=product.id,
                price=Decimal(str(price_data["price"])),
                original_price=Decimal(str(price_data["original_price"])) if price_data["original_price"] else None,
                discount_percent=Decimal(str(price_data["discount_percent"])) if price_data["discount_percent"] else None,
                stock_status=price_data["stock_status"],
                promotion_text=price_data["promotion_text"],
                recorded_at=price_data["date"],
            )
            session.add(snapshot)
            total_own_snapshots += 1

        # 為每個產品隨機選擇 3-5 個競爭對手
        num_competitors = random.randint(3, 5)
        selected_platforms = random.sample(list(competitor_map.keys()), num_competitors)

        for platform in selected_platforms:
            competitor = competitor_map[platform]

            # 計算競爭對手基礎價格
            price_factor = random.uniform(*COMPETITOR_PRICE_FACTORS[platform])
            comp_base_price = prod_data["base_price"] * price_factor

            # 創建競品商品
            comp_product = CompetitorProduct(
                competitor_id=competitor.id,
                name=f"{prod_data['name']} ({competitor.name.replace(MOCK_COMPETITOR_PREFIX, '')})",
                url=f"https://mock.{platform}.com/product/{prod_data['sku'].lower()}",
                sku=f"{platform.upper()}-{prod_data['sku']}",
                category=prod_data["category"],
                is_active=True,
            )
            session.add(comp_product)
            session.flush()

            # 創建產品-競品映射
            mapping = ProductCompetitorMapping(
                product_id=product.id,
                competitor_product_id=comp_product.id,
                match_confidence=Decimal(str(round(random.uniform(0.85, 0.99), 2))),
                is_verified=True,
            )
            session.add(mapping)

            # 生成競品價格歷史
            comp_prices = generate_price_history(comp_base_price, days=90)
            for price_data in comp_prices:
                snapshot = PriceSnapshot(
                    competitor_product_id=comp_product.id,
                    price=Decimal(str(price_data["price"])),
                    original_price=Decimal(str(price_data["original_price"])) if price_data["original_price"] else None,
                    discount_percent=Decimal(str(price_data["discount_percent"])) if price_data["discount_percent"] else None,
                    stock_status=price_data["stock_status"],
                    promotion_text=price_data["promotion_text"],
                    scraped_at=price_data["date"],
                )
                session.add(snapshot)
                total_competitor_snapshots += 1

            print(f"      - {competitor.name.replace(MOCK_COMPETITOR_PREFIX, '')}: {len(comp_prices)} 筆")

    session.commit()

    print(f"\n=== Mock 數據插入完成 ===")
    print(f"   - 自家產品: {len(OWN_PRODUCTS)} 個")
    print(f"   - 競爭對手: {len(COMPETITORS)} 個")
    print(f"   - 自家價格快照: {total_own_snapshots} 筆")
    print(f"   - 競品價格快照: {total_competitor_snapshots} 筆")
    print(f"   - 總計: {total_own_snapshots + total_competitor_snapshots} 筆\n")


def cleanup_data(session):
    """清除所有 mock 數據"""
    print("\n=== 開始清除 Mock 數據 ===\n")

    # 1. 刪除自家產品價格快照（通過 CASCADE 會自動刪除）
    # 2. 刪除競品價格快照（通過 CASCADE 會自動刪除）
    # 3. 刪除產品-競品映射（通過 CASCADE 會自動刪除）

    # 刪除自家產品（SKU 以 MOCK- 開頭）
    result = session.execute(
        text(f"DELETE FROM products WHERE sku LIKE '{MOCK_PREFIX}%'")
    )
    deleted_products = result.rowcount
    print(f"   - 刪除自家產品: {deleted_products} 個")

    # 刪除競爭對手（名稱以 [Mock] 開頭）
    result = session.execute(
        text(f"DELETE FROM competitors WHERE name LIKE '{MOCK_COMPETITOR_PREFIX}%'")
    )
    deleted_competitors = result.rowcount
    print(f"   - 刪除競爭對手: {deleted_competitors} 個")

    session.commit()

    print(f"\n=== Mock 數據清除完成 ===\n")


def main():
    parser = argparse.ArgumentParser(description="價格趨勢 Mock 數據管理")
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="清除所有 mock 數據",
    )
    args = parser.parse_args()

    # 創建數據庫連接
    engine = create_engine(settings.database_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        if args.cleanup:
            cleanup_data(session)
        else:
            # 先清除舊的 mock 數據
            cleanup_data(session)
            # 插入新的 mock 數據
            seed_data(session)
    except Exception as e:
        session.rollback()
        print(f"\n[ERROR] 操作失敗: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
