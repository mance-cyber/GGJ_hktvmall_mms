# =============================================
# 類別數據庫管理 API
# =============================================

from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
from decimal import Decimal
import time
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy import select, func, desc, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
import logging

from app.models.database import get_db
from app.models.category import (
    CategoryDatabase,
    CategoryProduct,
    CategoryPriceSnapshot,
    CategoryAnalysisReport
)
from app.utils.unit_price import calculate_unit_price
from app.services.telegram import get_telegram_notifier

logger = logging.getLogger(__name__)

router = APIRouter()


# =============================================
# Schema 定義
# =============================================

class CategoryDatabaseCreate(BaseModel):
    """創建類別數據庫"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    hktv_category_url: Optional[str] = None
    scrape_frequency: str = Field(default="weekly")  # daily, weekly, monthly


class CategoryDatabaseUpdate(BaseModel):
    """更新類別數據庫"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    hktv_category_url: Optional[str] = None
    scrape_frequency: Optional[str] = None
    is_active: Optional[bool] = None


class CategoryDatabaseResponse(BaseModel):
    """類別數據庫響應"""
    id: str
    name: str
    description: Optional[str]
    hktv_category_url: Optional[str]
    total_products: int
    last_scraped_at: Optional[datetime]
    scrape_frequency: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CategoryDatabaseListResponse(BaseModel):
    """類別數據庫列表響應"""
    items: List[CategoryDatabaseResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class CategoryProductResponse(BaseModel):
    """類別商品響應"""
    id: str
    category_id: str
    name: str
    url: str
    sku: Optional[str]
    brand: Optional[str]
    price: Optional[Decimal]
    original_price: Optional[Decimal]
    discount_percent: Optional[Decimal]
    attributes: Optional[Dict[str, Any]]
    unit_price: Optional[Decimal]
    unit_type: Optional[str]
    stock_status: Optional[str]
    is_available: bool
    rating: Optional[Decimal]
    review_count: Optional[int]
    image_url: Optional[str]
    first_seen_at: datetime
    last_updated_at: datetime

    class Config:
        from_attributes = True


class CategoryProductListResponse(BaseModel):
    """類別商品列表響應"""
    items: List[CategoryProductResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class TriggerCategoryScrapeRequest(BaseModel):
    """觸發類別抓取請求"""
    category_id: str
    max_products: Optional[int] = Field(default=None, ge=1, le=1000)


class TriggerCategoryScrapeResponse(BaseModel):
    """觸發類別抓取響應"""
    task_id: str
    message: str
    category_name: str


class SyncScrapeRequest(BaseModel):
    """同步抓取請求"""
    max_products: int = Field(default=20, ge=1, le=100)


class SyncScrapeProgress(BaseModel):
    """同步抓取進度"""
    status: str  # discovering, scraping, saving, completed, error
    current_step: int
    total_steps: int
    message: str
    urls_found: int = 0
    products_scraped: int = 0
    products_saved: int = 0
    errors: List[str] = []


class SyncScrapeResponse(BaseModel):
    """同步抓取響應"""
    success: bool
    message: str
    category_name: str
    urls_discovered: int
    products_scraped: int
    products_saved: int
    errors: List[str] = []
    duration_seconds: float


class CategoryStatsResponse(BaseModel):
    """類別統計響應"""
    category_id: str
    category_name: str
    total_products: int
    available_products: int
    avg_price: Optional[Decimal]
    min_price: Optional[Decimal]
    max_price: Optional[Decimal]
    price_range: Optional[Decimal]
    brands_count: int
    last_scraped_at: Optional[datetime]


class CategoryAnalysisResponse(BaseModel):
    """AI 分析報告響應"""
    id: str
    category_id: str
    report_type: str
    report_title: str
    summary: str
    key_findings: Optional[Dict[str, Any]]
    recommendations: Optional[Dict[str, Any]]
    data_snapshot: Optional[Dict[str, Any]]
    generated_by: str
    generated_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class PriceSnapshotResponse(BaseModel):
    """價格快照響應"""
    id: str
    product_id: str
    price: Optional[Decimal]
    original_price: Optional[Decimal]
    discount_percent: Optional[Decimal]
    unit_price: Optional[Decimal]
    stock_status: Optional[str]
    is_available: Optional[bool]
    scraped_at: datetime

    class Config:
        from_attributes = True


class PriceHistoryResponse(BaseModel):
    """價格歷史響應"""
    product_id: str
    product_name: str
    current_price: Optional[Decimal]
    price_change_7d: Optional[Decimal]
    price_change_30d: Optional[Decimal]
    lowest_price: Optional[Decimal]
    highest_price: Optional[Decimal]
    snapshots: List[PriceSnapshotResponse]
    total_snapshots: int


class TriggerAnalysisRequest(BaseModel):
    """觸發 AI 分析請求"""
    category_id: str
    analysis_type: str = Field(..., pattern="^(summary|trend)$")  # summary 或 trend
    model: Optional[str] = Field(default="claude-sonnet-4-20250514")


class SyncAnalysisRequest(BaseModel):
    """同步 AI 分析請求"""
    analysis_type: str = Field(default="summary", pattern="^(summary|trend)$")
    model: str = Field(default="claude-sonnet-4-20250514")


class SyncAnalysisResponse(BaseModel):
    """同步 AI 分析響應"""
    success: bool
    report_id: Optional[str] = None
    category_name: str
    analysis_type: str
    summary: str
    key_findings: Optional[Dict[str, Any]] = None
    recommendations: Optional[Dict[str, Any]] = None
    duration_seconds: float
    error: Optional[str] = None


class TriggerAnalysisResponse(BaseModel):
    """觸發 AI 分析響應"""
    task_id: str
    message: str
    analysis_type: str


# =============================================
# 類別數據庫 CRUD API
# =============================================

@router.get("", response_model=CategoryDatabaseListResponse)
async def list_category_databases(
    db: AsyncSession = Depends(get_db),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    is_active: Optional[bool] = None,
):
    """獲取類別數據庫列表"""
    query = select(CategoryDatabase)

    if is_active is not None:
        query = query.where(CategoryDatabase.is_active == is_active)

    # 計算總數
    count_query = select(func.count()).select_from(query.subquery())
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0

    # 分頁查詢
    query = query.order_by(desc(CategoryDatabase.created_at))
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    categories = result.scalars().all()

    items = [
        CategoryDatabaseResponse(
            id=str(cat.id),
            name=cat.name,
            description=cat.description,
            hktv_category_url=cat.hktv_category_url,
            total_products=cat.total_products,
            last_scraped_at=cat.last_scraped_at,
            scrape_frequency=cat.scrape_frequency,
            is_active=cat.is_active,
            created_at=cat.created_at,
            updated_at=cat.updated_at,
        )
        for cat in categories
    ]

    return CategoryDatabaseListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.post("", response_model=CategoryDatabaseResponse, status_code=201)
async def create_category_database(
    data: CategoryDatabaseCreate,
    db: AsyncSession = Depends(get_db),
):
    """創建類別數據庫"""
    category = CategoryDatabase(
        name=data.name,
        description=data.description,
        hktv_category_url=data.hktv_category_url,
        scrape_frequency=data.scrape_frequency,
    )

    db.add(category)
    await db.commit()
    await db.refresh(category)

    return CategoryDatabaseResponse(
        id=str(category.id),
        name=category.name,
        description=category.description,
        hktv_category_url=category.hktv_category_url,
        total_products=category.total_products,
        last_scraped_at=category.last_scraped_at,
        scrape_frequency=category.scrape_frequency,
        is_active=category.is_active,
        created_at=category.created_at,
        updated_at=category.updated_at,
    )


@router.get("/{category_id}", response_model=CategoryDatabaseResponse)
async def get_category_database(
    category_id: str,
    db: AsyncSession = Depends(get_db),
):
    """獲取單個類別數據庫"""
    result = await db.execute(
        select(CategoryDatabase).where(CategoryDatabase.id == UUID(category_id))
    )
    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(status_code=404, detail="類別數據庫不存在")

    return CategoryDatabaseResponse(
        id=str(category.id),
        name=category.name,
        description=category.description,
        hktv_category_url=category.hktv_category_url,
        total_products=category.total_products,
        last_scraped_at=category.last_scraped_at,
        scrape_frequency=category.scrape_frequency,
        is_active=category.is_active,
        created_at=category.created_at,
        updated_at=category.updated_at,
    )


@router.put("/{category_id}", response_model=CategoryDatabaseResponse)
async def update_category_database(
    category_id: str,
    data: CategoryDatabaseUpdate,
    db: AsyncSession = Depends(get_db),
):
    """更新類別數據庫"""
    result = await db.execute(
        select(CategoryDatabase).where(CategoryDatabase.id == UUID(category_id))
    )
    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(status_code=404, detail="類別數據庫不存在")

    # 更新非 None 的欄位
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(category, key, value)

    await db.commit()
    await db.refresh(category)

    return CategoryDatabaseResponse(
        id=str(category.id),
        name=category.name,
        description=category.description,
        hktv_category_url=category.hktv_category_url,
        total_products=category.total_products,
        last_scraped_at=category.last_scraped_at,
        scrape_frequency=category.scrape_frequency,
        is_active=category.is_active,
        created_at=category.created_at,
        updated_at=category.updated_at,
    )


@router.delete("/{category_id}", status_code=204)
async def delete_category_database(
    category_id: str,
    db: AsyncSession = Depends(get_db),
):
    """刪除類別數據庫"""
    result = await db.execute(
        select(CategoryDatabase).where(CategoryDatabase.id == UUID(category_id))
    )
    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(status_code=404, detail="類別數據庫不存在")

    await db.execute(
        delete(CategoryDatabase).where(CategoryDatabase.id == UUID(category_id))
    )
    await db.commit()


# =============================================
# 類別商品 API
# =============================================

@router.get("/{category_id}/products", response_model=CategoryProductListResponse)
async def list_category_products(
    category_id: str,
    db: AsyncSession = Depends(get_db),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
    is_available: Optional[bool] = None,
    brand: Optional[str] = None,
):
    """獲取類別內的商品列表"""
    query = select(CategoryProduct).where(CategoryProduct.category_id == UUID(category_id))

    if is_available is not None:
        query = query.where(CategoryProduct.is_available == is_available)
    if brand:
        query = query.where(CategoryProduct.brand == brand)

    # 計算總數
    count_query = select(func.count()).select_from(query.subquery())
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0

    # 分頁查詢
    query = query.order_by(CategoryProduct.unit_price.asc().nullslast())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    products = result.scalars().all()

    items = [
        CategoryProductResponse(
            id=str(p.id),
            category_id=str(p.category_id),
            name=p.name,
            url=p.url,
            sku=p.sku,
            brand=p.brand,
            price=p.price,
            original_price=p.original_price,
            discount_percent=p.discount_percent,
            attributes=p.attributes,
            unit_price=p.unit_price,
            unit_type=p.unit_type,
            stock_status=p.stock_status,
            is_available=p.is_available,
            rating=p.rating,
            review_count=p.review_count,
            image_url=p.image_url,
            first_seen_at=p.first_seen_at,
            last_updated_at=p.last_updated_at,
        )
        for p in products
    ]

    return CategoryProductListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.get("/{category_id}/stats", response_model=CategoryStatsResponse)
async def get_category_stats(
    category_id: str,
    db: AsyncSession = Depends(get_db),
):
    """獲取類別統計數據"""
    # 獲取類別
    cat_result = await db.execute(
        select(CategoryDatabase).where(CategoryDatabase.id == UUID(category_id))
    )
    category = cat_result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="類別數據庫不存在")

    # 統計商品
    total_result = await db.execute(
        select(func.count(CategoryProduct.id)).where(
            CategoryProduct.category_id == UUID(category_id)
        )
    )
    total_products = total_result.scalar() or 0

    available_result = await db.execute(
        select(func.count(CategoryProduct.id)).where(
            CategoryProduct.category_id == UUID(category_id),
            CategoryProduct.is_available == True
        )
    )
    available_products = available_result.scalar() or 0

    # 價格統計
    price_stats = await db.execute(
        select(
            func.avg(CategoryProduct.price),
            func.min(CategoryProduct.price),
            func.max(CategoryProduct.price)
        ).where(
            CategoryProduct.category_id == UUID(category_id),
            CategoryProduct.price.isnot(None)
        )
    )
    avg_price, min_price, max_price = price_stats.first() or (None, None, None)

    # 品牌數
    brands_result = await db.execute(
        select(func.count(func.distinct(CategoryProduct.brand))).where(
            CategoryProduct.category_id == UUID(category_id),
            CategoryProduct.brand.isnot(None)
        )
    )
    brands_count = brands_result.scalar() or 0

    price_range = None
    if min_price and max_price:
        price_range = Decimal(str(max_price)) - Decimal(str(min_price))

    return CategoryStatsResponse(
        category_id=str(category.id),
        category_name=category.name,
        total_products=total_products,
        available_products=available_products,
        avg_price=Decimal(str(avg_price)) if avg_price else None,
        min_price=Decimal(str(min_price)) if min_price else None,
        max_price=Decimal(str(max_price)) if max_price else None,
        price_range=price_range,
        brands_count=brands_count,
        last_scraped_at=category.last_scraped_at,
    )


# =============================================
# 類別抓取 API
# =============================================

@router.post("/{category_id}/scrape", response_model=TriggerCategoryScrapeResponse)
async def trigger_category_scrape(
    category_id: str,
    request: TriggerCategoryScrapeRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """觸發類別抓取任務"""
    # 驗證類別存在
    result = await db.execute(
        select(CategoryDatabase).where(CategoryDatabase.id == UUID(category_id))
    )
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="類別數據庫不存在")

    if not category.hktv_category_url:
        raise HTTPException(status_code=400, detail="類別缺少 HKTVmall URL")

    try:
        from app.tasks.category_tasks import scrape_category_products
    except ImportError:
        # Celery 未配置時的模擬響應
        return TriggerCategoryScrapeResponse(
            task_id="demo-task-category",
            message=f"已啟動類別抓取任務（演示模式）",
            category_name=category.name,
        )

    # 啟動 Celery 任務
    task = scrape_category_products.delay(
        category_id=str(category.id),
        max_products=request.max_products
    )

    return TriggerCategoryScrapeResponse(
        task_id=task.id,
        message=f"已啟動類別 '{category.name}' 的抓取任務",
        category_name=category.name,
    )


@router.post("/{category_id}/scrape-sync", response_model=SyncScrapeResponse)
async def sync_scrape_category(
    category_id: str,
    request: SyncScrapeRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    同步執行類別抓取（不需要 Celery Worker）

    此端點會立即執行抓取並返回結果，適合測試和小規模抓取
    """
    start_time = time.time()
    errors: List[str] = []

    # 驗證類別存在
    result = await db.execute(
        select(CategoryDatabase).where(CategoryDatabase.id == UUID(category_id))
    )
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="類別數據庫不存在")

    if not category.hktv_category_url:
        raise HTTPException(status_code=400, detail="類別缺少 HKTVmall URL")

    logger.info(f"開始同步抓取類別: {category.name}, URL: {category.hktv_category_url}")

    # 初始化 Firecrawl 連接器
    try:
        from app.connectors.firecrawl import get_firecrawl_connector
        connector = get_firecrawl_connector()
    except Exception as e:
        logger.error(f"初始化 Firecrawl 連接器失敗: {e}")
        raise HTTPException(status_code=500, detail=f"初始化爬蟲失敗: {str(e)}")

    # Step 1: 發現商品 URL
    logger.info("Step 1: 發現商品 URL...")
    product_urls = []

    # 判斷是否為 HKTVmall URL，使用專門的發現方法
    is_hktv = "hktvmall.com" in category.hktv_category_url.lower()

    if is_hktv:
        # 使用 HKTVmall 專用發現方法（支持分頁）
        logger.info("檢測到 HKTVmall URL，使用專用發現方法...")
        try:
            product_urls = connector.discover_hktv_products(
                category.hktv_category_url,
                max_products=request.max_products,
                search_pages=5  # 搜索 5 頁
            )
            logger.info(f"HKTVmall 專用方法發現 {len(product_urls)} 個商品 URL")
        except Exception as e:
            logger.error(f"HKTVmall 專用發現失敗: {e}")
            errors.append(f"HKTVmall URL 發現失敗: {str(e)}")

    # 如果 HKTVmall 方法沒有找到足夠的 URL，或不是 HKTVmall，使用通用方法
    if len(product_urls) < request.max_products:
        try:
            logger.info("使用通用 URL 發現方法...")
            generic_urls = connector.discover_product_urls(
                category.hktv_category_url,
                keywords=["product", "p/", "pd/", "goods", "item", "H"]
            )
            # 合併結果（去重）
            existing_urls = set(product_urls)
            for url in generic_urls:
                if url not in existing_urls and len(product_urls) < request.max_products:
                    product_urls.append(url)
            logger.info(f"通用方法補充後共 {len(product_urls)} 個商品 URL")
        except Exception as e:
            logger.error(f"通用發現 URL 失敗: {e}")
            errors.append(f"URL 發現失敗: {str(e)}")

    # 最後嘗試：如果仍然沒有找到 URL，使用 map
    if not product_urls:
        logger.info("嘗試使用 map 功能發現 URL...")
        try:
            map_result = connector.map_urls(category.hktv_category_url, limit=request.max_products * 2)
            # 過濾 HKTVmall 產品 URL
            for url in map_result.urls:
                if "/p/H" in url or "/p/" in url.lower():
                    product_urls.append(url)
                    if len(product_urls) >= request.max_products:
                        break
            logger.info(f"Map 發現 {len(product_urls)} 個 URL")
        except Exception as e:
            logger.error(f"Map 失敗: {e}")
            errors.append(f"Map 失敗: {str(e)}")

    # 最終限制數量
    product_urls = product_urls[:request.max_products]

    urls_discovered = len(product_urls)
    products_scraped = 0
    products_saved = 0
    price_changes = []  # 追踪價格變化 [{"name": str, "old": Decimal, "new": Decimal, "url": str}]

    # Step 2: 抓取每個商品頁面
    logger.info(f"Step 2: 開始抓取 {len(product_urls)} 個商品頁面...")
    scraped_products = []

    for i, url in enumerate(product_urls):
        try:
            logger.info(f"抓取商品 {i+1}/{len(product_urls)}: {url}")
            product_info = connector.extract_product_info(url)
            products_scraped += 1

            scraped_products.append({
                "url": url,
                "info": product_info
            })
            logger.info(f"成功抓取: {product_info.name}, 價格: {product_info.price}")
        except Exception as e:
            logger.error(f"抓取商品失敗 {url}: {e}")
            errors.append(f"抓取失敗 ({url}): {str(e)}")

    # Step 3: 保存到數據庫
    logger.info(f"Step 3: 保存 {len(scraped_products)} 個商品到數據庫...")

    for item in scraped_products:
        try:
            url = item["url"]
            info = item["info"]

            # 計算單位價格
            unit_price = None
            unit_type = "per_100g"  # 預設
            if info.price:
                calc_unit_price, calc_unit_type = calculate_unit_price(info.price, info.name)
                if calc_unit_price:
                    unit_price = calc_unit_price
                    unit_type = calc_unit_type
                    logger.info(f"計算單位價格: {info.name} -> HK${unit_price}/{unit_type}")

            # 檢查商品是否已存在
            existing = await db.execute(
                select(CategoryProduct).where(
                    CategoryProduct.category_id == UUID(category_id),
                    CategoryProduct.url == url
                )
            )
            existing_product = existing.scalar_one_or_none()

            if existing_product:
                # 檢查價格是否有變化，記錄快照
                price_changed = (
                    existing_product.price != info.price or
                    existing_product.original_price != info.original_price or
                    existing_product.stock_status != info.stock_status
                )

                if price_changed and existing_product.price is not None:
                    # 創建價格快照（記錄變化前的價格）
                    snapshot = CategoryPriceSnapshot(
                        category_product_id=existing_product.id,
                        price=existing_product.price,
                        original_price=existing_product.original_price,
                        discount_percent=existing_product.discount_percent,
                        unit_price=existing_product.unit_price,
                        stock_status=existing_product.stock_status,
                        is_available=existing_product.is_available,
                    )
                    db.add(snapshot)
                    logger.info(f"價格變化，創建快照: {info.name} ({existing_product.price} -> {info.price})")

                    # 追踪價格變化（用於 Telegram 通知）
                    if info.price and existing_product.price != info.price:
                        price_changes.append({
                            "name": info.name,
                            "old": existing_product.price,
                            "new": info.price,
                            "url": url
                        })

                # 更新現有商品
                existing_product.name = info.name
                existing_product.price = info.price
                existing_product.original_price = info.original_price
                existing_product.discount_percent = info.discount_percent
                existing_product.stock_status = info.stock_status
                existing_product.rating = info.rating
                existing_product.review_count = info.review_count
                existing_product.image_url = info.image_url
                existing_product.brand = info.brand
                existing_product.sku = info.sku
                existing_product.unit_price = unit_price
                existing_product.unit_type = unit_type
                existing_product.is_available = info.stock_status != "out_of_stock"
                existing_product.last_updated_at = datetime.utcnow()
                logger.info(f"更新商品: {info.name}")
            else:
                # 創建新商品
                new_product = CategoryProduct(
                    category_id=UUID(category_id),
                    name=info.name,
                    url=url,
                    price=info.price,
                    original_price=info.original_price,
                    discount_percent=info.discount_percent,
                    stock_status=info.stock_status,
                    rating=info.rating,
                    review_count=info.review_count,
                    image_url=info.image_url,
                    brand=info.brand,
                    sku=info.sku,
                    unit_price=unit_price,
                    unit_type=unit_type,
                    is_available=info.stock_status != "out_of_stock" if info.stock_status else True,
                )
                db.add(new_product)
                logger.info(f"新增商品: {info.name}")

            products_saved += 1

        except Exception as e:
            logger.error(f"保存商品失敗: {e}")
            errors.append(f"保存失敗: {str(e)}")

    # 更新類別統計
    try:
        category.total_products = products_saved
        category.last_scraped_at = datetime.utcnow()
        await db.commit()
        logger.info(f"類別統計已更新: total_products={products_saved}")
    except Exception as e:
        logger.error(f"更新類別統計失敗: {e}")
        errors.append(f"更新統計失敗: {str(e)}")
        await db.rollback()

    duration = time.time() - start_time
    success = products_saved > 0

    logger.info(f"同步抓取完成: 發現={urls_discovered}, 抓取={products_scraped}, 保存={products_saved}, 耗時={duration:.2f}秒")

    # 發送 Telegram 通知
    try:
        telegram = get_telegram_notifier()
        if telegram.enabled:
            # 通知爬取完成
            await telegram.notify_scrape_complete(
                category_name=category.name,
                product_count=products_saved,
                new_products=products_saved,
                updated_products=0,
                duration_seconds=duration
            )
            logger.info("已發送 Telegram 爬取完成通知")

            # 如果有顯著價格變化，發送價格變動通知
            if price_changes:
                from app.config import get_settings
                settings = get_settings()
                threshold = settings.price_alert_threshold  # 默認 10%
                await telegram.notify_significant_price_changes(
                    category_name=category.name,
                    changes=price_changes,
                    threshold_percent=float(threshold)
                )
                logger.info(f"已發送 Telegram 價格變動通知 ({len(price_changes)} 個變化)")
    except Exception as e:
        logger.warning(f"發送 Telegram 通知失敗: {e}")

    return SyncScrapeResponse(
        success=success,
        message=f"抓取完成: 保存了 {products_saved} 個商品" if success else "抓取失敗，未保存任何商品",
        category_name=category.name,
        urls_discovered=urls_discovered,
        products_scraped=products_scraped,
        products_saved=products_saved,
        errors=errors,
        duration_seconds=round(duration, 2),
    )


# =============================================
# AI 分析 API
# =============================================

@router.get("/{category_id}/reports", response_model=List[CategoryAnalysisResponse])
async def list_category_reports(
    category_id: str,
    db: AsyncSession = Depends(get_db),
    report_type: Optional[str] = None,
    limit: int = Query(default=10, ge=1, le=50),
):
    """獲取類別的 AI 分析報告列表"""
    query = select(CategoryAnalysisReport).where(
        CategoryAnalysisReport.category_id == UUID(category_id)
    )

    if report_type:
        query = query.where(CategoryAnalysisReport.report_type == report_type)

    query = query.order_by(desc(CategoryAnalysisReport.generated_at)).limit(limit)

    result = await db.execute(query)
    reports = result.scalars().all()

    return [
        CategoryAnalysisResponse(
            id=str(r.id),
            category_id=str(r.category_id),
            report_type=r.report_type,
            report_title=r.report_title,
            summary=r.summary,
            key_findings=r.key_findings,
            recommendations=r.recommendations,
            data_snapshot=r.data_snapshot,
            generated_by=r.generated_by,
            generated_at=r.generated_at,
            created_at=r.created_at,
        )
        for r in reports
    ]


@router.post("/{category_id}/analyze", response_model=TriggerAnalysisResponse)
async def trigger_category_analysis(
    category_id: str,
    request: TriggerAnalysisRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """觸發 AI 分析任務"""
    # 驗證類別存在
    result = await db.execute(
        select(CategoryDatabase).where(CategoryDatabase.id == UUID(category_id))
    )
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="類別數據庫不存在")

    # 檢查是否有商品數據
    count_result = await db.execute(
        select(func.count(CategoryProduct.id)).where(
            CategoryProduct.category_id == UUID(category_id)
        )
    )
    product_count = count_result.scalar() or 0

    if product_count == 0:
        raise HTTPException(status_code=400, detail="類別內沒有商品數據，請先執行抓取")

    try:
        from app.tasks.category_tasks import analyze_category_data
    except ImportError:
        # Celery 未配置時的模擬響應
        return TriggerAnalysisResponse(
            task_id="demo-task-analysis",
            message=f"已啟動 AI 分析任務（演示模式）",
            analysis_type=request.analysis_type,
        )

    # 啟動 Celery 任務
    task = analyze_category_data.delay(
        category_id=str(category.id),
        analysis_type=request.analysis_type,
        model=request.model
    )

    analysis_type_name = "數據摘要" if request.analysis_type == "summary" else "趨勢預測"

    return TriggerAnalysisResponse(
        task_id=task.id,
        message=f"已啟動 {analysis_type_name} 分析任務",
        analysis_type=request.analysis_type,
    )


# =============================================
# 價格歷史 API
# =============================================

@router.get("/{category_id}/products/{product_id}/price-history", response_model=PriceHistoryResponse)
async def get_product_price_history(
    category_id: str,
    product_id: str,
    db: AsyncSession = Depends(get_db),
    limit: int = Query(default=50, ge=1, le=200),
):
    """獲取商品價格歷史"""
    from datetime import timedelta

    # 獲取商品
    result = await db.execute(
        select(CategoryProduct).where(
            CategoryProduct.id == UUID(product_id),
            CategoryProduct.category_id == UUID(category_id)
        )
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")

    # 獲取價格快照
    snapshots_result = await db.execute(
        select(CategoryPriceSnapshot)
        .where(CategoryPriceSnapshot.category_product_id == UUID(product_id))
        .order_by(desc(CategoryPriceSnapshot.scraped_at))
        .limit(limit)
    )
    snapshots = snapshots_result.scalars().all()

    # 計算價格變化
    now = datetime.utcnow()
    price_7d_ago = None
    price_30d_ago = None

    for snap in snapshots:
        days_ago = (now - snap.scraped_at).days
        if days_ago <= 7 and price_7d_ago is None:
            price_7d_ago = snap.price
        if days_ago <= 30 and price_30d_ago is None:
            price_30d_ago = snap.price

    price_change_7d = None
    price_change_30d = None

    if product.price and price_7d_ago:
        price_change_7d = product.price - price_7d_ago
    if product.price and price_30d_ago:
        price_change_30d = product.price - price_30d_ago

    # 計算最高最低價
    all_prices = [s.price for s in snapshots if s.price]
    if product.price:
        all_prices.append(product.price)

    lowest_price = min(all_prices) if all_prices else None
    highest_price = max(all_prices) if all_prices else None

    # 統計總快照數
    count_result = await db.execute(
        select(func.count(CategoryPriceSnapshot.id))
        .where(CategoryPriceSnapshot.category_product_id == UUID(product_id))
    )
    total_snapshots = count_result.scalar() or 0

    snapshot_responses = [
        PriceSnapshotResponse(
            id=str(s.id),
            product_id=str(s.category_product_id),
            price=s.price,
            original_price=s.original_price,
            discount_percent=s.discount_percent,
            unit_price=s.unit_price,
            stock_status=s.stock_status,
            is_available=s.is_available,
            scraped_at=s.scraped_at,
        )
        for s in snapshots
    ]

    return PriceHistoryResponse(
        product_id=str(product.id),
        product_name=product.name,
        current_price=product.price,
        price_change_7d=price_change_7d,
        price_change_30d=price_change_30d,
        lowest_price=lowest_price,
        highest_price=highest_price,
        snapshots=snapshot_responses,
        total_snapshots=total_snapshots,
    )


@router.get("/{category_id}/price-changes")
async def get_category_price_changes(
    category_id: str,
    db: AsyncSession = Depends(get_db),
    days: int = Query(default=7, ge=1, le=90),
    limit: int = Query(default=20, ge=1, le=100),
):
    """獲取類別內最近有價格變化的商品"""
    from datetime import timedelta

    cutoff_date = datetime.utcnow() - timedelta(days=days)

    # 查詢最近有快照的商品
    query = (
        select(
            CategoryProduct,
            func.count(CategoryPriceSnapshot.id).label("snapshot_count"),
            func.max(CategoryPriceSnapshot.scraped_at).label("last_change")
        )
        .join(CategoryPriceSnapshot, CategoryProduct.id == CategoryPriceSnapshot.category_product_id)
        .where(
            CategoryProduct.category_id == UUID(category_id),
            CategoryPriceSnapshot.scraped_at >= cutoff_date
        )
        .group_by(CategoryProduct.id)
        .order_by(desc("last_change"))
        .limit(limit)
    )

    result = await db.execute(query)
    rows = result.all()

    changes = []
    for row in rows:
        product = row[0]
        snapshot_count = row[1]
        last_change = row[2]

        # 獲取最近一次快照（變化前的價格）
        snap_result = await db.execute(
            select(CategoryPriceSnapshot)
            .where(CategoryPriceSnapshot.category_product_id == product.id)
            .order_by(desc(CategoryPriceSnapshot.scraped_at))
            .limit(1)
        )
        last_snapshot = snap_result.scalar_one_or_none()

        old_price = last_snapshot.price if last_snapshot else None
        price_diff = None
        if product.price and old_price:
            price_diff = float(product.price - old_price)

        changes.append({
            "product_id": str(product.id),
            "product_name": product.name,
            "current_price": float(product.price) if product.price else None,
            "old_price": float(old_price) if old_price else None,
            "price_diff": price_diff,
            "change_count": snapshot_count,
            "last_change_at": last_change.isoformat() if last_change else None,
        })

    return {
        "category_id": category_id,
        "days": days,
        "total_changes": len(changes),
        "items": changes,
    }


# =============================================
# 同步 AI 分析 API
# =============================================

@router.post("/{category_id}/analyze-sync", response_model=SyncAnalysisResponse)
async def sync_analyze_category(
    category_id: str,
    request: SyncAnalysisRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    同步執行 AI 分析（不需要 Celery Worker）

    此端點會立即執行分析並返回結果
    """
    import re
    start_time = time.time()

    # 驗證類別存在
    result = await db.execute(
        select(CategoryDatabase).where(CategoryDatabase.id == UUID(category_id))
    )
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="類別數據庫不存在")

    # 檢查是否有商品數據
    products_result = await db.execute(
        select(CategoryProduct).where(
            CategoryProduct.category_id == UUID(category_id),
            CategoryProduct.is_available == True
        )
    )
    products = products_result.scalars().all()

    if len(products) == 0:
        return SyncAnalysisResponse(
            success=False,
            category_name=category.name,
            analysis_type=request.analysis_type,
            summary="",
            duration_seconds=round(time.time() - start_time, 2),
            error="類別內沒有可用商品數據，請先執行抓取"
        )

    logger.info(f"開始同步 AI 分析: {category.name} - {request.analysis_type}")

    # 構建數據快照
    data_snapshot = {
        "total_products": len(products),
        "products": [
            {
                "name": p.name,
                "brand": p.brand,
                "price": float(p.price) if p.price else None,
                "original_price": float(p.original_price) if p.original_price else None,
                "discount_percent": float(p.discount_percent) if p.discount_percent else None,
                "unit_price": float(p.unit_price) if p.unit_price else None,
                "rating": float(p.rating) if p.rating else None,
                "review_count": p.review_count,
            }
            for p in products[:100]
        ],
        "price_stats": _calculate_price_stats(products),
        "brands": list(set(p.brand for p in products if p.brand))[:20],
    }

    # 調用 Claude AI
    try:
        from anthropic import Anthropic
        from app.config import get_settings
        settings = get_settings()

        if not settings.anthropic_api_key:
            raise ValueError("Anthropic API Key 未設定")

        anthropic_client = Anthropic(api_key=settings.anthropic_api_key)

        # 構建提示詞
        if request.analysis_type == "summary":
            prompt = _build_summary_prompt(category.name, data_snapshot)
            report_title = f"{category.name} - 數據摘要"
        else:
            prompt = _build_trend_prompt(category.name, data_snapshot)
            report_title = f"{category.name} - 趨勢預測"

        logger.info(f"正在調用 Claude AI ({request.model})...")

        response = anthropic_client.messages.create(
            model=request.model,
            max_tokens=2000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        ai_response = response.content[0].text
        logger.info(f"AI 分析完成，響應長度: {len(ai_response)}")

        # 解析 AI 響應
        summary, key_findings, recommendations = _parse_ai_response(ai_response)

        # 保存報告
        report = CategoryAnalysisReport(
            category_id=UUID(category_id),
            report_type=request.analysis_type,
            report_title=report_title,
            summary=summary,
            key_findings=key_findings,
            recommendations=recommendations,
            data_snapshot=data_snapshot,
            generated_by=request.model,
        )
        db.add(report)
        await db.commit()
        await db.refresh(report)

        duration = time.time() - start_time
        logger.info(f"同步 AI 分析完成: {report_title}, 耗時 {duration:.2f}秒")

        return SyncAnalysisResponse(
            success=True,
            report_id=str(report.id),
            category_name=category.name,
            analysis_type=request.analysis_type,
            summary=summary,
            key_findings=key_findings,
            recommendations=recommendations,
            duration_seconds=round(duration, 2),
        )

    except Exception as e:
        logger.error(f"AI 分析失敗: {e}")
        return SyncAnalysisResponse(
            success=False,
            category_name=category.name,
            analysis_type=request.analysis_type,
            summary="",
            duration_seconds=round(time.time() - start_time, 2),
            error=str(e)
        )


def _calculate_price_stats(products: List[CategoryProduct]) -> Dict[str, Any]:
    """計算價格統計"""
    prices = [float(p.price) for p in products if p.price]
    if not prices:
        return {"avg": None, "min": None, "max": None}
    return {
        "avg": sum(prices) / len(prices),
        "min": min(prices),
        "max": max(prices),
    }


def _build_summary_prompt(category_name: str, data: Dict[str, Any]) -> str:
    """構建數據摘要提示詞"""
    avg_price = data['price_stats']['avg']
    min_price = data['price_stats']['min']
    max_price = data['price_stats']['max']

    avg_str = f"HK${avg_price:.2f}" if avg_price else "N/A"
    min_str = f"HK${min_price:.2f}" if min_price else "N/A"
    max_str = f"HK${max_price:.2f}" if max_price else "N/A"
    brands_str = ', '.join(data['brands'][:5]) if data['brands'] else 'N/A'

    return f"""你是一位專業的電商數據分析師。請分析以下 HKTVmall「{category_name}」類別的商品數據，並提供數據摘要。

# 數據概覽
- 總商品數：{data['total_products']}
- 平均價格：{avg_str}
- 價格區間：{min_str} - {max_str}
- 品牌數量：{len(data['brands'])}
- 主要品牌：{brands_str}

# 商品樣本（前 20 個）
{chr(10).join(f"- {p['name']}: HK${p['price']} ({p['brand']})" for p in data['products'][:20] if p['price'])}

# 分析要求
請提供以下內容：

## 摘要（Summary）
用 2-3 句話概括這個類別的整體情況。

## 關鍵發現（Key Findings）
列出 3-5 個數據洞察，格式：
1. 發現標題 - 具體描述
2. ...

## 建議（Recommendations）
提供 3-5 個可執行的建議，格式：
1. 建議標題 - 具體描述
2. ...

請用繁體中文回答，語言專業且簡潔。"""


def _build_trend_prompt(category_name: str, data: Dict[str, Any]) -> str:
    """構建趨勢預測提示詞"""
    avg_price = data['price_stats']['avg']
    min_price = data['price_stats']['min']
    max_price = data['price_stats']['max']

    avg_str = f"HK${avg_price:.2f}" if avg_price else "N/A"
    min_str = f"HK${min_price:.2f}" if min_price else "N/A"
    max_str = f"HK${max_price:.2f}" if max_price else "N/A"
    brands_str = ', '.join(data['brands'][:5]) if data['brands'] else 'N/A'

    return f"""你是一位專業的電商市場分析師。請基於以下 HKTVmall「{category_name}」類別的數據，預測市場趨勢。

# 數據概覽
- 總商品數：{data['total_products']}
- 平均價格：{avg_str}
- 價格區間：{min_str} - {max_str}
- 品牌數量：{len(data['brands'])}
- 主要品牌：{brands_str}

# 商品樣本
{chr(10).join(f"- {p['name']}: HK${p['price']} ({p['brand']})" for p in data['products'][:20] if p['price'])}

# 分析要求
請提供以下內容：

## 摘要（Summary）
用 2-3 句話概括市場現狀和趨勢方向。

## 關鍵趨勢（Key Findings）
列出 3-5 個市場趨勢，格式：
1. 趨勢標題 - 具體描述和證據
2. ...

## 未來建議（Recommendations）
提供 3-5 個前瞻性建議，格式：
1. 建議標題 - 具體行動方案
2. ...

請用繁體中文回答，語言專業且具洞察力。"""


def _parse_ai_response(response: str) -> tuple:
    """
    解析 AI 響應

    返回：(summary, key_findings, recommendations)
    """
    import re
    lines = response.strip().split('\n')

    summary = ""
    key_findings = {}
    recommendations = {}

    current_section = None
    current_content = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 檢測章節標題
        if '摘要' in line or 'Summary' in line:
            if current_section and current_content:
                _save_section_content(current_section, current_content, key_findings, recommendations)
            current_section = 'summary'
            current_content = []
        elif '關鍵發現' in line or '關鍵趨勢' in line or 'Key Findings' in line:
            if current_section == 'summary':
                summary = '\n'.join(current_content).strip()
            current_section = 'findings'
            current_content = []
        elif '建議' in line or 'Recommendations' in line:
            if current_section == 'findings' and current_content:
                _save_section_content(current_section, current_content, key_findings, recommendations)
            current_section = 'recommendations'
            current_content = []
        else:
            current_content.append(line)

    # 保存最後一個章節
    if current_section == 'summary':
        summary = '\n'.join(current_content).strip()
    elif current_section and current_content:
        _save_section_content(current_section, current_content, key_findings, recommendations)

    return summary, key_findings, recommendations


def _save_section_content(section: str, content: List[str], findings: Dict, recommendations: Dict):
    """保存章節內容"""
    import re
    text = '\n'.join(content).strip()

    items = {}
    for line in content:
        match = re.match(r'^(\d+)\.\s*(.+?)\s*[-–—]\s*(.+)$', line)
        if match:
            num = match.group(1)
            title = match.group(2).strip()
            desc = match.group(3).strip()
            items[f"item_{num}"] = {"title": title, "description": desc}
        elif line.strip():
            items[f"item_{len(items) + 1}"] = {"text": line.strip()}

    if section == 'findings':
        findings.update(items if items else {"text": text})
    elif section == 'recommendations':
        recommendations.update(items if items else {"text": text})


# =============================================
# 數據導出 API
# =============================================

@router.get("/{category_id}/export/csv")
async def export_products_csv(
    category_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    導出類別商品為 CSV 格式

    返回 CSV 文件下載
    """
    from fastapi.responses import StreamingResponse
    import csv
    import io

    # 獲取類別
    category = await db.get(CategoryDatabase, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="類別不存在")

    # 獲取所有商品
    result = await db.execute(
        select(CategoryProduct)
        .where(CategoryProduct.category_id == category_id)
        .order_by(CategoryProduct.unit_price.asc().nulls_last())
    )
    products = result.scalars().all()

    # 創建 CSV
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)

    # 表頭
    writer.writerow([
        '商品名稱', 'SKU', '品牌', '價格', '原價', '折扣%',
        '單位價格', '單位類型', '庫存狀態', '是否有貨',
        '評分', '評論數', '商品連結', '首次發現', '最後更新'
    ])

    # 數據行
    for p in products:
        writer.writerow([
            p.name,
            p.sku or '',
            p.brand or '',
            str(p.price) if p.price else '',
            str(p.original_price) if p.original_price else '',
            str(p.discount_percent) if p.discount_percent else '',
            str(p.unit_price) if p.unit_price else '',
            p.unit_type or '',
            p.stock_status or '',
            '是' if p.is_available else '否',
            str(p.rating) if p.rating else '',
            str(p.review_count) if p.review_count else '',
            p.url,
            p.first_seen_at.strftime('%Y-%m-%d %H:%M') if p.first_seen_at else '',
            p.last_updated_at.strftime('%Y-%m-%d %H:%M') if p.last_updated_at else '',
        ])

    output.seek(0)
    filename = f"{category.name}_products_{datetime.now().strftime('%Y%m%d')}.csv"

    # 添加 BOM 以支持 Excel 中文顯示
    bom = '\ufeff'
    content = bom + output.getvalue()

    return StreamingResponse(
        iter([content.encode('utf-8')]),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{filename}"
        }
    )


@router.get("/{category_id}/export/excel")
async def export_products_excel(
    category_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    導出類別商品為 Excel 格式

    返回 Excel 文件下載
    """
    from fastapi.responses import StreamingResponse
    import pandas as pd
    import io

    # 獲取類別
    category = await db.get(CategoryDatabase, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="類別不存在")

    # 獲取所有商品
    result = await db.execute(
        select(CategoryProduct)
        .where(CategoryProduct.category_id == category_id)
        .order_by(CategoryProduct.unit_price.asc().nulls_last())
    )
    products = result.scalars().all()

    # 轉換為 DataFrame
    data = []
    for p in products:
        data.append({
            '商品名稱': p.name,
            'SKU': p.sku or '',
            '品牌': p.brand or '',
            '價格': float(p.price) if p.price else None,
            '原價': float(p.original_price) if p.original_price else None,
            '折扣%': float(p.discount_percent) if p.discount_percent else None,
            '單位價格': float(p.unit_price) if p.unit_price else None,
            '單位類型': p.unit_type or '',
            '庫存狀態': p.stock_status or '',
            '是否有貨': '是' if p.is_available else '否',
            '評分': float(p.rating) if p.rating else None,
            '評論數': p.review_count or 0,
            '商品連結': p.url,
            '首次發現': p.first_seen_at.strftime('%Y-%m-%d %H:%M') if p.first_seen_at else '',
            '最後更新': p.last_updated_at.strftime('%Y-%m-%d %H:%M') if p.last_updated_at else '',
        })

    df = pd.DataFrame(data)

    # 創建 Excel 文件
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='商品列表', index=False)

        # 調整列寬
        worksheet = writer.sheets['商品列表']
        for idx, col in enumerate(df.columns):
            max_length = max(
                df[col].astype(str).map(len).max(),
                len(col)
            ) + 2
            worksheet.column_dimensions[chr(65 + idx)].width = min(max_length, 50)

    output.seek(0)
    filename = f"{category.name}_products_{datetime.now().strftime('%Y%m%d')}.xlsx"

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{filename}"
        }
    )


