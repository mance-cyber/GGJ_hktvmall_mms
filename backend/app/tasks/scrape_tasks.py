# =============================================
# 爬取任務（純 async，無 Celery 依賴）
# =============================================

import asyncio
import logging
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional

from app.config import get_settings

logger = logging.getLogger(__name__)


# =============================================
# 單個競爭對手爬取
# =============================================

async def scrape_competitor_async(competitor_id: str):
    """
    爬取單個競爭對手的所有商品

    Args:
        competitor_id: 競爭對手 UUID
    """
    from app.models.database import async_session_maker
    from app.models.competitor import CompetitorProduct, PriceSnapshot
    from app.models.system import ScrapeLog
    from app.connectors.firecrawl import get_firecrawl_connector
    from sqlalchemy import select

    connector = get_firecrawl_connector()
    settings = get_settings()

    async with async_session_maker() as db:
        log = ScrapeLog(
            task_id=str(uuid4()),
            task_type="competitor_scrape",
            competitor_id=UUID(competitor_id),
            status="running",
            started_at=datetime.utcnow(),
        )
        db.add(log)
        await db.flush()

        try:
            result = await db.execute(
                select(CompetitorProduct).where(
                    CompetitorProduct.competitor_id == UUID(competitor_id),
                    CompetitorProduct.is_active == True
                )
            )
            products = result.scalars().all()
            log.products_total = len(products)

            for product in products:
                try:
                    info = connector.extract_product_info(product.url)

                    last_snapshot_result = await db.execute(
                        select(PriceSnapshot)
                        .where(PriceSnapshot.competitor_product_id == product.id)
                        .order_by(PriceSnapshot.scraped_at.desc())
                        .limit(1)
                    )
                    last_snapshot = last_snapshot_result.scalar_one_or_none()

                    snapshot = PriceSnapshot(
                        competitor_product_id=product.id,
                        price=info.price,
                        original_price=info.original_price,
                        discount_percent=info.discount_percent,
                        stock_status=info.stock_status,
                        rating=info.rating,
                        review_count=info.review_count,
                        promotion_text=info.promotion_text,
                        raw_data=info.raw_data,
                    )
                    db.add(snapshot)

                    if info.name and info.name != "未知商品":
                        product.name = info.name
                    if info.image_url:
                        product.image_url = info.image_url
                    if info.sku:
                        product.sku = info.sku
                    product.last_scraped_at = datetime.utcnow()
                    product.scrape_error = None

                    if last_snapshot and info.price:
                        await _check_price_alert(
                            db, product, last_snapshot, info, settings.price_alert_threshold
                        )

                    log.products_scraped += 1

                except Exception as e:
                    product.scrape_error = str(e)
                    log.products_failed += 1
                    if log.errors is None:
                        log.errors = []
                    log.errors.append({
                        "product_id": str(product.id),
                        "error": str(e)
                    })

            log.status = "success" if log.products_failed == 0 else "partial"
            log.completed_at = datetime.utcnow()
            log.duration_seconds = int((log.completed_at - log.started_at).total_seconds())

            await db.commit()

            # 觸發 Agent 事件
            try:
                from app.agents.hooks import on_scrape_completed
                await on_scrape_completed(
                    competitor_id=competitor_id,
                    alerts_created=log.products_scraped,
                    products_scraped=log.products_scraped,
                )
            except Exception as hook_err:
                logger.warning(f"Agent hook 失敗: {hook_err}")

        except Exception as e:
            log.status = "failed"
            log.completed_at = datetime.utcnow()
            if log.errors is None:
                log.errors = []
            log.errors.append({"error": str(e)})
            await db.commit()
            raise


async def _check_price_alert(db, product, last_snapshot, info, threshold):
    """檢查並創建價格警報"""
    from app.models.competitor import PriceAlert
    from decimal import Decimal

    old_price = last_snapshot.price
    new_price = info.price
    old_stock = last_snapshot.stock_status
    new_stock = info.stock_status

    if old_price and new_price and old_price > 0:
        change_percent = (new_price - old_price) / old_price * 100

        if abs(change_percent) >= threshold:
            alert_type = "price_drop" if change_percent < 0 else "price_increase"
            alert = PriceAlert(
                competitor_product_id=product.id,
                alert_type=alert_type,
                old_value=str(old_price),
                new_value=str(new_price),
                change_percent=Decimal(str(round(change_percent, 2))),
            )
            db.add(alert)

            # 觸發告警工作流（fire-and-forget）
            from app.tasks.workflow_tasks import execute_alert_workflow_async

            alert_data = {
                "product_id": str(product.id),
                "product_name": product.name or info.name or "未知產品",
                "old_price": float(old_price),
                "new_price": float(new_price),
                "change_percent": round(change_percent, 2),
                "category_id": str(product.category_id) if hasattr(product, 'category_id') and product.category_id else None,
                "alert_type": alert_type,
                "competitor_id": str(product.competitor_id) if product.competitor_id else None,
            }

            asyncio.create_task(execute_alert_workflow_async(alert_data))

    if old_stock and new_stock and old_stock != new_stock:
        if old_stock == "in_stock" and new_stock == "out_of_stock":
            alert = PriceAlert(
                competitor_product_id=product.id,
                alert_type="out_of_stock",
                old_value=old_stock,
                new_value=new_stock,
            )
            db.add(alert)
        elif old_stock == "out_of_stock" and new_stock == "in_stock":
            alert = PriceAlert(
                competitor_product_id=product.id,
                alert_type="back_in_stock",
                old_value=old_stock,
                new_value=new_stock,
            )
            db.add(alert)


