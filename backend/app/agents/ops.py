# =============================================
# Ops Agent（運營官）
# =============================================
# 用途：數據同步 + 異常監控
# 封裝：OrderService
# =============================================

from typing import Any

from app.agents.base import AgentBase
from app.agents.events import Event, Events


class OpsAgent(AgentBase):
    """
    運營官：自動同步 HKTVmall 數據，監控運營狀態

    每日同步：訂單數據
    異常監控：訂單超時預警
    """

    LOW_STOCK_THRESHOLD = 5

    @property
    def name(self) -> str:
        return "ops"

    @property
    def description(self) -> str:
        return "運營官：數據同步、庫存監控、訂單追蹤"

    def register_handlers(self) -> dict[str, Any]:
        return {
            Events.SCHEDULE_OPS_DAILY_SYNC: self._on_daily_sync,
            # 自訂閱：_on_daily_sync 發射 ORDER_SYNCED 後觸發異常檢查
            # 注意：_on_order_synced 內 **禁止** 再次發射 ORDER_SYNCED，否則無限遞歸
            Events.ORDER_SYNCED: self._on_order_synced,
        }

    # ==================== 事件處理 ====================

    async def _on_daily_sync(self, event: Event) -> None:
        """Commander 排程：每日數據同步"""
        self._logger.info("排程觸發：每日數據同步")

        from app.services.order_service import OrderService

        synced_count = 0
        async with self.get_db_session() as session:
            try:
                order_svc = OrderService(session)
                synced_count = await order_svc.sync_orders(days=7)
                self._logger.info(f"訂單同步完成: {synced_count} 筆")
            except RuntimeError as exc:
                # HKTVmall API 未配置
                self._logger.warning(f"訂單同步跳過: {exc}")
                return
            except Exception as exc:
                self._logger.error(f"訂單同步失敗: {exc}")
                await self.escalate_to_human(
                    "訂單同步失敗",
                    "每日訂單數據同步出錯，請檢查 HKTVmall API 配置",
                    {"error": str(exc)[:200]},
                )
                return

        # 通知 Strategist 數據已就緒
        await self.emit(Events.DAILY_DATA_READY, {
            "source": self.name,
            "orders_synced": synced_count,
        })

        await self.emit(Events.ORDER_SYNCED, {
            "orders_count": synced_count,
        })

        await self.emit(Events.AGENT_TASK_COMPLETED, {
            "agent": self.name,
            "task": "daily_sync",
            "orders_synced": synced_count,
        })

    async def _on_order_synced(self, event: Event) -> None:
        """訂單同步完成 -> 檢查異常（超時未出貨）"""
        orders_count = event.payload.get("orders_count", 0)
        if orders_count == 0:
            return

        self._logger.info(f"訂單同步: {orders_count} 筆 -> 檢查異常")

        from datetime import timedelta
        from sqlalchemy import select, func
        from app.models.order import Order, OrderStatus
        from app.models.database import utcnow

        overdue_count = 0
        async with self.get_db_session() as session:
            cutoff = utcnow() - timedelta(hours=48)
            stmt = (
                select(func.count(Order.id))
                .where(
                    Order.status.in_([
                        OrderStatus.PENDING,
                        OrderStatus.CONFIRMED,
                        OrderStatus.PACKING,
                    ]),
                    Order.order_date < cutoff,
                )
            )
            result = await session.execute(stmt)
            overdue_count = result.scalar() or 0

        if overdue_count > 0:
            self._logger.warning(f"發現 {overdue_count} 筆超時未出貨訂單")
            await self.escalate_to_human(
                "訂單超時預警",
                f"有 {overdue_count} 筆訂單超過 48 小時未出貨",
                {"overdue_count": overdue_count},
            )

    # ==================== 工具方法 ====================

    def to_dict(self) -> dict:
        """擴展狀態：加入庫存閾值"""
        base = super().to_dict()
        base["low_stock_threshold"] = self.LOW_STOCK_THRESHOLD
        return base
