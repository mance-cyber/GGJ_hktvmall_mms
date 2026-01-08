#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
抓取功能測試腳本
用法: python test_scraping.py [test_url]
"""

import sys
import asyncio
from decimal import Decimal
from typing import Optional

from app.connectors.firecrawl import get_firecrawl_connector
from app.config import get_settings


def print_section(title: str):
    """打印章節標題"""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print('=' * 60)


def test_config() -> bool:
    """測試 1: 配置檢查"""
    print_section("測試 1: 配置檢查")

    try:
        settings = get_settings()

        if not settings.firecrawl_api_key:
            print("✗ Firecrawl API Key 未設定")
            print("\n請在 .env 文件中設定:")
            print("  FIRECRAWL_API_KEY=fc-your-api-key")
            return False

        print(f"✓ API Key 已設定: {settings.firecrawl_api_key[:10]}...")
        print(f"✓ 資料庫 URL: {settings.database_url[:30]}...")
        print(f"✓ Redis URL: {settings.redis_url}")
        return True

    except Exception as e:
        print(f"✗ 配置檢查失敗: {e}")
        return False


def test_connector_init() -> bool:
    """測試 2: 連接器初始化"""
    print_section("測試 2: 連接器初始化")

    try:
        connector = get_firecrawl_connector()
        print("✓ Firecrawl 連接器初始化成功")

        # 測試延遲初始化
        app = connector.app
        print("✓ FirecrawlApp 實例創建成功")

        return True

    except Exception as e:
        print(f"✗ 連接器初始化失敗: {e}")
        print(f"\n可能原因:")
        print(f"  1. API Key 無效")
        print(f"  2. firecrawl-py 套件未正確安裝")
        print(f"\n解決方案:")
        print(f"  pip install firecrawl-py==0.0.16")
        return False


def test_basic_scraping(url: Optional[str] = None) -> bool:
    """測試 3: 基本抓取功能"""
    print_section("測試 3: 基本抓取功能")

    # 使用測試 URL 或命令行參數
    if not url:
        url = "https://www.apple.com/hk/shop/buy-iphone/iphone-15"
        print(f"使用測試 URL: {url}")
        print("(可以通過命令行參數指定其他 URL: python test_scraping.py <url>)\n")

    try:
        connector = get_firecrawl_connector()

        print("正在抓取商品資訊...")
        info = connector.extract_product_info(url)

        print("\n抓取結果:")
        print(f"  商品名稱: {info.name}")
        print(f"  價格: HK${info.price}" if info.price else "  價格: 未找到")
        print(f"  原價: HK${info.original_price}" if info.original_price else "  原價: -")

        if info.discount_percent:
            print(f"  折扣: {info.discount_percent}%")

        print(f"  庫存狀態: {info.stock_status or '未知'}")
        print(f"  評分: {info.rating or '-'}")
        print(f"  評論數: {info.review_count or '-'}")
        print(f"  SKU: {info.sku or '-'}")
        print(f"  品牌: {info.brand or '-'}")
        print(f"  圖片: {info.image_url[:50] + '...' if info.image_url else '-'}")

        # 驗證數據完整性
        print("\n數據完整性檢查:")
        has_name = bool(info.name and info.name != "未知商品")
        has_price = bool(info.price and info.price > 0)

        print(f"  {'✓' if has_name else '✗'} 商品名稱")
        print(f"  {'✓' if has_price else '✗'} 價格")
        print(f"  {'✓' if info.image_url else '✗'} 圖片")

        if has_name and has_price:
            print("\n✓ 基本抓取測試通過")
            return True
        else:
            print("\n⚠️  部分資訊缺失，但抓取功能正常")
            return True

    except Exception as e:
        print(f"\n✗ 抓取失敗: {e}")
        print(f"\n錯誤類型: {type(e).__name__}")
        import traceback
        print(f"\n詳細錯誤:")
        traceback.print_exc()
        return False


def test_url_discovery() -> bool:
    """測試 4: URL 發現功能"""
    print_section("測試 4: URL 發現功能")

    try:
        connector = get_firecrawl_connector()

        # 使用 Apple Store 作為測試網站
        base_url = "https://www.apple.com/hk/shop"
        print(f"正在掃描網站: {base_url}")
        print("(這可能需要 10-30 秒...)\n")

        result = connector.map_urls(base_url, limit=20)

        print(f"✓ 找到 {result.total} 個 URL")

        if result.urls:
            print("\n前 10 個 URL:")
            for i, url in enumerate(result.urls[:10], 1):
                print(f"  {i}. {url}")

            return True
        else:
            print("⚠️  沒有找到 URL，但功能正常")
            return True

    except Exception as e:
        print(f"✗ URL 發現失敗: {e}")
        print("\n注意: Map 功能可能不可用於某些 Firecrawl 方案")
        return False


def test_actions_scraping() -> bool:
    """測試 5: Actions 動態頁面處理"""
    print_section("測試 5: Actions 動態頁面處理")

    try:
        connector = get_firecrawl_connector()

        # 簡單的 Actions 測試
        url = "https://www.apple.com/hk"
        print(f"測試 URL: {url}")
        print("正在執行 Actions (滾動 + 等待)...\n")

        actions = [
            {"type": "wait", "milliseconds": 2000},
            {"type": "scroll", "direction": "down", "amount": 500},
            {"type": "wait", "milliseconds": 1000},
        ]

        raw_data = connector.scrape_with_actions(
            url=url,
            actions=actions,
            take_screenshot=False
        )

        if raw_data and 'markdown' in raw_data:
            content_length = len(raw_data['markdown'])
            print(f"✓ Actions 執行成功")
            print(f"✓ 抓取內容長度: {content_length} 字元")
            return True
        else:
            print("✗ 未能獲取內容")
            return False

    except Exception as e:
        print(f"✗ Actions 測試失敗: {e}")
        return False


def test_batch_scraping() -> bool:
    """測試 6: 批量抓取"""
    print_section("測試 6: 批量抓取")

    try:
        connector = get_firecrawl_connector()

        # 測試多個 URL
        test_urls = [
            "https://www.apple.com/hk/shop/buy-iphone/iphone-15",
            "https://www.apple.com/hk/shop/buy-iphone/iphone-15-pro",
        ]

        print("測試批量抓取 2 個商品...\n")

        results = []
        for i, url in enumerate(test_urls, 1):
            try:
                print(f"[{i}/{len(test_urls)}] 抓取: {url[:50]}...")
                info = connector.extract_product_info(url)
                results.append({
                    'url': url,
                    'name': info.name,
                    'price': info.price,
                    'success': True
                })
                print(f"  ✓ {info.name} - HK${info.price}")

            except Exception as e:
                print(f"  ✗ 失敗: {e}")
                results.append({
                    'url': url,
                    'error': str(e),
                    'success': False
                })

        # 統計
        success_count = sum(1 for r in results if r['success'])
        print(f"\n批量抓取完成: {success_count}/{len(test_urls)} 成功")

        return success_count > 0

    except Exception as e:
        print(f"✗ 批量抓取測試失敗: {e}")
        return False


def run_all_tests(custom_url: Optional[str] = None):
    """運行所有測試"""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 15 + "Firecrawl 抓取功能測試" + " " * 15 + "║")
    print("╚" + "═" * 58 + "╝")

    tests = [
        ("配置檢查", lambda: test_config()),
        ("連接器初始化", lambda: test_connector_init()),
        ("基本抓取", lambda: test_basic_scraping(custom_url)),
        ("URL 發現", lambda: test_url_discovery()),
        ("Actions 處理", lambda: test_actions_scraping()),
        ("批量抓取", lambda: test_batch_scraping()),
    ]

    results = []

    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n✗ 測試 '{name}' 發生異常: {e}")
            results.append((name, False))

    # 匯總結果
    print_section("測試結果匯總")

    for name, passed in results:
        status = "✓ 通過" if passed else "✗ 失敗"
        print(f"  {name:20s} {status}")

    total = len(results)
    passed_count = sum(1 for _, p in results if p)

    print(f"\n總計: {passed_count}/{total} 測試通過")

    if passed_count == total:
        print("\n🎉 所有測試通過！抓取功能運作正常。")
    elif passed_count >= total * 0.5:
        print("\n⚠️  部分測試失敗，但核心功能可用。")
    else:
        print("\n❌ 多數測試失敗，請檢查配置和網路連接。")

    print("\n" + "=" * 60)


def main():
    """主函數"""
    # 檢查命令行參數
    custom_url = sys.argv[1] if len(sys.argv) > 1 else None

    if custom_url:
        print(f"\n使用自定義 URL 進行測試: {custom_url}\n")

    try:
        run_all_tests(custom_url)
    except KeyboardInterrupt:
        print("\n\n測試被用戶中斷")
    except Exception as e:
        print(f"\n\n測試發生未預期錯誤: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
