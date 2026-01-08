from typing import Optional
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel

class PromotionBase(BaseModel):
    product_id: UUID
    promotion_type: str = "discount_single"
    original_price: Decimal
    discount_percent: Decimal
    discounted_price: Decimal
    start_date: datetime
    end_date: datetime
    reason: str
    marketing_copy: Optional[str] = None

class PromotionCreate(PromotionBase):
    pass

class PromotionResponse(PromotionBase):
    id: UUID
    projected_profit: Decimal
    projected_margin: float
    status: str
    created_at: datetime
    
    product_name: Optional[str] = None
    product_sku: Optional[str] = None
    
    class Config:
        from_attributes = True

class PromotionStats(BaseModel):
    active_count: int
    pending_count: int
    avg_discount: float
