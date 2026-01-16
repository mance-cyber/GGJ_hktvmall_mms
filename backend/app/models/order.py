# =============================================
# 訂單與物流模型
# =============================================

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from sqlalchemy import String, Text, Boolean, ForeignKey, Numeric, Integer, Index, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.database import Base, utcnow

class OrderStatus:
    PENDING = "Pending"           # 待處理
    CONFIRMED = "Confirmed"       # 已確認
    PACKING = "Packing"           # 包裝中
    PACKED = "Packed"             # 已包裝 (等待收貨)
    SHIPPED = "Shipped"           # 已出貨
    DELIVERED = "Delivered"       # 已送達
    CANCELLED = "Cancelled"       # 已取消
    RETURNED = "Returned"         # 已退貨

class Order(Base):
    """HKTVmall 訂單主表"""
    __tablename__ = "orders"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 核心識別
    order_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, comment="HKTVmall 訂單號 (e.g. 1234567890)")
    
    # 時間相關
    order_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    ship_by_date: Mapped[Optional[datetime]] = mapped_column(DateTime, comment="最遲出貨日")
    
    # 狀態
    status: Mapped[str] = mapped_column(String(50), default=OrderStatus.PENDING, index=True)
    hktv_status: Mapped[Optional[str]] = mapped_column(String(50), comment="HKTVmall 原始狀態")
    
    # 金額
    total_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    commission: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), comment="平台佣金")
    
    # 物流資訊
    delivery_mode: Mapped[Optional[str]] = mapped_column(String(50), comment="HD=Home Delivery, O2O=Shop")
    awb_number: Mapped[Optional[str]] = mapped_column(String(100), comment="運單號")
    
    # 客戶資訊 (部分隱私)
    customer_region: Mapped[Optional[str]] = mapped_column(String(100), comment="配送地區")
    
    # 系統資訊
    is_synced: Mapped[bool] = mapped_column(Boolean, default=True)
    last_synced_at: Mapped[datetime] = mapped_column(default=utcnow)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow, onupdate=utcnow)

    # 關聯
    items: Mapped[List["OrderItem"]] = relationship(back_populates="order", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_orders_order_number", "order_number"),
        Index("idx_orders_status", "status"),
        Index("idx_orders_date", "order_date"),
    )


class OrderItem(Base):
    """訂單商品明細"""
    __tablename__ = "order_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"))
    
    # 商品資訊
    sku_code: Mapped[str] = mapped_column(String(100), nullable=False)
    product_name: Mapped[str] = mapped_column(String(500))
    
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    unit_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    subtotal: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    
    # 關聯到本地商品庫 (如果有的話)
    product_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="SET NULL"), nullable=True)
    
    # 關聯
    order: Mapped["Order"] = relationship(back_populates="items")
