# =============================================
# 智能抓取服務
# =============================================
# 優化 Firecrawl API 消耗，實現：
# 1. URL 緩存 - 避免重複發現
# 2. 增量更新 - 只抓取需要更新的商品
# 3. 優先級調度 - 高頻監控重要商品

import hashlib
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID

from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import (
    CategoryDatabase,
    CategoryProduct,
    CategoryUrlCache,
    ScrapeQuotaUsage,
    CategoryPriceSnapshot
)
from app.connectors.firecrawl import get_firecrawl_connector, ProductInfo
from app.utils.unit_price import calculate_unit_price

logger = logging.getLogger(__name__)


# =============================================
# 配額追蹤器
# =============================================

class QuotaTracker:
    """追蹤 API 配額使用"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self._session_credits = 0

    async def record_usage(
        self,
        operation_type: str,
        url: str,
        category_id: Optional[UUID] = None,
        product_id: Optional[UUID] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        credits_used: int = 1
    ):
        """記錄配額使用"""
        usage = ScrapeQuotaUsage(
            operation_type=operation_type,
            credits_used=credits_used,
            category_id=category_id,
            product_id=product_id,
            success=success,
            error_message=error_message,
            url=url,
        )
        self.db.add(usage)
        self._session_credits += credits_used
        logger.debug(f"API 消耗: {operation_type} = {credits_used} credit(s), URL: {url[:50]}...")

    @property
    def session_credits(self) -> int:
        """本次會話消耗的 credits"""
        return self._session_credits

    async def get_daily_usage(self) -> int:
        """獲取今日使用量"""
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        result = await self.db.execute(
            select(func.sum(ScrapeQuotaUsage.credits_used)).where(
                ScrapeQuotaUsage.created_at >= today
            )
        )
        return result.scalar() or 0

    async def get_monthly_usage(self) -> int:
        """獲取本月使用量"""
        first_day = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        result = await self.db.execute(
            select(func.sum(ScrapeQuotaUsage.credits_used)).where(
                ScrapeQuotaUsage.created_at >= first_day
            )
        )
        return result.scalar() or 0


# =============================================
# URL 緩存管理器
# =============================================

class UrlCacheManager:
    """管理 URL 緩存"""

    def __init__(self, db: AsyncSession):
        self.db = db

    @staticmethod
    def hash_url(url: str) -> str:
        """計算 URL 的 hash"""
        return hashlib.sha256(url.encode()).hexdigest()

    async def get_cached_urls(
        self,
        category_id: UUID,
        only_valid: bool = True,
        limit: Optional[int] = None
    ) -> List[str]:
        """獲取緩存的 URL 列表"""
        query = select(CategoryUrlCache.url).where(
            CategoryUrlCache.category_id == category_id
        )
        if only_valid:
            query = query.where(CategoryUrlCache.is_valid == True)
        if limit:
            query = query.limit(limit)

        result = await self.db.execute(query)
        return [row[0] for row in result.fetchall()]

    async def get_cached_url_count(self, category_id: UUID) -> int:
        """獲取緩存的 URL 數量"""
        result = await self.db.execute(
            select(func.count(CategoryUrlCache.id)).where(
                CategoryUrlCache.category_id == category_id,
                CategoryUrlCache.is_valid == True
            )
        )
        return result.scalar() or 0

    async def cache_urls(
        self,
        category_id: UUID,
        urls: List[str]
    ) -> Tuple[int, int]:
        """
        緩存 URL 列表

        返回：(新增數量, 已存在數量)
        """
        new_count = 0
        existing_count = 0

        for url in urls:
            url_hash = self.hash_url(url)

            # 檢查是否已存在
            existing = await self.db.execute(
                select(CategoryUrlCache).where(
                    CategoryUrlCache.category_id == category_id,
                    CategoryUrlCache.url_hash == url_hash
                )
            )
            if existing.scalar_one_or_none():
                existing_count += 1
                continue

            # 新增緩存
            cache_entry = CategoryUrlCache(
                category_id=category_id,
                url=url,
                url_hash=url_hash,
            )
            self.db.add(cache_entry)
            new_count += 1

        return new_count, existing_count

    async def mark_url_invalid(self, category_id: UUID, url: str, error: str):
        """標記 URL 為無效"""
        url_hash = self.hash_url(url)
        await self.db.execute(
            select(CategoryUrlCache).where(
                CategoryUrlCache.category_id == category_id,
                CategoryUrlCache.url_hash == url_hash
            )
        )
        # 使用 update 語句
        from sqlalchemy import update
        await self.db.execute(
            update(CategoryUrlCache).where(
                CategoryUrlCache.category_id == category_id,
                CategoryUrlCache.url_hash == url_hash
            ).values(
                is_valid=False,
                verification_error=error,
                updated_at=datetime.utcnow()
            )
        )

    async def link_url_to_product(self, category_id: UUID, url: str, product_id: UUID):
        """將 URL 關聯到商品"""
        url_hash = self.hash_url(url)
        from sqlalchemy import update
        await self.db.execute(
            update(CategoryUrlCache).where(
                CategoryUrlCache.category_id == category_id,
                CategoryUrlCache.url_hash == url_hash
            ).values(
                product_id=product_id,
                last_verified_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        )


# =============================================
# 智能抓取服務
# =============================================

class SmartScrapeService:
    """
    智能抓取服務

    核心優化：
    1. URL 緩存 - 避免重複調用 Map API
    2. 增量更新 - 只抓取需要更新的商品
    3. 優先級調度 - 高頻監控重要商品
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.connector = get_firecrawl_connector()
        self.quota_tracker = QuotaTracker(db)
        self.url_cache = UrlCacheManager(db)

    # =============================================
    # URL 發現（帶緩存）
    # =============================================

    async def discover_urls(
        self,
        category: CategoryDatabase,
        max_urls: int = 50,
        force_refresh: bool = False
    ) -> Tuple[List[str], int]:
        """
        發現商品 URL（優先使用緩存）

        返回：(URL 列表, 消耗的 credits)
        """
        category_id = category.id
        credits_used = 0

        # 檢查緩存
        if not force_refresh:
            cached_count = await self.url_cache.get_cached_url_count(category_id)
            if cached_count >= max_urls:
                logger.info(f"使用緩存的 URL（{cached_count} 個），節省 API 調用")
                urls = await self.url_cache.get_cached_urls(category_id, limit=max_urls)
                return urls, 0

        # 需要發現新 URL
        logger.info(f"開始發現 URL: {category.hktv_category_url}")

        try:
            is_hktv = "hktvmall.com" in category.hktv_category_url.lower()

            if is_hktv:
                # HKTVmall 專用發現
                urls = self.connector.discover_hktv_products(
                    category.hktv_category_url,
                    max_products=max_urls,
                    search_pages=3  # 減少分頁數以節省 credits
                )
                # 估算消耗：主頁 + 分頁 + map
                credits_used = 4
            else:
                # 通用發現
                urls = self.connector.discover_product_urls(
                    category.hktv_category_url,
                    keywords=["product", "p/", "pd/", "goods", "item"]
                )
                credits_used = 2

            # 記錄配額使用
            await self.quota_tracker.record_usage(
                operation_type="discover",
                url=category.hktv_category_url,
                category_id=category_id,
                credits_used=credits_used
            )

            # 緩存發現的 URL
            new_count, existing_count = await self.url_cache.cache_urls(category_id, urls)
            logger.info(f"URL 發現完成: {len(urls)} 個，新增緩存 {new_count} 個，已存在 {existing_count} 個")

            return urls[:max_urls], credits_used

        except Exception as e:
            logger.error(f"URL 發現失敗: {e}")
            await self.quota_tracker.record_usage(
                operation_type="discover",
                url=category.hktv_category_url,
                category_id=category_id,
                success=False,
                error_message=str(e),
                credits_used=credits_used
            )
            # 嘗試返回緩存的 URL
            cached_urls = await self.url_cache.get_cached_urls(category_id, limit=max_urls)
            return cached_urls, credits_used

    # =============================================
    # 增量更新
    # =============================================

    async def get_products_to_update(
        self,
        category_id: UUID,
        limit: int = 50
    ) -> List[CategoryProduct]:
        """
        獲取需要更新的商品列表

        優先級排序：
        1. 高優先級商品（monitor_priority = 'high'）
        2. 超過更新頻率的商品
        3. 從未抓取過的商品
        """
        now = datetime.utcnow()

        # 查詢需要更新的商品
        result = await self.db.execute(
            select(CategoryProduct).where(
                CategoryProduct.category_id == category_id,
                CategoryProduct.is_monitored == True,
                or_(
                    # 高優先級商品，超過 24 小時未更新
                    and_(
                        CategoryProduct.monitor_priority == "high",
                        or_(
                            CategoryProduct.last_updated_at == None,
                            CategoryProduct.last_updated_at < now - timedelta(hours=24)
                        )
                    ),
                    # 普通優先級，超過設定的更新頻率
                    and_(
                        CategoryProduct.monitor_priority == "normal",
                        or_(
                            CategoryProduct.last_updated_at == None,
                            CategoryProduct.last_updated_at < now - timedelta(hours=168)  # 7 天
                        )
                    ),
                    # 低優先級，超過 30 天未更新
                    and_(
                        CategoryProduct.monitor_priority == "low",
                        or_(
                            CategoryProduct.last_updated_at == None,
                            CategoryProduct.last_updated_at < now - timedelta(days=30)
                        )
                    )
                )
            ).order_by(
                # 高優先級優先
                CategoryProduct.monitor_priority.desc(),
                # 最久未更新的優先
                CategoryProduct.last_updated_at.asc().nullsfirst()
            ).limit(limit)
        )

        return list(result.scalars().all())

    async def get_new_urls_to_scrape(
        self,
        category_id: UUID,
        limit: int = 20
    ) -> List[str]:
        """獲取尚未抓取的新 URL"""
        result = await self.db.execute(
            select(CategoryUrlCache.url).where(
                CategoryUrlCache.category_id == category_id,
                CategoryUrlCache.is_valid == True,
                CategoryUrlCache.product_id == None  # 尚未關聯商品
            ).limit(limit)
        )
        return [row[0] for row in result.fetchall()]

    # =============================================
    # 智能抓取執行
    # =============================================

    async def scrape_product(
        self,
        url: str,
        category_id: UUID,
        product_id: Optional[UUID] = None
    ) -> Tuple[Optional[ProductInfo], int]:
        """
        抓取單個商品

        返回：(商品信息, 消耗的 credits)
        """
        try:
            info = self.connector.extract_product_info(url)

            await self.quota_tracker.record_usage(
                operation_type="scrape",
                url=url,
                category_id=category_id,
                product_id=product_id,
                credits_used=1
            )

            return info, 1

        except Exception as e:
            logger.error(f"抓取失敗 {url}: {e}")
            await self.quota_tracker.record_usage(
                operation_type="scrape",
                url=url,
                category_id=category_id,
                product_id=product_id,
                success=False,
                error_message=str(e),
                credits_used=1
            )
            return None, 1

    async def smart_update_category(
        self,
        category: CategoryDatabase,
        max_new_products: int = 10,
        max_updates: int = 20
    ) -> Dict[str, Any]:
        """
        智能更新類別

        步驟：
        1. 使用緩存的 URL 發現新商品
        2. 更新需要刷新的現有商品
        3. 記錄配額使用

        返回：更新統計
        """
        category_id = category.id
        stats = {
            "new_products": 0,
            "updated_products": 0,
            "failed": 0,
            "credits_used": 0,
            "errors": []
        }

        # ==================== 階段 1: 發現新 URL ====================
        urls, discover_credits = await self.discover_urls(
            category,
            max_urls=max_new_products + max_updates,
            force_refresh=False
        )
        stats["credits_used"] += discover_credits

        # ==================== 階段 2: 抓取新商品 ====================
        new_urls = await self.get_new_urls_to_scrape(category_id, limit=max_new_products)

        for url in new_urls:
            info, credits = await self.scrape_product(url, category_id)
            stats["credits_used"] += credits

            if info:
                # 創建新商品
                product = await self._create_product(category_id, url, info)
                if product:
                    stats["new_products"] += 1
                    # 關聯 URL 緩存
                    await self.url_cache.link_url_to_product(category_id, url, product.id)
            else:
                stats["failed"] += 1
                await self.url_cache.mark_url_invalid(category_id, url, "抓取失敗")

        # ==================== 階段 3: 更新現有商品 ====================
        products_to_update = await self.get_products_to_update(category_id, limit=max_updates)

        for product in products_to_update:
            info, credits = await self.scrape_product(product.url, category_id, product.id)
            stats["credits_used"] += credits

            if info:
                await self._update_product(product, info)
                stats["updated_products"] += 1
            else:
                stats["failed"] += 1
                product.scrape_error_count = (product.scrape_error_count or 0) + 1
                # 連續失敗 5 次，降低優先級
                if product.scrape_error_count >= 5:
                    product.is_monitored = False
                    logger.warning(f"商品 {product.name} 連續失敗 5 次，已停止監控")

        # ==================== 提交變更 ====================
        await self.db.commit()

        # 更新類別統計
        await self._update_category_stats(category)

        logger.info(
            f"智能更新完成: 新增 {stats['new_products']}, "
            f"更新 {stats['updated_products']}, "
            f"失敗 {stats['failed']}, "
            f"消耗 {stats['credits_used']} credits"
        )

        return stats

    # =============================================
    # 輔助方法
    # =============================================

    async def _create_product(
        self,
        category_id: UUID,
        url: str,
        info: ProductInfo
    ) -> Optional[CategoryProduct]:
        """創建新商品"""
        try:
            unit_price = None
            unit_type = "per_100g"
            if info.price:
                calc_result = calculate_unit_price(info.price, info.name)
                if calc_result[0]:
                    unit_price, unit_type = calc_result

            product = CategoryProduct(
                category_id=category_id,
                name=info.name,
                url=url,
                sku=info.sku,
                brand=info.brand,
                price=info.price,
                original_price=info.original_price,
                discount_percent=info.discount_percent,
                unit_price=unit_price,
                unit_type=unit_type,
                stock_status=info.stock_status,
                is_available=info.stock_status != "out_of_stock" if info.stock_status else True,
                rating=info.rating,
                review_count=info.review_count,
                image_url=info.image_url,
                attributes={},
                monitor_priority="normal",
                is_monitored=True,
            )
            self.db.add(product)
            await self.db.flush()

            # 創建價格快照
            snapshot = CategoryPriceSnapshot(
                category_product_id=product.id,
                price=info.price,
                original_price=info.original_price,
                discount_percent=info.discount_percent,
                unit_price=unit_price,
                stock_status=info.stock_status,
                is_available=product.is_available,
            )
            self.db.add(snapshot)

            return product

        except Exception as e:
            logger.error(f"創建商品失敗: {e}")
            return None

    async def _update_product(self, product: CategoryProduct, info: ProductInfo):
        """更新現有商品"""
        old_price = product.price

        product.name = info.name
        product.price = info.price
        product.original_price = info.original_price
        product.discount_percent = info.discount_percent
        product.stock_status = info.stock_status
        product.is_available = info.stock_status != "out_of_stock" if info.stock_status else True
        product.rating = info.rating
        product.review_count = info.review_count
        product.image_url = info.image_url
        product.brand = info.brand
        product.sku = info.sku
        product.last_updated_at = datetime.utcnow()
        product.scrape_error_count = 0  # 重置錯誤計數

        # 計算單位價格
        if info.price:
            calc_result = calculate_unit_price(info.price, info.name)
            if calc_result[0]:
                product.unit_price, product.unit_type = calc_result

        # 檢測價格變動
        if old_price and info.price and old_price != info.price:
            product.last_price_change_at = datetime.utcnow()
            # 計算價格波動率
            change_percent = abs((info.price - old_price) / old_price * 100)
            product.price_volatility = Decimal(str(round(float(change_percent), 2)))

        # 創建價格快照
        snapshot = CategoryPriceSnapshot(
            category_product_id=product.id,
            price=info.price,
            original_price=info.original_price,
            discount_percent=info.discount_percent,
            unit_price=product.unit_price,
            stock_status=info.stock_status,
            is_available=product.is_available,
        )
        self.db.add(snapshot)

    async def _update_category_stats(self, category: CategoryDatabase):
        """更新類別統計"""
        result = await self.db.execute(
            select(func.count(CategoryProduct.id)).where(
                CategoryProduct.category_id == category.id
            )
        )
        category.total_products = result.scalar() or 0
        category.last_scraped_at = datetime.utcnow()


# =============================================
# 工廠函數
# =============================================

def get_smart_scrape_service(db: AsyncSession) -> SmartScrapeService:
    """獲取智能抓取服務實例"""
    return SmartScrapeService(db)
