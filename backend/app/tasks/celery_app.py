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
    # 每日爬取所有競品
    "scrape-all-competitors-daily": {
        "task": "app.tasks.scrape_tasks.scrape_all_competitors",
        "schedule": crontab(hour=9, minute=0),  # 每天 09:00
    },
}
