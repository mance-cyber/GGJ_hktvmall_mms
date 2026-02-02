from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from typing import List

from app.models.database import get_db
from app.models.finance import Settlement, SettlementItem
from app.services.finance_service import FinanceService
from app.schemas.finance import SettlementResponse, ProfitSummary

router = APIRouter()

@router.post("/sync-mock")
async def sync_mock_data(db: AsyncSession = Depends(get_db)):
    """生成測試用的財務數據"""
    service = FinanceService(db)
    result = await service.sync_mock_data()
    return {"status": "success", "message": result}

@router.get("/settlements", response_model=List[SettlementResponse])
async def get_settlements(limit: int = 10, db: AsyncSession = Depends(get_db)):
    """獲取最新的結算單"""
    service = FinanceService(db)
    return await service.get_settlements(limit)

@router.get("/profit-summary", response_model=ProfitSummary)
async def get_profit_summary(db: AsyncSession = Depends(get_db)):
    """獲取利潤統計摘要"""
    service = FinanceService(db)
    return await service.get_profit_summary()


@router.delete("/cleanup/mock-data")
async def cleanup_finance_data(
    db: AsyncSession = Depends(get_db),
    confirm: bool = Query(default=False, description="確認刪除"),
):
    """清理所有結算資料"""
    if not confirm:
        settlement_count = (await db.execute(select(func.count(Settlement.id)))).scalar() or 0
        item_count = (await db.execute(select(func.count(SettlementItem.id)))).scalar() or 0
        return {
            "preview": True,
            "settlements_to_delete": settlement_count,
            "items_to_delete": item_count,
            "message": "加上 ?confirm=true 確認刪除"
        }

    await db.execute(delete(SettlementItem))
    await db.execute(delete(Settlement))
    await db.commit()

    return {"message": "所有結算資料已清除"}
