#!/usr/bin/env python3
# =============================================
# 競品建庫 CLI 腳本
# =============================================
# 用途：建立競品商品庫、補建初始價格快照、查看統計
#
# 子命令：
#   build     — 調用 CatalogService（Algolia + HTTP，0 credits）
#   snapshot  — 為無快照商品用 Firecrawl 補建價格快照（1 credit/商品）
#   stats     — 顯示競品庫統計
#
# 執行：
#   python scripts/build_competitor_db.py build --platform hktvmall
#   python scripts/build_competitor_db.py build --platform hktvmall --dry-run
#   python scripts/build_competitor_db.py snapshot --batch-size 50
#   python scripts/build_competitor_db.py stats
# =============================================

import asyncio
import sys
import os
import time
import argparse
import logging
from pathlib import Path

# 添加項目根目錄到 Python 路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import select, func, distinct
from app.models.database import async_session_maker, init_db, utcnow
from app.models.competitor import Competitor, CompetitorProduct, PriceSnapshot

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


# =============================================
# build — 建庫（0 credits）
# =============================================

async def cmd_build(platform: str, dry_run: bool):
    """建庫：HKTVmall 用 Algolia API，惠康用 HTTP — 不消耗 Firecrawl credits"""
    print("=" * 60)
    print("競品建庫工具")
    print("=" * 60)
    print(f"  平台: {platform}")
    print(f"  模式: {'測試模式（不執行）' if dry_run else '正式執行'}")
    print("=" * 60)

    await init_db()

    if dry_run:
        # 測試模式：驗證 API 連通性
        if platform in ("hktvmall", "all"):
            from app.connectors.hktv_api import HKTVApiClient
            client = HKTVApiClient()
            try:
                products = await client.search_products("和牛", page_size=5)
                print(f"\nHKTVmall Algolia API 正常")
                print(f"  測試關鍵詞「和牛」返回 {len(products)} 個結果：")
                for p in products[:3]:
                    print(f"    - {p.name} | ${p.price}")
            finally:
                await client.close()

        if platform in ("wellcome", "all"):
            print(f"\n惠康建庫需要 agent_browser，dry-run 跳過")
        return

    # 正式建庫
    async with async_session_maker() as session:
        from app.services.cataloger import CatalogService
        result = await CatalogService.build_catalog(session, platform=platform)

        print("\n" + "=" * 60)
        print("建庫結果:")
        for plat, plat_stats in result.items():
            if isinstance(plat_stats, dict) and "skipped" not in plat_stats:
                print(f"  [{plat}]")
                print(f"    總抓取: {plat_stats.get('total_fetched', 0)}")
                print(f"    新增: {plat_stats.get('new', 0)}")
                print(f"    更新: {plat_stats.get('updated', 0)}")
                print(f"    無變化: {plat_stats.get('unchanged', 0)}")
            elif isinstance(plat_stats, dict) and plat_stats.get("skipped"):
                print(f"  [{plat}] 跳過: {plat_stats.get('reason', '')}")
        print("=" * 60)


# =============================================
# snapshot — 補建價格快照（Firecrawl, 1 credit/商品）
# =============================================

