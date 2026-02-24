# =============================================
# Cataloger - 競品建庫模塊
# =============================================
# 職責：爬取 HKTVmall 和惠康的肉類/海鮮分類商品，寫入 competitor_products 表。
# 只管「對手有什麼」— 不管標籤（Tagger）、不管匹配（Matcher）。
#
# HKTVmall 側：Algolia API 按關鍵詞批量搜索
# 惠康側：Playwright 分類頁 → 提取 URL → HTTP GET JSON-LD
#
# 每日更新策略：
#   新 URL → 新品入庫，needs_matching=True, last_seen_at=now
#   已有 URL → 更新價格 + last_seen_at，名稱變更則清空標籤
#   消失的 URL → 不處理（Monitor 模塊判定連續 3 天未見才下架）

import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, Set

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.connectors.hktv_api import HKTVApiClient, HKTVProduct
from app.connectors.wellcome_client import (
    WellcomeProduct,
    get_wellcome_http_client,
    normalize_url,
)
from app.connectors.agent_browser import get_agent_browser_connector
from app.config import get_settings
from app.models.database import utcnow
from app.models.competitor import Competitor, CompetitorProduct, PriceSnapshot

logger = logging.getLogger(__name__)


# =============================================
# 搜索關鍵詞（肉類 + 海鮮）
# =============================================

HKTV_KEYWORDS = [
    "和牛", "西冷", "肉眼", "牛柳", "牛仔骨",
    "豬扒", "豬腩", "排骨",
    "三文魚", "刺身", "蝦", "蟹", "帶子", "鮑魚", "龍蝦", "魚柳",
    "急凍牛肉", "急凍豬肉", "急凍海鮮",
]

# 惠康分類 ID → 中文名
WELLCOME_CATEGORIES = {
    "100015-100182-101092": "牛肉",
    "100015-100182-101093": "豬肉",
    "100015-100186-101115": "其他急凍肉",
    "100015-100183": "海鮮",
}

WELLCOME_CATEGORY_URL = "https://www.wellcome.com.hk/en/category/{category_id}/{page}.html"

# Algolia 每頁拉取數量
HKTV_HITS_PER_PAGE = 50
# HKTVmall 每個關鍵詞最多拉取頁數
HKTV_MAX_PAGES = 3
# 惠康每個分類最多拉取頁數
WELLCOME_MAX_PAGES = 5


# =============================================
# CatalogService
# =============================================

