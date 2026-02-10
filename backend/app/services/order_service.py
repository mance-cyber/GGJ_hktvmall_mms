# =============================================
# 訂單服務
# =============================================

from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload

from app.models.order import Order, OrderItem, OrderStatus
from app.services.hktvmall import HKTVMallClient
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class OrderService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    def _get_client(self) -> HKTVMallClient:
        """獲取 HKTVmall API 客戶端"""
        if not settings.hktv_access_token or not settings.hktv_store_code:
            raise RuntimeError("HKTVmall API 尚未配置")
        return HKTVMallClient()

    async def sync_orders(self, days: int = 7):
        """同步最近 N 天的訂單"""
        client = self._get_client()
        
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        try:
            resp = await client.get_orders(start_date, end_date)
            
            if resp.get("returnCode") != "0000":
                logger.error(f"Failed to sync orders: {resp}")
                return 0
                
            orders_data = resp.get("data", [])
            synced_count = 0
            
            for order_data in orders_data:
                await self._upsert_order(order_data)
                synced_count += 1
                
            await self.db.commit()
            return synced_count

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Sync orders exception: {e}", exc_info=True)
            raise

    async def _upsert_order(self, data: dict):
        """更新或插入訂單"""
        order_number = data.get("orderNumber")
        
        # Check existing
        result = await self.db.execute(select(Order).where(Order.order_number == order_number))
        order = result.scalar_one_or_none()
        
        # Parse Dates
        try:
            order_date = datetime.strptime(data.get("orderDate"), "%Y-%m-%d %H:%M:%S")
        except (ValueError, TypeError) as e:
            logger.debug(f"無法解析 orderDate: {data.get('orderDate')}, 使用當前時間")
            order_date = datetime.now()  # Fallback

        ship_by = None
        if data.get("shipByDate"):
            try:
                ship_by = datetime.strptime(data.get("shipByDate"), "%Y-%m-%d %H:%M:%S")
            except (ValueError, TypeError) as e:
                logger.debug(f"無法解析 shipByDate: {data.get('shipByDate')}")

        if not order:
            order = Order(
                order_number=order_number,
                order_date=order_date,
                status=data.get("orderStatus", OrderStatus.PENDING),
                hktv_status=data.get("orderStatus"),
                total_amount=data.get("totalAmount"),
                delivery_mode=data.get("deliveryMode"),
                customer_region=data.get("customerRegion"),
                ship_by_date=ship_by
            )
            self.db.add(order)
            await self.db.flush() # Get ID
        else:
            # Update fields
            order.status = data.get("orderStatus", order.status)
            order.hktv_status = data.get("orderStatus")
            order.updated_at = datetime.utcnow()
            
        # Handle Items (Simplest way: delete all and recreate, or check one by one)
        # For sync, delete and recreate is safer to ensure consistency if item details changed
        # BUT `delete-orphan` on relationship might handle it if we clear the list.
        # However, accessing `order.items` requires eager load if not already loaded.
        # Since we just fetched `order` (lazy), `order.items` might be issue in async.
        
        # We will manually delete existing items
        from sqlalchemy import delete
        await self.db.execute(delete(OrderItem).where(OrderItem.order_id == order.id))
        
        # Add items
        items_data = data.get("items", [])
        for item in items_data:
            order_item = OrderItem(
                order_id=order.id,
                sku_code=item.get("skuCode"),
                product_name=item.get("name") or item.get("nameEn"),
                quantity=item.get("quantity", 1),
                unit_price=item.get("price"),
                subtotal=item.get("price", 0) * item.get("quantity", 1)
            )
            self.db.add(order_item)

    async def get_orders(self, page: int = 1, limit: int = 20, status: str = None):
        """查詢本地訂單"""
        query = select(Order).options(selectinload(Order.items))
        
        if status and status != 'all':
            query = query.where(Order.status == status)
            
        query = query.order_by(desc(Order.order_date))
        
        # Pagination
        total = await self.db.scalar(select(func.count()).select_from(query.subquery()))
        # Wait, count on subquery is complex. simpler:
        # total = await self.db.scalar(select(func.count(Order.id)).where(...))
        
        # Simplified count for now (ignoring filter for speed in writing)
        # Proper count:
        from sqlalchemy import func
        count_query = select(func.count(Order.id))
        if status and status != 'all':
            count_query = count_query.where(Order.status == status)
        total = await self.db.scalar(count_query) or 0
        
        query = query.offset((page - 1) * limit).limit(limit)
        result = await self.db.execute(query)
        orders = result.scalars().all()
        
        return {
            "data": orders,
            "total": total,
            "page": page,
            "limit": limit
        }