async def cmd_snapshot(platform: str, batch_size: int, dry_run: bool):
    """為沒有 PriceSnapshot 的商品補建初始快照（用 Firecrawl）"""
    print("=" * 60)
    print("價格快照補建工具（Firecrawl）")
    print("=" * 60)
    print(f"  平台: {platform}")
    print(f"  批次大小: {batch_size}")
    print(f"  模式: {'測試模式（不執行）' if dry_run else '正式執行'}")
    print(f"  注意: 每個商品消耗 1 Firecrawl credit")
    print("=" * 60)

    await init_db()

    async with async_session_maker() as session:
        # 查詢沒有 PriceSnapshot 的活躍商品
        has_snapshot = select(PriceSnapshot.competitor_product_id).distinct()

        query = (
            select(CompetitorProduct)
            .join(Competitor, CompetitorProduct.competitor_id == Competitor.id)
            .where(
                CompetitorProduct.is_active == True,
                ~CompetitorProduct.id.in_(has_snapshot),
            )
        )

        if platform != "all":
            query = query.where(Competitor.platform == platform)

        query = query.limit(batch_size)

        result = await session.execute(query)
        products = result.scalars().all()

        if not products:
            print("\n所有商品都已有價格快照")
            return

        print(f"\n找到 {len(products)} 個待補建快照的商品")

        if dry_run:
            print("\n待處理商品列表:")
            for idx, cp in enumerate(products[:10], 1):
                url_display = cp.url[:60] + "..." if len(cp.url) > 60 else cp.url
                print(f"  {idx}. {cp.name[:50]} ({url_display})")
            if len(products) > 10:
                print(f"  ... 還有 {len(products) - 10} 個商品")
            print(f"\n測試模式：不會實際抓取，預計消耗 {len(products)} credits")
            return

        # 確認（非交互環境需設定 BATCH_AUTO_CONFIRM=1）
        auto_confirm = os.environ.get("BATCH_AUTO_CONFIRM", "0") == "1"
        if not auto_confirm:
            try:
                confirm = input(
                    f"\n將為 {len(products)} 個商品抓取價格"
                    f"（消耗 ~{len(products)} credits）。繼續？(y/N): "
                )
                if confirm.lower() != "y":
                    print("已取消")
                    return
            except EOFError:
                print("非交互模式：請設定 BATCH_AUTO_CONFIRM=1 以允許自動執行")
                return

        # Firecrawl 是同步 SDK，CLI 順序執行直接調用即可
        from app.connectors.firecrawl import get_firecrawl_connector
        connector = get_firecrawl_connector()

        success_count = 0
        error_count = 0
        now = utcnow()
        commit_every = 10

        print("\n開始抓取...\n")

        for idx, cp in enumerate(products, 1):
            name_display = cp.name[:40] + "..." if len(cp.name) > 40 else cp.name
            print(f"[{idx}/{len(products)}] 抓取: {name_display}")

            try:
                info = connector.extract_product_info(cp.url)

                if info.price is not None:
                    session.add(PriceSnapshot(
                        competitor_product_id=cp.id,
                        price=info.price,
                        original_price=info.original_price,
                        discount_percent=info.discount_percent,
                        stock_status=info.stock_status,
                        rating=info.rating,
                        review_count=info.review_count,
                        promotion_text=info.promotion_text,
                        currency="HKD",
                    ))
                    cp.last_scraped_at = now
                    success_count += 1

                    price_str = f"${info.price}"
                    if info.original_price:
                        price_str += f" (原價 ${info.original_price})"
                    print(f"  -> {price_str}")
                else:
                    error_count += 1
                    print(f"  -> 未能提取價格")

            except Exception as e:
                error_count += 1
                print(f"  -> 錯誤: {str(e)[:80]}")

            # 每 N 個商品中間 commit（防止全量回滾丟失已消耗的 credits）
            if idx % commit_every == 0:
                await session.commit()

            # 請求間延遲
            if idx < len(products):
                time.sleep(1.0)

        await session.commit()

        print("\n" + "=" * 60)
        print("快照補建結果:")
        print(f"  處理: {len(products)}")
        print(f"  成功: {success_count}")
        print(f"  失敗: {error_count}")
        print(f"  消耗 credits: ~{success_count + error_count}")
        print("=" * 60)


# =============================================
# stats — 競品庫統計
# =============================================

