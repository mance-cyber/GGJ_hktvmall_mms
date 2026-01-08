from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel

class SettlementItemBase(BaseModel):
    order_number: str
    sku: str
    product_name: Optional[str] = None
    quantity: int
    item_price: Decimal
    commission_rate: Decimal
    commission_amount: Decimal
    transaction_date: datetime

class SettlementItemResponse(SettlementItemBase):
    id: UUID
    settlement_id: UUID
    
    class Config:
        from_attributes = True

class SettlementBase(BaseModel):
    statement_no: str
    cycle_start: datetime
    cycle_end: datetime
    settlement_date: datetime
    total_sales_amount: Decimal
    total_commission: Decimal
    total_shipping_fee: Decimal
    other_deductions: Decimal
    net_settlement_amount: Decimal
    currency: str = "HKD"
    status: str = "Paid"

class SettlementResponse(SettlementBase):
    id: UUID
    items: List[SettlementItemResponse] = []
    created_at: datetime
    
    class Config:
        from_attributes = True

class ProfitSummary(BaseModel):
    total_revenue: Decimal
    total_commission: Decimal
    total_profit: Decimal
    profit_margin: float # %
    period_start: datetime
    period_end: datetime
