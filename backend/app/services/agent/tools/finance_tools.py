from typing import Dict, Any, List
from sqlalchemy import select, func, desc, text
from datetime import datetime, timedelta

from app.services.agent.tools.base import BaseTool, ToolResult
from app.models.finance import Settlement
from app.models.order import Order

class QuerySalesTool(BaseTool):
    name = "query_sales"
    description = "查詢銷售數據，支持按天/週/月聚合，可查詢營收(revenue)或利潤(profit)"
    parameters = {
        "metric": {
            "type": "string",
            "description": "指標類型: revenue (營收) 或 profit (利潤)",
            "required": True
        },
        "period": {
            "type": "string",
            "description": "時間範圍: last_7_days, last_30_days, this_month, last_month",
            "required": True
        }
    }

    async def execute(self, metric: str, period: str) -> ToolResult:
        # Determine date range
        now = datetime.now()
        start_date = now - timedelta(days=30)
        
        if period == "last_7_days":
            start_date = now - timedelta(days=7)
        elif period == "last_30_days":
            start_date = now - timedelta(days=30)
        elif period == "this_month":
            start_date = now.replace(day=1, hour=0, minute=0, second=0)
        elif period == "last_month":
            # First day of this month
            this_month_start = now.replace(day=1, hour=0, minute=0, second=0)
            # Last day of prev month
            last_month_end = this_month_start - timedelta(seconds=1)
            # First day of prev month
            start_date = last_month_end.replace(day=1, hour=0, minute=0, second=0)
            now = last_month_end

        # Query
        if metric == "revenue":
            query = select(
                func.sum(Settlement.total_sales_amount)
            ).where(
                Settlement.settlement_date >= start_date,
                Settlement.settlement_date <= now
            )
        else:
            query = select(
                func.sum(Settlement.net_settlement_amount)
            ).where(
                Settlement.settlement_date >= start_date,
                Settlement.settlement_date <= now
            )
            
        result = await self.db.execute(query)
        total = result.scalar() or 0
        
        return ToolResult(
            tool_name=self.name,
            success=True,
            data={
                "value": float(total),
                "currency": "HKD",
                "period": period,
                "metric": metric
            }
        )

class QueryTopProductsTool(BaseTool):
    name = "query_top_products"
    description = "查詢銷量最高或利潤最高的產品"
    parameters = {
        "by": {
            "type": "string",
            "description": "排序依據: sales (銷量), revenue (營收)",
            "required": True
        },
        "limit": {
            "type": "int",
            "description": "返回數量，默認 5",
            "required": False
        }
    }

    async def execute(self, by: str, limit: int = 5) -> ToolResult:
        # 由於 SettlementItem 才有具體產品銷售數據，我們查詢 SettlementItem
        from app.models.finance import SettlementItem
        
        if by == "sales":
            query = select(
                SettlementItem.product_name,
                func.sum(SettlementItem.quantity).label("total_qty")
            ).group_by(
                SettlementItem.product_name
            ).order_by(
                desc("total_qty")
            ).limit(limit)
            
            result = await self.db.execute(query)
            rows = result.all()
            
            data = [{"name": r.product_name, "value": r.total_qty} for r in rows]
            
        else: # revenue
            query = select(
                SettlementItem.product_name,
                func.sum(SettlementItem.item_price * SettlementItem.quantity).label("total_rev")
            ).group_by(
                SettlementItem.product_name
            ).order_by(
                desc("total_rev")
            ).limit(limit)
            
            result = await self.db.execute(query)
            rows = result.all()
            
            data = [{"name": r.product_name, "value": float(r.total_rev)} for r in rows]

        return ToolResult(
            tool_name=self.name,
            success=True,
            data={
                "items": data,
                "chart_type": "bar", # Hint for frontend
                "x_key": "name",
                "y_key": "value",
                "title": f"Top {limit} Products by {by}"
            }
        )
