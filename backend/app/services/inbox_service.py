# =============================================
# 客服收件箱服務
# =============================================

from datetime import datetime
from typing import List, Optional, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload

from app.models.inbox import Conversation, Message
from app.services.hktvmall import HKTVMallClient, HKTVMallMockClient
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class InboxService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    def _get_client(self) -> Union[HKTVMallClient, HKTVMallMockClient]:
        """獲取 HKTVmall API 客戶端（真實或 Mock）"""
        if settings.hktv_access_token and settings.hktv_access_token != "mock_token":
            return HKTVMallClient()
        return HKTVMallMockClient()

    async def sync_conversations(self):
        """同步對話列表"""
        client = self._get_client()
        try:
            resp = await client.get_conversations()
            data = resp.get("data", [])
            
            for item in data:
                topic_id = item.get("topicId")
                
                # Check existing
                result = await self.db.execute(select(Conversation).where(Conversation.hktv_topic_id == topic_id))
                conv = result.scalar_one_or_none()
                
                last_msg_at = datetime.now()
                try:
                    last_msg_at = datetime.strptime(item.get("lastMessageAt"), "%Y-%m-%d %H:%M:%S")
                except (ValueError, TypeError) as e:
                    logger.debug(f"無法解析 lastMessageAt: {item.get('lastMessageAt')}, 使用當前時間")

                if not conv:
                    conv = Conversation(
                        hktv_topic_id=topic_id,
                        customer_name=item.get("customerName"),
                        subject=item.get("subject"),
                        status=item.get("status", "open"),
                        last_message_at=last_msg_at
                    )
                    self.db.add(conv)
                else:
                    conv.last_message_at = last_msg_at
                    conv.status = item.get("status", "open")
            
            await self.db.commit()
            return len(data)
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Sync conversations failed: {e}", exc_info=True)
            return 0

    async def get_conversations(self):
        """獲取本地對話列表"""
        query = select(Conversation).order_by(desc(Conversation.last_message_at))
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_messages(self, conversation_id: str):
        """獲取對話訊息 (並同步)"""
        # 1. Get Conversation
        result = await self.db.execute(select(Conversation).where(Conversation.id == conversation_id))
        conv = result.scalar_one_or_none()
        if not conv:
            return []
            
        # 2. Sync from API
        client = self._get_client()
        try:
            resp = await client.get_messages(conv.hktv_topic_id)
            data = resp.get("data", [])
            
            for item in data:
                msg_id = item.get("messageId")
                # Check exist
                res = await self.db.execute(select(Message).where(Message.hktv_message_id == msg_id))
                if not res.scalar_one_or_none():
                    sent_at = datetime.now()
                    try:
                        sent_at = datetime.strptime(item.get("sentAt"), "%Y-%m-%d %H:%M:%S")
                    except (ValueError, TypeError) as e:
                        logger.debug(f"無法解析 sentAt: {item.get('sentAt')}, 使用當前時間")

                    msg = Message(
                        conversation_id=conv.id,
                        hktv_message_id=msg_id,
                        content=item.get("content"),
                        sender_type=item.get("sender"),
                        sent_at=sent_at
                    )
                    self.db.add(msg)
            await self.db.commit()
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Sync messages failed: {e}", exc_info=True)

        # 3. Return local messages
        query = select(Message).where(Message.conversation_id == conversation_id).order_by(Message.sent_at)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def send_message(self, conversation_id: str, content: str, is_draft: bool = False):
        """發送訊息 (或草稿)"""
        result = await self.db.execute(select(Conversation).where(Conversation.id == conversation_id))
        conv = result.scalar_one_or_none()
        if not conv:
            raise ValueError("Conversation not found")
            
        # If real send, call API (Skipped for Phase 3 Mock)
        
        msg = Message(
            conversation_id=conv.id,
            content=content,
            sender_type="merchant",
            is_draft=is_draft,
            sent_at=datetime.utcnow()
        )
        self.db.add(msg)
        await self.db.commit()
        await self.db.refresh(msg)
        return msg
