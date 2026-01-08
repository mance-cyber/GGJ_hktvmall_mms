# =============================================
# 分析/Dashboard API
# =============================================

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List, Optional

from app.models.database import get_db
from app.models.competitor import Competitor, CompetitorProduct, PriceAlert
from app.models.content import AIContent

router = APIRouter()


class AlertSummary(BaseModel):
    unread: int
    today: int
    price_drops: int
    price_increases: int


class CompetitorSummary(BaseModel):
    total: int
    active: int
    products_monitored: int


class ContentSummary(BaseModel):
    generated_today: int
    pending_approval: int


class RecentAlert(BaseModel):
    id: str
    product_name: str
    alert_type: str
    change_percent: Optional[float]
    created_at: datetime


class PriceTrend(BaseModel):
    date: str
    avg_price_change: float


class DashboardResponse(BaseModel):
    competitors: CompetitorSummary
    alerts: AlertSummary
    content: ContentSummary
    recent_alerts: List[RecentAlert]
    price_trends: List[PriceTrend]


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
):
    """獲取 Dashboard 總覽數據"""
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    # 競爭對手統計
    total_competitors = await db.execute(select(func.count(Competitor.id)))
    active_competitors = await db.execute(
        select(func.count(Competitor.id)).where(Competitor.is_active == True)
    )
    total_products = await db.execute(
        select(func.count(CompetitorProduct.id)).where(CompetitorProduct.is_active == True)
    )

    competitors_summary = CompetitorSummary(
        total=total_competitors.scalar() or 0,
        active=active_competitors.scalar() or 0,
        products_monitored=total_products.scalar() or 0,
    )

    # 警報統計
    unread_alerts = await db.execute(
        select(func.count(PriceAlert.id)).where(PriceAlert.is_read == False)
    )
    today_alerts = await db.execute(
        select(func.count(PriceAlert.id)).where(PriceAlert.created_at >= today)
    )
    price_drops = await db.execute(
        select(func.count(PriceAlert.id)).where(
            PriceAlert.alert_type == "price_drop",
            PriceAlert.created_at >= today - timedelta(days=7)
        )
    )
    price_increases = await db.execute(
        select(func.count(PriceAlert.id)).where(
            PriceAlert.alert_type == "price_increase",
            PriceAlert.created_at >= today - timedelta(days=7)
        )
    )

    alerts_summary = AlertSummary(
        unread=unread_alerts.scalar() or 0,
        today=today_alerts.scalar() or 0,
        price_drops=price_drops.scalar() or 0,
        price_increases=price_increases.scalar() or 0,
    )

    # 內容統計
    generated_today = await db.execute(
        select(func.count(AIContent.id)).where(AIContent.generated_at >= today)
    )
    pending_approval = await db.execute(
        select(func.count(AIContent.id)).where(AIContent.status == "draft")
    )

    content_summary = ContentSummary(
        generated_today=generated_today.scalar() or 0,
        pending_approval=pending_approval.scalar() or 0,
    )

    # 最近警報
    recent_alerts_query = select(PriceAlert).order_by(
        PriceAlert.created_at.desc()
    ).limit(5)
    recent_alerts_result = await db.execute(recent_alerts_query)
    recent_alerts_data = recent_alerts_result.scalars().all()

    recent_alerts = []
    for alert in recent_alerts_data:
        # 獲取商品名稱
        product_query = select(CompetitorProduct.name).where(
            CompetitorProduct.id == alert.competitor_product_id
        )
        product_result = await db.execute(product_query)
        product_name = product_result.scalar() or "未知商品"

        recent_alerts.append(RecentAlert(
            id=str(alert.id),
            product_name=product_name,
            alert_type=alert.alert_type,
            change_percent=float(alert.change_percent) if alert.change_percent else None,
            created_at=alert.created_at,
        ))

    # 價格趨勢（過去7天的平均變動）
    # 這裡簡化處理，實際應該從 price_snapshots 計算
    price_trends = []
    for i in range(7):
        date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        price_trends.append(PriceTrend(date=date, avg_price_change=0.0))

    return DashboardResponse(
        competitors=competitors_summary,
        alerts=alerts_summary,
        content=content_summary,
        recent_alerts=recent_alerts,
        price_trends=list(reversed(price_trends)),
    )
