# =============================================
# 數據抓取 API
# =============================================

from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy import select, func, desc, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
import asyncio
import json
import logging

from app.models.database import get_db
from app.models.system import ScrapeLog, SystemSetting
from app.models.competitor import Competitor, CompetitorProduct
from app.models.scrape_config import ScrapeConfig
from app.models.import_job import ImportJob, ImportJobItem
from app.services import (
    ScrapeExecutor,
    SmartScrapeExecutor,
    ScrapeConfig as ScrapeConfigService,
    ScrapeResult,
    BatchOptimizer,
    BatchConfig,
    BatchProgress,
    get_smart_scrape_executor,
    get_batch_optimizer,
)

logger = logging.getLogger(__name__)


router = APIRouter()


# =============================================
# Schema 定義
# =============================================

class ScrapeLogResponse(BaseModel):
    id: str
    task_id: Optional[str]
    task_type: Optional[str]
    competitor_id: Optional[str]
    competitor_name: Optional[str]
    status: str
    products_total: int
    products_scraped: int
    products_failed: int
    errors: Optional[list]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    duration_seconds: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class ScrapeLogListResponse(BaseModel):
    items: list[ScrapeLogResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ScrapeStatsResponse(BaseModel):
    total_scrapes: int
    successful_scrapes: int
    failed_scrapes: int
    products_scraped_today: int
    last_scrape_at: Optional[datetime]
    avg_duration_seconds: Optional[float]
    success_rate: float


class TriggerScrapeRequest(BaseModel):
    competitor_id: Optional[str] = None
    scrape_all: bool = False


class TriggerScrapeResponse(BaseModel):
    task_id: str
    message: str
    competitors_queued: int = 0


class ScrapePreviewRequest(BaseModel):
    """抓取預覽請求"""
    url: str = Field(..., min_length=1, max_length=2000)
    use_actions: bool = False  # 是否使用 Actions 處理動態頁面


class DiscoverUrlsRequest(BaseModel):
    """URL 發現請求"""
    base_url: str = Field(..., min_length=1, max_length=2000)
    keywords: Optional[List[str]] = None  # 過濾關鍵詞


class DiscoverUrlsResponse(BaseModel):
    """URL 發現響應"""
    urls: List[str]
    total: int


class ScrapePreviewResponse(BaseModel):
    """抓取預覽響應"""
    success: bool
    url: str
    name: Optional[str] = None
    price: Optional[Decimal] = None
    original_price: Optional[Decimal] = None
    discount_percent: Optional[Decimal] = None
    stock_status: Optional[str] = None
    image_url: Optional[str] = None
    sku: Optional[str] = None
    brand: Optional[str] = None
    rating: Optional[Decimal] = None
    review_count: Optional[int] = None
    promotion_text: Optional[str] = None
    description: Optional[str] = None
    raw_data: Optional[dict] = None
    error: Optional[str] = None
    duration_ms: Optional[int] = None


class ScheduleConfigResponse(BaseModel):
    """定時任務配置響應"""
    enabled: bool
    cron_expression: str
    last_run_at: Optional[datetime] = None
    next_run_at: Optional[datetime] = None


class ScheduleConfigUpdate(BaseModel):
    """定時任務配置更新"""
    enabled: Optional[bool] = None
    cron_expression: Optional[str] = Field(None, max_length=100)


class RetryFailedRequest(BaseModel):
    """重試失敗商品請求"""
    product_ids: Optional[List[str]] = None
    retry_all: bool = False


class RetryFailedResponse(BaseModel):
    """重試失敗商品響應"""
    queued_count: int
    message: str


class FailedProductResponse(BaseModel):
    """失敗商品響應"""
    id: str
    name: str
    url: str
    competitor_name: str
    error: Optional[str]
    last_scraped_at: Optional[datetime]


# =============================================
# 平台配置 Schema
# =============================================

class ScrapeConfigResponse(BaseModel):
    """平台爬取配置響應"""
    id: str
    platform: str
    product_schema: Optional[Dict[str, Any]] = None
    rate_limit_requests: int
    rate_limit_window_seconds: int
    concurrent_limit: int
    max_retries: int
    retry_delay_seconds: int
    timeout_seconds: int
    proxy_enabled: bool
    proxy_pool: Optional[List[str]] = None
    custom_headers: Optional[Dict[str, str]] = None
    use_actions: bool
    actions_config: Optional[Dict[str, Any]] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ScrapeConfigCreate(BaseModel):
    """創建平台配置"""
    platform: str = Field(..., min_length=1, max_length=100)
    product_schema: Optional[Dict[str, Any]] = None
    rate_limit_requests: int = Field(default=10, ge=1, le=1000)
    rate_limit_window_seconds: int = Field(default=60, ge=1, le=3600)
    concurrent_limit: int = Field(default=3, ge=1, le=50)
    max_retries: int = Field(default=3, ge=0, le=10)
    retry_delay_seconds: int = Field(default=5, ge=1, le=300)
    timeout_seconds: int = Field(default=30, ge=5, le=300)
    proxy_enabled: bool = False
    proxy_pool: Optional[List[str]] = None
    custom_headers: Optional[Dict[str, str]] = None
    use_actions: bool = False
    actions_config: Optional[Dict[str, Any]] = None


class ScrapeConfigUpdate(BaseModel):
    """更新平台配置"""
    product_schema: Optional[Dict[str, Any]] = None
    rate_limit_requests: Optional[int] = Field(default=None, ge=1, le=1000)
    rate_limit_window_seconds: Optional[int] = Field(default=None, ge=1, le=3600)
    concurrent_limit: Optional[int] = Field(default=None, ge=1, le=50)
    max_retries: Optional[int] = Field(default=None, ge=0, le=10)
    retry_delay_seconds: Optional[int] = Field(default=None, ge=1, le=300)
    timeout_seconds: Optional[int] = Field(default=None, ge=5, le=300)
    proxy_enabled: Optional[bool] = None
    proxy_pool: Optional[List[str]] = None
    custom_headers: Optional[Dict[str, str]] = None
    use_actions: Optional[bool] = None
    actions_config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class ScrapeConfigListResponse(BaseModel):
    """平台配置列表響應"""
    items: List[ScrapeConfigResponse]
    total: int


class ScrapeConfigTestRequest(BaseModel):
    """測試配置請求"""
    test_url: str = Field(..., min_length=1, max_length=2000)


class ScrapeConfigTestResponse(BaseModel):
    """測試配置響應"""
    success: bool
    platform: str
    url: str
    duration_ms: int
    product_name: Optional[str] = None
    price: Optional[Decimal] = None
    error: Optional[str] = None
    raw_data: Optional[Dict[str, Any]] = None


# =============================================
# 智能抓取 Schema
# =============================================

class SmartScrapeRequest(BaseModel):
    """智能抓取請求"""
    url: str = Field(..., min_length=1, max_length=2000)
    force_actions: bool = False  # 強制使用 Actions


class SmartScrapeResponse(BaseModel):
    """智能抓取響應"""
    success: bool
    url: str
    strategy_used: str  # basic, actions, llm_extract
    duration_ms: int
    retries: int
    name: Optional[str] = None
    price: Optional[Decimal] = None
    original_price: Optional[Decimal] = None
    stock_status: Optional[str] = None
    image_url: Optional[str] = None
    brand: Optional[str] = None
    error: Optional[str] = None
    error_type: Optional[str] = None


# =============================================
# 批量抓取 Schema
# =============================================

class BatchScrapeRequest(BaseModel):
    """批量抓取請求"""
    urls: List[str] = Field(..., min_items=1, max_items=500)
    max_concurrent: int = Field(default=5, ge=1, le=20)
    domain_concurrent: int = Field(default=2, ge=1, le=10)


class BatchScrapeItemResult(BaseModel):
    """批量抓取單項結果"""
    url: str
    success: bool
    name: Optional[str] = None
    price: Optional[Decimal] = None
    error: Optional[str] = None


class BatchScrapeProgress(BaseModel):
    """批量抓取進度"""
    total: int
    processed: int
    successful: int
    failed: int
    progress_percent: float
    success_rate: float
    current_concurrency: int


class BatchScrapeResponse(BaseModel):
    """批量抓取響應"""
    total: int
    successful: int
    failed: int
    results: List[BatchScrapeItemResult]
    duration_seconds: float


# =============================================
# URL 驗證 Schema
# =============================================

class ValidateUrlRequest(BaseModel):
    """URL 驗證請求"""
    url: str = Field(..., min_length=1, max_length=2000)


class ValidateUrlResponse(BaseModel):
    """URL 驗證響應"""
    valid: bool
    url: str
    platform: Optional[str] = None
    has_config: bool = False
    error: Optional[str] = None


# =============================================
# 抓取日誌 API
# =============================================

@router.get("/logs", response_model=ScrapeLogListResponse)
async def list_scrape_logs(
    db: AsyncSession = Depends(get_db),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status: Optional[str] = None,
    task_type: Optional[str] = None,
    competitor_id: Optional[str] = None,
):
    """獲取抓取日誌列表"""
    query = select(ScrapeLog)

    if status:
        query = query.where(ScrapeLog.status == status)
    if task_type:
        query = query.where(ScrapeLog.task_type == task_type)
    if competitor_id:
        query = query.where(ScrapeLog.competitor_id == UUID(competitor_id))

    # 計算總數
    count_query = select(func.count()).select_from(query.subquery())
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0

    # 分頁查詢
    query = query.order_by(desc(ScrapeLog.created_at))
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    logs = result.scalars().all()

    # 獲取競爭對手名稱
    items = []
    for log in logs:
        competitor_name = None
        if log.competitor_id:
            comp_result = await db.execute(
                select(Competitor.name).where(Competitor.id == log.competitor_id)
            )
            competitor_name = comp_result.scalar()

        items.append(ScrapeLogResponse(
            id=str(log.id),
            task_id=log.task_id,
            task_type=log.task_type,
            competitor_id=str(log.competitor_id) if log.competitor_id else None,
            competitor_name=competitor_name,
            status=log.status,
            products_total=log.products_total,
            products_scraped=log.products_scraped,
            products_failed=log.products_failed,
            errors=log.errors,
            started_at=log.started_at,
            completed_at=log.completed_at,
            duration_seconds=log.duration_seconds,
            created_at=log.created_at,
        ))

    return ScrapeLogListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.get("/stats", response_model=ScrapeStatsResponse)
async def get_scrape_stats(
    db: AsyncSession = Depends(get_db),
    days: int = Query(default=7, ge=1, le=90),
):
    """獲取抓取統計數據"""
    since = datetime.utcnow() - timedelta(days=days)
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    # 總抓取次數
    total_query = select(func.count(ScrapeLog.id)).where(ScrapeLog.created_at >= since)
    total_result = await db.execute(total_query)
    total_scrapes = total_result.scalar() or 0

    # 成功抓取次數
    success_query = select(func.count(ScrapeLog.id)).where(
        ScrapeLog.created_at >= since,
        ScrapeLog.status.in_(["success", "partial"])
    )
    success_result = await db.execute(success_query)
    successful_scrapes = success_result.scalar() or 0

    # 失敗抓取次數
    failed_query = select(func.count(ScrapeLog.id)).where(
        ScrapeLog.created_at >= since,
        ScrapeLog.status == "failed"
    )
    failed_result = await db.execute(failed_query)
    failed_scrapes = failed_result.scalar() or 0

    # 今日抓取商品數
    today_query = select(func.sum(ScrapeLog.products_scraped)).where(
        ScrapeLog.created_at >= today_start
    )
    today_result = await db.execute(today_query)
    products_scraped_today = today_result.scalar() or 0

    # 最後抓取時間
    last_query = select(func.max(ScrapeLog.completed_at))
    last_result = await db.execute(last_query)
    last_scrape_at = last_result.scalar()

    # 平均耗時
    avg_query = select(func.avg(ScrapeLog.duration_seconds)).where(
        ScrapeLog.created_at >= since,
        ScrapeLog.duration_seconds.isnot(None)
    )
    avg_result = await db.execute(avg_query)
    avg_duration = avg_result.scalar()

    # 成功率
    success_rate = (successful_scrapes / total_scrapes * 100) if total_scrapes > 0 else 0

    return ScrapeStatsResponse(
        total_scrapes=total_scrapes,
        successful_scrapes=successful_scrapes,
        failed_scrapes=failed_scrapes,
        products_scraped_today=products_scraped_today,
        last_scrape_at=last_scrape_at,
        avg_duration_seconds=float(avg_duration) if avg_duration else None,
        success_rate=round(success_rate, 1),
    )


@router.post("/trigger", response_model=TriggerScrapeResponse)
async def trigger_scrape(
    request: TriggerScrapeRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """手動觸發抓取任務"""
    try:
        from app.tasks.scrape_tasks import scrape_competitor, scrape_all_competitors
    except ImportError:
        # Celery 未配置時的模擬響應
        if request.scrape_all:
            # 計算活躍競爭對手數量
            count_result = await db.execute(
                select(func.count(Competitor.id)).where(Competitor.is_active == True)
            )
            count = count_result.scalar() or 0
            return TriggerScrapeResponse(
                task_id="demo-task-all",
                message="已加入所有活躍競爭對手的抓取隊列（演示模式）",
                competitors_queued=count,
            )
        else:
            return TriggerScrapeResponse(
                task_id="demo-task-single",
                message="抓取任務已啟動（演示模式）",
                competitors_queued=1 if request.competitor_id else 0,
            )

    if request.scrape_all:
        # 抓取所有競爭對手
        task = scrape_all_competitors.delay()
        count_result = await db.execute(
            select(func.count(Competitor.id)).where(Competitor.is_active == True)
        )
        count = count_result.scalar() or 0
        return TriggerScrapeResponse(
            task_id=task.id,
            message="已加入所有活躍競爭對手的抓取隊列",
            competitors_queued=count,
        )
    elif request.competitor_id:
        # 抓取指定競爭對手
        result = await db.execute(
            select(Competitor).where(Competitor.id == UUID(request.competitor_id))
        )
        if not result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="競爭對手不存在")

        task = scrape_competitor.delay(request.competitor_id)
        return TriggerScrapeResponse(
            task_id=task.id,
            message="抓取任務已啟動",
            competitors_queued=1,
        )
    else:
        raise HTTPException(status_code=400, detail="請指定競爭對手或選擇抓取全部")


@router.get("/running", response_model=list[ScrapeLogResponse])
async def get_running_tasks(
    db: AsyncSession = Depends(get_db),
):
    """獲取正在運行的抓取任務"""
    query = select(ScrapeLog).where(
        ScrapeLog.status == "running"
    ).order_by(desc(ScrapeLog.started_at))

    result = await db.execute(query)
    logs = result.scalars().all()

    items = []
    for log in logs:
        competitor_name = None
        if log.competitor_id:
            comp_result = await db.execute(
                select(Competitor.name).where(Competitor.id == log.competitor_id)
            )
            competitor_name = comp_result.scalar()

        items.append(ScrapeLogResponse(
            id=str(log.id),
            task_id=log.task_id,
            task_type=log.task_type,
            competitor_id=str(log.competitor_id) if log.competitor_id else None,
            competitor_name=competitor_name,
            status=log.status,
            products_total=log.products_total,
            products_scraped=log.products_scraped,
            products_failed=log.products_failed,
            errors=log.errors,
            started_at=log.started_at,
            completed_at=log.completed_at,
            duration_seconds=log.duration_seconds,
            created_at=log.created_at,
        ))

    return items


# =============================================
# 抓取預覽測試 API
# =============================================

@router.post("/preview", response_model=ScrapePreviewResponse)
async def preview_scrape(
    request: ScrapePreviewRequest,
):
    """
    預覽抓取結果（不保存到數據庫）
    用於測試 URL 是否可以正確抓取

    - use_actions: 啟用 Actions 處理動態頁面（滾動、等待等）
    """
    import time
    start_time = time.time()

    try:
        from app.connectors.firecrawl import get_firecrawl_connector
        connector = get_firecrawl_connector()
        info = connector.extract_product_info(request.url, use_actions=request.use_actions)

        duration_ms = int((time.time() - start_time) * 1000)

        return ScrapePreviewResponse(
            success=True,
            url=request.url,
            name=info.name,
            price=info.price,
            original_price=info.original_price,
            discount_percent=info.discount_percent,
            stock_status=info.stock_status,
            image_url=info.image_url,
            sku=info.sku,
            brand=info.brand,
            rating=info.rating,
            review_count=info.review_count,
            promotion_text=info.promotion_text,
            description=info.description,
            raw_data=info.raw_data,
            duration_ms=duration_ms,
        )

    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        return ScrapePreviewResponse(
            success=False,
            url=request.url,
            error=str(e),
            duration_ms=duration_ms,
        )


@router.post("/discover", response_model=DiscoverUrlsResponse)
async def discover_urls(
    request: DiscoverUrlsRequest,
):
    """
    發現網站上的商品頁面 URL

    使用 Firecrawl 的 Map 功能快速獲取網站所有 URL，
    然後根據關鍵詞過濾出可能是商品頁面的 URL。

    - base_url: 網站根 URL
    - keywords: 過濾關鍵詞（如 ["product", "item"]）
    """
    try:
        from app.connectors.firecrawl import get_firecrawl_connector
        connector = get_firecrawl_connector()

        urls = connector.discover_product_urls(
            request.base_url,
            keywords=request.keywords
        )

        return DiscoverUrlsResponse(
            urls=urls,
            total=len(urls)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================
# 定時任務配置 API
# =============================================

@router.get("/schedule", response_model=ScheduleConfigResponse)
async def get_schedule_config(
    db: AsyncSession = Depends(get_db),
):
    """獲取定時任務配置"""
    # 查詢系統設置
    enabled_result = await db.execute(
        select(SystemSetting).where(SystemSetting.key == "scrape_schedule_enabled")
    )
    enabled_setting = enabled_result.scalar_one_or_none()

    cron_result = await db.execute(
        select(SystemSetting).where(SystemSetting.key == "scrape_schedule_cron")
    )
    cron_setting = cron_result.scalar_one_or_none()

    last_run_result = await db.execute(
        select(SystemSetting).where(SystemSetting.key == "scrape_schedule_last_run")
    )
    last_run_setting = last_run_result.scalar_one_or_none()

    enabled = enabled_setting.value == "true" if enabled_setting else False
    cron_expression = cron_setting.value if cron_setting else "0 2 * * *"  # 默認每天凌晨2點
    last_run_at = None
    if last_run_setting and last_run_setting.value:
        try:
            last_run_at = datetime.fromisoformat(last_run_setting.value)
        except ValueError:
            pass

    # 計算下次運行時間（簡化處理）
    next_run_at = None
    if enabled:
        # 簡單計算：假設每天運行，下次運行時間為明天同一時間
        from croniter import croniter
        try:
            cron = croniter(cron_expression, datetime.utcnow())
            next_run_at = cron.get_next(datetime)
        except Exception:
            pass

    return ScheduleConfigResponse(
        enabled=enabled,
        cron_expression=cron_expression,
        last_run_at=last_run_at,
        next_run_at=next_run_at,
    )


@router.put("/schedule", response_model=ScheduleConfigResponse)
async def update_schedule_config(
    config: ScheduleConfigUpdate,
    db: AsyncSession = Depends(get_db),
):
    """更新定時任務配置"""
    if config.enabled is not None:
        await _upsert_setting(db, "scrape_schedule_enabled", "true" if config.enabled else "false")

    if config.cron_expression is not None:
        # 驗證 cron 表達式
        try:
            from croniter import croniter
            croniter(config.cron_expression)
        except Exception:
            raise HTTPException(status_code=400, detail="無效的 cron 表達式")
        await _upsert_setting(db, "scrape_schedule_cron", config.cron_expression)

    await db.commit()

    # 返回更新後的配置
    return await get_schedule_config(db)


async def _upsert_setting(db: AsyncSession, key: str, value: str):
    """更新或創建系統設置"""
    result = await db.execute(
        select(SystemSetting).where(SystemSetting.key == key)
    )
    setting = result.scalar_one_or_none()

    if setting:
        setting.value = value
    else:
        setting = SystemSetting(key=key, value=value)
        db.add(setting)


# =============================================
# 錯誤重試 API
# =============================================

@router.get("/failed", response_model=List[FailedProductResponse])
async def get_failed_products(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(default=50, ge=1, le=200),
):
    """獲取抓取失敗的商品列表"""
    query = select(CompetitorProduct).where(
        CompetitorProduct.scrape_error.isnot(None),
        CompetitorProduct.is_active == True
    ).order_by(CompetitorProduct.last_scraped_at.desc()).limit(limit)

    result = await db.execute(query)
    products = result.scalars().all()

    items = []
    for product in products:
        # 獲取競爭對手名稱
        comp_result = await db.execute(
            select(Competitor.name).where(Competitor.id == product.competitor_id)
        )
        competitor_name = comp_result.scalar() or "未知"

        items.append(FailedProductResponse(
            id=str(product.id),
            name=product.name,
            url=product.url,
            competitor_name=competitor_name,
            error=product.scrape_error,
            last_scraped_at=product.last_scraped_at,
        ))

    return items


@router.post("/retry", response_model=RetryFailedResponse)
async def retry_failed_products(
    request: RetryFailedRequest,
    db: AsyncSession = Depends(get_db),
):
    """重試失敗的商品抓取"""
    try:
        from app.tasks.scrape_tasks import scrape_single_product
    except ImportError:
        # Celery 未配置時的模擬響應
        if request.retry_all:
            count_result = await db.execute(
                select(func.count(CompetitorProduct.id)).where(
                    CompetitorProduct.scrape_error.isnot(None),
                    CompetitorProduct.is_active == True
                )
            )
            count = count_result.scalar() or 0
        else:
            count = len(request.product_ids) if request.product_ids else 0

        return RetryFailedResponse(
            queued_count=count,
            message=f"已加入 {count} 個商品到重試隊列（演示模式）"
        )

    queued_count = 0

    if request.retry_all:
        # 重試所有失敗商品
        result = await db.execute(
            select(CompetitorProduct.id).where(
                CompetitorProduct.scrape_error.isnot(None),
                CompetitorProduct.is_active == True
            )
        )
        product_ids = result.scalars().all()

        for product_id in product_ids:
            scrape_single_product.delay(str(product_id))
            queued_count += 1

    elif request.product_ids:
        # 重試指定商品
        for product_id in request.product_ids:
            # 驗證商品存在
            result = await db.execute(
                select(CompetitorProduct).where(CompetitorProduct.id == UUID(product_id))
            )
            if result.scalar_one_or_none():
                scrape_single_product.delay(product_id)
                queued_count += 1

    # 清除已重試商品的錯誤標記
    if request.retry_all:
        await db.execute(
            update(CompetitorProduct)
            .where(CompetitorProduct.scrape_error.isnot(None))
            .values(scrape_error=None)
        )
    elif request.product_ids:
        for product_id in request.product_ids:
            await db.execute(
                update(CompetitorProduct)
                .where(CompetitorProduct.id == UUID(product_id))
                .values(scrape_error=None)
            )

    await db.commit()

    return RetryFailedResponse(
        queued_count=queued_count,
        message=f"已加入 {queued_count} 個商品到重試隊列"
    )


# =============================================
# 平台配置管理 API
# =============================================

@router.get("/configs", response_model=ScrapeConfigListResponse)
async def list_scrape_configs(
    db: AsyncSession = Depends(get_db),
    is_active: Optional[bool] = None,
):
    """獲取所有平台爬取配置"""
    query = select(ScrapeConfig)

    if is_active is not None:
        query = query.where(ScrapeConfig.is_active == is_active)

    query = query.order_by(ScrapeConfig.platform)

    result = await db.execute(query)
    configs = result.scalars().all()

    items = [
        ScrapeConfigResponse(
            id=str(config.id),
            platform=config.platform,
            product_schema=config.product_schema,
            rate_limit_requests=config.rate_limit_requests,
            rate_limit_window_seconds=config.rate_limit_window_seconds,
            concurrent_limit=config.concurrent_limit,
            max_retries=config.max_retries,
            retry_delay_seconds=config.retry_delay_seconds,
            timeout_seconds=config.timeout_seconds,
            proxy_enabled=config.proxy_enabled,
            proxy_pool=config.proxy_pool,
            custom_headers=config.custom_headers,
            use_actions=config.use_actions,
            actions_config=config.actions_config,
            is_active=config.is_active,
            created_at=config.created_at,
            updated_at=config.updated_at,
        )
        for config in configs
    ]

    return ScrapeConfigListResponse(items=items, total=len(items))


@router.post("/configs", response_model=ScrapeConfigResponse, status_code=201)
async def create_scrape_config(
    config_data: ScrapeConfigCreate,
    db: AsyncSession = Depends(get_db),
):
    """創建平台爬取配置"""
    # 檢查平台是否已存在
    existing = await db.execute(
        select(ScrapeConfig).where(ScrapeConfig.platform == config_data.platform)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail=f"平台 '{config_data.platform}' 的配置已存在"
        )

    config = ScrapeConfig(
        platform=config_data.platform,
        product_schema=config_data.product_schema,
        rate_limit_requests=config_data.rate_limit_requests,
        rate_limit_window_seconds=config_data.rate_limit_window_seconds,
        concurrent_limit=config_data.concurrent_limit,
        max_retries=config_data.max_retries,
        retry_delay_seconds=config_data.retry_delay_seconds,
        timeout_seconds=config_data.timeout_seconds,
        proxy_enabled=config_data.proxy_enabled,
        proxy_pool=config_data.proxy_pool,
        custom_headers=config_data.custom_headers,
        use_actions=config_data.use_actions,
        actions_config=config_data.actions_config,
    )

    db.add(config)
    await db.commit()
    await db.refresh(config)

    return ScrapeConfigResponse(
        id=str(config.id),
        platform=config.platform,
        product_schema=config.product_schema,
        rate_limit_requests=config.rate_limit_requests,
        rate_limit_window_seconds=config.rate_limit_window_seconds,
        concurrent_limit=config.concurrent_limit,
        max_retries=config.max_retries,
        retry_delay_seconds=config.retry_delay_seconds,
        timeout_seconds=config.timeout_seconds,
        proxy_enabled=config.proxy_enabled,
        proxy_pool=config.proxy_pool,
        custom_headers=config.custom_headers,
        use_actions=config.use_actions,
        actions_config=config.actions_config,
        is_active=config.is_active,
        created_at=config.created_at,
        updated_at=config.updated_at,
    )


@router.get("/configs/{platform}", response_model=ScrapeConfigResponse)
async def get_scrape_config(
    platform: str,
    db: AsyncSession = Depends(get_db),
):
    """獲取指定平台的爬取配置"""
    result = await db.execute(
        select(ScrapeConfig).where(ScrapeConfig.platform == platform)
    )
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(
            status_code=404,
            detail=f"平台 '{platform}' 的配置不存在"
        )

    return ScrapeConfigResponse(
        id=str(config.id),
        platform=config.platform,
        product_schema=config.product_schema,
        rate_limit_requests=config.rate_limit_requests,
        rate_limit_window_seconds=config.rate_limit_window_seconds,
        concurrent_limit=config.concurrent_limit,
        max_retries=config.max_retries,
        retry_delay_seconds=config.retry_delay_seconds,
        timeout_seconds=config.timeout_seconds,
        proxy_enabled=config.proxy_enabled,
        proxy_pool=config.proxy_pool,
        custom_headers=config.custom_headers,
        use_actions=config.use_actions,
        actions_config=config.actions_config,
        is_active=config.is_active,
        created_at=config.created_at,
        updated_at=config.updated_at,
    )


@router.put("/configs/{platform}", response_model=ScrapeConfigResponse)
async def update_scrape_config(
    platform: str,
    config_data: ScrapeConfigUpdate,
    db: AsyncSession = Depends(get_db),
):
    """更新平台爬取配置"""
    result = await db.execute(
        select(ScrapeConfig).where(ScrapeConfig.platform == platform)
    )
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(
            status_code=404,
            detail=f"平台 '{platform}' 的配置不存在"
        )

    # 更新非 None 的欄位
    update_data = config_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            setattr(config, key, value)

    await db.commit()
    await db.refresh(config)

    return ScrapeConfigResponse(
        id=str(config.id),
        platform=config.platform,
        product_schema=config.product_schema,
        rate_limit_requests=config.rate_limit_requests,
        rate_limit_window_seconds=config.rate_limit_window_seconds,
        concurrent_limit=config.concurrent_limit,
        max_retries=config.max_retries,
        retry_delay_seconds=config.retry_delay_seconds,
        timeout_seconds=config.timeout_seconds,
        proxy_enabled=config.proxy_enabled,
        proxy_pool=config.proxy_pool,
        custom_headers=config.custom_headers,
        use_actions=config.use_actions,
        actions_config=config.actions_config,
        is_active=config.is_active,
        created_at=config.created_at,
        updated_at=config.updated_at,
    )


@router.delete("/configs/{platform}", status_code=204)
async def delete_scrape_config(
    platform: str,
    db: AsyncSession = Depends(get_db),
):
    """刪除平台爬取配置"""
    result = await db.execute(
        select(ScrapeConfig).where(ScrapeConfig.platform == platform)
    )
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(
            status_code=404,
            detail=f"平台 '{platform}' 的配置不存在"
        )

    await db.execute(
        delete(ScrapeConfig).where(ScrapeConfig.platform == platform)
    )
    await db.commit()


@router.post("/configs/{platform}/test", response_model=ScrapeConfigTestResponse)
async def test_scrape_config(
    platform: str,
    request: ScrapeConfigTestRequest,
    db: AsyncSession = Depends(get_db),
):
    """測試平台爬取配置"""
    import time

    # 獲取配置
    result = await db.execute(
        select(ScrapeConfig).where(ScrapeConfig.platform == platform)
    )
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(
            status_code=404,
            detail=f"平台 '{platform}' 的配置不存在"
        )

    start_time = time.time()

    try:
        from app.connectors.firecrawl import get_firecrawl_connector
        connector = get_firecrawl_connector()
        info = connector.extract_product_info(
            request.test_url,
            use_actions=config.use_actions
        )

        duration_ms = int((time.time() - start_time) * 1000)

        return ScrapeConfigTestResponse(
            success=True,
            platform=platform,
            url=request.test_url,
            duration_ms=duration_ms,
            product_name=info.name,
            price=info.price,
            raw_data=info.raw_data,
        )

    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        return ScrapeConfigTestResponse(
            success=False,
            platform=platform,
            url=request.test_url,
            duration_ms=duration_ms,
            error=str(e),
        )


# =============================================
# 智能抓取 API
# =============================================

@router.post("/smart", response_model=SmartScrapeResponse)
async def smart_scrape(
    request: SmartScrapeRequest,
):
    """
    智能抓取（自動識別最佳策略）

    自動識別頁面結構，選擇最佳抓取策略：
    1. 基礎抓取 - 靜態頁面
    2. Actions 抓取 - 動態頁面（滾動、等待等）
    3. LLM 提取 - 複雜結構頁面
    """
    import time
    start_time = time.time()

    try:
        executor = get_smart_scrape_executor()
        result = await executor.smart_execute(request.url)

        duration_ms = int((time.time() - start_time) * 1000)

        return SmartScrapeResponse(
            success=result.success,
            url=result.url,
            strategy_used=result.strategy_used or "basic",
            duration_ms=duration_ms,
            retries=result.retries,
            name=result.data.get("name") if result.data else None,
            price=Decimal(str(result.data.get("price"))) if result.data and result.data.get("price") else None,
            original_price=Decimal(str(result.data.get("original_price"))) if result.data and result.data.get("original_price") else None,
            stock_status=result.data.get("stock_status") if result.data else None,
            image_url=result.data.get("image_url") if result.data else None,
            brand=result.data.get("brand") if result.data else None,
            error=result.error_message,
            error_type=result.error_type.value if result.error_type else None,
        )

    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        logger.error(f"智能抓取失敗: {e}")
        return SmartScrapeResponse(
            success=False,
            url=request.url,
            strategy_used="error",
            duration_ms=duration_ms,
            retries=0,
            error=str(e),
        )


# =============================================
# 批量抓取 API
# =============================================

@router.post("/batch", response_model=BatchScrapeResponse)
async def batch_scrape(
    request: BatchScrapeRequest,
):
    """
    批量抓取 URL

    功能：
    - 按域名分組，避免單域名過載
    - 動態調整並發（基於成功率）
    - 返回所有結果
    """
    import time
    start_time = time.time()

    config = BatchConfig(
        max_concurrent=request.max_concurrent,
        domain_concurrent=request.domain_concurrent,
    )
    optimizer = BatchOptimizer(config=config)

    results: List[BatchScrapeItemResult] = []
    successful = 0
    failed = 0

    async for result in optimizer.process_batch(request.urls):
        if result.success:
            successful += 1
            results.append(BatchScrapeItemResult(
                url=result.url,
                success=True,
                name=result.data.get("name") if result.data else None,
                price=Decimal(str(result.data.get("price"))) if result.data and result.data.get("price") else None,
            ))
        else:
            failed += 1
            results.append(BatchScrapeItemResult(
                url=result.url,
                success=False,
                error=result.error_message,
            ))

    duration_seconds = time.time() - start_time

    return BatchScrapeResponse(
        total=len(request.urls),
        successful=successful,
        failed=failed,
        results=results,
        duration_seconds=round(duration_seconds, 2),
    )


@router.post("/batch/stream")
async def batch_scrape_stream(
    request: BatchScrapeRequest,
):
    """
    批量抓取（SSE 流式返回進度）

    使用 Server-Sent Events 即時返回抓取進度和結果
    """
    async def generate():
        config = BatchConfig(
            max_concurrent=request.max_concurrent,
            domain_concurrent=request.domain_concurrent,
        )
        optimizer = BatchOptimizer(config=config)

        def on_progress(progress: BatchProgress):
            # 發送進度更新
            data = json.dumps({
                "type": "progress",
                "data": progress.to_dict()
            })
            return f"data: {data}\n\n"

        progress_updates = []

        async for result in optimizer.process_batch(
            request.urls,
            on_progress=lambda p: progress_updates.append(p)
        ):
            # 發送單個結果
            result_data = {
                "type": "result",
                "data": {
                    "url": result.url,
                    "success": result.success,
                    "name": result.data.get("name") if result.data else None,
                    "price": str(result.data.get("price")) if result.data and result.data.get("price") else None,
                    "error": result.error_message,
                }
            }
            yield f"data: {json.dumps(result_data)}\n\n"

            # 發送最新進度
            if progress_updates:
                progress = progress_updates[-1]
                progress_data = {
                    "type": "progress",
                    "data": progress.to_dict()
                }
                yield f"data: {json.dumps(progress_data)}\n\n"
                progress_updates.clear()

        # 發送完成信號
        yield f"data: {json.dumps({'type': 'complete'})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


# =============================================
# URL 驗證 API
# =============================================

@router.post("/validate-url", response_model=ValidateUrlResponse)
async def validate_url(
    request: ValidateUrlRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    驗證 URL 是否可抓取

    檢查：
    1. URL 格式是否有效
    2. 識別對應平台
    3. 是否有該平台的配置
    """
    from urllib.parse import urlparse

    url = request.url.strip()

    # 基本格式驗證
    if not url:
        return ValidateUrlResponse(
            valid=False,
            url=url,
            error="URL 為空"
        )

    if not url.startswith(("http://", "https://")):
        return ValidateUrlResponse(
            valid=False,
            url=url,
            error="URL 必須以 http:// 或 https:// 開頭"
        )

    try:
        parsed = urlparse(url)
        if not parsed.netloc:
            return ValidateUrlResponse(
                valid=False,
                url=url,
                error="無效的 URL 格式"
            )
    except Exception:
        return ValidateUrlResponse(
            valid=False,
            url=url,
            error="無法解析 URL"
        )

    # 識別平台
    domain = parsed.netloc.lower()
    platform = None

    # 平台域名映射
    platform_domains = {
        "hktvmall": ["hktvmall.com", "www.hktvmall.com"],
        "watsons": ["watsons.com.hk", "www.watsons.com.hk"],
        "mannings": ["mannings.com.hk", "www.mannings.com.hk"],
        "parknshop": ["parknshop.com", "www.parknshop.com"],
        "wellcome": ["wellcome.com.hk", "www.wellcome.com.hk"],
        "jdcom": ["jd.hk", "www.jd.hk"],
        "taobao": ["taobao.com", "world.taobao.com"],
        "tmall": ["tmall.com", "tmall.hk"],
        "amazon": ["amazon.com", "www.amazon.com", "amazon.co.jp"],
    }

    for plat, domains in platform_domains.items():
        for d in domains:
            if domain == d or domain.endswith("." + d):
                platform = plat
                break
        if platform:
            break

    # 檢查是否有配置
    has_config = False
    if platform:
        result = await db.execute(
            select(ScrapeConfig).where(
                ScrapeConfig.platform == platform,
                ScrapeConfig.is_active == True
            )
        )
        has_config = result.scalar_one_or_none() is not None

    return ValidateUrlResponse(
        valid=True,
        url=url,
        platform=platform,
        has_config=has_config,
    )
