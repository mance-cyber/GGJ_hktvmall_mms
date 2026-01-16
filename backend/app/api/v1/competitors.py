# =============================================
# 競品監測 API
# =============================================

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.database import get_db
from app.models.competitor import Competitor, CompetitorProduct, PriceSnapshot, PriceAlert
from app.schemas.competitor import (
    CompetitorCreate,
    CompetitorUpdate,
    CompetitorResponse,
    CompetitorListResponse,
    CompetitorProductCreate,
    CompetitorProductUpdate,
    CompetitorProductBulkCreate,
    CompetitorProductResponse,
    CompetitorProductListResponse,
    PriceHistoryResponse,
    PriceSnapshotResponse,
    PriceAlertResponse,
    PriceAlertListResponse,
    ScrapeTaskResponse,
)

router = APIRouter()
alerts_router = APIRouter()


# =============================================
# 競爭對手 CRUD
# =============================================

@router.get("", response_model=CompetitorListResponse)
async def list_competitors(
    db: AsyncSession = Depends(get_db),
    is_active: Optional[bool] = None,
):
    """列出所有競爭對手"""
    # 使用子查詢避免 N+1 問題
    # 統計每個競爭對手的商品數量和最後爬取時間
    product_stats_subquery = (
        select(
            CompetitorProduct.competitor_id,
            func.count(CompetitorProduct.id).label("product_count"),
            func.max(CompetitorProduct.last_scraped_at).label("last_scraped_at"),
        )
        .group_by(CompetitorProduct.competitor_id)
        .subquery()
    )

    # 主查詢：左連接統計子查詢
    query = (
        select(
            Competitor,
            func.coalesce(product_stats_subquery.c.product_count, 0).label("product_count"),
            product_stats_subquery.c.last_scraped_at,
        )
        .outerjoin(
            product_stats_subquery,
            Competitor.id == product_stats_subquery.c.competitor_id
        )
    )

    if is_active is not None:
        query = query.where(Competitor.is_active == is_active)
    query = query.order_by(Competitor.created_at.desc())

    result = await db.execute(query)
    rows = result.all()

    # 構建響應（單次查詢，無 N+1）
    data = [
        CompetitorResponse(
            id=row.Competitor.id,
            name=row.Competitor.name,
            platform=row.Competitor.platform,
            base_url=row.Competitor.base_url,
            notes=row.Competitor.notes,
            is_active=row.Competitor.is_active,
            created_at=row.Competitor.created_at,
            updated_at=row.Competitor.updated_at,
            product_count=row.product_count,
            last_scraped_at=row.last_scraped_at,
        )
        for row in rows
    ]

    return CompetitorListResponse(data=data, total=len(data))


@router.post("", response_model=CompetitorResponse, status_code=201)
async def create_competitor(
    competitor_in: CompetitorCreate,
    db: AsyncSession = Depends(get_db),
):
    """新增競爭對手"""
    competitor = Competitor(**competitor_in.model_dump())
    db.add(competitor)
    await db.flush()
    await db.refresh(competitor)

    return CompetitorResponse(
        id=competitor.id,
        name=competitor.name,
        platform=competitor.platform,
        base_url=competitor.base_url,
        notes=competitor.notes,
        is_active=competitor.is_active,
        created_at=competitor.created_at,
        updated_at=competitor.updated_at,
        product_count=0,
        last_scraped_at=None,
    )


