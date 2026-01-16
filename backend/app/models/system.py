# =============================================
# 系統相關模型
# =============================================

import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Integer, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.database import Base, utcnow


class ScrapeLog(Base):
    """爬取任務日誌"""
    __tablename__ = "scrape_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id: Mapped[Optional[str]] = mapped_column(String(255), comment="Celery task ID")
    task_type: Mapped[Optional[str]] = mapped_column(String(50), comment="competitor_scrape, full_scrape, single_product")
    competitor_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("competitors.id", ondelete="SET NULL"))
    status: Mapped[str] = mapped_column(String(50), nullable=False, comment="pending, running, success, partial, failed")
    products_total: Mapped[int] = mapped_column(Integer, default=0)
    products_scraped: Mapped[int] = mapped_column(Integer, default=0)
    products_failed: Mapped[int] = mapped_column(Integer, default=0)
    errors: Mapped[Optional[list]] = mapped_column(JSONB)
    started_at: Mapped[Optional[datetime]] = mapped_column()
    completed_at: Mapped[Optional[datetime]] = mapped_column()
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)

    __table_args__ = (
        Index("idx_scrape_logs_status", "status"),
        Index("idx_scrape_logs_created_at", "created_at"),
    )


class SyncLog(Base):
    """HKTVmall 同步日誌"""
    __tablename__ = "sync_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id: Mapped[Optional[str]] = mapped_column(String(255))
    sync_type: Mapped[Optional[str]] = mapped_column(String(50), comment="products, orders, inventory")
    source: Mapped[Optional[str]] = mapped_column(String(50), comment="hktv_mms")
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    records_total: Mapped[int] = mapped_column(Integer, default=0)
    records_synced: Mapped[int] = mapped_column(Integer, default=0)
    records_failed: Mapped[int] = mapped_column(Integer, default=0)
    errors: Mapped[Optional[list]] = mapped_column(JSONB)
    started_at: Mapped[Optional[datetime]] = mapped_column()
    completed_at: Mapped[Optional[datetime]] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=utcnow)


class Settings(Base):
    """系統設定（JSON 格式）"""
    __tablename__ = "settings"

    key: Mapped[str] = mapped_column(String(255), primary_key=True)
    value: Mapped[dict] = mapped_column(JSONB, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow, onupdate=utcnow)


class SystemSetting(Base):
    """系統設定（字符串格式，用於簡單配置）"""
    __tablename__ = "system_settings"

    key: Mapped[str] = mapped_column(String(255), primary_key=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow, onupdate=utcnow)
