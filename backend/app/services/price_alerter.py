# =============================================
# Price Alerter — Competitor v2
# 價格/庫存變動警報管理
# =============================================

import logging
from typing import Optional
from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.competitor import PriceAlert, PriceSnapshot, CompetitorProduct, Competitor
from app.models.product import ProductCompetitorMapping

logger = logging.getLogger(__name__)


class PriceAlerter:
    """
    價格變動警報生成器
    
    - check_alerts(): 比較新舊 snapshot → 生成 PriceAlert
    - get_pending_alerts(): 取未讀警報
    - get_alert_summary(): 取警報摘要（給 Morning Brief 用）
    """

    # 價格變動閾值
    PRICE_DROP_THRESHOLD_PCT = Decimal("10.0")     # 競品降價 ≥10%
    PRICE_INCREASE_THRESHOLD_PCT = Decimal("15.0")  # 競品加價 ≥15%

    @staticmethod
    async def check_alerts(
        db: AsyncSession,
        new_snapshot: PriceSnapshot,
        previous_snapshot: Optional[PriceSnapshot],
    ) -> Optional[PriceAlert]:
        """
        比較新舊 snapshot，生成 alert。
        
        Alert 條件：
        - price_drop: 降價 ≥ 10%
        - price_increase: 加價 ≥ 15%
        - out_of_stock: 有貨 → 無貨
        - back_in_stock: 無貨 → 有貨
        """
        if not previous_snapshot:
            return None

        now = datetime.now(timezone.utc).replace(tzinfo=None)
        alert = None

        # 價格變動
        if (
            previous_snapshot.price
            and new_snapshot.price
            and previous_snapshot.price > 0
        ):
            change = new_snapshot.price - previous_snapshot.price
            change_pct = abs(change / previous_snapshot.price * 100)

            if change < 0 and change_pct >= PriceAlerter.PRICE_DROP_THRESHOLD_PCT:
                alert = PriceAlert(
                    id=uuid4(),
                    competitor_product_id=new_snapshot.competitor_product_id,
                    alert_type="price_drop",
                    old_value=str(previous_snapshot.price),
                    new_value=str(new_snapshot.price),
                    change_percent=Decimal(str(round(float(change_pct), 2))),
                    created_at=now,
                )
            elif change > 0 and change_pct >= PriceAlerter.PRICE_INCREASE_THRESHOLD_PCT:
                alert = PriceAlert(
                    id=uuid4(),
                    competitor_product_id=new_snapshot.competitor_product_id,
                    alert_type="price_increase",
                    old_value=str(previous_snapshot.price),
                    new_value=str(new_snapshot.price),
                    change_percent=Decimal(str(round(float(change_pct), 2))),
                    created_at=now,
                )

        # 庫存變動
        if not alert:
            prev_stock = previous_snapshot.stock_status
            new_stock = new_snapshot.stock_status

            if prev_stock == "in_stock" and new_stock == "out_of_stock":
                alert = PriceAlert(
                    id=uuid4(),
                    competitor_product_id=new_snapshot.competitor_product_id,
                    alert_type="out_of_stock",
                    old_value=prev_stock,
                    new_value=new_stock,
                    created_at=now,
                )
            elif prev_stock == "out_of_stock" and new_stock == "in_stock":
                alert = PriceAlert(
                    id=uuid4(),
                    competitor_product_id=new_snapshot.competitor_product_id,
                    alert_type="back_in_stock",
                    old_value=prev_stock,
                    new_value=new_stock,
                    created_at=now,
                )

        if alert:
            db.add(alert)

        return alert

    @staticmethod
    async def get_pending_alerts(
        db: AsyncSession,
        limit: int = 50,
    ) -> list[dict]:
        """
        取未讀警報（附帶商品名稱 + 商戶名稱）
        
        Returns:
            [{"alert": PriceAlert, "product_name": str, "merchant_name": str, "merchant_tier": int}]
        """
        stmt = (
            select(PriceAlert, CompetitorProduct.name, Competitor.name, Competitor.tier)
            .join(CompetitorProduct, PriceAlert.competitor_product_id == CompetitorProduct.id)
            .join(Competitor, CompetitorProduct.competitor_id == Competitor.id)
            .where(PriceAlert.is_notified == False)
            .order_by(PriceAlert.created_at.desc())
            .limit(limit)
        )
        result = await db.execute(stmt)
        rows = result.all()

        return [
            {
                "alert": row[0],
                "product_name": row[1],
                "merchant_name": row[2],
                "merchant_tier": row[3],
            }
            for row in rows
        ]

    @staticmethod
    async def get_alert_summary(
        db: AsyncSession,
        hours: int = 24,
    ) -> dict:
        """
        取最近 N 小時的警報摘要（給 Morning Brief 用）
        
        Returns:
            {
                "total": N,
                "price_drops": N,
                "price_increases": N,
                "stock_changes": N,
                "top_alerts": [...]
            }
        """
        from datetime import timedelta

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=hours)

        stmt = select(PriceAlert).where(PriceAlert.created_at >= cutoff)
        result = await db.execute(stmt)
        alerts = result.scalars().all()

        price_drops = [a for a in alerts if a.alert_type == "price_drop"]
        price_increases = [a for a in alerts if a.alert_type == "price_increase"]
        stock_changes = [a for a in alerts if a.alert_type in ("out_of_stock", "back_in_stock")]

        # 取 top alerts（附帶商品名）
        top_stmt = (
            select(PriceAlert, CompetitorProduct.name, Competitor.name)
            .join(CompetitorProduct, PriceAlert.competitor_product_id == CompetitorProduct.id)
            .join(Competitor, CompetitorProduct.competitor_id == Competitor.id)
            .where(PriceAlert.created_at >= cutoff)
            .order_by(PriceAlert.change_percent.desc().nullslast())
            .limit(10)
        )
        top_result = await db.execute(top_stmt)
        top_rows = top_result.all()

        return {
            "total": len(alerts),
            "price_drops": len(price_drops),
            "price_increases": len(price_increases),
            "stock_changes": len(stock_changes),
            "top_alerts": [
                {
                    "type": row[0].alert_type,
                    "product": row[1],
                    "merchant": row[2],
                    "old": row[0].old_value,
                    "new": row[0].new_value,
                    "change_pct": float(row[0].change_percent) if row[0].change_percent else None,
                }
                for row in top_rows
            ],
        }

    @staticmethod
    async def mark_notified(
        db: AsyncSession,
        alert_ids: list,
    ):
        """標記警報已通知"""
        if not alert_ids:
            return
        stmt = select(PriceAlert).where(PriceAlert.id.in_(alert_ids))
        result = await db.execute(stmt)
        for alert in result.scalars().all():
            alert.is_notified = True
