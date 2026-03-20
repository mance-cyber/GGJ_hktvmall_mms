# =============================================
# 任務模組（純 async，無 Celery 依賴）
# =============================================

from app.tasks.scrape_tasks import (
    scrape_competitor_async,
    scrape_all_competitors_async,
    scrape_single_product_async,
    scrape_by_priority_async,
    auto_classify_monitoring_priority_async,
)
from app.tasks.agent_tasks import (
    trigger_ops_daily_sync_async,
    trigger_scout_analyze_async,
    trigger_pricer_batch_async,
    trigger_strategist_briefing_async,
    daily_catalog_sync_async,
)

__all__ = [
    "scrape_competitor_async",
    "scrape_all_competitors_async",
    "scrape_single_product_async",
    "scrape_by_priority_async",
    "auto_classify_monitoring_priority_async",
    "trigger_ops_daily_sync_async",
    "trigger_scout_analyze_async",
    "trigger_pricer_batch_async",
    "trigger_strategist_briefing_async",
    "daily_catalog_sync_async",
]
