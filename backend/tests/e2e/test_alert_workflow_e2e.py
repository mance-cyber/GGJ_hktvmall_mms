# =============================================
# 告警工作流 E2E 測試
# =============================================
# 測試完整流程：
# - 價格告警觸發
# - AI 分析生成
# - Telegram 通知發送
# - Webhook 回調處理
# =============================================

import pytest
from datetime import datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from httpx import ASGITransport, AsyncClient
from fastapi import FastAPI

from app.api.v1.workflow import router as workflow_router
from app.api.v1.telegram import router as telegram_router


# =============================================
# Fixtures
# =============================================

@pytest.fixture
def app():
    """創建測試 FastAPI 應用"""
    app = FastAPI()
    app.include_router(workflow_router, prefix="/api/v1/workflow")
    app.include_router(telegram_router, prefix="/api/v1/telegram")
    return app


@pytest.fixture
def sample_alert_config_data():
    """示例告警配置數據"""
    return {
        "name": "大幅降價告警",
        "is_active": True,
        "trigger_conditions": {
            "price_drop_threshold": 10,
            "price_increase_threshold": 15,
        },
        "auto_analyze": True,
        "auto_create_proposal": False,
        "notify_channels": {
            "telegram": {"enabled": True}
        },
        "quiet_hours_start": "00:00",
        "quiet_hours_end": "06:00",
    }


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
        "competitor_id": str(uuid4()),
    }


@pytest.fixture
def mock_db_session():
    """模擬數據庫 session"""
    session = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.execute = AsyncMock()
    session.get = AsyncMock()
    session.delete = AsyncMock()
    return session


# =============================================
# Alert Config API 測試
# =============================================

class TestAlertConfigAPI:
    """測試告警配置 API 端點"""

    @pytest.mark.asyncio
    async def test_alert_config_schema_validation(self, sample_alert_config_data):
        """測試告警配置 Schema 驗證"""
        from app.schemas.workflow import AlertConfigCreate

        # 測試 schema 可以正確解析配置數據
        config = AlertConfigCreate(**sample_alert_config_data)

        assert config.name == sample_alert_config_data["name"]
        assert config.is_active == sample_alert_config_data["is_active"]
        assert config.trigger_conditions == sample_alert_config_data["trigger_conditions"]
        assert config.auto_analyze == sample_alert_config_data["auto_analyze"]

    @pytest.mark.asyncio
    async def test_alert_config_model_creation(self, sample_alert_config_data):
        """測試告警配置 Model 創建"""
        from app.models.workflow import AlertWorkflowConfig

        # 測試 model 可以正確創建
        config = AlertWorkflowConfig(
            name=sample_alert_config_data["name"],
            is_active=sample_alert_config_data["is_active"],
            trigger_conditions=sample_alert_config_data["trigger_conditions"],
            auto_analyze=sample_alert_config_data["auto_analyze"],
            auto_create_proposal=sample_alert_config_data["auto_create_proposal"],
            notify_channels=sample_alert_config_data["notify_channels"],
            quiet_hours_start=sample_alert_config_data["quiet_hours_start"],
            quiet_hours_end=sample_alert_config_data["quiet_hours_end"],
        )

        assert config.name == sample_alert_config_data["name"]
        assert config.trigger_conditions["price_drop_threshold"] == 10


# =============================================
# Alert Workflow 執行測試
# =============================================

