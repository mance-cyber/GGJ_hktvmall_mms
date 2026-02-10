# =============================================
# 商品管理 API
# =============================================

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query
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
