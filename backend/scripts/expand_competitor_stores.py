#!/usr/bin/env python3
# =============================================
# 擴展競品店舖商品目錄腳本
# =============================================
# 用途：對已確認的競品店舖，通過 Algolia facetFilters 獲取其完整商品目錄
#       並自動創建 ProductCompetitorMapping（基於 category_tag 匹配，無需 Claude）
# 執行：python scripts/expand_competitor_stores.py
# =============================================

import asyncio
import sys
import os
from pathlib import Path
from decimal import Decimal
from collections import Counter

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import select, func, text
from sqlalchemy.exc import IntegrityError
from app.models.database import async_session_maker, init_db, engine
from app.models.product import Product, ProductCompetitorMapping
from app.models.competitor import Competitor, CompetitorProduct
from app.connectors.hktv_api import get_hktv_api_client


ALGOLIA_PAGE_SIZE = 100
EXPAND_THRESHOLD = 50


def extract_store_code_from_skus(skus: list) -> str | None:
    """從 SKU 列表中提取最常見的 store code (H8363002_S_xxx -> H8363002)"""
    codes = []
    for sku in skus:
        if sku and '_S_' in sku:
            code = sku.split('_S_')[0]
            if code:
                codes.append(code)
    if not codes:
        return None
    counter = Counter(codes)
    return counter.most_common(1)[0][0]


async def get_store_product_counts(session) -> dict:
    result = await session.execute(
        select(Competitor).where(Competitor.platform == "hktvmall", Competitor.is_active == True)
    )
    competitors = result.scalars().all()
    store_map = {}
    for comp in competitors:
        count_result = await session.execute(
            select(func.count(CompetitorProduct.id)).where(CompetitorProduct.competitor_id == comp.id)
        )
        count = count_result.scalar() or 0
        store_map[comp.name] = (comp.id, count)
    return store_map


async def get_all_store_names_from_products(session) -> dict:
    return await get_store_product_counts(session)


async def expand_store(session, competitor_id, store_name: str, dry_run: bool = False) -> tuple[int, int]:
    """擴展單個店舖的商品目錄，優先用 storeCode facetFilter"""
    client = get_hktv_api_client()

    # 從現有商品 SKU 提取 store code
    sku_result = await session.execute(
        select(CompetitorProduct.sku).where(
            CompetitorProduct.competitor_id == competitor_id,
            CompetitorProduct.sku.isnot(None),
        )
    )
    skus = [r[0] for r in sku_result.all()]
    store_code = extract_store_code_from_skus(skus)

    use_store_code = store_code is not None
    if use_store_code:
        print(f"  使用 storeCode: {store_code}")
    else:
        print(f"  ⚠️ 無法提取 store code，fallback 到 storeNameZh")

    all_products = []
    page = 0
    while True:
        if use_store_code:
            products = await client.search_by_store_code(store_code, page_size=ALGOLIA_PAGE_SIZE, page=page)
        else:
            products = await client.search_by_store(store_name, page_size=ALGOLIA_PAGE_SIZE, page=page)
        if not products:
            break
        all_products.extend(products)
        if len(products) < ALGOLIA_PAGE_SIZE:
            break
        page += 1
        if page >= 10:
            break

    print(f"  Algolia 找到 {len(all_products)} 件商品")

    if dry_run:
        for p in all_products[:5]:
            print(f"    - {p.name[:50]} | {p.sku}")
        if len(all_products) > 5:
            print(f"    ... 還有 {len(all_products) - 5} 件")
        return 0, 0

    existing_urls_result = await session.execute(
        select(CompetitorProduct.url).where(CompetitorProduct.competitor_id == competitor_id)
    )
    existing_urls = set(existing_urls_result.scalars().all())

    new_cp_count = 0
    new_mapping_count = 0

    for hktv_p in all_products:
        if not hktv_p.url or hktv_p.url in existing_urls:
            continue
        cp = CompetitorProduct(
            competitor_id=competitor_id, name=hktv_p.name, url=hktv_p.url,
            sku=hktv_p.sku or None, image_url=hktv_p.image_url,
            is_active=True, needs_matching=True,
        )
        try:
            async with session.begin_nested():
                session.add(cp)
                await session.flush()
            existing_urls.add(hktv_p.url)
            new_cp_count += 1
        except IntegrityError:
            continue

        if cp.category_tag:
            products_result = await session.execute(
                select(Product).where(
                    Product.source.in_(["gogojap_csv", "xlsx_import"]),
                    Product.category_tag == cp.category_tag,
                )
            )
            our_products = products_result.scalars().all()
            for our_p in our_products:
                existing_map = await session.execute(
                    select(ProductCompetitorMapping).where(
                        ProductCompetitorMapping.product_id == our_p.id,
                        ProductCompetitorMapping.competitor_product_id == cp.id,
                    )
                )
                if existing_map.scalar():
                    continue
                mapping = ProductCompetitorMapping(
                    product_id=our_p.id, competitor_product_id=cp.id,
                    match_confidence=Decimal("0.50"), match_level=3,
                )
                try:
                    async with session.begin_nested():
                        session.add(mapping)
                        await session.flush()
                    new_mapping_count += 1
                except IntegrityError:
                    continue

    await session.commit()
    return new_cp_count, new_mapping_count


