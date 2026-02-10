# =============================================
# HKTVmall HTTP 元數據提取器（零 Firecrawl Credit）
# =============================================
# 從靜態 HTML 的 OG meta tags 提取商品元數據
# 用途：商品發現、URL 驗證、元數據獲取
# 不依賴 JS 渲染，速度快（~50ms/請求），零 credit 消耗

import re
import asyncio
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field

import httpx

logger = logging.getLogger(__name__)


# =============================================
# 數據模型
# =============================================

@dataclass
class HKTVMetadata:
    """從 OG tags 提取的商品元數據"""
    url: str
    name: Optional[str] = None
    brand: Optional[str] = None
    sku: Optional[str] = None
    image_url: Optional[str] = None
    description: Optional[str] = None
    valid: bool = True
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "url": self.url,
            "name": self.name,
            "brand": self.brand,
            "sku": self.sku,
            "image_url": self.image_url,
            "description": self.description,
            "valid": self.valid,
        }


# =============================================
# OG Tag 解析
# =============================================

# 預編譯正則：從 HTML 中提取 meta 標籤的 content
_OG_PATTERNS = {
    "og:title": re.compile(
        r'<meta\s+(?:property|name)=["\']og:title["\']\s+content=["\']([^"\']+)["\']',
        re.IGNORECASE,
    ),
    "og:description": re.compile(
        r'<meta\s+(?:property|name)=["\']og:description["\']\s+content=["\']([^"\']+)["\']',
        re.IGNORECASE,
    ),
    "og:image": re.compile(
        r'<meta\s+(?:property|name)=["\']og:image["\']\s+content=["\']([^"\']+)["\']',
        re.IGNORECASE,
    ),
}

# 反向 content-first 模式（某些頁面 content 在前）
_OG_PATTERNS_REV = {
    "og:title": re.compile(
        r'<meta\s+content=["\']([^"\']+)["\']\s+(?:property|name)=["\']og:title["\']',
        re.IGNORECASE,
    ),
    "og:description": re.compile(
        r'<meta\s+content=["\']([^"\']+)["\']\s+(?:property|name)=["\']og:description["\']',
        re.IGNORECASE,
    ),
    "og:image": re.compile(
        r'<meta\s+content=["\']([^"\']+)["\']\s+(?:property|name)=["\']og:image["\']',
        re.IGNORECASE,
    ),
}

# HKTVmall SKU 模式
_SKU_PATTERN = re.compile(r"H\d{7,}")


def parse_og_tags(html: str) -> Dict[str, Optional[str]]:
    """從 HTML 中提取 OG meta tags"""
    result = {}
    for key, pattern in _OG_PATTERNS.items():
        match = pattern.search(html)
        if not match:
            match = _OG_PATTERNS_REV[key].search(html)
        if match:
            content = match.group(1).strip()
            result[key] = content if content else None
        else:
            result[key] = None
    return result


def extract_sku_from_url(url: str) -> Optional[str]:
    """從 URL 中提取 HKTVmall SKU"""
    match = re.search(r"/p/(H\d{7,})", url, re.IGNORECASE)
    return match.group(1) if match else None


def parse_brand_from_title(title: str) -> Optional[str]:
    """
    從 OG title 中提取品牌名
    HKTVmall 商品標題格式常見：「品牌名 - 商品名」或「品牌名 商品名」
    """
    if not title:
        return None

    # 嘗試「品牌 - 商品名」格式
    parts = title.split(" - ", 1)
    if len(parts) == 2 and 2 <= len(parts[0].strip()) <= 30:
        return parts[0].strip()

    # 嘗試「品牌 | 商品名」格式
    parts = title.split(" | ", 1)
    if len(parts) == 2 and 2 <= len(parts[0].strip()) <= 30:
        return parts[0].strip()

    return None


# =============================================
# HTTP Client
# =============================================

