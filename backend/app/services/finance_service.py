from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from datetime import datetime, timedelta
import random
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

    async def sync_mock_data(self):
        """生成模擬結算數據 (測試用)"""
        # 檢查是否已有數據
        existing = await self.db.execute(select(Settlement))
        if existing.scalars().first():
            return "Already has data"
            
        # 生成過去 3 個月的結算單 (每月 2 次)
        base_date = datetime.now()
        
        for i in range(6):
            date = base_date - timedelta(days=15 * i)
            statement_no = f"S{date.strftime('%Y%m%d')}"
            
            # 隨機金額
            sales = Decimal(random.randint(50000, 150000))
            commission_rate = Decimal(0.15) # 15% 佣金
            commission = sales * commission_rate
            shipping = Decimal(random.randint(1000, 5000))
            net = sales - commission - shipping
            
            settlement = Settlement(
                statement_no=statement_no,
                cycle_start=date - timedelta(days=14),
                cycle_end=date,
                settlement_date=date + timedelta(days=3),
                total_sales_amount=sales,
                total_commission=commission,
                total_shipping_fee=shipping,
                net_settlement_amount=net,
                status="Paid"
            )
            self.db.add(settlement)
            
            # 生成明細 items
            for j in range(5):
                item_price = Decimal(random.randint(100, 500))
                qty = random.randint(1, 10)
                item_comm = item_price * qty * commission_rate
                
                item = SettlementItem(
                    order_number=f"ORD-{date.strftime('%Y%m')}-{j:04d}",
                    sku=f"SKU-{random.randint(100, 999)}",
                    product_name=f"測試產品 {j}",
                    quantity=qty,
                    item_price=item_price,
                    commission_rate=commission_rate * 100,
                    commission_amount=item_comm,
                    transaction_date=date - timedelta(days=random.randint(1, 10)),
                    settlement=settlement
                )
                self.db.add(item)
                
        await self.db.commit()
        return "Mock data created"
