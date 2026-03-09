# =============================================
# Competitor Builder — Competitor v2
# 競品建庫主引擎：Line A（自家商品→搵競品）+ Line B（商戶→全部生鮮）
# =============================================
# 不 commit — 由 caller 控制事務邊界。

import logging
import re
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional
from uuid import uuid4

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.competitor import (
    Competitor,
    CompetitorProduct,
    PriceSnapshot,
    PriceAlert,
)
from app.models.product import Product, ProductCompetitorMapping
from app.services.algolia_fetcher import AlgoliaFetcher, get_algolia_fetcher
from app.services.ai_filter import AIProductFilter, get_ai_filter
from app.connectors.hktv_api import HKTVProduct
from app.services.stock_prober import probe_stocks_batch

logger = logging.getLogger(__name__)

# 排除關鍵詞（明顯非生鮮）
EXCLUDE_KEYWORDS = frozenset([
    "薯片", "零食", "餅乾", "朱古力", "糖果", "即食麵", "罐頭",
    "醬油", "調味", "湯底", "飲品", "果汁", "啤酒", "紅酒",
    "日用品", "廚具", "清潔", "紙巾", "寵物",
    "貓", "狗", "倉鼠",
])

# 生鮮相關搜索關鍵詞模板
FRESH_SEARCH_KEYWORDS = [
    "和牛", "A5和牛", "日本和牛",
    "三文魚", "三文魚刺身", "吞拿魚",
    "帶子", "海膽", "蝦",
    "急凍牛肉", "急凍魚",
    "日本水果", "日本蜜瓜",
]