@router.get("/{category_id}/products/{product_id}/price-history")
async def get_product_price_history(
    category_id: UUID,
    product_id: UUID,
    days: int = Query(default=30, ge=1, le=365),
    db: AsyncSession = Depends(get_db)
):
    """
    獲取商品價格歷史（用於圖表）

    返回指定天數內的價格變化記錄
    """
    from datetime import timedelta

    # 驗證商品存在
    product = await db.get(CategoryProduct, product_id)
    if not product or str(product.category_id) != str(category_id):
        raise HTTPException(status_code=404, detail="商品不存在")

    # 計算日期範圍
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    # 獲取價格快照
    result = await db.execute(
        select(CategoryPriceSnapshot)
        .where(CategoryPriceSnapshot.product_id == product_id)
        .where(CategoryPriceSnapshot.scraped_at >= start_date)
        .order_by(CategoryPriceSnapshot.scraped_at.asc())
    )
    snapshots = result.scalars().all()

    # 構建圖表數據
    chart_data = []
    for s in snapshots:
        chart_data.append({
            "date": s.scraped_at.strftime('%Y-%m-%d'),
            "datetime": s.scraped_at.isoformat(),
            "price": float(s.price) if s.price else None,
            "original_price": float(s.original_price) if s.original_price else None,
            "unit_price": float(s.unit_price) if s.unit_price else None,
            "discount_percent": float(s.discount_percent) if s.discount_percent else None,
            "is_available": s.is_available,
        })

    # 計算統計
    prices = [s.price for s in snapshots if s.price]
    stats = {
        "min_price": float(min(prices)) if prices else None,
        "max_price": float(max(prices)) if prices else None,
        "avg_price": float(sum(prices) / len(prices)) if prices else None,
        "current_price": float(product.price) if product.price else None,
        "price_trend": None,
    }

    # 計算趨勢
    if len(prices) >= 2:
        first_price = prices[0]
        last_price = prices[-1]
        if first_price and last_price:
            change_pct = ((last_price - first_price) / first_price) * 100
            stats["price_trend"] = round(float(change_pct), 2)

    return {
        "product_id": str(product_id),
        "product_name": product.name,
        "days": days,
        "data_points": len(chart_data),
        "chart_data": chart_data,
        "statistics": stats,
    }


