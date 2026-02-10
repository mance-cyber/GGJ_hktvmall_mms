from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from datetime import datetime, timedelta
from decimal import Decimal

from app.models.finance import Settlement, SettlementItem
from app.schemas.finance import ProfitSummary

class FinanceService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_settlements(self, limit: int = 10) -> List[Settlement]:
        """獲取結算單列表"""
        query = select(Settlement).order_by(Settlement.settlement_date.desc()).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_profit_summary(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> ProfitSummary:
        """計算利潤摘要"""
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()
            
        # 簡單計算：加總此期間內的所有 Settlement
        query = select(
            func.sum(Settlement.total_sales_amount).label("revenue"),
            func.sum(Settlement.total_commission).label("commission"),
            func.sum(Settlement.net_settlement_amount).label("profit")
        ).where(
            Settlement.settlement_date >= start_date,
            Settlement.settlement_date <= end_date
        )
        
        result = await self.db.execute(query)
        row = result.one_or_none()
        
        revenue = row.revenue or Decimal(0)
        commission = row.commission or Decimal(0)
        profit = row.profit or Decimal(0)
        
        margin = 0.0
        if revenue > 0:
            margin = float(profit / revenue) * 100
            
        return ProfitSummary(
            total_revenue=revenue,
            total_commission=commission,
            total_profit=profit,
            profit_margin=margin,
            period_start=start_date,
            period_end=end_date
        )

