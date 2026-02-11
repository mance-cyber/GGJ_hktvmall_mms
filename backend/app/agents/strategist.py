# =============================================
# Strategist Agent（軍師）
# =============================================
# 用途：市場策略 — 綜合分析、機會識別、策略建議
# 封裝：AIAnalysisService + AnalyticsService
# =============================================

import asyncio
from typing import Any

from app.agents.base import AgentBase
from app.agents.events import Event, Events


class StrategistAgent(AgentBase):
    """
    軍師：數據驅動策略建議

    核心能力：
    - 每日市場簡報（AI 雙串聯：Insights -> Strategy）
    - 競品缺貨搶市分析
    - 促銷日曆提前預警
    """

    # 香港電商促銷日曆
    PROMO_CALENDAR = {
        "01-01": "新年",
        "02-14": "情人節",
        "05-01": "勞動節",
        "06-18": "618",
        "11-11": "雙十一",
        "12-12": "雙十二",
        "12-25": "聖誕",
    }

    @property
    def name(self) -> str:
        return "strategist"

    @property
    def description(self) -> str:
        return "軍師：市場分析、策略建議、促銷預警"

    def register_handlers(self) -> dict[str, Any]:
        return {
            Events.DAILY_DATA_READY: self._on_daily_data_ready,
            Events.COMPETITOR_STOCKOUT: self._on_competitor_stockout,
            Events.SCHEDULE_STRATEGIST_BRIEFING: self._on_schedule_briefing,
        }

    # ==================== 事件處理 ====================

    async def _on_daily_data_ready(self, event: Event) -> None:
        """Ops 數據就緒 -> 記錄並等待完整簡報觸發"""
        source = event.payload.get("source", "unknown")
        orders = event.payload.get("orders_synced", 0)
        self._logger.info(f"數據就緒 (source={source}, orders={orders})")

        # 完整分析由 _on_schedule_briefing 執行
        await self.emit(Events.AGENT_TASK_COMPLETED, {
            "agent": self.name,
            "task": "data_received",
            "source": source,
        })

    async def _on_competitor_stockout(self, event: Event) -> None:
        """競品缺貨 -> 搶市機會通知"""
        cp_id = event.payload.get("competitor_product_id", "unknown")
        product_name = event.payload.get("product_name", "unknown")

        self._logger.info(f"競品缺貨: {product_name} -> 搶市機會")

        await self.escalate_to_human(
            "搶市機會",
            f"競品商品缺貨，可考慮提升曝光或促銷",
            {
                "competitor_product_id": cp_id,
                "product_name": product_name,
            },
        )

        await self.emit(Events.AGENT_TASK_COMPLETED, {
            "agent": self.name,
            "task": "opportunity_analysis",
            "competitor_product_id": cp_id,
        })

    async def _on_schedule_briefing(self, event: Event) -> None:
        """
        Commander 排程：每日市場簡報

        AI 雙串聯：
        1. AnalyticsService.get_dashboard_summary() -> 數據
        2. AIAnalysisService.generate_data_insights() -> 摘要
        3. AIAnalysisService.generate_marketing_strategy() -> 策略
        4. escalate_to_human -> Telegram 發送
        """
        self._logger.info("排程觸發：生成每日市場簡報")

        from app.services.analytics_service import AnalyticsService
        from app.services.ai_service import AIAnalysisService, AISettingsService

        # 1. 獲取儀表板數據
        dashboard_data = {}
        async with self.get_db_session() as session:
            try:
                analytics = AnalyticsService(session)
                dashboard_data = await analytics.get_dashboard_summary()
            except Exception as exc:
                self._logger.error(f"獲取儀表板數據失敗: {exc}")
                return

        if not dashboard_data:
            self._logger.warning("無數據可供分析")
            return

        # 2. AI 雙串聯分析
        try:
            async with self.get_db_session() as session:
                config = await AISettingsService.get_config(session)

            ai_service = AIAnalysisService(config)

            # generate_data_insights 是同步方法，需要 to_thread
            insights_resp = await asyncio.to_thread(
                ai_service.generate_data_insights, dashboard_data
            )

            if not insights_resp.success:
                self._logger.warning(
                    f"AI 摘要生成失敗: {insights_resp.error}"
                )
                return

            # generate_marketing_strategy 是同步方法
            strategy_resp = await asyncio.to_thread(
                ai_service.generate_marketing_strategy,
                insights_resp.content,
                {"source": "daily_briefing"},
            )

            # 3. 組裝簡報
            briefing_parts = [
                f"數據摘要:\n{insights_resp.content[:500]}",
            ]
            if strategy_resp.success:
                briefing_parts.append(
                    f"策略建議:\n{strategy_resp.content[:500]}"
                )

            await self.escalate_to_human(
                "每日市場簡報",
                "\n\n".join(briefing_parts),
                {"model": insights_resp.model},
            )

        except Exception as exc:
            self._logger.error(f"AI 分析出錯: {exc}")
            await self.escalate_to_human(
                "市場簡報生成失敗",
                "AI 分析服務暫時不可用",
                {"error": str(exc)[:200]},
            )
            return

        await self.emit(Events.AGENT_TASK_COMPLETED, {
            "agent": self.name,
            "task": "daily_briefing",
            "status": "completed",
        })

    # ==================== 工具方法 ====================

    def to_dict(self) -> dict:
        """擴展狀態：加入促銷日曆"""
        base = super().to_dict()
        base["promo_calendar"] = self.PROMO_CALENDAR
        return base