class TestAlertWorkflowExecution:
    """測試告警工作流執行"""

    @pytest.mark.asyncio
    async def test_full_workflow_execution(self, sample_alert_data):
        """測試完整工作流執行：告警 → AI 分析 → 通知"""
        from app.services.workflow.triggers import AlertTrigger, process_price_alert

        mock_db = AsyncMock()
        trigger = AlertTrigger(mock_db)

        # 創建模擬配置
        mock_config = MagicMock()
        mock_config.id = uuid4()
        mock_config.name = "測試配置"
        mock_config.is_active = True
        mock_config.trigger_conditions = {"price_drop_threshold": 10}
        mock_config.auto_analyze = True
        mock_config.auto_create_proposal = False
        mock_config.notify_channels = None  # 跳過實際通知
        mock_config.quiet_hours_start = None
        mock_config.quiet_hours_end = None

        # 執行工作流
        result = await trigger.execute_workflow(mock_config, sample_alert_data)

        # 驗證結果
        assert result["config_id"] == str(mock_config.id)
        assert "ai_analysis" in result["actions_executed"]
        assert result["analysis_result"] is not None
        assert "impact_assessment" in result["analysis_result"]
        assert "recommendations" in result["analysis_result"]

        # 驗證分析內容
        analysis = result["analysis_result"]
        assert analysis["product_name"] == sample_alert_data["product_name"]
        assert analysis["price_change"]["change_percent"] == sample_alert_data["change_percent"]
        assert "高影響" in analysis["impact_assessment"]  # 23.2% 應該是高影響

    @pytest.mark.asyncio
    async def test_workflow_with_auto_proposal(self, sample_alert_data):
        """測試帶自動提案創建的工作流"""
        from app.services.workflow.triggers import AlertTrigger

        mock_db = AsyncMock()

        # 模擬 PriceProposal 添加
        def mock_add(obj):
            obj.id = uuid4()

        mock_db.add = mock_add
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()

        trigger = AlertTrigger(mock_db)

        mock_config = MagicMock()
        mock_config.id = uuid4()
        mock_config.name = "自動提案配置"
        mock_config.is_active = True
        mock_config.trigger_conditions = {"price_drop_threshold": 10}
        mock_config.auto_analyze = True
        mock_config.auto_create_proposal = True
        mock_config.notify_channels = None
        mock_config.quiet_hours_start = None
        mock_config.quiet_hours_end = None

        result = await trigger.execute_workflow(mock_config, sample_alert_data)

        # 驗證提案創建
        assert "create_proposal" in result["actions_executed"]
        assert result["proposal_created"] is not None

    @pytest.mark.asyncio
    async def test_process_price_alert_function(self, sample_alert_data):
        """測試 process_price_alert 便捷函數"""
        from app.services.workflow.triggers import process_price_alert

        mock_db = AsyncMock()

        # 模擬沒有活躍配置
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result

        results = await process_price_alert(mock_db, sample_alert_data)

        # 沒有配置時應返回空列表
        assert results == []


# =============================================
# Telegram Webhook 測試
# =============================================

class TestTelegramWebhook:
    """測試 Telegram Webhook 回調處理"""

    @pytest.mark.asyncio
    async def test_create_proposal_callback(self, app, mock_db_session):
        """測試創建改價任務按鈕回調"""
        product_id = str(uuid4())

        webhook_data = {
            "update_id": 12345,
            "callback_query": {
                "id": "callback_123",
                "data": f"create_proposal:{product_id}",
                "message": {
                    "chat": {"id": 987654321},
                    "message_id": 100
                }
            }
        }

        with patch("app.api.v1.telegram.get_db") as mock_get_db, \
             patch("app.api.v1.telegram.get_telegram_notifier") as mock_notifier:

            mock_get_db.return_value = mock_db_session

            # 模擬產品
            mock_product = MagicMock()
            mock_product.id = uuid4()
            mock_product.name = "測試產品"
            mock_db_session.get.return_value = mock_product

            # 模擬快照
            mock_snapshot_result = MagicMock()
            mock_snapshot = MagicMock()
            mock_snapshot.price = Decimal("298.00")
            mock_snapshot_result.scalar_one_or_none.return_value = mock_snapshot
            mock_db_session.execute.return_value = mock_snapshot_result

            # 模擬 Telegram
            notifier = MagicMock()
            notifier.enabled = True
            notifier.answer_callback_query = AsyncMock(return_value={"ok": True})
            notifier.edit_message_reply_markup = AsyncMock(return_value={"ok": True})
            mock_notifier.return_value = notifier

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/telegram/webhook",
                    json=webhook_data
                )

            # 驗證回調處理
            assert notifier.answer_callback_query.called

    @pytest.mark.asyncio
    async def test_ignore_alert_callback(self, app, mock_db_session):
        """測試忽略告警按鈕回調"""
        product_id = str(uuid4())

        webhook_data = {
            "update_id": 12346,
            "callback_query": {
                "id": "callback_456",
                "data": f"ignore_alert:{product_id}",
                "message": {
                    "chat": {"id": 987654321},
                    "message_id": 101
                }
            }
        }

        with patch("app.api.v1.telegram.get_db") as mock_get_db, \
             patch("app.api.v1.telegram.get_telegram_notifier") as mock_notifier:

            mock_get_db.return_value = mock_db_session

            notifier = MagicMock()
            notifier.enabled = True
            notifier.answer_callback_query = AsyncMock(return_value={"ok": True})
            notifier.edit_message_reply_markup = AsyncMock(return_value={"ok": True})
            mock_notifier.return_value = notifier

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/telegram/webhook",
                    json=webhook_data
                )

            # 驗證按鈕被移除
            notifier.edit_message_reply_markup.assert_called_once()


# =============================================
# Celery Task 整合測試
# =============================================

