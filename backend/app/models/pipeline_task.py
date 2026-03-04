# =============================================
# 建庫管線任務模型
# =============================================
# 持久化管線進度到 DB，伺服器重啟後狀態不丟失

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.database import Base, utcnow


class PipelineTask(Base):
    """建庫管線任務狀態（DB 持久化）"""
    __tablename__ = "pipeline_tasks"

    id: Mapped[str] = mapped_column(String(16), primary_key=True)
    platform: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="running",
        comment="running | done | error",
    )
    current_step: Mapped[Optional[str]] = mapped_column(String(20))
    current_step_number: Mapped[int] = mapped_column(Integer, default=0)
    step_results: Mapped[dict] = mapped_column(JSONB, default=dict)
    step_errors: Mapped[dict] = mapped_column(JSONB, default=dict)
    step_durations: Mapped[dict] = mapped_column(JSONB, default=dict)
    step_started_at: Mapped[Optional[datetime]] = mapped_column()
    progress: Mapped[Optional[dict]] = mapped_column(
        JSONB, default=None,
        comment="當前步驟即時進度，如 {current: 3, total: 15, message: '...'}",
    )
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow, onupdate=utcnow)

    __table_args__ = (
        Index("idx_pipeline_tasks_status", "status"),
        Index("idx_pipeline_tasks_created_at", "created_at"),
    )
