# =============================================
# AI Agent 主服務
# 協調意圖識別、槽位管理、工具執行和報告生成
# =============================================

from typing import Any, Dict, List, Optional, AsyncGenerator
from dataclasses import dataclass, field
from enum import Enum
import uuid
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from .intent_classifier import IntentClassifier, IntentType, IntentResult
from .slot_manager import SlotManager, AnalysisSlots, SlotStatus, SlotCompleteness
from .tool_executor import ToolExecutor
from .report_generator import ReportGenerator, Report


class ResponseType(Enum):
    """響應類型"""
    THINKING = "thinking"         # 思考中
    MESSAGE = "message"           # 普通訊息
    CLARIFICATION = "clarification"  # 需要澄清
    REPORT = "report"             # 分析報告
    ERROR = "error"               # 錯誤


@dataclass
class AgentMessage:
    """對話訊息"""
    role: str  # user, assistant
    content: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentState:
    """Agent 狀態"""
    conversation_id: str
    messages: List[AgentMessage]
    slots: AnalysisSlots
    current_intent: Optional[IntentType] = None
    pending_clarifications: List[Dict] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)  # 工作流等額外狀態
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "conversation_id": self.conversation_id,
            "messages": [
                {
                    "role": m.role,
                    "content": m.content,
                    "timestamp": m.timestamp.isoformat()
                }
                for m in self.messages
            ],
            "slots": self.slots.to_dict(),
            "current_intent": self.current_intent.value if self.current_intent else None,
            "pending_clarifications": self.pending_clarifications,
            "metadata": self.metadata,
        }


@dataclass
class AgentResponse:
    """Agent 響應"""
    type: ResponseType
    content: str
    conversation_id: str
    options: Optional[List[Dict]] = None  # 用於澄清
    report: Optional[Dict] = None         # 報告數據
    charts: Optional[List[Dict]] = None   # 圖表數據
    state: Optional[AgentState] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "type": self.type.value,
            "content": self.content,
            "conversation_id": self.conversation_id,
        }
        if self.options:
            result["options"] = self.options
        if self.report:
            result["report"] = self.report
        if self.charts:
            result["charts"] = self.charts
        return result


