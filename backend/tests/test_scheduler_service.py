# =============================================
# 排程服務單元測試
# =============================================

import pytest
from datetime import datetime, timedelta
from uuid import uuid4
from unittest.mock import MagicMock, AsyncMock, patch

import pytz

from app.models.workflow import (
    ScheduledReport,
    ReportExecution,
    ScheduleFrequency,
    ScheduleStatus,
    ExecutionStatus,
    ReportType,
)
from app.services.workflow.scheduler import SchedulerService, MAX_CONSECUTIVE_FAILURES


# =============================================
# Fixtures
# =============================================

@pytest.fixture
def mock_db():
    """模擬數據庫 session"""
    db = AsyncMock()
    db.add = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    db.delete = AsyncMock()
    db.get = AsyncMock()
    db.execute = AsyncMock()
    return db


@pytest.fixture
def scheduler(mock_db):
    """創建 SchedulerService 實例"""
    return SchedulerService(mock_db)


@pytest.fixture
def sample_schedule():
    """創建示例排程"""
    return ScheduledReport(
        id=uuid4(),
        name="測試排程",
        report_type=ReportType.PRICE_ANALYSIS.value,
        frequency=ScheduleFrequency.DAILY.value,
        schedule_time="09:00",
        timezone="Asia/Hong_Kong",
        status=ScheduleStatus.ACTIVE.value,
        run_count=0,
        success_count=0,
        failure_count=0,
        consecutive_failures=0,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


# =============================================
# 創建排程測試
# =============================================

class TestCreateSchedule:
    """測試創建排程"""

    @pytest.mark.asyncio
    async def test_create_daily_schedule(self, scheduler, mock_db):
        """測試創建每日排程"""
        # 模擬 refresh 會設置 id
        async def mock_refresh(obj):
            obj.id = uuid4()
        mock_db.refresh.side_effect = mock_refresh

        result = await scheduler.create_schedule(
            name="每日價格報告",
            report_type=ReportType.PRICE_ANALYSIS.value,
            frequency=ScheduleFrequency.DAILY.value,
            schedule_time="09:00",
        )

        # 驗證 db 操作
        assert mock_db.add.called
        assert mock_db.commit.called
        assert mock_db.refresh.called

        # 驗證排程屬性
        added_schedule = mock_db.add.call_args[0][0]
        assert added_schedule.name == "每日價格報告"
        assert added_schedule.frequency == ScheduleFrequency.DAILY.value
        assert added_schedule.status == ScheduleStatus.ACTIVE.value
        assert added_schedule.next_run_at is not None

    @pytest.mark.asyncio
    async def test_create_weekly_schedule(self, scheduler, mock_db):
        """測試創建每週排程"""
        async def mock_refresh(obj):
            obj.id = uuid4()
        mock_db.refresh.side_effect = mock_refresh

        result = await scheduler.create_schedule(
            name="每週競品報告",
            report_type=ReportType.COMPETITOR_REPORT.value,
            frequency=ScheduleFrequency.WEEKLY.value,
            schedule_time="10:00",
            schedule_day=1,  # 週一
        )

        added_schedule = mock_db.add.call_args[0][0]
        assert added_schedule.frequency == ScheduleFrequency.WEEKLY.value
        assert added_schedule.schedule_day == 1

    @pytest.mark.asyncio
    async def test_create_monthly_schedule(self, scheduler, mock_db):
        """測試創建每月排程"""
        async def mock_refresh(obj):
            obj.id = uuid4()
        mock_db.refresh.side_effect = mock_refresh

        result = await scheduler.create_schedule(
            name="每月銷售報告",
            report_type=ReportType.SALES_SUMMARY.value,
            frequency=ScheduleFrequency.MONTHLY.value,
            schedule_time="08:00",
            schedule_day=15,  # 每月 15 號
        )

        added_schedule = mock_db.add.call_args[0][0]
        assert added_schedule.frequency == ScheduleFrequency.MONTHLY.value
        assert added_schedule.schedule_day == 15


# =============================================
# 排程狀態管理測試
# =============================================

class TestScheduleStatusManagement:
    """測試排程狀態管理"""

    @pytest.mark.asyncio
    async def test_pause_schedule(self, scheduler, mock_db, sample_schedule):
        """測試暫停排程"""
        mock_db.get.return_value = sample_schedule

        result = await scheduler.pause_schedule(sample_schedule.id)

        assert sample_schedule.status == ScheduleStatus.PAUSED.value
        assert mock_db.commit.called

    @pytest.mark.asyncio
    async def test_resume_schedule(self, scheduler, mock_db, sample_schedule):
        """測試恢復排程"""
        sample_schedule.status = ScheduleStatus.PAUSED.value
        sample_schedule.consecutive_failures = 2
        mock_db.get.return_value = sample_schedule

        result = await scheduler.resume_schedule(sample_schedule.id)

        assert sample_schedule.status == ScheduleStatus.ACTIVE.value
        assert sample_schedule.consecutive_failures == 0
        assert sample_schedule.next_run_at is not None

    @pytest.mark.asyncio
    async def test_delete_schedule(self, scheduler, mock_db, sample_schedule):
        """測試刪除排程"""
        mock_db.get.return_value = sample_schedule

        result = await scheduler.delete_schedule(sample_schedule.id)

        assert result is True
        assert mock_db.delete.called
        assert mock_db.commit.called

    @pytest.mark.asyncio
    async def test_delete_nonexistent_schedule(self, scheduler, mock_db):
        """測試刪除不存在的排程"""
        mock_db.get.return_value = None

        result = await scheduler.delete_schedule(uuid4())

        assert result is False
        assert not mock_db.delete.called


# =============================================
# 獲取到期排程測試
# =============================================

class TestGetDueSchedules:
    """測試獲取到期排程"""

    @pytest.mark.asyncio
    async def test_get_due_schedules(self, scheduler, mock_db, sample_schedule):
        """測試獲取到期排程"""
        sample_schedule.next_run_at = datetime.utcnow() - timedelta(minutes=5)

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_schedule]
        mock_db.execute.return_value = mock_result

        result = await scheduler.get_due_schedules()

        assert len(result) == 1
        assert result[0].id == sample_schedule.id

    @pytest.mark.asyncio
    async def test_no_due_schedules(self, scheduler, mock_db):
        """測試無到期排程"""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result

        result = await scheduler.get_due_schedules()

        assert len(result) == 0


