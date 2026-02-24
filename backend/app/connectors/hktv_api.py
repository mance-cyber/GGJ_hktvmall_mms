# =============================================
# HKTVmall Product Search Client
# 雙引擎搜索：Algolia 全文搜索 + 分類 API
# =============================================
# Algolia（主路線）：HKTVmall 前端的真正搜索引擎，全文匹配
# Category API（備用）：分類搜索 API，僅在 Algolia 不可用時使用
# 優勢：~200-500ms/請求、結構化 JSON、含價格、零 credit

import re
import json
import time
import asyncio
import logging
import threading
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from urllib.parse import quote

import httpx

logger = logging.getLogger(__name__)


# =============================================
# 數據模型
# =============================================

@dataclass
class HKTVProduct:
    """HKTVmall 商品數據"""
    name: str
    url: str
    sku: str
    price: Optional[Decimal] = None
    image_url: Optional[str] = None
    store_name: Optional[str] = None
    # 擴展字段：Algolia 完整競品情報
    original_price: Optional[Decimal] = None    # priceList 中 type=BUY（原價）
    plus_price: Optional[Decimal] = None        # priceList 中 type=PLUS（會員價）
    rating: Optional[Decimal] = None            # ratingValue
    review_count: Optional[int] = None          # numberOfReviews
    sold_quantity: Optional[str] = None         # soldQuantity（"100+" 格式）
    origin_country: Optional[str] = None        # originCountry
    stock_status: Optional[str] = None          # inventoryStatus → in_stock/out_of_stock

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "name": self.name,
            "url": self.url,
            "sku": self.sku,
            "price": str(self.price) if self.price else None,
            "image_url": self.image_url,
            "store_name": self.store_name,
        }
        # 擴展字段：僅在有值時輸出
        if self.original_price is not None:
            result["original_price"] = str(self.original_price)
        if self.plus_price is not None:
            result["plus_price"] = str(self.plus_price)
        if self.rating is not None:
            result["rating"] = str(self.rating)
        if self.review_count is not None:
            result["review_count"] = self.review_count
        if self.sold_quantity is not None:
            result["sold_quantity"] = self.sold_quantity
        if self.origin_country is not None:
            result["origin_country"] = self.origin_country
        if self.stock_status is not None:
            result["stock_status"] = self.stock_status
        return result


# =============================================
# API Client
# =============================================

