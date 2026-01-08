from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel

class OrderItemBase(BaseModel):
    sku_code: str
    product_name: str
    quantity: int
    unit_price: Optional[Decimal]
    subtotal: Optional[Decimal]

class OrderItemResponse(OrderItemBase):
    id: UUID
    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    order_number: str
    order_date: datetime
    ship_by_date: Optional[datetime]
    status: str
    hktv_status: Optional[str]
    total_amount: Optional[Decimal]
    delivery_mode: Optional[str]
    customer_region: Optional[str]

class OrderResponse(OrderBase):
    id: UUID
    items: List[OrderItemResponse] = []
    
    class Config:
        from_attributes = True

class OrderListResponse(BaseModel):
    data: List[OrderResponse]
    total: int
    page: int
    limit: int
