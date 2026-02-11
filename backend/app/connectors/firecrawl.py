# =============================================
# Firecrawl 爬蟲連接器（優化版）
# =============================================
# 使用 JSON Mode 結構化提取、Map 發現 URL、Actions 處理動態頁面
# 優化：timeout、skipTlsVerification、headers、mobile、batch 支持

import re
import logging
import asyncio
from typing import Optional, Dict, Any, List, Callable
from decimal import Decimal, InvalidOperation
from dataclasses import dataclass, field
from pydantic import BaseModel
from enum import Enum

from app.config import get_settings

logger = logging.getLogger(__name__)


# =============================================
# 抓取配置
# =============================================

class ScrapeMode(Enum):
    """抓取模式"""
    FAST = "fast"           # 快速模式：較短等待時間
    STANDARD = "standard"   # 標準模式：平衡速度和成功率
    THOROUGH = "thorough"   # 徹底模式：較長等待時間，適合 SPA


@dataclass
class ScrapeOptions:
    """抓取選項（對應 Firecrawl API 參數）"""
    # 等待配置
    wait_for: int = 3000                    # 等待時間（毫秒）
    wait_for_selector: Optional[str] = None  # 等待特定元素出現

    # 超時配置
    timeout: int = 30000                     # 請求超時（毫秒）

    # TLS 配置
    skip_tls_verification: bool = False      # 跳過 TLS 驗證

    # 設備模擬
    mobile: bool = False                     # 模擬手機

    # 請求頭
    headers: Optional[Dict[str, str]] = None

    # 緩存配置
    max_age: Optional[int] = None            # 緩存最大年齡（毫秒）

    # 內容配置
    only_main_content: bool = True           # 只提取主要內容
    include_tags: Optional[List[str]] = None
    exclude_tags: Optional[List[str]] = None

    @classmethod
    def for_hktvmall(cls) -> "ScrapeOptions":
        """HKTVmall 優化配置"""
        return cls(
            wait_for=8000,
            timeout=60000,
            skip_tls_verification=True,
            only_main_content=False,  # HKTVmall 需要完整頁面
        )

    @classmethod
    def for_google(cls) -> "ScrapeOptions":
        """Google SERP 配置"""
        return cls(
            wait_for=5000,
            timeout=30000,
            headers={
                "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8"
            }
        )

    @classmethod
    def for_mode(cls, mode: ScrapeMode) -> "ScrapeOptions":
        """根據模式創建配置"""
        if mode == ScrapeMode.FAST:
            return cls(wait_for=2000, timeout=20000)
        elif mode == ScrapeMode.THOROUGH:
            return cls(wait_for=10000, timeout=60000)
        else:
            return cls()  # STANDARD


# =============================================
# 數據模型
# =============================================

@dataclass
class ProductInfo:
    """爬取的商品資訊"""
    name: str
    price: Optional[Decimal] = None
    original_price: Optional[Decimal] = None
    discount_percent: Optional[Decimal] = None
    stock_status: Optional[str] = None
    rating: Optional[Decimal] = None
    review_count: Optional[int] = None
    image_url: Optional[str] = None
    description: Optional[str] = None
    sku: Optional[str] = None
    category: Optional[str] = None
    promotion_text: Optional[str] = None
    brand: Optional[str] = None
    raw_data: Optional[Dict[str, Any]] = None


@dataclass
class MapResult:
    """URL 發現結果"""
    urls: List[str] = field(default_factory=list)
    total: int = 0


class ProductSchema(BaseModel):
    """商品提取 Schema（用於 Firecrawl JSON Mode）"""
    product_name: Optional[str] = None
    current_price: Optional[float] = None
    original_price: Optional[float] = None
    currency: Optional[str] = None
    stock_status: Optional[str] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    sku: Optional[str] = None
    brand: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    promotion_text: Optional[str] = None
    image_url: Optional[str] = None


# =============================================
# Firecrawl 連接器
# =============================================

