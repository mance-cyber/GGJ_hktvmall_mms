# =============================================
# Agent 工作流意圖處理測試
# =============================================

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from decimal import Decimal
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.agent.intent_classifier import IntentClassifier, IntentType, IntentResult
from app.services.agent.tools.workflow_tools import (
    CreateApprovalTaskTool,
    GetPendingProposalsTool,
    SuggestPriceChangeTool,
)
from app.models.product import Product
from app.models.pricing import PriceProposal, ProposalStatus, SourceType


# =============================================
# 意圖識別測試
# =============================================

class TestWorkflowIntentClassification:
    """測試工作流相關意圖識別"""

    @pytest.fixture
    def classifier(self):
        """創建意圖識別器"""
        return IntentClassifier()

    @pytest.mark.asyncio
    async def test_classify_create_approval_task_intent(self, classifier: IntentClassifier):
        """測試識別創建審批任務意圖"""
        test_messages = [
            "幫我創建改價任務",
            "想改呢個價",
            "申請改價到 $99",
            "建議改價",
            "提交審批",
        ]

        for msg in test_messages:
            result = await classifier.classify(msg)
            assert result.intent == IntentType.CREATE_APPROVAL_TASK, f"Failed for: {msg}"
            assert result.confidence >= 0.5

    @pytest.mark.asyncio
    async def test_classify_confirm_action_intent(self, classifier: IntentClassifier):
        """測試識別確認動作意圖"""
        test_messages = [
            "好",
            "確認",
            "係",
            "ok",
            "同意",
            "執行",
        ]

        for msg in test_messages:
            result = await classifier.classify(msg)
            assert result.intent == IntentType.CONFIRM_ACTION, f"Failed for: {msg}"

    @pytest.mark.asyncio
    async def test_classify_decline_action_intent(self, classifier: IntentClassifier):
        """測試識別拒絕動作意圖"""
        test_messages = [
            "唔好",
            "取消",
            "算啦",
            "唔要",
            "拒絕",
        ]

        for msg in test_messages:
            result = await classifier.classify(msg)
            assert result.intent == IntentType.DECLINE_ACTION, f"Failed for: {msg}"


# =============================================
# 工作流工具測試
# =============================================

class TestCreateApprovalTaskTool:
    """測試 CreateApprovalTaskTool"""

    @pytest_asyncio.fixture
    async def test_product(self, db_session: AsyncSession) -> Product:
        """創建測試產品"""
        product = Product(
            name="測試三文魚",
            sku="TEST-SALMON-001",
            price=Decimal("199.00"),
        )
        db_session.add(product)
        await db_session.commit()
        await db_session.refresh(product)
        return product

    @pytest.mark.asyncio
    async def test_create_approval_task_success(
        self,
        db_session: AsyncSession,
        test_product: Product
    ):
        """測試成功創建審批任務"""
        with patch("app.services.agent.tools.workflow_tools.handle_pricing_approval_trigger") as mock_trigger:
            mock_trigger.return_value = {
                "success": True,
                "proposal": {
                    "success": True,
                    "proposal_id": "test-proposal-id",
                    "product_name": "測試三文魚",
                    "product_sku": "TEST-SALMON-001",
                    "current_price": 199.00,
                    "proposed_price": 179.00,
                },
                "notification": {"success": True},
            }

            tool = CreateApprovalTaskTool(db_session)
            result = await tool.execute(
                product_id=str(test_product.id),
                proposed_price=179.00,
                reason="競品降價",
                conversation_id="conv-test",
            )

            assert result.success is True
            assert result.data["proposal_id"] == "test-proposal-id"

    @pytest.mark.asyncio
    async def test_create_approval_task_failure(self, db_session: AsyncSession):
        """測試創建審批任務失敗"""
        with patch("app.services.agent.tools.workflow_tools.handle_pricing_approval_trigger") as mock_trigger:
            mock_trigger.return_value = {
                "success": False,
                "error": "產品不存在",
            }

            tool = CreateApprovalTaskTool(db_session)
            result = await tool.execute(
                product_id="fake-id",
                proposed_price=100.00,
            )

            assert result.success is False
            assert "產品不存在" in result.error


