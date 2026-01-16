# =============================================
# 批次導入任務模型
# =============================================

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
import uuid

from sqlalchemy import Column, String, Integer, Boolean, Text, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.models.database import Base, utcnow


class ImportJob(Base):
    """批次導入任務"""

    __tablename__ = "import_jobs"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    competitor_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("competitors.id", ondelete="SET NULL"), nullable=True
    )

    # 任務狀態
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="pending"
    )  # pending, processing, completed, failed, cancelled

    # 導入來源
    source_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # file, url_list, discovery
    source_data: Mapped[Optional[Dict]] = mapped_column(JSONB, nullable=True)

    # 處理統計
    total_urls: Mapped[int] = mapped_column(Integer, default=0)
    processed_urls: Mapped[int] = mapped_column(Integer, default=0)
    successful_urls: Mapped[int] = mapped_column(Integer, default=0)
    failed_urls: Mapped[int] = mapped_column(Integer, default=0)
    duplicate_urls: Mapped[int] = mapped_column(Integer, default=0)

    # 驗證結果
    validation_errors: Mapped[List] = mapped_column(JSONB, default=list)

    # 時間戳
    started_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)

    # 關聯
    competitor = relationship("Competitor", back_populates="import_jobs")
    items = relationship(
        "ImportJobItem", back_populates="import_job", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_import_jobs_status", "status"),
        Index("idx_import_jobs_competitor_id", "competitor_id"),
        Index("idx_import_jobs_created_at", "created_at"),
    )

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "id": str(self.id),
            "name": self.name,
            "competitor_id": str(self.competitor_id) if self.competitor_id else None,
            "status": self.status,
            "source_type": self.source_type,
            "source_data": self.source_data,
            "total_urls": self.total_urls,
            "processed_urls": self.processed_urls,
            "successful_urls": self.successful_urls,
            "failed_urls": self.failed_urls,
            "duplicate_urls": self.duplicate_urls,
            "validation_errors": self.validation_errors,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "progress_percent": (
                round(self.processed_urls / self.total_urls * 100, 1)
                if self.total_urls > 0
                else 0
            ),
        }


class ImportJobItem(Base):
    """導入任務項目"""

    __tablename__ = "import_job_items"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    import_job_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("import_jobs.id", ondelete="CASCADE"), nullable=False
    )

    url: Mapped[str] = mapped_column(String(2000), nullable=False)
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="pending"
    )  # pending, processing, success, failed, duplicate, skipped

    # 結果
    competitor_product_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("competitor_products.id", ondelete="SET NULL"),
        nullable=True,
    )
    extracted_data: Mapped[Optional[Dict]] = mapped_column(JSONB, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # 處理時間
    processed_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)

    # 關聯
    import_job = relationship("ImportJob", back_populates="items")
    competitor_product = relationship("CompetitorProduct")

    __table_args__ = (
        Index("idx_import_job_items_job_id", "import_job_id"),
        Index("idx_import_job_items_status", "status"),
    )

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "id": str(self.id),
            "import_job_id": str(self.import_job_id),
            "url": self.url,
            "status": self.status,
            "competitor_product_id": (
                str(self.competitor_product_id) if self.competitor_product_id else None
            ),
            "extracted_data": self.extracted_data,
            "error_message": self.error_message,
            "processed_at": self.processed_at.isoformat() if self.processed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
