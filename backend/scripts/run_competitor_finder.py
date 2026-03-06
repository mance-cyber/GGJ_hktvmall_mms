"""
CLI: Product-driven competitor discovery（以自家商品為起點搵競品）

Usage:
    python scripts/run_competitor_finder.py [--dry-run] [--product-id UUID]

Examples:
    # 全量跑所有商品
    python scripts/run_competitor_finder.py

    # Dry run（唔寫入 DB，只睇結果）
    python scripts/run_competitor_finder.py --dry-run

    # 搜索指定商品
    python scripts/run_competitor_finder.py --product-id <UUID>
"""

import sys
import os
import asyncio
import argparse
import json
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.database import async_session_maker
from app.services.product_competitor_finder import ProductCompetitorFinder

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)


async def main(dry_run: bool = False, product_id: str = None):
    finder = ProductCompetitorFinder()

    async with async_session_maker() as db:
        if product_id:
            import uuid
            logger.info(f"搜索指定商品: {product_id} (dry_run={dry_run})")
            result = await finder.find_for_product(db, uuid.UUID(product_id), dry_run=dry_run)
        else:
            logger.info(f"全量搜索所有有 tag 的自家商品 (dry_run={dry_run})")
            result = await finder.find_all(db, dry_run=dry_run)

    # 摘要
    sep = "=" * 60
    print(f"\n{sep}")
    print("COMPETITOR DISCOVERY RESULTS")
    print(sep)

    if "error" in result:
        print(f"  ❌ Error: {result['error']}")
        return

    print(f"  商品數量:      {result.get('products_processed', '-')}")
    print(f"  搜索次數:      {result.get('queries_sent', '-')}")
    print(f"  總搜索結果:    {result.get('hits_total', '-')}")
    print(f"  相關結果:      {result.get('hits_relevant', '-')}")
    print(f"  過濾掉:        {result.get('hits_filtered', '-')}")
    print(f"  新增競品:      {result.get('new_competitors', '-')}")
    print(f"  更新競品:      {result.get('updated_competitors', '-')}")
    print(f"  新建 mapping:  {result.get('new_mappings', '-')}")
    print(f"  已有 mapping:  {result.get('skipped_existing_mappings', '-')}")

    if result.get("dry_run"):
        print("\n  [!] DRY RUN -- not written to DB")
    else:
        print("\n  [OK] Written to DB")

    print(sep)

    # 逐商品明細
    per_product = result.get("per_product", [])
    if per_product:
        print("\n📦 逐商品明細：")
        for p in per_product:
            bar = "█" * min(p["relevant"], 20) + "░" * max(0, 20 - p["relevant"])
            print(f"\n  {p['product_name'][:40]}")
            print(f"    tags: {p['category_tag']}/{p.get('sub_tag', '-')}")
            print(f"    queries: {p['queries']}")
            print(f"    結果: {p['relevant']}/{p['total']} 相關 [{bar}]")

    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="以自家商品為起點搵 HKTVmall 競品"
    )
    parser.add_argument("--dry-run", action="store_true", help="唔寫入 DB，只睇結果")
    parser.add_argument("--product-id", type=str, help="搜索指定商品（UUID）")
    args = parser.parse_args()

    asyncio.run(main(dry_run=args.dry_run, product_id=args.product_id))
