# =============================================
# SEO 排名追蹤 Schemas
# =============================================
#
# 用於關鍵詞排名追蹤、分析報告、警報等 API
# =============================================

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from enum import Enum
from pydantic import BaseModel, Field, field_validator


# =============================================
# 枚舉類型
# =============================================

class KeywordTypeEnum(str, Enum):
    """關鍵詞類型"""
    PRIMARY = "primary"
    SECONDARY = "secondary"
    LONG_TAIL = "long_tail"
    BRAND = "brand"
    COMPETITOR = "competitor"


class RankingSourceEnum(str, Enum):
    """排名來源"""
    GOOGLE_HK = "google_hk"
    HKTVMALL = "hktvmall"
    GOOGLE_ORGANIC = "google_organic"
    GOOGLE_LOCAL = "google_local"


class ReportTypeEnum(str, Enum):
    """報告類型"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    MANUAL = "manual"


class AlertSeverityEnum(str, Enum):
    """警報嚴重程度"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class ScrapeJobStatusEnum(str, Enum):
    """抓取任務狀態"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# =============================================
# 關鍵詞配置 Schemas
# =============================================

class KeywordConfigCreate(BaseModel):
    """創建關鍵詞配置"""
    product_id: Optional[UUID] = Field(
        default=None,
        description="關聯的產品 ID"
    )
    keyword: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="要追蹤的關鍵詞"
    )
    keyword_type: KeywordTypeEnum = Field(
        default=KeywordTypeEnum.SECONDARY,
        description="關鍵詞類型"
    )
    track_google: bool = Field(default=True, description="是否追蹤 Google 排名")
    track_hktvmall: bool = Field(default=True, description="是否追蹤 HKTVmall 站內排名")
    target_google_rank: Optional[int] = Field(
        default=None,
        ge=1,
        le=100,
        description="Google 目標排名"
    )
    target_hktvmall_rank: Optional[int] = Field(
        default=None,
        ge=1,
        le=100,
        description="HKTVmall 目標排名"
    )
    track_competitors: bool = Field(default=False, description="是否追蹤競品排名")
    competitor_product_ids: List[UUID] = Field(
        default=[],
        description="要追蹤的競品產品 ID 列表"
    )
    notes: Optional[str] = Field(default=None, description="備註")
    tags: List[str] = Field(default=[], description="標籤")

    @field_validator('keyword')
    @classmethod
    def normalize_keyword(cls, v: str) -> str:
        return v.strip()


class KeywordConfigUpdate(BaseModel):
    """更新關鍵詞配置"""
    keyword_type: Optional[KeywordTypeEnum] = None
    track_google: Optional[bool] = None
    track_hktvmall: Optional[bool] = None
    is_active: Optional[bool] = None
    target_google_rank: Optional[int] = Field(default=None, ge=1, le=100)
    target_hktvmall_rank: Optional[int] = Field(default=None, ge=1, le=100)
    track_competitors: Optional[bool] = None
    competitor_product_ids: Optional[List[UUID]] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None


class KeywordConfigResponse(BaseModel):
    """關鍵詞配置響應"""
    id: UUID
    product_id: Optional[UUID] = None
    keyword: str
    keyword_normalized: str
    keyword_type: str
    track_google: bool
    track_hktvmall: bool
    is_active: bool
    target_google_rank: Optional[int] = None
    target_hktvmall_rank: Optional[int] = None
    baseline_google_rank: Optional[int] = None
    baseline_hktvmall_rank: Optional[int] = None
    latest_google_rank: Optional[int] = None
    latest_hktvmall_rank: Optional[int] = None
    latest_tracked_at: Optional[datetime] = None
    track_competitors: bool
    competitor_product_ids: List[UUID] = Field(default=[])
    notes: Optional[str] = None
    tags: List[str] = Field(default=[])
    created_at: datetime
    updated_at: datetime

    # 計算字段
    google_rank_change: Optional[int] = Field(
        default=None,
        description="與基準相比的 Google 排名變化"
    )
    hktvmall_rank_change: Optional[int] = Field(
        default=None,
        description="與基準相比的 HKTVmall 排名變化"
    )
    google_target_gap: Optional[int] = Field(
        default=None,
        description="與 Google 目標排名的差距"
    )
    hktvmall_target_gap: Optional[int] = Field(
        default=None,
        description="與 HKTVmall 目標排名的差距"
    )

    model_config = {"from_attributes": True}


class KeywordConfigListResponse(BaseModel):
    """關鍵詞配置列表響應"""
    data: List[KeywordConfigResponse]
    total: int
    page: int = 1
    page_size: int = 20


class KeywordConfigBatchCreate(BaseModel):
    """批量創建關鍵詞配置"""
    product_id: Optional[UUID] = None
    keywords: List[str] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="關鍵詞列表"
    )
    keyword_type: KeywordTypeEnum = Field(default=KeywordTypeEnum.SECONDARY)
    track_google: bool = Field(default=True)
    track_hktvmall: bool = Field(default=True)


class KeywordConfigBatchResponse(BaseModel):
    """批量創建響應"""
    created: int
    skipped: int
    errors: List[str] = Field(default=[])
    configs: List[KeywordConfigResponse] = Field(default=[])


# =============================================
# 關鍵詞排名 Schemas
# =============================================

class KeywordRankingData(BaseModel):
    """排名數據（單次抓取）"""
    keyword_config_id: UUID
    keyword: str

    # Google 數據
    google_rank: Optional[int] = Field(default=None, description="Google 排名 1-100")
    google_page: Optional[int] = None
    google_url: Optional[str] = None
    google_snippet: Optional[str] = None
    google_total_results: Optional[int] = None

    # HKTVmall 數據
    hktvmall_rank: Optional[int] = Field(default=None, description="HKTVmall 排名")
    hktvmall_page: Optional[int] = None
    hktvmall_total_results: Optional[int] = None
    hktvmall_product_url: Optional[str] = None

    # 競品數據
    competitor_rankings: Optional[Dict[str, Any]] = None

    # SERP 特徵
    serp_features: Optional[Dict[str, bool]] = None


class KeywordRankingResponse(BaseModel):
    """排名記錄響應"""
    id: UUID
    keyword_config_id: UUID
    product_id: Optional[UUID] = None
    keyword: str

    google_rank: Optional[int] = None
    google_page: Optional[int] = None
    google_url: Optional[str] = None
    google_rank_change: Optional[int] = None

    hktvmall_rank: Optional[int] = None
    hktvmall_page: Optional[int] = None
    hktvmall_rank_change: Optional[int] = None

    competitor_rankings: Optional[Dict[str, Any]] = None
    serp_features: Optional[Dict[str, bool]] = None

    source: str
    tracked_at: datetime
    scrape_success: bool

    model_config = {"from_attributes": True}


class KeywordRankingHistoryRequest(BaseModel):
    """排名歷史查詢請求"""
    keyword_config_id: Optional[UUID] = None
    product_id: Optional[UUID] = None
    keyword: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    source: Optional[RankingSourceEnum] = None
    limit: int = Field(default=30, ge=1, le=365)


class KeywordRankingHistoryResponse(BaseModel):
    """排名歷史響應"""
    keyword: str
    keyword_config_id: UUID
    records: List[KeywordRankingResponse]
    summary: "RankingHistorySummary"


class RankingHistorySummary(BaseModel):
    """排名歷史摘要"""
    total_records: int
    date_range: Dict[str, Optional[datetime]]

    # Google 統計
    google_avg_rank: Optional[float] = None
    google_best_rank: Optional[int] = None
    google_worst_rank: Optional[int] = None
    google_trend: Optional[str] = Field(
        default=None,
        description="improving, declining, stable"
    )

    # HKTVmall 統計
    hktvmall_avg_rank: Optional[float] = None
    hktvmall_best_rank: Optional[int] = None
    hktvmall_worst_rank: Optional[int] = None
    hktvmall_trend: Optional[str] = None


# =============================================
# 排名排行榜 Schemas
# =============================================

class RankingLeaderboardRequest(BaseModel):
    """排名排行榜請求"""
    source: RankingSourceEnum = Field(
        default=RankingSourceEnum.GOOGLE_HK,
        description="排名來源"
    )
    keyword_type: Optional[KeywordTypeEnum] = None
    product_id: Optional[UUID] = None
    sort_by: str = Field(
        default="rank_asc",
        description="rank_asc, rank_desc, change_asc, change_desc"
    )
    limit: int = Field(default=20, ge=1, le=100)
    include_unranked: bool = Field(
        default=False,
        description="是否包含未進入排名的關鍵詞"
    )


class LeaderboardEntry(BaseModel):
    """排行榜條目"""
    rank: int = Field(description="排行榜位置")
    keyword_config_id: UUID
    keyword: str
    keyword_type: str
    product_id: Optional[UUID] = None
    product_name: Optional[str] = None

    current_rank: Optional[int] = Field(
        default=None,
        description="當前搜尋排名"
    )
    previous_rank: Optional[int] = Field(
        default=None,
        description="上次搜尋排名"
    )
    rank_change: Optional[int] = Field(
        default=None,
        description="排名變化（正=上升）"
    )
    target_rank: Optional[int] = None
    target_gap: Optional[int] = None

    last_tracked_at: Optional[datetime] = None


class RankingLeaderboardResponse(BaseModel):
    """排名排行榜響應"""
    source: str
    generated_at: datetime
    entries: List[LeaderboardEntry]
    summary: "LeaderboardSummary"


class LeaderboardSummary(BaseModel):
    """排行榜摘要"""
    total_keywords: int
    ranked_keywords: int
    unranked_keywords: int
    top_10_count: int
    top_30_count: int
    avg_rank: Optional[float] = None
    improved_count: int = 0
    declined_count: int = 0


# =============================================
# SEO 報告 Schemas
# =============================================

class SEOReportGenerateRequest(BaseModel):
    """SEO 報告生成請求"""
    product_id: Optional[UUID] = None
    report_type: ReportTypeEnum = Field(default=ReportTypeEnum.WEEKLY)
    period_days: int = Field(
        default=7,
        ge=1,
        le=90,
        description="報告週期（天數）"
    )
    include_competitors: bool = Field(default=True)
    include_recommendations: bool = Field(default=True)


class SEOReportResponse(BaseModel):
    """SEO 報告響應"""
    id: UUID
    product_id: Optional[UUID] = None
    report_type: str
    report_title: str
    report_period_start: datetime
    report_period_end: datetime

    google_summary: Optional[Dict[str, Any]] = None
    hktvmall_summary: Optional[Dict[str, Any]] = None
    keyword_details: Optional[List[Dict[str, Any]]] = None
    competitor_comparison: Optional[Dict[str, Any]] = None
    recommendations: Optional[List[Dict[str, Any]]] = None

    improvement_score: Optional[int] = None
    status: str
    generated_at: datetime

    model_config = {"from_attributes": True}


class SEOReportListResponse(BaseModel):
    """SEO 報告列表響應"""
    data: List[SEOReportResponse]
    total: int


class ReportRecommendation(BaseModel):
    """報告優化建議"""
    priority: str = Field(description="high, medium, low")
    category: str = Field(
        description="title_optimization, description_optimization, keyword_optimization, etc."
    )
    keyword: Optional[str] = None
    current_issue: str
    suggestion: str
    expected_impact: str


# =============================================
# 排名警報 Schemas
# =============================================

class RankingAlertResponse(BaseModel):
    """排名警報響應"""
    id: UUID
    keyword_config_id: UUID
    product_id: Optional[UUID] = None
    alert_type: str
    severity: str
    keyword: str
    source: str
    previous_rank: Optional[int] = None
    current_rank: Optional[int] = None
    rank_change: int
    message: str
    details: Optional[Dict[str, Any]] = None
    is_read: bool
    is_resolved: bool
    resolved_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class RankingAlertListResponse(BaseModel):
    """警報列表響應"""
    data: List[RankingAlertResponse]
    total: int
    unread_count: int


class RankingAlertResolve(BaseModel):
    """解決警報請求"""
    resolution_notes: Optional[str] = None


class RankingAlertBatchAction(BaseModel):
    """批量警報操作"""
    alert_ids: List[UUID] = Field(..., min_length=1)
    action: str = Field(description="mark_read, mark_unread, resolve")
    resolution_notes: Optional[str] = None


# =============================================
# 抓取任務 Schemas
# =============================================

class RankingScrapeRequest(BaseModel):
    """排名抓取請求"""
    job_type: str = Field(
        default="full",
        description="full, google_only, hktvmall_only, single_keyword"
    )
    keyword_config_ids: Optional[List[UUID]] = Field(
        default=None,
        description="指定要抓取的關鍵詞配置 ID，為空則抓取所有啟用的"
    )
    product_id: Optional[UUID] = Field(
        default=None,
        description="指定產品 ID，只抓取該產品的關鍵詞"
    )


class RankingScrapeJobResponse(BaseModel):
    """抓取任務響應"""
    id: UUID
    job_type: str
    status: str
    total_keywords: int
    processed_keywords: int
    successful_keywords: int
    failed_keywords: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    errors: List[Dict[str, Any]] = Field(default=[])
    triggered_by: str
    created_at: datetime

    # 計算字段
    progress_percent: int = Field(default=0)
    success_rate: Optional[float] = None

    model_config = {"from_attributes": True}


class RankingScrapeJobListResponse(BaseModel):
    """抓取任務列表響應"""
    data: List[RankingScrapeJobResponse]
    total: int


# =============================================
# 儀表板 Schemas
# =============================================

class SEODashboardRequest(BaseModel):
    """SEO 儀表板請求"""
    product_id: Optional[UUID] = None
    days: int = Field(default=7, ge=1, le=90)


class SEODashboardResponse(BaseModel):
    """SEO 儀表板響應"""
    # 概覽指標
    overview: "DashboardOverview"

    # Google 排名摘要
    google_rankings: "RankingSummaryBySource"

    # HKTVmall 排名摘要
    hktvmall_rankings: "RankingSummaryBySource"

    # 排名趨勢（用於圖表）
    ranking_trends: List["RankingTrendPoint"]

    # 最近的警報
    recent_alerts: List[RankingAlertResponse]

    # 最近的抓取任務
    recent_jobs: List[RankingScrapeJobResponse]


class DashboardOverview(BaseModel):
    """儀表板概覽"""
    total_keywords: int
    active_keywords: int
    keywords_with_data: int

    # 變化統計
    improved_keywords: int
    declined_keywords: int
    unchanged_keywords: int

    # 健康分數
    seo_health_score: int = Field(ge=0, le=100)

    # 最近更新時間
    last_scrape_at: Optional[datetime] = None


class RankingSummaryBySource(BaseModel):
    """按來源的排名摘要"""
    source: str
    total_keywords: int
    ranked_keywords: int
    avg_rank: Optional[float] = None
    top_10_count: int
    top_30_count: int
    best_keyword: Optional[Dict[str, Any]] = None
    worst_keyword: Optional[Dict[str, Any]] = None


class RankingTrendPoint(BaseModel):
    """排名趨勢數據點"""
    date: datetime
    google_avg_rank: Optional[float] = None
    google_top_10_count: int = 0
    hktvmall_avg_rank: Optional[float] = None
    hktvmall_top_10_count: int = 0


# =============================================
# 競品對比 Schemas
# =============================================

class CompetitorComparisonRequest(BaseModel):
    """競品對比請求"""
    product_id: UUID
    competitor_product_ids: List[UUID] = Field(..., min_length=1, max_length=10)
    keywords: Optional[List[str]] = Field(
        default=None,
        description="指定關鍵詞，為空則使用產品的所有關鍵詞"
    )


class CompetitorRankingComparison(BaseModel):
    """競品排名對比"""
    keyword: str
    our_google_rank: Optional[int] = None
    our_hktvmall_rank: Optional[int] = None
    competitor_rankings: Dict[str, Dict[str, Optional[int]]] = Field(
        default_factory=dict,
        description="{competitor_id: {google_rank: X, hktvmall_rank: Y}}"
    )
    our_position: str = Field(description="winning, losing, tied")


class CompetitorComparisonResponse(BaseModel):
    """競品對比響應"""
    product_id: UUID
    competitors: Dict[str, str] = Field(
        description="{competitor_id: competitor_name}"
    )
    keyword_comparisons: List[CompetitorRankingComparison]
    summary: "CompetitorComparisonSummary"


class CompetitorComparisonSummary(BaseModel):
    """競品對比摘要"""
    total_keywords: int
    winning_keywords: int
    losing_keywords: int
    tied_keywords: int
    avg_rank_difference: Optional[float] = None
