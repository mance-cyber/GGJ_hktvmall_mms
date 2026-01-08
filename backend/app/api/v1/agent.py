# =============================================
# AI Agent API
# 對話式數據分析接口
# =============================================

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
import json

from app.models.database import get_db
from app.services.agent import AgentService
from app.services.ai_service import AISettingsService, AIAnalysisService

router = APIRouter()


# =============================================
# Pydantic Schemas
# =============================================

class ChatMessage(BaseModel):
    """聊天訊息"""
    content: str = Field(..., description="用戶訊息內容")
    conversation_id: Optional[str] = Field(None, description="對話 ID（留空則創建新對話）")


class SlotSelection(BaseModel):
    """槽位選擇"""
    slot_name: str
    value: Any


class ClarificationResponse(BaseModel):
    """澄清回應"""
    conversation_id: str
    selections: Dict[str, Any] = Field(..., description="用戶選擇的槽位值")


class ChatResponse(BaseModel):
    """聊天響應"""
    type: str = Field(..., description="響應類型: thinking, message, clarification, report, error")
    content: str = Field(..., description="響應內容")
    conversation_id: str
    options: Optional[List[Dict]] = Field(None, description="澄清選項")
    report: Optional[Dict] = Field(None, description="報告數據")
    charts: Optional[List[Dict]] = Field(None, description="圖表數據")


class ConversationState(BaseModel):
    """對話狀態"""
    conversation_id: str
    messages: List[Dict]
    slots: Dict
    current_intent: Optional[str]


# =============================================
# Helper Functions
# =============================================

async def get_agent_service(db: AsyncSession) -> AgentService:
    """獲取 Agent 服務實例"""
    # 獲取 AI 配置
    config = await AISettingsService.get_config(db)
    
    # 如果有 API Key，創建 AI 服務
    ai_service = None
    if config.api_key:
        ai_service = AIAnalysisService(config)
    
    return AgentService(db=db, ai_service=ai_service)


# =============================================
# REST API
# =============================================

@router.post("/chat", response_model=ChatResponse)
async def chat(
    message: ChatMessage,
    db: AsyncSession = Depends(get_db)
):
    """
    發送聊天訊息
    
    這是主要的對話接口。發送用戶訊息，獲取 AI Agent 的響應。
    響應可能是：
    - 普通訊息（message）
    - 澄清問題（clarification）- 需要用戶選擇選項
    - 分析報告（report）- 包含 Markdown 報告和圖表數據
    """
    agent = await get_agent_service(db)
    
    # 收集所有響應（非串流模式）
    final_response = None
    async for response in agent.process_message(
        message=message.content,
        conversation_id=message.conversation_id
    ):
        # 跳過 thinking 響應
        if response.type.value != "thinking":
            final_response = response
    
    if not final_response:
        raise HTTPException(status_code=500, detail="無法處理訊息")
    
    return ChatResponse(
        type=final_response.type.value,
        content=final_response.content,
        conversation_id=final_response.conversation_id,
        options=final_response.options,
        report=final_response.report,
        charts=final_response.charts
    )


@router.post("/clarify", response_model=ChatResponse)
async def clarify(
    response: ClarificationResponse,
    db: AsyncSession = Depends(get_db)
):
    """
    處理澄清問題的回應
    
    當 AI 返回 clarification 類型時，用戶需要選擇選項。
    使用此接口提交選擇，繼續對話流程。
    """
    agent = await get_agent_service(db)
    
    final_response = None
    async for resp in agent.handle_clarification(
        conversation_id=response.conversation_id,
        selections=response.selections
    ):
        if resp.type.value != "thinking":
            final_response = resp
    
    if not final_response:
        raise HTTPException(status_code=500, detail="無法處理回應")
    
    return ChatResponse(
        type=final_response.type.value,
        content=final_response.content,
        conversation_id=final_response.conversation_id,
        options=final_response.options,
        report=final_response.report,
        charts=final_response.charts
    )


@router.get("/conversations")
async def get_conversations(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """獲取對話歷史列表"""
    agent = await get_agent_service(db)
    conversations = await agent.get_conversations(limit, offset)
    return {"conversations": conversations}


@router.get("/conversation/{conversation_id}", response_model=ConversationState)
async def get_conversation(
    conversation_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    獲取對話狀態
    
    返回對話的完整狀態，包括歷史訊息和槽位。
    """
    agent = await get_agent_service(db)
    # 使用新的異步方法
    if hasattr(agent, 'get_state_async'):
        state = await agent.get_state_async(conversation_id)
    else:
        state = agent.get_state(conversation_id)
    
    if not state:
        raise HTTPException(status_code=404, detail="對話不存在")
    
    return ConversationState(
        conversation_id=state.conversation_id,
        messages=[
            {
                "role": m.role,
                "content": m.content,
                "timestamp": m.timestamp.isoformat()
            }
            for m in state.messages
        ],
        slots=state.slots.to_dict(),
        current_intent=state.current_intent.value if state.current_intent else None
    )


# =============================================
# WebSocket API（串流模式）
# =============================================

@router.websocket("/ws/{conversation_id}")
async def websocket_chat(
    websocket: WebSocket,
    conversation_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    WebSocket 聊天接口（串流模式）
    """
    await websocket.accept()
    
    agent = await get_agent_service(db)
    
    try:
        while True:
            # 接收消息
            data = await websocket.receive_json()
            msg_type = data.get("type", "message")
            
            if msg_type == "message":
                # 處理用戶訊息
                content = data.get("content", "")
                
                async for response in agent.process_message(
                    message=content,
                    conversation_id=conversation_id
                ):
                    await websocket.send_json(response.to_dict())
            
            elif msg_type == "clarify":
                # 處理澄清回應
                selections = data.get("selections", {})
                
                async for response in agent.handle_clarification(
                    conversation_id=conversation_id,
                    selections=selections
                ):
                    await websocket.send_json(response.to_dict())
            
            elif msg_type == "ping":
                # 心跳
                await websocket.send_json({"type": "pong"})
    
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "content": f"發生錯誤: {str(e)}"
        })


# =============================================
# 輔助接口
# =============================================

@router.get("/suggestions")
async def get_suggestions():
    """
    獲取查詢建議
    
    返回一些常用的查詢示例，幫助用戶快速開始。
    """
    return {
        "suggestions": [
            {
                "text": "分析 A5 和牛嘅價格趨勢",
                "category": "趨勢分析"
            },
            {
                "text": "比較我哋同百佳嘅海鮮價格",
                "category": "競爭對手"
            },
            {
                "text": "邊啲日本零食最受歡迎？",
                "category": "熱門產品"
            },
            {
                "text": "幫我出份和牛同海膽嘅市場報告",
                "category": "報告生成"
            },
            {
                "text": "三文魚刺身最近有冇減價？",
                "category": "價格追蹤"
            }
        ]
    }


@router.get("/product-categories")
async def get_product_categories():
    """
    獲取可查詢的產品類別
    
    返回系統支持的產品類別列表，用於前端展示。
    """
    from app.services.agent.taxonomy import PRODUCT_TAXONOMY
    
    categories = []
    for name, info in PRODUCT_TAXONOMY.items():
        categories.append({
            "name": name,
            "aliases": info.get("aliases", []),
            "has_parts": "parts" in info,
            "has_types": "types" in info,
            "example_query": f"分析{name}嘅價格"
        })
    
    return {"categories": categories}
