# =============================================
# 商品管理 API
# =============================================

from typing import Optional, Literal
from uuid import UUID
from decimal import Decimal
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import get_db
from app.models.product import Product
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductListResponse,
)
from app.core.exceptions import NotFoundError, DuplicateError

router = APIRouter()


@router.get("", response_model=ProductListResponse)
async def list_products(
    db: AsyncSession = Depends(get_db),
    page: int = Query(default=1, ge=1, le=1000, description="頁碼（最大 1000）"),
    limit: int = Query(default=20, ge=1, le=100, description="每頁數量（最大 100）"),
    search: Optional[str] = Query(default=None, max_length=100, description="搜索關鍵字（最大 100 字符）"),
    status: Optional[str] = Query(default=None, max_length=50),
    category: Optional[str] = Query(default=None, max_length=100),
):
    """列出所有商品"""
    query = select(Product)

    if search:
        query = query.where(
            Product.name.ilike(f"%{search}%") | Product.sku.ilike(f"%{search}%")
        )
    if status:
        query = query.where(Product.status == status)
    if category:
        query = query.where(Product.category == category)

    # 計算總數
    count_query = select(func.count()).select_from(query.subquery())
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0

    # 分頁
    query = query.order_by(Product.created_at.desc())
    query = query.offset((page - 1) * limit).limit(limit)

    result = await db.execute(query)
    products = result.scalars().all()

    return ProductListResponse(
        data=[ProductResponse.model_validate(p) for p in products],
        total=total,
        page=page,
        limit=limit,
    )


@router.post("", response_model=ProductResponse, status_code=201)
async def create_product(
    product_in: ProductCreate,
    db: AsyncSession = Depends(get_db),
):
    """創建商品"""
    # 檢查 SKU 是否已存在
    existing = await db.execute(
        select(Product).where(Product.sku == product_in.sku)
    )
    if existing.scalar_one_or_none():
        raise DuplicateError(resource="商品", field="SKU")

    product = Product(**product_in.model_dump())
    db.add(product)
    await db.flush()
    await db.refresh(product)

    return ProductResponse.model_validate(product)


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """獲取單個商品"""
    result = await db.execute(
        select(Product).where(Product.id == product_id)
    )
    product = result.scalar_one_or_none()
    if not product:
        raise NotFoundError(resource="商品")

    return ProductResponse.model_validate(product)


@router.patch("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: UUID,
    product_in: ProductUpdate,
    db: AsyncSession = Depends(get_db),
):
    """更新商品"""
    result = await db.execute(
        select(Product).where(Product.id == product_id)
    )
    product = result.scalar_one_or_none()
    if not product:
        raise NotFoundError(resource="商品")

    update_data = product_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)

    await db.flush()
    await db.refresh(product)

    return ProductResponse.model_validate(product)