# =============================================
# 商品刪除 API
# =============================================

class DeleteProductsRequest(BaseModel):
    """批量刪除商品請求"""
    product_ids: List[str] = Field(..., min_length=1, max_length=100)


@router.delete("/{category_id}/products/{product_id}", status_code=204)
async def delete_category_product(
    category_id: str,
    product_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    刪除類別內的單個商品

    同時刪除相關的價格快照
    """
    # 驗證商品存在且屬於該類別
    result = await db.execute(
        select(CategoryProduct).where(
            CategoryProduct.id == UUID(product_id),
            CategoryProduct.category_id == UUID(category_id)
        )
    )
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")

    product_name = product.name
    logger.info(f"刪除商品: {product_name} (ID: {product_id})")

    # 刪除相關價格快照
    await db.execute(
        delete(CategoryPriceSnapshot).where(
            CategoryPriceSnapshot.category_product_id == UUID(product_id)
        )
    )

    # 刪除商品
    await db.execute(
        delete(CategoryProduct).where(CategoryProduct.id == UUID(product_id))
    )

    # 更新類別統計
    count_result = await db.execute(
        select(func.count(CategoryProduct.id)).where(
            CategoryProduct.category_id == UUID(category_id)
        )
    )
    new_count = count_result.scalar() or 0

    await db.execute(
        update(CategoryDatabase)
        .where(CategoryDatabase.id == UUID(category_id))
        .values(total_products=new_count)
    )

    await db.commit()
    logger.info(f"商品 {product_name} 已刪除，類別商品數更新為 {new_count}")


@router.post("/{category_id}/products/bulk-delete", status_code=200)
async def bulk_delete_category_products(
    category_id: str,
    request: DeleteProductsRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    批量刪除類別內的商品

    同時刪除相關的價格快照
    """
    # 驗證類別存在
    cat_result = await db.execute(
        select(CategoryDatabase).where(CategoryDatabase.id == UUID(category_id))
    )
    category = cat_result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="類別不存在")

    deleted_count = 0
    errors = []

    for pid in request.product_ids:
        try:
            # 驗證商品存在且屬於該類別
            result = await db.execute(
                select(CategoryProduct).where(
                    CategoryProduct.id == UUID(pid),
                    CategoryProduct.category_id == UUID(category_id)
                )
            )
            product = result.scalar_one_or_none()

            if not product:
                errors.append(f"商品 {pid} 不存在")
                continue

            # 刪除相關價格快照
            await db.execute(
                delete(CategoryPriceSnapshot).where(
                    CategoryPriceSnapshot.category_product_id == UUID(pid)
                )
            )

            # 刪除商品
            await db.execute(
                delete(CategoryProduct).where(CategoryProduct.id == UUID(pid))
            )

            deleted_count += 1
            logger.info(f"批量刪除: 已刪除商品 {product.name}")

        except Exception as e:
            errors.append(f"刪除 {pid} 失敗: {str(e)}")
            logger.error(f"批量刪除商品失敗: {e}")

    # 更新類別統計
    count_result = await db.execute(
        select(func.count(CategoryProduct.id)).where(
            CategoryProduct.category_id == UUID(category_id)
        )
    )
    new_count = count_result.scalar() or 0

    await db.execute(
        update(CategoryDatabase)
        .where(CategoryDatabase.id == UUID(category_id))
        .values(total_products=new_count)
    )

    await db.commit()
    logger.info(f"批量刪除完成: 刪除 {deleted_count} 個商品，類別商品數更新為 {new_count}")

    return {
        "success": True,
        "deleted_count": deleted_count,
        "total_requested": len(request.product_ids),
        "errors": errors,
        "remaining_products": new_count,
    }


