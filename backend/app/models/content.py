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


# 避免循環導入
from app.models.product import Product
