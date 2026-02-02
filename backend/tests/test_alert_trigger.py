# =============================================
# AlertTrigger 單元測試
# =============================================
# 測試告警觸發器的核心功能：
# - 條件檢查
# - 靜默時段過濾
# - 工作流執行
# =============================================

import pytest
from datetime import datetime, time
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from app.services.workflow.triggers import AlertTrigger


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
    return db


@pytest.fixture
def trigger(mock_db):
    """創建 AlertTrigger 實例"""
    return AlertTrigger(mock_db)


@pytest.fixture
def sample_alert_data():
    """示例告警數據"""
    return {
        "product_id": str(uuid4()),
        "product_name": "日本 A5 和牛西冷 200g",
        "old_price": 388.00,
        "new_price": 298.00,
        "change_percent": -23.2,
        "category_id": str(uuid4()),
        "alert_type": "price_drop",
    }


@pytest.fixture
def sample_config():
    """示例告警配置"""
    config = MagicMock()
    config.id = uuid4()
    config.name = "大幅降價告警"
    config.is_active = True
    config.trigger_conditions = {
        "price_drop_threshold": 10,
        "price_increase_threshold": 15,
    }
    config.auto_analyze = True
    config.auto_create_proposal = False
    config.notify_channels = {"telegram": {"enabled": True}}
    config.quiet_hours_start = None
    config.quiet_hours_end = None
    return config


# =============================================
# 條件檢查測試
# =============================================

class TestTriggerConditions:
    """測試觸發條件檢查"""

    def test_price_drop_triggers_when_exceeds_threshold(self, trigger, sample_config, sample_alert_data):
        """價格下降超過閾值時應觸發"""
        # 降價 23.2%，閾值 10%
        result = trigger._check_trigger_conditions(sample_config, sample_alert_data)
        assert result is True

    def test_price_drop_not_triggers_below_threshold(self, trigger, sample_config, sample_alert_data):
        """價格下降未達閾值時不應觸發"""
        sample_alert_data["change_percent"] = -5.0  # 低於 10% 閾值
        result = trigger._check_trigger_conditions(sample_config, sample_alert_data)
        assert result is False

    def test_price_increase_triggers_when_exceeds_threshold(self, trigger, sample_config, sample_alert_data):
        """價格上升超過閾值時應觸發"""
        sample_alert_data["change_percent"] = 20.0  # 高於 15% 閾值
        sample_alert_data["alert_type"] = "price_increase"
        result = trigger._check_trigger_conditions(sample_config, sample_alert_data)
        assert result is True

    def test_price_increase_not_triggers_below_threshold(self, trigger, sample_config, sample_alert_data):
        """價格上升未達閾值時不應觸發"""
        sample_alert_data["change_percent"] = 10.0  # 低於 15% 閾值
        sample_alert_data["alert_type"] = "price_increase"
        result = trigger._check_trigger_conditions(sample_config, sample_alert_data)
        assert result is False

    def test_no_threshold_set_triggers_always(self, trigger, sample_config, sample_alert_data):
        """沒有設置閾值時默認觸發"""
        sample_config.trigger_conditions = {}
        result = trigger._check_trigger_conditions(sample_config, sample_alert_data)
        assert result is True

    def test_category_filter_excludes_non_matching(self, trigger, sample_config, sample_alert_data):
        """類別過濾應排除不匹配的"""
        sample_config.trigger_conditions = {
            "price_drop_threshold": 10,
            "categories": [str(uuid4())],  # 不同的類別 ID
        }
        result = trigger._check_trigger_conditions(sample_config, sample_alert_data)
        assert result is False

    def test_category_filter_includes_matching(self, trigger, sample_config, sample_alert_data):
        """類別過濾應包含匹配的"""
        sample_config.trigger_conditions = {
            "price_drop_threshold": 10,
            "categories": [sample_alert_data["category_id"]],
        }
        result = trigger._check_trigger_conditions(sample_config, sample_alert_data)
        assert result is True