class FirecrawlConnector:
    """Firecrawl 爬蟲連接器"""

    def __init__(self):
        settings = get_settings()
        self.api_key = settings.firecrawl_api_key
        self._app = None

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

    def scrape_url(
        self,
        url: str,
        use_json_mode: bool = False,
        options: Optional[ScrapeOptions] = None,
        wait_for: Optional[int] = None  # 向後兼容
    ) -> Dict[str, Any]:
        """
        爬取單個 URL（優化版）

        Args:
            url: 要爬取的 URL
            use_json_mode: 是否使用 JSON Mode 結構化提取
            options: 抓取選項（推薦使用）
            wait_for: 等待頁面載入時間（向後兼容，優先使用 options）

        Returns:
            Firecrawl 返回的原始數據（轉換為 dict 格式）
        """
        # 使用選項或創建默認
        opts = options or ScrapeOptions()
        if wait_for is not None:
            opts.wait_for = wait_for

        # SDK v4.x 使用直接參數而非 params dict
        formats = ["markdown", "html"]

        # 使用 JSON Mode 結構化提取商品數據
        if use_json_mode:
            formats = [
                {
                    "type": "json",
                    "schema": ProductSchema.model_json_schema(),
                },
                "markdown",
                "html"
            ]

        # 構建 scrape 參數
        scrape_kwargs = {
            "formats": formats,
            "only_main_content": opts.only_main_content,
            "wait_for": opts.wait_for,
            "timeout": opts.timeout,
        }

        # 可選參數（只有設置時才傳遞）
        if opts.skip_tls_verification:
            scrape_kwargs["skip_tls_verification"] = True
        if opts.mobile:
            scrape_kwargs["mobile"] = True
        if opts.headers:
            scrape_kwargs["headers"] = opts.headers
        if opts.max_age is not None:
            scrape_kwargs["max_age"] = opts.max_age
        if opts.include_tags:
            scrape_kwargs["include_tags"] = opts.include_tags
        if opts.exclude_tags:
            scrape_kwargs["exclude_tags"] = opts.exclude_tags

        logger.debug(f"Scraping URL: {url} with options: timeout={opts.timeout}ms, wait_for={opts.wait_for}ms")

        result = self.app.scrape(url, **scrape_kwargs)

        # 將 Document 對象轉換為 dict
        return self._document_to_dict(result)

    def scrape_with_actions(
        self,
        url: str,
        actions: List[Dict[str, Any]],
        take_screenshot: bool = False,
        options: Optional[ScrapeOptions] = None
    ) -> Dict[str, Any]:
        """
        使用 Actions 爬取動態頁面（優化版）

        Args:
            url: 要爬取的 URL
            actions: 動作列表（click, scroll, wait 等）
            take_screenshot: 是否截圖
            options: 抓取選項

        Returns:
            Firecrawl 返回的數據
        """
        opts = options or ScrapeOptions()

        action_list = list(actions)
        if take_screenshot:
            action_list.append({"type": "screenshot", "fullPage": True})

        # 構建參數
        scrape_kwargs = {
            "formats": ["markdown", "html"],
            "only_main_content": opts.only_main_content,
            "actions": action_list,
            "timeout": opts.timeout,
        }

        if opts.skip_tls_verification:
            scrape_kwargs["skip_tls_verification"] = True
        if opts.mobile:
            scrape_kwargs["mobile"] = True
        if opts.headers:
            scrape_kwargs["headers"] = opts.headers

        logger.debug(f"Scraping URL with actions: {url}, {len(action_list)} actions")

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
    # URL 發現
    # =============================================

    def map_urls(self, url: str, search: Optional[str] = None, limit: int = 100) -> MapResult:
        """
        發現網站上的所有 URL（極快）

        Args:
            url: 網站根 URL
            search: 可選的搜索過濾詞
            limit: 最大返回數量

        Returns:
            MapResult 包含發現的 URL 列表
        """
        try:
            # SDK v4.x 使用直接參數
            result = self.app.map(url, search=search, limit=limit)

            # MapData 對象的 links 可能是字串列表或 Link 對象列表
            links = result.links if hasattr(result, 'links') and result.links else []

            # 提取 URL 字串
            urls = []
            for link in links:
                if isinstance(link, str):
                    urls.append(link)
                elif hasattr(link, 'url'):
                    urls.append(link.url)
                else:
                    urls.append(str(link))

            return MapResult(urls=urls, total=len(urls))

        except Exception as e:
            # Map 功能可能不可用，返回空結果
            return MapResult(urls=[], total=0)

    def discover_product_urls(self, base_url: str, keywords: List[str] = None) -> List[str]:
        """
        發現網站上的商品頁面 URL（增強版）

        Args:
            base_url: 網站根 URL
            keywords: 過濾關鍵詞（如 ["product", "item", "goods"]）

        Returns:
            商品頁面 URL 列表
        """
        if keywords is None:
            keywords = ["product", "item", "goods", "商品", "p/", "pd/"]

        all_urls = set()

        # =============================================
        # 策略 1: 使用 map 發現所有 URL
        # =============================================
        result = self.map_urls(base_url, limit=500)

        # 過濾出可能是商品頁面的 URL
        for url in result.urls:
            url_lower = url.lower()
            if any(kw in url_lower for kw in keywords):
                all_urls.add(url)

        # =============================================
        # 策略 2: HKTVmall 特定 URL 模式識別
        # =============================================
        # HKTVmall 商品 URL 模式:
        # - /hktv/zh/p/H[number] - 產品頁面
        # - 包含 H[number] 格式的 SKU
        hktv_product_patterns = [
            r"hktvmall\.com.*?/p/H\d+",      # 標準產品頁 /p/H12345678
            r"hktvmall\.com.*?/main/.*?H\d+", # 類別頁中的產品連結
            r"hktvmall\.com.*?H\d{6,}",       # 任何包含 SKU 格式的連結
        ]

        for url in result.urls:
            for pattern in hktv_product_patterns:
                if re.search(pattern, url, re.IGNORECASE):
                    all_urls.add(url)
                    break

        # =============================================
        # 策略 3: 從頁面 HTML 中提取更多連結
        # =============================================
        if len(all_urls) < 10:
            try:
                extra_urls = self._extract_product_links_from_page(base_url)
                all_urls.update(extra_urls)
            except Exception:
                pass

        return list(all_urls)

    def _extract_product_links_from_page(self, url: str) -> List[str]:
        """
        從頁面 HTML 中提取商品連結

        Args:
            url: 頁面 URL

        Returns:
            商品連結列表
        """
        try:
            raw_data = self.scrape_url(url, use_json_mode=False, wait_for=5000)
            html = raw_data.get("html", "")

            product_urls = set()

            # HKTVmall 商品連結模式（放寬版：支持所有字母開頭）
            # 標準產品頁: /hktv/zh/p/H12345678, /p/B12345678 等
            patterns = [
                r'href="([^"]*?/p/[A-Z]\d+[^"]*)"',           # /p/H12345, /p/B12345 等
                r'href="([^"]*hktvmall\.com[^"]*[A-Z]\d{6,}[^"]*)"',  # 完整 URL
                r'data-href="([^"]*?/p/[A-Z]\d+[^"]*)"',      # data-href 屬性
                r'onclick="[^"]*(/p/[A-Z]\d+)[^"]*"',         # onclick 中的連結
                r'href="([^"]*?/product/[^"]*)"',             # /product/ 格式（備用）
            ]

            for pattern in patterns:
                matches = re.findall(pattern, html, re.IGNORECASE)
                for match in matches:
                    # 補全相對路徑
                    if match.startswith("/"):
                        full_url = "https://www.hktvmall.com" + match
                    elif match.startswith("http"):
                        full_url = match
                    else:
                        continue

                    # 清理 URL（移除追蹤參數）
                    full_url = full_url.split("?")[0]
                    product_urls.add(full_url)

            return list(product_urls)

        except Exception:
            return []

    def discover_hktv_products(
        self,
        category_url: str,
        max_products: int = 50,
        search_pages: int = 3
    ) -> List[str]:
        """
        專門針對 HKTVmall 的商品發現（增強版）

        Args:
            category_url: HKTVmall 類別頁面 URL
            max_products: 最大返回商品數
            search_pages: 搜索的頁數（用於分頁）

        Returns:
            商品 URL 列表
        """
        all_urls = set()

        # =============================================
        # 步驟 1: 主頁面爬取
        # =============================================
        try:
            page_urls = self._extract_product_links_from_page(category_url)
            all_urls.update(page_urls)
        except Exception:
            pass

        # =============================================
        # 步驟 2: 嘗試分頁 URL（HKTVmall 分頁格式）
        # =============================================
        # HKTVmall 分頁格式: ?page=2, ?page=3 等
        base_url = category_url.split("?")[0]

        for page_num in range(2, search_pages + 1):
            if len(all_urls) >= max_products:
                break

            try:
                page_url = f"{base_url}?page={page_num}"
                page_urls = self._extract_product_links_from_page(page_url)
                all_urls.update(page_urls)
            except Exception:
                break  # 如果分頁失敗，停止嘗試

        # =============================================
        # 步驟 3: 使用 map 作為補充
        # =============================================
        if len(all_urls) < max_products:
            try:
                map_result = self.map_urls(category_url, limit=200)
                for url in map_result.urls:
                    if re.search(r"/p/H\d+", url, re.IGNORECASE):
                        all_urls.add(url)
                        if len(all_urls) >= max_products:
                            break
            except Exception:
                pass

        # 限制返回數量
        return list(all_urls)[:max_products]

    # =============================================
    # 商品信息提取
    # =============================================

    def extract_product_info(self, url: str, use_actions: bool = False) -> ProductInfo:
        """
        爬取並解析商品資訊

        Args:
            url: 商品頁面 URL
            use_actions: 是否使用 Actions（用於動態頁面）

        Returns:
            ProductInfo 對象
        """
        # 優先使用 JSON Mode
        try:
            raw_data = self.scrape_url(url, use_json_mode=True)
            return self._parse_json_mode_result(raw_data)
        except Exception:
            pass

        # 如果需要處理動態頁面
        if use_actions:
            raw_data = self.scrape_with_actions(
                url,
                actions=[
                    {"type": "wait", "milliseconds": 2000},
                    {"type": "scroll", "direction": "down", "amount": 500},
                    {"type": "wait", "milliseconds": 1000},
                ]
            )
        else:
            raw_data = self.scrape_url(url, use_json_mode=False)

        return self._parse_fallback_result(raw_data)

    def _parse_json_mode_result(self, raw_data: Dict[str, Any]) -> ProductInfo:
        """解析 JSON Mode 返回的結構化數據"""
        json_data = raw_data.get("json", {})

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
        if price and original_price and original_price > 0:
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

        # 獲取圖片 URL
        image_url = json_data.get("image_url") or self._extract_image(raw_data)

        return ProductInfo(
            name=json_data.get("product_name") or "未知商品",
            price=price,
            original_price=original_price,
            discount_percent=discount_percent,
            stock_status=stock_status,
            rating=rating,
            review_count=json_data.get("review_count"),
            image_url=image_url,
            description=json_data.get("description"),
            sku=json_data.get("sku"),
            brand=json_data.get("brand"),
            category=json_data.get("category"),
            promotion_text=json_data.get("promotion_text"),
            raw_data=raw_data,
        )

    def _parse_fallback_result(self, raw_data: Dict[str, Any]) -> ProductInfo:
        """使用正則表達式解析（後備方案）"""
        markdown = raw_data.get("markdown", "")
        html = raw_data.get("html", "")

        # 解析商品名稱
        name = self._extract_title(markdown, html)

        # 解析價格
        price, original_price = self._extract_prices(markdown, html)

        # 計算折扣
        discount_percent = None
        if price and original_price and original_price > 0:
            discount_percent = round((1 - price / original_price) * 100, 2)

        # 解析庫存狀態
        stock_status = self._extract_stock_status(markdown, html)

        # 解析評分
        rating, review_count = self._extract_rating(markdown, html)

        # 解析圖片
        image_url = self._extract_image(raw_data)

        return ProductInfo(
            name=name or "未知商品",
            price=price,
            original_price=original_price,
            discount_percent=discount_percent,
            stock_status=stock_status,
            rating=rating,
            review_count=review_count,
            image_url=image_url,
            raw_data=raw_data,
        )

    # =============================================
    # 輔助解析方法
    # =============================================

    def _normalize_stock_status(self, status: Optional[str]) -> Optional[str]:
        """標準化庫存狀態"""
        if not status:
            return None

        status_lower = status.lower()

        if any(kw in status_lower for kw in ["out of stock", "缺貨", "售罄", "暫時缺貨", "sold out"]):
            return "out_of_stock"
        elif any(kw in status_lower for kw in ["low stock", "庫存緊張", "只剩", "limited"]):
            return "low_stock"
        elif any(kw in status_lower for kw in ["pre-order", "預購", "預訂", "preorder"]):
            return "preorder"
        elif any(kw in status_lower for kw in ["in stock", "有貨", "現貨", "available"]):
            return "in_stock"

        return status

    def _extract_title(self, markdown: str, html: str) -> Optional[str]:
        """從內容中提取標題"""
        # 嘗試從 markdown 的第一個標題提取
        match = re.search(r"^#\s+(.+)$", markdown, re.MULTILINE)
        if match:
            return match.group(1).strip()

        # 嘗試從 HTML title 提取
        match = re.search(r"<title>(.+?)</title>", html, re.IGNORECASE)
        if match:
            return match.group(1).strip()

        return None

    def _extract_prices(self, markdown: str, html: str) -> tuple[Optional[Decimal], Optional[Decimal]]:
        """從內容中提取價格"""
        # 匹配 HKD 價格格式
        price_patterns = [
            r"HK\$\s*([\d,]+(?:\.\d{2})?)",
            r"\$\s*([\d,]+(?:\.\d{2})?)",
            r"([\d,]+(?:\.\d{2})?)\s*(?:HKD|港幣)",
        ]

        prices = []
        for pattern in price_patterns:
            matches = re.findall(pattern, markdown + html)
            for match in matches:
                try:
                    price = Decimal(match.replace(",", ""))
                    if price > 0:
                        prices.append(price)
                except (ValueError, TypeError, InvalidOperation):
                    # 無法解析的價格字符串，跳過
                    pass

        if not prices:
            return None, None

        # 去重並排序
        prices = sorted(set(prices))

        # 最低價為現價，最高價為原價
        current_price = prices[0]
        original_price = prices[-1] if len(prices) > 1 else None

        return current_price, original_price

    def _extract_stock_status(self, markdown: str, html: str) -> Optional[str]:
        """從內容中提取庫存狀態"""
        content = (markdown + html).lower()
        return self._normalize_stock_status(content)

    def _extract_rating(self, markdown: str, html: str) -> tuple[Optional[Decimal], Optional[int]]:
        """從內容中提取評分"""
        content = markdown + html

        # 匹配評分格式
        rating_match = re.search(r"(\d+(?:\.\d)?)\s*(?:/\s*5|★|stars?)", content, re.IGNORECASE)
        rating = Decimal(rating_match.group(1)) if rating_match else None

        # 匹配評論數
        review_match = re.search(r"(\d+)\s*(?:reviews?|評論|則評價)", content, re.IGNORECASE)
        review_count = int(review_match.group(1)) if review_match else None

        return rating, review_count

    def _extract_image(self, raw_data: Dict[str, Any]) -> Optional[str]:
        """從原始數據中提取圖片 URL"""
        # Firecrawl 可能在 metadata 中返回圖片
        metadata = raw_data.get("metadata", {})
        if "ogImage" in metadata:
            return metadata["ogImage"]

        # 從 HTML 中提取第一張產品圖片
        html = raw_data.get("html", "")
        match = re.search(r'<img[^>]+src="([^"]+)"[^>]*class="[^"]*product[^"]*"', html, re.IGNORECASE)
        if match:
            return match.group(1)

        return None

    # =============================================
    # 批量操作
    # =============================================

    def crawl_products(self, url: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        爬取整個網站的商品頁面

        Args:
            url: 起始 URL
            limit: 最大爬取頁面數

        Returns:
            爬取結果列表
        """
        try:
            # SDK v4.x 使用 crawl() 方法
            result = self.app.crawl(
                url,
                limit=limit,
                scrape_options={
                    "formats": ["markdown"],
                    "onlyMainContent": True,
                }
            )

            # CrawlJob 對象有 data 屬性
            if hasattr(result, 'data') and result.data:
                return [self._document_to_dict(doc) for doc in result.data]
            return []
        except Exception:
            return []

    def batch_scrape(
        self,
        urls: List[str],
        options: Optional[ScrapeOptions] = None,
        use_json_mode: bool = False,
        on_progress: Optional[Callable[[int, int], None]] = None
    ) -> List[Dict[str, Any]]:
        """
        批量抓取多個 URL（使用 Firecrawl Batch API）

        Args:
            urls: URL 列表
            options: 抓取選項
            use_json_mode: 是否使用 JSON Mode
            on_progress: 進度回調 (completed, total)

        Returns:
            抓取結果列表
        """
        if not urls:
            return []

        opts = options or ScrapeOptions()

        # 構建格式
        formats = ["markdown", "html"]
        if use_json_mode:
            formats = [
                {
                    "type": "json",
                    "schema": ProductSchema.model_json_schema(),
                },
                "markdown",
                "html"
            ]

        logger.info(f"Starting batch scrape of {len(urls)} URLs")

        try:
            # 使用 Firecrawl batch_scrape API
            job = self.app.batch_scrape(
                urls,
                formats=formats,
                only_main_content=opts.only_main_content,
                wait_for=opts.wait_for,
                timeout=opts.timeout,
            )

            # 等待完成並收集結果
            results = []
            if hasattr(job, 'data') and job.data:
                for doc in job.data:
                    results.append(self._document_to_dict(doc))

            logger.info(f"Batch scrape completed: {len(results)}/{len(urls)} successful")
            return results

        except AttributeError:
            # SDK 版本不支持 batch_scrape，回退到逐個抓取
            logger.warning("Firecrawl SDK does not support batch_scrape, falling back to sequential")
            return self._fallback_batch_scrape(urls, opts, use_json_mode, on_progress)

        except Exception as e:
            logger.error(f"Batch scrape failed: {e}")
            return self._fallback_batch_scrape(urls, opts, use_json_mode, on_progress)

    def _fallback_batch_scrape(
        self,
        urls: List[str],
        options: ScrapeOptions,
        use_json_mode: bool,
        on_progress: Optional[Callable[[int, int], None]] = None
    ) -> List[Dict[str, Any]]:
        """批量抓取的回退實現（逐個抓取）"""
        import time

        results = []
        total = len(urls)

        for idx, url in enumerate(urls):
            try:
                result = self.scrape_url(url, use_json_mode=use_json_mode, options=options)
                results.append(result)
            except Exception as e:
                logger.warning(f"Failed to scrape {url}: {e}")
                results.append({"error": str(e), "url": url})

            if on_progress:
                on_progress(idx + 1, total)

            # 請求間延遲（避免速率限制）
            if idx < total - 1:
                time.sleep(1.0)

        return results

    async def batch_scrape_async(
        self,
        urls: List[str],
        options: Optional[ScrapeOptions] = None,
        use_json_mode: bool = False,
        max_concurrent: int = 5,
        on_progress: Optional[Callable[[int, int], None]] = None
    ) -> List[Dict[str, Any]]:
        """
        異步批量抓取（並發執行）

        Args:
            urls: URL 列表
            options: 抓取選項
            use_json_mode: 是否使用 JSON Mode
            max_concurrent: 最大並發數
            on_progress: 進度回調

        Returns:
            抓取結果列表
        """
        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        opts = options or ScrapeOptions()
        results = [None] * len(urls)
        completed = 0

        async def scrape_one(idx: int, url: str):
            nonlocal completed
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                try:
                    result = await loop.run_in_executor(
                        executor,
                        lambda: self.scrape_url(url, use_json_mode=use_json_mode, options=opts)
                    )
                    results[idx] = result
                except Exception as e:
                    logger.warning(f"Failed to scrape {url}: {e}")
                    results[idx] = {"error": str(e), "url": url}

                completed += 1
                if on_progress:
                    on_progress(completed, len(urls))

        # 使用 semaphore 控制並發
        semaphore = asyncio.Semaphore(max_concurrent)

        async def bounded_scrape(idx: int, url: str):
            async with semaphore:
                await scrape_one(idx, url)
                # 並發請求間的小延遲
                await asyncio.sleep(0.5)

        # 並發執行
        tasks = [bounded_scrape(idx, url) for idx, url in enumerate(urls)]
        await asyncio.gather(*tasks)

        return results


# =============================================
# 單例
# =============================================

_connector: Optional[FirecrawlConnector] = None


def get_firecrawl_connector() -> FirecrawlConnector:
    """獲取 Firecrawl 連接器單例"""
    global _connector
    if _connector is None:
        _connector = FirecrawlConnector()
    return _connector
