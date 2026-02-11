# =============================================
# Celery 配置
# =============================================

from celery import Celery
from celery.schedules import crontab

from app.config import get_settings

settings = get_settings()

# 創建 Celery 應用
celery_app = Celery(
    "hktv_ops",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "app.tasks.scrape_tasks",
        "app.tasks.content_tasks",
        "app.tasks.image_generation_tasks",
        "app.tasks.seo_ranking_tasks",
        "app.tasks.workflow_tasks",
        "app.tasks.agent_tasks",
    ]
)

# Celery 配置
celery_app.conf.update(
    # 序列化
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",

    # 時區
    timezone="Asia/Hong_Kong",
    enable_utc=True,

    # 任務設定
    task_track_started=True,
    task_time_limit=300,  # 5 分鐘超時
    worker_prefetch_multiplier=1,

    # 結果過期時間
    result_expires=3600,  # 1 小時

    # 重試設定
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)

# 定時任務
celery_app.conf.beat_schedule = {
    # =============================================
    # 競品價格監測 - 每天 2 次（08:00 + 20:00）
    # =============================================
    # 早上 08:00 - 開市前監測，為當日定價決策提供數據
    "scrape-all-competitors-morning": {
        "task": "app.tasks.scrape_tasks.scrape_all_competitors",
        "schedule": crontab(hour=8, minute=0),  # 每天 08:00 HKT
    },
    # 晚上 20:00 - 晚間監測，捕捉全天價格變動
    "scrape-all-competitors-evening": {
        "task": "app.tasks.scrape_tasks.scrape_all_competitors",
        "schedule": crontab(hour=20, minute=0),  # 每天 20:00 HKT
    },
    # 每日清理過期的圖片生成任務（7 天前）
    "cleanup-old-image-tasks-daily": {
        "task": "cleanup_old_image_tasks",
        "schedule": crontab(hour=3, minute=0),  # 每天凌晨 03:00
    },
    # =============================================
    # SEO 排名追蹤定時任務
    # =============================================
    # 每日追蹤所有關鍵詞排名（早上 6 點，避開高峰）
    "track-all-keyword-rankings-daily": {
        "task": "app.tasks.seo_ranking_tasks.track_all_keywords",
        "schedule": crontab(hour=6, minute=0),
    },
    # 每週生成 SEO 報告（週一早上 8 點）
    "generate-weekly-seo-reports": {
        "task": "app.tasks.seo_ranking_tasks.generate_weekly_reports",
        "schedule": crontab(hour=8, minute=0, day_of_week=1),
    },
    # =============================================
    # 工作流排程任務
    # =============================================
    # 每分鐘檢查到期的排程報告
    "check-due-scheduled-reports": {
        "task": "app.tasks.workflow_tasks.check_and_execute_due_schedules",
        "schedule": crontab(minute="*"),  # 每分鐘執行
    },
    # =============================================
    # Agent Team 排程任務
    # =============================================
    # 每日 08:00 — 運營官數據同步
    "agent-ops-daily-sync": {
        "task": "app.tasks.agent_tasks.trigger_ops_daily_sync",
        "schedule": crontab(hour=8, minute=0),
    },
    # 每日 09:30 — 偵察兵批量分析
    "agent-scout-analyze": {
        "task": "app.tasks.agent_tasks.trigger_scout_analyze",
        "schedule": crontab(hour=9, minute=30),
    },
    # 每日 10:00 — 定價師批量定價
    "agent-pricer-batch": {
        "task": "app.tasks.agent_tasks.trigger_pricer_batch",
        "schedule": crontab(hour=10, minute=0),
    },
    # 每日 11:00 — 軍師市場簡報
    "agent-strategist-briefing": {
        "task": "app.tasks.agent_tasks.trigger_strategist_briefing",
        "schedule": crontab(hour=11, minute=0),
    },
}
