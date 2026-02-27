# =============================================
# Agent 排程器
# =============================================
# 用途：按 Commander.DAILY_SCHEDULE 定時 emit 排程事件
# 設計：asyncio background task，FastAPI lifespan 啟停
# =============================================

import asyncio
import logging
from datetime import datetime, timezone, timedelta

from app.agents.events import EventBus

logger = logging.getLogger(__name__)

# 香港時區 (UTC+8)
HK_TZ = timezone(timedelta(hours=8))


class AgentScheduler:
    """
    輕量級排程器

    每分鐘檢查一次，到點就 emit 對應事件。
    用 set 記錄今日已觸發的時間點，避免重複。
    """

    def __init__(self, event_bus: EventBus) -> None:
        self._event_bus = event_bus
        self._task: asyncio.Task | None = None
        self._fired_today: set[str] = set()
        self._last_date: str = ""

    async def start(self) -> None:
        """啟動排程 loop"""
        self._task = asyncio.create_task(self._loop())
        logger.info("AgentScheduler 啟動")

    async def stop(self) -> None:
        """停止排程"""
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("AgentScheduler 停止")

    async def _loop(self) -> None:
        """主循環：每 30 秒檢查一次"""
        from app.agents.commander import CommanderAgent

        while True:
            try:
                now = datetime.now(HK_TZ)
                today = now.strftime("%Y-%m-%d")

                # 日期變更 -> 重置已觸發記錄
                if today != self._last_date:
                    self._fired_today.clear()
                    self._last_date = today

                current_time = now.strftime("%H:%M")

                for scheduled_time, events in CommanderAgent.DAILY_SCHEDULE.items():
                    if scheduled_time in self._fired_today:
                        continue

                    # 允許 2 分鐘誤差窗口
                    if self._within_window(current_time, scheduled_time, minutes=2):
                        for event_type in events:
                            logger.info(
                                f"排程觸發: {event_type} "
                                f"(scheduled={scheduled_time}, actual={current_time})"
                            )
                            await self._event_bus.emit(
                                event_type,
                                payload={"trigger": "scheduler", "scheduled_time": scheduled_time},
                                source="scheduler",
                            )
                        self._fired_today.add(scheduled_time)

            except asyncio.CancelledError:
                raise
            except Exception as exc:
                logger.error(f"排程器錯誤: {exc}", exc_info=True)

            await asyncio.sleep(30)

    @staticmethod
    def _within_window(current: str, target: str, minutes: int = 2) -> bool:
        """檢查 current 是否在 target 的 ±minutes 窗口內"""
        try:
            ch, cm = map(int, current.split(":"))
            th, tm = map(int, target.split(":"))
            current_mins = ch * 60 + cm
            target_mins = th * 60 + tm
            return 0 <= (current_mins - target_mins) < minutes
        except (ValueError, TypeError):
            return False


# 全局實例（在 startup 時初始化）
_scheduler: AgentScheduler | None = None


async def start_scheduler(event_bus: EventBus) -> None:
    """啟動全局排程器"""
    global _scheduler
    _scheduler = AgentScheduler(event_bus)
    await _scheduler.start()


async def stop_scheduler() -> None:
    """停止全局排程器"""
    global _scheduler
    if _scheduler:
        await _scheduler.stop()
        _scheduler = None