class HKTVHttpClient:
    """
    零成本 HTTP 元數據提取器

    從 HKTVmall 商品頁面的靜態 HTML 中提取 OG meta tags，
    無需 JS 渲染，不消耗 Firecrawl credits。

    適用場景：
    - 商品發現：驗證 URL 是否有效
    - 元數據獲取：名稱、品牌、圖片
    - 競品匹配前置：先用 metadata 做初步篩選
    """

    # 並發控制
    MAX_CONCURRENT = 10
    REQUEST_TIMEOUT = 15.0  # 秒

    # 請求 headers（模擬瀏覽器）
    DEFAULT_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8",
    }

    def __init__(self):
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """延遲初始化 httpx 客戶端"""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=self.REQUEST_TIMEOUT,
                headers=self.DEFAULT_HEADERS,
                follow_redirects=True,
                verify=False,  # HKTVmall CDN 需要跳過 TLS
            )
        return self._client

    async def close(self):
        """關閉 HTTP 客戶端"""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    # =============================================
    # 核心方法
    # =============================================

    async def fetch_product_metadata(self, url: str) -> HKTVMetadata:
        """
        提取單個商品的 OG tag 元數據

        Args:
            url: HKTVmall 商品頁面 URL

        Returns:
            HKTVMetadata 包含名稱、品牌、SKU、圖片、描述
        """
        sku = extract_sku_from_url(url)

        try:
            client = await self._get_client()
            resp = await client.get(url)

            if resp.status_code != 200:
                return HKTVMetadata(
                    url=url, sku=sku, valid=False,
                    error=f"HTTP {resp.status_code}",
                )

            # 只需要 <head> 部分，OG tags 都在 head 裡
            html = resp.text
            head_end = html.find("</head>")
            if head_end > 0:
                html = html[:head_end + 7]

            og = parse_og_tags(html)

            title = og.get("og:title")
            # 移除常見後綴
            if title:
                title = re.sub(r"\s*[|\-–]\s*HKTVmall.*$", "", title).strip()

            brand = parse_brand_from_title(og.get("og:title", ""))

            return HKTVMetadata(
                url=url,
                name=title,
                brand=brand,
                sku=sku,
                image_url=og.get("og:image"),
                description=og.get("og:description"),
                valid=True,
            )

        except httpx.TimeoutException:
            logger.warning(f"HTTP 超時: {url}")
            return HKTVMetadata(url=url, sku=sku, valid=False, error="timeout")

        except Exception as e:
            logger.warning(f"HTTP 請求失敗: {url} - {e}")
            return HKTVMetadata(url=url, sku=sku, valid=False, error=str(e))

    async def batch_fetch_metadata(self, urls: List[str]) -> List[HKTVMetadata]:
        """
        批量提取元數據（並發，受 semaphore 控制）

        Args:
            urls: HKTVmall 商品 URL 列表

        Returns:
            HKTVMetadata 列表（順序與輸入一致）
        """
        if not urls:
            return []

        semaphore = asyncio.Semaphore(self.MAX_CONCURRENT)

        async def bounded_fetch(url: str) -> HKTVMetadata:
            async with semaphore:
                return await self.fetch_product_metadata(url)

        tasks = [bounded_fetch(url) for url in urls]
        return await asyncio.gather(*tasks)

    async def validate_product_url(self, url: str) -> bool:
        """
        驗證商品 URL 是否有效（HEAD 請求，極快）

        Args:
            url: 待驗證的 URL

        Returns:
            True 表示 URL 有效（200 OK）
        """
        try:
            client = await self._get_client()
            resp = await client.head(url)
            return resp.status_code == 200
        except Exception:
            return False

    async def batch_validate_urls(self, urls: List[str]) -> List[bool]:
        """批量驗證 URL 有效性"""
        if not urls:
            return []

        semaphore = asyncio.Semaphore(self.MAX_CONCURRENT)

        async def bounded_validate(url: str) -> bool:
            async with semaphore:
                return await self.validate_product_url(url)

        tasks = [bounded_validate(url) for url in urls]
        return await asyncio.gather(*tasks)


# =============================================
# 單例
# =============================================

_http_client: Optional[HKTVHttpClient] = None


def get_hktv_http_client() -> HKTVHttpClient:
    """獲取 HKTVHttpClient 單例"""
    global _http_client
    if _http_client is None:
        _http_client = HKTVHttpClient()
    return _http_client
