"""
CLI: Competitor Builder v2 — 競品建庫 + 價格更新

Usage:
    python scripts/run_competitor_build.py --mode full       # 完整建庫（Line A + B）
    python scripts/run_competitor_build.py --mode line-a     # 自家商品搵競品
    python scripts/run_competitor_build.py --mode line-b     # 商戶全部生鮮
    python scripts/run_competitor_build.py --mode prices     # 價格更新
    python scripts/run_competitor_build.py --mode discover   # 新商戶發現
    python scripts/run_competitor_build.py --mode line-a --dry-run
    python scripts/run_competitor_build.py --mode line-a --product-id <UUID>
"""

import sys
import os
import asyncio
import argparse
import json
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.database import async_session_maker
from app.services.competitor_builder import CompetitorBuilder

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)


async def main(mode: str, dry_run: bool = False, product_id: str = None):
    builder = CompetitorBuilder()

    async with async_session_maker() as db:
        if mode == "full":
            logger.info("=" * 60)
            logger.info("Full build: Line A + Line B")
            logger.info("=" * 60)

            logger.info("\n--- Line A: 自家商品 → 搵競品 ---")
            result_a = await builder.build_line_a(db, dry_run=dry_run, product_id=product_id)
            logger.info(f"Line A 結果: {json.dumps(result_a, ensure_ascii=False)}")

            logger.info("\n--- Line B: 商戶 → 全部生鮮 ---")
            result_b = await builder.build_line_b(db, dry_run=dry_run)
            logger.info(f"Line B 結果: {json.dumps(result_b, ensure_ascii=False)}")

            if not dry_run:
                await db.commit()
                logger.info("\n✅ Full build 完成並已 commit")

        elif mode == "line-a":
            logger.info("Line A: 自家商品 → 搵競品")
            result = await builder.build_line_a(db, dry_run=dry_run, product_id=product_id)
            logger.info(f"結果: {json.dumps(result, ensure_ascii=False)}")
            if not dry_run:
                await db.commit()
                logger.info("✅ Line A 完成並已 commit")

        elif mode == "line-b":
            logger.info("Line B: 商戶 → 全部生鮮")
            result = await builder.build_line_b(db, dry_run=dry_run)
            logger.info(f"結果: {json.dumps(result, ensure_ascii=False)}")
            if not dry_run:
                await db.commit()
                logger.info("✅ Line B 完成並已 commit")

        elif mode == "prices":
            logger.info("Price refresh: 更新所有競品價格")
            result = await builder.refresh_prices(db)
            logger.info(f"結果: {json.dumps(result, ensure_ascii=False)}")
            await db.commit()
            logger.info("✅ Price refresh 完成")

        elif mode == "discover":
            logger.info("Discover: 搜索新商戶")
            new_merchants = await builder.discover_new_merchants(db)
            if new_merchants:
                logger.info(f"\n發現 {len(new_merchants)} 間新商戶:")
                for m in new_merchants:
                    logger.info(
                        f"  🏪 {m['store_name']} ({m['product_count']} 件相關商品)"
                    )
                    for sample in m['sample_products']:
                        logger.info(f"     - {sample}")
            else:
                logger.info("未發現新商戶")

        else:
            logger.error(f"未知模式: {mode}")
            sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Competitor Builder v2")
    parser.add_argument(
        "--mode",
        required=True,
        choices=["full", "line-a", "line-b", "prices", "discover"],
        help="建庫模式",
    )
    parser.add_argument("--dry-run", action="store_true", help="唔寫 DB，只睇結果")
    parser.add_argument("--product-id", help="指定單件自家商品 UUID（Line A 用）")
    args = parser.parse_args()
    asyncio.run(main(mode=args.mode, dry_run=args.dry_run, product_id=args.product_id))