class CompetitorBuilder:
    """
    競品建庫主引擎
    
    - build_line_a(): 以自家 23 件商品為起點搜索競品
    - build_line_b(): 以 Tier 1/2 商戶為起點抓取全部生鮮
    - refresh_prices(): 更新所有追蹤中的競品價格
    - discover_new_merchants(): 搜索新的競爭商戶
    """

    def __init__(
        self,
        fetcher: Optional[AlgoliaFetcher] = None,
        ai_filter: Optional[AIProductFilter] = None,
    ):
        self.fetcher = fetcher or get_algolia_fetcher()
        self.ai_filter = ai_filter or get_ai_filter()

    # =============================================
    # Line A: 自家商品 → 搵競品
    # =============================================

    async def build_line_a(
        self,
        db: AsyncSession,
        dry_run: bool = False,
        product_id: Optional[str] = None,
    ) -> dict:
        """
        Line A: 以自家商品為起點，搜索 Algolia 找競品。
        
        流程：
        1. 取自家商品
        2. 每件生成搜索關鍵詞
        3. Algolia 搜索
        4. 規則快速過濾
        5. AI 判斷剩餘
        6. 存入 competitor_products + product_competitor_mapping
        
        Returns:
            {"products_searched": N, "competitors_found": N, "mappings_created": N}
        """
        # 1. 取自家商品
        stmt = select(Product).where(Product.status == "active")
        if product_id:
            stmt = stmt.where(Product.id == product_id)
        result = await db.execute(stmt)
        our_products = result.scalars().all()

        if not our_products:
            logger.warning("無自家商品可搜索")
            return {"products_searched": 0, "competitors_found": 0, "mappings_created": 0}

        logger.info(f"Line A: 搜索 {len(our_products)} 件自家商品的競品")

        total_found = 0
        total_mappings = 0

        for product in our_products:
            keywords = self._generate_keywords(product)
            logger.info(f"  商品: {product.name} → 關鍵詞: {keywords}")

            all_candidates = []
            for kw in keywords:
                hits = await self.fetcher.search_by_keyword(kw, max_results=30)
                all_candidates.extend(hits)

            # 去重（按 SKU）
            seen_skus = set()
            unique_candidates = []
            for p in all_candidates:
                if p.sku not in seen_skus:
                    seen_skus.add(p.sku)
                    unique_candidates.append(p)

            # 規則快速過濾
            after_rules = self._rule_filter(unique_candidates)
            logger.info(
                f"    Algolia: {len(unique_candidates)} → 規則過濾後: {len(after_rules)}"
            )

            if not after_rules:
                continue

            # AI 分類
            ai_input = [
                {"sku": p.sku, "name": p.name}
                for p in after_rules
            ]
            ai_results = await self.ai_filter.classify_products(ai_input)
            
            # 建立 SKU → AI 結果 的映射
            ai_map = {r["sku"]: r for r in ai_results if r.get("relevant")}
            logger.info(f"    AI 過濾: {len(ai_results)} → 相關: {len(ai_map)}")

            if dry_run:
                total_found += len(ai_map)
                for p in after_rules:
                    if p.sku in ai_map:
                        ai = ai_map[p.sku]
                        logger.info(
                            f"    [DRY] {p.name} | ¥{p.price} | "
                            f"{ai.get('category')} | {ai.get('product_type')}"
                        )
                continue

            # 存入 DB
            for hktv_product in after_rules:
                if hktv_product.sku not in ai_map:
                    continue
                ai = ai_map[hktv_product.sku]

                # 找或創建 competitor（按 store_name）
                competitor = await self._get_or_create_competitor(
                    db, hktv_product.store_name or "Unknown"
                )

                # 存入 competitor_products
                cp = await self._upsert_competitor_product(
                    db, competitor, hktv_product, ai
                )

                # 建立 mapping
                mapping = await self._create_mapping(
                    db, product, cp, match_type="ai_matched"
                )
                if mapping:
                    total_mappings += 1

                total_found += 1

        return {
            "products_searched": len(our_products),
            "competitors_found": total_found,
            "mappings_created": total_mappings,
        }

    # =============================================
    # Line B: 商戶 → 全部生鮮
    # =============================================

    async def build_line_b(
        self,
        db: AsyncSession,
        dry_run: bool = False,
    ) -> dict:
        """
        Line B: 以 Tier 1/2 商戶為起點，抓取全部生鮮商品。
        
        用途：市場情報，瞭解對手全部生鮮品類。
        不建立 product_competitor_mapping（那是 Line A 的事）。
        
        Returns:
            {"merchants_scanned": N, "products_found": N, "fresh_products": N}
        """
        stmt = select(Competitor).where(
            Competitor.is_active == True,
            Competitor.tier <= 2,
            Competitor.store_code.isnot(None),
        )
        result = await db.execute(stmt)
        merchants = result.scalars().all()

        if not merchants:
            logger.warning("無 Tier 1/2 商戶（或缺少 store_code）")
            return {"merchants_scanned": 0, "products_found": 0, "fresh_products": 0}

        logger.info(f"Line B: 掃描 {len(merchants)} 間商戶")

        total_products = 0
        total_fresh = 0

        for merchant in merchants:
            products = await self.fetcher.search_by_store_code(
                merchant.store_code, max_results=500
            )
            logger.info(f"  商戶: {merchant.name} ({merchant.store_code}) → {len(products)} 件")

            if not products:
                continue

            total_products += len(products)

            # 規則過濾
            after_rules = self._rule_filter(products)

            # AI 分類
            ai_input = [{"sku": p.sku, "name": p.name} for p in after_rules]
            ai_results = await self.ai_filter.classify_products(ai_input)
            ai_map = {r["sku"]: r for r in ai_results if r.get("relevant")}
            
            logger.info(f"    規則: {len(after_rules)} → AI: {len(ai_map)} 件生鮮")

            if dry_run:
                total_fresh += len(ai_map)
                continue

            # 存入 DB（不建 mapping）
            for hktv_product in after_rules:
                if hktv_product.sku not in ai_map:
                    continue
                ai = ai_map[hktv_product.sku]
                try:
                    await self._upsert_competitor_product(
                        db, merchant, hktv_product, ai
                    )
                except Exception as e:
                    if "connection is closed" in str(e):
                        logger.warning(f"    DB 連線斷開，重新連接...")
                        await db.rollback()
                        await self._upsert_competitor_product(
                            db, merchant, hktv_product, ai
                        )
                    else:
                        raise
                total_fresh += 1

            # Commit per merchant to keep connection alive
            await db.commit()
            logger.info(f"    已提交 {merchant.name}: {len(ai_map)} 件生鮮")

        return {
            "merchants_scanned": len(merchants),
            "products_found": total_products,
            "fresh_products": total_fresh,
        }

    # =============================================
    # 價格更新
    # =============================================

    async def refresh_prices(
        self,
        db: AsyncSession,
    ) -> dict:
        """
        更新所有追蹤中的競品價格。
        
        流程：
        1. 取所有 is_active 的 competitor_products（按商戶分組）
        2. 每間商戶一次 Algolia 查詢取最新價
        3. 與上次 snapshot 比較
        4. 生成 PriceAlert（如有重大變動）
        
        Returns:
            {"products_updated": N, "alerts_generated": N}
        """
        # 取所有活躍競品，按商戶分組
        stmt = (
            select(CompetitorProduct)
            .join(Competitor)
            .where(CompetitorProduct.is_active == True)
            .order_by(Competitor.id)
        )
        result = await db.execute(stmt)
        all_products = result.scalars().all()

        if not all_products:
            return {"products_updated": 0, "alerts_generated": 0}

        # 按 competitor_id 分組
        by_competitor: dict[str, list[CompetitorProduct]] = {}
        for cp in all_products:
            cid = str(cp.competitor_id)
            by_competitor.setdefault(cid, []).append(cp)

        updated = 0
        alerts = 0
        # 追蹤本輪有新 snapshot 的 product IDs
        refreshed_cp_ids: set[str] = set()

        # 取每個商戶的最新商品數據
        for cid, cps in by_competitor.items():
            # 取商戶 store_code
            comp_result = await db.execute(
                select(Competitor).where(Competitor.id == cps[0].competitor_id)
            )
            competitor = comp_result.scalar_one_or_none()
            if not competitor or not competitor.store_code:
                continue

            # Algolia 抓最新
            fresh = await self.fetcher.search_by_store_code(competitor.store_code, max_results=500)
            fresh_by_sku = {p.sku: p for p in fresh}

            for cp in cps:
                hktv = fresh_by_sku.get(cp.sku)
                if not hktv:
                    # 商品可能已下架
                    continue

                # 取上次 snapshot
                prev_stmt = (
                    select(PriceSnapshot)
                    .where(PriceSnapshot.competitor_product_id == cp.id)
                    .order_by(PriceSnapshot.scraped_at.desc())
                    .limit(1)
                )
                prev_result = await db.execute(prev_stmt)
                prev = prev_result.scalar_one_or_none()

                # 建立新 snapshot
                now = datetime.now(timezone.utc).replace(tzinfo=None)
                new_price = hktv.price
                unit_price = None
                if new_price and cp.unit_weight_g and cp.unit_weight_g > 0:
                    unit_price = round(float(new_price) / cp.unit_weight_g * 100, 2)

                snapshot = PriceSnapshot(
                    id=uuid4(),
                    competitor_product_id=cp.id,
                    price=new_price,
                    original_price=hktv.original_price,
                    stock_status=hktv.stock_status or ("in_stock" if hktv.price else None),
                    unit_price_per_100g=Decimal(str(unit_price)) if unit_price else None,
                    scraped_at=now,
                )
                db.add(snapshot)
                updated += 1
                refreshed_cp_ids.add(str(cp.id))

                # 更新 last_scraped_at
                cp.last_scraped_at = now

                # 檢查價格變動 → alert
                if prev and prev.price and new_price and prev.price > 0:
                    change_pct = abs((new_price - prev.price) / prev.price * 100)
                    if change_pct >= 10:
                        alert_type = "price_drop" if new_price < prev.price else "price_increase"
                        alert = PriceAlert(
                            id=uuid4(),
                            competitor_product_id=cp.id,
                            alert_type=alert_type,
                            old_value=str(prev.price),
                            new_value=str(new_price),
                            change_percent=Decimal(str(round(float(change_pct), 2))),
                            created_at=now,
                        )
                        db.add(alert)
                        alerts += 1
                        logger.info(
                            f"  🚨 {alert_type}: {cp.name} "
                            f"${prev.price} → ${new_price} ({change_pct:.1f}%)"
                        )

        # ── Phase 2: Stock Probe（產品頁 SSR）──
        # 批次讀取精確庫存，寫入最新 snapshot
        all_skus = [cp.sku for cps in by_competitor.values() for cp in cps if cp.sku]
        stock_probed = 0
        if all_skus:
            logger.info(f"Stock probe: {len(all_skus)} SKUs...")
            try:
                stock_results = await probe_stocks_batch(
                    all_skus, concurrency=5, delay=0.3
                )
                # 更新 snapshots：本輪有新的直接寫，冇新的建 carry-forward snapshot
                now_stock = datetime.now(timezone.utc).replace(tzinfo=None)
                for cps in by_competitor.values():
                    for cp in cps:
                        if not cp.sku or cp.sku not in stock_results:
                            continue
                        sr = stock_results[cp.sku]
                        if sr.stock_level is None:
                            continue

                        cp_id_str = str(cp.id)

                        if cp_id_str in refreshed_cp_ids:
                            # 本輪有新 snapshot → 直接更新
                            latest_stmt = (
                                select(PriceSnapshot)
                                .where(PriceSnapshot.competitor_product_id == cp.id)
                                .order_by(PriceSnapshot.scraped_at.desc())
                                .limit(1)
                            )
                            latest_result = await db.execute(latest_stmt)
                            latest = latest_result.scalar_one_or_none()
                            if latest:
                                latest.stock_level = sr.stock_level
                                stock_probed += 1
                        else:
                            # Algolia 冇返回此 SKU → 建 carry-forward snapshot
                            # 沿用上次 price，寫入新 stock_level
                            prev_stmt = (
                                select(PriceSnapshot)
                                .where(PriceSnapshot.competitor_product_id == cp.id)
                                .order_by(PriceSnapshot.scraped_at.desc())
                                .limit(1)
                            )
                            prev_result = await db.execute(prev_stmt)
                            prev = prev_result.scalar_one_or_none()

                            carried_price = prev.price if prev else None
                            carried_original = prev.original_price if prev else None
                            carried_unit = prev.unit_price_per_100g if prev else None
                            stock_status = "out_of_stock" if sr.stock_level == 0 else "in_stock"

                            new_snapshot = PriceSnapshot(
                                id=uuid4(),
                                competitor_product_id=cp.id,
                                price=carried_price,
                                original_price=carried_original,
                                stock_status=stock_status,
                                unit_price_per_100g=carried_unit,
                                stock_level=sr.stock_level,
                                scraped_at=now_stock,
                            )
                            db.add(new_snapshot)
                            stock_probed += 1
                            updated += 1
                            cp.last_scraped_at = now_stock
                            logger.debug(
                                f"  📦 carry-forward snapshot: {cp.name} "
                                f"stock={sr.stock_level} (Algolia missed)"
                            )

                        # 庫存歸零告警（兩條路徑共用）
                        if sr.stock_level == 0:
                            # 查本輪最新 snapshot 的 stock_status
                            chk_stmt = (
                                select(PriceSnapshot)
                                .where(PriceSnapshot.competitor_product_id == cp.id)
                                .order_by(PriceSnapshot.scraped_at.desc())
                                .limit(1)
                            )
                            chk_result = await db.execute(chk_stmt)
                            chk = chk_result.scalar_one_or_none()
                            if chk and chk.stock_status != "out_of_stock":
                                chk.stock_status = "out_of_stock"
                            alert = PriceAlert(
                                id=uuid4(),
                                competitor_product_id=cp.id,
                                alert_type="out_of_stock",
                                old_value=None,
                                new_value="0",
                                created_at=now_stock,
                            )
                            db.add(alert)
                            alerts += 1
                            logger.info(f"  🚨 out_of_stock: {cp.name}")

                logger.info(f"Stock probe done: {stock_probed}/{len(all_skus)} updated")
            except Exception as e:
                logger.warning(f"Stock probe failed (non-fatal): {e}")

        return {
            "products_updated": updated,
            "alerts_generated": alerts,
            "stock_probed": stock_probed,
        }

    # =============================================
    # 新商戶發現
    # =============================================

    async def discover_new_merchants(
        self,
        db: AsyncSession,
    ) -> list[dict]:
        """
        搜索新的競爭商戶（週一自動跑）。
        
        用生鮮關鍵詞搜 Algolia，找出未追蹤的商戶。
        
        Returns:
            list of {"store_name": str, "product_count": int, "sample_products": [str]}
        """
        # 已追蹤的商戶名稱
        stmt = select(Competitor.name).where(Competitor.is_active == True)
        result = await db.execute(stmt)
        known_names = {row[0] for row in result.all()}

        # 搜索
        new_stores: dict[str, list[str]] = {}
        for kw in FRESH_SEARCH_KEYWORDS:
            hits = await self.fetcher.search_by_keyword(kw, max_results=30)
            for p in hits:
                store = p.store_name or "Unknown"
                if store in known_names or store == "Unknown":
                    continue
                new_stores.setdefault(store, []).append(p.name)

        return [
            {
                "store_name": store,
                "product_count": len(products),
                "sample_products": products[:5],
            }
            for store, products in sorted(
                new_stores.items(), key=lambda x: len(x[1]), reverse=True
            )
        ]

    # =============================================
    # 內部方法
    # =============================================

    def _generate_keywords(self, product: Product) -> list[str]:
        """從自家商品生成搜索關鍵詞"""
        keywords = []
        
        # 用 name_zh（中文品名）
        if product.name_zh:
            keywords.append(product.name_zh)
        
        # 用 name（主名稱）
        if product.name and product.name != product.name_zh:
            keywords.append(product.name)
        
        # 用 category_tag + sub_tag 組合
        if product.category_tag:
            keywords.append(product.category_tag)
            if product.sub_tag:
                keywords.append(f"{product.category_tag} {product.sub_tag}")

        # 如果都沒有，用主名稱的前 10 個字
        if not keywords and product.name:
            keywords.append(product.name[:10])

        return keywords[:3]  # 最多 3 個關鍵詞，避免過多 API call

    def _rule_filter(self, products: list[HKTVProduct]) -> list[HKTVProduct]:
        """規則快速過濾明顯非生鮮商品"""
        filtered = []
        for p in products:
            name_lower = p.name.lower() if p.name else ""
            # 排除關鍵詞檢查
            if any(kw in name_lower for kw in EXCLUDE_KEYWORDS):
                continue
            filtered.append(p)
        return filtered

    async def _get_or_create_competitor(
        self, db: AsyncSession, store_name: str
    ) -> Competitor:
        """取得或創建競爭商戶"""
        stmt = select(Competitor).where(Competitor.name == store_name)
        result = await db.execute(stmt)
        competitor = result.scalar_one_or_none()

        if competitor:
            return competitor

        competitor = Competitor(
            id=uuid4(),
            name=store_name,
            platform="hktvmall",
            tier=3,  # 自動發現的預設為 Tier 3
            is_active=True,
        )
        db.add(competitor)
        await db.flush()
        return competitor

    async def _upsert_competitor_product(
        self,
        db: AsyncSession,
        competitor: Competitor,
        hktv: HKTVProduct,
        ai: dict,
    ) -> CompetitorProduct:
        """插入或更新競品商品"""
        # 檢查是否已存在
        stmt = select(CompetitorProduct).where(CompetitorProduct.url == hktv.url)
        result = await db.execute(stmt)
        cp = result.scalar_one_or_none()

        now = datetime.now(timezone.utc).replace(tzinfo=None)

        if cp:
            # 更新
            cp.name = hktv.name
            cp.image_url = hktv.image_url
            cp.product_type = ai.get("product_type", "unknown")
            cp.category = ai.get("category")
            cp.unit_weight_g = ai.get("unit_weight_g")
            cp.last_scraped_at = now
            cp.last_seen_at = now
            cp.is_active = True
        else:
            # 新建
            cp = CompetitorProduct(
                id=uuid4(),
                competitor_id=competitor.id,
                name=hktv.name,
                url=hktv.url,
                sku=hktv.sku,
                image_url=hktv.image_url,
                product_type=ai.get("product_type", "unknown"),
                category=ai.get("category"),
                unit_weight_g=ai.get("unit_weight_g"),
                is_active=True,
                last_scraped_at=now,
                last_seen_at=now,
            )
            db.add(cp)
            await db.flush()

        # 建立首次 price snapshot
        unit_price = None
        if hktv.price and cp.unit_weight_g and cp.unit_weight_g > 0:
            unit_price = round(float(hktv.price) / cp.unit_weight_g * 100, 2)

        snapshot = PriceSnapshot(
            id=uuid4(),
            competitor_product_id=cp.id,
            price=hktv.price,
            original_price=hktv.original_price,
            stock_status=hktv.stock_status or ("in_stock" if hktv.price else None),
            unit_price_per_100g=Decimal(str(unit_price)) if unit_price else None,
            scraped_at=now,
        )
        db.add(snapshot)
        return cp

    async def _create_mapping(
        self,
        db: AsyncSession,
        our_product: Product,
        competitor_product: CompetitorProduct,
        match_type: str = "ai_matched",
    ) -> Optional[ProductCompetitorMapping]:
        """建立自家商品與競品的 mapping（去重）"""
        stmt = select(ProductCompetitorMapping).where(
            ProductCompetitorMapping.product_id == our_product.id,
            ProductCompetitorMapping.competitor_product_id == competitor_product.id,
        )
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()
        if existing:
            return None  # 已存在

        mapping = ProductCompetitorMapping(
            id=uuid4(),
            product_id=our_product.id,
            competitor_product_id=competitor_product.id,
            match_type=match_type,
            match_confidence=Decimal("0.80"),
            match_level=2,
            match_reason="AI auto-matched via competitor builder v2",
        )
        db.add(mapping)
        return mapping
