# =============================================
# 商品 Schemas
# =============================================

from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Any
from uuid import UUID
from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    """商品基礎 Schema"""
    sku: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=255)
    brand: Optional[str] = Field(None, max_length=255)
    price: Optional[Decimal] = Field(None, ge=0)
    cost: Optional[Decimal] = Field(None, ge=0)
    stock_quantity: int = Field(default=0, ge=0)
    status: str = Field(default="active")
    images: List[str] = Field(default=[])
    attributes: dict = Field(default={})


class ProductCreate(ProductBase):
    """創建商品"""
    pass


class ProductUpdate(BaseModel):
    """更新商品"""
    name: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=255)
    brand: Optional[str] = Field(None, max_length=255)
    price: Optional[Decimal] = Field(None, ge=0)
    cost: Optional[Decimal] = Field(None, ge=0)
    stock_quantity: Optional[int] = Field(None, ge=0)
    status: Optional[str] = None
    images: Optional[List[str]] = None
    attributes: Optional[dict] = None


class ProductResponse(ProductBase):
    """商品響應"""
    id: UUID
    hktv_product_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProductListResponse(BaseModel):
    """商品列表響應"""
    data: List[ProductResponse]
    total: int
    page: int
    limit: int