async def cmd_stats():
    """顯示競品庫全面統計"""
    await init_db()

    async with async_session_maker() as session:
        # 各平台商品數
        platform_stmt = (
            select(
                Competitor.platform,
                func.count(CompetitorProduct.id).label("count"),
            )
            .join(CompetitorProduct, CompetitorProduct.competitor_id == Competitor.id)
            .where(CompetitorProduct.is_active == True)
            .group_by(Competitor.platform)
        )
        platform_result = await session.execute(platform_stmt)
        platforms = {row.platform: row.count for row in platform_result}

        # 有快照的商品數
        has_snapshot_stmt = (
            select(func.count(distinct(PriceSnapshot.competitor_product_id)))
        )
        has_snapshot_result = await session.execute(has_snapshot_stmt)
        has_snapshot = has_snapshot_result.scalar() or 0

        # 快照總數
        total_snaps_stmt = select(func.count()).select_from(PriceSnapshot)
        total_snaps_result = await session.execute(total_snaps_stmt)
        total_snaps = total_snaps_result.scalar() or 0

        # 已打標數
        tagged_stmt = (
            select(func.count())
            .select_from(CompetitorProduct)
            .where(
                CompetitorProduct.is_active == True,
                CompetitorProduct.category_tag.isnot(None),
            )
        )
        tagged_result = await session.execute(tagged_stmt)
        tagged = tagged_result.scalar() or 0

        # 待匹配數
        needs_match_stmt = (
            select(func.count())
            .select_from(CompetitorProduct)
            .where(
                CompetitorProduct.is_active == True,
                CompetitorProduct.needs_matching == True,
            )
        )
        needs_match_result = await session.execute(needs_match_stmt)
        needs_match = needs_match_result.scalar() or 0

        total_active = sum(platforms.values())
        no_snapshot = total_active - has_snapshot

        print("=" * 60)
        print("競品庫統計")
        print("=" * 60)

        print(f"\n商品總數（活躍）: {total_active}")
        for plat, count in sorted(platforms.items()):
            print(f"  {plat}: {count}")

        print(f"\n價格快照:")
        print(f"  有快照的商品: {has_snapshot}")
        print(f"  無快照的商品: {no_snapshot}")
        print(f"  快照總數: {total_snaps}")

        print(f"\n標籤狀態:")
        print(f"  已打標: {tagged}")
        print(f"  未打標: {total_active - tagged}")
        print(f"  待匹配: {needs_match}")
        print("=" * 60)


# =============================================
# CLI 入口
# =============================================

def main():
    parser = argparse.ArgumentParser(
        description="競品建庫 CLI 工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
子命令說明:
  build      建庫（HKTVmall: Algolia API, 惠康: HTTP）— 0 credits
  snapshot   為無快照商品補建價格快照（Firecrawl）— 1 credit/商品
  stats      顯示競品庫統計

範例:
  python scripts/build_competitor_db.py build --platform hktvmall --dry-run
  python scripts/build_competitor_db.py build --platform all
  python scripts/build_competitor_db.py snapshot --batch-size 100
  python scripts/build_competitor_db.py stats
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="操作類型")

    # build
    build_parser = subparsers.add_parser("build", help="建庫（0 credits）")
    build_parser.add_argument(
        "--platform", type=str, default="all",
        choices=["hktvmall", "wellcome", "all"],
        help="平台（預設: all）",
    )
    build_parser.add_argument("--dry-run", action="store_true", help="測試模式")

    # snapshot
    snap_parser = subparsers.add_parser(
        "snapshot", help="補建價格快照（Firecrawl, 1 credit/商品）",
    )
    snap_parser.add_argument(
        "--platform", type=str, default="all",
        choices=["hktvmall", "wellcome", "all"],
        help="平台（預設: all）",
    )
    snap_parser.add_argument(
        "--batch-size", type=int, default=50,
        help="每批處理數量（預設: 50）",
    )
    snap_parser.add_argument("--dry-run", action="store_true", help="測試模式")

    # stats
    subparsers.add_parser("stats", help="顯示統計")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return

    if args.command == "build":
        asyncio.run(cmd_build(platform=args.platform, dry_run=args.dry_run))
    elif args.command == "snapshot":
        asyncio.run(cmd_snapshot(
            platform=args.platform,
            batch_size=args.batch_size,
            dry_run=args.dry_run,
        ))
    elif args.command == "stats":
        asyncio.run(cmd_stats())


if __name__ == "__main__":
    main()