# =============================================
# 執行記錄管理測試
# =============================================

class TestExecutionManagement:
    """測試執行記錄管理"""

    @pytest.mark.asyncio
    async def test_create_execution(self, scheduler, mock_db):
        """測試創建執行記錄"""
        schedule_id = uuid4()
        scheduled_at = datetime.utcnow()

        async def mock_refresh(obj):
            obj.id = uuid4()
        mock_db.refresh.side_effect = mock_refresh

        result = await scheduler.create_execution(schedule_id, scheduled_at)

        assert mock_db.add.called
        added_execution = mock_db.add.call_args[0][0]
        assert added_execution.schedule_id == schedule_id
        assert added_execution.status == ExecutionStatus.PENDING.value

    @pytest.mark.asyncio
    async def test_mark_execution_started(self, scheduler, mock_db):
        """測試標記執行開始"""
        execution = ReportExecution(
            id=uuid4(),
            schedule_id=uuid4(),
            status=ExecutionStatus.PENDING.value,
            scheduled_at=datetime.utcnow(),
            created_at=datetime.utcnow(),
        )
        mock_db.get.return_value = execution

        result = await scheduler.mark_execution_started(execution.id)

        assert execution.status == ExecutionStatus.RUNNING.value
        assert execution.started_at is not None

    @pytest.mark.asyncio
    async def test_mark_execution_completed(self, scheduler, mock_db):
        """測試標記執行完成"""
        execution = ReportExecution(
            id=uuid4(),
            schedule_id=uuid4(),
            status=ExecutionStatus.RUNNING.value,
            scheduled_at=datetime.utcnow(),
            started_at=datetime.utcnow() - timedelta(seconds=10),
            created_at=datetime.utcnow(),
        )
        mock_db.get.return_value = execution

        result = await scheduler.mark_execution_completed(
            execution.id,
            report_content="報告內容",
            report_data={"key": "value"},
        )

        assert execution.status == ExecutionStatus.COMPLETED.value
        assert execution.completed_at is not None
        assert execution.duration_ms is not None
        assert execution.report_content == "報告內容"

    @pytest.mark.asyncio
    async def test_mark_execution_failed(self, scheduler, mock_db):
        """測試標記執行失敗"""
        execution = ReportExecution(
            id=uuid4(),
            schedule_id=uuid4(),
            status=ExecutionStatus.RUNNING.value,
            scheduled_at=datetime.utcnow(),
            started_at=datetime.utcnow(),
            created_at=datetime.utcnow(),
        )
        mock_db.get.return_value = execution

        result = await scheduler.mark_execution_failed(
            execution.id,
            error_message="執行錯誤",
        )

        assert execution.status == ExecutionStatus.FAILED.value
        assert execution.error_message == "執行錯誤"


# =============================================
# 執行後統計更新測試
# =============================================

