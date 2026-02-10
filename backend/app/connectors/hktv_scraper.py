# =============================================
# HKTVmall 專用精準抓取器（優化版）
# =============================================
# 針對 HKTVmall JavaScript SPA 設計的專用抓取方案
# 解決：動態加載、Algolia 搜尋、商品識別等問題
# 優化：timeout 配置、智能等待、批量抓取

import re
import time
import hashlib
import asyncio
import logging
from typing import Optional, Dict, Any, List, Tuple
from decimal import Decimal, InvalidOperation
from dataclasses import dataclass, field
from datetime import datetime
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

from app.config import get_settings
from app.connectors.hktv_http_client import get_hktv_http_client, HKTVMetadata

logger = logging.getLogger(__name__)


# =============================================
# HKTVmall 優化配置常量
# =============================================

# 基於 Firecrawl 最佳實踐的配置
HKTV_CONFIG = {
    # 頁面加載配置
    "page_load_wait_ms": 10000,      # SPA 需要較長等待
    "scroll_wait_ms": 2000,           # 滾動後等待
    "max_scroll_count": 5,            # 最大滾動次數

    # 超時配置
    "timeout_ms": 60000,              # 60 秒超時

    # 重試配置
    "max_retries": 3,
    "retry_delay_seconds": 2.0,

    # TLS 配置
    "skip_tls_verification": True,    # HKTVmall 某些 CDN 需要

    # 請求間隔（避免速率限制）
    "request_delay_seconds": 1.0,
}


# =============================================
# 數據模型
# =============================================

@dataclass
class HKTVProduct:
    """HKTVmall 商品數據"""
    sku: str                                      # H0340001 格式
    name: str
    url: str
    price: Optional[Decimal] = None
    original_price: Optional[Decimal] = None
    discount_percent: Optional[Decimal] = None
    brand: Optional[str] = None
    store_name: Optional[str] = None              # 商店名稱
    store_code: Optional[str] = None              # B1517001 格式
    image_url: Optional[str] = None
    stock_status: Optional[str] = None
    rating: Optional[Decimal] = None
    review_count: Optional[int] = None
    category: Optional[str] = None
    weight: Optional[str] = None                  # 重量/規格
    origin: Optional[str] = None                  # 產地
    raw_data: Optional[Dict[str, Any]] = None
    scraped_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "sku": self.sku,
            "name": self.name,
            "url": self.url,
            "price": float(self.price) if self.price else None,
            "original_price": float(self.original_price) if self.original_price else None,
            "discount_percent": float(self.discount_percent) if self.discount_percent else None,
            "brand": self.brand,
            "store_name": self.store_name,
            "store_code": self.store_code,
            "image_url": self.image_url,
            "stock_status": self.stock_status,
            "rating": float(self.rating) if self.rating else None,
            "review_count": self.review_count,
            "category": self.category,
            "weight": self.weight,
            "origin": self.origin,
            "scraped_at": self.scraped_at.isoformat(),
        }


@dataclass
class ScrapeResult:
    """抓取結果"""
    success: bool
    products: List[HKTVProduct] = field(default_factory=list)
    total_found: int = 0
    total_scraped: int = 0
    failed_urls: List[str] = field(default_factory=list)
    error_message: Optional[str] = None
    duration_ms: int = 0
    credits_used: int = 0


# =============================================
# URL 工具
# =============================================