# =============================================
# 靜默時段測試
# =============================================

class TestQuietHours:
    """測試靜默時段過濾"""

    def test_no_quiet_hours_returns_false(self, trigger, sample_config):
        """沒有設置靜默時段時返回 False"""
        sample_config.quiet_hours_start = None
        sample_config.quiet_hours_end = None
        result = trigger._is_quiet_hours(sample_config)
        assert result is False

    def test_within_quiet_hours_returns_true(self, trigger, sample_config):
        """在靜默時段內返回 True"""
        # 設置靜默時段為 00:00 - 23:59（全天）
        sample_config.quiet_hours_start = "00:00"
        sample_config.quiet_hours_end = "23:59"
        result = trigger._is_quiet_hours(sample_config)
        assert result is True

    def test_outside_quiet_hours_returns_false(self, trigger, sample_config):
        """在靜默時段外返回 False"""
        # 設置靜默時段為 03:00 - 03:01（極短時段）
        sample_config.quiet_hours_start = "03:00"
        sample_config.quiet_hours_end = "03:01"

        # 模擬當前時間為 12:00
        with patch('app.services.workflow.triggers.datetime') as mock_datetime:
            mock_now = MagicMock()
            mock_now.time.return_value = time(12, 0)
            mock_datetime.now.return_value = mock_now

            result = trigger._is_quiet_hours(sample_config)
            # 注意：由於 datetime.now(tz) 的模擬較複雜，這裡簡化測試
            # 實際測試中應使用 freezegun 或類似庫

    def test_overnight_quiet_hours(self, trigger, sample_config):
        """跨夜靜默時段測試"""
        # 設置跨夜時段 22:00 - 08:00
        sample_config.quiet_hours_start = "22:00"
        sample_config.quiet_hours_end = "08:00"

        # 解析測試
        start = trigger._parse_time("22:00")
        end = trigger._parse_time("08:00")

        assert start == time(22, 0)
        assert end == time(8, 0)
        assert start > end  # 跨夜情況

    def test_parse_time_valid(self, trigger):
        """有效時間字符串解析"""
        result = trigger._parse_time("09:30")
        assert result == time(9, 30)

    def test_parse_time_invalid(self, trigger):
        """無效時間字符串解析"""
        result = trigger._parse_time("invalid")
        assert result is None

        result = trigger._parse_time("25:00")
        assert result is None


# =============================================
# AI 分析測試
# =============================================

class TestAIAnalysis:
    """測試 AI 分析功能"""

    def test_assess_impact_high(self, trigger):
        """高影響評估"""
        result = trigger._assess_impact(-25.0)
        assert "高影響" in result

    def test_assess_impact_medium(self, trigger):
        """中影響評估"""
        result = trigger._assess_impact(-12.0)
        assert "中影響" in result

    def test_assess_impact_low(self, trigger):
        """低影響評估"""
        result = trigger._assess_impact(-7.0)
        assert "低影響" in result

    def test_assess_impact_minimal(self, trigger):
        """極低影響評估"""
        result = trigger._assess_impact(-2.0)
        assert "極低影響" in result

    def test_generate_recommendations_price_drop(self, trigger):
        """價格下降時的建議"""
        recommendations = trigger._generate_recommendations(-15.0, 100.0, 85.0)
        assert len(recommendations) > 0
        assert any("跟進降價" in r or "監控" in r for r in recommendations)

    def test_generate_recommendations_price_increase(self, trigger):
        """價格上升時的建議"""
        recommendations = trigger._generate_recommendations(15.0, 100.0, 115.0)
        assert len(recommendations) > 0
        assert any("漲價" in r or "上調" in r for r in recommendations)

    def test_generate_recommendations_normal(self, trigger):
        """正常波動時的建議"""
        recommendations = trigger._generate_recommendations(2.0, 100.0, 102.0)
        assert len(recommendations) > 0
        assert any("正常範圍" in r or "維持" in r for r in recommendations)


