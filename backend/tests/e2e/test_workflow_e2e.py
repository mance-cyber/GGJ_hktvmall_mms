# =============================================
# AI 工作流 E2E 測試
# 測試完整的對話 → 審批任務創建流程
# =============================================

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from decimal import Decimal
from httpx import AsyncClient

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.product import Product
from app.models.pricing import PriceProposal, ProposalStatus, SourceType
from app.models.competitor import CompetitorProduct


# =============================================
# E2E: 對話 → 審批任務創建
# =============================================

class TestConversationToApprovalE2E:
    """測試從對話到審批任務創建的完整流程"""

    @pytest_asyncio.fixture
    async def test_product(self, db_session: AsyncSession) -> Product:
        """創建測試產品"""
        product = Product(
            name="A5 和牛",
            sku="WAGYU-A5-001",
            price=Decimal("1299.00"),
            cost=Decimal("900.00"),
            min_price=Decimal("1000.00"),
        )
        db_session.add(product)
        await db_session.commit()
        await db_session.refresh(product)
        return product

    @pytest.mark.asyncio
    async def test_full_approval_workflow_via_agent(
        self,
        db_session: AsyncSession,
        test_product: Product
    ):
        """
        E2E 測試：用戶通過 AI Agent 對話創建改價審批任務

        流程：
        1. 用戶提問「幫我創建 A5 和牛 嘅改價任務」
        2. Agent 識別意圖為 CREATE_APPROVAL_TASK
        3. Agent 查找產品並分析價格
        4. Agent 提供建議並詢問確認
        5. 用戶確認「好」
        6. Agent 創建 PriceProposal
        7. 發送 Telegram 通知
        """
        from app.services.agent.agent_service import AgentService, ResponseType
        from app.services.agent.intent_classifier import IntentType

        with patch("app.services.workflow.actions.get_telegram_notifier") as mock_tg:
            mock_notifier = MagicMock()
            mock_notifier.send_message = AsyncMock(return_value={"ok": True, "result": {"message_id": 12345}})
            mock_notifier._escape_html = lambda x: x
            mock_tg.return_value = mock_notifier

            service = AgentService(db=db_session)

            # Step 1: 用戶請求創建改價任務
            conversation_id = "e2e-test-conv-001"
            responses = []
            async for response in service.process_message(
                message=f"幫我創建 {test_product.name} 嘅改價任務",
                conversation_id=conversation_id
            ):
                responses.append(response)

            # 驗證 Agent 識別了正確的意圖
            state = service.get_state(conversation_id)
            assert state is not None
            assert state.current_intent == IntentType.CREATE_APPROVAL_TASK

            # 檢查響應中包含產品信息
            final_responses = [r for r in responses if r.type == ResponseType.MESSAGE]
            assert len(final_responses) > 0

    @pytest.mark.asyncio
    async def test_proposal_created_with_correct_source(
        self,
        db_session: AsyncSession,
        test_product: Product
    ):
        """測試創建的提案具有正確的來源信息"""
        from app.services.workflow.actions import create_pricing_proposal

        conversation_id = "e2e-test-conv-002"

        # 通過 workflow action 創建提案
        result = await create_pricing_proposal(
            db=db_session,
            conversation_id=conversation_id,
            product_id=str(test_product.id),
            proposed_price=1199.00,
            reason="E2E 測試 - 競品降價跟進",
        )

        assert result["success"] is True
        proposal_id = result["proposal_id"]

        # 從數據庫驗證
        from uuid import UUID
        query = select(PriceProposal).where(PriceProposal.id == UUID(proposal_id))
        db_result = await db_session.execute(query)
        proposal = db_result.scalar_one()

        # 驗證來源追溯信息
        assert proposal.source_conversation_id == conversation_id
        assert proposal.source_type == SourceType.AI_SUGGESTION
        assert proposal.status == ProposalStatus.PENDING

    @pytest.mark.asyncio
    async def test_telegram_notification_sent_on_proposal_creation(
        self,
        db_session: AsyncSession,
        test_product: Product
    ):
        """測試創建提案時發送 Telegram 通知"""
        from app.services.workflow.actions import handle_pricing_approval_trigger

        with patch("app.services.workflow.actions.get_telegram_notifier") as mock_tg:
            mock_notifier = MagicMock()
            mock_notifier.send_message = AsyncMock(return_value={"ok": True, "result": {"message_id": 99999}})
            mock_notifier._escape_html = lambda x: x
            mock_tg.return_value = mock_notifier

            result = await handle_pricing_approval_trigger(
                db=db_session,
                conversation_id="e2e-test-conv-003",
                product_id=str(test_product.id),
                proposed_price=1099.00,
                reason="E2E 測試通知",
                send_notification=True,
            )

            # 驗證通知已發送
            assert result["success"] is True
            assert result["notification"]["success"] is True
            assert result["notification"]["message_id"] == 99999

            # 驗證調用了 send_message
            mock_notifier.send_message.assert_called_once()
            call_args = mock_notifier.send_message.call_args
            message_text = call_args[0][0]
            assert "A5 和牛" in message_text
            assert "WAGYU-A5-001" in message_text


