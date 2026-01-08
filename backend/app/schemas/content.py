# =============================================
# AI 內容 Schemas
# =============================================

from datetime import datetime
from typing import Optional, List, Any
from uuid import UUID
from pydantic import BaseModel, Field


# =============================================
# 內容生成請求
# =============================================

class ProductInfo(BaseModel):
    """商品資訊（用於生成文案）"""
    name: str = Field(..., min_length=1)
    brand: Optional[str] = None
    features: List[str] = Field(default=[])
    target_audience: Optional[str] = None
    price: Optional[str] = None
    category: Optional[str] = None


class ContentGenerateRequest(BaseModel):
    """生成文案請求"""
    product_id: Optional[UUID] = None
    product_info: Optional[ProductInfo] = None
    content_type: str = Field(default="full_copy", description="title, description, selling_points, full_copy")
    style: str = Field(default="professional", description="formal, casual, playful, professional")
    language: str = Field(default="zh-HK", description="zh-HK, zh-TW, en")


class ContentBatchGenerateRequest(BaseModel):
    """批量生成文案請求"""
    product_ids: List[UUID]
    content_type: str = Field(default="full_copy")
    style: str = Field(default="professional")


# =============================================
# 內容響應
# =============================================

class GeneratedContent(BaseModel):
    """生成的內容"""
    title: Optional[str] = None
    selling_points: Optional[List[str]] = None
    description: Optional[str] = None
    short_description: Optional[str] = None
    hashtags: Optional[List[str]] = None


class ContentGenerateResponse(BaseModel):
    """生成文案響應"""
    id: UUID
    content_type: str
    content: GeneratedContent
    metadata: dict = Field(default={})


class ContentResponse(BaseModel):
    """內容響應"""
    id: UUID
    product_id: Optional[UUID] = None
    product_name: Optional[str] = None
    content_type: str
    style: Optional[str] = None
    language: str
    content: str
    content_json: Optional[dict] = None
    version: int
    status: str
    generated_at: datetime
    approved_at: Optional[datetime] = None
    approved_by: Optional[str] = None

    model_config = {"from_attributes": True}


class ContentListResponse(BaseModel):
    """內容列表響應"""
    data: List[ContentResponse]
    total: int


class ContentApproveResponse(BaseModel):
    """審批響應"""
    id: UUID
    status: str
    approved_at: datetime


class BatchTaskResponse(BaseModel):
    """批量任務響應"""
    task_id: str
    message: str
    product_count: int
