# =============================================
# Product-Driven Competitor Discovery
# 以自家商品為起點，搵 HKTVmall 上嘅競品
# =============================================
# 舊設計問題：固定關鍵詞盲搜 → 4,295 件無關競品入庫
# 新設計：以 23 件自家商品的 category_tag + sub_tag 為起點
#         → 品類過濾 → 入庫即 mapping → stock_status
#
# 預期效果：4,295 → ~200-400 件真正相關競品

import re
import logging
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.connectors.hktv_api import HKTVApiClient, HKTVProduct
from app.models.competitor import Competitor, CompetitorProduct, PriceSnapshot
from app.models.product import Product, ProductCompetitorMapping
from app.models.database import utcnow

logger = logging.getLogger(__name__)


# =============================================
# 過濾規則
# =============================================

# Algolia catNameZh 白名單：至少命中其中一個才保留
FOOD_CATEGORIES = frozenset({
    "急凍食品", "肉類", "海鮮", "魚類", "蝦蟹貝類",
    "超級市場", "新鮮食品", "凍肉", "刺身",
    "牛肉", "豬肉", "雞肉", "羊肉",
    "急凍肉類", "急凍海鮮", "魚", "肉",
})

# 商品名黑名單：命中任何一個即排除
NON_FOOD_KEYWORDS = frozenset({
    "拉麵", "湯底", "醬", "調味", "零食",
    "薯片", "餅乾", "糖果", "飲品", "杯麵",
    "貓", "狗", "寵物",
    "清潔", "廚具", "餐具",
    "咖喱粉", "即食", "罐頭", "泡麵",
})

# 自家店鋪名（排除自家商品）
OWN_STORE_NAMES = frozenset({"GoGoJap", "GoGoFoods", "gogojap", "gogofoods"})

# Algolia 搜索參數
MAX_HITS_PER_QUERY = 50
MAX_PAGES_PER_QUERY = 2


# =============================================
# 統計
# =============================================

@dataclass
class FinderStats:
    products_processed: int = 0
    queries_sent: int = 0
    hits_total: int = 0
    hits_relevant: int = 0
    hits_filtered: int = 0
    new_competitors: int = 0
    updated_competitors: int = 0
    new_mappings: int = 0
    skipped_existing_mappings: int = 0


# =============================================
# ProductCompetitorFinder
# =============================================

