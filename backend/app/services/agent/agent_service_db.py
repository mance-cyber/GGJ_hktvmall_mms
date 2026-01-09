# =============================================
# AI Agent 主服務 (數據庫持久化版)
# =============================================

from typing import Any, Dict, List, Optional, AsyncGenerator
from dataclasses import dataclass, field
from enum import Enum
import uuid
from datetime import datetime

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.agent_db import AgentConversation, AgentMessage as DBAgentMessage

from .intent_classifier import IntentClassifier, IntentType, IntentResult
from .slot_manager import SlotManager, AnalysisSlots, SlotStatus, SlotCompleteness
from .tool_executor import ToolExecutor
from .report_generator import ReportGenerator, Report
from .mock_data import is_mock_mode_enabled, MockResponseGenerator
from .persona import (
    RESPONSE_TEMPLATES,
    format_order_stats,
    format_finance_summary,
    format_alert_summary,
    get_greeting,
    get_thinking,
    get_success,
    get_error,
    get_follow_up_suggestions,
)


class ResponseType(Enum):
    """響應類型"""
    THINKING = "thinking"
    MESSAGE = "message"
    CLARIFICATION = "clarification"
    REPORT = "report"
    ERROR = "error"


# =============================================
# 意圖分類配置
# =============================================

# 直接執行的意圖（不需要產品槽位）
DIRECT_ACTION_INTENTS = {
    IntentType.ORDER_STATS,
    IntentType.ORDER_SEARCH,
    IntentType.FINANCE_SUMMARY,
    IntentType.SETTLEMENT_QUERY,
    IntentType.ALERT_QUERY,
    IntentType.ALERT_ACTION,
    IntentType.SEND_NOTIFICATION,
    IntentType.ADD_COMPETITOR,
    IntentType.ADD_PRODUCT,
    IntentType.NAVIGATE,
    IntentType.INVENTORY_QUERY,
    IntentType.FINANCE_ANALYSIS,
    IntentType.ORDER_QUERY,
}

# 需要產品槽位的意圖
PRODUCT_REQUIRED_INTENTS = {
    IntentType.PRODUCT_SEARCH,
    IntentType.PRODUCT_DETAIL,
    IntentType.PRICE_ANALYSIS,
    IntentType.TREND_ANALYSIS,
    IntentType.COMPETITOR_ANALYSIS,
    IntentType.BRAND_ANALYSIS,
    IntentType.MARKET_OVERVIEW,
    IntentType.GENERATE_REPORT,
    IntentType.MARKETING_STRATEGY,
}


@dataclass
class AgentMessage:
    """對話訊息"""
    role: str
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
        }


@dataclass
class AgentResponse:
    """Agent 響應"""
    type: ResponseType
    content: str
    conversation_id: str
    options: Optional[List[Dict]] = None
    report: Optional[Dict] = None
    charts: Optional[List[Dict]] = None
    suggestions: Optional[List[Dict]] = None  # 後續建議按鈕
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
        if self.suggestions:
            result["suggestions"] = self.suggestions
        return result


