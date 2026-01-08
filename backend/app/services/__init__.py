# =============================================
# 業務服務模組
# =============================================

from app.services.rate_limiter import (
    RateLimiterConfig,
    TokenBucketRateLimiter,
    DomainRateLimiter,
    ConcurrencyLimiter,
    RateLimitContext,
)
from app.services.scrape_executor import (
    ErrorType,
    ScrapeConfig,
    ScrapeResult,
    ScrapeExecutor,
    SmartScrapeExecutor,
    get_scrape_executor,
    get_smart_scrape_executor,
)
from app.services.batch_optimizer import (
    BatchConfig,
    BatchProgress,
    BatchOptimizer,
    PriorityBatchOptimizer,
    BatchImportProcessor,
    ImportResult,
    get_batch_optimizer,
    get_priority_batch_optimizer,
)
from app.services.telegram import (
    TelegramNotifier,
    get_telegram_notifier,
    send_telegram_notification,
)

__all__ = [
    # 速率限制
    "RateLimiterConfig",
    "TokenBucketRateLimiter",
    "DomainRateLimiter",
    "ConcurrencyLimiter",
    "RateLimitContext",
    # 爬取執行器
    "ErrorType",
    "ScrapeConfig",
    "ScrapeResult",
    "ScrapeExecutor",
    "SmartScrapeExecutor",
    "get_scrape_executor",
    "get_smart_scrape_executor",
    # 批量優化器
    "BatchConfig",
    "BatchProgress",
    "BatchOptimizer",
    "PriorityBatchOptimizer",
    "BatchImportProcessor",
    "ImportResult",
    "get_batch_optimizer",
    "get_priority_batch_optimizer",
    # Telegram 通知
    "TelegramNotifier",
    "get_telegram_notifier",
    "send_telegram_notification",
]
