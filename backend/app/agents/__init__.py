# =============================================
# Agent Team 初始化與生命週期管理
# =============================================
# 用途：Agent 註冊、啟動、關閉、狀態查詢
# 入口：startup_agents() / shutdown_agents() 在 main.py lifespan 中調用
# =============================================

import logging

from app.agents.events import EventBus
from app.agents.base import AgentBase
from app.agents.commander import CommanderAgent
from app.agents.scout import ScoutAgent
from app.agents.pricer import PricerAgent
from app.agents.writer import WriterAgent
from app.agents.ops import OpsAgent
from app.agents.strategist import StrategistAgent

logger = logging.getLogger(__name__)

# ==================== 全局單例 ====================

event_bus = EventBus()

_agents: dict[str, AgentBase] = {}


# ==================== 生命週期 ====================

async def startup_agents() -> None:
    """
    啟動所有 Agent

    在 FastAPI lifespan 中調用，init_db() 之後。
    每個 Agent 的 startup() 會：
    1. 從 DB 載入啟用狀態
    2. 註冊事件處理器到 EventBus
    """
    global _agents

    agent_classes = [
        CommanderAgent,
        ScoutAgent,
        PricerAgent,
        WriterAgent,
        OpsAgent,
        StrategistAgent,
    ]

    for cls in agent_classes:
        agent = cls(event_bus)
        try:
            await agent.startup()
            _agents[agent.name] = agent
        except Exception as exc:
            logger.error(f"Agent [{cls.__name__}] 啟動失敗: {exc}", exc_info=True)
            # 單個 Agent 啟動失敗不阻塞其他 Agent

    logger.info(
        f"Agent Team 啟動完成: {len(_agents)}/{len(agent_classes)} 個 Agent 就緒"
    )


async def shutdown_agents() -> None:
    """關閉所有 Agent"""
    for name, agent in _agents.items():
        try:
            await agent.shutdown()
        except Exception as exc:
            logger.error(f"Agent [{name}] 關閉失敗: {exc}")

    _agents.clear()
    logger.info("Agent Team 已關閉")


# ==================== 查詢接口 ====================

def get_agent(name: str) -> AgentBase | None:
    """獲取指定 Agent 實例"""
    return _agents.get(name)


def get_event_bus() -> EventBus:
    """獲取全局 EventBus 實例"""
    return event_bus


def get_team_status() -> dict:
    """
    獲取 Agent Team 整體狀態（Dashboard API 用）

    Returns:
        {
            "agents": [{name, description, enabled, subscriptions}, ...],
            "event_bus": {
                "handler_map": {event_type: [handler_names]},
                "recent_events": [{id, type, source, timestamp}, ...],
            },
        }
    """
    return {
        "agents": [agent.to_dict() for agent in _agents.values()],
        "event_bus": {
            "handler_map": event_bus.get_handler_map(),
            "recent_events": event_bus.get_recent_events(limit=20),
        },
    }
