# =============================================
# Agent 基類
# =============================================
# 用途：所有 Agent 的公共行為（啟停、日誌、通知、DB 存取）
# 設計：AOP 風格 handler wrapping — 自動處理 enable/disable + 日誌
# =============================================

import logging
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from html import escape as html_escape
from typing import Any

from app.agents.events import Event, EventBus, EventHandler, Events
from app.models.database import async_session_maker, utcnow
from app.models.system import SystemSetting
from app.services.telegram import get_telegram_notifier


class AgentBase(ABC):
    """
    Agent 基類

    子類需實現：
    - name: Agent 名稱（如 "scout"）
    - description: Agent 描述
    - register_handlers(): 返回 {event_type: handler} 映射
    """

    def __init__(self, event_bus: EventBus) -> None:
        self._event_bus = event_bus
        self._enabled: bool = True
        self._logger = logging.getLogger(f"agent.{self.name}")
        self._registered_handlers: dict[str, EventHandler] = {}

    # ==================== 子類必須實現 ====================

    @property
    @abstractmethod
    def name(self) -> str:
        """Agent 唯一標識"""

    @property
    @abstractmethod
    def description(self) -> str:
        """Agent 描述"""

    @abstractmethod
    def register_handlers(self) -> dict[str, Any]:
        """
        返回事件處理器映射

        Returns:
            {event_type: handler_coroutine} 字典
            例如: {"product.created": self.on_product_created}
        """

    # ==================== 生命週期 ====================

    async def startup(self) -> None:
        """啟動 Agent：載入啟用狀態 + 註冊 handlers"""
        await self._load_enabled_state()

        handlers = self.register_handlers()
        for event_type, handler in handlers.items():
            wrapped = self._wrap_handler(handler)
            self._registered_handlers[event_type] = wrapped
            self._event_bus.subscribe(event_type, wrapped)

        status = "啟用" if self._enabled else "停用"
        self._logger.info(
            f"Agent [{self.name}] 啟動完成 ({status}), "
            f"註冊 {len(handlers)} 個事件處理器"
        )

    async def shutdown(self) -> None:
        """關閉 Agent：取消所有事件訂閱"""
        for event_type, wrapped in self._registered_handlers.items():
            self._event_bus.unsubscribe(event_type, wrapped)
        self._registered_handlers.clear()
        self._logger.info(f"Agent [{self.name}] 關閉")

    # ==================== 啟用/停用 ====================

    @property
    def enabled(self) -> bool:
        return self._enabled

    async def set_enabled(self, value: bool) -> None:
        """設定啟用狀態（同步寫入 DB + 內存）"""
        self._enabled = value

        async with self.get_db_session() as session:
            setting = await session.get(SystemSetting, f"agent.{self.name}.enabled")
            if setting:
                setting.value = str(value).lower()
                setting.updated_at = utcnow()
            else:
                session.add(SystemSetting(
                    key=f"agent.{self.name}.enabled",
                    value=str(value).lower(),
                    description=f"Agent [{self.name}] 啟用狀態",
                ))

        self._logger.info(f"Agent [{self.name}] {'啟用' if value else '停用'}")

    async def _load_enabled_state(self) -> None:
        """從 DB 載入啟用狀態"""
        try:
            async with self.get_db_session() as session:
                setting = await session.get(
                    SystemSetting, f"agent.{self.name}.enabled"
                )
                if setting:
                    self._enabled = setting.value.lower() == "true"
                else:
                    session.add(SystemSetting(
                        key=f"agent.{self.name}.enabled",
                        value="true",
                        description=f"Agent [{self.name}] 啟用狀態",
                    ))
                    self._enabled = True
        except Exception as exc:
            self._logger.warning(f"載入啟用狀態失敗，預設啟用: {exc}")
            self._enabled = True

    # ==================== AOP Handler 包裝 ====================

    def _wrap_handler(self, handler: Any) -> EventHandler:
        """
        包裝 handler：自動處理啟用檢查 + 日誌 + 錯誤捕獲

        這是 Agent 系統的核心設計 — 每個 handler 自動獲得：
        1. 啟用/停用閘門
        2. 進入/退出日誌
        3. 異常捕獲（不上拋，由 EventBus 處理）
        """
        agent_name = self.name

        async def wrapped(event: Event) -> None:
            if not self._enabled:
                self._logger.debug(
                    f"[{agent_name}] 已停用，跳過 {event.type}"
                )
                return

            self._logger.info(f"[{agent_name}] 處理 {event.type} (id={event.id})")
            try:
                await handler(event)
                self._logger.info(f"[{agent_name}] 完成 {event.type}")
            except Exception as exc:
                self._logger.error(
                    f"[{agent_name}] 處理 {event.type} 失敗: {exc}",
                    exc_info=True,
                )
                raise  # 讓 EventBus 的 fail-silent 機制處理

        wrapped.__qualname__ = f"{self.name}.{handler.__name__}"
        return wrapped

    # ==================== 工具方法 ====================

    async def emit(self, event_type: str, payload: dict | None = None) -> None:
        """發射事件（自動填充 source）"""
        await self._event_bus.emit(event_type, payload, source=self.name)

    async def escalate_to_human(
        self,
        title: str,
        message: str,
        data: dict | None = None,
    ) -> None:
        """
        上報人類決策

        通過 Telegram 發送通知，並發射 escalation 事件
        所有輸入均進行 HTML 轉義，防止注入
        """
        notifier = get_telegram_notifier()
        text = f"<b>{html_escape(title)}</b>\n\n{html_escape(message)}"
        if data:
            detail = "\n".join(
                f"  {html_escape(str(k))}: {html_escape(str(v))}"
                for k, v in data.items()
            )
            text += f"\n\n<pre>{detail}</pre>"

        await notifier.send_message(text)
        await self.emit(Events.AGENT_ESCALATION, {
            "agent": self.name,
            "title": title,
            "data": data or {},
        })

    @asynccontextmanager
    async def get_db_session(self):
        """獲取 DB session（帶 commit/rollback 安全保護）"""
        async with async_session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    # ==================== 狀態查詢 ====================

    def to_dict(self) -> dict:
        """返回 Agent 狀態（Dashboard API 用）"""
        handlers = self.register_handlers()
        return {
            "name": self.name,
            "description": self.description,
            "enabled": self._enabled,
            "subscriptions": list(handlers.keys()),
        }
