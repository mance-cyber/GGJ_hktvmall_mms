# =============================================
# 工作流模型
# 排程報告、執行記錄、告警配置
# =============================================

import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Text, Boolean, ForeignKey, Integer, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from enum import Enum

from app.models.database import Base, utcnow


# =============================================
# 枚舉類型
# =============================================

class ScheduleFrequency(str, Enum):
    """排程頻率"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"  # cron 表達式


class ScheduleStatus(str, Enum):
    """排程狀態"""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"  # 一次性任務完成
    FAILED = "failed"       # 多次失敗後停用


class ExecutionStatus(str, Enum):
    """執行狀態"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class ReportType(str, Enum):
    """報告類型"""
    PRICE_ANALYSIS = "price_analysis"
    COMPETITOR_REPORT = "competitor_report"
    SALES_SUMMARY = "sales_summary"
    INVENTORY_ALERT = "inventory_alert"
    CUSTOM = "custom"


class DeliveryChannel(str, Enum):
    """交付渠道"""
    TELEGRAM = "telegram"
    EMAIL = "email"
    WEBHOOK = "webhook"
    IN_APP = "in_app"


# =============================================
# ScheduledReport 模型
# =============================================

class ScheduledReport(Base):
    """
    排程報告

    用戶可以通過 AI 對話創建自動化報告：
    - 「每日早上 9 點發送和牛價格報告」
    - 「每週一生成競品分析」
    """
    __tablename__ = "scheduled_reports"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    # 基本信息
    name: Mapped[str] = mapped_column(
        String(200),
        comment="排程名稱"
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="排程描述"
    )

    # 報告配置
    report_type: Mapped[str] = mapped_column(
        String(50),
        default=ReportType.PRICE_ANALYSIS.value,
        comment="報告類型"
    )
    report_config: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="報告配置 (產品、篩選條件等)"
    )

    # 排程配置
    frequency: Mapped[str] = mapped_column(
        String(20),
        default=ScheduleFrequency.DAILY.value,
        comment="頻率: daily, weekly, monthly, custom"
    )
    cron_expression: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Cron 表達式 (frequency=custom 時使用)"
    )
    schedule_time: Mapped[Optional[str]] = mapped_column(
        String(10),
        nullable=True,
        comment="執行時間 HH:MM 格式"
    )
    schedule_day: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="執行日期 (週幾 1-7 或 月幾號 1-31)"
    )
    timezone: Mapped[str] = mapped_column(
        String(50),
        default="Asia/Hong_Kong",
        comment="時區"
    )

    # 交付配置
    delivery_channels: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="交付渠道配置 {telegram: {chat_id}, email: {to}}"
    )

    # 狀態
    status: Mapped[str] = mapped_column(
        String(20),
        default=ScheduleStatus.ACTIVE.value,
        index=True,
        comment="狀態"
    )

    # 執行統計
    last_run_at: Mapped[Optional[datetime]] = mapped_column(
        nullable=True,
        comment="上次執行時間"
    )
    next_run_at: Mapped[Optional[datetime]] = mapped_column(
        nullable=True,
        index=True,
        comment="下次執行時間"
    )
    run_count: Mapped[int] = mapped_column(
        default=0,
        comment="總執行次數"
    )
    success_count: Mapped[int] = mapped_column(
        default=0,
        comment="成功次數"
    )
    failure_count: Mapped[int] = mapped_column(
        default=0,
        comment="失敗次數"
    )
    consecutive_failures: Mapped[int] = mapped_column(
        default=0,
        comment="連續失敗次數 (用於自動暫停)"
    )

    # 來源追溯
    source_conversation_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
        comment="來源對話 ID"
    )
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        comment="創建者"
    )

    # 時間戳
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow, onupdate=utcnow)

    # 關聯
    executions: Mapped[List["ReportExecution"]] = relationship(
        back_populates="schedule",
        cascade="all, delete-orphan"
    )


# =============================================
# ReportExecution 模型
# =============================================

class ReportExecution(Base):
    """
    報告執行記錄

    每次排程執行都會創建一條記錄，用於：
    - 追蹤執行歷史
    - 調試失敗原因
    - 查看生成的報告內容
    """
    __tablename__ = "report_executions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    # 關聯排程
    schedule_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("scheduled_reports.id", ondelete="CASCADE"),
        index=True
    )

    # 執行狀態
    status: Mapped[str] = mapped_column(
        String(20),
        default=ExecutionStatus.PENDING.value,
        index=True,
        comment="執行狀態"
    )

    # 執行時間
    scheduled_at: Mapped[datetime] = mapped_column(
        comment="計劃執行時間"
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(
        nullable=True,
        comment="實際開始時間"
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        nullable=True,
        comment="完成時間"
    )
    duration_ms: Mapped[Optional[int]] = mapped_column(
        nullable=True,
        comment="執行耗時 (毫秒)"
    )

    # 報告內容
    report_content: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="生成的報告內容 (Markdown)"
    )
    report_data: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="報告數據 (JSON)"
    )

    # 交付狀態
    delivery_status: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="各渠道交付狀態 {telegram: {sent: true, message_id: 123}}"
    )

    # 錯誤信息
    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="錯誤信息"
    )
    error_details: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="錯誤詳情"
    )

    # 重試
    retry_count: Mapped[int] = mapped_column(
        default=0,
        comment="重試次數"
    )

    # 時間戳
    created_at: Mapped[datetime] = mapped_column(default=utcnow)

    # 關聯
    schedule: Mapped["ScheduledReport"] = relationship(back_populates="executions")


# =============================================
# AlertWorkflowConfig 模型 (Phase 3 預備)
# =============================================

class AlertWorkflowConfig(Base):
    """
    告警工作流配置

    定義價格告警觸發時的自動化動作：
    - 自動 AI 分析
    - 自動創建改價提案
    - 通知配置
    """
    __tablename__ = "alert_workflow_configs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    # 基本信息
    name: Mapped[str] = mapped_column(
        String(200),
        comment="配置名稱"
    )
    is_active: Mapped[bool] = mapped_column(
        default=True,
        index=True,
        comment="是否啟用"
    )

    # 觸發條件
    trigger_conditions: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="觸發條件 {price_drop_threshold: 10, categories: [...]}"
    )

    # 動作配置
    auto_analyze: Mapped[bool] = mapped_column(
        default=True,
        comment="自動執行 AI 分析"
    )
    auto_create_proposal: Mapped[bool] = mapped_column(
        default=False,
        comment="自動創建改價提案"
    )
    notify_channels: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="通知渠道配置"
    )

    # 靜默時段
    quiet_hours_start: Mapped[Optional[str]] = mapped_column(
        String(10),
        nullable=True,
        comment="靜默開始時間 HH:MM"
    )
    quiet_hours_end: Mapped[Optional[str]] = mapped_column(
        String(10),
        nullable=True,
        comment="靜默結束時間 HH:MM"
    )

    # 時間戳
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow, onupdate=utcnow)