class AgentService:
    """
    AI Agent 主服務
    
    協調整個對話流程：
    1. 接收用戶訊息
    2. 識別意圖
    3. 提取/更新槽位
    4. 檢查完整性 → 生成澄清問題 或 執行工具
    5. 生成報告
    """
    
    def __init__(
        self,
        db: AsyncSession,
        ai_service=None
    ):
        self.db = db
        self.ai_service = ai_service
        self.intent_classifier = IntentClassifier(ai_service)
        self.slot_manager = SlotManager()
        self.tool_executor = ToolExecutor(db)
        self.report_generator = ReportGenerator(ai_service)

        self._states: Dict[str, AgentState] = {}
    
    async def process_message(
        self,
        message: str,
        conversation_id: str = None
    ) -> AsyncGenerator[AgentResponse, None]:
        """
        處理用戶訊息（串流響應）
        
        Args:
            message: 用戶訊息
            conversation_id: 對話 ID
        
        Yields:
            AgentResponse: 響應
        """
        # 獲取或創建狀態
        if conversation_id and conversation_id in self._states:
            state = self._states[conversation_id]
        else:
            conversation_id = conversation_id or str(uuid.uuid4())
            state = AgentState(
                conversation_id=conversation_id,
                messages=[],
                slots=AnalysisSlots()
            )
            self._states[conversation_id] = state
        
        # 添加用戶訊息
        state.messages.append(AgentMessage(role="user", content=message))
        
        # Step 1: 思考中
        yield AgentResponse(
            type=ResponseType.THINKING,
            content="分析緊你嘅問題...",
            conversation_id=conversation_id,
            state=state
        )
        
        # Step 2: 意圖識別
        intent_result = await self.intent_classifier.classify(
            message=message,
            context=[{"role": m.role, "content": m.content} for m in state.messages[-5:]],
            use_ai=self.ai_service is not None
        )
        state.current_intent = intent_result.intent
        
        # 處理特殊意圖
        if intent_result.intent == IntentType.GREETING:
            yield AgentResponse(
                type=ResponseType.MESSAGE,
                content=self._get_greeting_response(),
                conversation_id=conversation_id,
                state=state
            )
            return
        
        if intent_result.intent == IntentType.HELP:
            yield AgentResponse(
                type=ResponseType.MESSAGE,
                content=self._get_help_response(),
                conversation_id=conversation_id,
                state=state
            )
            return
        
        if intent_result.intent == IntentType.UNKNOWN:
            yield AgentResponse(
                type=ResponseType.MESSAGE,
                content="唔好意思，我唔太明你嘅意思。你可以試下話俾我知你想分析啲咩產品？例如「我想睇和牛嘅資料」。",
                conversation_id=conversation_id,
                state=state
            )
            return

        # 處理工作流相關意圖
        if intent_result.intent in [
            IntentType.CREATE_APPROVAL_TASK,
            IntentType.CONFIRM_ACTION,
            IntentType.DECLINE_ACTION
        ]:
            async for response in self._handle_workflow_intent(
                intent_result=intent_result,
                message=message,
                state=state,
                conversation_id=conversation_id
            ):
                yield response
            return
        
        # Step 3: 槽位提取
        yield AgentResponse(
            type=ResponseType.THINKING,
            content="提取緊查詢條件...",
            conversation_id=conversation_id,
            state=state
        )
        
        extracted_slots = self.slot_manager.extract_slots(
            message=message,
            entities=intent_result.entities
        )
        state.slots = self.slot_manager.merge_slots(state.slots, extracted_slots)
        
        # Step 4: 檢查完整性
        completeness = self.slot_manager.check_completeness(state.slots)
        
        if not completeness.is_complete:
            # 需要澄清
            clarification = self.slot_manager.generate_clarification_message(
                completeness.clarification_needed
            )
            state.pending_clarifications = completeness.clarification_needed
            
            yield AgentResponse(
                type=ResponseType.CLARIFICATION,
                content=clarification["message"],
                conversation_id=conversation_id,
                options=clarification["options"],
                state=state
            )
            return
        
        # Step 5: 執行工具
        yield AgentResponse(
            type=ResponseType.THINKING,
            content="查詢緊數據...",
            conversation_id=conversation_id,
            state=state
        )

        tool_results = await self.tool_executor.execute(
            intent=state.current_intent,
            slots=state.slots
        )
        
        aggregated = self.tool_executor.aggregate_results(tool_results)
        
        yield AgentResponse(
            type=ResponseType.THINKING,
            content="生成緊報告...",
            conversation_id=conversation_id,
            state=state
        )
        
        report = await self.report_generator.generate(
            products=state.slots.products,
            tool_results=aggregated["data"],
            include_ai_insights=self.ai_service is not None
        )
        
        state.messages.append(AgentMessage(
            role="assistant",
            content=report.markdown,
            metadata={"type": "report"}
        ))
        
        yield AgentResponse(
            type=ResponseType.REPORT,
            content=report.markdown,
            conversation_id=conversation_id,
            report=report.to_dict(),
            charts=[c.__dict__ for c in report.charts],
            state=state
        )
    
    async def handle_clarification(
        self,
        conversation_id: str,
        selections: Dict[str, Any]
    ) -> AsyncGenerator[AgentResponse, None]:
        """
        處理用戶對澄清問題的回應
        
        Args:
            conversation_id: 對話 ID
            selections: 用戶選擇
        
        Yields:
            AgentResponse
        """
        state = self._states.get(conversation_id)
        if not state:
            yield AgentResponse(
                type=ResponseType.ERROR,
                content="找不到對話記錄，請重新開始。",
                conversation_id=conversation_id
            )
            return
        
        # 更新槽位
        for slot_name, value in selections.items():
            state.slots = self.slot_manager.update_slot(
                state.slots,
                slot_name,
                value
            )
        
        # 清除待處理的澄清
        state.pending_clarifications = []
        
        # 重新檢查完整性並執行
        completeness = self.slot_manager.check_completeness(state.slots)
        
        if not completeness.is_complete:
            # 還需要更多澄清
            clarification = self.slot_manager.generate_clarification_message(
                completeness.clarification_needed
            )
            
            yield AgentResponse(
                type=ResponseType.CLARIFICATION,
                content=clarification["message"],
                conversation_id=conversation_id,
                options=clarification["options"],
                state=state
            )
            return
        
        # 執行工具和生成報告
        yield AgentResponse(
            type=ResponseType.THINKING,
            content="查詢緊數據...",
            conversation_id=conversation_id,
            state=state
        )
        
        tool_results = await self.tool_executor.execute(
            intent=state.current_intent,
            slots=state.slots
        )
        
        aggregated = self.tool_executor.aggregate_results(tool_results)
        
        yield AgentResponse(
            type=ResponseType.THINKING,
            content="生成緊報告...",
            conversation_id=conversation_id,
            state=state
        )
        
        report = await self.report_generator.generate(
            products=state.slots.products,
            tool_results=aggregated["data"],
            include_ai_insights=self.ai_service is not None
        )
        
        yield AgentResponse(
            type=ResponseType.REPORT,
            content=report.markdown,
            conversation_id=conversation_id,
            report=report.to_dict(),
            charts=[c.__dict__ for c in report.charts],
            state=state
        )
    
    def get_state(self, conversation_id: str) -> Optional[AgentState]:
        """獲取對話狀態"""
        return self._states.get(conversation_id)

    def _get_greeting_response(self) -> str:
        """問候回應"""
        return """你好！我係 AI 分析助手 🤖

我可以幫你分析 HKTVmall 嘅產品數據，例如：
- 📊 產品價格概覽
- 📈 價格趨勢分析
- ⚔️ 競爭對手比較
- 🏆 熱門產品排行

試下話俾我知你想分析啲咩？例如：
• 「我想睇 A5 和牛同海膽嘅資料」
• 「分析三文魚嘅價格趨勢」
• 「同百佳比較吓日本零食」"""
    
    def _get_help_response(self) -> str:
        """幫助回應"""
        return """## 我可以幫你做啲咩？

### 📊 產品分析
- 「分析和牛嘅價格」
- 「我想睇三文魚同海膽嘅資料」

### 📈 趨勢追蹤
- 「過去 30 日和牛價格趨勢」
- 「呢個月有咩產品減價？」

### ⚔️ 競爭對手比較
- 「同百佳比較日本零食價格」
- 「邊個平台賣和牛最平？」

### 🏆 熱門產品
- 「邊款海膽最多人買？」
- 「評分最高嘅三文魚」

### 📝 生成報告
- 「幫我出份和牛市場報告」

### 💰 改價審批
- 「幫我創建改價任務」
- 「建議改呢個產品嘅價」

---
直接打字問我就得喇！"""

    async def _handle_workflow_intent(
        self,
        intent_result: IntentResult,
        message: str,
        state: AgentState,
        conversation_id: str
    ) -> AsyncGenerator[AgentResponse, None]:
        """
        處理工作流相關意圖

        包括：創建審批任務、確認/拒絕動作
        """
        from .tools import SuggestPriceChangeTool, CreateApprovalTaskTool

        # 處理確認/拒絕動作
        if intent_result.intent == IntentType.CONFIRM_ACTION:
            # 檢查是否有待確認的動作
            pending_action = state.metadata.get("pending_workflow_action") if hasattr(state, 'metadata') else None

            if pending_action and pending_action.get("type") == "create_approval":
                # 執行創建審批任務
                yield AgentResponse(
                    type=ResponseType.THINKING,
                    content="創建緊改價提案...",
                    conversation_id=conversation_id,
                    state=state
                )

                tool = CreateApprovalTaskTool(self.db)
                result = await tool.execute(
                    product_id=pending_action.get("product_id"),
                    proposed_price=pending_action.get("proposed_price"),
                    reason=pending_action.get("reason"),
                    conversation_id=conversation_id,
                    send_notification=True
                )

                if result.success:
                    data = result.data
                    response_text = f"""✅ 改價提案已創建！

📦 **產品**: {data.get('product_name', '未知')} ({data.get('product_sku', '')})
💰 **現價**: HK${data.get('current_price', 0):.2f}
💵 **建議價**: HK${data.get('proposed_price', 0):.2f}
📝 **提案 ID**: {data.get('proposal_id', '')[:8]}...

{'📱 已發送 Telegram 通知' if data.get('notification_sent') else ''}

你可以喺 [改價審批頁面](/pricing-approval) 查看同審批呢個提案。"""
                else:
                    response_text = f"❌ 創建提案失敗: {result.error}"

                # 清除待確認動作
                if hasattr(state, 'metadata'):
                    state.metadata.pop("pending_workflow_action", None)

                state.messages.append(AgentMessage(
                    role="assistant",
                    content=response_text,
                    metadata={"type": "workflow_result"}
                ))

                yield AgentResponse(
                    type=ResponseType.MESSAGE,
                    content=response_text,
                    conversation_id=conversation_id,
                    state=state
                )
                return

            # 沒有待確認動作
            yield AgentResponse(
                type=ResponseType.MESSAGE,
                content="冇嘢需要確認喎。你想做咩？",
                conversation_id=conversation_id,
                state=state
            )
            return

        if intent_result.intent == IntentType.DECLINE_ACTION:
            # 清除待確認動作
            if hasattr(state, 'metadata'):
                state.metadata.pop("pending_workflow_action", None)

            yield AgentResponse(
                type=ResponseType.MESSAGE,
                content="好嘅，已取消。仲有咩可以幫到你？",
                conversation_id=conversation_id,
                state=state
            )
            return

        # 處理創建審批任務意圖
        if intent_result.intent == IntentType.CREATE_APPROVAL_TASK:
            # 需要先識別產品
            if not intent_result.entities:
                yield AgentResponse(
                    type=ResponseType.MESSAGE,
                    content="你想幫邊個產品創建改價任務？請話俾我知產品名或者 SKU。",
                    conversation_id=conversation_id,
                    state=state
                )
                return

            # 嘗試查找產品
            yield AgentResponse(
                type=ResponseType.THINKING,
                content="搵緊產品...",
                conversation_id=conversation_id,
                state=state
            )

            from sqlalchemy import select, or_
            from app.models.product import Product

            product_name = intent_result.entities[0]
            query = select(Product).where(
                or_(
                    Product.name.ilike(f"%{product_name}%"),
                    Product.sku.ilike(f"%{product_name}%")
                )
            ).limit(1)

            result = await self.db.execute(query)
            product = result.scalar_one_or_none()

            if not product:
                yield AgentResponse(
                    type=ResponseType.MESSAGE,
                    content=f"搵唔到「{product_name}」呢個產品。請確認產品名稱或者 SKU 係唔係正確。",
                    conversation_id=conversation_id,
                    state=state
                )
                return

            # 獲取價格建議
            yield AgentResponse(
                type=ResponseType.THINKING,
                content="分析緊競品價格...",
                conversation_id=conversation_id,
                state=state
            )

            suggest_tool = SuggestPriceChangeTool(self.db)
            suggestion_result = await suggest_tool.execute(product_id=str(product.id))

            if not suggestion_result.success:
                yield AgentResponse(
                    type=ResponseType.MESSAGE,
                    content=f"分析價格時出錯: {suggestion_result.error}",
                    conversation_id=conversation_id,
                    state=state
                )
                return

            suggestion = suggestion_result.data

            # 如果有建議價格，詢問確認
            if suggestion.get("suggested_price"):
                # 儲存待確認動作
                if not hasattr(state, 'metadata'):
                    state.metadata = {}
                state.metadata["pending_workflow_action"] = {
                    "type": "create_approval",
                    "product_id": str(product.id),
                    "proposed_price": suggestion["suggested_price"],
                    "reason": suggestion.get("reason", "")
                }

                competitors_text = ""
                if suggestion.get("competitors"):
                    competitors_text = "\n**競品價格**:\n"
                    for comp in suggestion["competitors"][:3]:
                        competitors_text += f"• {comp['name']} ({comp['platform']}): HK${comp['price']:.2f}\n"

                response_text = f"""📊 **價格分析結果**

📦 **產品**: {suggestion['product_name']} ({suggestion['product_sku']})
💰 **現價**: HK${suggestion['current_price']:.2f}
💵 **建議價**: HK${suggestion['suggested_price']:.2f}
📈 **建議**: {suggestion['recommendation']}
{competitors_text}
📝 **原因**:
{suggestion.get('reason', '')}

---
要幫你創建改價提案嗎？（回覆「好」確認，「唔好」取消）"""

                state.messages.append(AgentMessage(
                    role="assistant",
                    content=response_text,
                    metadata={"type": "workflow_suggestion"}
                ))

                yield AgentResponse(
                    type=ResponseType.MESSAGE,
                    content=response_text,
                    conversation_id=conversation_id,
                    state=state
                )
            else:
                # 沒有建議價格
                response_text = f"""📊 **價格分析結果**

📦 **產品**: {suggestion['product_name']} ({suggestion['product_sku']})
💰 **現價**: HK${suggestion['current_price']:.2f if suggestion['current_price'] else 0}
📈 **建議**: {suggestion.get('recommendation', '暫無建議')}

{suggestion.get('reason', '')}"""

                yield AgentResponse(
                    type=ResponseType.MESSAGE,
                    content=response_text,
                    conversation_id=conversation_id,
                    state=state
                )
