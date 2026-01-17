# =============================================
# SEO 排名追蹤相關模型
# =============================================
#
# 功能：追蹤關鍵詞在 Google 和 HKTVmall 的排名
# 包含：
#   - KeywordConfig: 關鍵詞配置與追蹤設定
#   - KeywordRanking: 排名歷史記錄
#   - SEOReport: 優化報告
#   - RankingAlert: 排名變化警報
# =============================================

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from enum import Enum

from sqlalchemy import String, Text, Integer, Boolean, ForeignKey, Index, Numeric, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.database import Base, utcnow


# =============================================
# 枚舉類型
# =============================================

class KeywordType(str, Enum):
    """關鍵詞類型"""
    PRIMARY = "primary"           # 主關鍵詞
    SECONDARY = "secondary"       # 次要關鍵詞
    LONG_TAIL = "long_tail"       # 長尾關鍵詞
    BRAND = "brand"               # 品牌詞
    COMPETITOR = "competitor"      # 競品詞


class RankingSource(str, Enum):
    """排名來源"""
    GOOGLE_HK = "google_hk"           # Google 香港
    HKTVMALL = "hktvmall"             # HKTVmall 站內搜尋
    GOOGLE_ORGANIC = "google_organic"  # Google 自然搜尋
    GOOGLE_LOCAL = "google_local"      # Google 本地搜尋


class ReportType(str, Enum):
    """報告類型"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    MANUAL = "manual"


class AlertSeverity(str, Enum):
    """警報嚴重程度"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


# =============================================
# 關鍵詞配置表
# =============================================

class KeywordConfig(Base):
    """
    關鍵詞追蹤配置

    定義要追蹤的關鍵詞及其設定，包括：
    - 關鍵詞與產品的關聯
    - 關鍵詞類型（主/次/長尾）
    - 追蹤頻率和狀態
    - 目標排名
    """
    __tablename__ = "keyword_configs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # =============================================
    # 關聯
    # =============================================
    product_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="SET NULL"),
        nullable=True,
        comment="關聯產品 ID"
    )

    # =============================================
    # 關鍵詞基本資訊
    # =============================================
    keyword: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="追蹤的關鍵詞"
    )
    keyword_normalized: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="標準化關鍵詞（小寫、去首尾空格）"
    )
    keyword_type: Mapped[KeywordType] = mapped_column(
        SQLEnum(KeywordType),
        default=KeywordType.SECONDARY,
        comment="關鍵詞類型"
    )

    # =============================================
    # 追蹤設定
    # =============================================
    track_google: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        comment="是否追蹤 Google 排名"
    )
    track_hktvmall: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        comment="是否追蹤 HKTVmall 站內排名"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        comment="是否啟用追蹤"
    )

    # =============================================
    # 目標與基準
    # =============================================
    target_google_rank: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment="Google 目標排名（如 Top 10）"
    )
    target_hktvmall_rank: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment="HKTVmall 目標排名"
    )
    baseline_google_rank: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment="Google 基準排名（首次記錄）"
    )
    baseline_hktvmall_rank: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment="HKTVmall 基準排名（首次記錄）"
    )

    # =============================================
    # 最新排名快照（方便查詢）
    # =============================================
    latest_google_rank: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment="最新 Google 排名"
    )
    latest_hktvmall_rank: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment="最新 HKTVmall 排名"
    )
    latest_tracked_at: Mapped[Optional[datetime]] = mapped_column(
        comment="最後追蹤時間"
    )

    # =============================================
    # 競品追蹤
    # =============================================
    track_competitors: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        comment="是否追蹤競品在該關鍵詞的排名"
    )
    competitor_product_ids: Mapped[Optional[list]] = mapped_column(
        JSONB,
        default=[],
        comment="要追蹤的競品產品 ID 列表"
    )

    # =============================================
    # 元數據
    # =============================================
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="備註"
    )
    tags: Mapped[Optional[list]] = mapped_column(
        JSONB,
        default=[],
        comment="標籤列表"
    )

    # =============================================
    # 時間戳
    # =============================================
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        default=utcnow,
        onupdate=utcnow
    )

    # =============================================
    # 關聯
    # =============================================
    product: Mapped[Optional["Product"]] = relationship()
    rankings: Mapped[List["KeywordRanking"]] = relationship(
        back_populates="keyword_config",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_keyword_configs_product_id", "product_id"),
        Index("idx_keyword_configs_keyword", "keyword"),
        Index("idx_keyword_configs_keyword_normalized", "keyword_normalized"),
        Index("idx_keyword_configs_keyword_type", "keyword_type"),
        Index("idx_keyword_configs_is_active", "is_active"),
        Index("idx_keyword_configs_latest_google_rank", "latest_google_rank"),
        Index("idx_keyword_configs_latest_hktvmall_rank", "latest_hktvmall_rank"),
    )


