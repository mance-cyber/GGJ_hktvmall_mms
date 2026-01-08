#!/usr/bin/env python3
# =============================================
# HKTVScraper 測試腳本
# =============================================
# 測試新的 HKTVmall 專用抓取器
#
# 使用方法：
#   cd backend
#   python test_hktv_scraper.py
#
# 測試項目：
#   1. URL 解析和驗證
#   2. 商品 URL 發現（JavaScript 渲染）
#   3. 單個商品抓取
#   4. 完整流程測試

import asyncio
import sys
import os
import time

# 添加 app 目錄到路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.connectors.hktv_scraper import (
    HKTVScraper,
    HKTVUrlParser,
    get_hktv_scraper,
    HKTVProduct,
    ScrapeResult
)


# =============================================
# 測試數據
# =============================================

# Steak King Market 商店（和牛類）
TEST_STORE_URL = "https://www.hktvmall.com/hktv/zh/main/Steak-King-Market/s/B1517001"

# 已知有效的商品 URL（用於測試單個抓取）
# 注意：這些 URL 可能會失效，需要定期更新
TEST_PRODUCT_URLS = [
    "https://www.hktvmall.com/hktv/zh/p/H7917001_S_B1517001001",  # 可能的 SKU 格式
]

# 其他測試商店
ALTERNATIVE_STORE_URLS = [
    # 如果主測試 URL 無效，可以嘗試這些
    "https://www.hktvmall.com/hktv/zh/main/Market-Place-by-Jasons/s/H0851001",
    "https://www.hktvmall.com/hktv/zh/main/7-Eleven/s/H6800001",
]


