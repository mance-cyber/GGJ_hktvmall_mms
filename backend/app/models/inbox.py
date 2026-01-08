# =============================================
# 客服收件箱模型
# =============================================

import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Text, Boolean, ForeignKey, Index, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.database import Base

class Conversation(Base):
    """HKTVmall 對話 (Topic/Session)"""
    __tablename__ = "conversations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 外部 ID
    hktv_topic_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, comment="Topic ID")
    
    # 客戶資訊
    customer_name: Mapped[Optional[str]] = mapped_column(String(255))
    customer_id: Mapped[Optional[str]] = mapped_column(String(100))
    
    # 狀態
    subject: Mapped[Optional[str]] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(50), default="open", comment="open, closed")
    has_unread: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # 時間
    last_message_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    
    # 關聯
    messages: Mapped[List["Message"]] = relationship(back_populates="conversation", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_conversations_last_msg", "last_message_at"),
        Index("idx_conversations_hktv_id", "hktv_topic_id"),
    )


class Message(Base):
    """對話訊息"""
    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"))
    
    hktv_message_id: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    
    content: Mapped[str] = mapped_column(Text)
    sender_type: Mapped[str] = mapped_column(String(50), comment="customer, merchant, system, ai_draft")
    
    # AI 相關
    ai_generated: Mapped[bool] = mapped_column(Boolean, default=False)
    is_draft: Mapped[bool] = mapped_column(Boolean, default=False, comment="如果是 AI 草稿，尚未發送")
    
    sent_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    
    # 關聯
    conversation: Mapped["Conversation"] = relationship(back_populates="messages")
