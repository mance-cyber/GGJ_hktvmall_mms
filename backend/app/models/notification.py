# =============================================
# 通知與 Webhook 模型
# =============================================

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
import uuid

from sqlalchemy import Column, String, Integer, Boolean, Text, Index
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.database import Base


class Notification(Base):
    """系統通知"""

    __tablename__ = "notifications"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # price_alert, scrape_complete, scrape_failed, report_ready, import_complete

    # 關聯
    related_type: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True
    )  # price_alert, scrape_log, market_report, import_job
    related_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)

    # 內容
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    data: Mapped[Optional[Dict]] = mapped_column(JSONB, nullable=True)

    # 發送狀態
    channels: Mapped[List] = mapped_column(JSONB, default=lambda: ["in_app"])
    sent_at: Mapped[Dict] = mapped_column(JSONB, default=dict)

    # 已讀狀態
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    read_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    __table_args__ = (
        Index("idx_notifications_created_at", "created_at"),
        Index("idx_notifications_is_read", "is_read"),
        Index("idx_notifications_type", "type"),
    )

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "id": str(self.id),
            "type": self.type,
            "related_type": self.related_type,
            "related_id": str(self.related_id) if self.related_id else None,
            "title": self.title,
            "message": self.message,
            "data": self.data,
            "channels": self.channels,
            "sent_at": self.sent_at,
            "is_read": self.is_read,
            "read_at": self.read_at.isoformat() if self.read_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Webhook(Base):
    """Webhook 配置"""

    __tablename__ = "webhooks"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(String(1000), nullable=False)
    secret: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # 訂閱事件
    events: Mapped[List] = mapped_column(
        JSONB, nullable=False, default=lambda: ["price_alert"]
    )

    # 狀態
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_triggered_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    last_status_code: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    failure_count: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow
    )

    __table_args__ = (Index("idx_webhooks_is_active", "is_active"),)

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "id": str(self.id),
            "name": self.name,
            "url": self.url,
            "secret": "***" if self.secret else None,  # 隱藏 secret
            "events": self.events,
            "is_active": self.is_active,
            "last_triggered_at": (
                self.last_triggered_at.isoformat() if self.last_triggered_at else None
            ),
            "last_status_code": self.last_status_code,
            "failure_count": self.failure_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
