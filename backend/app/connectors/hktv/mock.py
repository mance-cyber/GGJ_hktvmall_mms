# =============================================
# HKTVmall Mock 連接器
# =============================================

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import random

from app.connectors.hktv.interface import (
    HKTVConnectorInterface,
    HKTVProduct,
    HKTVOrder,
)


class MockHKTVConnector(HKTVConnectorInterface):
    """HKTVmall Mock 連接器（開發/測試用）"""

    def __init__(self):
        # 模擬商品數據
        self._products = [
            HKTVProduct(
                product_id=f"PROD-{i:04d}",
                sku=f"SKU-{i:04d}",
                name=f"測試商品 {i}",
                price=round(random.uniform(50, 500), 2),
                stock=random.randint(0, 100),
                status="active" if random.random() > 0.2 else "inactive",
                images=[f"https://example.com/product-{i}.jpg"],
                attributes={"category": random.choice(["保健品", "美妝", "食品", "日用品"])},
            )
            for i in range(1, 21)
        ]

        # 模擬訂單數據
        self._orders = [
            HKTVOrder(
                order_id=f"ORD-{i:06d}",
                order_number=f"HK{datetime.now().strftime('%Y%m%d')}{i:04d}",
                status=random.choice(["pending", "confirmed", "shipped", "delivered"]),
                total_amount=round(random.uniform(100, 2000), 2),
                items=[
                    {
                        "sku": f"SKU-{random.randint(1, 20):04d}",
                        "name": f"商品 {random.randint(1, 20)}",
                        "quantity": random.randint(1, 3),
                        "unit_price": round(random.uniform(50, 300), 2),
                    }
                ],
                customer_info={
                    "name": f"客戶 {i}",
                    "phone": f"9{random.randint(1000, 9999)}{random.randint(1000, 9999)}",
                    "email": f"customer{i}@example.com",
                },
                shipping_info={
                    "address": f"香港某區某街 {i} 號",
                    "method": random.choice(["順豐", "自取", "送貨上門"]),
                },
                order_date=(datetime.now() - timedelta(days=random.randint(0, 30))).isoformat(),
            )
            for i in range(1, 11)
        ]

    async def get_products(self, page: int = 1, limit: int = 50) -> List[HKTVProduct]:
        """獲取商品列表"""
        start = (page - 1) * limit
        end = start + limit
        return self._products[start:end]

    async def get_product(self, product_id: str) -> Optional[HKTVProduct]:
        """獲取單個商品"""
        for product in self._products:
            if product.product_id == product_id:
                return product
        return None

    async def update_product(self, product_id: str, data: Dict[str, Any]) -> bool:
        """更新商品"""
        for i, product in enumerate(self._products):
            if product.product_id == product_id:
                # 更新商品屬性
                for key, value in data.items():
                    if hasattr(product, key):
                        setattr(self._products[i], key, value)
                return True
        return False

    async def get_orders(
        self,
        status: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        page: int = 1,
        limit: int = 50,
    ) -> List[HKTVOrder]:
        """獲取訂單列表"""
        orders = self._orders

        if status:
            orders = [o for o in orders if o.status == status]

        start = (page - 1) * limit
        end = start + limit
        return orders[start:end]

    async def get_order(self, order_id: str) -> Optional[HKTVOrder]:
        """獲取單個訂單"""
        for order in self._orders:
            if order.order_id == order_id:
                return order
        return None

    async def update_inventory(self, sku: str, quantity: int) -> bool:
        """更新庫存"""
        for i, product in enumerate(self._products):
            if product.sku == sku:
                self._products[i].stock = quantity
                return True
        return False


def get_hktv_connector() -> HKTVConnectorInterface:
    """獲取 HKTVmall 連接器（根據配置返回 Mock 或真實連接器）"""
    from app.config import get_settings
    settings = get_settings()

    if settings.hktv_connector_type == "mock":
        return MockHKTVConnector()
    else:
        # TODO: 實現真實的 MMS API 連接器
        return MockHKTVConnector()