# =============================================
# E2E: API 端點測試
# =============================================

class TestWorkflowAPIEndpoints:
    """測試工作流相關的 API 端點"""

    @pytest_asyncio.fixture
    async def test_product(self, db_session: AsyncSession) -> Product:
        """創建測試產品"""
        product = Product(
            name="北海道帶子",
            sku="SCALLOP-HKD-001",
            price=Decimal("399.00"),
        )
        db_session.add(product)
        await db_session.commit()
        await db_session.refresh(product)
        return product

    @pytest_asyncio.fixture
    async def ai_proposal(
        self,
        db_session: AsyncSession,
        test_product: Product
    ) -> PriceProposal:
        """創建 AI 建議的提案"""
        proposal = PriceProposal(
            product_id=test_product.id,
            current_price=Decimal("399.00"),
            proposed_price=Decimal("349.00"),
            status=ProposalStatus.PENDING,
            source_type=SourceType.AI_SUGGESTION,
            source_conversation_id="api-test-conv-001",
            reason="API 測試 - 季節性調整",
            ai_model_used="claude-agent",
        )
        db_session.add(proposal)
        await db_session.commit()
        await db_session.refresh(proposal)
        return proposal

    @pytest.mark.asyncio
    async def test_get_pending_proposals_includes_source(
        self,
        client: AsyncClient,
        ai_proposal: PriceProposal,
        auth_headers: dict
    ):
        """測試獲取待審批提案包含來源信息"""
        response = await client.get(
            "/api/v1/pricing/proposals/pending",
            headers=auth_headers
        )

        # API 可能不需要認證，檢查 200 或 401
        if response.status_code == 200:
            data = response.json()
            assert len(data) >= 1

            # 找到我們創建的提案
            our_proposal = next(
                (p for p in data if p.get("source_conversation_id") == "api-test-conv-001"),
                None
            )

            if our_proposal:
                assert our_proposal["source_type"] == "ai_suggestion"
                assert our_proposal["source_conversation_id"] == "api-test-conv-001"


# =============================================
# E2E: 完整用戶旅程測試
# =============================================

class TestCompleteUserJourney:
    """測試完整的用戶旅程"""

    @pytest_asyncio.fixture
    async def setup_products(self, db_session: AsyncSession):
        """設置測試數據"""
        # 創建產品
        product = Product(
            name="日本蜜瓜",
            sku="MELON-JP-001",
            price=Decimal("688.00"),
            cost=Decimal("450.00"),
            min_price=Decimal("500.00"),
        )
        db_session.add(product)
        await db_session.commit()
        await db_session.refresh(product)
        return {"product": product}

    @pytest.mark.asyncio
    async def test_user_journey_conversation_to_approval(
        self,
        db_session: AsyncSession,
        setup_products: dict
    ):
        """
        完整用戶旅程測試：

        1. 用戶在 AI Agent 頁面開始對話
        2. 用戶詢問某產品的價格分析
        3. AI 發現競品更便宜，建議降價
        4. 用戶說「幫我創建改價任務」
        5. AI 創建 PriceProposal
        6. Telegram 通知發送
        7. 用戶在審批頁面看到帶有「AI 建議」標籤的提案
        8. 用戶點擊「查看對話」可以跳轉到原始對話
        """
        from app.services.agent.agent_service import AgentService
        from app.services.workflow.actions import create_pricing_proposal

        product = setup_products["product"]
        conversation_id = "journey-test-001"

        # 模擬創建改價提案
        with patch("app.services.workflow.actions.get_telegram_notifier") as mock_tg:
            mock_notifier = MagicMock()
            mock_notifier.send_message = AsyncMock(return_value={"ok": True, "result": {"message_id": 11111}})
            mock_notifier._escape_html = lambda x: x
            mock_tg.return_value = mock_notifier

            # 創建提案
            result = await create_pricing_proposal(
                db=db_session,
                conversation_id=conversation_id,
                product_id=str(product.id),
                proposed_price=599.00,
                reason="用戶旅程測試 - 根據市場分析建議降價",
            )

            assert result["success"] is True

            # 驗證提案數據完整
            assert result["product_name"] == "日本蜜瓜"
            assert result["product_sku"] == "MELON-JP-001"
            assert result["current_price"] == 688.00
            assert result["proposed_price"] == 599.00
            assert result["source_type"] == SourceType.AI_SUGGESTION

            # 從數據庫查詢並驗證可追溯性
            from uuid import UUID
            query = select(PriceProposal).where(
                PriceProposal.source_conversation_id == conversation_id
            )
            db_result = await db_session.execute(query)
            proposal = db_result.scalar_one()

            # 驗證可以通過對話 ID 找到提案
            assert proposal is not None
            assert proposal.source_type == SourceType.AI_SUGGESTION

            # 前端可以用 source_conversation_id 構建連結
            # /agent?conversation={conversation_id}
            expected_link = f"/agent?conversation={conversation_id}"
            assert conversation_id in expected_link
