# =============================================
# APScheduler 定時任務排程器
# =============================================
# 替代 Celery Beat，嵌入 FastAPI 進程
# 所有任務皆 I/O 密集，使用 AsyncIOScheduler

import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)

# 全局排程器實例
_scheduler: AsyncIOScheduler | None = None


# =============================================
# 任務包裝器：捕獲異常，避免排程器崩潰
# =============================================

async def _safe_run(name: str, func, **kwargs):
    """安全執行任務，異常只記錄不傳播"""
    try:
        logger.info(f"[Scheduler] 開始執行: {name}")
        result = await func(**kwargs) if kwargs else await func()
        logger.info(f"[Scheduler] 完成: {name} → {result}")
        return result
    except Exception as e:
        logger.error(f"[Scheduler] 任務失敗: {name} — {e}", exc_info=True)


# =============================================
# 競品監測任務
# =============================================

async def job_scrape_by_priority(priorities: list[str]):
    """按優先級爬取競品"""
    from app.tasks.scrape_tasks import scrape_by_priority_async
    await _safe_run(
        f"scrape_by_priority({priorities})",
        scrape_by_priority_async,
        priorities=priorities,
    )


async def job_auto_classify_priority():
    """自動分類商品監測優先級"""
    from app.tasks.scrape_tasks import auto_classify_monitoring_priority_async
    await _safe_run(
        "auto_classify_monitoring_priority",
        auto_classify_monitoring_priority_async,
    )


# =============================================
# 圖片任務
# =============================================

async def job_cleanup_old_image_tasks():
    """清理過期圖片生成任務"""
    from app.tasks.image_generation_tasks import cleanup_old_image_tasks_async
    await _safe_run(
        "cleanup_old_image_tasks",
        cleanup_old_image_tasks_async,
    )


# =============================================
# SEO 排名任務
# =============================================

async def job_track_all_keywords():
    """每日追蹤所有關鍵詞排名"""
    from app.tasks.seo_ranking_tasks import track_all_keywords_async
    await _safe_run(
        "track_all_keywords",
        track_all_keywords_async,
    )


async def job_generate_weekly_reports():
    """每週生成 SEO 報告"""
    from app.tasks.seo_ranking_tasks import generate_weekly_reports_async
    await _safe_run(
        "generate_weekly_reports",
        generate_weekly_reports_async,
    )


# =============================================
# 工作流任務
# =============================================

async def job_check_due_schedules():
    """每分鐘檢查到期的排程報告"""
    from app.tasks.workflow_tasks import check_and_execute_due_schedules_async
    await _safe_run(
        "check_due_schedules",
        check_and_execute_due_schedules_async,
    )


# =============================================
# Agent Team 任務
# =============================================

async def job_ops_daily_sync():
    """每日運營官數據同步"""
    from app.tasks.agent_tasks import trigger_ops_daily_sync_async
    await _safe_run("ops_daily_sync", trigger_ops_daily_sync_async)


async def job_scout_analyze():
    """偵察兵批量分析"""
    from app.tasks.agent_tasks import trigger_scout_analyze_async
    await _safe_run("scout_analyze", trigger_scout_analyze_async)


async def job_pricer_batch():
    """定價師批量定價"""
    from app.tasks.agent_tasks import trigger_pricer_batch_async
    await _safe_run("pricer_batch", trigger_pricer_batch_async)


async def job_strategist_briefing():
    """軍師市場簡報"""
    from app.tasks.agent_tasks import trigger_strategist_briefing_async
    await _safe_run("strategist_briefing", trigger_strategist_briefing_async)


async def job_daily_catalog_sync():
    """每日競品庫同步"""
    from app.tasks.agent_tasks import daily_catalog_sync_async
    await _safe_run("daily_catalog_sync", daily_catalog_sync_async)


# =============================================
# 排程器生命週期
# =============================================