# =============================================
# 關鍵詞排名記錄表
# =============================================

class KeywordRanking(Base):
    """
    關鍵詞排名歷史記錄

    每次抓取的排名數據，用於：
    - 追蹤排名變化趨勢
    - 分析優化效果
    - 與競品對比
    """
    __tablename__ = "keyword_rankings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # =============================================
    # 關聯
    # =============================================
    keyword_config_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("keyword_configs.id", ondelete="CASCADE"),
        nullable=False
    )
    product_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="SET NULL"),
        nullable=True
    )

    # =============================================
    # 關鍵詞（冗餘存儲方便查詢）
    # =============================================
    keyword: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    # =============================================
    # Google 排名數據
    # =============================================
    google_rank: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment="Google 搜尋排名 (1-100, NULL=未進前100)"
    )
    google_page: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment="Google 搜尋結果頁碼"
    )
    google_url: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="在 Google 搜尋結果中的 URL"
    )
    google_snippet: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="Google 搜尋結果摘要"
    )
    google_total_results: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment="Google 搜尋總結果數"
    )

    # =============================================
    # HKTVmall 排名數據
    # =============================================
    hktvmall_rank: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment="HKTVmall 站內搜尋排名"
    )
    hktvmall_page: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment="HKTVmall 搜尋結果頁碼"
    )
    hktvmall_total_results: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment="HKTVmall 搜尋總結果數"
    )
    hktvmall_product_url: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="HKTVmall 產品頁 URL"
    )

    # =============================================
    # 排名變化
    # =============================================
    google_rank_change: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment="Google 排名變化 (正=上升, 負=下降)"
    )
    hktvmall_rank_change: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment="HKTVmall 排名變化"
    )

    # =============================================
    # 競品排名（同一關鍵詞）
    # =============================================
    competitor_rankings: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        comment="""競品排名數據 {
            "competitor_id_1": {
                "google_rank": 5,
                "hktvmall_rank": 3,
                "url": "..."
            }
        }"""
    )

    # =============================================
    # SERP 特徵（Google）
    # =============================================
    serp_features: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        comment="""SERP 特徵 {
            "featured_snippet": false,
            "local_pack": false,
            "shopping_ads": true,
            "image_pack": false
        }"""
    )

    # =============================================
    # 抓取元數據
    # =============================================
    source: Mapped[RankingSource] = mapped_column(
        SQLEnum(RankingSource),
        default=RankingSource.GOOGLE_HK
    )
    tracked_at: Mapped[datetime] = mapped_column(
        default=utcnow,
        comment="抓取時間"
    )
    scrape_duration_ms: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment="抓取耗時（毫秒）"
    )
    scrape_success: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )
    scrape_error: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="抓取錯誤訊息"
    )

    # =============================================
    # 關聯
    # =============================================
    keyword_config: Mapped["KeywordConfig"] = relationship(
        back_populates="rankings"
    )
    product: Mapped[Optional["Product"]] = relationship()

    __table_args__ = (
        Index("idx_keyword_rankings_keyword_config_id", "keyword_config_id"),
        Index("idx_keyword_rankings_product_id", "product_id"),
        Index("idx_keyword_rankings_keyword", "keyword"),
        Index("idx_keyword_rankings_tracked_at", "tracked_at"),
        Index("idx_keyword_rankings_google_rank", "google_rank"),
        Index("idx_keyword_rankings_hktvmall_rank", "hktvmall_rank"),
        # 複合索引：方便查詢特定關鍵詞的排名歷史
        Index(
            "idx_keyword_rankings_keyword_tracked",
            "keyword_config_id", "tracked_at"
        ),
    )


