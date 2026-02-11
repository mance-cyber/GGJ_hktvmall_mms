# =============================================
# Commander Agent（指揮官）
# =============================================
# 用途：Agent 團隊的中央神經系統
# 職責：排程協調、錯誤監控、人類上報閘門、靜默時段控制
# =============================================

import logging
from datetime import datetime, timezone, timedelta
from typing import Any

from app.agents.base import AgentBase
from app.agents.events import Event, EventBus, Events

# 香港時區 (UTC+8)
HK_TZ = timezone(timedelta(hours=8))


class CommanderAgent(AgentBase):
    """
    指揮官：協調所有 Agent 的中央節點

    核心能力：
    1. 監聽排程事件，觸發對應 Agent 動作
    2. 監控 agent.error 事件，累計錯誤後上報人類
    3. 靜默時段控制（23:00-08:00 不打擾賣家）
    """

    # 每日排程表（時間 → 事件列表）
    DAILY_SCHEDULE = {
        "08:00": [Events.SCHEDULE_OPS_DAILY_SYNC],
        "09:30": [Events.SCHEDULE_SCOUT_ANALYZE],
        "10:00": [Events.SCHEDULE_PRICER_BATCH],
        "11:00": [Events.SCHEDULE_STRATEGIST_BRIEFING],
    }

    # 靜默時段：不主動發送 Telegram 通知
    QUIET_HOURS = (23, 8)  # 23:00 ~ 08:00

    @property
    def name(self) -> str:
        return "commander"

    @property
    def description(self) -> str:
        return "指揮官：協調排程、錯誤監控、人類上報"

    def register_handlers(self) -> dict[str, Any]:
        return {
            Events.AGENT_ERROR: self._on_agent_error,
            Events.AGENT_ESCALATION: self._on_escalation,
            Events.AGENT_TASK_COMPLETED: self._on_task_completed,
        }

    # ==================== 事件處理 ====================

    async def _on_agent_error(self, event: Event) -> None:
        """Agent 錯誤監控：累計錯誤後上報"""
        failed_event = event.payload.get("failed_event", "unknown")
        handler = event.payload.get("handler", "unknown")
        error = event.payload.get("error", "")

        self._logger.warning(
            f"Agent 錯誤: {handler} 處理 {failed_event} 失敗 — {error}"
        )

        # Phase 2: 累計錯誤計數，達到閾值後上報人類
        # 目前僅記錄日誌

    async def _on_escalation(self, event: Event) -> None:
        """人類上報事件：記錄 + 確認"""
        agent = event.payload.get("agent", "unknown")
        title = event.payload.get("title", "")
        self._logger.info(f"人類上報: [{agent}] {title}")

    async def _on_task_completed(self, event: Event) -> None:
        """Agent 任務完成通知"""
        agent = event.payload.get("agent", "unknown")
        task = event.payload.get("task", "unknown")
        self._logger.info(f"任務完成: [{agent}] {task}")

    # ==================== 工具方法 ====================

    @staticmethod
    def is_quiet_hours() -> bool:
        """檢查是否在靜默時段（香港時間）"""
        hour = datetime.now(HK_TZ).hour
        quiet_start, quiet_end = CommanderAgent.QUIET_HOURS
        if quiet_start > quiet_end:
            # 跨午夜：23:00 ~ 08:00
            return hour >= quiet_start or hour < quiet_end
        return quiet_start <= hour < quiet_end

    def get_schedule(self) -> dict[str, list[str]]:
        """返回每日排程表（Dashboard API 用）"""
        return self.DAILY_SCHEDULE

    def to_dict(self) -> dict:
        """擴展狀態：加入排程和靜默狀態"""
        base = super().to_dict()
        base["schedule"] = self.DAILY_SCHEDULE
        base["is_quiet_hours"] = self.is_quiet_hours()
        return base
