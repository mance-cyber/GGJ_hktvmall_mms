# =============================================
# ROI 分析 API
# 展示 GoGoJap 為用戶創造的價值
# =============================================

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Literal

from app.models.database import get_db
from app.services.roi_service import ROIService
from app.schemas.roi import (
    ROISummary, ROITrendsResponse,
    PricingImpactResponse, CompetitorInsights
)

router = APIRouter()


@router.get("/summary", response_model=ROISummary)
async def get_roi_summary(
    period: Literal["today", "week", "month", "quarter"] = Query(
        default="month",
        description="時間範圍: today=今日, week=本週, month=本月, quarter=本季"
    ),
    db: AsyncSession = Depends(get_db)
):
    """
    獲取 ROI 總覽

    計算指定時間範圍內的:
    - 總價值創造
    - AI 定價貢獻
    - 競品監測價值
    - 風險規避價值
    - 整體 ROI 百分比
    """
    service = ROIService(db)
    return await service.get_summary(period=period)


@router.get("/trends", response_model=ROITrendsResponse)
async def get_roi_trends(
    days: int = Query(default=30, ge=1, le=365, description="天數範圍"),
    granularity: Literal["day", "week", "month"] = Query(
        default="day",
        description="數據粒度"
    ),
    db: AsyncSession = Depends(get_db)
):
    """
    獲取 ROI 趨勢數據

    返回時間序列數據用於圖表展示:
    - 每日/每週累計價值
    - AI 定價貢獻趨勢
    - 競品監測價值趨勢
    """
    service = ROIService(db)
    return await service.get_trends(days=days, granularity=granularity)


@router.get("/pricing-impact", response_model=PricingImpactResponse)
async def get_pricing_impact(
    limit: int = Query(default=10, ge=1, le=100, description="返回數量限制"),
    db: AsyncSession = Depends(get_db)
):
    """
    獲取 AI 改價影響分析

    返回:
    - 影響最大的改價提案列表
    - 改價統計摘要 (總數、執行數、通過率)
    - 總影響金額
    """
    service = ROIService(db)
    return await service.get_pricing_impact(limit=limit)


@router.get("/competitor-insights", response_model=CompetitorInsights)
async def get_competitor_insights(
    period: Literal["today", "week", "month", "quarter"] = Query(
        default="month",
        description="時間範圍"
    ),
    db: AsyncSession = Depends(get_db)
):
    """
    獲取競品監測價值洞察

    返回:
    - 觸發的價格告警數
    - 降價/加價偵測統計
    - 潛在節省金額估算
    """
    service = ROIService(db)
    return await service.get_competitor_insights(period=period)
