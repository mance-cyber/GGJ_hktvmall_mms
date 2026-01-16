# =============================================
# SEO & GEO 相關模型
# =============================================

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional, List

from sqlalchemy import String, Text, Integer, Boolean, ForeignKey, Index, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.database import Base, utcnow


class SEOContent(Base):
    """SEO 優化內容"""
    __tablename__ = "seo_contents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    product_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="SET NULL"),
        nullable=True
    )

    # =============================================
    # SEO 核心欄位
    # =============================================
    meta_title: Mapped[str] = mapped_column(
        String(70),
        nullable=False,
        comment="SEO 標題 (max 70 chars)"
    )
    meta_description: Mapped[str] = mapped_column(
        String(160),
        nullable=False,
        comment="SEO 描述 (max 160 chars)"
    )

    # =============================================
    # 關鍵詞
    # =============================================
    primary_keyword: Mapped[Optional[str]] = mapped_column(
        String(100),
        comment="主關鍵詞"
    )
    secondary_keywords: Mapped[Optional[list]] = mapped_column(
        JSONB,
        default=[],
        comment="次要關鍵詞列表 ['keyword1', 'keyword2']"
    )
    long_tail_keywords: Mapped[Optional[list]] = mapped_column(
        JSONB,
        default=[],
        comment="長尾關鍵詞 ['long tail 1', 'long tail 2']"
    )

    # =============================================
    # SEO 評分
    # =============================================
    seo_score: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment="SEO 總評分 0-100"
    )
    score_breakdown: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        comment="評分詳情 {title_score, desc_score, keyword_score, readability_score}"
    )
    improvement_suggestions: Mapped[Optional[list]] = mapped_column(
        JSONB,
        default=[],
        comment="改進建議列表"
    )

    # =============================================
    # 多語言 SEO
    # =============================================
    language: Mapped[str] = mapped_column(
        String(10),
        default="zh-HK",
        comment="主語言"
    )
    localized_seo: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        comment="多語言SEO {zh-HK: {title, desc}, en: {title, desc}}"
    )

    # =============================================
    # Open Graph & Social
    # =============================================
    og_title: Mapped[Optional[str]] = mapped_column(
        String(100),
        comment="Open Graph 標題"
    )
    og_description: Mapped[Optional[str]] = mapped_column(
        String(200),
        comment="Open Graph 描述"
    )
    og_image_url: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="Open Graph 圖片 URL"
    )

    # =============================================
    # 版本控制與狀態
    # =============================================
    version: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(
        String(50),
        default="draft",
        comment="draft, approved, published, rejected"
    )

    # =============================================
    # 生成元數據
    # =============================================
    generation_metadata: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        comment="生成元數據 {model, tokens_used, duration_ms}"
    )
    input_data: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        comment="生成時的輸入數據"
    )

    # =============================================
    # 時間戳
    # =============================================
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        default=utcnow,
        onupdate=utcnow
    )
    approved_at: Mapped[Optional[datetime]] = mapped_column()
    approved_by: Mapped[Optional[str]] = mapped_column(String(255))

    # =============================================
    # 關聯
    # =============================================
    product: Mapped[Optional["Product"]] = relationship(back_populates="seo_contents")

    __table_args__ = (
        Index("idx_seo_contents_product_id", "product_id"),
        Index("idx_seo_contents_primary_keyword", "primary_keyword"),
        Index("idx_seo_contents_status", "status"),
        Index("idx_seo_contents_language", "language"),
        Index("idx_seo_contents_seo_score", "seo_score"),
    )


class StructuredData(Base):
    """結構化數據 (Schema.org JSON-LD)"""
    __tablename__ = "structured_data"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    product_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="SET NULL"),
        nullable=True
    )

    # =============================================
    # Schema.org 類型
    # =============================================
    schema_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Product, FAQPage, BreadcrumbList, Organization, etc."
    )

    # =============================================
    # JSON-LD 數據
    # =============================================
    json_ld: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        comment="完整 JSON-LD 結構"
    )

    # =============================================
    # AI 搜索引擎優化 (GEO)
    # =============================================
    ai_summary: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="AI 搜索引擎友好摘要 (100字內)"
    )
    ai_facts: Mapped[Optional[list]] = mapped_column(
        JSONB,
        default=[],
        comment="結構化事實列表 ['fact1', 'fact2']"
    )
    ai_entities: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        comment="實體關聯 {brand: 'GogoJap', origin: '日本', ...}"
    )

    # =============================================
    # 驗證狀態
    # =============================================
    is_valid: Mapped[bool] = mapped_column(Boolean, default=True)
    validation_errors: Mapped[Optional[list]] = mapped_column(
        JSONB,
        default=[],
        comment="驗證錯誤列表"
    )
    last_validated_at: Mapped[Optional[datetime]] = mapped_column()

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
    product: Mapped[Optional["Product"]] = relationship(back_populates="structured_data")

    __table_args__ = (
        Index("idx_structured_data_product_id", "product_id"),
        Index("idx_structured_data_schema_type", "schema_type"),
        Index("idx_structured_data_is_valid", "is_valid"),
    )


