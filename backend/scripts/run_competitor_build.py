"""
競品監測系統 v2 — 主執行腳本

Usage:
    python scripts/run_competitor_build.py --mode full      # 完整重建（Line A + B）
    python scripts/run_competitor_build.py --mode line-a    # 只跑 Line A（自家商品 → 競品）
    python scripts/run_competitor_build.py --mode line-b    # 只跑 Line B（商戶全部生鮮）
    python scripts/run_competitor_build.py --mode prices    # 每日價格刷新
    python scripts/run_competitor_build.py --mode discover  # 新商戶發現
    python scripts/run_competitor_build.py --mode alerts    # 生成價格警報

Examples:
    # 首次建庫（migration 後）
    python scripts/run_competitor_build.py --mode full

    # 每日 06:00 / 15:00 跑
    python scripts/run_competitor_build.py --mode prices
"""

import sys
import os
import asyncio
import argparse
import logging
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.database import async_session_maker
from app.services.competitor_builder import CompetitorBuilder
from app.services.price_alerter import PriceAlerter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)


async def run_full():
    """完整重建：Line A + Line B"""
    builder = CompetitorBuilder()
    async with async_session_maker() as db:
        logger.info("=== Line A: 自家商品 → 競品 ===")
        stats_a = await builder.build_line_a(db)
        await db.commit()

        logger.info("=== Line B: 核心商戶 → 全部生鮮 ===")
        stats_b = await builder.build_line_b(db)
        await db.commit()

    logger.info(f"完整重建完成: Line A={stats_a}, Line B={stats_b}")
    return {"line_a": stats_a, "line_b": stats_b}


async def run_line_a():
    """只跑 Line A"""
    builder = CompetitorBuilder()
    async with async_session_maker() as db:
        stats = await builder.build_line_a(db)
        await db.commit()
    logger.info(f"Line A 完成: {stats}")
    return stats


async def run_line_b():
    """只跑 Line B"""
    builder = CompetitorBuilder()
    async with async_session_maker() as db:
        stats = await builder.build_line_b(db)
        await db.commit()
    logger.info(f"Line B 完成: {stats}")
    return stats


async def run_prices():
    """每日價格刷新"""
    builder = CompetitorBuilder()
    async with async_session_maker() as db:
        stats = await builder.refresh_prices(db)
        await db.commit()
    logger.info(f"價格刷新完成: {stats}")
    return stats


async def run_discover():
    """新商戶發現"""
    builder = CompetitorBuilder()
    async with async_session_maker() as db:
        new_merchants = await builder.discover_new_merchants(db)

    if new_merchants:
        logger.info(f"發現 {len(new_merchants)} 間新商戶：")
        for m in new_merchants:
            logger.info(
                f"  {m['store_name']} ({m['store_code']}) — "
                f"示例商品: {m['sample_products'][:2]}"
            )
        print("\n=== 新商戶候選（請確認後加入 init_competitors.py）===")
        print(json.dumps(new_merchants, ensure_ascii=False, indent=2))
    else:
        logger.info("未發現新商戶")
    return new_merchants


async def run_alerts():
    """生成價格警報"""
    async with async_session_maker() as db:
        stats = await PriceAlerter.check_all_products(db)
        await db.commit()

        pending = await PriceAlerter.get_pending_alerts(db)
        if pending:
            logger.info(f"待通知警報 {len(pending)} 條：")
            for a in pending:
                logger.info(
                    f"  [{a.alert_type}] {a.old_value} → {a.new_value} "
                    f"({a.change_percent:+.1f}%)"
                )
        else:
            logger.info("無待通知警報")
    return stats


MODES = {
    "full": run_full,
    "line-a": run_line_a,
    "line-b": run_line_b,
    "prices": run_prices,
    "discover": run_discover,
    "alerts": run_alerts,
}


async def main(mode: str):
    if mode not in MODES:
        logger.error(f"未知模式: {mode}，可用: {list(MODES.keys())}")
        sys.exit(1)

    logger.info(f"執行模式: {mode}")
    result = await MODES[mode]()
    logger.info(f"執行完成: {result}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="競品監測系統 v2")
    parser.add_argument(
        "--mode",
        choices=list(MODES.keys()),
        default="prices",
        help="執行模式（預設: prices）",
    )
    args = parser.parse_args()
    asyncio.run(main(args.mode))
