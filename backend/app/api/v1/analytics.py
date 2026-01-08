from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from app.models.database import get_db
from app.models.competitor import Competitor, CompetitorProduct, PriceAlert
from app.models.content import AIContent
from app.services.analytics_service import AnalyticsService

router = APIRouter()

# Keep old models for backward compatibility if needed, or replace them
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

# New Command Center Models
class CommandCenterResponse(BaseModel):
    stats: Dict[str, Any]
    recent_activity: List[Dict[str, Any]]

@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
):
    """(Legacy) 獲取舊版 Dashboard 數據 - 僅包含競品與內容"""
    # 這裡保留舊代碼邏輯，或者可以重構
    # 為節省時間和保持兼容，我這裡保留部分邏輯但簡化
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    # 競爭對手統計
    total_competitors = await db.execute(select(func.count(Competitor.id)))
    active_competitors = await db.execute(select(func.count(Competitor.id)).where(Competitor.is_active == True))
    total_products = await db.execute(select(func.count(CompetitorProduct.id)).where(CompetitorProduct.is_active == True))

    competitors_summary = CompetitorSummary(
        total=total_competitors.scalar() or 0,
        active=active_competitors.scalar() or 0,
        products_monitored=total_products.scalar() or 0,
    )

    # 警報統計
    unread_alerts = await db.execute(select(func.count(PriceAlert.id)).where(PriceAlert.is_read == False))
    today_alerts = await db.execute(select(func.count(PriceAlert.id)).where(PriceAlert.created_at >= today))
    
    alerts_summary = AlertSummary(
        unread=unread_alerts.scalar() or 0,
        today=today_alerts.scalar() or 0,
        price_drops=0,
        price_increases=0,
    )

    content_summary = ContentSummary(generated_today=0, pending_approval=0)
    
    return DashboardResponse(
        competitors=competitors_summary,
        alerts=alerts_summary,
        content=content_summary,
        recent_alerts=[],
        price_trends=[],
    )

@router.get("/command-center", response_model=CommandCenterResponse)
async def get_command_center(db: AsyncSession = Depends(get_db)):
    """獲取全功能營運總覽數據"""
    service = AnalyticsService(db)
    result = await service.get_dashboard_summary()
    return CommandCenterResponse(**result)