class HKTVUrlParser:
    """HKTVmall URL 解析器"""

    # HKTVmall URL 模式
    # SKU 格式：H0340001 或帶後綴如 H9423001_S_WNF-003A
    PRODUCT_URL_PATTERN = re.compile(
        r"hktvmall\.com.*?/p/(H\d{7,}[A-Za-z0-9_-]*)",
        re.IGNORECASE
    )
    STORE_URL_PATTERN = re.compile(
        r"hktvmall\.com.*?/s/(B\d{7,})",   # 商店頁: /s/B1517001
        re.IGNORECASE
    )
    CATEGORY_URL_PATTERN = re.compile(
        r"hktvmall\.com.*?/c/([A-Z0-9_]+)",  # 分類頁: /c/AA123
        re.IGNORECASE
    )
    SKU_PATTERN = re.compile(r"H\d{7,}[A-Za-z0-9_-]*")  # SKU 格式（含後綴）

    @classmethod
    def is_product_url(cls, url: str) -> bool:
        """判斷是否為商品頁面 URL"""
        return bool(cls.PRODUCT_URL_PATTERN.search(url))

    @classmethod
    def is_store_url(cls, url: str) -> bool:
        """判斷是否為商店頁面 URL"""
        return bool(cls.STORE_URL_PATTERN.search(url))

    @classmethod
    def extract_sku(cls, url: str) -> Optional[str]:
        """從 URL 提取 SKU"""
        match = cls.PRODUCT_URL_PATTERN.search(url)
        return match.group(1) if match else None

    @classmethod
    def extract_store_code(cls, url: str) -> Optional[str]:
        """從 URL 提取商店代碼"""
        match = cls.STORE_URL_PATTERN.search(url)
        return match.group(1) if match else None

    @classmethod
    def build_product_url(cls, sku: str) -> str:
        """構建商品頁面 URL"""
        sku = sku.upper()
        if not sku.startswith("H"):
            sku = f"H{sku}"
        return f"https://www.hktvmall.com/hktv/zh/p/{sku}"

    @classmethod
    def build_store_url(cls, store_code: str) -> str:
        """構建商店頁面 URL"""
        store_code = store_code.upper()
        if not store_code.startswith("B"):
            store_code = f"B{store_code}"
        return f"https://www.hktvmall.com/hktv/zh/main/store/s/{store_code}"

    @classmethod
    def normalize_url(cls, url: str) -> str:
        """標準化 URL（移除追蹤參數）"""
        parsed = urlparse(url)
        # 只保留必要的查詢參數
        query = parse_qs(parsed.query)
        essential_params = {k: v for k, v in query.items() if k in ["page", "sort"]}
        new_query = urlencode(essential_params, doseq=True)
        return urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            new_query,
            ""  # 移除 fragment
        ))

    @classmethod
    def validate_product_urls(cls, urls: List[str]) -> List[str]:
        """
        驗證並過濾商品 URL

        只保留格式正確的商品頁面 URL
        """
        valid_urls = []
        for url in urls:
            if cls.is_product_url(url):
                normalized = cls.normalize_url(url)
                if normalized not in valid_urls:
                    valid_urls.append(normalized)
        return valid_urls


# =============================================
# HKTVmall 專用抓取器
# =============================================

