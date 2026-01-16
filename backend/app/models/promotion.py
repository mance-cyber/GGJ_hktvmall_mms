import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import String, DateTime, Numeric, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.database import Base, utcnow

class PromotionProposal(Base):
    """AI 推廣建議與活動記錄"""
    __tablename__ = "promotion_proposals"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("products.id"))
    
    # 推廣類型
    promotion_type: Mapped[str] = mapped_column(String(50), default="discount_single") # discount_single, bundle
    
    # 價格設定
    original_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    discount_percent: Mapped[Decimal] = mapped_column(Numeric(5, 2)) # e.g. 10.00 for 10% off
    discounted_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    
    # 預測數據
    projected_profit: Mapped[Decimal] = mapped_column(Numeric(10, 2)) # 折後預計每單利潤
    projected_margin: Mapped[float] = mapped_column(Numeric(5, 2))    # 折後利潤率 %
    
    # 時間
    start_date: Mapped[datetime] = mapped_column(DateTime)
    end_date: Mapped[datetime] = mapped_column(DateTime)
    
    # AI 內容
    reason: Mapped[str] = mapped_column(Text) # 推薦原因
    marketing_copy: Mapped[str] = mapped_column(Text, nullable=True) # 建議文案
    
    # 狀態: pending, approved, rejected, active, expired
    status: Mapped[str] = mapped_column(String(50), default="pending")
    
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    
    # 關聯
    product = relationship("Product")

