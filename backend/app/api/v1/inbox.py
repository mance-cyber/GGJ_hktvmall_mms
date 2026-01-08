from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from app.models.database import get_db
from app.services.inbox_service import InboxService
from app.schemas.inbox import ConversationResponse, MessageResponse, MessageCreate

router = APIRouter()

@router.post("/sync")
async def sync_inbox(db: AsyncSession = Depends(get_db)):
    service = InboxService(db)
    count = await service.sync_conversations()
    return {"status": "success", "synced_count": count}

@router.get("/conversations", response_model=List[ConversationResponse])
async def get_conversations(db: AsyncSession = Depends(get_db)):
    service = InboxService(db)
    return await service.get_conversations()

@router.get("/conversations/{id}/messages", response_model=List[MessageResponse])
async def get_messages(id: UUID, db: AsyncSession = Depends(get_db)):
    service = InboxService(db)
    return await service.get_messages(id)

@router.post("/conversations/{id}/messages")
async def send_message(id: UUID, msg: MessageCreate, db: AsyncSession = Depends(get_db)):
    service = InboxService(db)
    return await service.send_message(id, msg.content, msg.is_draft)