@router.get("/{category_id}/price-overview")
async def get_category_price_overview(
    category_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    獲取類別價格概覽（儀表板用）

    返回類別內商品的價格分佈和趨勢
    """
    # 獲取類別
    category = await db.get(CategoryDatabase, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="類別不存在")

    # 獲取所有商品
    result = await db.execute(
        select(CategoryProduct)
        .where(CategoryProduct.category_id == category_id)
        .where(CategoryProduct.price.isnot(None))
    )
    products = result.scalars().all()

    if not products:
        return {
            "category_id": str(category_id),
            "category_name": category.name,
            "total_products": 0,
            "price_distribution": [],
            "brand_comparison": [],
            "top_deals": [],
        }

    # 價格分佈（按價格區間分組）
    price_ranges = [
        (0, 50, "$0-50"),
        (50, 100, "$50-100"),
        (100, 200, "$100-200"),
        (200, 500, "$200-500"),
        (500, 1000, "$500-1000"),
        (1000, float('inf'), "$1000+"),
    ]

    distribution = []
    for min_p, max_p, label in price_ranges:
        count = sum(1 for p in products if p.price and min_p <= float(p.price) < max_p)
        if count > 0:
            distribution.append({"range": label, "count": count})

    # 品牌價格比較
    brand_prices = {}
    for p in products:
        brand = p.brand or "未知品牌"
        if brand not in brand_prices:
            brand_prices[brand] = []
        if p.price:
            brand_prices[brand].append(float(p.price))

    brand_comparison = []
    for brand, prices in sorted(brand_prices.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
        if prices:
            brand_comparison.append({
                "brand": brand,
                "avg_price": round(sum(prices) / len(prices), 2),
                "min_price": round(min(prices), 2),
                "max_price": round(max(prices), 2),
                "product_count": len(prices),
            })

    # 最優惠商品（折扣最大）
    discounted = [p for p in products if p.discount_percent and float(p.discount_percent) > 0]
    discounted.sort(key=lambda x: float(x.discount_percent or 0), reverse=True)

    top_deals = []
    for p in discounted[:10]:
        top_deals.append({
            "name": p.name[:50] + "..." if len(p.name) > 50 else p.name,
            "price": float(p.price) if p.price else None,
            "original_price": float(p.original_price) if p.original_price else None,
            "discount_percent": float(p.discount_percent) if p.discount_percent else None,
            "url": p.url,
        })

    return {
        "category_id": str(category_id),
        "category_name": category.name,
        "total_products": len(products),
        "price_distribution": distribution,
        "brand_comparison": brand_comparison,
        "top_deals": top_deals,
    }


# =============================================
# 抓取預覽/審核模式 API
# =============================================

# 全局臨時存儲預覽數據（生產環境應使用 Redis）
_preview_cache: Dict[str, Any] = {}


class PreviewScrapeRequest(BaseModel):
    """預覽抓取請求"""
    max_products: int = Field(default=20, ge=1, le=100)


class PreviewProductItem(BaseModel):
    """預覽商品項目"""
    url: str
    name: str
    price: Optional[Decimal] = None
    original_price: Optional[Decimal] = None
    discount_percent: Optional[Decimal] = None
    stock_status: Optional[str] = None
    brand: Optional[str] = None
    sku: Optional[str] = None
    image_url: Optional[str] = None
    rating: Optional[Decimal] = None
    review_count: Optional[int] = None
    unit_price: Optional[Decimal] = None
    unit_type: Optional[str] = None


class PreviewScrapeResponse(BaseModel):
    """預覽抓取響應"""
    preview_id: str
    category_id: str
    category_name: str
    total_scraped: int
    products: List[PreviewProductItem]
    errors: List[str]
    expires_at: datetime
    duration_seconds: float


class ConfirmScrapeRequest(BaseModel):
    """確認保存請求"""
    preview_id: str
    selected_product_indices: Optional[List[int]] = None  # None 表示全部保存


class ConfirmScrapeResponse(BaseModel):
    """確認保存響應"""
    success: bool
    message: str
    saved_count: int
    skipped_count: int
    errors: List[str]


@router.post("/{category_id}/scrape-preview", response_model=PreviewScrapeResponse)
async def preview_scrape_category(
    category_id: str,
    request: PreviewScrapeRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    預覽抓取類別商品（不保存到數據庫）

    抓取結果會暫存 30 分鐘，需要調用 scrape-confirm 來確認保存
    """
    import uuid as uuid_module
    start_time = time.time()
    errors: List[str] = []

    # 驗證類別存在
    result = await db.execute(
        select(CategoryDatabase).where(CategoryDatabase.id == UUID(category_id))
    )
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="類別數據庫不存在")

    if not category.hktv_category_url:
        raise HTTPException(status_code=400, detail="類別缺少 HKTVmall URL")

    logger.info(f"開始預覽抓取類別: {category.name}, URL: {category.hktv_category_url}")

    # 初始化 Firecrawl 連接器
    try:
        from app.connectors.firecrawl import get_firecrawl_connector
        connector = get_firecrawl_connector()
    except Exception as e:
        logger.error(f"初始化 Firecrawl 連接器失敗: {e}")
        raise HTTPException(status_code=500, detail=f"初始化爬蟲失敗: {str(e)}")

    # 發現商品 URL
    product_urls = []
    is_hktv = "hktvmall.com" in category.hktv_category_url.lower()

    if is_hktv:
        try:
            product_urls = connector.discover_hktv_products(
                category.hktv_category_url,
                max_products=request.max_products,
                search_pages=5
            )
        except Exception as e:
            errors.append(f"HKTVmall URL 發現失敗: {str(e)}")

    if len(product_urls) < request.max_products:
        try:
            generic_urls = connector.discover_product_urls(
                category.hktv_category_url,
                keywords=["product", "p/", "pd/", "goods", "item", "H"]
            )
            existing_urls = set(product_urls)
            for url in generic_urls:
                if url not in existing_urls and len(product_urls) < request.max_products:
                    product_urls.append(url)
        except Exception as e:
            errors.append(f"URL 發現失敗: {str(e)}")

    product_urls = product_urls[:request.max_products]

    # 抓取商品詳情（不保存）
    preview_products: List[PreviewProductItem] = []

    for i, url in enumerate(product_urls):
        try:
            logger.info(f"預覽抓取 {i+1}/{len(product_urls)}: {url}")
            info = connector.extract_product_info(url)

            # 計算單位價格
            unit_price = None
            unit_type = "per_100g"
            if info.price:
                calc_unit_price, calc_unit_type = calculate_unit_price(info.price, info.name)
                if calc_unit_price:
                    unit_price = calc_unit_price
                    unit_type = calc_unit_type

            preview_products.append(PreviewProductItem(
                url=url,
                name=info.name,
                price=info.price,
                original_price=info.original_price,
                discount_percent=info.discount_percent,
                stock_status=info.stock_status,
                brand=info.brand,
                sku=info.sku,
                image_url=info.image_url,
                rating=info.rating,
                review_count=info.review_count,
                unit_price=unit_price,
                unit_type=unit_type,
            ))
        except Exception as e:
            logger.error(f"預覽抓取失敗 {url}: {e}")
            errors.append(f"抓取失敗 ({url}): {str(e)}")

    # 生成預覽 ID 並緩存
    preview_id = str(uuid_module.uuid4())
    expires_at = datetime.utcnow() + timedelta(minutes=30)

    _preview_cache[preview_id] = {
        "category_id": category_id,
        "category_name": category.name,
        "products": [p.model_dump() for p in preview_products],
        "expires_at": expires_at,
    }

    duration = time.time() - start_time
    logger.info(f"預覽抓取完成: {len(preview_products)} 個商品, 耗時 {duration:.2f}秒")

    return PreviewScrapeResponse(
        preview_id=preview_id,
        category_id=category_id,
        category_name=category.name,
        total_scraped=len(preview_products),
        products=preview_products,
        errors=errors,
        expires_at=expires_at,
        duration_seconds=round(duration, 2),
    )


