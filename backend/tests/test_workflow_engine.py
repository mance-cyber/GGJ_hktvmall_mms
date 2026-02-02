# =============================================
# Workflow Engine 單元測試
# =============================================

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from decimal import Decimal
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.workflow.engine import (
    WorkflowEngine,
    WorkflowStatus,
    TriggerType,
    WorkflowExecution,
    TriggerConfig,
)
from app.services.workflow.actions import (
    create_pricing_proposal,
    send_telegram_notification,
    handle_pricing_approval_trigger,
)
from app.models.pricing import PriceProposal, ProposalStatus, SourceType
from app.models.product import Product


# =============================================
# WorkflowEngine 測試
# =============================================

class TestWorkflowEngine:
    """測試 WorkflowEngine 核心功能"""

    @pytest_asyncio.fixture
    async def engine(self, db_session: AsyncSession):
        """創建 WorkflowEngine 實例"""
        return WorkflowEngine(db_session)

    @pytest.mark.asyncio
    async def test_register_trigger(self, engine: WorkflowEngine):
        """測試註冊觸發器"""
        async def dummy_handler(db, **kwargs):
            return {"status": "ok"}

        engine.register_trigger(
            TriggerType.PRICING_APPROVAL,
            dummy_handler,
            "測試觸發器"
        )

        assert TriggerType.PRICING_APPROVAL in engine._triggers
        assert engine._triggers[TriggerType.PRICING_APPROVAL].description == "測試觸發器"

    @pytest.mark.asyncio
    async def test_trigger_unknown_type_raises_error(self, engine: WorkflowEngine):
        """測試觸發未知類型會拋出錯誤"""
        with pytest.raises(ValueError) as exc_info:
            await engine.trigger(TriggerType.PRICING_APPROVAL)

        assert "Unknown trigger type" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_trigger_successful_execution(self, engine: WorkflowEngine):
        """測試成功觸發工作流"""
        test_result = {"proposal_id": "123", "status": "created"}

        async def success_handler(db, conversation_id=None, **kwargs):
            return test_result

        engine.register_trigger(
            TriggerType.PRICING_APPROVAL,
            success_handler,
            "成功處理器"
        )

        execution = await engine.trigger(
            TriggerType.PRICING_APPROVAL,
            conversation_id="conv-123"
        )

        assert execution.status == WorkflowStatus.COMPLETED
        assert execution.result == test_result
        assert execution.conversation_id == "conv-123"
        assert execution.error_message is None

    @pytest.mark.asyncio
    async def test_trigger_failed_execution(self, engine: WorkflowEngine):
        """測試失敗觸發工作流"""
        async def fail_handler(db, **kwargs):
            raise ValueError("處理失敗")

        engine.register_trigger(
            TriggerType.PRICING_APPROVAL,
            fail_handler,
            "失敗處理器"
        )

        with pytest.raises(ValueError):
            await engine.trigger(TriggerType.PRICING_APPROVAL)

        # 檢查執行記錄
        executions = list(engine._executions.values())
        assert len(executions) == 1
        assert executions[0].status == WorkflowStatus.FAILED
        assert "處理失敗" in executions[0].error_message

    @pytest.mark.asyncio
    async def test_get_execution(self, engine: WorkflowEngine):
        """測試獲取執行記錄"""
        async def handler(db, **kwargs):
            return {"ok": True}

        engine.register_trigger(TriggerType.PRICING_APPROVAL, handler, "")

        execution = await engine.trigger(TriggerType.PRICING_APPROVAL)

        # 通過 ID 獲取
        retrieved = engine.get_execution(execution.id)
        assert retrieved is not None
        assert retrieved.id == execution.id

        # 不存在的 ID
        assert engine.get_execution("non-existent") is None

    @pytest.mark.asyncio
    async def test_get_executions_by_conversation(self, engine: WorkflowEngine):
        """測試按對話 ID 獲取執行記錄"""
        async def handler(db, **kwargs):
            return {"ok": True}

        engine.register_trigger(TriggerType.PRICING_APPROVAL, handler, "")

        # 創建多個執行
        await engine.trigger(TriggerType.PRICING_APPROVAL, conversation_id="conv-1")
        await engine.trigger(TriggerType.PRICING_APPROVAL, conversation_id="conv-1")
        await engine.trigger(TriggerType.PRICING_APPROVAL, conversation_id="conv-2")

        # 獲取 conv-1 的執行記錄
        conv1_executions = engine.get_executions_by_conversation("conv-1")
        assert len(conv1_executions) == 2

        # 獲取 conv-2 的執行記錄
        conv2_executions = engine.get_executions_by_conversation("conv-2")
        assert len(conv2_executions) == 1

    @pytest.mark.asyncio
    async def test_get_registered_triggers(self, engine: WorkflowEngine):
        """測試獲取已註冊觸發器列表"""
        async def handler(db, **kwargs):
            return {}

        engine.register_trigger(TriggerType.PRICING_APPROVAL, handler, "")
        engine.register_trigger(TriggerType.ALERT_RESPONSE, handler, "")

        triggers = engine.get_registered_triggers()
        assert TriggerType.PRICING_APPROVAL in triggers
        assert TriggerType.ALERT_RESPONSE in triggers
        assert len(triggers) == 2