class TestGetPendingProposalsTool:
    """測試 GetPendingProposalsTool"""

    @pytest_asyncio.fixture
    async def test_product(self, db_session: AsyncSession) -> Product:
        """創建測試產品"""
        product = Product(
            name="測試鰻魚",
            sku="TEST-EEL-001",
            price=Decimal("399.00"),
        )
        db_session.add(product)
        await db_session.commit()
        await db_session.refresh(product)
        return product

    @pytest_asyncio.fixture
    async def pending_proposals(
        self,
        db_session: AsyncSession,
        test_product: Product
    ):
        """創建待審批提案"""
        proposals = []
        for i in range(3):
            proposal = PriceProposal(
                product_id=test_product.id,
                current_price=Decimal("399.00"),
                proposed_price=Decimal(f"{350 - i * 10}.00"),
                status=ProposalStatus.PENDING,
                source_type=SourceType.AI_SUGGESTION,
                reason=f"測試提案 {i+1}",
            )
            db_session.add(proposal)
            proposals.append(proposal)

        await db_session.commit()
        return proposals

    @pytest.mark.asyncio
    async def test_get_pending_proposals(
        self,
        db_session: AsyncSession,
        pending_proposals
    ):
        """測試獲取待審批提案"""
        tool = GetPendingProposalsTool(db_session)
        result = await tool.execute()

        assert result.success is True
        assert result.data["count"] == 3

    @pytest.mark.asyncio
    async def test_get_pending_proposals_with_limit(
        self,
        db_session: AsyncSession,
        pending_proposals
    ):
        """測試限制返回數量"""
        tool = GetPendingProposalsTool(db_session)
        result = await tool.execute(limit=2)

        assert result.success is True
        assert result.data["count"] == 2

    @pytest.mark.asyncio
    async def test_get_pending_proposals_empty(self, db_session: AsyncSession):
        """測試無待審批提案"""
        tool = GetPendingProposalsTool(db_session)
        result = await tool.execute()

        assert result.success is True
        assert result.data["count"] == 0


class TestSuggestPriceChangeTool:
    """測試 SuggestPriceChangeTool"""

    @pytest_asyncio.fixture
    async def test_product(self, db_session: AsyncSession) -> Product:
        """創建測試產品"""
        product = Product(
            name="測試龍蝦",
            sku="TEST-LOBSTER-001",
            price=Decimal("899.00"),
            cost=Decimal("600.00"),
            min_price=Decimal("700.00"),
        )
        db_session.add(product)
        await db_session.commit()
        await db_session.refresh(product)
        return product

    @pytest.mark.asyncio
    async def test_suggest_price_no_competitors(
        self,
        db_session: AsyncSession,
        test_product: Product
    ):
        """測試無競品時的建議"""
        tool = SuggestPriceChangeTool(db_session)
        result = await tool.execute(product_id=str(test_product.id))

        assert result.success is True
        assert result.data["recommendation"] == "暫無競品數據，無法生成自動建議"

    @pytest.mark.asyncio
    async def test_suggest_price_product_not_found(self, db_session: AsyncSession):
        """測試產品不存在"""
        tool = SuggestPriceChangeTool(db_session)
        result = await tool.execute(product_id=str(uuid.uuid4()))

        assert result.success is False
        assert "找不到產品" in result.error


# =============================================
# Agent Service 工作流處理測試
# =============================================

class TestAgentServiceWorkflowHandling:
    """測試 AgentService 的工作流處理邏輯"""

    @pytest_asyncio.fixture
    async def test_product(self, db_session: AsyncSession) -> Product:
        """創建測試產品"""
        product = Product(
            name="測試蟹",
            sku="TEST-CRAB-001",
            price=Decimal("499.00"),
        )
        db_session.add(product)
        await db_session.commit()
        await db_session.refresh(product)
        return product

    @pytest.mark.asyncio
    async def test_agent_handles_create_approval_intent(
        self,
        db_session: AsyncSession,
        test_product: Product
    ):
        """測試 Agent 處理創建審批意圖"""
        from app.services.agent.agent_service import AgentService, ResponseType

        service = AgentService(db=db_session)

        # 模擬對話：用戶請求創建改價任務
        responses = []
        async for response in service.process_message(
            message=f"幫我創建 {test_product.name} 嘅改價任務",
            conversation_id="test-conv-1"
        ):
            responses.append(response)

        # 應該有思考狀態和回應
        assert len(responses) > 0
        # 最後一個響應應該是消息類型
        final_response = responses[-1]
        assert final_response.type in [ResponseType.MESSAGE, ResponseType.THINKING]

    @pytest.mark.asyncio
    async def test_agent_handles_confirm_without_pending_action(
        self,
        db_session: AsyncSession
    ):
        """測試 Agent 處理確認但沒有待確認動作"""
        from app.services.agent.agent_service import AgentService, ResponseType

        service = AgentService(db=db_session)

        responses = []
        async for response in service.process_message(
            message="好",
            conversation_id="test-conv-2"
        ):
            responses.append(response)

        # 應該回應沒有需要確認的東西
        final_response = responses[-1]
        assert final_response.type == ResponseType.MESSAGE
        assert "冇嘢需要確認" in final_response.content

    @pytest.mark.asyncio
    async def test_agent_handles_decline_action(self, db_session: AsyncSession):
        """測試 Agent 處理拒絕動作"""
        from app.services.agent.agent_service import AgentService, ResponseType

        service = AgentService(db=db_session)

        responses = []
        async for response in service.process_message(
            message="唔好",
            conversation_id="test-conv-3"
        ):
            responses.append(response)

        final_response = responses[-1]
        assert final_response.type == ResponseType.MESSAGE
        assert "取消" in final_response.content
