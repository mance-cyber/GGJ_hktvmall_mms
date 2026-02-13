# =============================================
# Wellcome (惠康) HTTP 元數據提取器
# =============================================
# 從惠康產品頁面的 JSON-LD 結構化數據提取商品資訊
# 零成本，無需 JS 渲染，速度 ~50-100ms/請求
# 惠康 URL 格式: /en/p/{name}/i/{product-id}.html

import re
import json
import asyncio
import logging
from typing import Optional, List
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from urllib.parse import urlparse, urlunparse, quote

import httpx

logger = logging.getLogger(__name__)


# =============================================
# 數據模型
# =============================================

@dataclass
class WellcomeProduct:
    """從 JSON-LD 提取的惠康商品數據"""
    url: str
    name: Optional[str] = None
    price: Optional[Decimal] = None
    brand: Optional[str] = None
    image_url: Optional[str] = None
    product_id: Optional[str] = None  # 9 位數字

    def to_dict(self) -> dict:
        return {
            "url": self.url,
            "name": self.name,
            "price": str(self.price) if self.price else None,
            "brand": self.brand,
            "image_url": self.image_url,
            "product_id": self.product_id,
        }


# =============================================
# URL 解析
# =============================================

# 惠康產品 URL: /en/p/{slug}/i/{9-digit-id}.html
_PRODUCT_ID_PATTERN = re.compile(r"/i/(\d{5,12})\.html")

# JSON-LD 提取（從 HTML 中找到 script 標籤）
_JSONLD_PATTERN = re.compile(
    r'<script\s+type=["\']application/ld\+json["\']>(.*?)</script>',
    re.DOTALL | re.IGNORECASE,
)


def extract_product_id(url: str) -> Optional[str]:
    """從惠康 URL 提取產品 ID"""
    match = _PRODUCT_ID_PATTERN.search(url)
    return match.group(1) if match else None


def normalize_url(url: str) -> str:
    """標準化惠康 URL（移除追蹤參數和 fragment）"""
    parsed = urlparse(url)
    return urlunparse((
        parsed.scheme or "https",
        parsed.netloc or "www.wellcome.com.hk",
        parsed.path,
        "",  # params
        "",  # query（惠康產品頁不需要查詢參數）
        "",  # fragment
    ))


def is_product_url(url: str) -> bool:
    """判斷是否為惠康產品頁面 URL"""
    return bool(_PRODUCT_ID_PATTERN.search(url))


# =============================================
# JSON-LD 解析
# =============================================

def parse_jsonld(html: str) -> Optional[dict]:
    """
    從 HTML 中提取 schema.org/Product JSON-LD

    惠康產品頁嵌入的格式：
    {
        "@type": "Product",
        "name": "...",
        "brand": {"name": "..."},
        "offers": {"price": "59.00", "priceCurrency": "HKD"},
        "image": "https://..."
    }
    """
    for match in _JSONLD_PATTERN.finditer(html):
        try:
            data = json.loads(match.group(1))
        except (json.JSONDecodeError, ValueError):
            continue

        # JSON-LD 可能是單個對象或數組
        items = data if isinstance(data, list) else [data]

        for item in items:
            item_type = item.get("@type", "")
            if item_type == "Product" or "Product" in str(item_type):
                return item

    return None


def extract_product_from_jsonld(jsonld: dict, url: str) -> WellcomeProduct:
    """從 JSON-LD 對象構建 WellcomeProduct"""
    name = jsonld.get("name")

    # 價格：offers 可能是對象或數組
    price = None
    offers = jsonld.get("offers", {})
    if isinstance(offers, list):
        offers = offers[0] if offers else {}
    price_str = offers.get("price")
    if price_str:
        try:
            price = Decimal(str(price_str))
        except (InvalidOperation, ValueError):
            pass

    # 品牌
    brand = None
    brand_data = jsonld.get("brand")
    if isinstance(brand_data, dict):
        brand = brand_data.get("name")
    elif isinstance(brand_data, str):
        brand = brand_data

    # 圖片
    image_url = None
    image_data = jsonld.get("image")
    if isinstance(image_data, str):
        image_url = image_data
    elif isinstance(image_data, list) and image_data:
        image_url = image_data[0]
    elif isinstance(image_data, dict):
        image_url = image_data.get("url")

    return WellcomeProduct(
        url=normalize_url(url),
        name=name,
        price=price,
        brand=brand,
        image_url=image_url,
        product_id=extract_product_id(url),
    )


# =============================================
# HTTP Client
# =============================================

class WellcomeHttpClient:
    """
    惠康零成本 HTTP 元數據提取器

    從產品頁面的 JSON-LD 結構化數據提取：名稱、價格、品牌、圖片
    無需 JS 渲染，速度 ~50-100ms/請求
    """

    MAX_CONCURRENT = 5  # 保守並發（惠康有 PoW CAPTCHA）
    REQUEST_TIMEOUT = 15.0

    DEFAULT_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-HK,zh;q=0.9,en;q=0.8",
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
            )
        return self._client

    async def close(self):
        """關閉 HTTP 客戶端"""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def fetch_product_jsonld(self, url: str) -> WellcomeProduct:
        """
        從惠康產品頁面提取 JSON-LD 元數據

        Args:
            url: 惠康產品頁面 URL

        Returns:
            WellcomeProduct（price 可能為 None 若提取失敗）
        """
        product_id = extract_product_id(url)

        try:
            client = await self._get_client()
            resp = await client.get(url)

            if resp.status_code != 200:
                logger.warning(f"wellcome HTTP {resp.status_code}: {url}")
                return WellcomeProduct(
                    url=normalize_url(url),
                    product_id=product_id,
                )

            html = resp.text
            jsonld = parse_jsonld(html)

            if not jsonld:
                logger.warning(f"wellcome 未找到 JSON-LD: {url}")
                return WellcomeProduct(
                    url=normalize_url(url),
                    product_id=product_id,
                )

            product = extract_product_from_jsonld(jsonld, url)
            logger.debug(
                f"wellcome 提取成功: {product.name} ${product.price} ({url})"
            )
            return product

        except httpx.TimeoutException:
            logger.warning(f"wellcome HTTP 超時: {url}")
            return WellcomeProduct(url=normalize_url(url), product_id=product_id)

        except Exception as e:
            logger.warning(f"wellcome HTTP 請求失敗: {url} - {e}")
            return WellcomeProduct(url=normalize_url(url), product_id=product_id)

    async def batch_fetch_products(
        self, urls: List[str]
    ) -> List[WellcomeProduct]:
        """
        批量提取惠康產品數據（並發，受 semaphore 控制）
        """
        if not urls:
            return []

        semaphore = asyncio.Semaphore(self.MAX_CONCURRENT)

        async def bounded_fetch(url: str) -> WellcomeProduct:
            async with semaphore:
                # 每個請求間隔 0.5s，降低觸發 CAPTCHA 風險
                await asyncio.sleep(0.5)
                return await self.fetch_product_jsonld(url)

        tasks = [bounded_fetch(url) for url in urls]
        return await asyncio.gather(*tasks)


# =============================================
# 單例
# =============================================

_wellcome_client: Optional[WellcomeHttpClient] = None


def get_wellcome_http_client() -> WellcomeHttpClient:
    """獲取 WellcomeHttpClient 單例"""
    global _wellcome_client
    if _wellcome_client is None:
        _wellcome_client = WellcomeHttpClient()
    return _wellcome_client
