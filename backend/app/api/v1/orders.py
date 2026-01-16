from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import get_db
from app.services.order_service import OrderService
from app.schemas.order import OrderListResponse

router = APIRouter()


@router.post("/sync")
async def sync_orders(
    days: int = Query(default=7, ge=1, le=365, description="同步天數（1-365）"),
    db: AsyncSession = Depends(get_db),
):
    """同步 HKTVmall 訂單"""
    service = OrderService(db)
    count = await service.sync_orders(days)
    return {"status": "success", "synced_count": count}


@router.get("/", response_model=OrderListResponse)
async def get_orders(
    page: int = Query(default=1, ge=1, le=1000, description="頁碼（最大 1000）"),
    limit: int = Query(default=20, ge=1, le=100, description="每頁數量（最大 100）"),
    status: Optional[str] = Query(default=None, max_length=50, description="訂單狀態"),
    db: AsyncSession = Depends(get_db),
):
    """獲取訂單列表"""
    service = OrderService(db)
    result = await service.get_orders(page, limit, status)
    return result
