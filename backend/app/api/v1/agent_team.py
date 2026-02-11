# =============================================
# Agent Team Dashboard API
# =============================================
# 用途：Agent 團隊狀態查詢、啟停控制
# 安全：所有端點需認證，寫操作需 agent:admin 權限
# =============================================

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query

from app.agents import get_agent, get_team_status, get_event_bus
from app.agents.events import Events
from app.api.deps import require_permissions

router = APIRouter()

# 合法 Agent 名稱
AgentName = Literal["commander", "scout", "pricer", "writer", "ops", "strategist"]

# 允許手動觸發的排程事件（不允許觸發業務事件如 product.created）
_MANUAL_EMITTABLE = {
    Events.SCHEDULE_OPS_DAILY_SYNC,
    Events.SCHEDULE_SCOUT_ANALYZE,
    Events.SCHEDULE_PRICER_BATCH,
    Events.SCHEDULE_STRATEGIST_BRIEFING,
}


# ==================== 團隊狀態 ====================

@router.get("/status")
async def team_status(
    _user=Depends(require_permissions("agent:read")),
):
    """獲取 Agent Team 整體狀態"""
    return get_team_status()


# ==================== 單個 Agent 控制 ====================

@router.post("/{agent_name}/enable")
async def enable_agent(
    agent_name: AgentName,
    _user=Depends(require_permissions("agent:admin")),
):
    """啟用指定 Agent"""
    agent = get_agent(agent_name)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")

    await agent.set_enabled(True)
    return {"agent": agent_name, "enabled": True}


@router.post("/{agent_name}/disable")
async def disable_agent(
    agent_name: AgentName,
    _user=Depends(require_permissions("agent:admin")),
):
    """停用指定 Agent"""
    agent = get_agent(agent_name)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")

    await agent.set_enabled(False)
    return {"agent": agent_name, "enabled": False}


# ==================== 手動觸發事件 ====================

@router.post("/emit/{event_type}")
async def emit_event(
    event_type: str,
    _user=Depends(require_permissions("agent:admin")),
):
    """手動觸發排程事件（僅限排程類事件）"""
    if event_type not in _MANUAL_EMITTABLE:
        raise HTTPException(
            status_code=400,
            detail=f"Event type not allowed for manual trigger. "
                   f"Allowed: {sorted(_MANUAL_EMITTABLE)}",
        )

    bus = get_event_bus()
    event = await bus.emit(event_type, {"source": "manual_trigger"})
    return {
        "event_id": event.id,
        "event_type": event.type,
        "status": "emitted",
    }


# ==================== 事件日誌 ====================

@router.get("/events")
async def recent_events(
    limit: int = Query(default=50, ge=1, le=200),
    _user=Depends(require_permissions("agent:read")),
):
    """獲取最近事件日誌"""
    bus = get_event_bus()
    return {"events": bus.get_recent_events(limit=limit)}
