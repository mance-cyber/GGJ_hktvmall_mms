from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel

class MessageBase(BaseModel):
    content: str
    sender_type: str
    ai_generated: bool = False
    is_draft: bool = False

class MessageResponse(MessageBase):
    id: UUID
    hktv_message_id: Optional[str]
    sent_at: datetime
    
    class Config:
        from_attributes = True

class ConversationBase(BaseModel):
    hktv_topic_id: str
    customer_name: Optional[str]
    subject: Optional[str]
    status: str
    has_unread: bool

class ConversationResponse(ConversationBase):
    id: UUID
    last_message_at: datetime
    created_at: datetime
    last_message: Optional[MessageResponse] = None # Latest msg
    
    class Config:
        from_attributes = True

class MessageCreate(BaseModel):
    content: str
    is_draft: bool = False
