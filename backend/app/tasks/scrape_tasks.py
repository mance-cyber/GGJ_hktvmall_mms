# =============================================
# 爬取任務
# =============================================

import asyncio
from datetime import datetime
from uuid import UUID
from typing import Optional

from app.tasks.celery_app import celery_app
from app.config import get_settings


def run_async(coro):
    """在同步環境中運行異步代碼"""
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coro)


@celery_app.task(bind=True, name="app.tasks.scrape_tasks.scrape_competitor")
def scrape_competitor(self, competitor_id: str):
    """
    爬取單個競爭對手的所有商品

    Args:
        competitor_id: 競爭對手 UUID
    """
    from app.models.database import async_session_maker
    from app.models.competitor import Competitor, CompetitorProduct, PriceSnapshot, PriceAlert
    from app.models.system import ScrapeLog
    from app.connectors.firecrawl import get_firecrawl_connector
    from sqlalchemy import select
    from decimal import Decimal

    async def _scrape():
        connector = get_firecrawl_connector()
        settings = get_settings()

        async with async_session_maker() as db:
            # 創建爬取日誌
            log = ScrapeLog(
                task_id=self.request.id,
                task_type="competitor_scrape",
                competitor_id=UUID(competitor_id),
                status="running",
                started_at=datetime.utcnow(),
            )
            db.add(log)
            await db.flush()

            try:
                # 獲取該競爭對手的所有活躍商品
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
                        # 爬取商品
                        info = connector.extract_product_info(product.url)

                        # 獲取上一次的價格快照
                        last_snapshot_result = await db.execute(
                            select(PriceSnapshot)
                            .where(PriceSnapshot.competitor_product_id == product.id)
                            .order_by(PriceSnapshot.scraped_at.desc())
                            .limit(1)
                        )
                        last_snapshot = last_snapshot_result.scalar_one_or_none()

                        # 創建新的價格快照
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

                        # 更新商品資訊
                        if info.name and info.name != "未知商品":
                            product.name = info.name
                        if info.image_url:
                            product.image_url = info.image_url
                        if info.sku:
                            product.sku = info.sku
                        product.last_scraped_at = datetime.utcnow()
                        product.scrape_error = None

                        # 檢查是否需要創建警報
                        if last_snapshot and info.price:
                            await _check_price_alert(
                                db, product.id, last_snapshot, info, settings.price_alert_threshold
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

                # 更新日誌
                log.status = "success" if log.products_failed == 0 else "partial"
                log.completed_at = datetime.utcnow()
                log.duration_seconds = int((log.completed_at - log.started_at).total_seconds())

                await db.commit()

            except Exception as e:
                log.status = "failed"
                log.completed_at = datetime.utcnow()
                if log.errors is None:
                    log.errors = []
                log.errors.append({"error": str(e)})
                await db.commit()
                raise

    return run_async(_scrape())


async def _check_price_alert(db, product_id, last_snapshot, info, threshold):
    """檢查並創建價格警報"""
    from app.models.competitor import PriceAlert
    from decimal import Decimal

    old_price = last_snapshot.price
    new_price = info.price
    old_stock = last_snapshot.stock_status
    new_stock = info.stock_status

    # 價格變動檢查
    if old_price and new_price and old_price > 0:
        change_percent = (new_price - old_price) / old_price * 100

        if abs(change_percent) >= threshold:
            alert_type = "price_drop" if change_percent < 0 else "price_increase"
            alert = PriceAlert(
                competitor_product_id=product_id,
                alert_type=alert_type,
                old_value=str(old_price),
                new_value=str(new_price),
                change_percent=Decimal(str(round(change_percent, 2))),
            )
            db.add(alert)

    # 庫存狀態變動檢查
    if old_stock and new_stock and old_stock != new_stock:
        if old_stock == "in_stock" and new_stock == "out_of_stock":
            alert = PriceAlert(
                competitor_product_id=product_id,
                alert_type="out_of_stock",
                old_value=old_stock,
                new_value=new_stock,
            )
            db.add(alert)
        elif old_stock == "out_of_stock" and new_stock == "in_stock":
            alert = PriceAlert(
                competitor_product_id=product_id,
                alert_type="back_in_stock",
                old_value=old_stock,
                new_value=new_stock,
            )
            db.add(alert)


@celery_app.task(name="app.tasks.scrape_tasks.scrape_all_competitors")
def scrape_all_competitors():
    """爬取所有活躍競爭對手的商品（定時任務）"""
    from app.models.database import async_session_maker
    from app.models.competitor import Competitor
    from sqlalchemy import select

    async def _scrape_all():
        async with async_session_maker() as db:
            result = await db.execute(
                select(Competitor.id).where(Competitor.is_active == True)
            )
            competitor_ids = result.scalars().all()

            # 為每個競爭對手創建爬取任務
            for competitor_id in competitor_ids:
                scrape_competitor.delay(str(competitor_id))

            return {"competitors_queued": len(competitor_ids)}

    return run_async(_scrape_all())


@celery_app.task(bind=True, name="app.tasks.scrape_tasks.scrape_single_product")
def scrape_single_product(self, product_id: str):
    """爬取單個商品"""
    from app.models.database import async_session_maker
    from app.models.competitor import CompetitorProduct, PriceSnapshot
    from app.connectors.firecrawl import get_firecrawl_connector
    from sqlalchemy import select

    async def _scrape():
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

                # 創建價格快照
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

                # 更新商品資訊
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

    return run_async(_scrape())