# =============================================
# 改價提案動作測試
# =============================================

class TestCreatePricingProposalAction:
    """測試 create_pricing_proposal 動作"""

    @pytest_asyncio.fixture
    async def test_product(self, db_session: AsyncSession) -> Product:
        """創建測試產品"""
        product = Product(
            name="測試和牛",
            sku="TEST-WAGYU-001",
            price=Decimal("599.00"),
            cost=Decimal("400.00"),
            min_price=Decimal("500.00"),
        )
        db_session.add(product)
        await db_session.commit()
        await db_session.refresh(product)
        return product

    @pytest.mark.asyncio
    async def test_create_proposal_success(
        self,
        db_session: AsyncSession,
        test_product: Product
    ):
        """測試成功創建改價提案"""
        result = await create_pricing_proposal(
            db=db_session,
            conversation_id="conv-test-123",
            product_id=str(test_product.id),
            proposed_price=549.00,
            reason="競品降價，建議跟進",
        )

        assert result["success"] is True
        assert result["product_name"] == "測試和牛"
        assert result["product_sku"] == "TEST-WAGYU-001"
        assert result["current_price"] == 599.00
        assert result["proposed_price"] == 549.00
        assert result["source_type"] == SourceType.AI_SUGGESTION

    @pytest.mark.asyncio
    async def test_create_proposal_missing_product_id(self, db_session: AsyncSession):
        """測試缺少 product_id 會報錯"""
        with pytest.raises(ValueError) as exc_info:
            await create_pricing_proposal(
                db=db_session,
                proposed_price=100.00,
            )

        assert "product_id is required" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_proposal_missing_price(
        self,
        db_session: AsyncSession,
        test_product: Product
    ):
        """測試缺少 proposed_price 會報錯"""
        with pytest.raises(ValueError) as exc_info:
            await create_pricing_proposal(
                db=db_session,
                product_id=str(test_product.id),
            )

        assert "proposed_price is required" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_proposal_product_not_found(self, db_session: AsyncSession):
        """測試產品不存在會報錯"""
        fake_id = str(uuid.uuid4())

        with pytest.raises(ValueError) as exc_info:
            await create_pricing_proposal(
                db=db_session,
                product_id=fake_id,
                proposed_price=100.00,
            )

        assert "not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_proposal_duplicate_pending(
        self,
        db_session: AsyncSession,
        test_product: Product
    ):
        """測試重複創建待審批提案會返回失敗"""
        # 第一次創建
        result1 = await create_pricing_proposal(
            db=db_session,
            product_id=str(test_product.id),
            proposed_price=549.00,
        )
        assert result1["success"] is True

        # 第二次創建同一產品
        result2 = await create_pricing_proposal(
            db=db_session,
            product_id=str(test_product.id),
            proposed_price=499.00,
        )
        assert result2["success"] is False
        assert "existing_proposal_id" in result2