class BrandKnowledge(Base):
    """品牌知識圖譜"""
    __tablename__ = "brand_knowledge"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # =============================================
    # 知識類型
    # =============================================
    knowledge_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="brand_info, product_fact, faq, expert_claim, testimonial"
    )

    # =============================================
    # 內容
    # =============================================
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[Optional[str]] = mapped_column(
        String(500),
        comment="簡短摘要"
    )

    # =============================================
    # 關聯實體
    # =============================================
    related_products: Mapped[Optional[list]] = mapped_column(
        JSONB,
        default=[],
        comment="關聯產品 ID 列表"
    )
    related_categories: Mapped[Optional[list]] = mapped_column(
        JSONB,
        default=[],
        comment="關聯分類"
    )

    # =============================================
    # 可信度與來源
    # =============================================
    credibility_score: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment="可信度評分 0-100"
    )
    source_type: Mapped[str] = mapped_column(
        String(50),
        default="internal",
        comment="internal, expert, verified, user_generated"
    )
    source_reference: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="來源引用/URL"
    )
    author: Mapped[Optional[str]] = mapped_column(
        String(255),
        comment="作者/專家名稱"
    )

    # =============================================
    # 標籤與搜索
    # =============================================
    tags: Mapped[Optional[list]] = mapped_column(
        JSONB,
        default=[],
        comment="標籤列表"
    )
    search_keywords: Mapped[Optional[list]] = mapped_column(
        JSONB,
        default=[],
        comment="搜索關鍵詞"
    )

    # =============================================
    # 狀態
    # =============================================
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_featured: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        comment="是否精選"
    )
    display_order: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment="顯示順序"
    )

    # =============================================
    # 時間戳
    # =============================================
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        default=utcnow,
        onupdate=utcnow
    )

    __table_args__ = (
        Index("idx_brand_knowledge_type", "knowledge_type"),
        Index("idx_brand_knowledge_is_active", "is_active"),
        Index("idx_brand_knowledge_is_featured", "is_featured"),
        Index("idx_brand_knowledge_tags", "tags", postgresql_using='gin'),
    )


class KeywordResearch(Base):
    """關鍵詞研究數據"""
    __tablename__ = "keyword_research"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # =============================================
    # 關鍵詞
    # =============================================
    keyword: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True
    )
    keyword_normalized: Mapped[Optional[str]] = mapped_column(
        String(255),
        comment="標準化關鍵詞 (小寫、去空格)"
    )

    # =============================================
    # 搜索數據
    # =============================================
    search_volume: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment="月搜索量"
    )
    difficulty: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment="競爭難度 0-100"
    )
    cpc: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2),
        comment="每次點擊成本 (HKD)"
    )
    competition_level: Mapped[Optional[str]] = mapped_column(
        String(20),
        comment="競爭程度: low, medium, high"
    )

    # =============================================
    # 趨勢數據
    # =============================================
    trend_data: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        comment="趨勢數據 {2024-01: 1000, 2024-02: 1200, ...}"
    )
    trend_direction: Mapped[Optional[str]] = mapped_column(
        String(20),
        comment="趨勢方向: rising, stable, declining"
    )
    seasonality: Mapped[Optional[str]] = mapped_column(
        String(50),
        comment="季節性標籤: all_year, winter, summer, holiday"
    )

    # =============================================
    # 相關詞
    # =============================================
    related_keywords: Mapped[Optional[list]] = mapped_column(
        JSONB,
        default=[],
        comment="相關關鍵詞"
    )
    long_tail_variants: Mapped[Optional[list]] = mapped_column(
        JSONB,
        default=[],
        comment="長尾變體"
    )

    # =============================================
    # 分類與意圖
    # =============================================
    category: Mapped[Optional[str]] = mapped_column(String(100))
    subcategory: Mapped[Optional[str]] = mapped_column(String(100))
    intent: Mapped[Optional[str]] = mapped_column(
        String(50),
        comment="搜索意圖: informational, transactional, navigational, commercial"
    )

    # =============================================
    # 數據來源
    # =============================================
    data_source: Mapped[str] = mapped_column(
        String(50),
        default="ai_generated",
        comment="google_trends, gsc, semrush, ai_generated, manual"
    )
    source_confidence: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment="數據可信度 0-100"
    )

    # =============================================
    # 時間戳
    # =============================================
    last_updated: Mapped[datetime] = mapped_column(default=utcnow)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)

    __table_args__ = (
        Index("idx_keyword_research_keyword", "keyword"),
        Index("idx_keyword_research_category", "category"),
        Index("idx_keyword_research_volume", "search_volume"),
        Index("idx_keyword_research_intent", "intent"),
        Index("idx_keyword_research_difficulty", "difficulty"),
    )


class ContentAudit(Base):
    """內容 SEO 審計記錄"""
    __tablename__ = "content_audits"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    product_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="SET NULL"),
        nullable=True
    )

    # =============================================
    # 審計結果
    # =============================================
    audit_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="full, title_only, description_only, keywords"
    )
    overall_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="總評分 0-100"
    )

    # =============================================
    # 分項評分
    # =============================================
    scores: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        comment="{title: 80, description: 70, keywords: 60, readability: 75, ...}"
    )

    # =============================================
    # 問題與建議
    # =============================================
    issues: Mapped[Optional[list]] = mapped_column(
        JSONB,
        default=[],
        comment="發現的問題列表 [{type, severity, message}]"
    )
    recommendations: Mapped[Optional[list]] = mapped_column(
        JSONB,
        default=[],
        comment="改進建議列表 [{priority, action, expected_impact}]"
    )

    # =============================================
    # 對比數據
    # =============================================
    competitor_comparison: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        comment="與競品對比數據"
    )
    industry_benchmark: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        comment="行業基準對比"
    )

    # =============================================
    # 時間戳
    # =============================================
    audited_at: Mapped[datetime] = mapped_column(default=utcnow)

    # =============================================
    # 關聯
    # =============================================
    product: Mapped[Optional["Product"]] = relationship()

    __table_args__ = (
        Index("idx_content_audits_product_id", "product_id"),
        Index("idx_content_audits_overall_score", "overall_score"),
        Index("idx_content_audits_audited_at", "audited_at"),
    )


# =============================================
# 避免循環導入
# =============================================
from app.models.product import Product
