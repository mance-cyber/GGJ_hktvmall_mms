# =============================================
# SEO & GEO Schemas
# =============================================

from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field


# =============================================
# 共用類型
# =============================================

class ProductInfo(BaseModel):
    """商品資訊（用於 SEO 生成）"""
    name: str = Field(..., min_length=1)
    brand: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    features: List[str] = Field(default=[])
    price: Optional[str] = None
    origin: Optional[str] = None


# =============================================
# SEO 內容請求
# =============================================

class SEOGenerateRequest(BaseModel):
    """SEO 內容生成請求"""
    product_id: Optional[UUID] = None
    product_info: Optional[ProductInfo] = None
    target_keywords: Optional[List[str]] = Field(
        default=None,
        description="目標關鍵詞，如不提供則 AI 自動提取"
    )
    target_languages: List[str] = Field(
        default=["zh-HK"],
        description="目標語言: zh-HK, zh-CN, en"
    )
    include_og: bool = Field(
        default=True,
        description="是否生成 Open Graph 標籤"
    )


class SEOBatchGenerateItem(BaseModel):
    """批量 SEO 生成單項"""
    product_id: Optional[UUID] = None
    product_info: Optional[ProductInfo] = None
    target_keywords: Optional[List[str]] = None


class SEOBatchGenerateRequest(BaseModel):
    """批量 SEO 生成請求"""
    items: List[SEOBatchGenerateItem] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="批量生成項目列表"
    )
    target_languages: List[str] = Field(default=["zh-HK"])
    include_og: bool = Field(default=True)


class KeywordExtractRequest(BaseModel):
    """關鍵詞提取請求"""
    product_id: Optional[UUID] = None
    product_info: Optional[ProductInfo] = None
    max_keywords: int = Field(default=10, ge=1, le=30)
    include_long_tail: bool = Field(default=True)


class SEOAnalyzeRequest(BaseModel):
    """SEO 分析請求"""
    product_id: Optional[UUID] = None
    title: Optional[str] = None
    description: Optional[str] = None
    keywords: Optional[List[str]] = None
    url: Optional[str] = None


# =============================================
# SEO 內容響應
# =============================================

class SEOScoreBreakdown(BaseModel):
    """SEO 評分詳情"""
    title_score: int = Field(..., ge=0, le=100)
    description_score: int = Field(..., ge=0, le=100)
    keyword_score: int = Field(..., ge=0, le=100)
    readability_score: int = Field(..., ge=0, le=100)


class LocalizedSEO(BaseModel):
    """本地化 SEO 內容"""
    meta_title: str
    meta_description: str
    keywords: List[str] = Field(default=[])


class SEOContentData(BaseModel):
    """SEO 內容數據"""
    meta_title: str = Field(..., max_length=70)
    meta_description: str = Field(..., max_length=160)
    primary_keyword: str
    secondary_keywords: List[str] = Field(default=[])
    long_tail_keywords: List[str] = Field(default=[])
    og_title: Optional[str] = None
    og_description: Optional[str] = None
    seo_score: Optional[int] = None
    score_breakdown: Optional[SEOScoreBreakdown] = None
    improvement_suggestions: List[str] = Field(default=[])
    localized: Optional[Dict[str, LocalizedSEO]] = None


class SEOContentResponse(BaseModel):
    """SEO 內容響應"""
    id: UUID
    product_id: Optional[UUID] = None
    content: SEOContentData
    language: str
    version: int
    status: str
    generation_metadata: Optional[dict] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class SEOBatchResultItem(BaseModel):
    """批量 SEO 生成單項結果"""
    index: int
    success: bool
    product_name: str
    content_id: Optional[UUID] = None
    content: Optional[SEOContentData] = None
    error: Optional[str] = None


class SEOBatchSyncResponse(BaseModel):
    """批量 SEO 同步響應"""
    mode: str = "sync"
    results: List[SEOBatchResultItem]
    summary: dict = Field(default_factory=dict)


class SEOBatchAsyncResponse(BaseModel):
    """批量 SEO 異步響應"""
    mode: str = "async"
    task_id: str
    total: int
    message: str = "批量 SEO 任務已提交"


