# =============================================
# Wellcome (惠康) 搜索策略
# =============================================
# 兩層降級搜索：本地索引 → Playwright 瀏覽器
#
# vs HKTVmall 的核心差異：
# HKTVmall 有 Algolia API 即搜即配；
# 惠康無搜索 API，需要「先爬後配」策略。
# =============================================

import logging
from typing import List, Optional
from urllib.parse import quote

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.connectors.wellcome_client import (
    WellcomeProduct,
    get_wellcome_http_client,
    normalize_url,
    extract_product_id,
    is_product_url,
)
from app.connectors.agent_browser import get_agent_browser_connector
from app.config import get_settings

logger = logging.getLogger(__name__)


class WellcomeSearchStrategy:
    """
    惠康兩層搜索策略

    優先級：
    1. 本地索引（查詢 competitor_products 表，~50ms）
    2. Playwright 瀏覽器搜索（實時降級，~30s）
    """

    # 本地索引結果不足此數量時，降級到瀏覽器搜索
    LOCAL_MIN_RESULTS = 3

    SEARCH_URL = "https://www.wellcome.com.hk/zh-hant/search?q={query}"
    CATEGORY_URL = "https://www.wellcome.com.hk/en/category/{category_id}/{page}.html"

    def __init__(self):
        self.http_client = get_wellcome_http_client()
        self.agent_browser = get_agent_browser_connector()

    def build_search_url(self, query: str) -> str:
        """構建搜索 URL"""
        return self.SEARCH_URL.format(query=quote(query))

    # =============================================
    # Layer 1: 本地索引搜索
    # =============================================

    async def search_local_index(
        self,
        db: AsyncSession,
        keyword: str,
        limit: int = 20,
    ) -> List[WellcomeProduct]:
        """
        從本地 competitor_products 表搜索已爬取的惠康商品

        零成本、~50ms，依賴後台定期爬取的分類數據
        """
        from app.models.competitor import Competitor, CompetitorProduct

        search_pattern = f"%{keyword}%"

        stmt = (
            select(CompetitorProduct)
            .join(Competitor, CompetitorProduct.competitor_id == Competitor.id)
            .where(
                Competitor.platform == "wellcome",
                CompetitorProduct.is_active == True,
                CompetitorProduct.name.ilike(search_pattern),
            )
            .limit(limit)
        )

        result = await db.execute(stmt)
        rows = result.scalars().all()

        products = []
        for row in rows:
            # 價格數據在 PriceSnapshot 表，本地索引搜索只需名稱匹配
            products.append(WellcomeProduct(
                url=row.url,
                name=row.name,
                price=None,
                product_id=extract_product_id(row.url),
            ))

        logger.info(
            f"wellcome 本地索引搜索: keyword='{keyword}' → {len(products)} 商品"
        )
        return products

    # =============================================
    # Layer 2: Playwright 瀏覽器搜索
    # =============================================

    async def search_via_browser(
        self,
        keyword: str,
        limit: int = 10,
    ) -> List[WellcomeProduct]:
        """
        用 Playwright 搜索惠康網站，提取產品 URL，再用 HTTP GET 取 JSON-LD

        ~30s，零 credit
        """
        settings = get_settings()
        if not settings.agent_browser_enabled:
            logger.info("wellcome 瀏覽器搜索已禁用")
            return []

        try:
            search_url = self.build_search_url(keyword)

            # 步驟 1: Playwright 提取產品 URL
            urls = await self.agent_browser.discover_wellcome_products(
                search_url, max_products=limit * 2
            )

            if not urls:
                logger.info(f"wellcome 瀏覽器搜索無結果: keyword='{keyword}'")
                return []

            # 步驟 2: HTTP GET JSON-LD 取詳情
            products = await self.http_client.batch_fetch_products(urls[:limit])

            # 過濾掉沒有名稱的結果
            valid = [p for p in products if p.name]

            logger.info(
                f"wellcome 瀏覽器搜索: keyword='{keyword}' → "
                f"{len(urls)} URLs → {len(valid)} 有效商品"
            )
            return valid

        except Exception as e:
            logger.warning(f"wellcome 瀏覽器搜索失敗: keyword='{keyword}' - {e}")
            return []

    # =============================================
    # 後台任務：分類頁爬取
    # =============================================

    async def crawl_category(
        self,
        db: AsyncSession,
        category_id: str,
        category_name: str = "",
        max_pages: int = 5,
    ) -> int:
        """
        爬取惠康分類頁面，填充本地索引

        流程：
        1. Playwright 導航分類頁
        2. 提取所有產品 URL
        3. 翻頁（最多 max_pages 頁）
        4. HTTP GET JSON-LD 取詳情
        5. 寫入 competitor_products 表

        Returns:
            寫入/更新的商品數量
        """
        from app.models.competitor import Competitor, CompetitorProduct

        all_urls = set()

        for page_num in range(1, max_pages + 1):
            page_url = self.CATEGORY_URL.format(
                category_id=category_id, page=page_num
            )

            try:
                urls = await self.agent_browser.discover_wellcome_products(
                    page_url, max_products=50
                )
                if not urls:
                    break  # 空頁 = 已到末頁
                all_urls.update(urls)
                logger.info(
                    f"wellcome 分類爬取: {category_name} 第{page_num}頁 → {len(urls)} URLs"
                )
            except Exception as e:
                logger.warning(
                    f"wellcome 分類爬取失敗: {category_name} 第{page_num}頁 - {e}"
                )
                break

        if not all_urls:
            return 0

        # 批量取 JSON-LD
        products = await self.http_client.batch_fetch_products(list(all_urls))
        valid_products = [p for p in products if p.name]

        # 獲取或創建 Wellcome Competitor
        stmt = select(Competitor).where(Competitor.platform == "wellcome").limit(1)
        result = await db.execute(stmt)
        competitor = result.scalar_one_or_none()

        if not competitor:
            competitor = Competitor(
                name="Wellcome 惠康",
                platform="wellcome",
                base_url="https://www.wellcome.com.hk",
                is_active=True,
            )
            db.add(competitor)
            await db.flush()

        # 寫入 CompetitorProduct
        count = 0
        for p in valid_products:
            normalized = normalize_url(p.url)

            stmt = select(CompetitorProduct).where(CompetitorProduct.url == normalized)
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                # 更新名稱和 SKU
                existing.name = p.name
                existing.sku = p.product_id
            else:
                cp = CompetitorProduct(
                    competitor_id=competitor.id,
                    name=p.name,
                    url=normalized,
                    sku=p.product_id,
                    is_active=True,
                )
                db.add(cp)
                count += 1

        await db.flush()

        logger.info(
            f"wellcome 分類爬取完成: {category_name} → "
            f"{len(all_urls)} URLs → {count} 新商品"
        )
        return count
