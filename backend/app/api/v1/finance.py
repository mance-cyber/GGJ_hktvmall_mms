from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.models.database import get_db
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
