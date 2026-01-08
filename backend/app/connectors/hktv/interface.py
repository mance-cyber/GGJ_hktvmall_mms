# =============================================
# HKTVmall 連接器接口
# =============================================

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class HKTVProduct:
    """HKTVmall 商品"""
    product_id: str
    sku: str
    name: str
    price: float
    stock: int
    status: str
    images: List[str]
    attributes: Dict[str, Any]


@dataclass
class HKTVOrder:
    """HKTVmall 訂單"""
    order_id: str
    order_number: str
    status: str
    total_amount: float
    items: List[Dict[str, Any]]
    customer_info: Dict[str, Any]
    shipping_info: Dict[str, Any]
    order_date: str


class HKTVConnectorInterface(ABC):
    """HKTVmall 連接器抽象接口"""

    @abstractmethod
    async def get_products(self, page: int = 1, limit: int = 50) -> List[HKTVProduct]:
        """獲取商品列表"""
        pass

    @abstractmethod
    async def get_product(self, product_id: str) -> Optional[HKTVProduct]:
        """獲取單個商品"""
        pass

    @abstractmethod
    async def update_product(self, product_id: str, data: Dict[str, Any]) -> bool:
        """更新商品"""
        pass

    @abstractmethod
    async def get_orders(
        self,
        status: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        page: int = 1,
        limit: int = 50,
    ) -> List[HKTVOrder]:
        """獲取訂單列表"""
        pass

    @abstractmethod
    async def get_order(self, order_id: str) -> Optional[HKTVOrder]:
        """獲取單個訂單"""
        pass

    @abstractmethod
    async def update_inventory(self, sku: str, quantity: int) -> bool:
        """更新庫存"""
        pass
