# =============================================
# 事件匯流排 + 事件定義
# =============================================
# 用途：Agent 間通訊的核心管道
# 設計：進程內異步事件匯流排，fail-silent + error event 雙保險
# =============================================

import logging
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Coroutine

from app.models.database import utcnow

logger = logging.getLogger(__name__)

# 事件處理器類型
EventHandler = Callable[["Event"], Coroutine[Any, Any, None]]


# =============================================
# 事件數據結構
# =============================================

@dataclass(frozen=True, slots=True)
class Event:
    """不可變事件對象"""
    type: str
    payload: dict = field(default_factory=dict)
    source: str = ""
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    timestamp: datetime = field(default_factory=utcnow)


# =============================================
# 事件類型常量
# =============================================

class Events:
    """所有事件類型常量"""

    # 商品生命週期
    PRODUCT_CREATED = "product.created"
    PRODUCT_UPDATED = "product.updated"
    PRODUCT_DELETED = "product.deleted"

    # 抓取生命週期
    SCRAPE_STARTED = "scrape.started"
    SCRAPE_COMPLETED = "scrape.completed"
    SCRAPE_FAILED = "scrape.failed"

    # 價格告警
    PRICE_ALERT_CREATED = "price_alert.created"
    COMPETITOR_PRICE_DROP = "competitor.price_drop"
    COMPETITOR_STOCKOUT = "competitor.stockout"

    # 內容生命週期
    CONTENT_GENERATED = "content.generated"
    CONTENT_APPROVED = "content.approved"

    # 運營數據
    DAILY_DATA_READY = "daily_data.ready"
    ORDER_SYNCED = "order.synced"

    # Commander 排程觸發
    SCHEDULE_OPS_DAILY_SYNC = "schedule.ops.daily_sync"
    SCHEDULE_SCOUT_ANALYZE = "schedule.scout.analyze"
    SCHEDULE_PRICER_BATCH = "schedule.pricer.batch"
    SCHEDULE_STRATEGIST_BRIEFING = "schedule.strategist.briefing"

    # Agent 內部通訊
    AGENT_TASK_COMPLETED = "agent.task_completed"
    AGENT_ESCALATION = "agent.escalation"
    AGENT_ERROR = "agent.error"


# =============================================
# 事件匯流排
# =============================================

class EventBus:
    """
    輕量級進程內異步事件匯流排

    設計原則：
    - fail-silent：單個 handler 失敗不影響其他 handler
    - 失敗時自動發射 agent.error 事件（用於 Commander 監控）
    - 維護最近事件日誌（內存，重啟即清）
    """

    # 合法事件類型白名單（防止注入偽造事件）
    _VALID_EVENTS: set[str] = {
        v for k, v in vars(Events).items()
        if not k.startswith("_") and isinstance(v, str)
    }

    def __init__(self) -> None:
        self._handlers: dict[str, list[EventHandler]] = defaultdict(list)
        self._event_log: deque[Event] = deque(maxlen=200)

    # ==================== 訂閱 / 取消 ====================

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        """註冊事件處理器"""
        self._handlers[event_type].append(handler)
        logger.debug(f"EventBus: {handler.__qualname__} 訂閱 {event_type}")

    def unsubscribe(self, event_type: str, handler: EventHandler) -> None:
        """取消註冊"""
        handlers = self._handlers.get(event_type, [])
        if handler in handlers:
            handlers.remove(handler)
            logger.debug(f"EventBus: {handler.__qualname__} 取消訂閱 {event_type}")

    # ==================== 發射事件 ====================

    async def emit(
        self,
        event_type: str,
        payload: dict | None = None,
        *,
        source: str = "",
        _internal: bool = False,
    ) -> Event:
        """
        發射事件並通知所有訂閱者

        Args:
            event_type: 事件類型
            payload: 事件負載
            source: 發射來源（Agent 名稱）
            _internal: 內部標記，防止 error 事件遞歸
        """
        # 事件類型白名單校驗
        if event_type not in self._VALID_EVENTS:
            logger.warning(f"EventBus: 未知事件類型 {event_type}，已忽略")
            return Event(type=event_type, payload=payload or {}, source=source)

        event = Event(
            type=event_type,
            payload=payload or {},
            source=source,
        )

        # 記錄事件日誌（deque 自動淘汰舊事件）
        self._event_log.append(event)

        handlers = self._handlers.get(event_type, [])
        if not handlers:
            logger.debug(f"EventBus: {event_type} 無訂閱者")
            return event

        logger.info(f"EventBus: {event_type} -> {len(handlers)} handler(s)")

        for handler in handlers:
            try:
                await handler(event)
            except Exception as exc:
                logger.error(
                    f"EventBus: handler {handler.__qualname__} "
                    f"處理 {event_type} 失敗: {exc}",
                    exc_info=True,
                )
                # 發射 error 事件（防遞歸，截斷錯誤信息防洩露）
                if not _internal:
                    await self.emit(
                        Events.AGENT_ERROR,
                        payload={
                            "failed_event": event_type,
                            "handler": handler.__qualname__,
                            "error": str(exc)[:200],
                        },
                        source="event_bus",
                        _internal=True,
                    )

        return event

    # ==================== 查詢 ====================

    def get_recent_events(self, limit: int = 50) -> list[dict]:
        """獲取最近事件（Dashboard API 用）"""
        from itertools import islice
        return [
            {
                "id": e.id,
                "type": e.type,
                "source": e.source,
                "payload_keys": list(e.payload.keys()),
                "timestamp": e.timestamp.isoformat(),
            }
            for e in islice(reversed(self._event_log), limit)
        ]

    def get_handler_map(self) -> dict[str, list[str]]:
        """獲取事件 -> handler 名稱映射（Debug 用）"""
        return {
            event_type: [h.__qualname__ for h in handlers]
            for event_type, handlers in self._handlers.items()
            if handlers
        }
