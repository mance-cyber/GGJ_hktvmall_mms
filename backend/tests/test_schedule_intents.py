# =============================================
# 排程意圖處理單元測試
# =============================================

import pytest
from datetime import datetime
from uuid import uuid4
from unittest.mock import MagicMock, AsyncMock, patch

from app.services.agent.intent_classifier import IntentClassifier, IntentType
from app.services.agent.slot_manager import SlotManager, ScheduleSlots
from app.services.agent.tools.schedule_tools import (
    CreateScheduleTool,
    ListSchedulesTool,
    PauseScheduleTool,
    ResumeScheduleTool,
    DeleteScheduleTool,
)
from app.models.workflow import ScheduledReport, ScheduleStatus


# =============================================
# Fixtures
# =============================================

@pytest.fixture
def intent_classifier():
    """創建意圖分類器"""
    return IntentClassifier()


@pytest.fixture
def slot_manager():
    """創建槽位管理器"""
    return SlotManager()


@pytest.fixture
def mock_db():
    """模擬數據庫 session"""
    db = AsyncMock()
    return db


@pytest.fixture
def sample_schedule():
    """創建示例排程"""
    return ScheduledReport(
        id=uuid4(),
        name="每日價格報告",
        report_type="price_analysis",
        frequency="daily",
        schedule_time="09:00",
        timezone="Asia/Hong_Kong",
        status=ScheduleStatus.ACTIVE.value,
        run_count=10,
        success_count=9,
        failure_count=1,
        consecutive_failures=0,
        next_run_at=datetime.utcnow(),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


# =============================================
# 意圖分類測試
# =============================================

class TestScheduleIntentClassification:
    """測試排程相關意圖分類"""

    def test_classify_create_schedule_intent(self, intent_classifier):
        """測試識別創建排程意圖"""
        test_cases = [
            "幫我設定每日 9 點發送價格報告",
            "我想排程每週一發送競品分析",
            "設定定時報告",
            "創建每月銷售報告排程",
        ]

        for text in test_cases:
            result = intent_classifier.classify(text)
            assert result.intent == IntentType.CREATE_SCHEDULED_REPORT, f"Failed for: {text}"

    def test_classify_list_schedules_intent(self, intent_classifier):
        """測試識別列出排程意圖"""
        test_cases = [
            "我有什麼排程",
            "列出所有排程",
            "查看定時報告",
            "顯示排程列表",
        ]

        for text in test_cases:
            result = intent_classifier.classify(text)
            assert result.intent == IntentType.LIST_SCHEDULES, f"Failed for: {text}"

    def test_classify_pause_schedule_intent(self, intent_classifier):
        """測試識別暫停排程意圖"""
        test_cases = [
            "暫停排程",
            "停止定時報告",
            "暫停每日報告",
        ]

        for text in test_cases:
            result = intent_classifier.classify(text)
            assert result.intent == IntentType.PAUSE_SCHEDULED_REPORT, f"Failed for: {text}"

    def test_classify_resume_schedule_intent(self, intent_classifier):
        """測試識別恢復排程意圖"""
        test_cases = [
            "恢復排程",
            "繼續定時報告",
            "重啟排程",
        ]

        for text in test_cases:
            result = intent_classifier.classify(text)
            assert result.intent == IntentType.RESUME_SCHEDULED_REPORT, f"Failed for: {text}"

    def test_classify_delete_schedule_intent(self, intent_classifier):
        """測試識別刪除排程意圖"""
        test_cases = [
            "刪除排程",
            "取消定時報告",
            "移除排程",
        ]

        for text in test_cases:
            result = intent_classifier.classify(text)
            assert result.intent == IntentType.DELETE_SCHEDULED_REPORT, f"Failed for: {text}"


# =============================================
# 槽位提取測試
# =============================================

class TestScheduleSlotExtraction:
    """測試排程槽位提取"""

    def test_extract_daily_schedule_slots(self, slot_manager):
        """測試提取每日排程槽位"""
        text = "每日 9 點發送價格報告"
        slots = slot_manager.extract_schedule_slots(text)

        assert slots.frequency == "daily"
        assert slots.schedule_time == "09:00"

    def test_extract_weekly_schedule_slots(self, slot_manager):
        """測試提取每週排程槽位"""
        text = "每週一早上 10 點發送競品報告"
        slots = slot_manager.extract_schedule_slots(text)

        assert slots.frequency == "weekly"
        assert slots.schedule_day == 1

    def test_extract_monthly_schedule_slots(self, slot_manager):
        """測試提取每月排程槽位"""
        text = "每月 15 號發送銷售報告"
        slots = slot_manager.extract_schedule_slots(text)

        assert slots.frequency == "monthly"
        assert slots.schedule_day == 15

    def test_extract_time_variations(self, slot_manager):
        """測試不同時間表達方式"""
        test_cases = [
            ("上午 9 點", "09:00"),
            ("下午 3 點", "15:00"),
            ("晚上 8 點", "20:00"),
            ("9:30", "09:30"),
            ("14:00", "14:00"),
        ]

        for text, expected_time in test_cases:
            slots = slot_manager.extract_schedule_slots(f"每日 {text} 發送報告")
            assert slots.schedule_time == expected_time, f"Failed for: {text}"

    def test_extract_weekday_variations(self, slot_manager):
        """測試不同星期表達方式"""
        test_cases = [
            ("週一", 1),
            ("星期一", 1),
            ("禮拜一", 1),
            ("周一", 1),
            ("週五", 5),
            ("星期日", 7),
        ]

        for text, expected_day in test_cases:
            slots = slot_manager.extract_schedule_slots(f"每 {text} 發送報告")
            assert slots.schedule_day == expected_day, f"Failed for: {text}"

    def test_check_schedule_completeness(self, slot_manager):
        """測試排程完整性檢查"""
        # 完整的排程
        complete_slots = ScheduleSlots(
            frequency="daily",
            schedule_time="09:00",
        )
        missing = slot_manager.check_schedule_completeness(complete_slots)
        assert len(missing) == 0

        # 缺少時間的排程
        incomplete_slots = ScheduleSlots(
            frequency="daily",
        )
        missing = slot_manager.check_schedule_completeness(incomplete_slots)
        assert "schedule_time" in missing

        # 缺少日期的週排程
        weekly_incomplete = ScheduleSlots(
            frequency="weekly",
            schedule_time="09:00",
        )
        missing = slot_manager.check_schedule_completeness(weekly_incomplete)
        assert "schedule_day" in missing


# =============================================
# 排程工具測試
# =============================================

class TestScheduleTools:
    """測試排程工具"""

    @pytest.mark.asyncio
    async def test_create_schedule_tool(self, mock_db, sample_schedule):
        """測試創建排程工具"""
        with patch('app.services.agent.tools.schedule_tools.SchedulerService') as MockService:
            mock_service = AsyncMock()
            mock_service.create_schedule.return_value = sample_schedule
            MockService.return_value = mock_service

            tool = CreateScheduleTool(mock_db)
            result = await tool.execute(
                name="測試排程",
                frequency="daily",
                schedule_time="09:00",
            )

            assert result.success is True
            assert "schedule_id" in result.data
            assert result.data["name"] == sample_schedule.name

    @pytest.mark.asyncio
    async def test_list_schedules_tool(self, mock_db, sample_schedule):
        """測試列出排程工具"""
        with patch('app.services.agent.tools.schedule_tools.SchedulerService') as MockService:
            mock_service = AsyncMock()
            mock_service.list_schedules.return_value = [sample_schedule]
            MockService.return_value = mock_service

            tool = ListSchedulesTool(mock_db)
            result = await tool.execute()

            assert result.success is True
            assert result.data["count"] == 1
            assert len(result.data["schedules"]) == 1

    @pytest.mark.asyncio
    async def test_pause_schedule_tool(self, mock_db, sample_schedule):
        """測試暫停排程工具"""
        sample_schedule.status = ScheduleStatus.PAUSED.value

        with patch('app.services.agent.tools.schedule_tools.SchedulerService') as MockService:
            mock_service = AsyncMock()
            mock_service.pause_schedule.return_value = sample_schedule
            MockService.return_value = mock_service

            tool = PauseScheduleTool(mock_db)
            result = await tool.execute(schedule_id=str(sample_schedule.id))

            assert result.success is True
            assert result.data["status"] == ScheduleStatus.PAUSED.value

    @pytest.mark.asyncio
    async def test_pause_schedule_not_found(self, mock_db):
        """測試暫停不存在的排程"""
        with patch('app.services.agent.tools.schedule_tools.SchedulerService') as MockService:
            mock_service = AsyncMock()
            mock_service.pause_schedule.return_value = None
            MockService.return_value = mock_service

            tool = PauseScheduleTool(mock_db)
            result = await tool.execute(schedule_id=str(uuid4()))

            assert result.success is False
            assert "找不到排程" in result.error

    @pytest.mark.asyncio
    async def test_resume_schedule_tool(self, mock_db, sample_schedule):
        """測試恢復排程工具"""
        with patch('app.services.agent.tools.schedule_tools.SchedulerService') as MockService:
            mock_service = AsyncMock()
            mock_service.resume_schedule.return_value = sample_schedule
            MockService.return_value = mock_service

            tool = ResumeScheduleTool(mock_db)
            result = await tool.execute(schedule_id=str(sample_schedule.id))

            assert result.success is True
            assert "next_run_at" in result.data

    @pytest.mark.asyncio
    async def test_delete_schedule_tool(self, mock_db, sample_schedule):
        """測試刪除排程工具"""
        with patch('app.services.agent.tools.schedule_tools.SchedulerService') as MockService:
            mock_service = AsyncMock()
            mock_service.get_schedule.return_value = sample_schedule
            mock_service.delete_schedule.return_value = True
            MockService.return_value = mock_service

            tool = DeleteScheduleTool(mock_db)
            result = await tool.execute(schedule_id=str(sample_schedule.id))

            assert result.success is True
            assert result.data["name"] == sample_schedule.name


# =============================================
# 工具執行器集成測試
# =============================================

class TestToolExecutorIntegration:
    """測試工具執行器與排程工具的集成"""

    @pytest.mark.asyncio
    async def test_schedule_intent_triggers_correct_tool(self, mock_db):
        """測試排程意圖觸發正確的工具"""
        from app.services.agent.tool_executor import ToolExecutor
        from app.services.agent.slot_manager import AnalysisSlots

        executor = ToolExecutor(mock_db)

        # 測試 CREATE_SCHEDULED_REPORT 意圖映射
        plan = executor.get_execution_plan(
            IntentType.CREATE_SCHEDULED_REPORT,
            AnalysisSlots(products=[])
        )
        assert "create_schedule" in plan.tools

        # 測試 LIST_SCHEDULES 意圖映射
        plan = executor.get_execution_plan(
            IntentType.LIST_SCHEDULES,
            AnalysisSlots(products=[])
        )
        assert "list_schedules" in plan.tools

        # 測試 PAUSE_SCHEDULED_REPORT 意圖映射
        plan = executor.get_execution_plan(
            IntentType.PAUSE_SCHEDULED_REPORT,
            AnalysisSlots(products=[])
        )
        assert "pause_schedule" in plan.tools

        # 測試 RESUME_SCHEDULED_REPORT 意圖映射
        plan = executor.get_execution_plan(
            IntentType.RESUME_SCHEDULED_REPORT,
            AnalysisSlots(products=[])
        )
        assert "resume_schedule" in plan.tools

        # 測試 DELETE_SCHEDULED_REPORT 意圖映射
        plan = executor.get_execution_plan(
            IntentType.DELETE_SCHEDULED_REPORT,
            AnalysisSlots(products=[])
        )
        assert "delete_schedule" in plan.tools


# =============================================
# 邊界情況測試
# =============================================

class TestEdgeCases:
    """測試邊界情況"""

    def test_invalid_time_format(self, slot_manager):
        """測試無效時間格式"""
        text = "每日 25:00 發送報告"
        slots = slot_manager.extract_schedule_slots(text)
        # 應該返回默認值或 None
        assert slots.schedule_time is None or slots.schedule_time == "09:00"

    def test_invalid_day_number(self, slot_manager):
        """測試無效日期數字"""
        text = "每月 35 號發送報告"
        slots = slot_manager.extract_schedule_slots(text)
        # 應該返回默認值或 None
        assert slots.schedule_day is None or slots.schedule_day <= 31

    def test_mixed_chinese_arabic_numbers(self, slot_manager):
        """測試中文和阿拉伯數字混用"""
        test_cases = [
            ("每日九點", "09:00"),
            ("每日 9 點", "09:00"),
        ]

        for text, expected in test_cases:
            slots = slot_manager.extract_schedule_slots(text)
            assert slots.schedule_time == expected, f"Failed for: {text}"

    @pytest.mark.asyncio
    async def test_create_schedule_with_missing_name(self, mock_db):
        """測試創建缺少名稱的排程"""
        with patch('app.services.agent.tools.schedule_tools.SchedulerService') as MockService:
            mock_service = AsyncMock()
            mock_service.create_schedule.side_effect = ValueError("Name is required")
            MockService.return_value = mock_service

            tool = CreateScheduleTool(mock_db)
            result = await tool.execute(
                name="",  # 空名稱
                frequency="daily",
            )

            assert result.success is False
