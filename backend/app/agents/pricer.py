# =============================================
# Pricer Agent（定價師）
# =============================================
# 用途：智能定價 — 生成提案，保護利潤底線
# 封裝：PricingService（AI 提案 + 審批工作流）
# 核心原則：永遠不自己改價，只提案
# =============================================

from decimal import Decimal
from types import MappingProxyType
from typing import Any
from uuid import UUID

from app.agents.base import AgentBase
from app.agents.events import Event, Events


class PricerAgent(AgentBase):
    """
    定價師：基於市場情報生成定價建議

    安全規則：
    - 所有改價必須經 PriceProposal 審批
    - 最低 5% 利潤率保護
    - 單次最大降幅 15%
    """

    # 定價安全規則（不可變，防止運行時意外修改）
    RULES = MappingProxyType({
        "min_margin": 0.05,        # 最低 5% 利潤率
        "max_drop_percent": 15,    # 單次最大降幅 15%
        "auto_approve_below": 10,  # 降幅 < HK$10 可自動批准（需用戶開啟）
        "require_human": True,     # 預設需要人工審批
    })

    @property
    def name(self) -> str:
        return "pricer"

    @property
    def description(self) -> str:
        return "定價師：智能定價提案、利潤保護"

    def register_handlers(self) -> dict[str, Any]:
        return {
            Events.PRICE_ALERT_CREATED: self._on_price_alert,
            Events.COMPETITOR_PRICE_DROP: self._on_competitor_drop,
            Events.SCHEDULE_PRICER_BATCH: self._on_schedule_batch,
        }

    # ==================== 事件處理 ====================

    async def _on_price_alert(self, event: Event) -> None:
        """價格告警 -> 記錄並評估是否超閾值"""
        cp_id = event.payload.get("competitor_product_id")
        change = event.payload.get("change_percent", 0)

        self._logger.info(
            f"價格告警: competitor_product={cp_id}, 變動={change:.1f}%"
        )

        # 超過最大降幅閾值 -> 上報人類
        if abs(change) > self.RULES["max_drop_percent"]:
            await self.escalate_to_human(
                "異常價格變動",
                f"競品商品價格變動 {change:.1f}%，"
                f"超過 {self.RULES['max_drop_percent']}% 閾值",
                {"competitor_product_id": cp_id, "change_percent": change},
            )

    async def _on_competitor_drop(self, event: Event) -> None:
        """競品降價 -> 查找我方商品 -> 生成改價提案"""
        cp_id = event.payload.get("competitor_product_id")
        new_price_str = event.payload.get("new_price")

        if not cp_id or not new_price_str:
            return

        self._logger.info(f"競品降價: cp={cp_id}, new_price={new_price_str}")

        try:
            competitor_price = Decimal(str(new_price_str))
        except Exception:
            self._logger.warning(f"無法解析競品價格: {new_price_str}")
            return

        from sqlalchemy import select
        from app.models.product import Product, ProductCompetitorMapping
        from app.services.pricing_service import PricingService

        proposals_created = 0
        async with self.get_db_session() as session:
            # 通過映射找到我方商品
            stmt = (
                select(Product)
                .join(ProductCompetitorMapping)
                .where(
                    ProductCompetitorMapping.competitor_product_id
                    == UUID(str(cp_id))
                )
            )
            result = await session.execute(stmt)
            our_products = result.scalars().all()

            if not our_products:
                self._logger.info(f"競品 {cp_id} 未映射到任何我方商品")
                # 不提前 return，跳到函數尾部發射 AGENT_TASK_COMPLETED
                our_products = []

            pricing = PricingService(session)

            for product in our_products:
                if not product.price or not product.auto_pricing_enabled:
                    continue

                if competitor_price >= product.price:
                    continue  # 競品價格更高，無需調整

                # 計算安全底價
                cost_floor = (
                    (product.cost or Decimal("0"))
                    * Decimal(str(1 + self.RULES["min_margin"]))
                )
                hard_floor = product.min_price or Decimal("0")
                final_floor = max(cost_floor, hard_floor)

                if final_floor == 0:
                    self._logger.warning(
                        f"商品 {product.sku} 無成本/底價設置，跳過"
                    )
                    continue

                suggested = competitor_price - Decimal("1.0")
                suggested = max(suggested, final_floor)

                if suggested >= product.price:
                    continue

                # 降幅超限 -> 上報人類而非自動提案
                drop_pct = float(
                    (product.price - suggested) / product.price * 100
                )
                if drop_pct > self.RULES["max_drop_percent"]:
                    await self.escalate_to_human(
                        "大幅降價需審批",
                        f"商品 {product.sku} 建議降價 {drop_pct:.1f}%",
                        {
                            "sku": product.sku,
                            "current": str(product.price),
                            "suggested": str(suggested),
                            "competitor": str(competitor_price),
                        },
                    )
                    continue

                await pricing.create_proposal(
                    product_id=product.id,
                    proposed_price=suggested,
                    reason=(
                        f"競品降價至 ${competitor_price}，"
                        f"建議跟進至 ${suggested}"
                    ),
                    model="agent_pricer",
                )
                proposals_created += 1
                self._logger.info(
                    f"已創建提案: {product.sku} "
                    f"${product.price} -> ${suggested}"
                )

        await self.emit(Events.AGENT_TASK_COMPLETED, {
            "agent": self.name,
            "task": "generate_proposal",
            "competitor_product_id": str(cp_id),
            "proposals_created": proposals_created,
        })

    async def _on_schedule_batch(self, event: Event) -> None:
        """Commander 排程：批量分析所有商品定價"""
        self._logger.info("排程觸發：批量定價分析")

        from app.services.pricing_service import PricingService

        count = 0
        async with self.get_db_session() as session:
            pricing = PricingService(session)
            count = await pricing.generate_proposals()

        self._logger.info(f"批量定價：生成 {count} 個提案")

        await self.emit(Events.AGENT_TASK_COMPLETED, {
            "agent": self.name,
            "task": "batch_pricing",
            "proposals_generated": count,
        })

    # ==================== 工具方法 ====================

    def to_dict(self) -> dict:
        """擴展狀態：加入定價規則"""
        base = super().to_dict()
        base["rules"] = dict(self.RULES)
        return base