class SEOScoreResponse(BaseModel):
    """SEO 評分響應"""
    product_id: UUID
    seo_score: int
    score_breakdown: SEOScoreBreakdown
    improvement_suggestions: List[str]
    analyzed_at: datetime


# =============================================
# 關鍵詞相關
# =============================================

class KeywordData(BaseModel):
    """關鍵詞數據"""
    keyword: str
    search_volume: Optional[int] = None
    difficulty: Optional[int] = None
    cpc: Optional[Decimal] = None
    intent: Optional[str] = None
    trend_direction: Optional[str] = None


class KeywordExtractionResponse(BaseModel):
    """關鍵詞提取響應"""
    primary_keyword: str
    secondary_keywords: List[str]
    long_tail_keywords: List[str]
    all_keywords: List[KeywordData]


class KeywordSuggestionsResponse(BaseModel):
    """關鍵詞建議響應"""
    query: str
    suggestions: List[KeywordData]
    related_categories: List[str] = Field(default=[])


class KeywordResearchCreate(BaseModel):
    """創建關鍵詞研究記錄"""
    keyword: str = Field(..., min_length=1, max_length=255)
    search_volume: Optional[int] = None
    difficulty: Optional[int] = Field(default=None, ge=0, le=100)
    cpc: Optional[Decimal] = None
    category: Optional[str] = None
    intent: Optional[str] = None
    related_keywords: List[str] = Field(default=[])


class KeywordResearchResponse(BaseModel):
    """關鍵詞研究響應"""
    id: UUID
    keyword: str
    search_volume: Optional[int] = None
    difficulty: Optional[int] = None
    cpc: Optional[Decimal] = None
    competition_level: Optional[str] = None
    trend_direction: Optional[str] = None
    seasonality: Optional[str] = None
    category: Optional[str] = None
    intent: Optional[str] = None
    related_keywords: List[str] = Field(default=[])
    data_source: str
    last_updated: datetime

    model_config = {"from_attributes": True}


# =============================================
# GEO 結構化數據
# =============================================

class ProductSchemaRequest(BaseModel):
    """Product Schema 生成請求"""
    product_id: Optional[UUID] = None
    product_info: Optional[ProductInfo] = None
    include_reviews: bool = Field(default=False)
    include_offers: bool = Field(default=True)


class FAQSchemaRequest(BaseModel):
    """FAQ Schema 生成請求"""
    product_id: Optional[UUID] = None
    faqs: Optional[List[Dict[str, str]]] = Field(
        default=None,
        description="FAQ 列表 [{question: '...', answer: '...'}]，如不提供則 AI 生成"
    )
    max_faqs: int = Field(default=5, ge=1, le=10)


class BreadcrumbSchemaRequest(BaseModel):
    """Breadcrumb Schema 生成請求"""
    product_id: Optional[UUID] = None
    breadcrumb_path: Optional[List[Dict[str, str]]] = Field(
        default=None,
        description="麵包屑路徑 [{name: '...', url: '...'}]"
    )


class BatchSchemaRequest(BaseModel):
    """批量 Schema 生成請求"""
    product_ids: List[UUID] = Field(..., min_length=1, max_length=50)
    schema_types: List[str] = Field(
        default=["Product"],
        description="要生成的 Schema 類型"
    )


class AISummaryRequest(BaseModel):
    """AI 搜索引擎摘要請求"""
    product_id: Optional[UUID] = None
    product_info: Optional[ProductInfo] = None
    max_facts: int = Field(default=5, ge=1, le=10)


class SchemaValidationRequest(BaseModel):
    """Schema 驗證請求"""
    json_ld: dict = Field(..., description="要驗證的 JSON-LD 數據")


class StructuredDataResponse(BaseModel):
    """結構化數據響應"""
    id: UUID
    product_id: Optional[UUID] = None
    schema_type: str
    json_ld: dict
    ai_summary: Optional[str] = None
    ai_facts: List[str] = Field(default=[])
    is_valid: bool
    validation_errors: List[str] = Field(default=[])
    created_at: datetime

    model_config = {"from_attributes": True}


