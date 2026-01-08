from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from app.models.database import get_db
from app.services.promotion_service import PromotionService
from app.schemas.promotion import PromotionResponse, PromotionStats

router = APIRouter()

@router.get("/suggestions", response_model=List[PromotionResponse])
async def get_suggestions(db: AsyncSession = Depends(get_db)):
    """獲取 AI 推薦的促銷活動"""
    service = PromotionService(db)
    return await service.get_proposals("pending")

@router.post("/generate")
async def generate_suggestions(db: AsyncSession = Depends(get_db)):
    """觸發 AI 生成建議"""
    service = PromotionService(db)
    count = await service.generate_suggestions()
    return {"status": "success", "generated_count": count}

@router.get("/stats", response_model=PromotionStats)
async def get_stats(db: AsyncSession = Depends(get_db)):
    service = PromotionService(db)
    return await service.get_stats()

@router.post("/{id}/approve")
async def approve_proposal(id: UUID, db: AsyncSession = Depends(get_db)):
    service = PromotionService(db)
    try:
        await service.approve_proposal(id)
        return {"status": "success"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/{id}/reject")
async def reject_proposal(id: UUID, db: AsyncSession = Depends(get_db)):
    service = PromotionService(db)
    try:
        await service.reject_proposal(id)
        return {"status": "success"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
