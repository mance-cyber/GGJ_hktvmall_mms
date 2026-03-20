# =============================================
# Agent Team 排程任務（純 async，無 Celery 依賴）
# =============================================
# 設計：任務只負責發射事件，業務邏輯在 Agent 中處理
# 注意：在 FastAPI 進程中，Agent Team 已通過 lifespan 啟動，
#       不需要像 Celery worker 那樣手動 startup/shutdown

import asyncio
import logging

logger = logging.getLogger(__name__)


async def _emit_event(event_type: str) -> dict:
    """
    發射排程事件到 Agent EventBus

    在 FastAPI 進程中，Agent 系統已通過 lifespan 初始化，
    直接使用 get_event_bus() 發射事件即可。
    """
    from app.agents import get_event_bus

    bus = get_event_bus()
    event = await bus.emit(event_type, {"source": "apscheduler"})
    return {
        "event_id": event.id,
        "event_type": event.type,
        "status": "emitted",
    }


# ==================== 排程任務 ====================

async def trigger_ops_daily_sync_async():
    """每日 08:00 — 觸發運營官數據同步"""
    from app.agents.events import Events
    logger.info("APScheduler: 觸發 OPS 每日同步")
    return await _emit_event(Events.SCHEDULE_OPS_DAILY_SYNC)


async def trigger_scout_analyze_async():
    """每日 09:30 — 觸發偵察兵批量分析"""
    from app.agents.events import Events
    logger.info("APScheduler: 觸發 Scout 批量分析")
    return await _emit_event(Events.SCHEDULE_SCOUT_ANALYZE)


async def trigger_pricer_batch_async():
    """每日 10:00 — 觸發定價師批量分析"""
    from app.agents.events import Events
    logger.info("APScheduler: 觸發 Pricer 批量定價")
    return await _emit_event(Events.SCHEDULE_PRICER_BATCH)


async def trigger_strategist_briefing_async():
    """每日 11:00 — 觸發軍師市場簡報"""
    from app.agents.events import Events
    logger.info("APScheduler: 觸發 Strategist 每日簡報")
    return await _emit_event(Events.SCHEDULE_STRATEGIST_BRIEFING)


# ==================== 競品批量任務 ====================

async def batch_find_competitors_async(
    limit: int = 50,
    category_main: str = None,
    category_sub: str = None,
    platform: str = "hktvmall",
) -> dict:
    """批量為商品搜索競品"""
    logger.info(f"開始批量競品匹配 (limit={limit}, platform={platform})")

    from sqlalchemy import select
    from app.models.database import async_session_maker
    from app.models.product import Product, ProductCompetitorMapping
    from app.models.competitor import Competitor, CompetitorProduct
    from app.services.competitor_matcher import CompetitorMatcherService

    async with async_session_maker() as session:
        subquery = (
            select(ProductCompetitorMapping.product_id)
            .join(CompetitorProduct, ProductCompetitorMapping.competitor_product_id == CompetitorProduct.id)
            .join(Competitor, CompetitorProduct.competitor_id == Competitor.id)
            .where(Competitor.platform == platform)
        )

        query = select(Product).where(~Product.id.in_(subquery))

        if category_main:
            query = query.where(Product.category_main == category_main)
        if category_sub:
            query = query.where(Product.category_sub == category_sub)

        query = query.limit(limit)

        result = await session.execute(query)
        products = result.scalars().all()

        if not products:
            logger.info("沒有待處理的商品")
            return {"status": "completed", "processed": 0, "message": "沒有待處理的商品"}

        service = CompetitorMatcherService()

        success_count = 0
        error_count = 0
        total_matches = 0

        for idx, product in enumerate(products, 1):
            try:
                logger.info(f"處理 [{idx}/{len(products)}]: {product.name_zh}")

                results = await service.find_competitors_for_product(
                    db=session,
                    product=product,
                    platform=platform,
                    max_candidates=3,
                )

                matches = [r for r in results if r.is_match and r.match_confidence >= 0.4]

                for match in matches[:1]:
                    await service.save_match_to_db(
                        db=session,
                        product_id=str(product.id),
                        match_result=match,
                        platform=platform,
                    )
                    total_matches += 1

                success_count += 1
                logger.info(f"[{platform}] {product.name_zh}: 找到 {len(matches)} 個匹配")

            except Exception as e:
                error_count += 1
                logger.error(f"[{platform}] {product.name_zh}: {str(e)}")

        await session.commit()

        result = {
            "status": "completed",
            "platform": platform,
            "processed": len(products),
            "success": success_count,
            "errors": error_count,
            "total_matches": total_matches,
        }

        logger.info(
            f"批量競品匹配完成 [{platform}]: 處理 {len(products)} 個商品, "
            f"成功 {success_count}, 失敗 {error_count}, "
            f"找到 {total_matches} 個競品"
        )

        return result


# ==================== 每日建庫同步 ====================

async def daily_catalog_sync_async() -> dict:
    """每日凌晨：建庫更新 → 打標新品 → 匹配 → 監測"""
    logger.info("APScheduler: 開始每日競品庫同步")

    from app.models.database import async_session_maker
    from app.services.cataloger import CatalogService
    from app.services.tagger import tag_all_untagged
    from app.services.matcher import match_all_pending
    from app.services.monitor import MonitorService

    async with async_session_maker() as session:
        catalog_result = await CatalogService.update_catalog(session)
        tag_result = await tag_all_untagged(session)
        match_result = await match_all_pending(session)
        monitor_result = await MonitorService.run_daily_check(session)
        await session.commit()

        result = {
            "status": "completed",
            "catalog": catalog_result,
            "tagging": tag_result,
            "matching": match_result,
            "monitoring": monitor_result,
        }
        logger.info(f"每日競品庫同步完成: {result}")
        return result


# ==================== 惠康分類爬取 ====================

async def crawl_wellcome_categories_async() -> dict:
    """定期爬取惠康重點分類"""
    logger.info("開始惠康分類爬取")

    from app.models.database import async_session_maker
    from app.services.wellcome_strategy import WellcomeSearchStrategy, ALL_CATEGORIES

    strategy = WellcomeSearchStrategy()
    total_new = 0

    async with async_session_maker() as session:
        try:
            for cat_id, cat_name in ALL_CATEGORIES.items():
                try:
                    count = await strategy.crawl_category(
                        db=session,
                        category_id=cat_id,
                        category_name=cat_name,
                        max_pages=5,
                    )
                    total_new += count
                    logger.info(f"惠康分類 [{cat_name}]: 新增 {count} 商品")
                except Exception as e:
                    logger.error(f"惠康分類 [{cat_name}] 爬取失敗: {e}")

            await session.commit()
        except Exception as e:
            logger.error(f"惠康分類爬取事務失敗: {e}")
            await session.rollback()
            raise

    result = {
        "status": "completed",
        "categories_crawled": len(ALL_CATEGORIES),
        "total_new_products": total_new,
    }
    logger.info(f"惠康分類爬取完成: {total_new} 個新商品")
    return result
