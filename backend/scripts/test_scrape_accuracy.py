# =============================================
# HKTVmall 抓取成功率測試腳本
# =============================================
# 測試目標：驗證抓取邏輯的成功率，找出最佳配置
#
# 使用方法：
#   cd backend
#   python scripts/test_scrape_accuracy.py
#
# 注意：此腳本會消耗 Firecrawl credits

import os
import sys
import time
import asyncio
from decimal import Decimal
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime

# 添加項目根目錄到路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import get_settings
from app.connectors.hktv_scraper import HKTVScraper, HKTVUrlParser, HKTVProduct


# =============================================
# 測試配置
# =============================================

@dataclass
class TestConfig:
    """測試配置"""
    # 測試商品 URL（選擇不同類型的商品）
    # 這些是從項目中找到的實際 URL 格式
    test_urls: List[str] = field(default_factory=lambda: [
        # 即食麵（完整 URL 格式）
        "https://www.hktvmall.com/hktv/zh/main/%E8%B6%85%E5%B8%82%E7%99%BE%E8%B2%A8/%E9%A3%9F%E5%93%81%E9%A3%B2%E5%93%81/%E5%8D%B3%E9%A3%9F%E9%BA%B5%E7%8E%8B/p/H4455001_S_P00001",
        # 帶 Store Code 的商品
        "https://www.hktvmall.com/hktv/zh/p/H7917001_S_B1517001001",
        # 帶 SKU 後綴的商品
        "https://www.hktvmall.com/hktv/zh/p/H0340001_S_SK_WAGYU",
    ])

    # 最佳配置（經過優化）
    page_load_wait_ms: int = 10000      # 增加等待時間
    scroll_wait_ms: int = 3000           # 滾動後等待
    max_retries: int = 2                 # 重試次數
    retry_delay_seconds: float = 2.0     # 重試間隔


@dataclass
class FieldResult:
    """單個字段的測試結果"""
    field_name: str
    extracted: bool
    value: Any = None
    confidence: str = "low"  # low, medium, high


@dataclass
class ProductTestResult:
    """單個商品的測試結果"""
    url: str
    sku: str
    success: bool
    fields: List[FieldResult] = field(default_factory=list)
    error_message: Optional[str] = None
    duration_ms: int = 0
    retries_used: int = 0
    extraction_method: str = "unknown"  # json_mode, regex, hybrid


@dataclass
class TestReport:
    """測試報告"""
    total_urls: int = 0
    successful: int = 0
    failed: int = 0
    field_success_rates: Dict[str, float] = field(default_factory=dict)
    avg_duration_ms: float = 0
    total_credits_used: int = 0
    results: List[ProductTestResult] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.now)
    ended_at: Optional[datetime] = None


# =============================================
# 增強版抓取器（最高成功率配置）
# =============================================

