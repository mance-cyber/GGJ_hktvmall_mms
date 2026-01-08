# =============================================
# 智能定價與審計模型
# =============================================

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import String, Text, Boolean, ForeignKey, Numeric, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.database import Base

class ProposalStatus:
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTED = "executed"
    FAILED = "failed"

class ProposalType:
    PRICE_UPDATE = "price_update"
    STOCK_UPDATE = "stock_update"

class PriceProposal(Base):
    """
    AI 改價/庫存提案
    Human-in-the-Loop 的核心: AI 創建 -> 人類審批 -> 系統執行
    """
    __tablename__ = "price_proposals"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"))
    
    proposal_type: Mapped[str] = mapped_column(String(50), default=ProposalType.PRICE_UPDATE, comment="price_update, stock_update")
    status: Mapped[str] = mapped_column(String(50), default=ProposalStatus.PENDING, index=True)
    
    current_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    proposed_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    final_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), comment="最終執行價格(可能被人類修改)")
    
    reason: Mapped[Optional[str]] = mapped_column(Text, comment="AI 給出的建議原因")
    ai_model_used: Mapped[Optional[str]] = mapped_column(String(100), comment="生成建議的模型")
    
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column()
    reviewed_by: Mapped[Optional[str]] = mapped_column(String(100), comment="審批人")
    executed_at: Mapped[Optional[datetime]] = mapped_column()
    error_message: Mapped[Optional[str]] = mapped_column(Text)

    # 關聯
    product: Mapped["Product"] = relationship(back_populates="price_proposals")


class AuditLog(Base):
    """
    審計日誌
    記錄所有關鍵操作，特別是涉及金錢(改價)和庫存的變動
    """
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    action: Mapped[str] = mapped_column(String(100), index=True, comment="例如: approve_price, reject_price, auto_sync")
    entity_type: Mapped[str] = mapped_column(String(50), index=True, comment="例如: product, proposal, order")
    entity_id: Mapped[Optional[str]] = mapped_column(String(100))
    
    user_id: Mapped[Optional[str]] = mapped_column(String(100), default="system")
    details: Mapped[Optional[dict]] = mapped_column(JSONB, comment="操作詳情 snapshot")
    
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

# 避免循環導入
from app.models.product import Product
