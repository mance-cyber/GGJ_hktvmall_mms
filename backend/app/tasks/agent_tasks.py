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