class EnhancedHKTVScraper(HKTVScraper):
    """
    增強版 HKTVmall 抓取器

    優化點：
    1. 更長的等待時間
    2. 多次重試
    3. JSON Mode + 正則後備
    4. 詳細的字段驗證
    """

    def __init__(self, config: TestConfig = None):
        super().__init__()
        self.config = config or TestConfig()
        self.page_load_wait_ms = self.config.page_load_wait_ms
        self.scroll_wait_ms = self.config.scroll_wait_ms

    def scrape_product_with_retry(self, url: str) -> tuple[Dict[str, Any], int, str]:
        """
        帶重試的商品抓取

        Returns:
            (raw_data, retries_used, extraction_method)
        """
        last_error = None
        retries_used = 0

        for attempt in range(self.config.max_retries + 1):
            try:
                # 使用 JSON Mode 抓取
                raw_data = self.scrape_product_page(url)

                # 判斷提取方法
                if raw_data.get("json"):
                    extraction_method = "json_mode"
                else:
                    extraction_method = "regex"

                return raw_data, retries_used, extraction_method

            except Exception as e:
                last_error = e
                retries_used = attempt + 1

                if attempt < self.config.max_retries:
                    print(f"    重試 {attempt + 1}/{self.config.max_retries}...")
                    time.sleep(self.config.retry_delay_seconds)

        raise last_error

    def validate_product_data(self, product: HKTVProduct) -> List[FieldResult]:
        """
        驗證商品數據的完整性

        Returns:
            各字段的提取結果
        """
        results = []

        # 必要字段
        results.append(FieldResult(
            field_name="name",
            extracted=bool(product.name and product.name != "未知商品"),
            value=product.name,
            confidence="high" if product.name and len(product.name) > 5 else "low"
        ))

        results.append(FieldResult(
            field_name="price",
            extracted=product.price is not None,
            value=float(product.price) if product.price else None,
            confidence="high" if product.price and product.price > 0 else "low"
        ))

        results.append(FieldResult(
            field_name="sku",
            extracted=bool(product.sku and product.sku.startswith("H")),
            value=product.sku,
            confidence="high" if product.sku and len(product.sku) >= 8 else "medium"
        ))

        # 可選但重要的字段
        results.append(FieldResult(
            field_name="stock_status",
            extracted=product.stock_status is not None,
            value=product.stock_status,
            confidence="high" if product.stock_status in ["in_stock", "out_of_stock", "low_stock", "preorder"] else "medium"
        ))

        results.append(FieldResult(
            field_name="image_url",
            extracted=bool(product.image_url),
            value=product.image_url[:50] + "..." if product.image_url and len(product.image_url) > 50 else product.image_url,
            confidence="high" if product.image_url and product.image_url.startswith("http") else "low"
        ))

        results.append(FieldResult(
            field_name="brand",
            extracted=bool(product.brand),
            value=product.brand,
            confidence="medium" if product.brand else "low"
        ))

        results.append(FieldResult(
            field_name="original_price",
            extracted=product.original_price is not None,
            value=float(product.original_price) if product.original_price else None,
            confidence="high" if product.original_price and product.original_price > 0 else "low"
        ))

        results.append(FieldResult(
            field_name="store_name",
            extracted=bool(product.store_name),
            value=product.store_name,
            confidence="medium" if product.store_name else "low"
        ))

        return results


# =============================================
# 測試執行器
# =============================================