def print_header(title: str):
    """打印標題"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_result(success: bool, message: str):
    """打印結果"""
    status = "[PASS]" if success else "[FAIL]"
    print(f"  {status}: {message}")


def test_url_parser():
    """測試 URL 解析器"""
    print_header("測試 1: URL 解析器")

    parser = HKTVUrlParser()

    # 測試商品 URL 識別
    test_cases = [
        ("https://www.hktvmall.com/hktv/zh/p/H0340001_S_SK_WAGYU", True, "H0340001"),
        ("https://www.hktvmall.com/hktv/zh/p/H7917001_S_B1517001001", True, "H7917001"),
        ("https://www.hktvmall.com/hktv/zh/main/store/s/B1517001", False, None),
        ("https://www.google.com", False, None),
    ]

    all_passed = True
    for url, expected_is_product, expected_sku in test_cases:
        is_product = parser.is_product_url(url)
        sku = parser.extract_sku(url)

        passed = (is_product == expected_is_product) and (sku == expected_sku)
        all_passed = all_passed and passed

        print_result(passed, f"URL: {url[:50]}...")
        print(f"       is_product={is_product} (expected: {expected_is_product})")
        print(f"       sku={sku} (expected: {expected_sku})")

    # 測試商店 URL 識別
    store_url = "https://www.hktvmall.com/hktv/zh/main/Steak-King-Market/s/B1517001"
    is_store = parser.is_store_url(store_url)
    store_code = parser.extract_store_code(store_url)

    print_result(is_store and store_code == "B1517001",
                 f"商店 URL 解析: code={store_code}")

    # 測試 URL 構建
    built_url = parser.build_product_url("H0340001")
    expected = "https://www.hktvmall.com/hktv/zh/p/H0340001"
    print_result(built_url == expected, f"URL 構建: {built_url}")

    return all_passed


def test_url_discovery():
    """測試商品 URL 發現（JavaScript 渲染）"""
    print_header("測試 2: 商品 URL 發現（JavaScript 渲染）")

    scraper = get_hktv_scraper()

    print(f"  測試 URL: {TEST_STORE_URL}")
    print("  注意：此測試需要較長時間（等待 JavaScript 渲染）...")

    start_time = time.time()

    try:
        # 發現商品 URL
        product_urls = scraper.discover_product_urls_from_store(
            TEST_STORE_URL,
            max_products=10  # 只獲取前 10 個以節省時間
        )

        duration = time.time() - start_time

        print(f"\n  執行時間: {duration:.2f} 秒")
        print(f"  發現 URL 數量: {len(product_urls)}")

        if product_urls:
            print("\n  發現的商品 URL:")
            for i, url in enumerate(product_urls[:5], 1):
                sku = HKTVUrlParser.extract_sku(url)
                print(f"    {i}. [SKU: {sku}] {url[:60]}...")

            # 驗證 URL 格式
            valid_count = sum(1 for url in product_urls if HKTVUrlParser.is_product_url(url))
            print(f"\n  有效商品 URL 數量: {valid_count}/{len(product_urls)}")

            print_result(valid_count > 0, f"成功發現 {valid_count} 個有效商品 URL")
            return valid_count > 0
        else:
            print_result(False, "未發現任何商品 URL")
            print("\n  可能原因：")
            print("    - HKTVmall 頁面結構已變更")
            print("    - JavaScript 渲染時間不足")
            print("    - 商店頁面沒有商品")
            return False

    except Exception as e:
        print_result(False, f"發生錯誤: {str(e)}")
        return False


def test_single_product_scrape():
    """測試單個商品抓取"""
    print_header("測試 3: 單個商品抓取")

    scraper = get_hktv_scraper()

    # 先獲取一個有效的商品 URL
    print("  正在獲取有效的商品 URL...")

    try:
        product_urls = scraper.discover_product_urls_from_store(
            TEST_STORE_URL,
            max_products=3
        )

        if not product_urls:
            print_result(False, "無法獲取商品 URL 進行測試")
            return False

        test_url = product_urls[0]
        print(f"  測試商品 URL: {test_url}")

        # 抓取商品詳情
        print("  正在抓取商品詳情...")
        start_time = time.time()

        raw_data = scraper.scrape_product_page(test_url)
        product = scraper.parse_product_data(test_url, raw_data)

        duration = time.time() - start_time

        print(f"\n  執行時間: {duration:.2f} 秒")
        print("\n  商品資料：")
        print(f"    SKU: {product.sku}")
        print(f"    名稱: {product.name}")
        print(f"    價格: HK${product.price}")
        print(f"    原價: HK${product.original_price}")
        print(f"    折扣: {product.discount_percent}%")
        print(f"    品牌: {product.brand}")
        print(f"    庫存: {product.stock_status}")
        print(f"    圖片: {product.image_url[:50] if product.image_url else 'N/A'}...")

        # 驗證結果
        has_name = product.name and product.name != "未知商品"
        has_valid_data = has_name and (product.price is not None or product.image_url is not None)

        print_result(has_valid_data, f"成功抓取商品: {product.name[:30]}...")
        return has_valid_data

    except Exception as e:
        print_result(False, f"發生錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_full_scrape():
    """測試完整抓取流程"""
    print_header("測試 4: 完整抓取流程（異步）")

    scraper = get_hktv_scraper()

    print(f"  測試 URL: {TEST_STORE_URL}")
    print("  最大商品數: 5")
    print("  注意：此測試可能需要較長時間...")

    start_time = time.time()

    try:
        result = await scraper.scrape_store_products(
            TEST_STORE_URL,
            max_products=5,
            scrape_details=True
        )

        duration = time.time() - start_time

        print(f"\n  執行時間: {duration:.2f} 秒")
        print(f"  抓取結果：")
        print(f"    成功: {result.success}")
        print(f"    發現 URL: {result.total_found}")
        print(f"    成功抓取: {result.total_scraped}")
        print(f"    失敗數量: {len(result.failed_urls)}")
        print(f"    使用 Credits: {result.credits_used}")

        if result.products:
            print("\n  抓取的商品：")
            for i, p in enumerate(result.products[:5], 1):
                print(f"    {i}. {p.name[:40]}... - HK${p.price}")

        if result.error_message:
            print(f"\n  錯誤信息: {result.error_message}")

        if result.failed_urls:
            print(f"\n  失敗的 URL ({len(result.failed_urls)}):")
            for url in result.failed_urls[:3]:
                print(f"    - {url[:50]}...")

        print_result(result.success and result.total_scraped > 0,
                     f"完整流程測試: 成功抓取 {result.total_scraped} 個商品")

        return result.success and result.total_scraped > 0

    except Exception as e:
        print_result(False, f"發生錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主測試函數"""
    print("\n")
    print("=" * 60)
    print("       HKTVScraper 測試套件")
    print("       針對 HKTVmall JavaScript SPA 優化的抓取器")
    print("=" * 60)

    results = {}

    # 測試 1: URL 解析器（不需要網絡）
    results["URL 解析器"] = test_url_parser()

    # 測試 2: 商品 URL 發現（需要網絡）
    results["URL 發現"] = test_url_discovery()

    # 測試 3: 單個商品抓取（需要網絡）
    results["單個商品抓取"] = test_single_product_scrape()

    # 測試 4: 完整抓取流程（需要網絡，異步）
    results["完整流程"] = asyncio.run(test_full_scrape())

    # 總結
    print_header("測試總結")

    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)

    for test_name, passed in results.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"  {status}: {test_name}")

    print(f"\n  Total: {passed_tests}/{total_tests} tests passed")

    if passed_tests == total_tests:
        print("\n  All tests passed! HKTVScraper is ready.")
    else:
        print("\n  Some tests failed. Please check error messages.")

    return passed_tests == total_tests


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