async def expand_competitor_stores(threshold: int = EXPAND_THRESHOLD, dry_run: bool = False, store_filter: str = None):
    print("=" * 60)
    print("競品店舖擴展工具")
    print("=" * 60)
    print(f"配置:")
    print(f"  - 擴展閾值: < {threshold} 件商品")
    print(f"  - 模式: {'測試模式（不保存）' if dry_run else '正式執行'}")
    if store_filter:
        print(f"  - 過濾店舖: {store_filter}")
    print("=" * 60)

    await init_db()
    # init_db may silently fail and poison the pool; always reset
    await engine.dispose()

    async with async_session_maker() as session:
        store_map = await get_all_store_names_from_products(session)
        if not store_map:
            print("\n❌ 沒有找到 hktvmall 競品記錄")
            return

        print(f"\n找到 {len(store_map)} 個競品店舖:")
        for name, (cid, count) in store_map.items():
            status = "⚠️ 需要擴展" if count < threshold else "✅ 已充足"
            print(f"  {status} {name}: {count} 件商品")

        to_expand = {n: v for n, v in store_map.items() if v[1] < threshold}
        if store_filter:
            to_expand = {k: v for k, v in to_expand.items() if store_filter in k}

        if not to_expand:
            print("\n✅ 所有店舖商品數量充足，無需擴展")
            return

        print(f"\n將擴展 {len(to_expand)} 個店舖:")
        total_new_products = 0
        total_new_mappings = 0

        for store_name, (competitor_id, current_count) in to_expand.items():
            print(f"\n[{store_name}] 現有 {current_count} 件商品，正在搜索...")
            new_p, new_m = await expand_store(session, competitor_id, store_name, dry_run=dry_run)
            print(f"  ✓ 新增商品: {new_p}, 新增映射: {new_m}")
            total_new_products += new_p
            total_new_mappings += new_m

        print("\n" + "=" * 60)
        print("📊 執行結果:")
        print(f"  - 處理店舖: {len(to_expand)}")
        print(f"  - 新增競品商品: {total_new_products}")
        print(f"  - 新增商品映射: {total_new_mappings}")
        print("=" * 60)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="競品店舖擴展工具")
    parser.add_argument("--threshold", type=int, default=EXPAND_THRESHOLD)
    parser.add_argument("--store", type=str, help="只處理特定店舖名稱（模糊匹配）")
    parser.add_argument("--dry-run", action="store_true", help="測試模式")
    args = parser.parse_args()
    asyncio.run(expand_competitor_stores(threshold=args.threshold, dry_run=args.dry_run, store_filter=args.store))


if __name__ == "__main__":
    main()