class HKTVApiClient:
    """
    HKTVmall 雙引擎搜索客戶端

    主路線：Algolia 全文搜索（~200-500ms，覆蓋所有關鍵詞）
    備用：分類搜索 API（Algolia 不可用時降級）
    """

    # ==================== Algolia 全文搜索 ====================
    ALGOLIA_URL = "https://8rn1y79f02-dsn.algolia.net/1/indexes/*/queries"
    ALGOLIA_APP_ID = "8RN1Y79F02"
    ALGOLIA_API_KEY = "a4a336abc62ab842842a81de642b484a"
    ALGOLIA_INDEX = "hktvProduct"
    ALGOLIA_HEADERS = {
        "Content-Type": "application/json",
        "x-algolia-application-id": "8RN1Y79F02",
        "x-algolia-api-key": "a4a336abc62ab842842a81de642b484a",
    }
    # 只請求實際需要的字段（126 → 14），減少傳輸量
    ALGOLIA_FIELDS = [
        "nameZh", "code", "urlZh", "sellingPrice", "priceList",
        "images", "storeNameZh", "hasStock", "catNameZh",
        "ratingValue", "numberOfReviews", "soldQuantity",
        "originCountry", "inventoryStatus",
    ]

    # inventoryStatus → stock_status 映射
    _INVENTORY_STATUS_MAP = {
        "INSTOCK": "in_stock",
        "IN_STOCK": "in_stock",
        "LOWSTOCK": "low_stock",
        "LOW_STOCK": "low_stock",
    }

    # 寵物食品分類黑名單（GoGoJap 是人類食品賣家）
    PET_CATEGORY_KEYWORDS = frozenset(["貓", "狗", "寵物"])

    # ==================== 分類搜索 API（備用） ====================
    CATEGORY_API_URL = "https://cate-search.hktvmall.com/query/products"
    CATEGORY_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": "https://www.hktvmall.com/",
        "Origin": "https://www.hktvmall.com",
        "Accept": "application/json",
        "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8",
    }

    REQUEST_TIMEOUT = 15.0
    HKTV_BASE = "https://www.hktvmall.com"
    CACHE_TTL = 300  # 搜索結果快取 5 分鐘
    CACHE_CLEANUP_INTERVAL = 600  # 每 10 分鐘清理過期條目

    def __init__(self):
        self._client: Optional[httpx.AsyncClient] = None
        self._client_lock = asyncio.Lock()
        self._cache: Dict[str, Tuple[List, float]] = {}
        self._last_cleanup = 0.0

    async def _get_client(self) -> httpx.AsyncClient:
        """延遲初始化 httpx 客戶端（async-safe）"""
        if self._client is not None and not self._client.is_closed:
            return self._client
        async with self._client_lock:
            if self._client is None or self._client.is_closed:
                self._client = httpx.AsyncClient(
                    timeout=self.REQUEST_TIMEOUT,
                    verify=False,
                )
        return self._client

    async def close(self):
        """關閉 HTTP 客戶端"""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    def _absolute_url(self, path: str) -> str:
        """構建絕對 URL（處理路徑前綴）"""
        if not path:
            return ""
        if not path.startswith("/"):
            path = f"/{path}"
        return f"{self.HKTV_BASE}{path}"

    # =============================================
    # 搜索結果快取
    # =============================================

    def _cache_get(self, key: str) -> Optional[List["HKTVProduct"]]:
        """查詢快取（TTL 過期自動清除，定期批量清理）"""
        now = time.monotonic()

        # 定期清理過期條目（防止記憶體洩漏）
        if now - self._last_cleanup > self.CACHE_CLEANUP_INTERVAL:
            self._cleanup_cache()
            self._last_cleanup = now

        entry = self._cache.get(key)
        if entry is None:
            return None
        results, ts = entry
        if now - ts > self.CACHE_TTL:
            del self._cache[key]
            return None
        return results

    def _cache_set(self, key: str, results: List["HKTVProduct"]):
        """寫入快取"""
        self._cache[key] = (results, time.monotonic())

    def _cleanup_cache(self):
        """移除所有過期條目"""
        now = time.monotonic()
        expired = [k for k, (_, ts) in self._cache.items() if now - ts > self.CACHE_TTL]
        for k in expired:
            del self._cache[k]
        if expired:
            logger.info(f"清理過期快取: {len(expired)} 條目")

    # =============================================
    # 統一搜索入口
    # =============================================

    async def search_products(
        self,
        keyword: str,
        page_size: int = 20,
        page: int = 0,
        sort: str = "sales-volume-desc",
    ) -> List[HKTVProduct]:
        """
        搜索 HKTVmall 商品（快取 → Algolia → 分類 API）

        Args:
            keyword: 搜索關鍵詞
            page_size: 每頁結果數
            page: 頁碼（從 0 開始）
            sort: 排序方式（僅分類 API 使用）

        Returns:
            HKTVProduct 列表
        """
        cache_key = f"{keyword}:{page_size}:{page}:{sort}"

        # 快取命中 → 0ms
        cached = self._cache_get(cache_key)
        if cached is not None:
            logger.info(f"cache hit: keyword='{keyword}' ({len(cached)} 商品)")
            return cached

        # Algolia → Category API
        products = await self._search_algolia(keyword, page_size, page)
        if not products:
            logger.info(f"Algolia 無結果，降級到分類 API: keyword='{keyword}'")
            products = await self._search_category_api(keyword, page_size, page, sort)

        # 寫入快取（含空結果，避免反覆重試）
        self._cache_set(cache_key, products)
        return products

    # =============================================
    # Algolia 全文搜索
    # =============================================

    async def _search_algolia(
        self,
        keyword: str,
        hits_per_page: int = 20,
        page: int = 0,
    ) -> List[HKTVProduct]:
        """
        Algolia 全文搜索

        HKTVmall 前端的真正搜索引擎。
        支持全部關鍵詞（包括泛分類詞如「刺身」「和牛」）。
        ~200-500ms，結構化 JSON，含價格。
        """
        attrs_json = json.dumps(self.ALGOLIA_FIELDS)
        params = (
            f"query={quote(keyword)}"
            f"&hitsPerPage={hits_per_page}"
            f"&page={page}"
            f"&attributesToRetrieve={quote(attrs_json)}"
        )

        payload = {
            "requests": [{
                "indexName": self.ALGOLIA_INDEX,
                "params": params,
            }]
        }

        try:
            client = await self._get_client()
            resp = await client.post(
                self.ALGOLIA_URL,
                json=payload,
                headers=self.ALGOLIA_HEADERS,
            )
            resp.raise_for_status()
            data = resp.json()
        except httpx.TimeoutException:
            logger.warning(f"algolia 超時: keyword={keyword}")
            return []
        except Exception as e:
            logger.warning(f"algolia 請求失敗: keyword={keyword} - {e}")
            return []

        return self._parse_algolia_hits(data)

    def _parse_algolia_hits(self, data: dict) -> List[HKTVProduct]:
        """解析 Algolia 搜索結果（含食品過濾）"""
        results_list = data.get("results", [])
        if not results_list:
            return []

        hits = results_list[0].get("hits", [])
        total = results_list[0].get("nbHits", 0)

        products = []
        filtered = 0
        for hit in hits:
            name = hit.get("nameZh", "")
            if not name:
                continue

            # 食品過濾：排除寵物食品
            if self._is_pet_product(hit):
                filtered += 1
                continue

            # URL
            full_url = self._absolute_url(hit.get("urlZh", ""))

            # 價格：優先 sellingPrice（實際售價），其次 priceList
            price = self._extract_algolia_price(hit)

            # 完整價格地圖：BUY（原價）/ DISCOUNT / PLUS（會員價）
            price_map = self._extract_algolia_price_map(hit)

            # 圖片
            image_url = self._extract_algolia_image(hit)

            # 評分 / 評論數
            rating = None
            raw_rating = hit.get("ratingValue")
            if raw_rating is not None:
                try:
                    rating = Decimal(str(raw_rating))
                except (ValueError, TypeError, InvalidOperation):
                    pass

            review_count = None
            raw_reviews = hit.get("numberOfReviews")
            if raw_reviews is not None:
                try:
                    review_count = int(raw_reviews)
                except (ValueError, TypeError):
                    pass

            # 庫存狀態映射（保留 low_stock 三態區分）
            inv_status = hit.get("inventoryStatus")
            stock_status = None
            if inv_status is not None:
                stock_status = self._INVENTORY_STATUS_MAP.get(
                    str(inv_status).upper(), "out_of_stock",
                )

            products.append(HKTVProduct(
                name=name,
                url=full_url,
                sku=hit.get("code", ""),
                price=price,
                image_url=image_url,
                store_name=hit.get("storeNameZh") or None,
                original_price=price_map.get("buy"),
                plus_price=price_map.get("plus"),
                rating=rating,
                review_count=review_count,
                sold_quantity=str(hit["soldQuantity"]).strip() if hit.get("soldQuantity") is not None else None,
                origin_country=hit.get("originCountry") or None,
                stock_status=stock_status,
            ))

        if filtered:
            logger.info(f"algolia: {len(products)} 商品, {filtered} 寵物食品已過濾 (total={total})")
        else:
            logger.info(f"algolia: {len(products)} 商品 (total={total})")
        return products

    def _is_pet_product(self, hit: dict) -> bool:
        """檢查是否為寵物食品（通過分類名稱判斷）"""
        categories = hit.get("catNameZh", [])
        if not categories:
            return False
        cat_text = " ".join(categories)
        return any(kw in cat_text for kw in self.PET_CATEGORY_KEYWORDS)

    @staticmethod
    def _extract_algolia_price(hit: dict) -> Optional[Decimal]:
        """從 Algolia hit 提取價格"""
        # 優先：sellingPrice（實際售價，含折扣）
        selling_price = hit.get("sellingPrice")
        if selling_price is not None:
            try:
                return Decimal(str(selling_price))
            except (ValueError, TypeError, InvalidOperation) as e:
                logger.debug(f"sellingPrice 格式異常: {selling_price!r} - {e}")

        # 備用：priceList[0].value
        price_list = hit.get("priceList")
        if price_list and isinstance(price_list, list) and len(price_list) > 0:
            first = price_list[0]
            if isinstance(first, dict):
                val = first.get("value")
                if val is not None:
                    try:
                        return Decimal(str(val))
                    except (ValueError, TypeError, InvalidOperation) as e:
                        logger.debug(f"priceList.value 格式異常: {val!r} - {e}")
                formatted = first.get("formattedValue", "")
                return HKTVApiClient._parse_price(formatted)

        return None

    @staticmethod
    def _extract_algolia_price_map(hit: dict) -> Dict[str, Optional[Decimal]]:
        """
        從 priceList 提取 BUY/DISCOUNT/PLUS 三級價格

        priceList 結構示例：
        [
            {"type": "BUY", "value": 199.0, ...},
            {"type": "DISCOUNT", "value": 159.0, ...},
            {"type": "PLUS", "value": 149.0, ...},
        ]
        """
        result: Dict[str, Optional[Decimal]] = {}
        price_list = hit.get("priceList")
        if not price_list or not isinstance(price_list, list):
            return result

        type_map = {"BUY": "buy", "DISCOUNT": "discount", "PLUS": "plus"}
        for entry in price_list:
            if not isinstance(entry, dict):
                continue
            ptype = str(entry.get("priceType") or entry.get("type") or "").upper()
            key = type_map.get(ptype)
            if not key:
                continue
            val = entry.get("value")
            if val is not None:
                try:
                    result[key] = Decimal(str(val))
                except (ValueError, TypeError, InvalidOperation):
                    pass
            elif formatted := entry.get("formattedValue"):
                parsed = HKTVApiClient._parse_price(formatted)
                if parsed is not None:
                    result[key] = parsed
        return result

    def _extract_algolia_image(self, hit: dict) -> Optional[str]:
        """從 Algolia hit 提取圖片 URL"""
        images = hit.get("images", [])
        if not images or not isinstance(images, list):
            return None

        first_img = images[0]
        if isinstance(first_img, dict):
            img_url = first_img.get("url", "")
        elif isinstance(first_img, str):
            img_url = first_img
        else:
            return None

        if not img_url:
            return None
        return self._absolute_url(img_url) if img_url.startswith("/") else img_url

    # =============================================
    # 分類搜索 API（備用）
    # =============================================

    async def _search_category_api(
        self,
        keyword: str,
        page_size: int = 20,
        page: int = 0,
        sort: str = "sales-volume-desc",
    ) -> List[HKTVProduct]:
        """
        分類搜索 API（Algolia 不可用時的備用方案）

        局限：非全文搜索，泛分類詞可能退化為推薦結果
        """
        query = f"{keyword}:{sort}:"
        form_data = {
            "query": query,
            "currentPage": str(page),
            "pageSize": str(min(page_size, 60)),
            "pageType": "search",
            "lang": "zh",
        }

        try:
            client = await self._get_client()
            resp = await client.post(
                self.CATEGORY_API_URL,
                data=form_data,
                headers=self.CATEGORY_HEADERS,
            )
            resp.raise_for_status()
            result = resp.json()
        except httpx.TimeoutException:
            logger.warning(f"category-api 超時: keyword={keyword}")
            return []
        except Exception as e:
            logger.warning(f"category-api 請求失敗: keyword={keyword} - {e}")
            return []

        return self._parse_category_products(result, keyword)

    def _parse_category_products(
        self, data: dict, keyword: str
    ) -> List[HKTVProduct]:
        """解析分類 API 響應，過濾不相關的推薦結果"""
        raw_products = data.get("products", [])
        if not raw_products:
            return []

        results = []
        for p in raw_products:
            name = p.get("name", "")
            full_url = self._absolute_url(p.get("url", ""))

            price = None
            price_list = p.get("priceList", [])
            if price_list:
                formatted = price_list[0].get("formattedValue", "")
                price = self._parse_price(formatted)

            image_url = None
            images = p.get("images", [])
            if images:
                img_url = images[0].get("url", "")
                if img_url:
                    image_url = self._absolute_url(img_url) if img_url.startswith("/") else img_url

            store_name = None
            store = p.get("store", {})
            if store:
                store_name = store.get("name")

            results.append(HKTVProduct(
                name=name,
                url=full_url,
                sku=p.get("code", ""),
                price=price,
                image_url=image_url,
                store_name=store_name,
            ))

        # 相關性過濾：分類 API 會退化返回推薦結果
        relevant = [p for p in results if keyword in p.name]
        if relevant:
            logger.info(
                f"category-api: keyword='{keyword}' → "
                f"{len(relevant)}/{len(results)} 相關"
            )
            return relevant

        logger.info(
            f"category-api: keyword='{keyword}' → "
            f"0/{len(results)} 相關（推薦結果已過濾）"
        )
        return []

    @staticmethod
    def _parse_price(formatted: str) -> Optional[Decimal]:
        """解析價格字串（如 '$ 130.00' → Decimal('130.00')）"""
        if not formatted:
            return None
        match = re.search(r"\$\s*([\d,]+\.?\d*)", formatted)
        if match:
            try:
                return Decimal(match.group(1).replace(",", ""))
            except Exception:
                return None
        return None


# =============================================
# 單例
# =============================================

_api_client: Optional[HKTVApiClient] = None
_api_client_lock = threading.Lock()


def get_hktv_api_client() -> HKTVApiClient:
    """獲取 HKTVApiClient 單例（線程安全）"""
    global _api_client
    if _api_client is None:
        with _api_client_lock:
            if _api_client is None:
                _api_client = HKTVApiClient()
    return _api_client
