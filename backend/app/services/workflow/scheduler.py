# =============================================
# 排程服務
# 管理定時報告的 CRUD 和執行調度
# =============================================

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID
import pytz
from croniter import croniter

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_

from app.models.workflow import (
    ScheduledReport,
    ReportExecution,
    ScheduleFrequency,
    ScheduleStatus,
    ExecutionStatus,
    ReportType,
)

logger = logging.getLogger(__name__)

# 連續失敗多少次後自動暫停
MAX_CONSECUTIVE_FAILURES = 3


class SchedulerService:
    """
    排程服務

    負責：
    - 排程 CRUD 操作
    - 計算下次執行時間
    - 管理排程狀態
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    # =============================================
    # CRUD 操作
    # =============================================

    async def create_schedule(
        self,
        name: str,
        report_type: str = ReportType.PRICE_ANALYSIS.value,
        report_config: Optional[Dict] = None,
        frequency: str = ScheduleFrequency.DAILY.value,
        schedule_time: str = "09:00",
        schedule_day: Optional[int] = None,
        cron_expression: Optional[str] = None,
        timezone: str = "Asia/Hong_Kong",
        delivery_channels: Optional[Dict] = None,
        source_conversation_id: Optional[str] = None,
        created_by: Optional[UUID] = None,
    ) -> ScheduledReport:
        """
        創建排程

        Args:
            name: 排程名稱
            report_type: 報告類型
            report_config: 報告配置 (產品列表等)
            frequency: 頻率 (daily/weekly/monthly/custom)
            schedule_time: 執行時間 HH:MM
            schedule_day: 執行日 (weekly: 1-7, monthly: 1-31)
            cron_expression: Cron 表達式 (frequency=custom 時使用)
            timezone: 時區
            delivery_channels: 交付渠道配置
            source_conversation_id: 來源對話 ID
            created_by: 創建者 ID

        Returns:
            ScheduledReport
        """
        schedule = ScheduledReport(
            name=name,
            report_type=report_type,
            report_config=report_config,
            frequency=frequency,
            schedule_time=schedule_time,
            schedule_day=schedule_day,
            cron_expression=cron_expression,
            timezone=timezone,
            delivery_channels=delivery_channels,
            status=ScheduleStatus.ACTIVE.value,
            source_conversation_id=source_conversation_id,
            created_by=created_by,
        )

        # 計算下次執行時間
        schedule.next_run_at = self._calculate_next_run(schedule)

        self.db.add(schedule)
        await self.db.commit()
        await self.db.refresh(schedule)

        logger.info(f"Created schedule: {schedule.id} - {name}, next_run: {schedule.next_run_at}")
        return schedule

    async def get_schedule(self, schedule_id: UUID) -> Optional[ScheduledReport]:
        """獲取排程"""
        return await self.db.get(ScheduledReport, schedule_id)

    async def list_schedules(
        self,
        status: Optional[str] = None,
        conversation_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[ScheduledReport]:
        """
        列出排程

        Args:
            status: 篩選狀態
            conversation_id: 篩選對話 ID
            limit: 返回數量
            offset: 偏移量

        Returns:
            排程列表
        """
        query = select(ScheduledReport)

        conditions = []
        if status:
            conditions.append(ScheduledReport.status == status)
        if conversation_id:
            conditions.append(ScheduledReport.source_conversation_id == conversation_id)

        if conditions:
            query = query.where(and_(*conditions))

        query = query.order_by(ScheduledReport.created_at.desc())
        query = query.offset(offset).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update_schedule(
        self,
        schedule_id: UUID,
        **updates
    ) -> Optional[ScheduledReport]:
        """
        更新排程

        Args:
            schedule_id: 排程 ID
            **updates: 要更新的字段

        Returns:
            更新後的排程
        """
        schedule = await self.get_schedule(schedule_id)
        if not schedule:
            return None

        # 更新字段
        for key, value in updates.items():
            if hasattr(schedule, key) and value is not None:
                setattr(schedule, key, value)

        # 如果更新了排程相關字段，重新計算下次執行時間
        schedule_fields = {'frequency', 'schedule_time', 'schedule_day', 'cron_expression', 'timezone'}
        if schedule_fields.intersection(updates.keys()):
            schedule.next_run_at = self._calculate_next_run(schedule)

        await self.db.commit()
        await self.db.refresh(schedule)

        logger.info(f"Updated schedule: {schedule_id}")
        return schedule

    async def pause_schedule(self, schedule_id: UUID) -> Optional[ScheduledReport]:
        """暫停排程"""
        return await self.update_schedule(
            schedule_id,
            status=ScheduleStatus.PAUSED.value
        )

    async def resume_schedule(self, schedule_id: UUID) -> Optional[ScheduledReport]:
        """恢復排程"""
        schedule = await self.get_schedule(schedule_id)
        if not schedule:
            return None

        # 重新計算下次執行時間
        schedule.status = ScheduleStatus.ACTIVE.value
        schedule.next_run_at = self._calculate_next_run(schedule)
        schedule.consecutive_failures = 0  # 重置連續失敗計數

        await self.db.commit()
        await self.db.refresh(schedule)

        logger.info(f"Resumed schedule: {schedule_id}")
        return schedule

    async def delete_schedule(self, schedule_id: UUID) -> bool:
        """刪除排程"""
        schedule = await self.get_schedule(schedule_id)
        if not schedule:
            return False

        await self.db.delete(schedule)
        await self.db.commit()

        logger.info(f"Deleted schedule: {schedule_id}")
        return True

    # =============================================
    # 執行管理
    # =============================================

    async def get_due_schedules(self, now: Optional[datetime] = None) -> List[ScheduledReport]:
        """
        獲取到期需要執行的排程

        Args:
            now: 當前時間 (默認 UTC now)

        Returns:
            到期的排程列表
        """
        if now is None:
            now = datetime.utcnow()

        query = select(ScheduledReport).where(
            and_(
                ScheduledReport.status == ScheduleStatus.ACTIVE.value,
                ScheduledReport.next_run_at <= now
            )
        ).order_by(ScheduledReport.next_run_at)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create_execution(
        self,
        schedule_id: UUID,
        scheduled_at: datetime
    ) -> ReportExecution:
        """創建執行記錄"""
        execution = ReportExecution(
            schedule_id=schedule_id,
            scheduled_at=scheduled_at,
            status=ExecutionStatus.PENDING.value,
        )

        self.db.add(execution)
        await self.db.commit()
        await self.db.refresh(execution)

        return execution

    async def update_execution(
        self,
        execution_id: UUID,
        **updates
    ) -> Optional[ReportExecution]:
        """更新執行記錄"""
        execution = await self.db.get(ReportExecution, execution_id)
        if not execution:
            return None

        for key, value in updates.items():
            if hasattr(execution, key):
                setattr(execution, key, value)

        await self.db.commit()
        await self.db.refresh(execution)

        return execution

    async def mark_execution_started(self, execution_id: UUID) -> Optional[ReportExecution]:
        """標記執行開始"""
        return await self.update_execution(
            execution_id,
            status=ExecutionStatus.RUNNING.value,
            started_at=datetime.utcnow()
        )

    async def mark_execution_completed(
        self,
        execution_id: UUID,
        report_content: str,
        report_data: Optional[Dict] = None,
        delivery_status: Optional[Dict] = None,
    ) -> Optional[ReportExecution]:
        """標記執行完成"""
        execution = await self.db.get(ReportExecution, execution_id)
        if not execution:
            return None

        now = datetime.utcnow()
        duration_ms = None
        if execution.started_at:
            duration_ms = int((now - execution.started_at).total_seconds() * 1000)

        return await self.update_execution(
            execution_id,
            status=ExecutionStatus.COMPLETED.value,
            completed_at=now,
            duration_ms=duration_ms,
            report_content=report_content,
            report_data=report_data,
            delivery_status=delivery_status,
        )

    async def mark_execution_failed(
        self,
        execution_id: UUID,
        error_message: str,
        error_details: Optional[Dict] = None,
    ) -> Optional[ReportExecution]:
        """標記執行失敗"""
        now = datetime.utcnow()
        execution = await self.db.get(ReportExecution, execution_id)
        if not execution:
            return None

        duration_ms = None
        if execution.started_at:
            duration_ms = int((now - execution.started_at).total_seconds() * 1000)

        return await self.update_execution(
            execution_id,
            status=ExecutionStatus.FAILED.value,
            completed_at=now,
            duration_ms=duration_ms,
            error_message=error_message,
            error_details=error_details,
        )

    async def update_schedule_after_execution(
        self,
        schedule_id: UUID,
        success: bool
    ) -> Optional[ScheduledReport]:
        """
        執行後更新排程統計

        Args:
            schedule_id: 排程 ID
            success: 是否成功

        Returns:
            更新後的排程
        """
        schedule = await self.get_schedule(schedule_id)
        if not schedule:
            return None

        now = datetime.utcnow()
        schedule.last_run_at = now
        schedule.run_count += 1

        if success:
            schedule.success_count += 1
            schedule.consecutive_failures = 0
        else:
            schedule.failure_count += 1
            schedule.consecutive_failures += 1

            # 檢查是否需要自動暫停
            if schedule.consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                schedule.status = ScheduleStatus.FAILED.value
                logger.warning(
                    f"Schedule {schedule_id} auto-paused after "
                    f"{schedule.consecutive_failures} consecutive failures"
                )

        # 計算下次執行時間
        if schedule.status == ScheduleStatus.ACTIVE.value:
            schedule.next_run_at = self._calculate_next_run(schedule)

        await self.db.commit()
        await self.db.refresh(schedule)

        return schedule

    async def get_execution_history(
        self,
        schedule_id: UUID,
        limit: int = 20,
    ) -> List[ReportExecution]:
        """獲取執行歷史"""
        query = select(ReportExecution).where(
            ReportExecution.schedule_id == schedule_id
        ).order_by(ReportExecution.created_at.desc()).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    # =============================================
    # 時間計算
    # =============================================

    def _calculate_next_run(self, schedule: ScheduledReport) -> datetime:
        """
        計算下次執行時間

        Args:
            schedule: 排程對象

        Returns:
            下次執行時間 (UTC)
        """
        tz = pytz.timezone(schedule.timezone)
        now = datetime.now(tz)

        if schedule.frequency == ScheduleFrequency.CUSTOM.value and schedule.cron_expression:
            # 使用 cron 表達式
            cron = croniter(schedule.cron_expression, now)
            next_run = cron.get_next(datetime)
            return next_run.astimezone(pytz.UTC).replace(tzinfo=None)

        # 解析執行時間
        hour, minute = 9, 0
        if schedule.schedule_time:
            parts = schedule.schedule_time.split(':')
            hour = int(parts[0])
            minute = int(parts[1]) if len(parts) > 1 else 0

        if schedule.frequency == ScheduleFrequency.DAILY.value:
            # 每日
            next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if next_run <= now:
                next_run += timedelta(days=1)

        elif schedule.frequency == ScheduleFrequency.WEEKLY.value:
            # 每週
            target_day = schedule.schedule_day or 1  # 默認週一
            current_weekday = now.isoweekday()
            days_ahead = target_day - current_weekday

            next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            next_run += timedelta(days=days_ahead)

            if next_run <= now:
                next_run += timedelta(weeks=1)

        elif schedule.frequency == ScheduleFrequency.MONTHLY.value:
            # 每月
            target_day = schedule.schedule_day or 1  # 默認 1 號
            next_run = now.replace(day=target_day, hour=hour, minute=minute, second=0, microsecond=0)

            if next_run <= now:
                # 下個月
                if now.month == 12:
                    next_run = next_run.replace(year=now.year + 1, month=1)
                else:
                    next_run = next_run.replace(month=now.month + 1)

        else:
            # 默認明天
            next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            next_run += timedelta(days=1)

        # 轉換為 UTC
        return next_run.astimezone(pytz.UTC).replace(tzinfo=None)

    def calculate_next_runs(
        self,
        schedule: ScheduledReport,
        count: int = 5
    ) -> List[datetime]:
        """
        預覽未來多次執行時間

        Args:
            schedule: 排程對象
            count: 預覽數量

        Returns:
            執行時間列表
        """
        runs = []
        tz = pytz.timezone(schedule.timezone)
        current = datetime.now(tz)

        if schedule.frequency == ScheduleFrequency.CUSTOM.value and schedule.cron_expression:
            cron = croniter(schedule.cron_expression, current)
            for _ in range(count):
                next_run = cron.get_next(datetime)
                runs.append(next_run.astimezone(pytz.UTC).replace(tzinfo=None))
        else:
            # 臨時創建副本計算
            temp_schedule = ScheduledReport(
                frequency=schedule.frequency,
                schedule_time=schedule.schedule_time,
                schedule_day=schedule.schedule_day,
                timezone=schedule.timezone,
            )

            for _ in range(count):
                next_run = self._calculate_next_run(temp_schedule)
                runs.append(next_run)
                # 模擬執行後更新
                temp_schedule.last_run_at = next_run

        return runs
