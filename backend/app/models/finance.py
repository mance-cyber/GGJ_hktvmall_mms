import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from sqlalchemy import String, DateTime, Numeric, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.database import Base

class Settlement(Base):
    """HKTVmall 結算單 (Statement)"""
    __tablename__ = "settlements"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    statement_no: Mapped[str] = mapped_column(String(50), unique=True) # 結算單號
    cycle_start: Mapped[datetime] = mapped_column(DateTime)
    cycle_end: Mapped[datetime] = mapped_column(DateTime)
    
    settlement_date: Mapped[datetime] = mapped_column(DateTime)
    
    # 金額總計
    total_sales_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0) # 銷售總額
    total_commission: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)   # 佣金總額
    total_shipping_fee: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0) # 運費總額
    other_deductions: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)   # 其他扣款
    net_settlement_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))         # 最終結算金額
    
    currency: Mapped[str] = mapped_column(String(10), default="HKD")
    status: Mapped[str] = mapped_column(String(50), default="Paid")
    
    items: Mapped[List["SettlementItem"]] = relationship("SettlementItem", back_populates="settlement", cascade="all, delete-orphan")
    
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)


class SettlementItem(Base):
    """結算單明細 (每筆訂單)"""
    __tablename__ = "settlement_items"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    settlement_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("settlements.id"))
    
    order_number: Mapped[str] = mapped_column(String(50)) # 對應訂單號
    sku: Mapped[str] = mapped_column(String(50))
    product_name: Mapped[str] = mapped_column(String(255), nullable=True)
    
    quantity: Mapped[int] = mapped_column(Integer)
    
    item_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))       # 單價
    commission_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2))   # 佣金率 %
    commission_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2)) # 佣金金額
    
    transaction_date: Mapped[datetime] = mapped_column(DateTime)
    
    settlement: Mapped["Settlement"] = relationship("Settlement", back_populates="items")