class AccuracyTester:
    """成功率測試執行器"""

    def __init__(self, config: TestConfig = None):
        self.config = config or TestConfig()
        self.scraper = EnhancedHKTVScraper(self.config)
        self.report = TestReport()

    def run_test(self, urls: List[str] = None) -> TestReport:
        """
        執行測試

        Args:
            urls: 要測試的 URL 列表（默認使用配置中的 URL）

        Returns:
            TestReport 測試報告
        """
        test_urls = urls or self.config.test_urls
        self.report = TestReport(total_urls=len(test_urls))
        self.report.started_at = datetime.now()

        print("\n" + "=" * 60)
        print("HKTVmall 抓取成功率測試")
        print("=" * 60)
        print(f"測試 URL 數量: {len(test_urls)}")
        print(f"等待時間: {self.config.page_load_wait_ms}ms")
        print(f"最大重試: {self.config.max_retries}")
        print("=" * 60 + "\n")

        for i, url in enumerate(test_urls, 1):
            print(f"[{i}/{len(test_urls)}] 測試: {url}")
            result = self._test_single_url(url)
            self.report.results.append(result)

            if result.success:
                self.report.successful += 1
                print(f"    [OK] Success ({result.extraction_method})")
            else:
                self.report.failed += 1
                print(f"    [FAIL] {result.error_message}")

            # 防止請求過快
            if i < len(test_urls):
                time.sleep(1)

        self.report.ended_at = datetime.now()
        self._calculate_statistics()

        return self.report

    def _test_single_url(self, url: str) -> ProductTestResult:
        """測試單個 URL"""
        start_time = time.time()
        sku = HKTVUrlParser.extract_sku(url) or "UNKNOWN"

        result = ProductTestResult(url=url, sku=sku, success=False)

        try:
            # 抓取
            raw_data, retries_used, extraction_method = self.scraper.scrape_product_with_retry(url)
            result.retries_used = retries_used
            result.extraction_method = extraction_method

            # 解析
            product = self.scraper.parse_product_data(url, raw_data)

            # 驗證
            result.fields = self.scraper.validate_product_data(product)

            # 判斷成功：至少要有名稱和價格
            name_ok = any(f.field_name == "name" and f.extracted for f in result.fields)
            price_ok = any(f.field_name == "price" and f.extracted for f in result.fields)

            result.success = name_ok and price_ok

            if not result.success:
                missing = []
                if not name_ok:
                    missing.append("name")
                if not price_ok:
                    missing.append("price")
                result.error_message = f"缺少必要字段: {', '.join(missing)}"

        except Exception as e:
            result.error_message = str(e)
            result.success = False

        result.duration_ms = int((time.time() - start_time) * 1000)
        return result

    def _calculate_statistics(self):
        """計算統計數據"""
        if not self.report.results:
            return

        # 平均耗時
        total_duration = sum(r.duration_ms for r in self.report.results)
        self.report.avg_duration_ms = total_duration / len(self.report.results)

        # 各字段成功率
        field_counts = {}
        field_success = {}

        for result in self.report.results:
            for field in result.fields:
                if field.field_name not in field_counts:
                    field_counts[field.field_name] = 0
                    field_success[field.field_name] = 0

                field_counts[field.field_name] += 1
                if field.extracted:
                    field_success[field.field_name] += 1

        for field_name in field_counts:
            if field_counts[field_name] > 0:
                rate = field_success[field_name] / field_counts[field_name] * 100
                self.report.field_success_rates[field_name] = round(rate, 1)

        # 估算 credits
        self.report.total_credits_used = len(self.report.results)

    def print_report(self):
        """打印測試報告"""
        r = self.report

        print("\n" + "=" * 60)
        print("測試報告")
        print("=" * 60)

        # 總體成功率
        success_rate = (r.successful / r.total_urls * 100) if r.total_urls > 0 else 0
        print(f"\n【總體成功率】")
        print(f"  成功: {r.successful}/{r.total_urls} ({success_rate:.1f}%)")
        print(f"  失敗: {r.failed}/{r.total_urls}")
        print(f"  平均耗時: {r.avg_duration_ms:.0f}ms")
        print(f"  Credits 消耗: {r.total_credits_used}")

        # 各字段成功率
        print(f"\n【字段提取成功率】")
        print("-" * 40)
        print(f"{'字段名':<15} {'成功率':>10}")
        print("-" * 40)

        # 按成功率排序
        sorted_fields = sorted(
            r.field_success_rates.items(),
            key=lambda x: x[1],
            reverse=True
        )

        for field_name, rate in sorted_fields:
            status = "[+]" if rate >= 80 else "[~]" if rate >= 50 else "[-]"
            print(f"{status} {field_name:<13} {rate:>8.1f}%")

        # 失敗詳情
        failed_results = [res for res in r.results if not res.success]
        if failed_results:
            print(f"\n【失敗詳情】")
            for res in failed_results:
                print(f"  - {res.sku}: {res.error_message}")

        # 成功詳情
        success_results = [res for res in r.results if res.success]
        if success_results:
            print(f"\n【成功詳情】")
            for res in success_results:
                print(f"  - {res.sku}:")
                for f in res.fields:
                    status = "[+]" if f.extracted else "[-]"
                    value_str = str(f.value)[:30] if f.value else "N/A"
                    print(f"      {status} {f.field_name}: {value_str}")

        print("\n" + "=" * 60)
        print(f"測試完成於: {r.ended_at}")
        print("=" * 60)


# =============================================
# 主程序
# =============================================

def main():
    """主程序"""
    # 檢查 API Key
    settings = get_settings()
    if not settings.firecrawl_api_key:
        print("錯誤: 未設定 FIRECRAWL_API_KEY")
        print("請在 .env 文件中設定 FIRECRAWL_API_KEY")
        sys.exit(1)

    # 解析命令行參數
    import argparse
    parser = argparse.ArgumentParser(description="HKTVmall 抓取成功率測試")
    parser.add_argument(
        "--urls",
        nargs="+",
        help="要測試的 URL 列表（默認使用內置測試 URL）"
    )
    parser.add_argument(
        "--wait",
        type=int,
        default=10000,
        help="頁面等待時間（毫秒，默認 10000）"
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=2,
        help="最大重試次數（默認 2）"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="只顯示將要測試的 URL，不實際執行"
    )

    args = parser.parse_args()

    # 創建配置
    config = TestConfig(
        page_load_wait_ms=args.wait,
        max_retries=args.retries,
    )

    if args.urls:
        config.test_urls = args.urls

    # Dry run
    if args.dry_run:
        print("\n將測試以下 URL:")
        for url in config.test_urls:
            print(f"  - {url}")
        print(f"\n配置:")
        print(f"  等待時間: {config.page_load_wait_ms}ms")
        print(f"  最大重試: {config.max_retries}")
        print(f"\n預計消耗 credits: {len(config.test_urls)}")
        return

    # 執行測試
    tester = AccuracyTester(config)
    tester.run_test()
    tester.print_report()


if __name__ == "__main__":
    main()