class TestCeleryTaskIntegration:
    """測試 Celery 任務整合"""

    @pytest.mark.asyncio
    async def test_execute_alert_workflow_task(self, sample_alert_data):
        """測試 execute_alert_workflow Celery 任務"""
        from app.services.workflow.triggers import process_price_alert

        # 直接測試 process_price_alert 函數
        mock_db = AsyncMock()

        # 模擬沒有活躍配置
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result

        results = await process_price_alert(mock_db, sample_alert_data)

        # 沒有配置時應返回空列表
        assert results == []
        assert mock_db.execute.called

    @pytest.mark.asyncio
    async def test_scrape_task_triggers_alert_workflow(self):
        """測試爬取任務觸發告警工作流"""
        from app.tasks.scrape_tasks import _check_price_alert

        mock_db = AsyncMock()

        # 創建模擬產品
        mock_product = MagicMock()
        mock_product.id = uuid4()
        mock_product.name = "測試產品"
        mock_product.competitor_id = uuid4()

        # 創建模擬快照
        mock_last_snapshot = MagicMock()
        mock_last_snapshot.price = Decimal("388.00")
        mock_last_snapshot.stock_status = "in_stock"

        # 創建模擬抓取信息
        mock_info = MagicMock()
        mock_info.price = Decimal("298.00")  # 23% 降價
        mock_info.stock_status = "in_stock"
        mock_info.name = "測試產品"

        threshold = 10.0  # 10% 閾值

        # Mock the import inside _check_price_alert
        with patch.dict('sys.modules', {'app.tasks.workflow_tasks': MagicMock()}):
            import app.tasks.workflow_tasks as workflow_tasks
            workflow_tasks.execute_alert_workflow = MagicMock()
            workflow_tasks.execute_alert_workflow.delay = MagicMock()

            await _check_price_alert(
                mock_db, mock_product, mock_last_snapshot, mock_info, threshold
            )

            # 驗證 PriceAlert 被創建
            assert mock_db.add.called


# =============================================
# Telegram Notification 測試
# =============================================

class TestTelegramNotification:
    """測試 Telegram 通知功能"""

    @pytest.mark.asyncio
    async def test_send_alert_notification_with_buttons(self, sample_alert_data):
        """測試發送帶按鈕的告警通知"""
        from app.services.telegram import TelegramNotifier

        with patch.object(TelegramNotifier, '__init__', return_value=None):
            notifier = TelegramNotifier()
            notifier.enabled = True
            notifier.api_url = "https://api.telegram.org/botTEST"
            notifier.chat_id = "123456"

            with patch("httpx.AsyncClient.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {"ok": True, "result": {"message_id": 100}}
                mock_post.return_value = mock_response

                analysis = {
                    "impact_assessment": "高影響：競爭對手大幅調價",
                    "recommendations": ["考慮跟進降價以維持競爭力"]
                }

                result = await notifier.send_alert_notification(
                    alert_data=sample_alert_data,
                    analysis=analysis,
                    include_action_buttons=True
                )

                # 驗證 API 被調用
                assert mock_post.called

                # 獲取調用參數
                call_kwargs = mock_post.call_args
                payload = call_kwargs.kwargs.get("json", {})

                # 驗證消息包含按鈕
                assert "reply_markup" in payload
                assert "inline_keyboard" in payload["reply_markup"]

    @pytest.mark.asyncio
    async def test_send_alert_notification_with_proposal(self, sample_alert_data):
        """測試發送帶提案信息的告警通知"""
        from app.services.telegram import TelegramNotifier

        with patch.object(TelegramNotifier, '__init__', return_value=None):
            notifier = TelegramNotifier()
            notifier.enabled = True
            notifier.api_url = "https://api.telegram.org/botTEST"
            notifier.chat_id = "123456"

            with patch("httpx.AsyncClient.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {"ok": True, "result": {"message_id": 101}}
                mock_post.return_value = mock_response

                proposal = {
                    "id": str(uuid4()),
                    "proposed_price": 320.00
                }

                result = await notifier.send_alert_notification(
                    alert_data=sample_alert_data,
                    proposal=proposal,
                    include_action_buttons=True
                )

                # 獲取調用參數
                call_kwargs = mock_post.call_args
                payload = call_kwargs.kwargs.get("json", {})

                # 驗證消息包含批准/拒絕按鈕
                keyboard = payload.get("reply_markup", {}).get("inline_keyboard", [])
                button_texts = [btn.get("text", "") for row in keyboard for btn in row]
                assert "✅ 批准提案" in button_texts
                assert "❌ 拒絕提案" in button_texts
