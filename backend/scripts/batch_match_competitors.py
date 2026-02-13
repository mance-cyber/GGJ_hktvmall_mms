#!/usr/bin/env python3
# =============================================
# 批量競品匹配腳本
# =============================================
# 用途：為所有 GoGoJap 商品批量搜索 HKTVmall 競品
# 執行：python scripts/batch_match_competitors.py
# =============================================

import asyncio
import sys
import os
from pathlib import Path

# 添加項目根目錄到 Python 路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import select, and_
from app.models.database import async_session_maker, init_db
from app.models.product import Product, ProductCompetitorMapping
from app.services.competitor_matcher import CompetitorMatcherService


async def batch_find_competitors(
    limit: int = 50,
    category_main: str = None,
    category_sub: str = None,
    dry_run: bool = False,
    platform: str = "hktvmall",
):
    """
    批量為商品搜索競品（多平台）

    Args:
        limit: 一次處理多少個商品（最多 100）
        category_main: 篩選大分類（可選）
        category_sub: 篩選小分類（可選）
        dry_run: 測試模式（不實際保存）
        platform: 搜索平台 ("hktvmall" | "wellcome")
    """
    print("=" * 60)
    print("批量競品匹配工具")
    print("=" * 60)
    print(f"配置:")
    print(f"  - 平台: {platform}")
    print(f"  - 處理數量: {limit}")
    print(f"  - 大分類: {category_main or '全部'}")
    print(f"  - 小分類: {category_sub or '全部'}")
    print(f"  - 模式: {'測試模式（不保存）' if dry_run else '正式執行'}")
    print("=" * 60)

    # 初始化數據庫
    await init_db()

    async with async_session_maker() as session:
        # 查詢尚未有競品關聯的商品
        subquery = select(ProductCompetitorMapping.product_id)

        # 支援多種 source：gogojap_csv / xlsx_import
        query = select(Product).where(
            and_(
                Product.source.in_(['gogojap_csv', 'xlsx_import']),
                ~Product.id.in_(subquery)
            )
        )

        if category_main:
            query = query.where(Product.category_main == category_main)
        if category_sub:
            query = query.where(Product.category_sub == category_sub)

        query = query.limit(limit)

        result = await session.execute(query)
        products = result.scalars().all()

        if not products:
            print("\n❌ 沒有待處理的商品")
            print("   所有商品都已有競品映射，或沒有符合條件的商品")
            return

        print(f"\n✅ 找到 {len(products)} 個待處理商品\n")

        if dry_run:
            print("📋 待處理商品列表:")
            for idx, product in enumerate(products[:10], 1):
                print(f"  {idx}. {product.name_zh} (SKU: {product.sku})")
            if len(products) > 10:
                print(f"  ... 還有 {len(products) - 10} 個商品")
            print("\n⚠️ 測試模式：不會實際搜索競品")
            return

        # 非交互模式：自動執行
        auto_confirm = os.environ.get("BATCH_AUTO_CONFIRM", "0") == "1"
        if not auto_confirm:
            try:
                confirm = input(f"\n將處理 {len(products)} 個商品，可能消耗 API 額度。繼續？(y/N): ")
                if confirm.lower() != 'y':
                    print("已取消")
                    return
            except EOFError:
                pass  # 非交互模式，直接執行

        print("\n開始處理...\n")

        service = CompetitorMatcherService()

        success_count = 0
        error_count = 0
        total_matches = 0

        for idx, product in enumerate(products, 1):
            display_name = product.name_zh or product.name or product.sku
            print(f"[{idx}/{len(products)}] 處理: {display_name}")

            try:
                results = await service.find_competitors_for_product(
                    db=session,
                    product=product,
                    platform=platform,
                    max_candidates=3,
                )

                matches = [r for r in results if r.is_match and r.match_confidence >= 0.4]

                if matches:
                    for match in matches[:1]:  # 每個商品最多保存一個最佳匹配
                        await service.save_match_to_db(
                            db=session,
                            product_id=str(product.id),
                            match_result=match,
                            platform=platform,
                        )
                        total_matches += 1
                        print(f"  ✓ 找到競品: {match.candidate_name} (信心度: {match.match_confidence:.2f})")
                else:
                    print(f"  ⚠️ 未找到匹配的競品")

                success_count += 1

            except Exception as e:
                error_count += 1
                print(f"  ✗ 錯誤: {str(e)}")

        await session.commit()

        print("\n" + "=" * 60)
        print("📊 執行結果:")
        print(f"  - 處理商品: {len(products)}")
        print(f"  - 成功: {success_count}")
        print(f"  - 失敗: {error_count}")
        print(f"  - 找到競品: {total_matches}")
        print("=" * 60)


async def show_stats():
    """顯示統計信息"""
    await init_db()

    async with async_session_maker() as session:
        # 總商品數
        total_result = await session.execute(
            select(Product).where(Product.source.in_(['gogojap_csv', 'xlsx_import']))
        )
        total_products = len(total_result.scalars().all())

        # 已有競品的商品數
        mapped_result = await session.execute(
            select(ProductCompetitorMapping.product_id).distinct()
        )
        mapped_count = len(mapped_result.scalars().all())

        # 待處理數
        pending = total_products - mapped_count

        print("=" * 60)
        print("📊 競品匹配統計")
        print("=" * 60)
        print(f"總商品數: {total_products}")
        if total_products > 0:
            print(f"已匹配: {mapped_count} ({mapped_count/total_products*100:.1f}%)")
            print(f"待處理: {pending} ({pending/total_products*100:.1f}%)")
        else:
            print("沒有商品")
        print("=" * 60)


def main():
    """主程序"""
    import argparse

    parser = argparse.ArgumentParser(description="批量競品匹配工具（多平台）")
    parser.add_argument("--limit", type=int, default=50, help="處理數量（預設: 50）")
    parser.add_argument("--category-main", type=str, help="篩選大分類")
    parser.add_argument("--category-sub", type=str, help="篩選小分類")
    parser.add_argument("--platform", type=str, default="hktvmall",
                        choices=["hktvmall", "wellcome"],
                        help="搜索平台（預設: hktvmall）")
    parser.add_argument("--dry-run", action="store_true", help="測試模式（不實際執行）")
    parser.add_argument("--stats", action="store_true", help="顯示統計信息")

    args = parser.parse_args()

    if args.stats:
        asyncio.run(show_stats())
    else:
        asyncio.run(batch_find_competitors(
            limit=args.limit,
            category_main=args.category_main,
            category_sub=args.category_sub,
            dry_run=args.dry_run,
            platform=args.platform,
        ))


if __name__ == "__main__":
    main()
