# =============================================
# Scout Agent（偵察兵）
# =============================================
# 用途：競品情報自動化 — 發現、監測、分析
# 封裝：CompetitorMatcherService + PriceAlert 分類
# =============================================

from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import select, desc

from app.agents.base import AgentBase
from app.agents.events import Event, Events


class ScoutAgent(AgentBase):
    """
    偵察兵：自動發現和監測競品

    核心能力：
    - 新商品上架時自動搜索 HKTVmall 競品
    - 爬取完成後分析價格變動，發射下游事件
    - 排程批量分析競品動態
    """

    # 顯著降價閾值（高於此值才觸發 COMPETITOR_PRICE_DROP）
    SIGNIFICANT_DROP_PERCENT = Decimal("5.0")

    @property
    def name(self) -> str:
        return "scout"

    @property
    def description(self) -> str:
        return "偵察兵：競品發現、價格監測、情報分析"

    def register_handlers(self) -> dict[str, Any]:
        return {
            Events.PRODUCT_CREATED: self._on_product_created,
            Events.SCRAPE_COMPLETED: self._on_scrape_completed,
            Events.SCHEDULE_SCOUT_ANALYZE: self._on_schedule_analyze,
        }

    # ==================== 事件處理 ====================

    async def _on_product_created(self, event: Event) -> None:
        """新商品上架 -> 自動搜索競品"""
        product_id = event.payload.get("product_id")
        if not product_id:
            return

        self._logger.info(f"新商品 {product_id} -> 搜索競品")

        from app.models.product import Product
        from app.services.competitor_matcher import CompetitorMatcherService

        matched_count = 0
        async with self.get_db_session() as session:
            product = await session.get(Product, UUID(str(product_id)))
            if not product:
                self._logger.warning(f"商品 {product_id} 不存在")
                return

            try:
                matcher = CompetitorMatcherService()
                matches = await matcher.find_competitors_for_product(
                    session, product, platform="hktvmall"
                )
                matched_count = sum(1 for m in matches if m.is_match)
                self._logger.info(
                    f"商品 {product.sku}: "
                    f"{matched_count}/{len(matches)} 個競品匹配"
                )
            except Exception as exc:
                self._logger.error(f"競品搜索失敗: {exc}")
                await self.escalate_to_human(
                    "競品搜索失敗",
                    f"商品 {product_id} 的自動競品搜索出錯",
                    {"product_id": str(product_id), "error": str(exc)[:200]},
                )
                return

        await self.emit(Events.AGENT_TASK_COMPLETED, {
            "agent": self.name,
            "task": "find_competitors",
            "product_id": str(product_id),
            "matches_found": matched_count,
        })

    async def _on_scrape_completed(self, event: Event) -> None:
        """爬取完成 -> 分析價格變動，發射下游事件"""
        competitor_id = event.payload.get("competitor_id")
        alerts_count = event.payload.get("alerts_created", 0)

        if not competitor_id or alerts_count == 0:
            return

        self._logger.info(
            f"爬取完成 competitor={competitor_id}, "
            f"{alerts_count} 個告警 -> 分析中"
        )

        from app.models.competitor import CompetitorProduct, PriceAlert

        # 收集告警數據（session 內），分類發射（session 外）
        alerts_data: list[dict] = []
        async with self.get_db_session() as session:
            stmt = (
                select(PriceAlert)
                .join(CompetitorProduct)
                .where(
                    CompetitorProduct.competitor_id == UUID(str(competitor_id)),
                    PriceAlert.is_read.is_(False),
                )
                .order_by(desc(PriceAlert.created_at))
                .limit(50)
            )
            result = await session.execute(stmt)
            for alert in result.scalars().all():
                alerts_data.append({
                    "cp_id": str(alert.competitor_product_id),
                    "alert_type": alert.alert_type,
                    "change_percent": (
                        float(alert.change_percent)
                        if alert.change_percent else 0
                    ),
                    "old_value": alert.old_value,
                    "new_value": alert.new_value,
                })

        # Session 已關閉，安全地發射下游事件
        for data in alerts_data:
            await self._classify_and_emit(data)

        await self.emit(Events.AGENT_TASK_COMPLETED, {
            "agent": self.name,
            "task": "analyze_scrape",
            "competitor_id": str(competitor_id),
            "alerts_analyzed": len(alerts_data),
        })

    async def _on_schedule_analyze(self, event: Event) -> None:
        """Commander 排程：統計需分析的商品數"""
        self._logger.info("排程觸發：批量競品分析")

        from app.models.product import Product, ProductCompetitorMapping

        products_count = 0
        async with self.get_db_session() as session:
            stmt = (
                select(Product)
                .join(ProductCompetitorMapping)
                .distinct()
            )
            result = await session.execute(stmt)
            products_count = len(result.scalars().all())

        self._logger.info(f"共 {products_count} 個商品有競品映射")

        # 實際批量爬取由 Celery beat 觸發，此處僅統計
        await self.emit(Events.AGENT_TASK_COMPLETED, {
            "agent": self.name,
            "task": "batch_analyze",
            "products_count": products_count,
        })

    # ==================== 工具方法 ====================

    async def _classify_and_emit(self, data: dict) -> None:
        """將告警數據分類並發射對應的高層事件"""
        cp_id = data["cp_id"]
        alert_type = data["alert_type"]
        change = data["change_percent"]

        if alert_type == "price_drop":
            # 顯著降價 -> 通知 Pricer
            if abs(change) >= float(self.SIGNIFICANT_DROP_PERCENT):
                await self.emit(Events.COMPETITOR_PRICE_DROP, {
                    "competitor_product_id": cp_id,
                    "new_price": data["new_value"],
                    "old_price": data["old_value"],
                    "change_percent": change,
                })

            # 所有降價都觸發告警
            await self.emit(Events.PRICE_ALERT_CREATED, {
                "competitor_product_id": cp_id,
                "alert_type": alert_type,
                "change_percent": change,
            })

        elif alert_type == "out_of_stock":
            await self.emit(Events.COMPETITOR_STOCKOUT, {
                "competitor_product_id": cp_id,
                "competitor_name": "unknown",
                "product_name": data["new_value"] or "unknown",
            })

        elif alert_type in ("price_increase", "back_in_stock"):
            await self.emit(Events.PRICE_ALERT_CREATED, {
                "competitor_product_id": cp_id,
                "alert_type": alert_type,
                "change_percent": change,
            })

    def to_dict(self) -> dict:
        """擴展狀態：加入降價閾值"""
        base = super().to_dict()
        base["significant_drop_percent"] = float(self.SIGNIFICANT_DROP_PERCENT)
        return base