# =============================================
# SEO 優化報告表
# =============================================

class SEOReport(Base):
    """
    SEO 優化報告

    包含：
    - 排名趨勢分析
    - 與競品對比
    - AI 優化建議
    - 效果追蹤
    """
    __tablename__ = "seo_reports"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # =============================================
    # 關聯
    # =============================================
    product_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="SET NULL"),
        nullable=True
    )

    # =============================================
    # 報告基本資訊
    # =============================================
    report_type: Mapped[ReportType] = mapped_column(
        SQLEnum(ReportType),
        default=ReportType.WEEKLY
    )
    report_title: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    report_period_start: Mapped[datetime] = mapped_column(
        nullable=False,
        comment="報告週期開始"
    )
    report_period_end: Mapped[datetime] = mapped_column(
        nullable=False,
        comment="報告週期結束"
    )

    # =============================================
    # Google SEO 摘要
    # =============================================
    google_summary: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        comment="""{
            "total_keywords": 10,
            "avg_rank": 15.5,
            "top_10_count": 3,
            "top_30_count": 7,
            "improved_count": 5,
            "declined_count": 2,
            "unchanged_count": 3,
            "best_keyword": {"keyword": "xxx", "rank": 3},
            "worst_keyword": {"keyword": "yyy", "rank": 85}
        }"""
    )

    # =============================================
    # HKTVmall SEO 摘要
    # =============================================
    hktvmall_summary: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        comment="""{
            "total_keywords": 10,
            "avg_rank": 8.2,
            "top_10_count": 6,
            "improved_count": 4,
            "declined_count": 1
        }"""
    )

    # =============================================
    # 關鍵詞排名詳情
    # =============================================
    keyword_details: Mapped[Optional[list]] = mapped_column(
        JSONB,
        comment="""[
            {
                "keyword": "日本零食",
                "type": "primary",
                "google_rank": 12,
                "google_change": +3,
                "hktvmall_rank": 5,
                "hktvmall_change": -1
            }
        ]"""
    )

    # =============================================
    # 競品對比
    # =============================================
    competitor_comparison: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        comment="""{
            "competitor_1": {
                "name": "759 阿信屋",
                "avg_google_rank": 8.5,
                "avg_hktvmall_rank": 3.2,
                "keywords_beating_us": 3,
                "keywords_we_beat": 5
            }
        }"""
    )

    # =============================================
    # AI 優化建議
    # =============================================
    recommendations: Mapped[Optional[list]] = mapped_column(
        JSONB,
        comment="""[
            {
                "priority": "high",
                "category": "title_optimization",
                "keyword": "日本零食",
                "current_issue": "標題未包含主關鍵詞",
                "suggestion": "建議將標題修改為...",
                "expected_impact": "預計提升 5-10 名"
            }
        ]"""
    )

    # =============================================
    # 效果追蹤
    # =============================================
    previous_report_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        comment="上一期報告 ID（用於對比）"
    )
    improvement_score: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment="改進分數 (-100 到 100)"
    )

    # =============================================
    # 報告狀態
    # =============================================
    status: Mapped[str] = mapped_column(
        String(50),
        default="draft",
        comment="draft, published, archived"
    )

    # =============================================
    # 生成元數據
    # =============================================
    generation_metadata: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        comment="{model, tokens_used, duration_ms}"
    )

    # =============================================
    # 時間戳
    # =============================================
    generated_at: Mapped[datetime] = mapped_column(default=utcnow)
    published_at: Mapped[Optional[datetime]] = mapped_column()

    # =============================================
    # 關聯
    # =============================================
    product: Mapped[Optional["Product"]] = relationship()

    __table_args__ = (
        Index("idx_seo_reports_product_id", "product_id"),
        Index("idx_seo_reports_report_type", "report_type"),
        Index("idx_seo_reports_generated_at", "generated_at"),
        Index("idx_seo_reports_status", "status"),
    )


# =============================================
# 排名變化警報表
# =============================================