@router.delete("/{product_id}", status_code=204)
async def delete_product(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """刪除商品"""
    result = await db.execute(
        select(Product).where(Product.id == product_id)
    )
    product = result.scalar_one_or_none()
    if not product:
        raise NotFoundError(resource="商品")

    await db.delete(product)

# =============================================
# SKU 利潤排行榜 - P0-4
# =============================================

from decimal import Decimal
from typing import List, Literal
from pydantic import BaseModel


class ProductProfitabilityItem(BaseModel):
    """SKU 利潤數據項"""
    id: str
    sku: str
    name: str
    name_zh: Optional[str] = None
    price: Optional[Decimal] = None
    cost: Optional[Decimal] = None
    profit_amount: Optional[Decimal] = None  # 利潤額 = price - cost
    profit_margin: Optional[float] = None  # 利潤率 = (price - cost) / cost * 100
    category: Optional[str] = None
    status: Optional[str] = None


class ProductProfitabilityResponse(BaseModel):
    """利潤排行榜響應"""
    data: List[ProductProfitabilityItem]
    total: int
    page: int
    limit: int
    sort_by: str
    avg_profit_margin: Optional[float] = None  # 平均利潤率


@router.get("/profitability-ranking", response_model=ProductProfitabilityResponse)
async def get_profitability_ranking(
    db: AsyncSession = Depends(get_db),
    page: int = Query(default=1, ge=1, le=1000, description="頁碼"),
    limit: int = Query(default=20, ge=1, le=100, description="每頁數量"),
    sort_by: Literal["profit_amount", "profit_margin"] = Query(
        default="profit_margin",
        description="排序方式：profit_amount=利潤額，profit_margin=利潤率"
    ),
    category: Optional[str] = Query(default=None, description="類別篩選"),
    min_profit_margin: Optional[float] = Query(default=None, ge=-100, le=1000, description="最低利潤率（%）"),
):
    """
    SKU 利潤排行榜 - 真實數據驅動選品
    
    返回所有商品的利潤數據，支持按利潤額或利潤率排序。
    只顯示有價格和成本數據的商品。
    
    **商業用途**：
    - 識別高利潤商品，優先推廣
    - 發現低利潤商品，考慮調價或下架
    - 選品決策：優先引入高利潤率商品
    """
    # 基礎查詢：只查詢有價格和成本數據的商品
    query = select(Product).where(
        Product.price.is_not(None),
        Product.cost.is_not(None),
        Product.price > 0,
        Product.cost > 0,
    )
    
    # 類別篩選
    if category:
        query = query.where(Product.category == category)
    
    # 執行查詢
    result = await db.execute(query)
    products = result.scalars().all()
    
    # 計算利潤數據
    profit_data = []
    for p in products:
        profit_amount = p.price - p.cost if (p.price and p.cost) else None
        profit_margin = float((p.price - p.cost) / p.cost * 100) if (p.price and p.cost and p.cost > 0) else None
        
        # 利潤率篩選
        if min_profit_margin is not None and (profit_margin is None or profit_margin < min_profit_margin):
            continue
        
        profit_data.append({
            "product": p,
            "profit_amount": profit_amount,
            "profit_margin": profit_margin,
        })
    
    # 排序
    if sort_by == "profit_amount":
        profit_data.sort(key=lambda x: x["profit_amount"] or Decimal("0"), reverse=True)
    else:  # profit_margin
        profit_data.sort(key=lambda x: x["profit_margin"] or 0, reverse=True)
    
    # 計算平均利潤率
    valid_margins = [item["profit_margin"] for item in profit_data if item["profit_margin"] is not None]
    avg_profit_margin = sum(valid_margins) / len(valid_margins) if valid_margins else None
    
    # 分頁
    total = len(profit_data)
    start = (page - 1) * limit
    end = start + limit
    paginated_data = profit_data[start:end]
    
    # 構建響應
    items = []
    for item in paginated_data:
        p = item["product"]
        items.append(ProductProfitabilityItem(
            id=str(p.id),
            sku=p.sku,
            name=p.name,
            name_zh=p.name_zh,
            price=p.price,
            cost=p.cost,
            profit_amount=item["profit_amount"],
            profit_margin=item["profit_margin"],
            category=p.category,
            status=p.status,
        ))
    
    return ProductProfitabilityResponse(
        data=items,
        total=total,
        page=page,
        limit=limit,
        sort_by=sort_by,
        avg_profit_margin=avg_profit_margin,
    )


# =============================================
# 監測優先級管理 - 分級監測策略
# =============================================


class MonitoringPriorityUpdate(BaseModel):
    """更新監測優先級請求"""
    priority: Literal["A", "B", "C"] = Field(
        ...,
        description="監測優先級：A=核心商品(3次/天), B=一般商品(2次/天), C=低優先(1次/天)"
    )


class MonitoringPriorityStats(BaseModel):
    """監測優先級統計"""
    a_count: int = Field(description="A級商品數量")
    b_count: int = Field(description="B級商品數量")
    c_count: int = Field(description="C級商品數量")
    total: int = Field(description="總商品數量")
    daily_scrapes_estimate: int = Field(description="預估每日爬取次數")


@router.patch("/{product_id}/monitoring-priority", response_model=ProductResponse)
async def update_monitoring_priority(
    product_id: UUID,
    priority_update: MonitoringPriorityUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    更新商品的監測優先級
    
    **優先級說明**：
    - **A級（核心商品）**: 每天爬取 3 次（08:00, 14:00, 20:00）
      - 適用於：高利潤率商品（>50%）、競爭激烈的商品
    - **B級（一般商品）**: 每天爬取 2 次（08:00, 20:00）
      - 適用於：中等利潤率商品（20-50%）
    - **C級（低優先）**: 每天爬取 1 次（08:00）
      - 適用於：低利潤率商品（<20%）、無競品的商品
    """
    result = await db.execute(
        select(Product).where(Product.id == product_id)
    )
    product = result.scalar_one_or_none()
    if not product:
        raise NotFoundError(resource="商品")
    
    product.monitoring_priority = priority_update.priority
    await db.flush()
    await db.refresh(product)
    
    return ProductResponse.model_validate(product)


@router.get("/monitoring-priority/stats", response_model=MonitoringPriorityStats)
async def get_monitoring_priority_stats(
    db: AsyncSession = Depends(get_db),
):
    """
    獲取監測優先級統計
    
    返回各優先級的商品數量和預估每日爬取次數
    """
    # 統計各優先級的商品數量
    a_count_result = await db.execute(
        select(func.count())
        .select_from(Product)
        .where(Product.monitoring_priority == "A")
    )
    a_count = a_count_result.scalar() or 0
    
    b_count_result = await db.execute(
        select(func.count())
        .select_from(Product)
        .where(Product.monitoring_priority == "B")
    )
    b_count = b_count_result.scalar() or 0
    
    c_count_result = await db.execute(
        select(func.count())
        .select_from(Product)
        .where(Product.monitoring_priority == "C")
    )
    c_count = c_count_result.scalar() or 0
    
    total = a_count + b_count + c_count
    
    # 估算每日爬取次數
    # A級：3次，B級：2次，C級：1次
    daily_scrapes = (a_count * 3) + (b_count * 2) + (c_count * 1)
    
    return MonitoringPriorityStats(
        a_count=a_count,
        b_count=b_count,
        c_count=c_count,
        total=total,
        daily_scrapes_estimate=daily_scrapes,
    )


@router.post("/monitoring-priority/auto-classify")
async def trigger_auto_classify(
    db: AsyncSession = Depends(get_db),
):
    """
    手動觸發自動分類監測優先級
    
    分類標準：
    - **A級**: 利潤率 > 50% 且有競品映射
    - **B級**: 利潤率 20-50%
    - **C級**: 利潤率 < 20% 或無競品映射
    
    **建議**: 在批量導入商品或修改成本價格後執行
    """
    from app.tasks.scrape_tasks import auto_classify_monitoring_priority
    
    # 觸發 Celery 任務
    task = auto_classify_monitoring_priority.delay()
    
    return {
        "success": True,
        "task_id": task.id,
        "message": "自動分類任務已啟動，請稍後查看結果"
    }
