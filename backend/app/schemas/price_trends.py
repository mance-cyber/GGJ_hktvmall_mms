# =============================================
# 價格趨勢 API Schema
# =============================================

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from uuid import UUID
from enum import Enum


class TimeInterval(str, Enum):
    """時間聚合粒度"""
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"


# =============================================
# 產品列表（下拉選單用）
# =============================================

class ProductListItem(BaseModel):
    """產品列表項（供下拉選單）"""
    id: UUID
    sku: str
    name: str
    current_price: Optional[Decimal] = None
    competitor_count: int = Field(description="關聯的競爭對手數量")

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    """產品列表響應"""
    products: List[ProductListItem]
    total: int


# =============================================
# 價格快照數據點
# =============================================

class PriceDataPoint(BaseModel):
    """價格數據點"""
    date: datetime
    price: Optional[Decimal] = None
    original_price: Optional[Decimal] = None
    discount_percent: Optional[Decimal] = None
    stock_status: Optional[str] = None
    promotion_text: Optional[str] = None


# =============================================
# 競爭對手信息
# =============================================

class CompetitorInfo(BaseModel):
    """競爭對手信息"""
    id: UUID
    name: str
    platform: str
    product_name: str
    current_price: Optional[Decimal] = None

    class Config:
        from_attributes = True


# =============================================
# 趨勢摘要統計
# =============================================

class TrendSummary(BaseModel):
    """趨勢摘要統計"""
    price_gap_current: Optional[float] = Field(
        None,
        description="當前價差百分比（正數表示自家較貴）"
    )
    price_gap_avg: Optional[float] = Field(
        None,
        description="平均價差百分比"
    )
    lowest_competitor_price: Optional[Decimal] = Field(
        None,
        description="競爭對手最低價"
    )
    volatility: Optional[float] = Field(
        None,
        description="價格波動率（標準差百分比）"
    )
    own_price_change: Optional[float] = Field(
        None,
        description="自家價格變化百分比（期間首尾對比）"
    )
    competitor_avg_change: Optional[float] = Field(
        None,
        description="競爭對手平均價格變化百分比"
    )


# =============================================
# 自家產品信息
# =============================================

class OwnProductInfo(BaseModel):
    """自家產品信息"""
    id: UUID
    sku: str
    name: str
    category: Optional[str] = None
    current_price: Optional[Decimal] = None

    class Config:
        from_attributes = True


# =============================================
# 完整趨勢響應
# =============================================

class PriceTrendResponse(BaseModel):
    """價格趨勢完整響應"""
    own_product: OwnProductInfo
    competitors: List[CompetitorInfo]
    trends: Dict[str, List[PriceDataPoint]] = Field(
        description="趨勢數據，key 為 'own' 或競爭對手 ID"
    )
    summary: TrendSummary

    # 查詢參數回顯
    start_date: date
    end_date: date
    interval: TimeInterval


# =============================================
# 請求參數
# =============================================

class PriceTrendQuery(BaseModel):
    """價格趨勢查詢參數"""
    start_date: Optional[date] = Field(
        None,
        description="開始日期，默認 30 天前"
    )
    end_date: Optional[date] = Field(
        None,
        description="結束日期，默認今天"
    )
    interval: Optional[TimeInterval] = Field(
        None,
        description="聚合粒度，默認根據時間範圍自動選擇"
    )
