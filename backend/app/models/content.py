# =============================================
# AI 內容相關模型
# =============================================

import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Integer, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.database import Base, utcnow


class AIContent(Base):
    """AI 生成的內容"""
    __tablename__ = "ai_contents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="SET NULL"))
    content_type: Mapped[str] = mapped_column(String(50), nullable=False, comment="title, description, selling_points, full_copy")
    style: Mapped[Optional[str]] = mapped_column(String(50), comment="formal, casual, playful, professional")
    language: Mapped[str] = mapped_column(String(10), default="zh-HK")
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_json: Mapped[Optional[dict]] = mapped_column(JSONB, comment="結構化內容")
    version: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(50), default="draft", comment="draft, approved, published, rejected")
    generation_metadata: Mapped[Optional[dict]] = mapped_column(JSONB, comment="tokens_used, model, duration_ms")
    input_data: Mapped[Optional[dict]] = mapped_column(JSONB, comment="生成時的輸入資料")
    generated_at: Mapped[datetime] = mapped_column(default=utcnow)
    approved_at: Mapped[Optional[datetime]] = mapped_column()
    approved_by: Mapped[Optional[str]] = mapped_column(String(255))
    rejected_reason: Mapped[Optional[str]] = mapped_column(Text)

    # 關聯
    product: Mapped[Optional["Product"]] = relationship(back_populates="ai_contents")

    __table_args__ = (
        Index("idx_ai_contents_product_id", "product_id"),
        Index("idx_ai_contents_status", "status"),
        Index("idx_ai_contents_type", "content_type"),
    )


class PipelineSession(Base):
    """內容流水線生成會話"""
    __tablename__ = "pipeline_sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="SET NULL"))

    # 輸入資料
    product_name: Mapped[str] = mapped_column(String(255), nullable=False, comment="產品名稱")
    product_info: Mapped[Optional[dict]] = mapped_column(JSONB, comment="完整產品資訊")
    languages: Mapped[list] = mapped_column(JSONB, default=["zh-HK"], comment="生成的語言列表")
    tone: Mapped[str] = mapped_column(String(50), default="professional", comment="語調風格")

    # 生成結果引用
    content_ids: Mapped[Optional[dict]] = mapped_column(JSONB, comment="AIContent IDs {lang: id}")
    seo_content_ids: Mapped[Optional[dict]] = mapped_column(JSONB, comment="SEOContent IDs {lang: id}")
    structured_data_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), comment="StructuredData ID")

    # 結果預覽（用於列表快速顯示）
    preview_title: Mapped[Optional[str]] = mapped_column(String(255), comment="預覽標題（第一語言）")
    preview_seo_score: Mapped[Optional[int]] = mapped_column(Integer, comment="預覽 SEO 分數")

    # 元數據
    generation_time_ms: Mapped[int] = mapped_column(Integer, default=0, comment="生成耗時（毫秒）")
    model_used: Mapped[Optional[str]] = mapped_column(String(100), comment="使用的模型")
    is_batch: Mapped[bool] = mapped_column(default=False, comment="是否批量生成")
    batch_index: Mapped[Optional[int]] = mapped_column(Integer, comment="批量生成中的索引")

    # 時間戳
    created_at: Mapped[datetime] = mapped_column(default=utcnow)

    # 關聯
    product: Mapped[Optional["Product"]] = relationship()

    __table_args__ = (
        Index("idx_pipeline_sessions_product_id", "product_id"),
        Index("idx_pipeline_sessions_created_at", "created_at"),
        Index("idx_pipeline_sessions_is_batch", "is_batch"),
    )


# 避免循環導入
from app.models.product import Product