class ProductCompetitorFinder:
    """
    以自家商品為起點，搵 HKTVmall 上嘅競品

    流程：
    1. 讀取所有有 category_tag 的自家商品
    2. 每件商品 → 生成搜索 queries（精確 → sub_tag → category）
    3. Algolia 搜索 → 品類過濾 → upsert competitor_products
    4. 即時建立 product_competitor_mapping（入庫即 mapping）
    5. 記錄 stock_status（從 Algolia hasStock 解析）
    """

    def __init__(self):
        self.client = HKTVApiClient()

    async def close(self):
        await self.client.close()

    # ==================== 公開介面 ====================

    async def find_all(self, db: AsyncSession, dry_run: bool = False) -> dict:
        """
        全量搜索所有有 tag 的自家商品競品

        Args:
            db: 資料庫 session
            dry_run: True 則只統計、不寫入 DB
        """
        stmt = select(Product).where(
            Product.status == "active",
            Product.category_tag.isnot(None),
        )
        result = await db.execute(stmt)
        products = result.scalars().all()

        if not products:
            logger.warning("find_all: 找不到有 category_tag 的自家商品")
            return {"error": "no_products_with_tags", "count": 0}

        logger.info(f"find_all: 共 {len(products)} 件自家商品，開始搜索競品")
        competitor = await self._ensure_competitor(db)
        stats = FinderStats()
        per_product = []

        try:
            for i, product in enumerate(products, 1):
                product_result = await self._find_for_product(
                    db, product, competitor, stats, dry_run
                )
                per_product.append(product_result)
                stats.products_processed += 1
                logger.info(
                    f"[{i}/{len(products)}] {product.name[:30]}: "
                    f"{product_result['relevant']}/{product_result['total']} 相關"
                )

            if not dry_run:
                await db.commit()
                logger.info("find_all: 已 commit")

        finally:
            await self.close()

        return {
            "products_processed": stats.products_processed,
            "queries_sent": stats.queries_sent,
            "hits_total": stats.hits_total,
            "hits_relevant": stats.hits_relevant,
            "hits_filtered": stats.hits_filtered,
            "new_competitors": stats.new_competitors,
            "updated_competitors": stats.updated_competitors,
            "new_mappings": stats.new_mappings,
            "skipped_existing_mappings": stats.skipped_existing_mappings,
            "dry_run": dry_run,
            "per_product": per_product,
        }

    async def find_for_product(
        self, db: AsyncSession, product_id, dry_run: bool = False
    ) -> dict:
        """搜索單件自家商品的競品"""
        stmt = select(Product).where(Product.id == product_id)
        result = await db.execute(stmt)
        product = result.scalar_one_or_none()

        if not product:
            return {"error": "product_not_found"}

        competitor = await self._ensure_competitor(db)
        stats = FinderStats()

        try:
            result = await self._find_for_product(db, product, competitor, stats, dry_run)
            if not dry_run:
                await db.commit()
        finally:
            await self.close()

        result["stats"] = {
            "new_competitors": stats.new_competitors,
            "updated_competitors": stats.updated_competitors,
            "new_mappings": stats.new_mappings,
        }
        return result

    # ==================== 核心邏輯 ====================

    async def _find_for_product(
        self,
        db: AsyncSession,
        product: Product,
        competitor: Competitor,
        stats: FinderStats,
        dry_run: bool,
    ) -> dict:
        """搜索單件商品的競品，建立 mapping"""
        queries = self._generate_queries(product)
        seen_urls: set[str] = set()
        relevant: list[HKTVProduct] = []
        total_hits = 0
        filtered_hits = 0

        for query in queries:
            for page in range(MAX_PAGES_PER_QUERY):
                hits = await self.client.search_products(
                    keyword=query,
                    page_size=MAX_HITS_PER_QUERY,
                    page=page,
                )
                stats.queries_sent += 1

                if not hits:
                    break

                for hit in hits:
                    total_hits += 1
                    if not hit.url or hit.url in seen_urls:
                        continue
                    seen_urls.add(hit.url)

                    if not self._is_relevant(hit):
                        filtered_hits += 1
                        continue

                    relevant.append(hit)

                if len(hits) < MAX_HITS_PER_QUERY:
                    break  # 最後一頁

        stats.hits_total += total_hits
        stats.hits_relevant += len(relevant)
        stats.hits_filtered += filtered_hits

        # 入庫 + 建 mapping
        if not dry_run:
            for hit in relevant:
                match_level = self._calculate_match_level(product, hit)
                cp = await self._upsert_competitor_product(
                    db, competitor.id, hit, stats
                )
                if cp:
                    await self._ensure_mapping(
                        db, product.id, cp.id, match_level, stats
                    )

        return {
            "product_id": str(product.id),
            "product_name": product.name,
            "category_tag": product.category_tag,
            "sub_tag": product.sub_tag,
            "queries": queries,
            "total": total_hits,
            "relevant": len(relevant),
            "filtered": filtered_hits,
        }

    def _generate_queries(self, product: Product) -> list[str]:
        """
        基於商品 tag 生成搜索 queries（精確 → 細分 → 大類）

        例：宮崎A5和牛西冷 200g → ["宮崎A5和牛西冷", "和牛", "急凍牛"]
        """
        queries = []

        # Level 1：精確名字（去掉重量/規格後綴）
        if product.name:
            clean = re.sub(
                r'[\d,.]+\s*[gGkKmMlL個件片塊包盒]+.*$',
                '', product.name
            ).strip()
            if clean and len(clean) > 2:
                queries.append(clean)

        # Level 2：sub_tag（+ 附加關鍵詞）— 跳過「其他」
        if product.sub_tag and product.sub_tag != "其他":
            queries.append(product.sub_tag)
            if product.name:
                # 帶產地/品級的精準搜索
                for kw in ["A5", "A4", "宮崎", "鹿兒島", "北海道"]:
                    if kw in product.name:
                        queries.append(f"{kw} {product.sub_tag}")
                        break  # 只加一個

        # Level 3：category_tag（大類）
        if product.category_tag:
            queries.append(f"急凍{product.category_tag}")
            # 避免 sub_tag 與 category_tag 重複
            if product.category_tag != product.sub_tag:
                queries.append(product.category_tag)

        # 去重保序
        return list(dict.fromkeys(q for q in queries if q))

    def _is_relevant(self, hit: HKTVProduct) -> bool:
        """
        品類過濾：判斷競品是否為相關食材

        排除：寵物食品、零食、加工品、自家商品
        保留：肉類、海鮮等生鮮食材
        """
        name = hit.name or ""

        # 名字黑名單
        for kw in NON_FOOD_KEYWORDS:
            if kw in name:
                return False

        # 排除自家店鋪
        store = hit.store_name or ""
        if any(own.lower() in store.lower() for own in OWN_STORE_NAMES):
            return False

        # catNameZh 白名單（有分類才做白名單過濾）
        if hit.cat_name_zh:
            cats = hit.cat_name_zh if isinstance(hit.cat_name_zh, list) else [str(hit.cat_name_zh)]
            cat_text = " ".join(cats)
            if not any(fc in cat_text for fc in FOOD_CATEGORIES):
                return False

        return True

    def _calculate_match_level(self, product: Product, hit: HKTVProduct) -> int:
        """
        計算 match_level：
        1 = 直接替代品（名字高度相似 + 同產地/品級）
        2 = 近似競品（同 sub_tag）
        3 = 品類競品（同 category_tag）
        """
        hit_name = hit.name or ""

        # Level 1：sub_tag 命中 + 附加關鍵詞（產地/品級）匹配
        if product.sub_tag and product.sub_tag in hit_name:
            if product.name:
                for kw in ["A5", "A4", "宮崎", "鹿兒島", "北海道", "三文魚", "吞拿魚", "甜蝦"]:
                    if kw in product.name and kw in hit_name:
                        return 1  # 直接替代
            return 2  # 同 sub_tag

        # Level 2：sub_tag 部分命中
        if product.sub_tag:
            parts = [p for p in product.sub_tag.split() if len(p) > 1]
            if any(p in hit_name for p in parts):
                return 2

        return 3  # 品類競品

    # ==================== DB 操作 ====================

    async def _upsert_competitor_product(
        self,
        db: AsyncSession,
        competitor_id,
        hit: HKTVProduct,
        stats: FinderStats,
    ) -> Optional[CompetitorProduct]:
        """插入或更新競品商品，回傳 DB record"""
        now = utcnow()

        stmt = select(CompetitorProduct).where(CompetitorProduct.url == hit.url)
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing is None:
            cp = CompetitorProduct(
                competitor_id=competitor_id,
                name=hit.name,
                url=hit.url,
                sku=hit.sku,
                image_url=hit.image_url,
                is_active=True,
                needs_matching=False,  # 入庫即 mapping，不需再跑 matcher
                last_seen_at=now,
            )
            db.add(cp)
            await db.flush()  # 取得 cp.id

            if hit.price is not None:
                db.add(PriceSnapshot(
                    competitor_product_id=cp.id,
                    price=hit.price,
                    original_price=hit.original_price,
                    stock_status=hit.stock_status,
                    review_count=hit.review_count,
                    currency="HKD",
                ))

            stats.new_competitors += 1
            return cp

        # 已存在：更新 last_seen_at + is_active
        existing.last_seen_at = now
        existing.is_active = True

        # 名字變更 → 更新
        if hit.name and existing.name != hit.name:
            existing.name = hit.name

        # 價格快照（有變化才建新快照）
        if hit.price is not None:
            latest_stmt = (
                select(PriceSnapshot.price)
                .where(PriceSnapshot.competitor_product_id == existing.id)
                .order_by(PriceSnapshot.scraped_at.desc())
                .limit(1)
            )
            latest_result = await db.execute(latest_stmt)
            latest_price = latest_result.scalar_one_or_none()

            if latest_price is None or latest_price != hit.price:
                db.add(PriceSnapshot(
                    competitor_product_id=existing.id,
                    price=hit.price,
                    original_price=hit.original_price,
                    stock_status=hit.stock_status,
                    review_count=hit.review_count,
                    currency="HKD",
                ))

        stats.updated_competitors += 1
        return existing

    async def _ensure_mapping(
        self,
        db: AsyncSession,
        product_id,
        competitor_product_id,
        match_level: int,
        stats: FinderStats,
    ):
        """建立 product_competitor_mapping（已存在則跳過）"""
        stmt = select(ProductCompetitorMapping).where(
            ProductCompetitorMapping.product_id == product_id,
            ProductCompetitorMapping.competitor_product_id == competitor_product_id,
        )
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            stats.skipped_existing_mappings += 1
            return

        confidence_map = {1: Decimal("0.90"), 2: Decimal("0.70"), 3: Decimal("0.50")}
        db.add(ProductCompetitorMapping(
            product_id=product_id,
            competitor_product_id=competitor_product_id,
            match_level=match_level,
            match_confidence=confidence_map.get(match_level, Decimal("0.50")),
            match_reason=f"auto:product_competitor_finder:L{match_level}",
            is_verified=False,
        ))
        stats.new_mappings += 1

    async def _ensure_competitor(self, db: AsyncSession) -> Competitor:
        """獲取或創建 HKTVmall Competitor 記錄"""
        stmt = select(Competitor).where(Competitor.platform == "hktvmall").limit(1)
        result = await db.execute(stmt)
        competitor = result.scalar_one_or_none()

        if competitor is None:
            competitor = Competitor(
                name="HKTVmall",
                platform="hktvmall",
                base_url="https://www.hktvmall.com",
                is_active=True,
            )
            db.add(competitor)
            await db.flush()
            logger.info("創建 HKTVmall Competitor 記錄")

        return competitor
