from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_
from typing import Dict, Any, List
from datetime import datetime, timedelta

from app.models.order import Order
from app.models.inbox import Conversation, Message
from app.models.pricing import PriceProposal
from app.models.finance import Settlement
from app.models.promotion import PromotionProposal
from app.models.notification import PriceAlert

class AnalyticsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_dashboard_summary(self) -> Dict[str, Any]:
        """獲取儀表板總覽數據"""
        
        # 1. 訂單統計 (待出貨)
        # 假設 status 'Pending' 或 'To Ship' 為待處理
        pending_orders_query = select(func.count(Order.id)).where(
            Order.status.in_(["Pending", "Processing", "To Ship"])
        )
        pending_orders = await self.db.scalar(pending_orders_query) or 0
        
        # 2. 客服統計 (未讀/待回覆)
        # 這裡簡化邏輯：假設 status 為 'Open' 的對話
        unread_msgs_query = select(func.count(Conversation.id)).where(
            Conversation.status == "Open"
        )
        unread_msgs = await self.db.scalar(unread_msgs_query) or 0
        
        # 3. 待辦事項 (Pending Actions)
        pending_prices_query = select(func.count(PriceProposal.id)).where(
            PriceProposal.status == "pending"
        )
        pending_prices = await self.db.scalar(pending_prices_query) or 0
        
        pending_promos_query = select(func.count(PromotionProposal.id)).where(
            PromotionProposal.status == "pending"
        )
        pending_promos = await self.db.scalar(pending_promos_query) or 0
        
        unread_alerts_query = select(func.count(PriceAlert.id)).where(
            PriceAlert.is_read == False
        )
        unread_alerts = await self.db.scalar(unread_alerts_query) or 0
        
        # 4. 財務快照 (本月)
        now = datetime.now()
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        finance_query = select(
            func.sum(Settlement.total_sales_amount).label("revenue"),
            func.sum(Settlement.net_settlement_amount).label("profit")
        ).where(
            Settlement.settlement_date >= start_of_month
        )
        finance_result = await self.db.execute(finance_query)
        finance_row = finance_result.one_or_none()
        
        revenue = finance_row.revenue or 0
        profit = finance_row.profit or 0
        
        # 5. 最近活動 (Recent Activity Feed)
        # 簡單撈取最新的 5 筆訂單
        recent_orders_query = select(Order).order_by(desc(Order.order_date)).limit(5)
        recent_orders_res = await self.db.execute(recent_orders_query)
        recent_orders = recent_orders_res.scalars().all()
        
        recent_activity = []
        for o in recent_orders:
            recent_activity.append({
                "type": "order",
                "title": f"新訂單 #{o.order_number}",
                "desc": f"金額: ${o.total_amount}",
                "time": o.order_date
            })
            
        return {
            "stats": {
                "orders_to_ship": pending_orders,
                "unread_messages": unread_msgs,
                "pending_price_reviews": pending_prices,
                "pending_promotion_reviews": pending_promos,
                "unread_alerts": unread_alerts,
                "monthly_revenue": revenue,
                "monthly_profit": profit
            },
            "recent_activity": recent_activity
        }