# =============================================
# 所有競爭對手
# =============================================

async def scrape_all_competitors_async():
    """爬取所有活躍競爭對手（為每個競爭對手創建背景任務）"""
    from app.models.database import async_session_maker
    from app.models.competitor import Competitor
    from sqlalchemy import select

    async with async_session_maker() as db:
        result = await db.execute(
            select(Competitor.id).where(Competitor.is_active == True)
        )
        competitor_ids = result.scalars().all()

        for competitor_id in competitor_ids:
            asyncio.create_task(scrape_competitor_async(str(competitor_id)))

        return {"competitors_queued": len(competitor_ids)}


# =============================================
# 單個商品
# =============================================

async def scrape_single_product_async(product_id: str):
    """爬取單個商品"""
    from app.models.database import async_session_maker
    from app.models.competitor import CompetitorProduct, PriceSnapshot
    from app.connectors.firecrawl import get_firecrawl_connector
    from sqlalchemy import select

    connector = get_firecrawl_connector()

    async with async_session_maker() as db:
        result = await db.execute(
            select(CompetitorProduct).where(CompetitorProduct.id == UUID(product_id))
        )
        product = result.scalar_one_or_none()

        if not product:
            return {"error": "商品不存在"}

        try:
            info = connector.extract_product_info(product.url)

            snapshot = PriceSnapshot(
                competitor_product_id=product.id,
                price=info.price,
                original_price=info.original_price,
                discount_percent=info.discount_percent,
                stock_status=info.stock_status,
                rating=info.rating,
                review_count=info.review_count,
                raw_data=info.raw_data,
            )
            db.add(snapshot)

            if info.name and info.name != "未知商品":
                product.name = info.name
            if info.image_url:
                product.image_url = info.image_url
            product.last_scraped_at = datetime.utcnow()
            product.scrape_error = None

            await db.commit()
            return {"success": True, "product_id": product_id}

        except Exception as e:
            product.scrape_error = str(e)
            await db.commit()
            return {"error": str(e)}


# =============================================
# 分級監測策略
# =============================================

async def scrape_by_priority_async(priorities: list[str] = None):
    """
    按優先級爬取競品商品

    Args:
        priorities: ["A", "B", "C"] 等
    """
    if priorities is None:
        priorities = ["A", "B", "C"]

    from app.models.database import async_session_maker
    from app.models.product import Product, ProductCompetitorMapping
    from app.models.competitor import CompetitorProduct
    from sqlalchemy import select, distinct

    async with async_session_maker() as db:
        stmt = (
            select(distinct(CompetitorProduct.competitor_id))
            .join(ProductCompetitorMapping, ProductCompetitorMapping.competitor_product_id == CompetitorProduct.id)
            .join(Product, Product.id == ProductCompetitorMapping.product_id)
            .where(
                Product.monitoring_priority.in_(priorities),
                CompetitorProduct.is_active == True
            )
        )

        result = await db.execute(stmt)
        competitor_ids = result.scalars().all()

        for competitor_id in competitor_ids:
            asyncio.create_task(scrape_competitor_async(str(competitor_id)))

        return {
            "priorities": priorities,
            "competitors_queued": len(competitor_ids),
            "message": f"已為 {len(competitor_ids)} 個競爭對手創建爬取任務（優先級: {', '.join(priorities)}）"
        }


async def auto_classify_monitoring_priority_async():
    """自動分類商品監測優先級（基於利潤率）"""
    from app.models.database import async_session_maker
    from app.models.product import Product, ProductCompetitorMapping
    from sqlalchemy import select, func

    async with async_session_maker() as db:
        result = await db.execute(select(Product))
        products = result.scalars().all()

        classified_count = {"A": 0, "B": 0, "C": 0}

        for product in products:
            if not product.price or not product.cost or product.cost == 0:
                product.monitoring_priority = "C"
                classified_count["C"] += 1
                continue

            profit_margin = float((product.price - product.cost) / product.cost * 100)

            mapping_result = await db.execute(
                select(func.count())
                .select_from(ProductCompetitorMapping)
                .where(ProductCompetitorMapping.product_id == product.id)
            )
            has_competitors = (mapping_result.scalar() or 0) > 0

            if profit_margin > 50 and has_competitors:
                product.monitoring_priority = "A"
                classified_count["A"] += 1
            elif profit_margin >= 20:
                product.monitoring_priority = "B"
                classified_count["B"] += 1
            else:
                product.monitoring_priority = "C"
                classified_count["C"] += 1

        await db.commit()

        return {
            "total_products": len(products),
            "classified": classified_count,
            "message": f"已分類 {len(products)} 個商品：A級 {classified_count['A']} 個，B級 {classified_count['B']} 個，C級 {classified_count['C']} 個"
        }
