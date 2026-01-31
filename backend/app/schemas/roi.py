# =============================================
# ROI 分析 Schema
# =============================================

from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field


class ROISummary(BaseModel):
    """ROI 總覽數據"""
    total_value_generated: Decimal = Field(..., description="總價值創造 (HKD)")
    ai_pricing_contribution: Decimal = Field(..., description="AI 定價貢獻 (HKD)")
    competitor_monitoring_value: Decimal = Field(..., description="競品監測價值 (HKD)")
    risk_avoidance_value: Decimal = Field(..., description="風險規避價值 (HKD)")
    roi_percentage: float = Field(..., description="投資回報率 (%)")
    period_start: datetime
    period_end: datetime


class ROITrendPoint(BaseModel):
    """ROI 趨勢數據點"""
    date: str = Field(..., description="日期 (YYYY-MM-DD)")
    cumulative_value: Decimal = Field(..., description="累計價值")
    ai_pricing: Decimal = Field(..., description="AI 定價貢獻")
    monitoring: Decimal = Field(..., description="競品監測價值")
    risk_avoidance: Decimal = Field(..., description="風險規避價值")


class ROITrendsResponse(BaseModel):
    """ROI 趨勢響應"""
    trends: List[ROITrendPoint]
    start_date: str
    end_date: str
    granularity: str = "day"


class PricingProposalImpact(BaseModel):
    """AI 改價影響數據"""
    id: str
    product_name: str
    old_price: Decimal
    new_price: Decimal
    price_diff: Decimal = Field(..., description="價格差異")
    impact: Decimal = Field(..., description="影響金額 (價差 × 預估銷量)")
    executed_at: datetime


class PricingImpactSummary(BaseModel):
    """改價影響統計"""
    total_proposals: int
    executed_count: int
    approved_count: int
    rejected_count: int
    total_impact: Decimal


class PricingImpactResponse(BaseModel):
    """改價影響響應"""
    proposals: List[PricingProposalImpact]
    summary: PricingImpactSummary


class CompetitorInsights(BaseModel):
    """競品監測價值洞察"""
    price_alerts_triggered: int = Field(..., description="觸發的價格告警數")
    price_drops_detected: int = Field(..., description="偵測到的降價次數")
    price_increases_detected: int = Field(..., description="偵測到的加價次數")
    avg_response_time_hours: Optional[float] = Field(None, description="平均響應時間 (小時)")
    potential_savings: Decimal = Field(..., description="潛在節省金額")
    period: str
