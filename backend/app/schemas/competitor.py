# =============================================
# 競品監測 Schemas
# =============================================

from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, HttpUrl


# =============================================
# 競爭對手 Schemas
# =============================================

class CompetitorBase(BaseModel):
    """競爭對手基礎 Schema"""
    name: str = Field(..., min_length=1, max_length=255)
    platform: str = Field(..., min_length=1, max_length=100)
    base_url: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = None


class CompetitorCreate(CompetitorBase):
    """創建競爭對手"""
    pass


class CompetitorUpdate(BaseModel):
    """更新競爭對手"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    platform: Optional[str] = Field(None, min_length=1, max_length=100)
    base_url: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class CompetitorResponse(CompetitorBase):
    """競爭對手響應"""
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    product_count: int = 0
    last_scraped_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class CompetitorListResponse(BaseModel):
    """競爭對手列表響應"""
    data: List[CompetitorResponse]
    total: int


# =============================================
# 競品商品 Schemas
# =============================================

class CompetitorProductBase(BaseModel):
    """競品商品基礎 Schema"""
    url: str = Field(..., max_length=1000)
    name: Optional[str] = Field(None, max_length=500)
    category: Optional[str] = Field(None, max_length=255)


class CompetitorProductCreate(CompetitorProductBase):
    """創建競品商品"""
    pass


class CompetitorProductUpdate(BaseModel):
    """更新競品商品"""
    name: Optional[str] = Field(None, max_length=500)
    url: Optional[str] = Field(None, max_length=1000)
    category: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = None


class CompetitorProductBulkCreate(BaseModel):
    """批量創建競品商品"""
    products: List["CompetitorProductCreate"]


class CompetitorProductResponse(BaseModel):
    """競品商品響應"""
    id: UUID
    competitor_id: UUID
    name: str
    url: str
    sku: Optional[str] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    is_active: bool
    last_scraped_at: Optional[datetime] = None
    current_price: Optional[Decimal] = None
    previous_price: Optional[Decimal] = None
    price_change: Optional[Decimal] = None
    stock_status: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class CompetitorProductListResponse(BaseModel):
    """競品商品列表響應"""
    data: List[CompetitorProductResponse]
    total: int
    page: int
    limit: int


# =============================================
# 價格快照 Schemas
# =============================================

class PriceSnapshotResponse(BaseModel):
    """價格快照響應"""
    id: UUID
    price: Optional[Decimal] = None
    original_price: Optional[Decimal] = None
    discount_percent: Optional[Decimal] = None
    stock_status: Optional[str] = None
    rating: Optional[Decimal] = None
    review_count: Optional[int] = None
    scraped_at: datetime

    model_config = {"from_attributes": True}


class PriceHistoryResponse(BaseModel):
    """價格歷史響應"""
    product: CompetitorProductResponse
    history: List[PriceSnapshotResponse]


# =============================================
# 價格警報 Schemas
# =============================================

class PriceAlertResponse(BaseModel):
    """價格警報響應"""
    id: UUID
    product_name: str
    competitor_name: str
    alert_type: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    change_percent: Optional[Decimal] = None
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class PriceAlertListResponse(BaseModel):
    """價格警報列表響應"""
    data: List[PriceAlertResponse]
    unread_count: int


# =============================================
# 爬取任務 Schemas
# =============================================

class ScrapeTaskResponse(BaseModel):
    """爬取任務響應"""
    task_id: str
    message: str