def create_scheduler() -> AsyncIOScheduler:
    """創建並配置排程器（不啟動）"""
    scheduler = AsyncIOScheduler(
        timezone="Asia/Hong_Kong",
        job_defaults={
            "coalesce": True,          # 錯過多次只補執行一次
            "max_instances": 1,        # 同一任務不並發
            "misfire_grace_time": 300,  # 5 分鐘容差
        },
    )

    # ==================== 競品價格監測 ====================

    # 08:00 — 所有商品 (A/B/C)
    scheduler.add_job(
        job_scrape_by_priority,
        CronTrigger(hour=8, minute=0),
        id="scrape-morning-all",
        name="競品監測 - 早上全量",
        kwargs={"priorities": ["A", "B", "C"]},
    )

    # 14:00 — 僅 A 級
    scheduler.add_job(
        job_scrape_by_priority,
        CronTrigger(hour=14, minute=0),
        id="scrape-afternoon-priority",
        name="競品監測 - 下午核心",
        kwargs={"priorities": ["A"]},
    )

    # 20:00 — A + B 級
    scheduler.add_job(
        job_scrape_by_priority,
        CronTrigger(hour=20, minute=0),
        id="scrape-evening-ab",
        name="競品監測 - 晚上 AB 級",
        kwargs={"priorities": ["A", "B"]},
    )

    # 02:00 — 自動分類優先級
    scheduler.add_job(
        job_auto_classify_priority,
        CronTrigger(hour=2, minute=0),
        id="auto-classify-priority",
        name="自動分類監測優先級",
    )

    # ==================== 圖片清理 ====================

    # 03:00 — 清理過期圖片任務
    scheduler.add_job(
        job_cleanup_old_image_tasks,
        CronTrigger(hour=3, minute=0),
        id="cleanup-old-image-tasks",
        name="清理過期圖片任務",
    )

    # ==================== SEO 排名 ====================

    # 06:00 — 每日關鍵詞排名追蹤
    scheduler.add_job(
        job_track_all_keywords,
        CronTrigger(hour=6, minute=0),
        id="track-keywords-daily",
        name="SEO 排名追蹤",
    )

    # 週一 08:00 — 每週 SEO 報告
    scheduler.add_job(
        job_generate_weekly_reports,
        CronTrigger(hour=8, minute=0, day_of_week="mon"),
        id="weekly-seo-reports",
        name="每週 SEO 報告",
    )

    # ==================== 工作流排程 ====================

    # 每分鐘 — 檢查到期排程
    scheduler.add_job(
        job_check_due_schedules,
        CronTrigger(minute="*"),
        id="check-due-schedules",
        name="檢查到期排程",
    )

    # ==================== Agent Team ====================

    # 08:00 — 運營官數據同步
    scheduler.add_job(
        job_ops_daily_sync,
        CronTrigger(hour=8, minute=0),
        id="agent-ops-daily-sync",
        name="Agent: 運營官同步",
    )

    # 09:30 — 偵察兵分析
    scheduler.add_job(
        job_scout_analyze,
        CronTrigger(hour=9, minute=30),
        id="agent-scout-analyze",
        name="Agent: 偵察兵分析",
    )

    # 10:00 — 定價師批量
    scheduler.add_job(
        job_pricer_batch,
        CronTrigger(hour=10, minute=0),
        id="agent-pricer-batch",
        name="Agent: 定價師批量",
    )

    # 11:00 — 軍師簡報
    scheduler.add_job(
        job_strategist_briefing,
        CronTrigger(hour=11, minute=0),
        id="agent-strategist-briefing",
        name="Agent: 軍師簡報",
    )

    # ==================== 競品建庫 ====================

    # 02:30 — 每日建庫同步
    scheduler.add_job(
        job_daily_catalog_sync,
        CronTrigger(hour=2, minute=30),
        id="daily-catalog-sync",
        name="每日競品庫同步",
    )

    return scheduler


async def start_scheduler() -> None:
    """啟動排程器"""
    global _scheduler
    _scheduler = create_scheduler()
    _scheduler.start()
    jobs = _scheduler.get_jobs()
    logger.info(f"APScheduler 啟動，已註冊 {len(jobs)} 個定時任務")
    for job in jobs:
        logger.info(f"  → {job.id}: {job.name} | {job.trigger}")


async def stop_scheduler() -> None:
    """停止排程器"""
    global _scheduler
    if _scheduler:
        _scheduler.shutdown(wait=False)
        logger.info("APScheduler 已停止")
        _scheduler = None


def get_scheduler() -> AsyncIOScheduler | None:
    """獲取排程器實例（用於 API 查詢任務狀態）"""
    return _scheduler