class RankingAlert(Base):
    """
    排名變化警報

    當排名發生顯著變化時生成警報，用於：
    - 及時通知排名下降
    - 追蹤競品排名變化
    - 監控 SEO 健康狀態
    """
    __tablename__ = "ranking_alerts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # =============================================
    # 關聯
    # =============================================
    keyword_config_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("keyword_configs.id", ondelete="CASCADE"),
        nullable=False
    )
    product_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="SET NULL"),
        nullable=True
    )

    # =============================================
    # 警報資訊
    # =============================================
    alert_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="rank_drop, rank_improve, competitor_overtake, target_achieved"
    )
    severity: Mapped[AlertSeverity] = mapped_column(
        SQLEnum(AlertSeverity),
        default=AlertSeverity.INFO
    )

    # =============================================
    # 警報內容
    # =============================================
    keyword: Mapped[str] = mapped_column(String(255), nullable=False)
    source: Mapped[RankingSource] = mapped_column(SQLEnum(RankingSource))

    previous_rank: Mapped[Optional[int]] = mapped_column(Integer)
    current_rank: Mapped[Optional[int]] = mapped_column(Integer)
    rank_change: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="排名變化（正=上升，負=下降）"
    )

    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="警報訊息"
    )
    details: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        comment="詳細資訊"
    )

    # =============================================
    # 狀態
    # =============================================
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    resolved_at: Mapped[Optional[datetime]] = mapped_column()
    resolved_by: Mapped[Optional[str]] = mapped_column(String(255))
    resolution_notes: Mapped[Optional[str]] = mapped_column(Text)

    # =============================================
    # 時間戳
    # =============================================
    created_at: Mapped[datetime] = mapped_column(default=utcnow)

    # =============================================
    # 關聯
    # =============================================
    keyword_config: Mapped["KeywordConfig"] = relationship()
    product: Mapped[Optional["Product"]] = relationship()

    __table_args__ = (
        Index("idx_ranking_alerts_keyword_config_id", "keyword_config_id"),
        Index("idx_ranking_alerts_product_id", "product_id"),
        Index("idx_ranking_alerts_alert_type", "alert_type"),
        Index("idx_ranking_alerts_severity", "severity"),
        Index("idx_ranking_alerts_is_read", "is_read"),
        Index("idx_ranking_alerts_created_at", "created_at"),
    )


# =============================================
# 抓取任務記錄表
# =============================================

class RankingScrapeJob(Base):
    """
    排名抓取任務記錄

    追蹤每次排名抓取任務的狀態和結果
    """
    __tablename__ = "ranking_scrape_jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # =============================================
    # 任務資訊
    # =============================================
    job_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="full, google_only, hktvmall_only, single_keyword"
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default="pending",
        comment="pending, running, completed, failed, cancelled"
    )

    # =============================================
    # 任務範圍
    # =============================================
    total_keywords: Mapped[int] = mapped_column(Integer, default=0)
    processed_keywords: Mapped[int] = mapped_column(Integer, default=0)
    successful_keywords: Mapped[int] = mapped_column(Integer, default=0)
    failed_keywords: Mapped[int] = mapped_column(Integer, default=0)

    # =============================================
    # 執行詳情
    # =============================================
    started_at: Mapped[Optional[datetime]] = mapped_column()
    completed_at: Mapped[Optional[datetime]] = mapped_column()
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer)

    # =============================================
    # 錯誤記錄
    # =============================================
    errors: Mapped[Optional[list]] = mapped_column(
        JSONB,
        default=[],
        comment="錯誤列表 [{keyword, error, timestamp}]"
    )

    # =============================================
    # 觸發資訊
    # =============================================
    triggered_by: Mapped[str] = mapped_column(
        String(50),
        default="scheduler",
        comment="scheduler, manual, api"
    )
    triggered_by_user: Mapped[Optional[str]] = mapped_column(String(255))

    # =============================================
    # 時間戳
    # =============================================
    created_at: Mapped[datetime] = mapped_column(default=utcnow)

    __table_args__ = (
        Index("idx_ranking_scrape_jobs_status", "status"),
        Index("idx_ranking_scrape_jobs_job_type", "job_type"),
        Index("idx_ranking_scrape_jobs_created_at", "created_at"),
    )


# =============================================
# 避免循環導入
# =============================================
from app.models.product import Product