class HKTVScraper:
    """
    HKTVmall 專用抓取器（優化版）

    設計原則：
    1. 針對 JavaScript SPA 優化
    2. 使用 Actions 等待頁面渲染
    3. 嚴格驗證商品 URL 格式
    4. 精準提取商品數據

    優化：
    - 正確傳遞 timeout 到 Firecrawl API
    - 使用 skipTlsVerification 處理 CDN
    - 智能重試和錯誤處理
    """

    def __init__(self):
        settings = get_settings()
        self.api_key = settings.firecrawl_api_key
        self._app = None
        self.url_parser = HKTVUrlParser()

        # 從全局配置加載（便於統一調整）
        self.page_load_wait_ms = HKTV_CONFIG["page_load_wait_ms"]
        self.scroll_wait_ms = HKTV_CONFIG["scroll_wait_ms"]
        self.max_scroll_count = HKTV_CONFIG["max_scroll_count"]
        self.request_timeout_ms = HKTV_CONFIG["timeout_ms"]
        self.skip_tls_verification = HKTV_CONFIG["skip_tls_verification"]
        self.request_delay_seconds = HKTV_CONFIG["request_delay_seconds"]

    @property
    def app(self):
        """延遲初始化 Firecrawl App"""
        if self._app is None:
            if not self.api_key:
                raise ValueError("Firecrawl API Key 未設定")
            from firecrawl import FirecrawlApp
            self._app = FirecrawlApp(api_key=self.api_key)
        return self._app

    # =============================================
    # 核心抓取方法
    # =============================================

    def scrape_with_js_render(
        self,
        url: str,
        wait_ms: int = None,
        scroll_count: int = None
    ) -> Dict[str, Any]:
        """
        使用 JavaScript 渲染抓取頁面（優化版）

        Args:
            url: 要抓取的 URL
            wait_ms: 等待時間（毫秒）
            scroll_count: 滾動次數

        Returns:
            包含 markdown, html 的結果字典
        """
        wait_ms = wait_ms or self.page_load_wait_ms
        scroll_count = scroll_count or self.max_scroll_count

        # 構建 Actions：等待 + 多次滾動
        actions = [
            {"type": "wait", "milliseconds": wait_ms},
        ]

        # 添加滾動動作以觸發懶加載
        for i in range(scroll_count):
            actions.extend([
                {"type": "scroll", "direction": "down", "amount": 800},
                {"type": "wait", "milliseconds": self.scroll_wait_ms},
            ])

        # 最後滾動回頂部
        actions.append({"type": "scroll", "direction": "up", "amount": 99999})

        # 構建參數（包含 timeout 和 skipTlsVerification）
        scrape_kwargs = {
            "formats": ["markdown", "html"],
            "only_main_content": False,  # 獲取完整頁面
            "actions": actions,
            "timeout": self.request_timeout_ms,  # 正確傳遞 timeout
        }

        # 添加 TLS 跳過（HKTVmall CDN 需要）
        if self.skip_tls_verification:
            scrape_kwargs["skip_tls_verification"] = True

        logger.debug(f"Scraping with JS render: {url}, timeout={self.request_timeout_ms}ms")

        result = self.app.scrape(url, **scrape_kwargs)

        return self._document_to_dict(result)

    def scrape_product_page(self, url: str) -> Dict[str, Any]:
        """
        抓取單個商品頁面（優化版）

        使用 JSON Mode 結構化提取商品數據
        """
        from pydantic import BaseModel

        class HKTVProductSchema(BaseModel):
            """HKTVmall 商品提取 Schema"""
            product_name: Optional[str] = None
            current_price: Optional[float] = None
            original_price: Optional[float] = None
            discount_percent: Optional[float] = None
            currency: Optional[str] = None
            stock_status: Optional[str] = None
            rating: Optional[float] = None
            review_count: Optional[int] = None
            sku: Optional[str] = None
            brand: Optional[str] = None
            store_name: Optional[str] = None
            category: Optional[str] = None
            description: Optional[str] = None
            weight_or_spec: Optional[str] = None
            origin_country: Optional[str] = None
            image_url: Optional[str] = None
            promotion_text: Optional[str] = None

        # 構建參數（包含優化配置）
        scrape_kwargs = {
            "formats": [
                {
                    "type": "json",
                    "schema": HKTVProductSchema.model_json_schema(),
                },
                "markdown",
                "html"
            ],
            "only_main_content": True,
            "wait_for": 8000,             # 商品頁等待 8 秒（SPA 需要更長）
            "timeout": self.request_timeout_ms,
        }

        if self.skip_tls_verification:
            scrape_kwargs["skip_tls_verification"] = True

        logger.debug(f"Scraping product page: {url}")

        result = self.app.scrape(url, **scrape_kwargs)

        return self._document_to_dict(result)

    def _document_to_dict(self, doc) -> Dict[str, Any]:
        """將 Firecrawl Document 對象轉換為 dict"""
        result = {}

        if hasattr(doc, 'markdown') and doc.markdown:
            result['markdown'] = doc.markdown
        if hasattr(doc, 'html') and doc.html:
            result['html'] = doc.html
        if hasattr(doc, 'json') and doc.json:
            result['json'] = doc.json
        if hasattr(doc, 'metadata') and doc.metadata:
            result['metadata'] = {
                'title': getattr(doc.metadata, 'title', None),
                'ogImage': getattr(doc.metadata, 'og_image', None),
                'description': getattr(doc.metadata, 'description', None),
            }

        return result

    # =============================================
    # 商品 URL 發現
    # =============================================

    def discover_product_urls_from_store(
        self,
        store_url: str,
        max_products: int = 50
    ) -> List[str]:
        """
        從商店頁面發現商品 URL

        使用 JS 渲染後提取所有商品連結

        Args:
            store_url: 商店頁面 URL
            max_products: 最大商品數

        Returns:
            商品 URL 列表
        """
        all_urls = set()

        # 第一步：抓取主頁面（等待 JS 渲染）
        try:
            raw_data = self.scrape_with_js_render(
                store_url,
                wait_ms=10000,    # 商店頁需要更長等待
                scroll_count=8    # 更多滾動以加載更多商品
            )
            html = raw_data.get("html", "")

            # 提取商品 URL
            page_urls = self._extract_product_urls_from_html(html)
            all_urls.update(page_urls)

        except Exception as e:
            logger.error(f"抓取商店頁面失敗: {e}", exc_info=True)

        # 第二步：嘗試分頁
        if len(all_urls) < max_products:
            base_url = store_url.split("?")[0]

            for page in range(2, 6):  # 嘗試第 2-5 頁
                if len(all_urls) >= max_products:
                    break

                try:
                    page_url = f"{base_url}?page={page}"
                    raw_data = self.scrape_with_js_render(
                        page_url,
                        wait_ms=8000,
                        scroll_count=5
                    )
                    html = raw_data.get("html", "")
                    page_urls = self._extract_product_urls_from_html(html)

                    if not page_urls:
                        break  # 沒有更多商品

                    all_urls.update(page_urls)

                except Exception as e:
                    logger.warning(f"抓取分頁 {page} 失敗: {e}")
                    break

        # 驗證並返回
        valid_urls = HKTVUrlParser.validate_product_urls(list(all_urls))
        return valid_urls[:max_products]

    def _extract_product_urls_from_html(self, html: str) -> List[str]:
        """
        從渲染後的 HTML 中提取商品 URL

        關鍵：只提取 /p/H{sku} 格式的商品頁面連結
        """
        product_urls = set()

        # HKTVmall 商品連結模式（支持帶後綴 SKU 如 H9423001_S_WNF-003A）
        _sku = r'H\d{7,}[A-Za-z0-9_-]*'
        patterns = [
            # 標準商品頁連結
            rf'href="([^"]*?/p/{_sku}[^"]*)"',
            rf"href='([^']*?/p/{_sku}[^']*)'",

            # data 屬性中的連結
            rf'data-href="([^"]*?/p/{_sku}[^"]*)"',
            rf'data-url="([^"]*?/p/{_sku}[^"]*)"',

            # JavaScript 中的連結
            rf'"url":\s*"([^"]*?/p/{_sku}[^"]*)"',
            rf"'url':\s*'([^']*?/p/{_sku}[^']*)'",

            # onclick 中的連結
            rf'onclick="[^"]*(/p/{_sku})[^"]*"',

            # 直接的完整 URL
            rf'(https?://[^"\s]*hktvmall\.com[^"\s]*/p/{_sku}[^"\s]*)',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            for match in matches:
                url = self._normalize_product_url(match)
                if url:
                    product_urls.add(url)

        return list(product_urls)

    def _normalize_product_url(self, url: str) -> Optional[str]:
        """標準化商品 URL"""
        if not url:
            return None

        # 補全相對路徑
        if url.startswith("/"):
            url = f"https://www.hktvmall.com{url}"
        elif not url.startswith("http"):
            url = f"https://www.hktvmall.com{url}"

        # 驗證是商品 URL
        if not HKTVUrlParser.is_product_url(url):
            return None

        # 標準化
        return HKTVUrlParser.normalize_url(url)

    # =============================================
    # 商品信息解析
    # =============================================

    def parse_product_data(
        self,
        url: str,
        raw_data: Dict[str, Any]
    ) -> HKTVProduct:
        """
        解析商品數據

        優先使用 JSON Mode 結果，失敗則使用正則提取
        """
        sku = HKTVUrlParser.extract_sku(url) or "UNKNOWN"

        # 嘗試從 JSON Mode 結果解析
        json_data = raw_data.get("json", {})
        if json_data:
            return self._parse_from_json(sku, url, json_data, raw_data)

        # 後備：從 markdown/html 解析
        return self._parse_from_content(sku, url, raw_data)

    def _parse_from_json(
        self,
        sku: str,
        url: str,
        json_data: Dict[str, Any],
        raw_data: Dict[str, Any]
    ) -> HKTVProduct:
        """從 JSON Mode 結果解析商品"""
        # 處理價格
        price = None
        original_price = None

        if json_data.get("current_price"):
            try:
                price = Decimal(str(json_data["current_price"]))
            except (ValueError, TypeError, InvalidOperation) as e:
                logger.debug(f"無法解析 current_price: {json_data.get('current_price')}, 錯誤: {e}")

        if json_data.get("original_price"):
            try:
                original_price = Decimal(str(json_data["original_price"]))
            except (ValueError, TypeError, InvalidOperation) as e:
                logger.debug(f"無法解析 original_price: {json_data.get('original_price')}, 錯誤: {e}")

        # 計算折扣
        discount_percent = None
        if price and original_price and original_price > price:
            discount_percent = round((1 - price / original_price) * 100, 2)

        # 標準化庫存狀態
        stock_status = self._normalize_stock_status(json_data.get("stock_status"))

        # 處理評分
        rating = None
        if json_data.get("rating"):
            try:
                rating = Decimal(str(json_data["rating"]))
            except (ValueError, TypeError, InvalidOperation) as e:
                logger.debug(f"無法解析 rating: {json_data.get('rating')}, 錯誤: {e}")

        # 獲取圖片
        image_url = json_data.get("image_url")
        if not image_url:
            metadata = raw_data.get("metadata", {})
            image_url = metadata.get("ogImage")

        return HKTVProduct(
            sku=sku,
            name=json_data.get("product_name") or "未知商品",
            url=url,
            price=price,
            original_price=original_price,
            discount_percent=discount_percent,
            brand=json_data.get("brand"),
            store_name=json_data.get("store_name"),
            image_url=image_url,
            stock_status=stock_status,
            rating=rating,
            review_count=json_data.get("review_count"),
            category=json_data.get("category"),
            weight=json_data.get("weight_or_spec"),
            origin=json_data.get("origin_country"),
            raw_data=raw_data,
        )

    def _parse_from_content(
        self,
        sku: str,
        url: str,
        raw_data: Dict[str, Any]
    ) -> HKTVProduct:
        """從 markdown/html 內容解析商品（後備方案）"""
        markdown = raw_data.get("markdown", "")
        html = raw_data.get("html", "")
        content = markdown + html

        # 提取名稱
        name = self._extract_name(markdown, html)

        # 提取價格
        price, original_price = self._extract_prices(content)

        # 計算折扣
        discount_percent = None
        if price and original_price and original_price > price:
            discount_percent = round((1 - price / original_price) * 100, 2)

        # 提取庫存狀態
        stock_status = self._extract_stock_status(content)

        # 提取品牌
        brand = self._extract_brand(content)

        # 提取圖片
        image_url = None
        metadata = raw_data.get("metadata", {})
        if metadata.get("ogImage"):
            image_url = metadata["ogImage"]

        return HKTVProduct(
            sku=sku,
            name=name or "未知商品",
            url=url,
            price=price,
            original_price=original_price,
            discount_percent=discount_percent,
            brand=brand,
            image_url=image_url,
            stock_status=stock_status,
            raw_data=raw_data,
        )

    def _extract_name(self, markdown: str, html: str) -> Optional[str]:
        """提取商品名稱"""
        # 從 markdown 標題
        match = re.search(r"^#\s+(.+)$", markdown, re.MULTILINE)
        if match:
            title = match.group(1).strip()
            # 過濾掉非商品名稱
            if len(title) > 5 and not any(kw in title.lower() for kw in ["hktvmall", "error", "loading"]):
                return title

        # 從 HTML title
        match = re.search(r"<title>([^<]+)</title>", html, re.IGNORECASE)
        if match:
            title = match.group(1).strip()
            # 移除 "| HKTVmall" 後綴
            title = re.sub(r"\s*\|\s*HKTVmall.*$", "", title)
            if len(title) > 3:
                return title

        # 從 og:title
        match = re.search(r'property="og:title"\s+content="([^"]+)"', html, re.IGNORECASE)
        if match:
            return match.group(1).strip()

        return None

    def _extract_prices(self, content: str) -> Tuple[Optional[Decimal], Optional[Decimal]]:
        """提取價格"""
        # HKTVmall 價格模式
        patterns = [
            r"HK\$\s*([\d,]+(?:\.\d{1,2})?)",
            r"\$\s*([\d,]+(?:\.\d{1,2})?)",
            r"([\d,]+(?:\.\d{1,2})?)\s*(?:HKD|港幣)",
        ]

        prices = []
        for pattern in patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                try:
                    price = Decimal(match.replace(",", ""))
                    # 過濾不合理的價格
                    if Decimal("1") <= price <= Decimal("100000"):
                        prices.append(price)
                except (ValueError, TypeError, InvalidOperation):
                    # 無法解析的價格字符串，跳過
                    pass

        if not prices:
            return None, None

        prices = sorted(set(prices))
        current_price = prices[0]
        original_price = prices[-1] if len(prices) > 1 and prices[-1] > prices[0] else None

        return current_price, original_price

    def _extract_stock_status(self, content: str) -> Optional[str]:
        """提取庫存狀態"""
        content_lower = content.lower()

        if any(kw in content_lower for kw in ["out of stock", "缺貨", "售罄", "暫時缺貨", "sold out"]):
            return "out_of_stock"
        elif any(kw in content_lower for kw in ["low stock", "庫存緊張", "只剩", "limited"]):
            return "low_stock"
        elif any(kw in content_lower for kw in ["pre-order", "預購", "預訂"]):
            return "preorder"
        elif any(kw in content_lower for kw in ["in stock", "有貨", "現貨", "available", "加入購物車"]):
            return "in_stock"

        return None

    def _extract_brand(self, content: str) -> Optional[str]:
        """提取品牌"""
        patterns = [
            r"品牌[：:]\s*([^\n<]+)",
            r"Brand[：:]\s*([^\n<]+)",
            r'"brand":\s*"([^"]+)"',
        ]

        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                brand = match.group(1).strip()
                if 2 <= len(brand) <= 50:
                    return brand

        return None

    def _normalize_stock_status(self, status: Optional[str]) -> Optional[str]:
        """標準化庫存狀態"""
        if not status:
            return None

        status_lower = status.lower()

        if any(kw in status_lower for kw in ["out", "缺", "售罄", "sold"]):
            return "out_of_stock"
        elif any(kw in status_lower for kw in ["low", "緊張", "limited"]):
            return "low_stock"
        elif any(kw in status_lower for kw in ["pre", "預"]):
            return "preorder"
        elif any(kw in status_lower for kw in ["in", "有", "現", "available"]):
            return "in_stock"

        return status

    # =============================================
    # 價格專用抓取（省 credit）
    # =============================================

    def scrape_price_only(self, url: str) -> Dict[str, Any]:
        """
        最小化 Firecrawl 消耗：只提取價格和庫存

        相比 scrape_product_page 的完整 schema：
        - schema 只含 price + stock（減少 LLM 提取時間）
        - wait_for: 5000ms（vs 8000ms，省 37.5% 等待）
        - only_main_content: True（減少 HTML 傳輸）
        - 不滾動頁面

        Returns:
            {"current_price": ..., "original_price": ..., "stock_status": ...}
        """
        from pydantic import BaseModel

        class PriceOnlySchema(BaseModel):
            """精簡 schema：只取價格"""
            current_price: Optional[float] = None
            original_price: Optional[float] = None
            stock_status: Optional[str] = None

        settings = get_settings()

        scrape_kwargs = {
            "formats": [
                {
                    "type": "json",
                    "schema": PriceOnlySchema.model_json_schema(),
                },
            ],
            "only_main_content": True,
            "wait_for": settings.hktv_price_only_wait_ms,
            "timeout": self.request_timeout_ms,
        }

        if self.skip_tls_verification:
            scrape_kwargs["skip_tls_verification"] = True

        logger.debug(f"Price-only scrape: {url}")

        result = self.app.scrape(url, **scrape_kwargs)

        # 從 Document 中提取 json 數據
        json_data = {}
        if hasattr(result, 'json') and result.json:
            json_data = result.json

        return {
            "current_price": json_data.get("current_price"),
            "original_price": json_data.get("original_price"),
            "stock_status": self._normalize_stock_status(json_data.get("stock_status")),
        }

    async def smart_scrape_product(
        self,
        url: str,
        need_price: bool = True
    ) -> HKTVProduct:
        """
        智能抓取：HTTP 優先，Firecrawl 按需

        策略：
        1. HTTP 取 metadata（0 credits）— 名稱、品牌、圖片
        2. 如果需要價格，用 Firecrawl price-only 模式（1 credit）
        3. 合併結果

        Args:
            url: HKTVmall 商品 URL
            need_price: 是否需要價格數據（需要 JS 渲染 = 1 credit）

        Returns:
            HKTVProduct 完整商品數據
        """
        sku = HKTVUrlParser.extract_sku(url) or "UNKNOWN"

        # 第一層：HTTP 元數據（0 credits）
        http_client = get_hktv_http_client()
        metadata = await http_client.fetch_product_metadata(url)

        price = None
        original_price = None
        discount_percent = None
        stock_status = None

        # 第二層：需要價格時用 Firecrawl（1 credit）
        # 注意：Firecrawl SDK 是同步的，用 asyncio.to_thread 避免阻塞事件循環
        if need_price:
            try:
                price_data = await asyncio.to_thread(self.scrape_price_only, url)

                if price_data.get("current_price"):
                    price = Decimal(str(price_data["current_price"]))
                if price_data.get("original_price"):
                    original_price = Decimal(str(price_data["original_price"]))
                if price and original_price and original_price > price:
                    discount_percent = round((1 - price / original_price) * 100, 2)
                stock_status = price_data.get("stock_status")

            except Exception as e:
                logger.warning(f"Price-only scrape 失敗，回退到完整 scrape: {url} - {e}")
                try:
                    raw_data = await asyncio.to_thread(self.scrape_product_page, url)
                    return self.parse_product_data(url, raw_data)
                except Exception as e2:
                    logger.error(f"完整 scrape 也失敗: {url} - {e2}")

        return HKTVProduct(
            sku=sku,
            name=metadata.name or "未知商品",
            url=url,
            price=price,
            original_price=original_price,
            discount_percent=discount_percent,
            brand=metadata.brand,
            image_url=metadata.image_url,
            stock_status=stock_status,
        )

    # =============================================
    # 高級抓取方法
    # =============================================

    async def scrape_store_products(
        self,
        store_url: str,
        max_products: int = 50,
        scrape_details: bool = True
    ) -> ScrapeResult:
        """
        抓取商店的所有商品

        Args:
            store_url: 商店頁面 URL
            max_products: 最大商品數
            scrape_details: 是否抓取商品詳情

        Returns:
            ScrapeResult 抓取結果
        """
        start_time = time.time()
        credits_used = 0

        # 第一步：發現商品 URL
        try:
            product_urls = self.discover_product_urls_from_store(store_url, max_products)
            credits_used += 1 + (len(product_urls) // 50)  # 估算 credits
        except Exception as e:
            return ScrapeResult(
                success=False,
                error_message=f"發現商品 URL 失敗: {str(e)}",
                duration_ms=int((time.time() - start_time) * 1000),
                credits_used=credits_used,
            )

        if not product_urls:
            return ScrapeResult(
                success=False,
                error_message="未發現任何商品 URL",
                duration_ms=int((time.time() - start_time) * 1000),
                credits_used=credits_used,
            )

        # 第二步：抓取商品詳情
        products = []
        failed_urls = []

        if scrape_details:
            for url in product_urls:
                try:
                    raw_data = self.scrape_product_page(url)
                    product = self.parse_product_data(url, raw_data)
                    products.append(product)
                    credits_used += 1

                except Exception as e:
                    failed_urls.append(url)
                    logger.warning(f"抓取商品失敗 {url}: {e}")

                # 防止過快請求（使用配置的延遲）
                await asyncio.sleep(self.request_delay_seconds)
        else:
            # 不抓取詳情，只返回 URL
            for url in product_urls:
                sku = HKTVUrlParser.extract_sku(url) or "UNKNOWN"
                products.append(HKTVProduct(
                    sku=sku,
                    name=f"商品 {sku}",
                    url=url,
                ))

        return ScrapeResult(
            success=True,
            products=products,
            total_found=len(product_urls),
            total_scraped=len(products),
            failed_urls=failed_urls,
            duration_ms=int((time.time() - start_time) * 1000),
            credits_used=credits_used,
        )

    async def scrape_single_product(self, product_url: str) -> ScrapeResult:
        """
        抓取單個商品

        Args:
            product_url: 商品頁面 URL

        Returns:
            ScrapeResult 抓取結果
        """
        start_time = time.time()

        # 驗證 URL
        if not HKTVUrlParser.is_product_url(product_url):
            return ScrapeResult(
                success=False,
                error_message=f"無效的商品 URL: {product_url}",
                duration_ms=int((time.time() - start_time) * 1000),
            )

        try:
            raw_data = self.scrape_product_page(product_url)
            product = self.parse_product_data(product_url, raw_data)

            return ScrapeResult(
                success=True,
                products=[product],
                total_found=1,
                total_scraped=1,
                duration_ms=int((time.time() - start_time) * 1000),
                credits_used=1,
            )

        except Exception as e:
            return ScrapeResult(
                success=False,
                error_message=str(e),
                failed_urls=[product_url],
                duration_ms=int((time.time() - start_time) * 1000),
                credits_used=1,
            )


# =============================================
# 單例工廠
# =============================================

_scraper: Optional[HKTVScraper] = None


def get_hktv_scraper() -> HKTVScraper:
    """獲取 HKTVScraper 單例"""
    global _scraper
    if _scraper is None:
        _scraper = HKTVScraper()
    return _scraper
