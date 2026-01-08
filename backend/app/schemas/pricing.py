from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID
from pydantic import BaseModel

class PriceProposalBase(BaseModel):
    product_id: UUID
    proposed_price: Decimal
    reason: Optional[str] = None

class PriceProposalCreate(PriceProposalBase):
    pass

class PriceProposalResponse(PriceProposalBase):
    id: UUID
    status: str
    current_price: Optional[Decimal]
    final_price: Optional[Decimal]
    created_at: datetime
    ai_model_used: Optional[str]
    
    # 關聯資訊 (Frontend 需要顯示 Product Name)
    product_name: Optional[str] = None
    product_sku: Optional[str] = None

    class Config:
        from_attributes = True

class ProductPricingConfig(BaseModel):
    cost: Optional[Decimal] = None
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    auto_pricing_enabled: bool = False
