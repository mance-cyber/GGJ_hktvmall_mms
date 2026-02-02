# =============================================
# 工作流 Schema
# =============================================

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, Field


# =============================================
# 枚舉值常量
# =============================================

class ScheduleFrequency:
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


class ScheduleStatus:
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class ExecutionStatus:
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class ReportType:
    PRICE_ANALYSIS = "price_analysis"
    COMPETITOR_REPORT = "competitor_report"
    SALES_SUMMARY = "sales_summary"
    INVENTORY_ALERT = "inventory_alert"
    CUSTOM = "custom"


# =============================================
# ScheduledReport Schemas
# =============================================

class ScheduleBase(BaseModel):
    """排程基礎 Schema"""
    name: str = Field(..., min_length=1, max_length=200, description="排程名稱")
    description: Optional[str] = Field(None, max_length=1000, description="排程描述")
    report_type: str = Field(default=ReportType.PRICE_ANALYSIS, description="報告類型")
    report_config: Optional[Dict[str, Any]] = Field(None, description="報告配置")
    frequency: str = Field(default=ScheduleFrequency.DAILY, description="頻率")
    schedule_time: Optional[str] = Field("09:00", pattern=r"^\d{2}:\d{2}$", description="執行時間 HH:MM")
    schedule_day: Optional[int] = Field(None, ge=1, le=31, description="執行日期")
    cron_expression: Optional[str] = Field(None, max_length=100, description="Cron 表達式")
    timezone: str = Field(default="Asia/Hong_Kong", description="時區")
    delivery_channels: Optional[Dict[str, Any]] = Field(None, description="交付渠道配置")


class ScheduleCreate(ScheduleBase):
    """創建排程請求"""
    pass


class ScheduleUpdate(BaseModel):
    """更新排程請求"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    report_type: Optional[str] = None
    report_config: Optional[Dict[str, Any]] = None
    frequency: Optional[str] = None
    schedule_time: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")
    schedule_day: Optional[int] = Field(None, ge=1, le=31)
    cron_expression: Optional[str] = Field(None, max_length=100)
    timezone: Optional[str] = None
    delivery_channels: Optional[Dict[str, Any]] = None
    status: Optional[str] = None


class ScheduleResponse(ScheduleBase):
    """排程響應"""
    id: UUID
    status: str
    last_run_at: Optional[datetime] = None
    next_run_at: Optional[datetime] = None
    run_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    consecutive_failures: int = 0
    source_conversation_id: Optional[str] = None
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ScheduleListResponse(BaseModel):
    """排程列表響應"""
    items: List[ScheduleResponse]
    total: int
    limit: int
    offset: int


# =============================================
# ReportExecution Schemas
# =============================================

class ExecutionResponse(BaseModel):
    """執行記錄響應"""
    id: UUID
    schedule_id: UUID
    status: str
    scheduled_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_ms: Optional[int] = None
    report_content: Optional[str] = None
    report_data: Optional[Dict[str, Any]] = None
    delivery_status: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


class ExecutionListResponse(BaseModel):
    """執行記錄列表響應"""
    items: List[ExecutionResponse]
    total: int


# =============================================
# 操作響應
# =============================================

class ScheduleActionResponse(BaseModel):
    """排程操作響應"""
    success: bool
    message: str
    schedule: Optional[ScheduleResponse] = None


class TriggerResponse(BaseModel):
    """觸發執行響應"""
    success: bool
    message: str
    execution_id: Optional[UUID] = None
    task_id: Optional[str] = None


# =============================================
# 預覽
# =============================================

class NextRunsPreview(BaseModel):
    """下次執行時間預覽"""
    schedule_id: UUID
    next_runs: List[datetime]


# =============================================
# AlertWorkflowConfig Schemas
# =============================================

class AlertConfigBase(BaseModel):
    """告警工作流配置基礎 Schema"""
    name: str = Field(..., min_length=1, max_length=200, description="配置名稱")
    is_active: bool = Field(default=True, description="是否啟用")
    trigger_conditions: Optional[Dict[str, Any]] = Field(
        None,
        description="觸發條件 {price_drop_threshold: 10, categories: [...]}"
    )
    auto_analyze: bool = Field(default=True, description="自動執行 AI 分析")
    auto_create_proposal: bool = Field(default=False, description="自動創建改價提案")
    notify_channels: Optional[Dict[str, Any]] = Field(
        None,
        description="通知渠道配置 {telegram: {enabled: true}, email: {...}}"
    )
    quiet_hours_start: Optional[str] = Field(
        None,
        pattern=r"^\d{2}:\d{2}$",
        description="靜默開始時間 HH:MM"
    )
    quiet_hours_end: Optional[str] = Field(
        None,
        pattern=r"^\d{2}:\d{2}$",
        description="靜默結束時間 HH:MM"
    )


class AlertConfigCreate(AlertConfigBase):
    """創建告警配置請求"""
    pass


class AlertConfigUpdate(BaseModel):
    """更新告警配置請求"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    is_active: Optional[bool] = None
    trigger_conditions: Optional[Dict[str, Any]] = None
    auto_analyze: Optional[bool] = None
    auto_create_proposal: Optional[bool] = None
    notify_channels: Optional[Dict[str, Any]] = None
    quiet_hours_start: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")
    quiet_hours_end: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")


class AlertConfigResponse(AlertConfigBase):
    """告警配置響應"""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AlertConfigListResponse(BaseModel):
    """告警配置列表響應"""
    items: List[AlertConfigResponse]
    total: int
