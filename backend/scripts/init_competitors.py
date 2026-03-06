"""
初始化競品商戶數據庫

Usage:
    python scripts/init_competitors.py [--dry-run]

功能：
    - 插入已知核心競品商戶（Tier 1/2）
    - 支持 --dry-run 模式（只顯示，不寫入）
"""

import sys
import os
import asyncio
import argparse
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from app.models.database import async_session_maker
from app.models.competitor import Competitor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)


# =============================================
# 初始競品商戶列表
# 更新方式：在此列表加入新商戶，重新跑 script
# =============================================
INITIAL_COMPETITORS = [
    {
        "name": "Foodianna",
        "store_code": "H6852001",
        "tier": 1,
        "platform": "hktvmall",
        "notes": "日本食材直競品，Tier 1 直接對手",
    },
    {
        "name": "Ocean Three 皇海三寶",
        "store_code": "H0147001",
        "tier": 2,
        "platform": "hktvmall",
        "notes": "海鮮為主，品類重疊",
    },
    # 如需添加更多商戶，在此加入：
    # {
    #     "name": "商戶名稱",
    #     "store_code": "HXXXXxxx",  # HKTVmall store code
    #     "tier": 1,                 # 1=直接對手, 2=品類重疊, 3=參考
    #     "platform": "hktvmall",
    #     "notes": "備註",
    # },
]


async def main(dry_run: bool = False):
    logger.info(f"初始化競品商戶 ({'DRY RUN' if dry_run else '寫入 DB'})")
    logger.info(f"共 {len(INITIAL_COMPETITORS)} 間商戶")

    if dry_run:
        for c in INITIAL_COMPETITORS:
            logger.info(f"  [DRY] Tier {c['tier']} | {c['name']} | store_code={c['store_code']}")
        return

    async with async_session_maker() as db:
        added = 0
        skipped = 0

        for item in INITIAL_COMPETITORS:
            # 檢查是否已存在（按 store_code）
            result = await db.execute(
                select(Competitor).where(
                    Competitor.store_code == item["store_code"]
                )
            )
            existing = result.scalars().first()

            if existing:
                # 更新 tier
                existing.tier = item["tier"]
                existing.notes = item.get("notes", existing.notes)
                logger.info(f"  更新: {item['name']} (tier={item['tier']})")
                skipped += 1
            else:
                comp = Competitor(
                    name=item["name"],
                    store_code=item["store_code"],
                    tier=item["tier"],
                    platform=item["platform"],
                    notes=item.get("notes"),
                    is_active=True,
                )
                db.add(comp)
                logger.info(f"  新增: {item['name']} (Tier {item['tier']}, {item['store_code']})")
                added += 1

        await db.commit()
        logger.info(f"完成：新增 {added} 間，更新 {skipped} 間")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="初始化競品商戶")
    parser.add_argument("--dry-run", action="store_true", help="只顯示不寫入")
    args = parser.parse_args()
    asyncio.run(main(dry_run=args.dry_run))
