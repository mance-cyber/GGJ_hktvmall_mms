# =============================================
# AI Agent 數據庫模型
# =============================================

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from .database import Base

class AgentConversation(Base):
    __tablename__ = "agent_conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255))
    
    # 狀態持久化
    slots = Column(JSON, default={})
    current_intent = Column(String(50), nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # 關聯
    messages = relationship("AgentMessage", back_populates="conversation", cascade="all, delete-orphan", order_by="AgentMessage.created_at")

class AgentMessage(Base):
    __tablename__ = "agent_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("agent_conversations.id", ondelete="CASCADE"))
    role = Column(String(50), nullable=False)  # user, assistant
    content = Column(Text, nullable=False)
    type = Column(String(50), default="message")  # message, clarification, report, thinking
    
    # 使用 quote=True 或直接定義 name 避免關鍵字衝突
    meta_data = Column("metadata", JSON, default={})
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # 關聯
    conversation = relationship("AgentConversation", back_populates="messages")
