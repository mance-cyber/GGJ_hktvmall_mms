import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import String, DateTime, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.database import Base

class Settlement(Base):
    """HKTVmall 結算單"""
    __tablename__ = "settlements"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    cycle_start: Mapped[datetime] = mapped_column(DateTime)
    cycle_end: Mapped[datetime] = mapped_column(DateTime)
    
    settlement_date: Mapped[datetime] = mapped_column(DateTime)
    settlement_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    
    currency: Mapped[str] = mapped_column(String(10), default="HKD")
    status: Mapped[str] = mapped_column(String(50), default="Paid")
    
    report_url: Mapped[Optional[str]] = mapped_column(String(500))
    
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
