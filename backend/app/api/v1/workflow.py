# =============================================
# 工作流 API 路由
# =============================================

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import get_db
from app.models.workflow import ScheduledReport, ReportExecution, ScheduleStatus, AlertWorkflowConfig
from app.services.workflow.scheduler import SchedulerService
from app.schemas.workflow import (
    ScheduleCreate,
    ScheduleUpdate,
    ScheduleResponse,
    ScheduleListResponse,
    ScheduleActionResponse,
    ExecutionResponse,
    ExecutionListResponse,
    TriggerResponse,
    NextRunsPreview,
    AlertConfigCreate,
    AlertConfigUpdate,
    AlertConfigResponse,
    AlertConfigListResponse,
)

router = APIRouter(prefix="/workflow", tags=["workflow"])


# =============================================
# Schedule CRUD
# =============================================

@router.get("/schedules", response_model=ScheduleListResponse)
async def list_schedules(
    status: Optional[str] = Query(None, description="篩選狀態"),
    conversation_id: Optional[str] = Query(None, description="篩選對話 ID"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """
    列出排程

    - **status**: 篩選狀態 (active/paused/completed/failed)
    - **conversation_id**: 篩選來源對話
    - **limit**: 返回數量
    - **offset**: 偏移量
    """
    scheduler = SchedulerService(db)
    schedules = await scheduler.list_schedules(
        status=status,
        conversation_id=conversation_id,
        limit=limit,
        offset=offset,
    )

    return ScheduleListResponse(
        items=[ScheduleResponse.model_validate(s) for s in schedules],
        total=len(schedules),  # TODO: 實現真正的 count
        limit=limit,
        offset=offset,
    )


@router.post("/schedules", response_model=ScheduleResponse, status_code=status.HTTP_201_CREATED)
async def create_schedule(
    data: ScheduleCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    創建排程

    創建一個新的定時報告排程。
    """
    scheduler = SchedulerService(db)

    schedule = await scheduler.create_schedule(
        name=data.name,
        description=data.description,
        report_type=data.report_type,
        report_config=data.report_config,
        frequency=data.frequency,
        schedule_time=data.schedule_time,
        schedule_day=data.schedule_day,
        cron_expression=data.cron_expression,
        timezone=data.timezone,
        delivery_channels=data.delivery_channels,
    )

    return ScheduleResponse.model_validate(schedule)


@router.get("/schedules/{schedule_id}", response_model=ScheduleResponse)
async def get_schedule(
    schedule_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    獲取排程詳情
    """
    scheduler = SchedulerService(db)
    schedule = await scheduler.get_schedule(schedule_id)

    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )

    return ScheduleResponse.model_validate(schedule)


@router.patch("/schedules/{schedule_id}", response_model=ScheduleResponse)
async def update_schedule(
    schedule_id: UUID,
    data: ScheduleUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    更新排程

    更新排程配置。可以更新部分字段。
    """
    scheduler = SchedulerService(db)

    # 過濾掉 None 值
    updates = {k: v for k, v in data.model_dump().items() if v is not None}

    schedule = await scheduler.update_schedule(schedule_id, **updates)

    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )

    return ScheduleResponse.model_validate(schedule)


@router.delete("/schedules/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_schedule(
    schedule_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    刪除排程

    刪除排程及其所有執行記錄。
    """
    scheduler = SchedulerService(db)
    deleted = await scheduler.delete_schedule(schedule_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )


# =============================================
# Schedule Actions
# =============================================

@router.post("/schedules/{schedule_id}/pause", response_model=ScheduleActionResponse)
async def pause_schedule(
    schedule_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    暫停排程

    暫停後排程不會執行，直到恢復。
    """
    scheduler = SchedulerService(db)
    schedule = await scheduler.pause_schedule(schedule_id)

    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )

    return ScheduleActionResponse(
        success=True,
        message="排程已暫停",
        schedule=ScheduleResponse.model_validate(schedule),
    )


@router.post("/schedules/{schedule_id}/resume", response_model=ScheduleActionResponse)
async def resume_schedule(
    schedule_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    恢復排程

    恢復後排程將重新開始執行。
    """
    scheduler = SchedulerService(db)
    schedule = await scheduler.resume_schedule(schedule_id)

    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )

    return ScheduleActionResponse(
        success=True,
        message="排程已恢復",
        schedule=ScheduleResponse.model_validate(schedule),
    )


@router.post("/schedules/{schedule_id}/trigger", response_model=TriggerResponse)
async def trigger_schedule(
    schedule_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    立即觸發排程

    手動觸發一次執行，不影響正常排程。
    """
    from app.tasks.workflow_tasks import execute_scheduled_report

    scheduler = SchedulerService(db)
    schedule = await scheduler.get_schedule(schedule_id)

    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )

    # 觸發 Celery 任務
    task = execute_scheduled_report.delay(str(schedule_id))

    return TriggerResponse(
        success=True,
        message="排程已觸發執行",
        task_id=task.id,
    )


@router.get("/schedules/{schedule_id}/preview", response_model=NextRunsPreview)
async def preview_next_runs(
    schedule_id: UUID,
    count: int = Query(5, ge=1, le=20, description="預覽數量"),
    db: AsyncSession = Depends(get_db),
):
    """
    預覽下次執行時間

    預覽未來幾次的執行時間。
    """
    scheduler = SchedulerService(db)
    schedule = await scheduler.get_schedule(schedule_id)

    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )

    next_runs = scheduler.calculate_next_runs(schedule, count=count)

    return NextRunsPreview(
        schedule_id=schedule_id,
        next_runs=next_runs,
    )


# =============================================
# Execution History
# =============================================

@router.get("/executions", response_model=ExecutionListResponse)
async def list_executions(
    schedule_id: Optional[UUID] = Query(None, description="篩選排程 ID"),
    status: Optional[str] = Query(None, description="篩選狀態"),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """
    列出執行記錄

    獲取排程執行歷史。
    """
    from sqlalchemy import select, and_

    query = select(ReportExecution)

    conditions = []
    if schedule_id:
        conditions.append(ReportExecution.schedule_id == schedule_id)
    if status:
        conditions.append(ReportExecution.status == status)

    if conditions:
        query = query.where(and_(*conditions))

    query = query.order_by(ReportExecution.created_at.desc()).limit(limit)

    result = await db.execute(query)
    executions = result.scalars().all()

    return ExecutionListResponse(
        items=[ExecutionResponse.model_validate(e) for e in executions],
        total=len(executions),
    )


@router.get("/executions/{execution_id}", response_model=ExecutionResponse)
async def get_execution(
    execution_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    獲取執行記錄詳情
    """
    execution = await db.get(ReportExecution, execution_id)

    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Execution not found"
        )

    return ExecutionResponse.model_validate(execution)


# =============================================
# Alert Workflow Config CRUD
# =============================================

@router.get("/alert-configs", response_model=AlertConfigListResponse)
async def list_alert_configs(
    is_active: Optional[bool] = Query(None, description="篩選啟用狀態"),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """
    列出告警工作流配置

    - **is_active**: 篩選啟用狀態
    - **limit**: 返回數量
    """
    from sqlalchemy import select

    query = select(AlertWorkflowConfig)

    if is_active is not None:
        query = query.where(AlertWorkflowConfig.is_active == is_active)

    query = query.order_by(AlertWorkflowConfig.created_at.desc()).limit(limit)

    result = await db.execute(query)
    configs = result.scalars().all()

    return AlertConfigListResponse(
        items=[AlertConfigResponse.model_validate(c) for c in configs],
        total=len(configs),
    )


@router.post("/alert-configs", response_model=AlertConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_alert_config(
    data: AlertConfigCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    創建告警工作流配置

    配置價格告警觸發時的自動化動作。
    """
    config = AlertWorkflowConfig(
        name=data.name,
        is_active=data.is_active,
        trigger_conditions=data.trigger_conditions,
        auto_analyze=data.auto_analyze,
        auto_create_proposal=data.auto_create_proposal,
        notify_channels=data.notify_channels,
        quiet_hours_start=data.quiet_hours_start,
        quiet_hours_end=data.quiet_hours_end,
    )

    db.add(config)
    await db.commit()
    await db.refresh(config)

    return AlertConfigResponse.model_validate(config)


@router.get("/alert-configs/{config_id}", response_model=AlertConfigResponse)
async def get_alert_config(
    config_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    獲取告警配置詳情
    """
    config = await db.get(AlertWorkflowConfig, config_id)

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert config not found"
        )

    return AlertConfigResponse.model_validate(config)


@router.patch("/alert-configs/{config_id}", response_model=AlertConfigResponse)
async def update_alert_config(
    config_id: UUID,
    data: AlertConfigUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    更新告警配置

    可以更新部分字段。
    """
    config = await db.get(AlertWorkflowConfig, config_id)

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert config not found"
        )

    # 更新非 None 的字段
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            setattr(config, key, value)

    await db.commit()
    await db.refresh(config)

    return AlertConfigResponse.model_validate(config)


@router.delete("/alert-configs/{config_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_alert_config(
    config_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    刪除告警配置
    """
    config = await db.get(AlertWorkflowConfig, config_id)

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert config not found"
        )

    await db.delete(config)
    await db.commit()


@router.post("/alert-configs/{config_id}/toggle", response_model=AlertConfigResponse)
async def toggle_alert_config(
    config_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    切換告警配置啟用狀態
    """
    config = await db.get(AlertWorkflowConfig, config_id)

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert config not found"
        )

    config.is_active = not config.is_active
    await db.commit()
    await db.refresh(config)

    return AlertConfigResponse.model_validate(config)
