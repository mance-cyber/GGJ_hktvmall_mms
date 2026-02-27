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

                # 更新日誌
                log.status = "success" if log.products_failed == 0 else "partial"
                log.completed_at = datetime.utcnow()
                log.duration_seconds = int((log.completed_at - log.started_at).total_seconds())

                await db.commit()

                # 觸發 Agent 事件：Scout 分析價格變動
                try:
                    from app.agents.hooks import on_scrape_completed
                    await on_scrape_completed(
                        competitor_id=competitor_id,
                        alerts_created=log.products_scraped,  # 近似值
                        products_scraped=log.products_scraped,
                    )
                except Exception as hook_err:
                    import logging
                    logging.getLogger(__name__).warning(f"Agent hook 失敗: {hook_err}")

            except Exception as e:
                log.status = "failed"
                log.completed_at = datetime.utcnow()
                if log.errors is None:
                    log.errors = []
                log.errors.append({"error": str(e)})
                await db.commit()
                raise

    return run_async(_scrape())


async def _check_price_alert(db, product, last_snapshot, info, threshold):
    """
    檢查並創建價格警報

    Args:
        db: 數據庫 session
        product: CompetitorProduct 對象
        last_snapshot: 上一次價格快照
        info: 當前爬取的產品資訊
        threshold: 價格變動閾值 (百分比)
    """
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
                competitor_product_id=product.id,
                alert_type=alert_type,
                old_value=str(old_price),
                new_value=str(new_price),
                change_percent=Decimal(str(round(change_percent, 2))),
            )
            db.add(alert)

            # =============================================
            # 觸發告警工作流
            # =============================================
            from app.tasks.workflow_tasks import execute_alert_workflow

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

            # 異步觸發告警工作流（不阻塞爬取流程）
            execute_alert_workflow.delay(alert_data)

    # 庫存狀態變動檢查
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

# =============================================
# 分級監測策略
# =============================================

@celery_app.task(name="app.tasks.scrape_tasks.scrape_by_priority")
def scrape_by_priority(priorities: list[str] = None):
    """
    按優先級爬取競品商品（分級監測策略）
    
    Args:
        priorities: 優先級列表，例如 ["A", "B", "C"]
                   - A級：核心商品（高利潤率 >50%）
                   - B級：一般商品（中等利潤率 20-50%）
                   - C級：低優先商品（低利潤率 <20%）
    
    排程：
        - 08:00: A + B + C（所有商品）
        - 14:00: A（僅核心商品）
        - 20:00: A + B（核心 + 一般）
    """
    if priorities is None:
        priorities = ["A", "B", "C"]
    
    from app.models.database import async_session_maker
    from app.models.product import Product, ProductCompetitorMapping
    from app.models.competitor import Competitor, CompetitorProduct
    from sqlalchemy import select, distinct
    
    async def _scrape_by_priority():
        async with async_session_maker() as db:
            # 查詢符合優先級的商品映射的競品
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
            
            # 為每個競爭對手創建爬取任務
            for competitor_id in competitor_ids:
                scrape_competitor.delay(str(competitor_id))
            
            return {
                "priorities": priorities,
                "competitors_queued": len(competitor_ids),
                "message": f"已為 {len(competitor_ids)} 個競爭對手創建爬取任務（優先級: {', '.join(priorities)}）"
            }
    
    return run_async(_scrape_by_priority())


@celery_app.task(name="app.tasks.scrape_tasks.auto_classify_monitoring_priority")
def auto_classify_monitoring_priority():
    """
    自動分類商品監測優先級（基於利潤率）
    
    分類標準：
    - A級：利潤率 > 50% 且有競品映射
    - B級：利潤率 20-50%
    - C級：利潤率 < 20% 或無競品映射
    
    建議：每天執行一次（例如凌晨 02:00），確保優先級始終最新
    """
    from app.models.database import async_session_maker
    from app.models.product import Product, ProductCompetitorMapping
    from sqlalchemy import select, func
    
    async def _auto_classify():
        async with async_session_maker() as db:
            # 查詢所有商品
            result = await db.execute(select(Product))
            products = result.scalars().all()
            
            classified_count = {"A": 0, "B": 0, "C": 0}
            
            for product in products:
                # 跳過無價格或成本的商品
                if not product.price or not product.cost or product.cost == 0:
                    product.monitoring_priority = "C"
                    classified_count["C"] += 1
                    continue
                
                # 計算利潤率
                profit_margin = float((product.price - product.cost) / product.cost * 100)
                
                # 檢查是否有競品映射
                mapping_result = await db.execute(
                    select(func.count())
                    .select_from(ProductCompetitorMapping)
                    .where(ProductCompetitorMapping.product_id == product.id)
                )
                has_competitors = (mapping_result.scalar() or 0) > 0
                
                # 分類邏輯
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
    
    return run_async(_auto_classify())
