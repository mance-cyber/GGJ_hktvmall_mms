"""
初始化核心競爭商戶（Competitor v2）

Usage:
    python scripts/init_competitors.py [--dry-run]
"""

import sys
import os
import asyncio
import argparse
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from uuid import uuid4
from app.models.database import async_session_maker
from app.models.competitor import Competitor
from sqlalchemy import select

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)


# =============================================
# 核心商戶列表 — 由 Mance 指定
# =============================================
INITIAL_COMPETITORS = [
    {
        "name": "Foodianna",
        "store_code": "H6852001",
        "tier": 1,
        "platform": "hktvmall",
        "notes": "直接對手：日本食材專門店",
    },
    {
        "name": "Ocean Three 皇海三寶",
        "store_code": "H0147001",
        "tier": 2,
        "platform": "hktvmall",
        "notes": "品類重疊：海鮮、和牛",
    },
    # TODO: Mance 確認後加更多商戶
    # {
    #     "name": "商戶名",
    #     "store_code": "H1234001",
    #     "tier": 2,
    #     "platform": "hktvmall",
    #     "notes": "",
    # },
]


async def main(dry_run: bool = False):
    logger.info(f"初始化競爭商戶（dry_run={dry_run}）")

    async with async_session_maker() as db:
        added = 0
        skipped = 0

        for comp_data in INITIAL_COMPETITORS:
            # 檢查是否已存在
            stmt = select(Competitor).where(
                Competitor.store_code == comp_data["store_code"]
            )
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                logger.info(f"  ⏭️  已存在: {comp_data['name']} ({comp_data['store_code']})")
                skipped += 1
                continue

            if dry_run:
                logger.info(f"  [DRY] 會加入: {comp_data['name']} (Tier {comp_data['tier']})")
                added += 1
                continue

            competitor = Competitor(
                id=uuid4(),
                name=comp_data["name"],
                store_code=comp_data["store_code"],
                tier=comp_data["tier"],
                platform=comp_data["platform"],
                notes=comp_data.get("notes"),
                is_active=True,
            )
            db.add(competitor)
            logger.info(f"  ✅ 已加入: {comp_data['name']} (Tier {comp_data['tier']}, store={comp_data['store_code']})")
            added += 1

        if not dry_run:
            await db.commit()

    logger.info(f"\n完成：加入 {added} 間，跳過 {skipped} 間")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="初始化競爭商戶")
    parser.add_argument("--dry-run", action="store_true", help="唔寫 DB，只睇結果")
    args = parser.parse_args()
    asyncio.run(main(dry_run=args.dry_run))
