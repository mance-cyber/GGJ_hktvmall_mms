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

from sqlalchemy import select
from app.models.database import async_session_maker
from app.models.product import Product
from app.services.competitor_builder import CompetitorBuilder

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)


async def main(mode: str, dry_run: bool = False, product_id: str = None):
    builder = CompetitorBuilder()

    if mode == "full":
        logger.info("=" * 60)
        logger.info("Full build: Line A + Line B")
        logger.info("=" * 60)

        # Line A with per-product commits
        logger.info("\n--- Line A: 自家商品 → 搵競品 ---")
        await run_line_a(builder, dry_run=dry_run, product_id=product_id)

        # Line B with single commit
        logger.info("\n--- Line B: 商戶 → 全部生鮮 ---")
        async with async_session_maker() as db:
            result_b = await builder.build_line_b(db, dry_run=dry_run)
            logger.info(f"Line B 結果: {json.dumps(result_b, ensure_ascii=False)}")
            if not dry_run:
                await db.commit()
                logger.info("✅ Line B 完成並已 commit")

    elif mode == "line-a":
        logger.info("Line A: 自家商品 → 搵競品")
        await run_line_a(builder, dry_run=dry_run, product_id=product_id)

    elif mode == "line-b":
        logger.info("Line B: 商戶 → 全部生鮮")
        async with async_session_maker() as db:
            result = await builder.build_line_b(db, dry_run=dry_run)
            logger.info(f"結果: {json.dumps(result, ensure_ascii=False)}")
            if not dry_run:
                await db.commit()
                logger.info("✅ Line B 完成並已 commit")

    elif mode == "prices":
        logger.info("Price refresh: 更新所有競品價格")
        async with async_session_maker() as db:
            result = await builder.refresh_prices(db)
            logger.info(f"結果: {json.dumps(result, ensure_ascii=False)}")
            await db.commit()
            logger.info("✅ Price refresh 完成")

    elif mode == "discover":
        logger.info("Discover: 搜索新商戶")
        async with async_session_maker() as db:
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


async def run_line_a(builder: CompetitorBuilder, dry_run: bool = False, product_id: str = None):
    """
    Per-product commit 模式：每件商品獨立 session，commit 後再處理下一件。
    即使中途 crash，已完成的商品資料都會保留。
    """
    # Step 1: 取所有商品 ID（獨立 session）
    async with async_session_maker() as db:
        stmt = select(Product.id, Product.name).where(Product.status == "active")
        if product_id:
            stmt = stmt.where(Product.id == product_id)
        result = await db.execute(stmt)
        all_products = [(str(r[0]), r[1]) for r in result.all()]

    if not all_products:
        logger.warning("無商品可搜索")
        return

    logger.info(f"共 {len(all_products)} 件商品，逐一處理（per-product commit）")

    total_found = 0
    total_mappings = 0
    success_count = 0
    fail_count = 0

    for i, (pid, pname) in enumerate(all_products, 1):
        logger.info(f"\n{'='*50}")
        logger.info(f"[{i}/{len(all_products)}] {pname} ({pid})")
        logger.info(f"{'='*50}")
        try:
            async with async_session_maker() as db:
                result = await builder.build_line_a(db, dry_run=dry_run, product_id=pid)
                if not dry_run:
                    await db.commit()
                    logger.info(f"✅ [{i}/{len(all_products)}] commit 成功: {json.dumps(result, ensure_ascii=False)}")
                else:
                    logger.info(f"🔍 [{i}/{len(all_products)}] dry-run: {json.dumps(result, ensure_ascii=False)}")
                total_found += result.get("competitors_found", 0)
                total_mappings += result.get("mappings_created", 0)
                success_count += 1
        except Exception as e:
            import traceback
            logger.error(f"❌ [{i}/{len(all_products)}] 商品 {pname} ({pid}) 失敗: {e}")
            traceback.print_exc()
            fail_count += 1
            continue  # 繼續下一件，唔影響已完成的

    logger.info(f"\n{'='*60}")
    logger.info(f"✅ Line A 完成")
    logger.info(f"   成功: {success_count}/{len(all_products)} 件")
    logger.info(f"   失敗: {fail_count}/{len(all_products)} 件")
    logger.info(f"   競品總計: {total_found}")
    logger.info(f"   映射總計: {total_mappings}")
    logger.info(f"{'='*60}")


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