@router.get("/{competitor_id}", response_model=CompetitorResponse)
async def get_competitor(
    competitor_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """獲取單個競爭對手"""
    result = await db.execute(
        select(Competitor).where(Competitor.id == competitor_id)
    )
    competitor = result.scalar_one_or_none()
    if not competitor:
        raise HTTPException(status_code=404, detail="競爭對手不存在")

    # 獲取商品數量
    count_result = await db.execute(
        select(func.count(CompetitorProduct.id)).where(
            CompetitorProduct.competitor_id == competitor_id
        )
    )
    product_count = count_result.scalar() or 0

    return CompetitorResponse(
        id=competitor.id,
        name=competitor.name,
        platform=competitor.platform,
        base_url=competitor.base_url,
        notes=competitor.notes,
        is_active=competitor.is_active,
        created_at=competitor.created_at,
        updated_at=competitor.updated_at,
        product_count=product_count,
        last_scraped_at=None,
    )


@router.patch("/{competitor_id}", response_model=CompetitorResponse)
async def update_competitor(
    competitor_id: UUID,
    competitor_in: CompetitorUpdate,
    db: AsyncSession = Depends(get_db),
):
    """更新競爭對手"""
    result = await db.execute(
        select(Competitor).where(Competitor.id == competitor_id)
    )
    competitor = result.scalar_one_or_none()
    if not competitor:
        raise HTTPException(status_code=404, detail="競爭對手不存在")

    update_data = competitor_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(competitor, field, value)

    await db.flush()
    await db.refresh(competitor)

    return CompetitorResponse(
        id=competitor.id,
        name=competitor.name,
        platform=competitor.platform,
        base_url=competitor.base_url,
        notes=competitor.notes,
        is_active=competitor.is_active,
        created_at=competitor.created_at,
        updated_at=competitor.updated_at,
        product_count=0,
        last_scraped_at=None,
    )


@router.delete("/{competitor_id}", status_code=204)
async def delete_competitor(
    competitor_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """刪除競爭對手"""
    result = await db.execute(
        select(Competitor).where(Competitor.id == competitor_id)
    )
    competitor = result.scalar_one_or_none()
    if not competitor:
        raise HTTPException(status_code=404, detail="競爭對手不存在")

    await db.delete(competitor)


# =============================================
# 競品商品
# =============================================

@router.get("/{competitor_id}/products", response_model=CompetitorProductListResponse)
async def list_competitor_products(
    competitor_id: UUID,
    db: AsyncSession = Depends(get_db),
    page: int = Query(default=1, ge=1, le=1000, description="頁碼（最大 1000）"),
    limit: int = Query(default=20, ge=1, le=100, description="每頁數量（最大 100）"),
    search: Optional[str] = Query(default=None, max_length=100, description="搜索關鍵字（最大 100 字符）"),
):
    """列出競品商品"""
    # 確認競爭對手存在
    result = await db.execute(
        select(Competitor).where(Competitor.id == competitor_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="競爭對手不存在")

    # 構建查詢
    query = select(CompetitorProduct).where(
        CompetitorProduct.competitor_id == competitor_id
    )
    if search:
        query = query.where(CompetitorProduct.name.ilike(f"%{search}%"))

    # 計算總數
    count_query = select(func.count()).select_from(query.subquery())
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0

    # 分頁
    query = query.order_by(CompetitorProduct.created_at.desc())
    query = query.offset((page - 1) * limit).limit(limit)

    result = await db.execute(query)
    products = result.scalars().all()

    # 獲取最新價格
    data = []
    for product in products:
        # 獲取最新兩個價格快照
        price_query = select(PriceSnapshot).where(
            PriceSnapshot.competitor_product_id == product.id
        ).order_by(PriceSnapshot.scraped_at.desc()).limit(2)
        price_result = await db.execute(price_query)
        snapshots = price_result.scalars().all()

        current_price = snapshots[0].price if snapshots else None
        previous_price = snapshots[1].price if len(snapshots) > 1 else None
        stock_status = snapshots[0].stock_status if snapshots else None

        price_change = None
        if current_price and previous_price:
            price_change = round((current_price - previous_price) / previous_price * 100, 2)

        data.append(CompetitorProductResponse(
            id=product.id,
            competitor_id=product.competitor_id,
            name=product.name,
            url=product.url,
            sku=product.sku,
            category=product.category,
            image_url=product.image_url,
            is_active=product.is_active,
            last_scraped_at=product.last_scraped_at,
            current_price=current_price,
            previous_price=previous_price,
            price_change=price_change,
            stock_status=stock_status,
            created_at=product.created_at,
        ))

    return CompetitorProductListResponse(
        data=data,
        total=total,
        page=page,
        limit=limit,
    )


@router.post("/{competitor_id}/products", response_model=ScrapeTaskResponse, status_code=201)
async def add_competitor_product(
    competitor_id: UUID,
    product_in: CompetitorProductCreate,
    db: AsyncSession = Depends(get_db),
):
    """新增競品商品並開始爬取"""
    # 確認競爭對手存在
    result = await db.execute(
        select(Competitor).where(Competitor.id == competitor_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="競爭對手不存在")

    # 檢查 URL 是否已存在
    existing = await db.execute(
        select(CompetitorProduct).where(CompetitorProduct.url == product_in.url)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="此 URL 已被監測")

    # 創建商品
    product = CompetitorProduct(
        competitor_id=competitor_id,
        url=product_in.url,
        name=product_in.name or "待爬取",
        category=product_in.category,
    )
    db.add(product)
    await db.flush()

    # TODO: 觸發 Celery 爬取任務
    # task = scrape_single_product.delay(str(product.id))

    return ScrapeTaskResponse(
        task_id="pending",
        message="已加入監測，正在爬取數據..."
    )


@router.post("/{competitor_id}/products/bulk", response_model=ScrapeTaskResponse, status_code=201)
async def bulk_add_products(
    competitor_id: UUID,
    bulk_data: CompetitorProductBulkCreate,
    db: AsyncSession = Depends(get_db),
):
    """批量新增競品商品"""
    # 確認競爭對手存在
    result = await db.execute(
        select(Competitor).where(Competitor.id == competitor_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="競爭對手不存在")

    added_count = 0
    skipped_count = 0

    for product_in in bulk_data.products:
        # 檢查 URL 是否已存在
        existing = await db.execute(
            select(CompetitorProduct).where(CompetitorProduct.url == product_in.url)
        )
        if existing.scalar_one_or_none():
            skipped_count += 1
            continue

        # 創建商品
        product = CompetitorProduct(
            competitor_id=competitor_id,
            url=product_in.url,
            name=product_in.name or "待爬取",
            category=product_in.category,
        )
        db.add(product)
        added_count += 1

    await db.flush()

    return ScrapeTaskResponse(
        task_id="batch-import",
        message=f"成功新增 {added_count} 個商品，跳過 {skipped_count} 個重複 URL"
    )


@router.get("/products/{product_id}", response_model=CompetitorProductResponse)
async def get_product(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """獲取單個競品商品詳情"""
    result = await db.execute(
        select(CompetitorProduct).where(CompetitorProduct.id == product_id)
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")

    # 獲取最新兩個價格快照
    price_query = select(PriceSnapshot).where(
        PriceSnapshot.competitor_product_id == product.id
    ).order_by(PriceSnapshot.scraped_at.desc()).limit(2)
    price_result = await db.execute(price_query)
    snapshots = price_result.scalars().all()

    current_price = snapshots[0].price if snapshots else None
    previous_price = snapshots[1].price if len(snapshots) > 1 else None
    stock_status = snapshots[0].stock_status if snapshots else None

    price_change = None
    if current_price and previous_price:
        price_change = round((current_price - previous_price) / previous_price * 100, 2)

    return CompetitorProductResponse(
        id=product.id,
        competitor_id=product.competitor_id,
        name=product.name,
        url=product.url,
        sku=product.sku,
        category=product.category,
        image_url=product.image_url,
        is_active=product.is_active,
        last_scraped_at=product.last_scraped_at,
        current_price=current_price,
        previous_price=previous_price,
        price_change=price_change,
        stock_status=stock_status,
        created_at=product.created_at,
    )


@router.patch("/products/{product_id}", response_model=CompetitorProductResponse)
async def update_product(
    product_id: UUID,
    product_in: CompetitorProductUpdate,
    db: AsyncSession = Depends(get_db),
):
    """更新競品商品"""
    result = await db.execute(
        select(CompetitorProduct).where(CompetitorProduct.id == product_id)
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")

    # 如果更新 URL，檢查是否重複
    if product_in.url and product_in.url != product.url:
        existing = await db.execute(
            select(CompetitorProduct).where(
                CompetitorProduct.url == product_in.url,
                CompetitorProduct.id != product_id
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="此 URL 已被其他商品使用")

    update_data = product_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)

    await db.flush()
    await db.refresh(product)

    return CompetitorProductResponse(
        id=product.id,
        competitor_id=product.competitor_id,
        name=product.name,
        url=product.url,
        sku=product.sku,
        category=product.category,
        image_url=product.image_url,
        is_active=product.is_active,
        last_scraped_at=product.last_scraped_at,
        current_price=None,
        previous_price=None,
        price_change=None,
        stock_status=None,
        created_at=product.created_at,
    )


@router.delete("/products/{product_id}", status_code=204)
async def delete_product(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """刪除競品商品"""
    result = await db.execute(
        select(CompetitorProduct).where(CompetitorProduct.id == product_id)
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")

    await db.delete(product)


@router.get("/products/{product_id}/history", response_model=PriceHistoryResponse)
async def get_price_history(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
    days: int = Query(default=30, ge=1, le=365),
):
    """獲取價格歷史"""
    from datetime import datetime, timedelta

    # 獲取商品
    result = await db.execute(
        select(CompetitorProduct).where(CompetitorProduct.id == product_id)
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")

    # 獲取價格歷史
    since = datetime.utcnow() - timedelta(days=days)
    history_query = select(PriceSnapshot).where(
        PriceSnapshot.competitor_product_id == product_id,
        PriceSnapshot.scraped_at >= since
    ).order_by(PriceSnapshot.scraped_at.desc())

    history_result = await db.execute(history_query)
    snapshots = history_result.scalars().all()

    return PriceHistoryResponse(
        product=CompetitorProductResponse(
            id=product.id,
            competitor_id=product.competitor_id,
            name=product.name,
            url=product.url,
            sku=product.sku,
            category=product.category,
            image_url=product.image_url,
            is_active=product.is_active,
            last_scraped_at=product.last_scraped_at,
            current_price=None,
            previous_price=None,
            price_change=None,
            stock_status=None,
            created_at=product.created_at,
        ),
        history=[
            PriceSnapshotResponse(
                id=s.id,
                price=s.price,
                original_price=s.original_price,
                discount_percent=s.discount_percent,
                stock_status=s.stock_status,
                rating=s.rating,
                review_count=s.review_count,
                scraped_at=s.scraped_at,
            )
            for s in snapshots
        ]
    )


@router.post("/{competitor_id}/scrape", response_model=ScrapeTaskResponse, status_code=202)
async def trigger_scrape(
    competitor_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """手動觸發爬取"""
    # 確認競爭對手存在
    result = await db.execute(
        select(Competitor).where(Competitor.id == competitor_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="競爭對手不存在")

    # TODO: 觸發 Celery 爬取任務
    # task = scrape_competitor.delay(str(competitor_id))

    return ScrapeTaskResponse(
        task_id="pending",
        message="爬取任務已啟動"
    )


# =============================================
# 警報
# =============================================

@alerts_router.get("", response_model=PriceAlertListResponse)
async def list_alerts(
    db: AsyncSession = Depends(get_db),
    is_read: Optional[bool] = Query(default=None, description="是否已讀"),
    alert_type: Optional[str] = Query(default=None, max_length=50, description="警報類型"),
    limit: int = Query(default=50, ge=1, le=200, description="返回數量（最大 200）"),
):
    """獲取價格警報"""
    query = select(PriceAlert).options(
        selectinload(PriceAlert.product).selectinload(CompetitorProduct.competitor)
    )

    if is_read is not None:
        query = query.where(PriceAlert.is_read == is_read)
    if alert_type:
        query = query.where(PriceAlert.alert_type == alert_type)

    query = query.order_by(PriceAlert.created_at.desc()).limit(limit)

    result = await db.execute(query)
    alerts = result.scalars().all()

    # 計算未讀數
    unread_query = select(func.count(PriceAlert.id)).where(PriceAlert.is_read == False)
    unread_result = await db.execute(unread_query)
    unread_count = unread_result.scalar() or 0

    return PriceAlertListResponse(
        data=[
            PriceAlertResponse(
                id=alert.id,
                product_name=alert.product.name if alert.product else "未知",
                competitor_name=alert.product.competitor.name if alert.product and alert.product.competitor else "未知",
                alert_type=alert.alert_type,
                old_value=alert.old_value,
                new_value=alert.new_value,
                change_percent=alert.change_percent,
                is_read=alert.is_read,
                created_at=alert.created_at,
            )
            for alert in alerts
        ],
        unread_count=unread_count,
    )


@alerts_router.put("/{alert_id}/read")
async def mark_alert_read(
    alert_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """標記警報為已讀"""
    result = await db.execute(
        select(PriceAlert).where(PriceAlert.id == alert_id)
    )
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="警報不存在")

    alert.is_read = True
    await db.flush()

    return {"message": "已標記為已讀"}
