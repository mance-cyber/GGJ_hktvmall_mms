import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.database import get_db
from app.models.product import Product as OwnProduct
from app.services.hktvmall import HKTVMallClient

logger = logging.getLogger(__name__)

router = APIRouter()

# ==========================================
# Schemas
# ==========================================

class PriceUpdate(BaseModel):
    sku_code: str
    price: float
    promotion_price: Optional[float] = None

class StockUpdate(BaseModel):
    sku_code: str
    quantity: int
    stock_status: str = "Active"

class SyncResult(BaseModel):
    success: bool
    message: str
    updated_count: int = 0
    errors: List[str] = []

# ==========================================
# Helper
# ==========================================

def get_hktv_client():
    """Dependency: 獲取 HKTVmall API 客戶端，未配置則返回 503"""
    if not settings.hktv_access_token or not settings.hktv_store_code:
        raise HTTPException(
            status_code=503,
            detail="HKTVmall API 尚未配置，請在 .env 設定 HKTVMALL_ACCESS_TOKEN 和 HKTVMALL_STORE_CODE"
        )
    return HKTVMallClient()

# ==========================================
# Endpoints
# ==========================================

@router.get("/status")
async def check_connection(client = Depends(get_hktv_client)):
    """測試與 HKTVmall 的連接狀態"""
    try:
        return {
            "status": "configured",
            "store_code": client.store_code,
            "base_url": client.base_url,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/products/{sku}/price")
async def update_product_price(
    sku: str, 
    data: PriceUpdate, 
    client = Depends(get_hktv_client),
    db: AsyncSession = Depends(get_db)
):
    """更新單個商品價格 (同步到 HKTVmall)"""
    try:
        # 1. Update remote
        result = await client.update_price(
            sku_code=sku,
            price=data.price,
            promotion_price=data.promotion_price
        )
        
        # 2. Update local DB
        query = select(OwnProduct).where(OwnProduct.sku == sku)
        db_result = await db.execute(query)
        product = db_result.scalar_one_or_none()
        
        if product:
            product.price = data.price
            await db.commit()
            
        return {"success": True, "remote_response": result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Update failed: {str(e)}")

@router.post("/products/{sku}/stock")
async def update_product_stock(
    sku: str, 
    data: StockUpdate, 
    client = Depends(get_hktv_client),
    db: AsyncSession = Depends(get_db)
):
    """更新單個商品庫存 (同步到 HKTVmall)"""
    try:
        # 1. Update remote
        result = await client.update_stock(
            sku_code=sku, 
            quantity=data.quantity,
            stock_status=data.stock_status
        )
        
        # 2. Update local DB
        query = select(OwnProduct).where(OwnProduct.sku == sku)
        db_result = await db.execute(query)
        product = db_result.scalar_one_or_none()
        
        if product:
            product.stock_quantity = data.quantity
            await db.commit()
            
        return {"success": True, "remote_response": result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Update failed: {str(e)}")

@router.post("/sync/products")
async def sync_products_from_remote(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    client = Depends(get_hktv_client)
):
    """
    從 HKTVmall 同步所有已對應 SKU 的商品資訊 (價格/庫存) 到本地
    """
    # 1. Get all local products with SKU
    query = select(OwnProduct).where(OwnProduct.sku != None)
    result = await db.execute(query)
    local_products = result.scalars().all()
    
    if not local_products:
        return {"message": "No local products with SKU found to sync"}

    skus = [p.sku for p in local_products if p.sku]
    
    background_tasks.add_task(run_sync_task, skus, client, db)
    
    return {"message": f"已開始同步 {len(skus)} 個商品"}

async def run_sync_task(skus: List[str], client, db: AsyncSession):
    """後台執行同步邏輯"""
    chunk_size = 20
    updated_count = 0
    errors = []
    
    for i in range(0, len(skus), chunk_size):
        chunk = skus[i:i + chunk_size]
        try:
            response = await client.get_product_details_batch(chunk)
            
            # TODO: 解析真實 response 並更新 DB
            # 這裡需要一個獨立的 DB Session 管理邏輯，暫時略過寫入
            # 僅打印日誌
            logger.info(f"Synced chunk {i}: {response}")
            
        except Exception as e:
            errors.append(f"Chunk {i} failed: {str(e)}")
            
    logger.info(f"Sync completed. Updated: {updated_count}. Errors: {len(errors)}")

