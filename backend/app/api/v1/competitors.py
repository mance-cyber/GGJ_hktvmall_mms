# =============================================
# 競品監測 API
# =============================================

import logging
from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.database import get_db
from app.models.competitor import Competitor, CompetitorProduct, PriceSnapshot, PriceAlert
from app.connectors.hktv_scraper import HKTVUrlParser
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

logger = logging.getLogger(__name__)

router = APIRouter()
alerts_router = APIRouter()


def _normalize_if_hktv(url: str) -> str:
    """HKTVmall URL 標準化：移除追蹤參數，保留完整路徑"""
    if "hktvmall.com" in url.lower():
        try:
            return HKTVUrlParser.normalize_url(url)
        except Exception as e:
            logger.warning(f"URL 標準化失敗 {url}: {e}")
            return url
    return url


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
        .where(CompetitorProduct.is_active == True)
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

    # 獲取商品數量（只計 active）
    count_result = await db.execute(
        select(func.count(CompetitorProduct.id)).where(
            CompetitorProduct.competitor_id == competitor_id,
            CompetitorProduct.is_active == True,
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

    # 構建查詢（只顯示 active 商品）
    query = select(CompetitorProduct).where(
        CompetitorProduct.competitor_id == competitor_id,
        CompetitorProduct.is_active == True,
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

    # 標準化 URL
    normalized_url = _normalize_if_hktv(product_in.url)

    # 檢查 URL 是否已存在
    existing = await db.execute(
        select(CompetitorProduct).where(CompetitorProduct.url == normalized_url)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="此 URL 已被監測")

    # 自動提取 SKU
    sku = HKTVUrlParser.extract_sku(normalized_url)

    # 創建商品
    product = CompetitorProduct(
        competitor_id=competitor_id,
        url=normalized_url,
        name=product_in.name or "待爬取",
        sku=sku,
        category=product_in.category,
    )
    db.add(product)
    await db.flush()
    await db.commit()

    # 觸發 Celery 爬取任務
    from app.tasks.scrape_tasks import scrape_single_product
    task = scrape_single_product.delay(str(product.id))

    return ScrapeTaskResponse(
        task_id=task.id,
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
        # 標準化 URL
        normalized_url = _normalize_if_hktv(product_in.url)

        # 檢查 URL 是否已存在
        existing = await db.execute(
            select(CompetitorProduct).where(CompetitorProduct.url == normalized_url)
        )
        if existing.scalar_one_or_none():
            skipped_count += 1
            continue

        # 自動提取 SKU
        sku = HKTVUrlParser.extract_sku(normalized_url)

        # 創建商品
        product = CompetitorProduct(
            competitor_id=competitor_id,
            url=normalized_url,
            name=product_in.name or "待爬取",
            sku=sku,
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

    # 如果更新 URL，標準化並檢查是否重複
    if product_in.url and product_in.url != product.url:
        normalized_url = _normalize_if_hktv(product_in.url)
        existing = await db.execute(
            select(CompetitorProduct).where(
                CompetitorProduct.url == normalized_url,
                CompetitorProduct.id != product_id
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="此 URL 已被其他商品使用")
        product_in.url = normalized_url

    update_data = product_in.model_dump(exclude_unset=True)
    # 更新 URL 時同步提取 SKU
    if "url" in update_data:
        update_data["sku"] = HKTVUrlParser.extract_sku(update_data["url"])
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

    # 觸發 Celery 爬取任務
    from app.tasks.scrape_tasks import scrape_competitor
    task = scrape_competitor.delay(str(competitor_id))

    return ScrapeTaskResponse(
        task_id=task.id,
        message=f"爬取任務已啟動（Task ID: {task.id}）"
    )


# =============================================
# URL 修復
# =============================================

@router.post("/fix-urls")
async def fix_product_urls(
    db: AsyncSession = Depends(get_db),
    confirm: bool = Query(default=False, description="確認執行修復"),
):
    """
    掃描並修復不符合 HKTVmall 格式的商品 URL

    - confirm=false：預覽需修復的記錄
    - confirm=true：執行修復
    """
    # 找出所有 active HKTVmall 商品
    result = await db.execute(
        select(CompetitorProduct).where(
            CompetitorProduct.url.ilike("%hktvmall.com%"),
            CompetitorProduct.is_active == True,
        )
    )
    products = result.scalars().all()

    issues: List[dict] = []
    for product in products:
        url = product.url
        problems = []

        # 檢查 URL 是否包含 /p/H{SKU}
        if not HKTVUrlParser.is_product_url(url):
            problems.append("缺少 /p/H{SKU} 路徑")

        # 檢查是否有追蹤參數可清理
        normalized = HKTVUrlParser.normalize_url(url)
        if normalized != url and HKTVUrlParser.is_product_url(url):
            problems.append("含追蹤參數")

        # 檢查 SKU 是否已提取
        sku = HKTVUrlParser.extract_sku(url)
        if sku and product.sku != sku:
            problems.append(f"SKU 未同步（應為 {sku}）")

        if problems:
            issues.append({
                "id": str(product.id),
                "name": product.name,
                "current_url": url,
                "normalized_url": normalized if HKTVUrlParser.is_product_url(url) else None,
                "extracted_sku": sku,
                "problems": problems,
                "fixable": HKTVUrlParser.is_product_url(url),
            })

    if not confirm:
        fixable = [i for i in issues if i["fixable"]]
        unfixable = [i for i in issues if not i["fixable"]]
        return {
            "preview": True,
            "total_scanned": len(products),
            "total_issues": len(issues),
            "fixable": len(fixable),
            "unfixable": len(unfixable),
            "issues": issues,
            "message": "加上 ?confirm=true 執行修復（僅修復 fixable 記錄）",
        }

    # 執行修復
    fixed_count = 0
    for issue in issues:
        if not issue["fixable"]:
            continue

        result = await db.execute(
            select(CompetitorProduct).where(
                CompetitorProduct.id == issue["id"]
            )
        )
        product = result.scalar_one_or_none()
        if not product:
            continue

        if issue["normalized_url"]:
            product.url = issue["normalized_url"]
        if issue["extracted_sku"]:
            product.sku = issue["extracted_sku"]
        fixed_count += 1

    await db.flush()

    unfixable = [i for i in issues if not i["fixable"]]
    return {
        "preview": False,
        "fixed": fixed_count,
        "unfixable_count": len(unfixable),
        "unfixable": unfixable,
        "message": f"已修復 {fixed_count} 條記錄" + (
            f"，{len(unfixable)} 條無法自動修復（缺少有效 /p/H{{SKU}} 路徑）"
            if unfixable else ""
        ),
    }


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


# =============================================
# Competitor v2 — Comparison Dashboard API
# =============================================

from app.models.product import Product, ProductCompetitorMapping

comparison_router = APIRouter()


@comparison_router.get("/summary")
async def get_comparison_summary(
    db: AsyncSession = Depends(get_db),
):
    """Dashboard 頂部統計摘要"""
    from datetime import datetime, timezone, timedelta

    # Total competitors
    total_comp = await db.execute(
        select(func.count()).select_from(Competitor).where(Competitor.is_active == True)
    )
    total_competitors = total_comp.scalar() or 0

    # Total tracked competitor products
    total_tracked = await db.execute(
        select(func.count()).select_from(CompetitorProduct).where(CompetitorProduct.is_active == True)
    )
    total_tracked_products = total_tracked.scalar() or 0

    # Our products
    our_count = await db.execute(
        select(func.count()).select_from(Product).where(Product.status == "active")
    )
    our_products = our_count.scalar() or 0

    # Mapped competitor products (with mappings)
    mapped_count = await db.execute(
        select(func.count(func.distinct(ProductCompetitorMapping.competitor_product_id)))
    )
    mapped_competitors = mapped_count.scalar() or 0

    # Price alerts in last 24h
    cutoff_24h = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=24)
    alerts_count = await db.execute(
        select(func.count()).select_from(PriceAlert).where(PriceAlert.created_at >= cutoff_24h)
    )
    price_alerts_24h = alerts_count.scalar() or 0

    # We are cheapest percentage (among mapped products)
    # For each of our products that has mappings, check if our price is the lowest
    our_products_stmt = (
        select(Product.id, Product.price)
        .where(Product.status == "active", Product.price.isnot(None))
    )
    our_result = await db.execute(our_products_stmt)
    our_rows = our_result.all()

    cheapest_count = 0
    compared_count = 0
    total_diff_pct = 0.0

    for pid, our_price in our_rows:
        if not our_price or our_price <= 0:
            continue
        # Get latest competitor prices for this product
        comp_prices_stmt = (
            select(func.min(PriceSnapshot.price))
            .join(CompetitorProduct, PriceSnapshot.competitor_product_id == CompetitorProduct.id)
            .join(ProductCompetitorMapping, ProductCompetitorMapping.competitor_product_id == CompetitorProduct.id)
            .where(
                ProductCompetitorMapping.product_id == pid,
                PriceSnapshot.price.isnot(None),
                PriceSnapshot.price > 0,
            )
        )
        min_result = await db.execute(comp_prices_stmt)
        min_price = min_result.scalar()

        if min_price is not None:
            compared_count += 1
            if float(our_price) <= float(min_price):
                cheapest_count += 1
            diff_pct = (float(min_price) - float(our_price)) / float(our_price) * 100
            total_diff_pct += diff_pct

    we_are_cheapest_pct = round(cheapest_count / compared_count * 100) if compared_count > 0 else 0
    avg_price_diff_pct = round(total_diff_pct / compared_count, 1) if compared_count > 0 else 0

    # Last scan time
    last_scan_result = await db.execute(
        select(func.max(CompetitorProduct.last_scraped_at))
    )
    last_scan = last_scan_result.scalar()

    return {
        "total_competitors": total_competitors,
        "total_tracked_products": total_tracked_products,
        "our_products": our_products,
        "mapped_competitors": mapped_competitors,
        "price_alerts_24h": price_alerts_24h,
        "we_are_cheapest_pct": we_are_cheapest_pct,
        "avg_price_diff_pct": avg_price_diff_pct,
        "last_scan": last_scan.isoformat() if last_scan else None,
    }


@comparison_router.get("/products")
async def get_comparison_products(
    db: AsyncSession = Depends(get_db),
    scope: str = Query("mapped", description="mapped=自家競品, all=全部生鮮"),
):
    """
    商品比較視角：每件自家商品配上競品價格
    Optimised: 3 batch queries instead of N*M individual queries
    """
    from datetime import timedelta, datetime, timezone
    from sqlalchemy import func, over

    # ── 1. 所有 active 自家商品 ──────────────────────────────────────────
    our_result = await db.execute(
        select(Product)
        .where(Product.status == "active")
        .order_by(Product.category_tag, Product.name)
    )
    our_products = our_result.scalars().all()
    if not our_products:
        return {"items": []}

    product_ids = [p.id for p in our_products]
    product_map = {p.id: p for p in our_products}

    # ── 2. Batch: 所有競品 + mapping（1 query）───────────────────────────
    if scope == "mapped":
        comp_stmt = (
            select(
                CompetitorProduct,
                Competitor.name.label("comp_name"),
                Competitor.tier.label("comp_tier"),
                ProductCompetitorMapping.product_id.label("our_product_id"),
            )
            .join(ProductCompetitorMapping,
                  ProductCompetitorMapping.competitor_product_id == CompetitorProduct.id)
            .join(Competitor, CompetitorProduct.competitor_id == Competitor.id)
            .where(
                ProductCompetitorMapping.product_id.in_(product_ids),
                CompetitorProduct.is_active == True,
            )
        )
    else:
        category_tags = list({p.category_tag for p in our_products if p.category_tag})
        if not category_tags:
            return {"items": []}
        comp_stmt = (
            select(
                CompetitorProduct,
                Competitor.name.label("comp_name"),
                Competitor.tier.label("comp_tier"),
                # for 'all' scope, group by category_tag
                CompetitorProduct.category.label("our_product_id"),  # placeholder, fixed below
            )
            .join(Competitor, CompetitorProduct.competitor_id == Competitor.id)
            .where(
                CompetitorProduct.is_active == True,
                CompetitorProduct.category.in_(category_tags),
            )
        )

    comp_result = await db.execute(comp_stmt)
    comp_rows = comp_result.all()

    # Build: cp_id → row
    all_cp_ids = [row.CompetitorProduct.id for row in comp_rows]

    # ── 3. Batch: latest price per competitor product（1 subquery）────────
    if all_cp_ids:
        # Subquery: latest scraped_at per cp_id
        latest_subq = (
            select(
                PriceSnapshot.competitor_product_id,
                func.max(PriceSnapshot.scraped_at).label("max_scraped_at"),
            )
            .where(PriceSnapshot.competitor_product_id.in_(all_cp_ids))
            .group_by(PriceSnapshot.competitor_product_id)
            .subquery()
        )
        # Join back to get full row
        price_result = await db.execute(
            select(PriceSnapshot)
            .join(latest_subq, (PriceSnapshot.competitor_product_id == latest_subq.c.competitor_product_id)
                  & (PriceSnapshot.scraped_at == latest_subq.c.max_scraped_at))
        )
        latest_prices: dict = {ps.competitor_product_id: ps for ps in price_result.scalars().all()}

        # ── 4. Batch: price 7 days ago（1 subquery）───────────────────────
        week_ago = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=7)
        old_subq = (
            select(
                PriceSnapshot.competitor_product_id,
                func.max(PriceSnapshot.scraped_at).label("max_old_at"),
            )
            .where(
                PriceSnapshot.competitor_product_id.in_(all_cp_ids),
                PriceSnapshot.scraped_at <= week_ago,
            )
            .group_by(PriceSnapshot.competitor_product_id)
            .subquery()
        )
        old_result = await db.execute(
            select(PriceSnapshot.competitor_product_id, PriceSnapshot.price)
            .join(old_subq, (PriceSnapshot.competitor_product_id == old_subq.c.competitor_product_id)
                  & (PriceSnapshot.scraped_at == old_subq.c.max_old_at))
        )
        old_prices: dict = {row.competitor_product_id: row.price for row in old_result.all()}
    else:
        latest_prices = {}
        old_prices = {}

    # ── 5. Assemble per-product ──────────────────────────────────────────
    # Group comp_rows by our_product_id
    from collections import defaultdict
    product_competitors: dict = defaultdict(list)

    if scope == "mapped":
        for row in comp_rows:
            cp = row.CompetitorProduct
            latest = latest_prices.get(cp.id)
            old_price_val = old_prices.get(cp.id)

            price_change_7d = None
            if latest and latest.price and old_price_val and old_price_val > 0:
                price_change_7d = round(float((latest.price - old_price_val) / old_price_val * 100), 1)

            product_competitors[row.our_product_id].append({
                "competitor_name": row.comp_name,
                "competitor_tier": row.comp_tier,
                "product_name": cp.name,
                "price": float(latest.price) if latest and latest.price else None,
                "original_price": float(latest.original_price) if latest and latest.original_price else None,
                "unit_price_per_100g": float(latest.unit_price_per_100g) if latest and latest.unit_price_per_100g else None,
                "price_change_7d": price_change_7d,
                "stock_status": latest.stock_status if latest else None,
                "url": cp.url,
                "last_updated": latest.scraped_at.isoformat() if latest and latest.scraped_at else None,
            })
    else:
        # For 'all' scope: group by category_tag, then fan out to matching products
        category_competitors: dict = defaultdict(list)
        for row in comp_rows:
            cp = row.CompetitorProduct
            latest = latest_prices.get(cp.id)
            old_price_val = old_prices.get(cp.id)
            price_change_7d = None
            if latest and latest.price and old_price_val and old_price_val > 0:
                price_change_7d = round(float((latest.price - old_price_val) / old_price_val * 100), 1)
            category_competitors[cp.category].append({
                "competitor_name": row.comp_name,
                "competitor_tier": row.comp_tier,
                "product_name": cp.name,
                "price": float(latest.price) if latest and latest.price else None,
                "original_price": float(latest.original_price) if latest and latest.original_price else None,
                "unit_price_per_100g": float(latest.unit_price_per_100g) if latest and latest.unit_price_per_100g else None,
                "price_change_7d": price_change_7d,
                "stock_status": latest.stock_status if latest else None,
                "url": cp.url,
                "last_updated": latest.scraped_at.isoformat() if latest and latest.scraped_at else None,
            })
        for p in our_products:
            if p.category_tag:
                product_competitors[p.id] = category_competitors.get(p.category_tag, [])

    items = []
    for product in our_products:
        competitors = product_competitors.get(product.id, [])
        competitors.sort(key=lambda x: x["price"] or 99999)

        all_prices = [c["price"] for c in competitors if c["price"]]
        our_price = float(product.price) if product.price else None
        our_rank = 1
        if our_price and all_prices:
            our_rank = sum(1 for p in all_prices if p < our_price) + 1

        items.append({
            "product": {
                "id": str(product.id),
                "name": product.name,
                "sku": product.sku,
                "price": float(product.price) if product.price else None,
                "image_url": (product.images[0] if product.images else None),
                "category_tag": product.category_tag,
            },
            "competitors": competitors,
            "cheapest_competitor": competitors[0]["competitor_name"] if competitors and competitors[0]["price"] else None,
            "our_price_rank": our_rank,
            "total_competitors": len(competitors),
        })

    return {"items": items}


@comparison_router.get("/merchants")
async def get_comparison_merchants(
    db: AsyncSession = Depends(get_db),
):
    """
    商戶概覽視角：每間商戶嘅競品統計
    """
    stmt = (
        select(Competitor)
        .where(Competitor.is_active == True)
        .order_by(Competitor.tier, Competitor.name)
    )
    result = await db.execute(stmt)
    merchants = result.scalars().all()

    items = []
    for merchant in merchants:
        # Total products
        total_stmt = select(func.count()).select_from(CompetitorProduct).where(
            CompetitorProduct.competitor_id == merchant.id,
            CompetitorProduct.is_active == True,
        )
        total_result = await db.execute(total_stmt)
        total_products = total_result.scalar() or 0

        # Fresh products (not 'unknown' or 'processed')
        fresh_stmt = select(func.count()).select_from(CompetitorProduct).where(
            CompetitorProduct.competitor_id == merchant.id,
            CompetitorProduct.is_active == True,
            CompetitorProduct.product_type.in_(["fresh", "frozen"]),
        )
        fresh_result = await db.execute(fresh_stmt)
        fresh_products = fresh_result.scalar() or 0

        # Overlap products (with mappings to our products)
        overlap_stmt = (
            select(func.count(func.distinct(ProductCompetitorMapping.competitor_product_id)))
            .join(CompetitorProduct, ProductCompetitorMapping.competitor_product_id == CompetitorProduct.id)
            .where(CompetitorProduct.competitor_id == merchant.id)
        )
        overlap_result = await db.execute(overlap_stmt)
        overlap_products = overlap_result.scalar() or 0
        unique_products = total_products - overlap_products

        # Price comparison for overlapping products
        cheaper = 0
        same = 0
        expensive = 0
        total_diff = 0.0
        compared = 0

        if overlap_products > 0:
            mapping_stmt = (
                select(ProductCompetitorMapping, Product.price)
                .join(Product, ProductCompetitorMapping.product_id == Product.id)
                .join(CompetitorProduct, ProductCompetitorMapping.competitor_product_id == CompetitorProduct.id)
                .where(CompetitorProduct.competitor_id == merchant.id)
            )
            mapping_result = await db.execute(mapping_stmt)

            for mapping, our_price in mapping_result.all():
                if not our_price:
                    continue
                # Get latest competitor price
                cp_price_stmt = (
                    select(PriceSnapshot.price)
                    .where(PriceSnapshot.competitor_product_id == mapping.competitor_product_id)
                    .order_by(PriceSnapshot.scraped_at.desc())
                    .limit(1)
                )
                cp_result = await db.execute(cp_price_stmt)
                cp_price = cp_result.scalar()
                if not cp_price:
                    continue

                compared += 1
                diff = float(cp_price) - float(our_price)
                diff_pct = diff / float(our_price) * 100
                total_diff += diff_pct

                if abs(diff_pct) < 3:
                    same += 1
                elif diff < 0:
                    cheaper += 1  # competitor is cheaper
                else:
                    expensive += 1  # competitor is more expensive (we are cheaper)

        avg_diff = round(total_diff / compared, 1) if compared > 0 else 0

        # Recent price changes (last 7 days)
        from datetime import datetime, timezone, timedelta
        week_ago = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=7)
        changes_stmt = (
            select(PriceAlert, CompetitorProduct.name)
            .join(CompetitorProduct, PriceAlert.competitor_product_id == CompetitorProduct.id)
            .where(
                CompetitorProduct.competitor_id == merchant.id,
                PriceAlert.created_at >= week_ago,
            )
            .order_by(PriceAlert.created_at.desc())
            .limit(5)
        )
        changes_result = await db.execute(changes_stmt)
        recent_changes = [
            {
                "product_name": name,
                "change_type": alert.alert_type,
                "old_price": float(alert.old_value) if alert.old_value else None,
                "new_price": float(alert.new_value) if alert.new_value else None,
                "change_pct": float(alert.change_percent) if alert.change_percent else None,
                "date": alert.created_at.strftime("%Y-%m-%d"),
            }
            for alert, name in changes_result.all()
        ]

        items.append({
            "competitor": {
                "id": str(merchant.id),
                "name": merchant.name,
                "tier": merchant.tier,
                "store_code": merchant.store_code,
                "total_products": total_products,
                "fresh_products": fresh_products,
                "overlap_products": overlap_products,
                "unique_products": unique_products,
            },
            "price_comparison": {
                "cheaper_count": cheaper,
                "same_count": same,
                "expensive_count": expensive,
                "avg_price_diff_pct": avg_diff,
            },
            "recent_changes": recent_changes,
        })

    return {"items": items}



# ═══════════════════════════════════════════════
# Feature 3: Price History Chart API
# ═══════════════════════════════════════════════
@comparison_router.get("/products/{product_id}/price-history")
async def get_product_price_history(
    product_id: UUID,
    days: int = Query(30, ge=7, le=90),
    db: AsyncSession = Depends(get_db),
):
    from datetime import datetime, timezone, timedelta
    from collections import defaultdict

    since = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=days)
    our_result = await db.execute(select(Product).where(Product.id == product_id))
    product = our_result.scalar_one_or_none()
    if not product:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Product not found")

    cp_stmt = (
        select(CompetitorProduct, Competitor.name.label("comp_name"))
        .join(ProductCompetitorMapping, ProductCompetitorMapping.competitor_product_id == CompetitorProduct.id)
        .join(Competitor, CompetitorProduct.competitor_id == Competitor.id)
        .where(ProductCompetitorMapping.product_id == product_id, CompetitorProduct.is_active == True)
        .limit(8)
    )
    cp_rows = (await db.execute(cp_stmt)).all()
    cp_ids = [r.CompetitorProduct.id for r in cp_rows]

    snaps = []
    if cp_ids:
        snaps_result = await db.execute(
            select(PriceSnapshot)
            .where(PriceSnapshot.competitor_product_id.in_(cp_ids), PriceSnapshot.scraped_at >= since, PriceSnapshot.price.isnot(None))
            .order_by(PriceSnapshot.scraped_at)
        )
        snaps = snaps_result.scalars().all()

    series_map: dict = defaultdict(dict)
    for s in snaps:
        series_map[s.competitor_product_id][s.scraped_at.strftime("%Y-%m-%d")] = float(s.price)

    dates = [(since + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days + 1)]
    series = []
    for row in cp_rows:
        cp = row.CompetitorProduct
        daily = series_map.get(cp.id, {})
        filled, last_price = [], None
        for d in dates:
            if d in daily:
                last_price = daily[d]
            filled.append(last_price)
        series.append({"id": str(cp.id), "name": row.comp_name, "data": filled})

    return {
        "product": {"id": str(product.id), "name": product.name.replace("GOGOJAP-", ""), "price": float(product.price) if product.price else None},
        "dates": dates,
        "our_price": float(product.price) if product.price else None,
        "series": series,
    }


# ═══════════════════════════════════════════════
# Feature 5: Export CSV
# ═══════════════════════════════════════════════
@comparison_router.get("/export")
async def export_comparison(db: AsyncSession = Depends(get_db)):
    import csv, io
    from fastapi.responses import StreamingResponse
    from sqlalchemy import func as sqlfunc

    our_result = await db.execute(select(Product).where(Product.status == "active").order_by(Product.category_tag, Product.name))
    our_products = our_result.scalars().all()
    product_ids = [p.id for p in our_products]
    if not product_ids:
        return StreamingResponse(iter([""]), media_type="text/csv")

    comp_stmt = (
        select(CompetitorProduct, Competitor.name.label("comp_name"), ProductCompetitorMapping.product_id.label("our_product_id"))
        .join(ProductCompetitorMapping, ProductCompetitorMapping.competitor_product_id == CompetitorProduct.id)
        .join(Competitor, CompetitorProduct.competitor_id == Competitor.id)
        .where(ProductCompetitorMapping.product_id.in_(product_ids), CompetitorProduct.is_active == True)
    )
    comp_rows = (await db.execute(comp_stmt)).all()
    all_cp_ids = [r.CompetitorProduct.id for r in comp_rows]

    latest_prices = {}
    if all_cp_ids:
        lsq = select(PriceSnapshot.competitor_product_id, sqlfunc.max(PriceSnapshot.scraped_at).label("max_at")).where(PriceSnapshot.competitor_product_id.in_(all_cp_ids)).group_by(PriceSnapshot.competitor_product_id).subquery()
        pr = await db.execute(select(PriceSnapshot).join(lsq, (PriceSnapshot.competitor_product_id == lsq.c.competitor_product_id) & (PriceSnapshot.scraped_at == lsq.c.max_at)))
        latest_prices = {ps.competitor_product_id: ps for ps in pr.scalars().all()}

    from collections import defaultdict
    pcmap = defaultdict(list)
    for row in comp_rows:
        pcmap[row.our_product_id].append(row)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["分類", "商品名", "我哋售價", "最平競品", "最平競品價", "價差%", "排名", "競品總數", "比我平嘅數", "有貨數"])
    for product in our_products:
        rows = pcmap.get(product.id, [])
        comps = []
        for row in rows:
            latest = latest_prices.get(row.CompetitorProduct.id)
            if latest and latest.price:
                comps.append({"name": row.comp_name, "price": float(latest.price), "stock": latest.stock_status})
        comps.sort(key=lambda x: x["price"])
        our_price = float(product.price) if product.price else None
        cheapest = comps[0] if comps else None
        cheapest_price = cheapest["price"] if cheapest else None
        diff_pct = round((our_price - cheapest_price) / our_price * 100, 1) if our_price and cheapest_price else None
        rank = sum(1 for c in comps if c["price"] < (our_price or 99999)) + 1 if our_price else None
        writer.writerow([product.category_tag or "", product.name.replace("GOGOJAP-", ""), f"${our_price:.0f}" if our_price else "", cheapest["name"] if cheapest else "", f"${cheapest_price:.0f}" if cheapest_price else "", f"{diff_pct:+.1f}%" if diff_pct is not None else "", f"{rank}/{len(comps)}" if rank else "", len(comps), sum(1 for c in comps if c["price"] < (our_price or 99999)), sum(1 for c in comps if c.get("stock") == "in_stock")])

    output.seek(0)
    from datetime import datetime as dt
    fname = f"gogojap_competitors_{dt.now().strftime('%Y%m%d_%H%M')}.csv"
    return StreamingResponse(iter(["\ufeff" + output.read()]), media_type="text/csv; charset=utf-8", headers={"Content-Disposition": f'attachment; filename="{fname}"'})


# ═══════════════════════════════════════════════
# Feature 6: Pricing Suggestions (Rule Engine)
# ═══════════════════════════════════════════════
@comparison_router.get("/pricing-suggestions")
async def get_pricing_suggestions(db: AsyncSession = Depends(get_db)):
    from sqlalchemy import func as sqlfunc
    from collections import defaultdict

    our_result = await db.execute(select(Product).where(Product.status == "active"))
    our_products = our_result.scalars().all()
    product_ids = [p.id for p in our_products]
    if not product_ids:
        return {"suggestions": []}

    comp_stmt = (
        select(CompetitorProduct, ProductCompetitorMapping.product_id.label("our_product_id"))
        .join(ProductCompetitorMapping, ProductCompetitorMapping.competitor_product_id == CompetitorProduct.id)
        .join(Competitor, CompetitorProduct.competitor_id == Competitor.id)
        .where(ProductCompetitorMapping.product_id.in_(product_ids), CompetitorProduct.is_active == True)
    )
    comp_rows = (await db.execute(comp_stmt)).all()
    all_cp_ids = [r.CompetitorProduct.id for r in comp_rows]

    latest_prices = {}
    if all_cp_ids:
        lsq = select(PriceSnapshot.competitor_product_id, sqlfunc.max(PriceSnapshot.scraped_at).label("max_at")).where(PriceSnapshot.competitor_product_id.in_(all_cp_ids)).group_by(PriceSnapshot.competitor_product_id).subquery()
        pr = await db.execute(select(PriceSnapshot).join(lsq, (PriceSnapshot.competitor_product_id == lsq.c.competitor_product_id) & (PriceSnapshot.scraped_at == lsq.c.max_at)))
        latest_prices = {ps.competitor_product_id: ps for ps in pr.scalars().all()}

    pcmap = defaultdict(list)
    for row in comp_rows:
        pcmap[row.our_product_id].append(row)

    suggestions = []
    for product in our_products:
        rows = pcmap.get(product.id, [])
        our_price = float(product.price) if product.price else None
        if not our_price or not rows:
            continue
        prices, out_of_stock = [], 0
        for row in rows:
            latest = latest_prices.get(row.CompetitorProduct.id)
            if latest and latest.price:
                prices.append(float(latest.price))
            if latest and latest.stock_status == "out_of_stock":
                out_of_stock += 1
        if not prices:
            continue
        prices.sort()
        cheapest = prices[0]
        avg_price = sum(prices) / len(prices)
        cheaper_count = sum(1 for p in prices if p < our_price)
        total = len(prices)
        stockout_pct = out_of_stock / total
        diff_pct = (our_price - cheapest) / our_price * 100

        action = reason = suggested_price = None
        priority = "low"
        if cheaper_count == 0 and diff_pct < -20:
            action, reason, suggested_price, priority = "raise", f"我哋係最平，比次平競品便宜 {abs(diff_pct):.0f}%，有加價空間", round(cheapest * 0.97, 0), "medium"
        elif cheaper_count == 0 and stockout_pct > 0.5:
            action, reason, suggested_price, priority = "raise", f"{stockout_pct*100:.0f}% 競品缺貨，供應緊張可考慮微加", round(our_price * 1.05, 0), "low"
        elif diff_pct > 25 and cheaper_count >= 3:
            action, reason, suggested_price, priority = "lower", f"有 {cheaper_count} 間競品比我平 {diff_pct:.0f}%，競爭力不足", round(cheapest * 1.02, 0), "high"
        elif diff_pct > 10 and cheaper_count >= 2:
            action, reason, suggested_price, priority = "lower", f"有 {cheaper_count} 間競品比我平，建議跟價", round(cheapest * 1.03, 0), "medium"
        elif stockout_pct > 0.7 and cheaper_count == 0:
            action, reason, priority = "maintain", f"{stockout_pct*100:.0f}% 競品缺貨，維持現價即可", "low"

        if action:
            suggestions.append({"product_id": str(product.id), "product_name": product.name.replace("GOGOJAP-", ""), "category": product.category_tag, "our_price": our_price, "cheapest_competitor_price": cheapest, "avg_competitor_price": round(avg_price, 1), "cheaper_count": cheaper_count, "total_competitors": total, "price_diff_pct": round(diff_pct, 1), "stockout_pct": round(stockout_pct * 100, 1), "action": action, "reason": reason, "suggested_price": suggested_price, "priority": priority})

    suggestions.sort(key=lambda x: ({"high": 0, "medium": 1, "low": 2}.get(x["priority"], 3), -abs(x["price_diff_pct"])))
    return {"suggestions": suggestions}