class TestUpdateAfterExecution:
    """測試執行後統計更新"""

    @pytest.mark.asyncio
    async def test_update_after_success(self, scheduler, mock_db, sample_schedule):
        """測試成功執行後更新"""
        sample_schedule.run_count = 5
        sample_schedule.success_count = 4
        sample_schedule.consecutive_failures = 1
        mock_db.get.return_value = sample_schedule

        result = await scheduler.update_schedule_after_execution(
            sample_schedule.id,
            success=True
        )

        assert sample_schedule.run_count == 6
        assert sample_schedule.success_count == 5
        assert sample_schedule.consecutive_failures == 0
        assert sample_schedule.last_run_at is not None

    @pytest.mark.asyncio
    async def test_update_after_failure(self, scheduler, mock_db, sample_schedule):
        """測試失敗執行後更新"""
        sample_schedule.run_count = 5
        sample_schedule.failure_count = 1
        sample_schedule.consecutive_failures = 1
        mock_db.get.return_value = sample_schedule

        result = await scheduler.update_schedule_after_execution(
            sample_schedule.id,
            success=False
        )

        assert sample_schedule.run_count == 6
        assert sample_schedule.failure_count == 2
        assert sample_schedule.consecutive_failures == 2

    @pytest.mark.asyncio
    async def test_auto_pause_after_consecutive_failures(self, scheduler, mock_db, sample_schedule):
        """測試連續失敗後自動暫停"""
        sample_schedule.consecutive_failures = MAX_CONSECUTIVE_FAILURES - 1
        mock_db.get.return_value = sample_schedule

        result = await scheduler.update_schedule_after_execution(
            sample_schedule.id,
            success=False
        )

        assert sample_schedule.status == ScheduleStatus.FAILED.value
        assert sample_schedule.consecutive_failures == MAX_CONSECUTIVE_FAILURES


# =============================================
# 時間計算測試
# =============================================

class TestTimeCalculation:
    """測試時間計算"""

    def test_calculate_next_run_daily(self, scheduler):
        """測試每日排程下次執行時間計算"""
        schedule = ScheduledReport(
            frequency=ScheduleFrequency.DAILY.value,
            schedule_time="09:00",
            timezone="Asia/Hong_Kong",
        )

        next_run = scheduler._calculate_next_run(schedule)

        assert next_run is not None
        # 應該在未來
        assert next_run > datetime.utcnow() - timedelta(minutes=1)

    def test_calculate_next_run_weekly(self, scheduler):
        """測試每週排程下次執行時間計算"""
        schedule = ScheduledReport(
            frequency=ScheduleFrequency.WEEKLY.value,
            schedule_time="10:00",
            schedule_day=1,  # 週一
            timezone="Asia/Hong_Kong",
        )

        next_run = scheduler._calculate_next_run(schedule)

        assert next_run is not None
        # 轉換為香港時間檢查星期
        hk_tz = pytz.timezone("Asia/Hong_Kong")
        next_run_hk = pytz.utc.localize(next_run).astimezone(hk_tz)
        assert next_run_hk.isoweekday() == 1  # 應該是週一

    def test_calculate_next_run_monthly(self, scheduler):
        """測試每月排程下次執行時間計算"""
        schedule = ScheduledReport(
            frequency=ScheduleFrequency.MONTHLY.value,
            schedule_time="08:00",
            schedule_day=15,  # 每月 15 號
            timezone="Asia/Hong_Kong",
        )

        next_run = scheduler._calculate_next_run(schedule)

        assert next_run is not None
        # 轉換為香港時間檢查日期
        hk_tz = pytz.timezone("Asia/Hong_Kong")
        next_run_hk = pytz.utc.localize(next_run).astimezone(hk_tz)
        assert next_run_hk.day == 15

    def test_calculate_next_runs_preview(self, scheduler):
        """測試預覽多次執行時間"""
        schedule = ScheduledReport(
            frequency=ScheduleFrequency.DAILY.value,
            schedule_time="09:00",
            timezone="Asia/Hong_Kong",
        )

        runs = scheduler.calculate_next_runs(schedule, count=5)

        assert len(runs) == 5
        # 每次執行時間應該遞增
        for i in range(1, len(runs)):
            assert runs[i] > runs[i-1]


# =============================================
# 列表查詢測試
# =============================================

class TestListSchedules:
    """測試列表查詢"""

    @pytest.mark.asyncio
    async def test_list_all_schedules(self, scheduler, mock_db, sample_schedule):
        """測試列出所有排程"""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_schedule]
        mock_db.execute.return_value = mock_result

        result = await scheduler.list_schedules()

        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_list_schedules_by_status(self, scheduler, mock_db, sample_schedule):
        """測試按狀態篩選排程"""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_schedule]
        mock_db.execute.return_value = mock_result

        result = await scheduler.list_schedules(status=ScheduleStatus.ACTIVE.value)

        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_list_schedules_by_conversation(self, scheduler, mock_db, sample_schedule):
        """測試按對話 ID 篩選排程"""
        sample_schedule.source_conversation_id = "conv-123"

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_schedule]
        mock_db.execute.return_value = mock_result

        result = await scheduler.list_schedules(conversation_id="conv-123")

        assert len(result) == 1
