"""
Soft-delete competitor products with no mapping to any own product.

鍐?mapping 鍒颁换浣曡嚜瀹跺晢鍝佺殑绔跺搧 鈫?妯欒 is_active=False锛坰oft delete锛?姝峰彶鍍规牸鏁告摎淇濈暀锛屽彧淇傚敂鍐嶅弮鑸囧垎鏋愩€?
Usage:
    # 鍙潎绲辫▓锛堝敂鏀逛换浣曞槩锛?    python scripts/soft_delete_orphan_competitors.py --stats-only

    # Dry run锛堢潎鏈冨埅骞惧锛屽敂鐪熷埅锛?    python scripts/soft_delete_orphan_competitors.py --dry-run

    # 鐪熸鍩疯
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

        # 鎵€鏈?active 绔跺搧鏁搁噺
        total_stmt = select(func.count()).select_from(CompetitorProduct).where(
            CompetitorProduct.is_active == True
        )
        total = (await db.execute(total_stmt)).scalar_one()

        # 宸叉湁 mapping 鐨勭鍝?IDs
        mapped_ids_stmt = select(
            ProductCompetitorMapping.competitor_product_id
        ).distinct()
        mapped_result = await db.execute(mapped_ids_stmt)
        mapped_ids = {row[0] for row in mapped_result}

        # 瀛ゅ厭绔跺搧锛坅ctive 浣嗙劇 mapping锛?        if mapped_ids:
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
        print(f"  Active 绔跺搧绺芥暩: {total}")
        print(f"  鏈?mapping:      {len(mapped_ids)}")
        print(f"  瀛ゅ厭锛堢劇 mapping锛? {len(orphans)}")
        print(sep)

        if not orphans:
            print("  鉁?鐒″鍏掔鍝侊紝鐒￠渶娓呯悊")
            return

        if stats_only:
            # 鎸?competitor 鍒嗙祫绲辫▓瀛ゅ厭
            print("\n瀛ゅ厭鎸?competitor 鍒嗕綀锛?)
            comp_counts: dict = {}
            for cp in orphans:
                cid = str(cp.competitor_id)
                comp_counts[cid] = comp_counts.get(cid, 0) + 1

            # 鍙?competitor 鍚嶅瓧
            for cid, count in sorted(comp_counts.items(), key=lambda x: -x[1]):
                comp_stmt = select(Competitor).where(Competitor.id == cid)
                comp_result = await db.execute(comp_stmt)
                comp = comp_result.scalar_one_or_none()
                comp_name = comp.name if comp else cid[:8]
                print(f"    {comp_name}: {count} 浠?)
            print()
            return

        if dry_run:
            print(f"\n  鈿狅笍  DRY RUN: 灏?soft-delete {len(orphans)} 浠跺鍏掔鍝?)
            print("  锛坕s_active=False锛屾鍙叉暩鎿氫繚鐣欙級")
            return

        # 鍩疯 soft delete
        for cp in orphans:
            cp.is_active = False

        await db.commit()
        print(f"\n  鉁?Soft-deleted {len(orphans)} 浠跺鍏掔鍝?(is_active 鈫?False)")
        print("  姝峰彶鍍规牸鏁告摎宸蹭繚鐣?)
        print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="娓呯悊鐒?mapping 鐨勫鍏掔鍝?)
    parser.add_argument("--dry-run", action="store_true", help="鍞旂湡鍒紝鍙潎绲愭灉")
    parser.add_argument("--stats-only", action="store_true", help="鍙潎绲辫▓")
    args = parser.parse_args()
    asyncio.run(main(dry_run=args.dry_run, stats_only=args.stats_only))
