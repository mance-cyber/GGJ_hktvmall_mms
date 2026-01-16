# =============================================
# 數據庫模型
# =============================================

from app.models.database import Base, get_db
from app.models.competitor import Competitor, CompetitorProduct, PriceSnapshot, PriceAlert
from app.models.product import Product, ProductHistory, ProductCompetitorMapping, OwnPriceSnapshot
from app.models.content import AIContent
from app.models.system import ScrapeLog, SyncLog, Settings
from app.models.scrape_config import ScrapeConfig
from app.models.import_job import ImportJob, ImportJobItem
from app.models.analytics import PriceAnalytics, MarketReport
from app.models.notification import Notification, Webhook
from app.models.user import User
from app.models.pricing import PriceProposal
from app.models.image_generation import (
    ImageGenerationTask,
    InputImage,
    OutputImage,
    GenerationMode,
    TaskStatus
)
from app.models.seo import (
    SEOContent,
    StructuredData,
    BrandKnowledge,
    KeywordResearch,
    ContentAudit
)

__all__ = [
    # 數據庫
    "Base",
    "get_db",
    # 用戶
    "User",
    # 競品監測
    "Competitor",
    "CompetitorProduct",
    "PriceSnapshot",
    "PriceAlert",
    # 商品管理
    "Product",
    "ProductHistory",
    "ProductCompetitorMapping",
    "OwnPriceSnapshot",
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
    # 智能定價
    "PriceProposal",
    # 圖片生成
    "ImageGenerationTask",
    "InputImage",
    "OutputImage",
    "GenerationMode",
    "TaskStatus",
    # SEO & GEO
    "SEOContent",
    "StructuredData",
    "BrandKnowledge",
    "KeywordResearch",
    "ContentAudit",
]