@router.post("/{category_id}/scrape-confirm", response_model=ConfirmScrapeResponse)
async def confirm_scrape_save(
    category_id: str,
    request: ConfirmScrapeRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    確認並保存預覽的抓取結果

    可以選擇保存全部或指定的商品
    """
    # 檢查預覽緩存
    if request.preview_id not in _preview_cache:
        raise HTTPException(status_code=404, detail="預覽數據不存在或已過期")

    cache_data = _preview_cache[request.preview_id]

    # 驗證類別匹配
    if cache_data["category_id"] != category_id:
        raise HTTPException(status_code=400, detail="類別 ID 不匹配")

    # 檢查是否過期
    if datetime.utcnow() > cache_data["expires_at"]:
        del _preview_cache[request.preview_id]
        raise HTTPException(status_code=410, detail="預覽數據已過期，請重新抓取")

    products_data = cache_data["products"]
    errors: List[str] = []
    saved_count = 0
    skipped_count = 0

    # 確定要保存的商品
    if request.selected_product_indices is not None:
        indices = set(request.selected_product_indices)
        products_to_save = [
            products_data[i] for i in range(len(products_data))
            if i in indices
        ]
        skipped_count = len(products_data) - len(products_to_save)
    else:
        products_to_save = products_data

    logger.info(f"確認保存: {len(products_to_save)} 個商品 (跳過 {skipped_count} 個)")

    # 保存到數據庫
    for item in products_to_save:
        try:
            # 檢查商品是否已存在
            existing = await db.execute(
                select(CategoryProduct).where(
                    CategoryProduct.category_id == UUID(category_id),
                    CategoryProduct.url == item["url"]
                )
            )
            existing_product = existing.scalar_one_or_none()

            if existing_product:
                # 更新現有商品
                existing_product.name = item["name"]
                existing_product.price = Decimal(str(item["price"])) if item["price"] else None
                existing_product.original_price = Decimal(str(item["original_price"])) if item["original_price"] else None
                existing_product.discount_percent = Decimal(str(item["discount_percent"])) if item["discount_percent"] else None
                existing_product.stock_status = item["stock_status"]
                existing_product.brand = item["brand"]
                existing_product.sku = item["sku"]
                existing_product.image_url = item["image_url"]
                existing_product.rating = Decimal(str(item["rating"])) if item["rating"] else None
                existing_product.review_count = item["review_count"]
                existing_product.unit_price = Decimal(str(item["unit_price"])) if item["unit_price"] else None
                existing_product.unit_type = item["unit_type"]
                existing_product.is_available = item["stock_status"] != "out_of_stock"
                existing_product.last_updated_at = datetime.utcnow()
                logger.info(f"更新商品: {item['name']}")
            else:
                # 創建新商品
                new_product = CategoryProduct(
                    category_id=UUID(category_id),
                    name=item["name"],
                    url=item["url"],
                    price=Decimal(str(item["price"])) if item["price"] else None,
                    original_price=Decimal(str(item["original_price"])) if item["original_price"] else None,
                    discount_percent=Decimal(str(item["discount_percent"])) if item["discount_percent"] else None,
                    stock_status=item["stock_status"],
                    brand=item["brand"],
                    sku=item["sku"],
                    image_url=item["image_url"],
                    rating=Decimal(str(item["rating"])) if item["rating"] else None,
                    review_count=item["review_count"],
                    unit_price=Decimal(str(item["unit_price"])) if item["unit_price"] else None,
                    unit_type=item["unit_type"],
                    is_available=item["stock_status"] != "out_of_stock" if item["stock_status"] else True,
                )
                db.add(new_product)
                logger.info(f"新增商品: {item['name']}")

            saved_count += 1

        except Exception as e:
            logger.error(f"保存商品失敗: {e}")
            errors.append(f"保存失敗 ({item.get('name', 'unknown')}): {str(e)}")

    # 更新類別統計
    try:
        count_result = await db.execute(
            select(func.count(CategoryProduct.id)).where(
                CategoryProduct.category_id == UUID(category_id)
            )
        )
        total_count = count_result.scalar() or 0

        await db.execute(
            update(CategoryDatabase)
            .where(CategoryDatabase.id == UUID(category_id))
            .values(
                total_products=total_count,
                last_scraped_at=datetime.utcnow()
            )
        )

        await db.commit()
    except Exception as e:
        logger.error(f"更新類別統計失敗: {e}")
        await db.rollback()
        errors.append(f"更新統計失敗: {str(e)}")

    # 清除緩存
    del _preview_cache[request.preview_id]

    logger.info(f"確認保存完成: 保存 {saved_count} 個, 跳過 {skipped_count} 個")

    return ConfirmScrapeResponse(
        success=saved_count > 0,
        message=f"已保存 {saved_count} 個商品" if saved_count > 0 else "未保存任何商品",
        saved_count=saved_count,
        skipped_count=skipped_count,
        errors=errors,
    )


@router.get("/{category_id}/scrape-preview/{preview_id}")
async def get_scrape_preview(
    category_id: str,
    preview_id: str,
):
    """
    獲取預覽抓取結果

    用於查看之前的預覽數據（如果尚未過期）
    """
    if preview_id not in _preview_cache:
        raise HTTPException(status_code=404, detail="預覽數據不存在或已過期")

    cache_data = _preview_cache[preview_id]

    if cache_data["category_id"] != category_id:
        raise HTTPException(status_code=400, detail="類別 ID 不匹配")

    if datetime.utcnow() > cache_data["expires_at"]:
        del _preview_cache[preview_id]
        raise HTTPException(status_code=410, detail="預覽數據已過期")

    return {
        "preview_id": preview_id,
        "category_id": category_id,
        "category_name": cache_data["category_name"],
        "total_products": len(cache_data["products"]),
        "products": cache_data["products"],
        "expires_at": cache_data["expires_at"].isoformat(),
    }


@router.delete("/{category_id}/scrape-preview/{preview_id}")
async def cancel_scrape_preview(
    category_id: str,
    preview_id: str,
):
    """
    取消/刪除預覽抓取結果

    用於放棄預覽的抓取數據
    """
    if preview_id not in _preview_cache:
        raise HTTPException(status_code=404, detail="預覽數據不存在或已過期")

    cache_data = _preview_cache[preview_id]

    if cache_data["category_id"] != category_id:
        raise HTTPException(status_code=400, detail="類別 ID 不匹配")

    del _preview_cache[preview_id]

    return {
        "success": True,
        "message": "預覽數據已刪除",
    }


# =============================================
# 智能抓取 API（優化版）
# =============================================

class SmartScrapeRequest(BaseModel):
    """智能抓取請求"""
    max_new_products: int = Field(default=10, ge=0, le=50)
    max_updates: int = Field(default=20, ge=0, le=100)


class SmartScrapeResponse(BaseModel):
    """智能抓取響應"""
    success: bool
    message: str
    category_name: str
    new_products: int
    updated_products: int
    failed: int
    credits_used: int
    errors: List[str]


class SetProductPriorityRequest(BaseModel):
    """設置商品優先級請求"""
    priority: str = Field(..., pattern="^(high|normal|low)$")
    product_ids: Optional[List[str]] = None  # None 表示全部


class QuotaUsageResponse(BaseModel):
    """配額使用響應"""
    # 本地統計（從數據庫）
    daily_usage: int
    monthly_usage: int
    # Firecrawl API 真實配額
    remaining_credits: int
    plan_credits: int
    used_credits: int
    usage_percent: float
    billing_period_start: Optional[str] = None
    billing_period_end: Optional[str] = None
    days_remaining: int = 0
    # 狀態
    is_low: bool = False
    is_critical: bool = False
    error_message: Optional[str] = None


class ProductPriorityResponse(BaseModel):
    """商品優先級響應"""
    id: str
    name: str
    monitor_priority: str
    update_frequency_hours: int
    last_updated_at: Optional[datetime]
    is_monitored: bool

    class Config:
        from_attributes = True


@router.post("/{category_id}/smart-scrape", response_model=SmartScrapeResponse)
async def smart_scrape_category(
    category_id: str,
    request: SmartScrapeRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    智能抓取類別商品（優化版）

    特點：
    1. 使用 URL 緩存，避免重複發現
    2. 增量更新，只抓取需要更新的商品
    3. 優先級調度，高頻監控重要商品

    Credits 消耗估算：
    - 有緩存時：max_new_products + max_updates
    - 無緩存時：max_new_products + max_updates + 4（URL 發現）
    """
    # 驗證類別存在
    result = await db.execute(
        select(CategoryDatabase).where(CategoryDatabase.id == UUID(category_id))
    )
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="類別數據庫不存在")

    if not category.hktv_category_url:
        raise HTTPException(status_code=400, detail="類別缺少 HKTVmall URL")

    logger.info(f"開始智能抓取: {category.name}")

    try:
        from app.services.smart_scraper import get_smart_scrape_service

        service = get_smart_scrape_service(db)
        stats = await service.smart_update_category(
            category,
            max_new_products=request.max_new_products,
            max_updates=request.max_updates
        )

        return SmartScrapeResponse(
            success=True,
            message=f"智能抓取完成，消耗 {stats['credits_used']} credits",
            category_name=category.name,
            new_products=stats["new_products"],
            updated_products=stats["updated_products"],
            failed=stats["failed"],
            credits_used=stats["credits_used"],
            errors=stats.get("errors", []),
        )

    except Exception as e:
        logger.error(f"智能抓取失敗: {e}")
        raise HTTPException(status_code=500, detail=f"智能抓取失敗: {str(e)}")


