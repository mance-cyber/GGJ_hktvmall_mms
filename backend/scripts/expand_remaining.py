#!/usr/bin/env python3
"""
Standalone expand script - bypasses init_db to avoid Neon cold start pool poisoning.
"""
import asyncio
import sys
from pathlib import Path
from decimal import Decimal
from collections import Counter

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from app.models.database import engine, async_session_maker
from app.models.product import Product, ProductCompetitorMapping
from app.models.competitor import Competitor, CompetitorProduct
from app.connectors.hktv_api import get_hktv_api_client

ALGOLIA_PAGE_SIZE = 100
EXPAND_THRESHOLD = 50


def extract_store_code_from_skus(skus: list) -> str | None:
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


async def expand_store(session, competitor_id, store_name: str) -> tuple[int, int]:
    client = get_hktv_api_client()

    sku_result = await session.execute(
        select(CompetitorProduct.sku).where(
            CompetitorProduct.competitor_id == competitor_id,
            CompetitorProduct.sku.isnot(None),
        )
    )
    skus = [r[0] for r in sku_result.all()]
    store_code = extract_store_code_from_skus(skus)

    if store_code:
        print(f"  使用 storeCode: {store_code}")
    else:
        print(f"  ⚠️ 無法提取 store code，fallback 到 storeNameZh")

    all_products = []
    page = 0
    while True:
        if store_code:
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

    await session.commit()
    return new_cp_count, new_mapping_count


async def main():
    # Reset pool to avoid init_db poison
    await engine.dispose()
    print("Pool reset. Connecting to Neon...")
    await asyncio.sleep(1)

    async with async_session_maker() as session:
        result = await session.execute(
            select(Competitor).where(Competitor.platform == "hktvmall", Competitor.is_active == True)
        )
        competitors = result.scalars().all()

        to_expand = []
        for comp in competitors:
            count_result = await session.execute(
                select(func.count(CompetitorProduct.id)).where(CompetitorProduct.competitor_id == comp.id)
            )
            count = count_result.scalar() or 0
            if count < EXPAND_THRESHOLD:
                to_expand.append((comp, count))
                print(f"  ⚠️ {comp.name}: {count} → 需要擴展")
            else:
                print(f"  ✅ {comp.name}: {count}")

        if not to_expand:
            print("\n✅ 所有店舖已充足")
            return

        print(f"\n將擴展 {len(to_expand)} 個店舖...")
        total_new = 0

        for comp, current in to_expand:
            print(f"\n[{comp.name}] 現有 {current} 件，搜索中...")
            new_p, new_m = await expand_store(session, comp.id, comp.name)
            print(f"  ✓ 新增商品: {new_p}")
            total_new += new_p

        print(f"\n📊 總計新增: {total_new} 件商品")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
