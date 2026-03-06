# =============================================
# Algolia Fetcher — Competitor v2
# 從 HKTVmall Algolia 搜索競品商品
# =============================================

import logging
from typing import Optional

from app.connectors.hktv_api import HKTVApiClient, HKTVProduct, get_hktv_api_client

logger = logging.getLogger(__name__)


class AlgoliaFetcher:
    """
    HKTVmall Algolia 商品搜索器（競品建庫用）
    
    封裝 HKTVApiClient，提供：
    - search_by_keyword：按關鍵詞搜索（Line A，找我方商品的競品）
    - search_by_store_code：按商戶代碼拉取所有商品（Line B，市場情報）
    - search_pages：多頁搜索（取大量商品）
    """

    def __init__(self, client: Optional[HKTVApiClient] = None):
        self._client = client or get_hktv_api_client()

    async def search_by_keyword(
        self,
        keyword: str,
        max_results: int = 50,
    ) -> list[HKTVProduct]:
        """
        按關鍵詞搜索 HKTVmall 商品。
        
        用於 Line A：為自家商品搜索競品候選。
        
        Args:
            keyword: 搜索關鍵詞（如 "和牛西冷"、"三文魚刺身"）
            max_results: 最多返回幾件商品
            
        Returns:
            HKTVProduct 列表
        """
        page_size = min(max_results, 100)
        pages_needed = (max_results + page_size - 1) // page_size

        results = []
        for page in range(pages_needed):
            products = await self._client.search_products(
                keyword=keyword,
                page_size=page_size,
                page=page,
            )
            results.extend(products)
            if len(products) < page_size:
                break  # 已到最後一頁
            if len(results) >= max_results:
                break

        return results[:max_results]

    async def search_by_store_code(
        self,
        store_code: str,
        max_results: int = 500,
    ) -> list[HKTVProduct]:
        """
        按商戶代碼拉取所有商品。
        
        用於 Line B：抓取 Tier 1/2 商戶的全部商品。
        
        Args:
            store_code: HKTVmall 商戶代碼（如 "H6852001"）
            max_results: 最多返回幾件商品
            
        Returns:
            HKTVProduct 列表
        """
        page_size = 100  # Algolia 最大 hitsPerPage
        results = []
        page = 0

        while len(results) < max_results:
            products = await self._client.search_by_store_code(
                store_code=store_code,
                page_size=page_size,
                page=page,
            )
            if not products:
                break
            results.extend(products)
            if len(products) < page_size:
                break  # 已到最後一頁
            page += 1

        logger.info(f"store_code={store_code} → {len(results)} 件商品")
        return results[:max_results]

    async def search_by_category_keywords(
        self,
        keywords: list[str],
        max_per_keyword: int = 20,
    ) -> dict[str, list[HKTVProduct]]:
        """
        按多個關鍵詞批量搜索（新商戶發現用）。
        
        Returns:
            {keyword: [HKTVProduct, ...]} 的字典
        """
        results = {}
        for kw in keywords:
            products = await self.search_by_keyword(kw, max_results=max_per_keyword)
            results[kw] = products
            logger.info(f"keyword='{kw}' → {len(products)} 件")
        return results

    async def close(self):
        """關閉底層 HTTP client"""
        await self._client.close()


# 全局單例（懶加載）
_fetcher: Optional[AlgoliaFetcher] = None


def get_algolia_fetcher() -> AlgoliaFetcher:
    global _fetcher
    if _fetcher is None:
        _fetcher = AlgoliaFetcher()
    return _fetcher
