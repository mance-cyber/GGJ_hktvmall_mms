# =============================================
# 數據庫模型
# =============================================

from app.models.database import Base, get_db
from app.models.competitor import Competitor, CompetitorProduct, PriceSnapshot, PriceAlert
from app.models.product import Product, ProductHistory, ProductCompetitorMapping
from app.models.content import AIContent
from app.models.system import ScrapeLog, SyncLog, Settings
from app.models.scrape_config import ScrapeConfig
from app.models.import_job import ImportJob, ImportJobItem
from app.models.analytics import PriceAnalytics, MarketReport
from app.models.notification import Notification, Webhook

__all__ = [
    # 數據庫
    "Base",
    "get_db",
    # 競品監測
    "Competitor",
    "CompetitorProduct",
    "PriceSnapshot",
    "PriceAlert",
    # 商品管理
    "Product",
    "ProductHistory",
    "ProductCompetitorMapping",
    # AI 內容
    "AIContent",
    # 系統
    "ScrapeLog",
    "SyncLog",
    "Settings",
    # 爬取配置
    "ScrapeConfig",
    # 批量導入
    "ImportJob",
    "ImportJobItem",
    # 分析報告
    "PriceAnalytics",
    "MarketReport",
    # 通知
    "Notification",
    "Webhook",
]