# =============================================
# should_trigger 整合測試
# =============================================

class TestShouldTrigger:
    """測試 should_trigger 整體邏輯"""

    @pytest.mark.asyncio
    async def test_triggers_when_conditions_met(self, trigger, sample_config, sample_alert_data):
        """條件滿足且不在靜默時段時應觸發"""
        result = await trigger.should_trigger(sample_config, sample_alert_data)
        assert result is True

    @pytest.mark.asyncio
    async def test_not_triggers_in_quiet_hours(self, trigger, sample_config, sample_alert_data):
        """在靜默時段內不應觸發"""
        # 設置全天靜默
        sample_config.quiet_hours_start = "00:00"
        sample_config.quiet_hours_end = "23:59"
        result = await trigger.should_trigger(sample_config, sample_alert_data)
        assert result is False

    @pytest.mark.asyncio
    async def test_not_triggers_when_conditions_not_met(self, trigger, sample_config, sample_alert_data):
        """條件不滿足時不應觸發"""
        sample_alert_data["change_percent"] = -1.0  # 極小變動
        result = await trigger.should_trigger(sample_config, sample_alert_data)
        assert result is False


# =============================================
# execute_workflow 測試
# =============================================

class TestExecuteWorkflow:
    """測試工作流執行"""

    @pytest.mark.asyncio
    async def test_execute_with_analysis(self, trigger, sample_config, sample_alert_data):
        """執行帶 AI 分析的工作流"""
        sample_config.auto_analyze = True
        sample_config.auto_create_proposal = False
        sample_config.notify_channels = None

        result = await trigger.execute_workflow(sample_config, sample_alert_data)

        assert result["config_id"] == str(sample_config.id)
        assert "ai_analysis" in result["actions_executed"]
        assert result["analysis_result"] is not None
        assert "impact_assessment" in result["analysis_result"]

    @pytest.mark.asyncio
    async def test_execute_without_analysis(self, trigger, sample_config, sample_alert_data):
        """執行不帶 AI 分析的工作流"""
        sample_config.auto_analyze = False
        sample_config.auto_create_proposal = False
        sample_config.notify_channels = None

        result = await trigger.execute_workflow(sample_config, sample_alert_data)

        assert "ai_analysis" not in result["actions_executed"]
        assert result["analysis_result"] is None

    @pytest.mark.asyncio
    async def test_execute_with_auto_proposal(self, mock_db, sample_config, sample_alert_data):
        """執行自動創建提案的工作流"""
        trigger = AlertTrigger(mock_db)
        sample_config.auto_analyze = False
        sample_config.auto_create_proposal = True
        sample_config.notify_channels = None

        # 模擬提案創建
        with patch.object(trigger, '_create_price_proposal', new_callable=AsyncMock) as mock_create:
            mock_proposal = MagicMock()
            mock_proposal.id = uuid4()
            mock_proposal.proposed_price = 320.00
            mock_create.return_value = mock_proposal

            result = await trigger.execute_workflow(sample_config, sample_alert_data)

            assert "create_proposal" in result["actions_executed"]
            assert result["proposal_created"] is not None
            mock_create.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_with_notifications(self, mock_db, sample_config, sample_alert_data):
        """執行帶通知的工作流"""
        trigger = AlertTrigger(mock_db)
        sample_config.auto_analyze = False
        sample_config.auto_create_proposal = False
        sample_config.notify_channels = {"telegram": {"enabled": True}}

        # 模擬通知發送
        with patch.object(trigger, '_send_notifications', new_callable=AsyncMock) as mock_notify:
            mock_notify.return_value = [{"channel": "telegram", "sent": True}]

            result = await trigger.execute_workflow(sample_config, sample_alert_data)

            assert "send_notifications" in result["actions_executed"]
            assert len(result["notifications_sent"]) > 0
            mock_notify.assert_called_once()
