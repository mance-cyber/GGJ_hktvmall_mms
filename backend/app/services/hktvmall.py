import httpx
from typing import Dict, List, Optional, Union, Any
import logging
import asyncio
from app.config import settings

logger = logging.getLogger(__name__)

class HKTVMallMockClient:
    """
    Mock Client for testing without real API tokens
    Simulates API responses
    """
    def __init__(self, *args, **kwargs):
        self.base_url = "https://mock.api/v2"
        self.store_code = "MOCK_STORE"
        logger.info("Initialized HKTVmall Mock Client")

    async def get_product_details(self, sku_codes: Union[str, List[str]]) -> Dict:
        await asyncio.sleep(0.5) # Simulate network latency
        if isinstance(sku_codes, str):
            sku_codes = [sku_codes]
        
        products = []
        for sku in sku_codes:
            products.append({
                "skuCode": sku,
                "price": 580.0,
                "promotionPrice": 550.0,
                "stock": 20,
                "stockStatus": "Active",
                "nameEn": f"Mock Product {sku}",
                "nameCh": f"模擬商品 {sku}"
            })
            
        return {
            "returnCode": "0000",
            "returnMsg": "Success",
            "data": products
        }

    async def get_product_details_batch(self, sku_codes: List[str]) -> Dict:
        return await self.get_product_details(sku_codes)

    async def update_price(self, sku_code: str, price: float, promotion_price: float = None):
        await asyncio.sleep(0.5)
        logger.info(f"MOCK: Updated price for {sku_code} to {price}")
        return {
            "returnCode": "0000",
            "returnMsg": "Update Success",
            "data": {
                "updated": 1,
                "skuCode": sku_code
            }
        }

    async def get_stock(self, sku_codes: Union[str, List[str]]):
        await asyncio.sleep(0.3)
        return {
            "returnCode": "0000",
            "data": [
                {"skuCode": sku, "inventory": 100, "status": "Active"} 
                for sku in (sku_codes if isinstance(sku_codes, list) else [sku_codes])
            ]
        }

    async def update_stock(self, sku_code: str, quantity: int, stock_status: str = "Active"):
        await asyncio.sleep(0.5)
        logger.info(f"MOCK: Updated stock for {sku_code} to {quantity}")
        return {
            "returnCode": "0000",
            "returnMsg": "Update Success"
        }

    async def get_orders(self, start_date: str, end_date: str, status: str = None):
        await asyncio.sleep(0.8)
        return {
            "returnCode": "0000",
            "data": [
                {
                    "orderNumber": "ORD-2024-001",
                    "orderDate": start_date,
                    "orderStatus": status or "Processing",
                    "totalAmount": 1280.0
                }
            ]
        }


class HKTVMallClient:
    """
    HKTVmall MMS Open API Client
    Based on MMS Open API v2.19
    """
    
    def __init__(self, access_token: str = None, store_code: str = None):
        self.base_url = settings.hktv_api_base_url or "https://merchant-oapi.shoalter.com/oapi/api"
        self.access_token = access_token or settings.hktv_access_token
        self.store_code = store_code or settings.hktv_store_code
        
        if not self.access_token:
            logger.warning("HKTVmall access token is not set. API calls will fail.")

    @property
    def headers(self):
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "x-auth-token": self.access_token
        }

    async def _request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None) -> Dict:
        """Internal request helper"""
        url = f"{self.base_url}{endpoint}"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    json=data,
                    params=params,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"HKTVmall API Error: {e.response.text}")
                try:
                    err_json = e.response.json()
                    err_msg = err_json.get('message', e.response.text)
                except:
                    err_msg = e.response.text
                raise Exception(f"HKTVmall API Error: {e.response.status_code} - {err_msg}")
            except Exception as e:
                logger.error(f"HKTVmall Request Failed: {str(e)}")
                raise

    # ==========================================
    # Product Management
    # ==========================================

    async def get_product_details(self, sku_codes: Union[str, List[str]]) -> Dict:
        """
        Get product details by SKU(s)
        Accepts single string or list of strings
        """
        if isinstance(sku_codes, str):
            sku_codes = [sku_codes]
            
        return await self._request(
            "POST", 
            "/product/hktv/products/queryByProductCode",
            data={"storeCode": self.store_code, "skuCodes": sku_codes}
        )
        
    # Alias for batch operations
    async def get_product_details_batch(self, sku_codes: List[str]) -> Dict:
        return await self.get_product_details(sku_codes)

    async def update_price(self, sku_code: str, price: float, promotion_price: float = None):
        """Batch update product price"""
        payload = {
            "storeCode": self.store_code,
            "skuPriceList": [
                {
                    "skuCode": sku_code,
                    "price": price,
                    "promotionPrice": promotion_price
                }
            ]
        }
        return await self._request("POST", "/product/hktv/batch/edit/price", data=payload)

    # ==========================================
    # Inventory Management
    # ==========================================

    async def get_stock(self, sku_codes: Union[str, List[str]]):
        """Get stock details"""
        if isinstance(sku_codes, str):
            sku_codes = [sku_codes]
            
        return await self._request(
            "POST",
            "/inventory/stock/details",
            data={"storeCode": self.store_code, "skuCodes": sku_codes}
        )

    async def update_stock(self, sku_code: str, quantity: int, stock_status: str = "Active"):
        """
        Update stock quantity
        stock_status: 'Active' or 'OutOfStock'
        """
        payload = {
            "storeCode": self.store_code,
            "skuStockList": [
                {
                    "skuCode": sku_code,
                    "quantity": quantity,
                    "stockStatus": stock_status
                }
            ]
        }
        return await self._request("POST", "/inventory/stock", data=payload)

    # ==========================================
    # Order Management
    # ==========================================

    async def get_orders(self, start_date: str, end_date: str, status: str = None):
        """
        Get orders
        Dates in YYYY-MM-DD format
        """
        payload = {
            "storeCode": self.store_code,
            "orderDateFrom": start_date,
            "orderDateTo": end_date
        }
        if status:
            payload["orderStatus"] = status
            
        return await self._request("POST", "/order/orders", data=payload)