class BatchSchemaResponse(BaseModel):
    """批量 Schema 響應"""
    results: List[StructuredDataResponse]
    summary: dict


class SchemaValidationResponse(BaseModel):
    """Schema 驗證響應"""
    is_valid: bool
    errors: List[str] = Field(default=[])
    warnings: List[str] = Field(default=[])
    suggestions: List[str] = Field(default=[])


class AISummaryResponse(BaseModel):
    """AI 摘要響應"""
    product_id: Optional[UUID] = None
    summary: str
    facts: List[str]
    entities: Dict[str, Any] = Field(default_factory=dict)


# =============================================
# 品牌知識圖譜
# =============================================

class BrandKnowledgeCreate(BaseModel):
    """創建品牌知識"""
    knowledge_type: str = Field(
        ...,
        description="brand_info, product_fact, faq, expert_claim, testimonial"
    )
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    summary: Optional[str] = Field(default=None, max_length=500)
    related_products: List[UUID] = Field(default=[])
    related_categories: List[str] = Field(default=[])
    credibility_score: Optional[int] = Field(default=None, ge=0, le=100)
    source_type: str = Field(default="internal")
    source_reference: Optional[str] = None
    author: Optional[str] = None
    tags: List[str] = Field(default=[])


class BrandKnowledgeUpdate(BaseModel):
    """更新品牌知識"""
    title: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    related_products: Optional[List[UUID]] = None
    related_categories: Optional[List[str]] = None
    credibility_score: Optional[int] = Field(default=None, ge=0, le=100)
    tags: Optional[List[str]] = None
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None


class BrandKnowledgeResponse(BaseModel):
    """品牌知識響應"""
    id: UUID
    knowledge_type: str
    title: str
    content: str
    summary: Optional[str] = None
    related_products: List[UUID] = Field(default=[])
    related_categories: List[str] = Field(default=[])
    credibility_score: Optional[int] = None
    source_type: str
    source_reference: Optional[str] = None
    author: Optional[str] = None
    tags: List[str] = Field(default=[])
    is_active: bool
    is_featured: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class BrandKnowledgeListResponse(BaseModel):
    """品牌知識列表響應"""
    data: List[BrandKnowledgeResponse]
    total: int


class ExpertContentRequest(BaseModel):
    """專家內容生成請求"""
    topic: str = Field(..., min_length=1)
    product_id: Optional[UUID] = None
    knowledge_type: str = Field(default="expert_claim")
    tone: str = Field(default="professional", description="professional, casual, authoritative")


# =============================================
# 內容審計
# =============================================

class ContentAuditRequest(BaseModel):
    """內容審計請求"""
    product_id: Optional[UUID] = None
    title: Optional[str] = None
    description: Optional[str] = None
    keywords: Optional[List[str]] = None
    audit_type: str = Field(default="full", description="full, title_only, description_only, keywords")


class AuditIssue(BaseModel):
    """審計問題"""
    type: str
    severity: str = Field(..., description="low, medium, high, critical")
    message: str
    field: Optional[str] = None


class AuditRecommendation(BaseModel):
    """審計建議"""
    priority: int = Field(..., ge=1, le=5)
    action: str
    expected_impact: str


class ContentAuditResponse(BaseModel):
    """內容審計響應"""
    id: UUID
    product_id: Optional[UUID] = None
    audit_type: str
    overall_score: int
    scores: Dict[str, int]
    issues: List[AuditIssue] = Field(default=[])
    recommendations: List[AuditRecommendation] = Field(default=[])
    audited_at: datetime

    model_config = {"from_attributes": True}


# =============================================
# 批量任務狀態
# =============================================

class SEOBatchProgress(BaseModel):
    """批量任務進度"""
    total: int
    completed: int
    failed: int
    percent: int


class SEOBatchTaskStatusResponse(BaseModel):
    """批量任務狀態響應"""
    task_id: str
    status: str = Field(..., description="pending / processing / completed / failed")
    progress: SEOBatchProgress
    results: List[SEOBatchResultItem] = Field(default=[])