@router.put("/{category_id}/products/priority", response_model=Dict[str, Any])
async def set_products_priority(
    category_id: str,
    request: SetProductPriorityRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    設置商品監控優先級

    優先級說明：
    - high: 每日更新（適合直接競品、價格敏感商品）
    - normal: 每週更新（默認，適合一般商品）
    - low: 每月更新（適合穩定價格商品）
    """
    # 驗證類別存在
    result = await db.execute(
        select(CategoryDatabase).where(CategoryDatabase.id == UUID(category_id))
    )
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="類別數據庫不存在")

    # 設置更新頻率
    frequency_map = {
        "high": 24,      # 24 小時
        "normal": 168,   # 7 天
        "low": 720,      # 30 天
    }
    update_frequency = frequency_map[request.priority]

    # 更新商品優先級
    if request.product_ids:
        # 更新指定商品
        product_uuids = [UUID(pid) for pid in request.product_ids]
        await db.execute(
            update(CategoryProduct)
            .where(
                CategoryProduct.category_id == UUID(category_id),
                CategoryProduct.id.in_(product_uuids)
            )
            .values(
                monitor_priority=request.priority,
                update_frequency_hours=update_frequency
            )
        )
        updated_count = len(request.product_ids)
    else:
        # 更新全部商品
        result = await db.execute(
            update(CategoryProduct)
            .where(CategoryProduct.category_id == UUID(category_id))
            .values(
                monitor_priority=request.priority,
                update_frequency_hours=update_frequency
            )
        )
        updated_count = result.rowcount

    await db.commit()

    return {
        "success": True,
        "message": f"已更新 {updated_count} 個商品的優先級為 {request.priority}",
        "updated_count": updated_count,
        "priority": request.priority,
        "update_frequency_hours": update_frequency,
    }


@router.get("/{category_id}/products/priorities", response_model=List[ProductPriorityResponse])
async def get_products_priorities(
    category_id: str,
    priority: Optional[str] = Query(None, pattern="^(high|normal|low)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """
    獲取商品優先級列表

    可按優先級過濾
    """
    query = select(CategoryProduct).where(
        CategoryProduct.category_id == UUID(category_id)
    )

    if priority:
        query = query.where(CategoryProduct.monitor_priority == priority)

    query = query.order_by(
        CategoryProduct.monitor_priority.desc(),
        CategoryProduct.last_updated_at.asc().nullsfirst()
    ).offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    products = result.scalars().all()

    return [
        ProductPriorityResponse(
            id=str(p.id),
            name=p.name,
            monitor_priority=p.monitor_priority or "normal",
            update_frequency_hours=p.update_frequency_hours or 168,
            last_updated_at=p.last_updated_at,
            is_monitored=p.is_monitored if p.is_monitored is not None else True,
        )
        for p in products
    ]


@router.get("/quota/usage", response_model=QuotaUsageResponse)
async def get_quota_usage(
    db: AsyncSession = Depends(get_db),
):
    """
    獲取 Firecrawl API 配額使用情況

    整合：
    1. 本地數據庫統計（今日/本月使用量）
    2. Firecrawl API 真實配額（剩餘額度、計劃總額）
    """
    from app.models.category import ScrapeQuotaUsage
    from app.services.firecrawl_quota import get_firecrawl_quota_service

    now = datetime.utcnow()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    first_day = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # ==================== 本地統計 ====================
    # 今日使用量
    daily_result = await db.execute(
        select(func.sum(ScrapeQuotaUsage.credits_used)).where(
            ScrapeQuotaUsage.created_at >= today
        )
    )
    daily_usage = daily_result.scalar() or 0

    # 本月使用量
    monthly_result = await db.execute(
        select(func.sum(ScrapeQuotaUsage.credits_used)).where(
            ScrapeQuotaUsage.created_at >= first_day
        )
    )
    monthly_usage = monthly_result.scalar() or 0

    # ==================== Firecrawl API 配額 ====================
    quota_service = get_firecrawl_quota_service()
    quota_status = await quota_service.get_quota()

    if quota_status.success and quota_status.quota:
        quota = quota_status.quota
        return QuotaUsageResponse(
            # 本地統計
            daily_usage=daily_usage,
            monthly_usage=monthly_usage,
            # Firecrawl 真實配額
            remaining_credits=quota.remaining_credits,
            plan_credits=quota.plan_credits,
            used_credits=quota.plan_credits - quota.remaining_credits,
            usage_percent=quota.usage_percent,
            billing_period_start=quota.billing_period_start.isoformat() if quota.billing_period_start else None,
            billing_period_end=quota.billing_period_end.isoformat() if quota.billing_period_end else None,
            days_remaining=quota.days_remaining,
            # 狀態
            is_low=quota_status.is_low,
            is_critical=quota_status.is_critical,
        )
    else:
        # API 調用失敗，返回本地統計 + 錯誤信息
        return QuotaUsageResponse(
            daily_usage=daily_usage,
            monthly_usage=monthly_usage,
            remaining_credits=0,
            plan_credits=0,
            used_credits=0,
            usage_percent=0,
            is_low=False,
            is_critical=True,
            error_message=quota_status.error_message or "無法獲取 Firecrawl 配額",
        )


@router.get("/quota/history")
async def get_quota_history(
    days: int = Query(7, ge=1, le=30),
    db: AsyncSession = Depends(get_db),
):
    """
    獲取配額使用歷史

    按天分組顯示使用量
    """
    from app.models.category import ScrapeQuotaUsage

    start_date = datetime.utcnow() - timedelta(days=days)

    result = await db.execute(
        select(
            func.date(ScrapeQuotaUsage.created_at).label("date"),
            func.sum(ScrapeQuotaUsage.credits_used).label("credits"),
            func.count(ScrapeQuotaUsage.id).label("operations")
        ).where(
            ScrapeQuotaUsage.created_at >= start_date
        ).group_by(
            func.date(ScrapeQuotaUsage.created_at)
        ).order_by(
            func.date(ScrapeQuotaUsage.created_at).desc()
        )
    )

    history = []
    for row in result.fetchall():
        history.append({
            "date": row.date.isoformat() if row.date else None,
            "credits_used": row.credits or 0,
            "operations_count": row.operations or 0,
        })

    return {
        "days": days,
        "history": history,
        "total_credits": sum(h["credits_used"] for h in history),
    }
