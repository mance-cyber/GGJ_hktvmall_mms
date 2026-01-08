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


class ResponseType(Enum):
    """響應類型"""
    THINKING = "thinking"
    MESSAGE = "message"
    CLARIFICATION = "clarification"
    REPORT = "report"
    ERROR = "error"


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
            content="分析緊你嘅問題...",
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
            yield AgentResponse(
                type=ResponseType.MESSAGE,
                content=response_content,
                conversation_id=conversation_id,
                state=state
            )
            return
        
        if intent_result.intent == IntentType.HELP:
            response_content = self._get_help_response()
            await self._save_message(conversation_id, "assistant", response_content, "message")
            yield AgentResponse(
                type=ResponseType.MESSAGE,
                content=response_content,
                conversation_id=conversation_id,
                state=state
            )
            return
        
        if intent_result.intent == IntentType.UNKNOWN:
            response_content = "唔好意思，我唔太明你嘅意思。你可以試下話俾我知你想分析啲咩產品？例如「我想睇和牛嘅資料」。"
            await self._save_message(conversation_id, "assistant", response_content, "message")
            yield AgentResponse(
                type=ResponseType.MESSAGE,
                content=response_content,
                conversation_id=conversation_id,
                state=state
            )
            return
        
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
        
        completeness = self.slot_manager.check_completeness(state.slots)
        
        if not completeness.is_complete:
            clarification = self.slot_manager.generate_clarification_message(
                completeness.clarification_needed
            )
            state.pending_clarifications = completeness.clarification_needed
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

    def _get_greeting_response(self) -> str:
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

---
直接打字問我就得喇！"""