class CatalogService:
    """
    競品建庫服務

    build_catalog()  — 手動觸發完整建庫（首次使用）
    update_catalog() — 每日增量更新（與 build 邏輯相同，差異由 upsert 處理）
    """

    # ==================== 公開介面 ====================

    @staticmethod
    async def build_catalog(db: AsyncSession, platform: str = "all") -> dict:
        """
        手動觸發完整建庫

        Args:
            db: 資料庫 session
            platform: "hktvmall" / "wellcome" / "all"

        Returns:
            {"hktvmall": {...}, "wellcome": {...}} 各平台統計
        """
        result = {}

        if platform in ("hktvmall", "all"):
            result["hktvmall"] = await CatalogService._catalog_hktvmall(db)

        if platform in ("wellcome", "all"):
            result["wellcome"] = await CatalogService._catalog_wellcome(db)

        await db.commit()
        logger.info(f"建庫完成: {result}")
        return result

    @staticmethod
    async def update_catalog(db: AsyncSession, platform: str = "all") -> dict:
        """
        每日增量更新（邏輯與 build 相同，upsert 自動處理差異）
        """
        return await CatalogService.build_catalog(db, platform)

    # ==================== HKTVmall 建庫 ====================

    @staticmethod
    async def _catalog_hktvmall(db: AsyncSession) -> dict:
        """
        HKTVmall 建庫：Algolia API 按關鍵詞批量搜索

        流程：
        1. 獲取或創建 HKTVmall Competitor 記錄
        2. 遍歷關鍵詞列表，每個關鍵詞拉取多頁
        3. URL 去重後 upsert 到 competitor_products
        """
        competitor = await CatalogService._ensure_competitor(
            db, name="HKTVmall", platform="hktvmall",
            base_url="https://www.hktvmall.com",
        )

        client = HKTVApiClient()
        seen_urls: Set[str] = set()
        stats = {"new": 0, "updated": 0, "unchanged": 0, "total_fetched": 0}

        try:
            for keyword in HKTV_KEYWORDS:
                for page in range(HKTV_MAX_PAGES):
                    products = await client.search_products(
                        keyword=keyword,
                        page_size=HKTV_HITS_PER_PAGE,
                        page=page,
                    )

                    if not products:
                        break

                    for product in products:
                        if not product.url or product.url in seen_urls:
                            continue
                        seen_urls.add(product.url)
                        stats["total_fetched"] += 1

                        # 組裝擴展數據（plus_price, sold_quantity, origin_country）
                        extra_raw = {
                            "plus_price": str(product.plus_price) if product.plus_price is not None else None,
                            "sold_quantity": product.sold_quantity,
                            "origin_country": product.origin_country,
                        }
                        extra_data = {k: v for k, v in extra_raw.items() if v is not None} or None

                        action = await CatalogService._upsert_competitor_product(
                            db=db,
                            competitor_id=competitor.id,
                            url=product.url,
                            name=product.name,
                            price=product.price,
                            sku=product.sku,
                            platform="hktvmall",
                            original_price=product.original_price,
                            rating=product.rating,
                            review_count=product.review_count,
                            stock_status=product.stock_status,
                            extra_data=extra_data,
                        )
                        stats[action] += 1

                    logger.info(
                        f"hktvmall 建庫: keyword='{keyword}' page={page} "
                        f"→ {len(products)} 商品"
                    )

                    # 結果數少於頁容量，說明已到最後一頁
                    if len(products) < HKTV_HITS_PER_PAGE:
                        break

        finally:
            await client.close()

        logger.info(
            f"hktvmall 建庫完成: 去重後 {stats['total_fetched']} 商品, "
            f"新增 {stats['new']}, 更新 {stats['updated']}, "
            f"無變化 {stats['unchanged']}"
        )
        return stats

    # ==================== 惠康建庫 ====================

    @staticmethod
    async def _catalog_wellcome(db: AsyncSession) -> dict:
        """
        惠康建庫：Playwright 分類頁 → 提取 URL → HTTP GET JSON-LD

        流程：
        1. 獲取或創建 Wellcome Competitor 記錄
        2. 遍歷分類 ID，Playwright 提取分類頁所有產品 URL
        3. 批量 HTTP GET JSON-LD 取產品詳情
        4. URL 去重後 upsert 到 competitor_products
        """
        settings = get_settings()
        if not settings.agent_browser_enabled:
            logger.warning("惠康建庫: agent_browser 已禁用，跳過")
            return {"skipped": True, "reason": "agent_browser_disabled"}

        competitor = await CatalogService._ensure_competitor(
            db, name="Wellcome 惠康", platform="wellcome",
            base_url="https://www.wellcome.com.hk",
        )

        agent_browser = get_agent_browser_connector()
        http_client = get_wellcome_http_client()
        seen_urls: Set[str] = set()
        stats = {"new": 0, "updated": 0, "unchanged": 0, "total_fetched": 0}

        try:
            for cat_id, cat_name in WELLCOME_CATEGORIES.items():
                all_urls: list[str] = []

                # 分類頁逐頁爬取產品 URL
                for page_num in range(1, WELLCOME_MAX_PAGES + 1):
                    page_url = WELLCOME_CATEGORY_URL.format(
                        category_id=cat_id, page=page_num,
                    )
                    try:
                        urls = await agent_browser.discover_wellcome_products(
                            page_url, max_products=50,
                        )
                        if not urls:
                            break
                        all_urls.extend(urls)
                        logger.info(
                            f"惠康建庫: {cat_name} 第{page_num}頁 → {len(urls)} URLs"
                        )
                    except Exception as e:
                        logger.warning(
                            f"惠康建庫: {cat_name} 第{page_num}頁爬取失敗 - {e}"
                        )
                        break

                if not all_urls:
                    logger.info(f"惠康建庫: {cat_name} 無產品 URL")
                    continue

                # 去重
                unique_urls = [u for u in all_urls if normalize_url(u) not in seen_urls]
                for u in unique_urls:
                    seen_urls.add(normalize_url(u))

                # 批量取 JSON-LD 詳情
                products = await http_client.batch_fetch_products(unique_urls)

                for product in products:
                    if not product.name:
                        continue
                    normalized = normalize_url(product.url)
                    stats["total_fetched"] += 1

                    action = await CatalogService._upsert_competitor_product(
                        db=db,
                        competitor_id=competitor.id,
                        url=normalized,
                        name=product.name,
                        price=product.price,
                        sku=product.product_id,
                        platform="wellcome",
                    )
                    stats[action] += 1

                logger.info(
                    f"惠康建庫: {cat_name} → {len(unique_urls)} URLs, "
                    f"{stats['total_fetched']} 有效商品"
                )

        finally:
            await http_client.close()

        logger.info(
            f"惠康建庫完成: 去重後 {stats['total_fetched']} 商品, "
            f"新增 {stats['new']}, 更新 {stats['updated']}, "
            f"無變化 {stats['unchanged']}"
        )
        return stats

    # ==================== 核心 upsert ====================

    @staticmethod
    async def _upsert_competitor_product(
        db: AsyncSession,
        competitor_id,
        url: str,
        name: str,
        price: Optional[Decimal],
        sku: Optional[str],
        platform: str,
        original_price: Optional[Decimal] = None,
        rating: Optional[Decimal] = None,
        review_count: Optional[int] = None,
        stock_status: Optional[str] = None,
        extra_data: Optional[dict] = None,
    ) -> str:
        """
        插入或更新單個競品商品

        更新策略：
        - 新 URL → 新品入庫，needs_matching=True, last_seen_at=now
        - 已有 URL → 更新價格 + last_seen_at，名稱變更則清空標籤
        - 返回 "new" / "updated" / "unchanged"
        """
        now = utcnow()

        stmt = select(CompetitorProduct).where(CompetitorProduct.url == url)
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing is None:
            # 新品入庫
            cp = CompetitorProduct(
                competitor_id=competitor_id,
                name=name,
                url=url,
                sku=sku,
                is_active=True,
                needs_matching=True,
                last_seen_at=now,
            )
            db.add(cp)
            await db.flush()

            # 順帶建立初始價格快照（Algolia/HTTP 免費取得的價格）
            # flush 省略：build_catalog() 末尾統一 commit，
            # 本輪不會重查此新品快照（seen_urls 保證 URL 唯一性）
            if price is not None:
                db.add(PriceSnapshot(
                    competitor_product_id=cp.id,
                    price=price,
                    original_price=original_price,
                    stock_status=stock_status,
                    rating=rating,
                    review_count=review_count,
                    raw_data=extra_data,
                    currency="HKD",
                ))

            return "new"

        # 已存在：檢查是否有變更
        changed = False

        # 價格更新 → 與最新快照比較，有變則建新快照
        if price is not None:
            latest = await CatalogService._latest_snapshot_price(db, existing.id)
            if latest is None or latest != price:
                db.add(PriceSnapshot(
                    competitor_product_id=existing.id,
                    price=price,
                    original_price=original_price,
                    stock_status=stock_status,
                    rating=rating,
                    review_count=review_count,
                    raw_data=extra_data,
                    currency="HKD",
                ))
                changed = True

        # 名稱變更 → 清空標籤（觸發重新打標）
        if name and existing.name != name:
            existing.name = name
            existing.category_tag = None
            existing.sub_tag = None
            existing.tag_source = None
            existing.needs_matching = True
            changed = True

        # SKU 更新
        if sku and existing.sku != sku:
            existing.sku = sku
            changed = True

        # 無論是否有其他變更，都更新 last_seen_at
        existing.last_seen_at = now
        existing.is_active = True

        return "updated" if changed else "unchanged"

    # ==================== 輔助方法 ====================

    @staticmethod
    async def _latest_snapshot_price(
        db: AsyncSession, competitor_product_id,
    ) -> Optional[Decimal]:
        """獲取最新快照價格（用於增量更新去重）"""
        stmt = (
            select(PriceSnapshot.price)
            .where(PriceSnapshot.competitor_product_id == competitor_product_id)
            .order_by(PriceSnapshot.scraped_at.desc())
            .limit(1)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def _ensure_competitor(
        db: AsyncSession,
        name: str,
        platform: str,
        base_url: str,
    ) -> Competitor:
        """獲取或創建 Competitor 記錄"""
        stmt = select(Competitor).where(Competitor.platform == platform).limit(1)
        result = await db.execute(stmt)
        competitor = result.scalar_one_or_none()

        if competitor is None:
            competitor = Competitor(
                name=name,
                platform=platform,
                base_url=base_url,
                is_active=True,
            )
            db.add(competitor)
            await db.flush()
            logger.info(f"創建 Competitor: {name} ({platform})")

        return competitor