class AgentService:
    """
    AI Agent 主服務 (DB Persistence)
    """
    
    def __init__(self, db: AsyncSession, ai_service=None):
        self.db = db
        self.ai_service = ai_service
        self.intent_classifier = IntentClassifier(ai_service)
        self.slot_manager = SlotManager()
        self.tool_executor = ToolExecutor(db)
        self.report_generator = ReportGenerator(ai_service)
        self.mock_mode = is_mock_mode_enabled()
        self.mock_generator = MockResponseGenerator() if self.mock_mode else None

    async def get_conversations(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """獲取對話列表"""
        query = select(AgentConversation).order_by(desc(AgentConversation.updated_at)).limit(limit).offset(offset)
        result = await self.db.execute(query)
        conversations = result.scalars().all()
        
        return [
            {
                "id": str(c.id),
                "title": c.title or c.created_at.strftime("%Y-%m-%d %H:%M"),
                "created_at": c.created_at.isoformat(),
                "updated_at": c.updated_at.isoformat()
            }
            for c in conversations
        ]
    
    def get_state(self, conversation_id: str) -> Optional[AgentState]:
        """
        同步方法獲取狀態 (保留兼容性，但實際使用 DB 應使用異步 load_state)
        注意：此方法在 DB 模式下可能無法工作，因為需要異步 IO。
        API 層應該改為調用異步方法。
        """
        # 由於這個方法被設計為同步，且依賴內存緩存，
        # 在 DB 模式下我們可能需要拋出異常或重構 API 調用者。
        # 暫時返回 None 強制調用者處理
        return None

    async def get_state_async(self, conversation_id: str) -> Optional[AgentState]:
        """異步獲取狀態"""
        try:
            uuid_obj = uuid.UUID(conversation_id)
            query = select(AgentConversation).where(AgentConversation.id == uuid_obj)
            result = await self.db.execute(query)
            conv = result.scalar_one_or_none()
            if not conv:
                return None
            return await self._load_state(conv)
        except ValueError:
            return None

    async def _get_or_create_conversation(self, conversation_id: Optional[str]) -> AgentConversation:
        if conversation_id:
            try:
                uuid_obj = uuid.UUID(conversation_id)
                query = select(AgentConversation).where(AgentConversation.id == uuid_obj)
                result = await self.db.execute(query)
                conv = result.scalar_one_or_none()
                if conv:
                    return conv
            except (ValueError, TypeError):
                pass
        
        # 創建新對話
        conv = AgentConversation(
            title=datetime.now().strftime("%Y-%m-%d %H:%M")
        )
        self.db.add(conv)
        await self.db.commit()
        await self.db.refresh(conv)
        return conv

    async def _load_state(self, conv: AgentConversation) -> AgentState:
        # 加載消息
        query = select(DBAgentMessage).where(DBAgentMessage.conversation_id == conv.id).order_by(DBAgentMessage.created_at)
        result = await self.db.execute(query)
        db_messages = result.scalars().all()
        
        messages = [
            AgentMessage(
                role=m.role,
                content=m.content,
                timestamp=m.created_at,
                metadata=m.meta_data or {}
            )
            for m in db_messages
        ]
        
        # 恢復 Slots
        slots = AnalysisSlots()
        if conv.slots:
            # 簡單恢復 (假設 slots 結構匹配)
            slots_dict = conv.slots
            if "products" in slots_dict: slots.products = slots_dict["products"]
            if "analysis_dimensions" in slots_dict: slots.analysis_dimensions = slots_dict["analysis_dimensions"]
            if "time_range" in slots_dict: slots.time_range = slots_dict["time_range"]
            if "competitors" in slots_dict: slots.competitors = slots_dict["competitors"]
            # 注意：product_details 是複雜對象，這裡簡化處理可能丟失細節，需要完善 SlotManager 的反序列化

        return AgentState(
            conversation_id=str(conv.id),
            messages=messages,
            slots=slots,
            current_intent=IntentType(conv.current_intent) if conv.current_intent else None,
            created_at=conv.created_at
        )

    async def _save_message(self, conversation_id: str, role: str, content: str, type: str = "message", metadata: Dict = None):
        msg = DBAgentMessage(
            conversation_id=uuid.UUID(conversation_id),
            role=role,
            content=content,
            type=type,
            meta_data=metadata or {}
        )
        self.db.add(msg)
        await self.db.commit()

    async def _update_conversation_state(self, conversation_id: str, slots: AnalysisSlots, intent: Optional[IntentType]):
        query = select(AgentConversation).where(AgentConversation.id == uuid.UUID(conversation_id))
        result = await self.db.execute(query)
        conv = result.scalar_one_or_none()
        if conv:
            conv.slots = slots.to_dict()
            conv.current_intent = intent.value if intent else None
            await self.db.commit()

    async def process_message(self, message: str, conversation_id: str = None) -> AsyncGenerator[AgentResponse, None]:
        conv = await self._get_or_create_conversation(conversation_id)
        conversation_id = str(conv.id)
        
        state = await self._load_state(conv)
        
        state.messages.append(AgentMessage(role="user", content=message))
        await self._save_message(conversation_id, "user", message)
        
        if not conv.title or conv.title == conv.created_at.strftime("%Y-%m-%d %H:%M"):
            conv.title = message[:50] + ("..." if len(message) > 50 else "")
            await self.db.commit()
        
        yield AgentResponse(
            type=ResponseType.THINKING,
            content=get_thinking(),
            conversation_id=conversation_id,
            state=state
        )
        
        intent_result = await self.intent_classifier.classify(
            message=message,
            context=[{"role": m.role, "content": m.content} for m in state.messages[-5:]],
            use_ai=self.ai_service is not None
        )
        state.current_intent = intent_result.intent
        
        if intent_result.intent == IntentType.GREETING:
            response_content = self._get_greeting_response()
            await self._save_message(conversation_id, "assistant", response_content, "message")
            # 問候後的建議
            greeting_suggestions = [
                {"text": "今日訂單點樣？", "icon": "📦"},
                {"text": "有咩警報？", "icon": "🔔"},
                {"text": "本月營收幾多？", "icon": "💰"},
                {"text": "分析和牛價格", "icon": "🥩"},
            ]
            yield AgentResponse(
                type=ResponseType.MESSAGE,
                content=response_content,
                conversation_id=conversation_id,
                suggestions=greeting_suggestions,
                state=state
            )
            return

        if intent_result.intent == IntentType.HELP:
            response_content = self._get_help_response()
            await self._save_message(conversation_id, "assistant", response_content, "message")
            # 幫助後的建議
            help_suggestions = [
                {"text": "睇今日訂單", "icon": "📦"},
                {"text": "查警報", "icon": "🚨"},
                {"text": "分析價格", "icon": "📊"},
                {"text": "比較競爭對手", "icon": "⚔️"},
            ]
            yield AgentResponse(
                type=ResponseType.MESSAGE,
                content=response_content,
                conversation_id=conversation_id,
                suggestions=help_suggestions,
                state=state
            )
            return
        
        if intent_result.intent == IntentType.UNKNOWN:
            response_content = """唔好意思，我唔係好明你嘅意思 😅

不如試下咁問：
• 「今日訂單點樣？」
• 「本月賺幾多？」
• 「有咩警報？」
• 「分析和牛價格」

或者話我知你想做咩，我盡量幫你！"""
            await self._save_message(conversation_id, "assistant", response_content, "message")
            # 未知意圖的建議
            unknown_suggestions = [
                {"text": "今日訂單點樣？", "icon": "📦"},
                {"text": "本月賺幾多？", "icon": "💰"},
                {"text": "有咩警報？", "icon": "🔔"},
                {"text": "分析和牛價格", "icon": "🥩"},
            ]
            yield AgentResponse(
                type=ResponseType.MESSAGE,
                content=response_content,
                conversation_id=conversation_id,
                suggestions=unknown_suggestions,
                state=state
            )
            return

        # =============================================
        # 直接執行的意圖（不需要產品槽位）
        # =============================================
        if intent_result.intent in DIRECT_ACTION_INTENTS:
            yield AgentResponse(
                type=ResponseType.THINKING,
                content="查詢緊數據...",
                conversation_id=conversation_id,
                state=state
            )

            # 直接執行工具
            tool_results = await self.tool_executor.execute(
                intent=state.current_intent,
                slots=state.slots
            )

            aggregated = self.tool_executor.aggregate_results(tool_results)

            # 生成簡潔回覆
            response_content = self._format_direct_action_response(
                intent=state.current_intent,
                data=aggregated["data"],
                errors=aggregated["errors"]
            )

            await self._update_conversation_state(conversation_id, state.slots, state.current_intent)
            await self._save_message(conversation_id, "assistant", response_content, "message")

            # 獲取後續建議
            follow_up = get_follow_up_suggestions(
                intent_result.intent.value,
                {"products": state.slots.products}
            )

            yield AgentResponse(
                type=ResponseType.MESSAGE,
                content=response_content,
                conversation_id=conversation_id,
                suggestions=follow_up,
                state=state
            )
            return

        # =============================================
        # 需要產品槽位的意圖
        # =============================================
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

        # 只有需要產品的意圖才檢查完整性
        if intent_result.intent in PRODUCT_REQUIRED_INTENTS:
            # 只在真正缺少必要信息時才問
            if not state.slots.products:
                clarification = {
                    "message": "想分析邊啲產品呀？🤔\n\n例如：和牛、三文魚、海膽、日本零食...\n\n直接話我知就得！",
                    "options": []
                }
                await self._update_conversation_state(conversation_id, state.slots, state.current_intent)
                await self._save_message(
                    conversation_id, "assistant", clarification["message"],
                    "clarification", {"options": []}
                )
                yield AgentResponse(
                    type=ResponseType.CLARIFICATION,
                    content=clarification["message"],
                    conversation_id=conversation_id,
                    options=[],
                    state=state
                )
                return

        yield AgentResponse(
            type=ResponseType.THINKING,
            content="查詢緊數據...",
            conversation_id=conversation_id,
            state=state
        )
        
        if self.mock_mode and self.mock_generator:
            async for response in self._generate_mock_response(state, conversation_id):
                yield response
            return
        
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
        
        await self._update_conversation_state(conversation_id, state.slots, state.current_intent)
        await self._save_message(
            conversation_id, "assistant", report.markdown,
            "report", {"charts": [c.__dict__ for c in report.charts]}
        )

        # 報告後的建議
        report_suggestions = get_follow_up_suggestions(
            state.current_intent.value if state.current_intent else "default",
            {"products": state.slots.products}
        )

        yield AgentResponse(
            type=ResponseType.REPORT,
            content=report.markdown,
            conversation_id=conversation_id,
            report=report.to_dict(),
            charts=[c.__dict__ for c in report.charts],
            suggestions=report_suggestions,
            state=state
        )

    async def handle_clarification(
        self,
        conversation_id: str,
        selections: Dict[str, Any]
    ) -> AsyncGenerator[AgentResponse, None]:
        state = await self.get_state_async(conversation_id)
        if not state:
            yield AgentResponse(
                type=ResponseType.ERROR,
                content="找不到對話記錄，請重新開始。",
                conversation_id=conversation_id
            )
            return
        
        for slot_name, value in selections.items():
            state.slots = self.slot_manager.update_slot(
                state.slots,
                slot_name,
                value
            )
        
        state.pending_clarifications = []
        
        completeness = self.slot_manager.check_completeness(state.slots)
        
        if not completeness.is_complete:
            clarification = self.slot_manager.generate_clarification_message(
                completeness.clarification_needed
            )
            await self._update_conversation_state(conversation_id, state.slots, state.current_intent)
            await self._save_message(
                conversation_id, "assistant", clarification["message"], 
                "clarification", {"options": clarification["options"]}
            )
            yield AgentResponse(
                type=ResponseType.CLARIFICATION,
                content=clarification["message"],
                conversation_id=conversation_id,
                options=clarification["options"],
                state=state
            )
            return
        
        yield AgentResponse(
            type=ResponseType.THINKING,
            content="查詢緊數據...",
            conversation_id=conversation_id,
            state=state
        )
        
        if self.mock_mode and self.mock_generator:
            async for response in self._generate_mock_response(state, conversation_id):
                yield response
            return
        
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
        
        await self._update_conversation_state(conversation_id, state.slots, state.current_intent)
        await self._save_message(
            conversation_id, "assistant", report.markdown,
            "report", {"charts": [c.__dict__ for c in report.charts]}
        )
        
        yield AgentResponse(
            type=ResponseType.REPORT,
            content=report.markdown,
            conversation_id=conversation_id,
            report=report.to_dict(),
            charts=[c.__dict__ for c in report.charts],
            state=state
        )

    async def _generate_mock_response(
        self,
        state: AgentState,
        conversation_id: str
    ) -> AsyncGenerator[AgentResponse, None]:
        yield AgentResponse(
            type=ResponseType.THINKING,
            content="生成緊模擬報告...",
            conversation_id=conversation_id,
            state=state
        )
        
        mock_report = self.mock_generator.generate_mock_report(
            product_names=state.slots.products or ["和牛"],
            report_type="price_analysis"
        )
        
        await self._save_message(
            conversation_id, "assistant", mock_report["markdown"],
            "report", {"charts": mock_report["charts"], "is_mock": True}
        )
        
        yield AgentResponse(
            type=ResponseType.REPORT,
            content=mock_report["markdown"],
            conversation_id=conversation_id,
            report=mock_report,
            charts=mock_report["charts"],
            state=state
        )

    # =============================================
    # 對話管理方法
    # =============================================

    async def delete_conversation(self, conversation_id: str) -> bool:
        """刪除單個對話"""
        try:
            uuid_obj = uuid.UUID(conversation_id)
            query = select(AgentConversation).where(AgentConversation.id == uuid_obj)
            result = await self.db.execute(query)
            conv = result.scalar_one_or_none()

            if not conv:
                return False

            await self.db.delete(conv)
            await self.db.commit()
            return True
        except (ValueError, TypeError):
            return False

    async def delete_conversations(self, conversation_ids: List[str]) -> int:
        """批量刪除對話"""
        deleted_count = 0

        for cid in conversation_ids:
            try:
                uuid_obj = uuid.UUID(cid)
                query = select(AgentConversation).where(AgentConversation.id == uuid_obj)
                result = await self.db.execute(query)
                conv = result.scalar_one_or_none()

                if conv:
                    await self.db.delete(conv)
                    deleted_count += 1
            except (ValueError, TypeError):
                continue

        await self.db.commit()
        return deleted_count

    def _get_greeting_response(self) -> str:
        return get_greeting() + """

我可以幫你：
• 📦 查訂單、睇營收
• 🚨 Check 警報、處理緊急事項
• 📊 分析產品價格同趨勢
• ⚔️ 監察競爭對手動態
• 💡 俾你營運建議

直接話我知你想做咩，我即刻幫你搞掂！"""

    def _get_help_response(self) -> str:
        return """## Jap仔 可以幫你做啲咩？ 💪

### 📦 營運查詢
「今日有幾多單？」「本月營收點？」

### 🚨 警報管理
「有咩警報？」「邊啲要緊急處理？」

### 📊 產品分析
「和牛價格點？」「三文魚趨勢」

### ⚔️ 競爭監測
「百佳賣幾錢？」「同對手比較」

### 💡 快速操作
「加新競爭對手」「新增產品」

---
直接打字問我就得！唔使客氣 😄"""

    def _format_direct_action_response(
        self,
        intent: IntentType,
        data: dict,
        errors: list
    ) -> str:
        """
        格式化直接執行意圖的回覆（Jap仔 風格）
        """
        if errors:
            error_msgs = [e.get("error", "未知錯誤") for e in errors]
            return get_error() + f" 詳情：{', '.join(error_msgs)}"

        # 訂單統計
        if intent == IntentType.ORDER_STATS:
            stats = data.get("order_stats", {})
            if not stats:
                return get_error() + " 暫時攞唔到訂單數據，等陣再試吓？"
            return format_order_stats(stats)

        # 財務摘要
        if intent in [IntentType.FINANCE_SUMMARY, IntentType.FINANCE_ANALYSIS]:
            finance = data.get("finance_summary", {})
            if not finance:
                return get_error() + " 暫時攞唔到財務數據，等陣再試吓？"
            return format_finance_summary(finance)

        # 警報查詢
        if intent == IntentType.ALERT_QUERY:
            alerts = data.get("alert_query", {})
            if not alerts:
                return "✅ 冇警報！一切正常，可以放心～"
            return format_alert_summary(alerts)

        # 導航引導
        if intent == IntentType.NAVIGATE:
            guide = data.get("navigation_guide", {})
            msg = guide.get("message", "")
            return f"好！{msg}" if msg else "你想去邊個頁面？話我知～"

        # 新增競爭對手引導
        if intent == IntentType.ADD_COMPETITOR:
            guide = data.get("add_competitor_guide", {})
            msg = guide.get("message", "")
            return msg if msg else """想加競爭對手？Easy！

1. 去「競品監測」頁面
2. 撳右上角「新增」按鈕
3. 填返對手資料就搞掂！

[👉 直接去競品監測](/competitors)"""

        # 新增產品引導
        if intent == IntentType.ADD_PRODUCT:
            guide = data.get("add_product_guide", {})
            msg = guide.get("message", "")
            return msg if msg else """想加新產品？冇問題！

1. 去「商品庫」頁面
2. 撳「新增產品」
3. 填返產品資料就得！

[👉 直接去商品庫](/products)"""

        # 通知發送
        if intent == IntentType.SEND_NOTIFICATION:
            result = data.get("notification_send", {})
            if result.get("success"):
                return get_success() + " 通知已經發出去喇！📬"
            return get_error() + " 通知發唔到，等陣再試吓？"

        # 庫存查詢
        if intent == IntentType.INVENTORY_QUERY:
            inventory = data.get("query_top_products", {})
            if not inventory:
                return "暫時冇庫存數據，可能要同步吓先～"
            return f"庫存情況：{inventory}"

        # 默認回覆
        return get_success() + f" 搞掂！仲有咩要幫手？"
