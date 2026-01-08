from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.database import get_db
from app.services.order_service import OrderService
from app.schemas.order import OrderListResponse

router = APIRouter()

@router.post("/sync")
async def sync_orders(days: int = 7, db: AsyncSession = Depends(get_db)):
    service = OrderService(db)
    count = await service.sync_orders(days)
    return {"status": "success", "synced_count": count}

@router.get("/", response_model=OrderListResponse)
async def get_orders(
    page: int = 1, 
    limit: int = 20, 
    status: str = Query(None),
    db: AsyncSession = Depends(get_db)
):
    service = OrderService(db)
    result = await service.get_orders(page, limit, status)
    return result