# =============================================
# Telegram 通知動作測試
# =============================================

class TestSendTelegramNotification:
    """測試 send_telegram_notification 動作"""

    @pytest.mark.asyncio
    async def test_send_general_notification(self, db_session: AsyncSession):
        """測試發送一般通知"""
        with patch("app.services.workflow.actions.get_telegram_notifier") as mock_get:
            mock_notifier = MagicMock()
            mock_notifier.send_message = AsyncMock(return_value={"ok": True, "result": {"message_id": 123}})
            mock_get.return_value = mock_notifier

            result = await send_telegram_notification(
                db=db_session,
                notification_type="general",
                message="測試消息"
            )

            assert result["success"] is True
            assert result["message_id"] == 123

    @pytest.mark.asyncio
    async def test_send_proposal_notification(self, db_session: AsyncSession):
        """測試發送提案通知"""
        with patch("app.services.workflow.actions.get_telegram_notifier") as mock_get:
            mock_notifier = MagicMock()
            mock_notifier.send_message = AsyncMock(return_value={"ok": True, "result": {"message_id": 456}})
            mock_notifier._escape_html = lambda x: x  # 簡單實現
            mock_get.return_value = mock_notifier

            result = await send_telegram_notification(
                db=db_session,
                notification_type="proposal_created",
                product_name="測試和牛",
                product_sku="TEST-001",
                current_price=599.00,
                proposed_price=549.00,
                reason="競品降價",
            )

            assert result["success"] is True
            assert result["notification_type"] == "proposal_created"

    @pytest.mark.asyncio
    async def test_send_notification_no_message(self, db_session: AsyncSession):
        """測試發送空消息會失敗"""
        result = await send_telegram_notification(
            db=db_session,
            notification_type="general",
        )

        assert result["success"] is False
        assert "No message" in result["message"]


# =============================================
# 完整工作流觸發測試
# =============================================

class TestHandlePricingApprovalTrigger:
    """測試完整的改價審批工作流觸發"""

    @pytest_asyncio.fixture
    async def test_product(self, db_session: AsyncSession) -> Product:
        """創建測試產品"""
        product = Product(
            name="測試海膽",
            sku="TEST-UNI-001",
            price=Decimal("299.00"),
        )
        db_session.add(product)
        await db_session.commit()
        await db_session.refresh(product)
        return product

    @pytest.mark.asyncio
    async def test_full_workflow_trigger(
        self,
        db_session: AsyncSession,
        test_product: Product
    ):
        """測試完整工作流觸發"""
        with patch("app.services.workflow.actions.get_telegram_notifier") as mock_get:
            mock_notifier = MagicMock()
            mock_notifier.send_message = AsyncMock(return_value={"ok": True, "result": {"message_id": 789}})
            mock_notifier._escape_html = lambda x: x
            mock_get.return_value = mock_notifier

            result = await handle_pricing_approval_trigger(
                db=db_session,
                conversation_id="conv-full-test",
                product_id=str(test_product.id),
                proposed_price=249.00,
                reason="季節性促銷",
                send_notification=True,
            )

            assert result["success"] is True
            assert result["proposal"] is not None
            assert result["proposal"]["success"] is True
            assert result["notification"]["success"] is True

    @pytest.mark.asyncio
    async def test_workflow_trigger_no_notification(
        self,
        db_session: AsyncSession,
        test_product: Product
    ):
        """測試工作流觸發但不發通知"""
        result = await handle_pricing_approval_trigger(
            db=db_session,
            product_id=str(test_product.id),
            proposed_price=249.00,
            send_notification=False,
        )

        assert result["success"] is True
        assert result["proposal"]["success"] is True
        assert result["notification"] is None
