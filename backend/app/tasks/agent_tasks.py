# =============================================
# Agent Team 排程任務
# =============================================
# 用途：通過 Celery Beat 觸發 Agent 排程事件
# 設計：任務只負責發射事件，業務邏輯在 Agent 中處理
# 安全：使用 asyncio.Lock 防止並發任務互相干擾全域 Agent 狀態
# =============================================

import asyncio
import logging
import threading

from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)

# 進程級互斥鎖：確保同一 worker 進程內不會同時 startup/shutdown Agent 系統
_agent_lock = threading.Lock()


def _run_async(coro):
    """在 Celery worker（同步環境）中串行執行異步協程"""
    with _agent_lock:
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()


async def _emit_schedule_event(event_type: str) -> dict:
    """
    初始化 Agent 系統並發射排程事件

    Celery worker 進程沒有 FastAPI lifespan，
    需要手動啟動 Agent Team 再發射事件。
    用 try/finally 保證啟動後一定關閉。
    """
    from app.agents import startup_agents, shutdown_agents, get_event_bus
    from app.models.database import init_db

    await init_db()
    await startup_agents()

    try:
        bus = get_event_bus()
        event = await bus.emit(event_type, {"source": "celery_beat"})
        return {
            "event_id": event.id,
            "event_type": event.type,
            "status": "emitted",
        }
    finally:
        await shutdown_agents()


# ==================== Celery 任務 ====================

@celery_app.task(name="app.tasks.agent_tasks.trigger_ops_daily_sync")
def trigger_ops_daily_sync():
    """每日 08:00 — 觸發運營官數據同步"""
    from app.agents.events import Events
    logger.info("Celery Beat: 觸發 OPS 每日同步")
    return _run_async(_emit_schedule_event(Events.SCHEDULE_OPS_DAILY_SYNC))


@celery_app.task(name="app.tasks.agent_tasks.trigger_scout_analyze")
def trigger_scout_analyze():
    """每日 09:30 — 觸發偵察兵批量分析"""
    from app.agents.events import Events
    logger.info("Celery Beat: 觸發 Scout 批量分析")
    return _run_async(_emit_schedule_event(Events.SCHEDULE_SCOUT_ANALYZE))


@celery_app.task(name="app.tasks.agent_tasks.trigger_pricer_batch")
def trigger_pricer_batch():
    """每日 10:00 — 觸發定價師批量分析"""
    from app.agents.events import Events
    logger.info("Celery Beat: 觸發 Pricer 批量定價")
    return _run_async(_emit_schedule_event(Events.SCHEDULE_PRICER_BATCH))


@celery_app.task(name="app.tasks.agent_tasks.trigger_strategist_briefing")
def trigger_strategist_briefing():
    """每日 11:00 — 觸發軍師市場簡報"""
    from app.agents.events import Events
    logger.info("Celery Beat: 觸發 Strategist 每日簡報")
    return _run_async(_emit_schedule_event(Events.SCHEDULE_STRATEGIST_BRIEFING))


@celery_app.task(name="app.tasks.agent_tasks.batch_find_competitors")
def batch_find_competitors(
    limit: int = 50,
    category_main: str = None,
    category_sub: str = None,
    platform: str = "hktvmall",
):
    """
    批量為商品搜索競品（多平台）

    Args:
        limit: 一次處理多少個商品（最多 50）
        category_main: 篩選大分類（可選）
        category_sub: 篩選小分類（可選）
        platform: 搜索平台 ("hktvmall" | "wellcome")

    Returns:
        處理結果統計
    """
    logger.info(f"Celery: 開始批量競品匹配 (limit={limit}, platform={platform})")
    return _run_async(
        _batch_find_competitors_async(limit, category_main, category_sub, platform)
    )


async def _batch_find_competitors_async(
    limit: int,
    category_main: str = None,
    category_sub: str = None,
    platform: str = "hktvmall",
) -> dict:
    """批量競品匹配的異步實現"""
    from sqlalchemy import select, and_
    from app.models.database import async_session_maker, init_db
    from app.models.product import Product, ProductCompetitorMapping
    from app.services.competitor_matcher import CompetitorMatcherService

    await init_db()

    async with async_session_maker() as session:
        # 查詢尚未有競品關聯的商品（所有來源）
        subquery = select(ProductCompetitorMapping.product_id)

        query = select(Product).where(
            ~Product.id.in_(subquery)
        )

        if category_main:
            query = query.where(Product.category_main == category_main)
        if category_sub:
            query = query.where(Product.category_sub == category_sub)

        query = query.limit(limit)

        result = await session.execute(query)
        products = result.scalars().all()

        if not products:
            logger.info("沒有待處理的商品（所有商品都已有競品映射）")
            return {
                "status": "completed",
                "processed": 0,
                "message": "沒有待處理的商品"
            }

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

                for match in matches[:1]:  # 每個商品最多保存一個最佳匹配
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


@celery_app.task(name="app.tasks.agent_tasks.crawl_wellcome_categories")
def crawl_wellcome_categories():
    """
    定期爬取惠康重點分類，填充本地索引

    用於支撐 WellcomeSearchStrategy 的 Layer 1 本地索引搜索。
    建議 Celery Beat 排程：每日凌晨執行。
    """
    logger.info("Celery: 開始惠康分類爬取")
    return _run_async(_crawl_wellcome_categories_async())


async def _crawl_wellcome_categories_async() -> dict:
    """惠康分類爬取的異步實現"""
    from app.models.database import async_session_maker, init_db
    from app.services.wellcome_strategy import WellcomeSearchStrategy

    await init_db()

    # 惠康重點分類（與 GoGoJap 商品線重疊的品類）
    CATEGORIES = {
        "100015-100182-101093": "豬肉",
        "100015-100182-101092": "牛肉",
        "100015-100186-101115": "其他急凍肉",
        "100015-100183": "海鮮",
    }

    strategy = WellcomeSearchStrategy()
    total_new = 0

    async with async_session_maker() as session:
        try:
            for cat_id, cat_name in CATEGORIES.items():
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
        "categories_crawled": len(CATEGORIES),
        "total_new_products": total_new,
    }
    logger.info(f"惠康分類爬取完成: {total_new} 個新商品")
    return result
