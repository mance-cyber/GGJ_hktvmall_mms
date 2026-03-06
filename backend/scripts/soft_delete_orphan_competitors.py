"""
Soft-delete competitor products with no mapping to any own product.

冇 mapping 到任何自家商品的競品 → 標記 is_active=False（soft delete）
歷史價格數據保留，只係唔再參與分析。

Usage:
    # 只睇統計（唔改任何嘢）
    python scripts/soft_delete_orphan_competitors.py --stats-only

    # Dry run（睇會刪幾多，唔真刪）
    python scripts/soft_delete_orphan_competitors.py --dry-run

    # 真正執行
    python scripts/soft_delete_orphan_competitors.py
"""

import sys
import os
import asyncio
import argparse
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select, func
from app.models.database import async_session_maker
from app.models.competitor import Competitor, CompetitorProduct
from app.models.product import ProductCompetitorMapping

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
logger = logging.getLogger(__name__)


async def main(dry_run: bool = False, stats_only: bool = False):
    async with async_session_maker() as db:

        # 所有 active 競品數量
        total_stmt = select(func.count()).select_from(CompetitorProduct).where(
            CompetitorProduct.is_active == True
        )
        total = (await db.execute(total_stmt)).scalar_one()

        # 已有 mapping 的競品 IDs
        mapped_ids_stmt = select(
            ProductCompetitorMapping.competitor_product_id
        ).distinct()
        mapped_result = await db.execute(mapped_ids_stmt)
        mapped_ids = {row[0] for row in mapped_result}

        # 孤兒競品（active 但無 mapping）
        if mapped_ids:
            orphan_stmt = select(CompetitorProduct).where(
                CompetitorProduct.is_active == True,
                CompetitorProduct.id.notin_(mapped_ids),
            )
        else:
            orphan_stmt = select(CompetitorProduct).where(
                CompetitorProduct.is_active == True
            )

        orphan_result = await db.execute(orphan_stmt)
        orphans = orphan_result.scalars().all()

        sep = "=" * 55
        print(f"\n{sep}")
        print("ORPHAN COMPETITOR CLEANUP")
        print(sep)
        print(f"  Active 競品總數: {total}")
        print(f"  有 mapping:      {len(mapped_ids)}")
        print(f"  孤兒（無 mapping）: {len(orphans)}")
        print(sep)

        if not orphans:
            print("  ✅ 無孤兒競品，無需清理")
            return

        if stats_only:
            # 按 competitor 分組統計孤兒
            print("\n孤兒按 competitor 分佈：")
            comp_counts: dict = {}
            for cp in orphans:
                cid = str(cp.competitor_id)
                comp_counts[cid] = comp_counts.get(cid, 0) + 1

            # 取 competitor 名字
            for cid, count in sorted(comp_counts.items(), key=lambda x: -x[1]):
                comp_stmt = select(Competitor).where(Competitor.id == cid)
                comp_result = await db.execute(comp_stmt)
                comp = comp_result.scalar_one_or_none()
                comp_name = comp.name if comp else cid[:8]
                print(f"    {comp_name}: {count} 件")
            print()
            return

        if dry_run:
            print(f"\n  ⚠️  DRY RUN: 將 soft-delete {len(orphans)} 件孤兒競品")
            print("  （is_active=False，歷史數據保留）")
            return

        # 執行 soft delete
        for cp in orphans:
            cp.is_active = False

        await db.commit()
        print(f"\n  ✅ Soft-deleted {len(orphans)} 件孤兒競品 (is_active → False)")
        print("  歷史價格數據已保留")
        print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="清理無 mapping 的孤兒競品")
    parser.add_argument("--dry-run", action="store_true", help="唔真刪，只睇結果")
    parser.add_argument("--stats-only", action="store_true", help="只睇統計")
    args = parser.parse_args()
    asyncio.run(main(dry_run=args.dry_run, stats_only=args.stats_only))
