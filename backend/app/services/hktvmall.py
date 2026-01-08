import httpx
from typing import Dict, List, Optional, Union, Any
import logging
import asyncio
from datetime import datetime, timedelta
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
        """Mock Order Response"""
        await asyncio.sleep(0.8)
        
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        orders = []
        if start_date <= today_str <= end_date:
            orders = [
                {
                    "orderNumber": f"ORD-{today_str.replace('-','')}-001",
                    "orderDate": f"{today_str} 10:30:00",
                    "orderStatus": "Pending",
                    "totalAmount": 1280.0,
                    "deliveryMode": "HD",
                    "shipByDate": f"{today_str} 18:00:00",
                    "customerRegion": "HK_ISLAND",
                    "items": [
                        {"skuCode": "SKU001", "quantity": 2, "price": 500.0, "name": "Mock Product A"},
                        {"skuCode": "SKU002", "quantity": 1, "price": 280.0, "name": "Mock Product B"}
                    ]
                },
                {
                    "orderNumber": f"ORD-{today_str.replace('-','')}-002",
                    "orderDate": f"{today_str} 14:15:00",
                    "orderStatus": "Pending",
                    "totalAmount": 550.0,
                    "deliveryMode": "O2O",
                    "shipByDate": f"{today_str} 18:00:00",
                    "customerRegion": "KLN",
                    "items": [
                        {"skuCode": "SKU003", "quantity": 1, "price": 550.0, "name": "Mock Product C"}
                    ]
                }
            ]
            
        if start_date < today_str:
             orders.append({
                "orderNumber": "ORD-HIST-001",
                "orderDate": f"{start_date} 09:00:00",
                "orderStatus": "Shipped",
                "totalAmount": 880.0,
                "deliveryMode": "HD",
                "shipByDate": f"{start_date} 18:00:00",
                "customerRegion": "NT",
                "items": [
                    {"skuCode": "SKU005", "quantity": 1, "price": 880.0, "name": "Mock Product E"}
                ]
            })

        return {
            "returnCode": "0000",
            "data": orders
        }

    async def get_conversations(self, page: int = 1, page_size: int = 20):
        """Mock Conversations"""
        await asyncio.sleep(0.5)
        return {
            "returnCode": "0000",
            "data": [
                {
                    "topicId": "TOPIC-001",
                    "subject": "關於訂單 ORD-2024-001",
                    "customerName": "Alice Chan",
                    "lastMessage": "請問幾時出貨？",
                    "lastMessageAt": "2024-05-20 14:30:00",
                    "status": "Open"
                },
                {
                    "topicId": "TOPIC-002",
                    "subject": "產品查詢: SKU001",
                    "customerName": "Bob Lee",
                    "lastMessage": "有無現貨？",
                    "lastMessageAt": "2024-05-20 10:00:00",
                    "status": "Open"
                }
            ]
        }
        
    async def get_messages(self, topic_id: str):
        """Mock Messages"""
        await asyncio.sleep(0.3)
        return {
            "returnCode": "0000",
            "data": [
                {
                    "messageId": "MSG-001",
                    "content": "你好，我想問下 SKU001 有無現貨？",
                    "sender": "customer",
                    "sentAt": "2024-05-20 09:55:00"
                },
                {
                    "messageId": "MSG-002",
                    "content": "有無現貨？",
                    "sender": "customer",
                    "sentAt": "2024-05-20 10:00:00"
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

    async def get_product_details(self, sku_codes: Union[str, List[str]]) -> Dict:
        if isinstance(sku_codes, str):
            sku_codes = [sku_codes]
        return await self._request("POST", "/product/hktv/products/queryByProductCode", data={"storeCode": self.store_code, "skuCodes": sku_codes})
        
    async def get_product_details_batch(self, sku_codes: List[str]) -> Dict:
        return await self.get_product_details(sku_codes)

    async def update_price(self, sku_code: str, price: float, promotion_price: float = None):
        payload = {
            "storeCode": self.store_code,
            "skuPriceList": [{"skuCode": sku_code, "price": price, "promotionPrice": promotion_price}]
        }
        return await self._request("POST", "/product/hktv/batch/edit/price", data=payload)

    async def get_stock(self, sku_codes: Union[str, List[str]]):
        if isinstance(sku_codes, str):
            sku_codes = [sku_codes]
        return await self._request("POST", "/inventory/stock/details", data={"storeCode": self.store_code, "skuCodes": sku_codes})

    async def update_stock(self, sku_code: str, quantity: int, stock_status: str = "Active"):
        payload = {
            "storeCode": self.store_code,
            "skuStockList": [{"skuCode": sku_code, "quantity": quantity, "stockStatus": stock_status}]
        }
        return await self._request("POST", "/inventory/stock", data=payload)

    async def get_orders(self, start_date: str, end_date: str, status: str = None):
        payload = {"storeCode": self.store_code, "orderDateFrom": start_date, "orderDateTo": end_date}
        if status: payload["orderStatus"] = status
        return await self._request("POST", "/order/orders", data=payload)

    async def get_conversations(self, page: int = 1, page_size: int = 20):
        # Placeholder for real API
        # Need to verify endpoint in documentation
        return {"returnCode": "0000", "data": []}

    async def get_messages(self, topic_id: str):
        # Placeholder for real API
        return {"returnCode": "0000", "data": []}
