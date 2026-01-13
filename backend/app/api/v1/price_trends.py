# =============================================
# 價格趨勢 API
# =============================================

from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Optional, List, Dict
from uuid import UUID
import statistics

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.database import get_db
from app.models.product import Product, ProductCompetitorMapping, OwnPriceSnapshot
from app.models.competitor import CompetitorProduct, PriceSnapshot, Competitor
from app.schemas.price_trends import (
    ProductListItem,
    ProductListResponse,
    PriceTrendResponse,
    PriceDataPoint,
    CompetitorInfo,
    OwnProductInfo,
    TrendSummary,
    TimeInterval,
)

router = APIRouter()


def determine_interval(start_date: date, end_date: date) -> TimeInterval:
    """根據時間範圍自動決定聚合粒度"""
    days = (end_date - start_date).days
    if days <= 7:
        return TimeInterval.HOUR
    elif days <= 30:
        return TimeInterval.DAY
    else:
        return TimeInterval.WEEK


def calculate_summary(
    own_prices: List[PriceDataPoint],
    competitor_prices: Dict[str, List[PriceDataPoint]]
) -> TrendSummary:
    """計算趨勢摘要統計"""

    # 獲取有效價格
    own_valid_prices = [p.price for p in own_prices if p.price is not None]

    # 所有競爭對手的有效價格
    all_competitor_prices = []
    for prices in competitor_prices.values():
        all_competitor_prices.extend([p.price for p in prices if p.price is not None])

    # 當前價差（使用最新價格）
    price_gap_current = None
    if own_valid_prices and all_competitor_prices:
        own_latest = float(own_valid_prices[-1])
        competitor_avg_latest = float(sum(all_competitor_prices[-len(competitor_prices):]) / len(competitor_prices)) if competitor_prices else 0
        if competitor_avg_latest > 0:
            price_gap_current = round((own_latest - competitor_avg_latest) / competitor_avg_latest * 100, 1)

    # 平均價差
    price_gap_avg = None
    if own_valid_prices and all_competitor_prices:
        own_avg = sum(float(p) for p in own_valid_prices) / len(own_valid_prices)
        comp_avg = sum(float(p) for p in all_competitor_prices) / len(all_competitor_prices)
        if comp_avg > 0:
            price_gap_avg = round((own_avg - comp_avg) / comp_avg * 100, 1)

    # 競爭對手最低價
    lowest_competitor_price = None
    if all_competitor_prices:
        lowest_competitor_price = min(all_competitor_prices)

    # 價格波動率（自家產品）
    volatility = None
    if len(own_valid_prices) > 1:
        mean_price = sum(float(p) for p in own_valid_prices) / len(own_valid_prices)
        if mean_price > 0:
            std_dev = statistics.stdev(float(p) for p in own_valid_prices)
            volatility = round(std_dev / mean_price * 100, 1)

    # 自家價格變化
    own_price_change = None
    if len(own_valid_prices) >= 2:
        first_price = float(own_valid_prices[0])
        last_price = float(own_valid_prices[-1])
        if first_price > 0:
            own_price_change = round((last_price - first_price) / first_price * 100, 1)

    # 競爭對手平均價格變化
    competitor_avg_change = None
    if competitor_prices:
        changes = []
        for prices in competitor_prices.values():
            valid = [p.price for p in prices if p.price is not None]
            if len(valid) >= 2:
                first = float(valid[0])
                last = float(valid[-1])
                if first > 0:
                    changes.append((last - first) / first * 100)
        if changes:
            competitor_avg_change = round(sum(changes) / len(changes), 1)

    return TrendSummary(
        price_gap_current=price_gap_current,
        price_gap_avg=price_gap_avg,
        lowest_competitor_price=lowest_competitor_price,
        volatility=volatility,
        own_price_change=own_price_change,
        competitor_avg_change=competitor_avg_change,
    )


@router.get("/products", response_model=ProductListResponse)
async def list_products_with_trends(
    db: AsyncSession = Depends(get_db),
    search: Optional[str] = None,
):
    """
    獲取有價格歷史的產品列表（供下拉選單）

    返回有關聯競爭對手的自家產品列表
    """
    # 查詢有競爭對手映射的產品
    query = (
        select(
            Product,
            func.count(ProductCompetitorMapping.id).label("competitor_count")
        )
        .outerjoin(ProductCompetitorMapping, Product.id == ProductCompetitorMapping.product_id)
        .group_by(Product.id)
        .having(func.count(ProductCompetitorMapping.id) > 0)
        .order_by(Product.name)
    )

    if search:
        query = query.where(
            Product.name.ilike(f"%{search}%") | Product.sku.ilike(f"%{search}%")
        )

    result = await db.execute(query)
    rows = result.all()

    products = []
    for row in rows:
        product = row[0]
        competitor_count = row[1]
        products.append(ProductListItem(
            id=product.id,
            sku=product.sku,
            name=product.name,
            current_price=product.price,
            competitor_count=competitor_count,
        ))

    return ProductListResponse(
        products=products,
        total=len(products),
    )


@router.get("/product/{product_id}", response_model=PriceTrendResponse)
async def get_product_price_trend(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
    start_date: Optional[date] = Query(None, description="開始日期，默認 30 天前"),
    end_date: Optional[date] = Query(None, description="結束日期，默認今天"),
    interval: Optional[TimeInterval] = Query(None, description="聚合粒度，默認自動"),
):
    """
    獲取單個產品的價格趨勢

    包含：
    - 自家產品價格歷史
    - 關聯競爭對手價格歷史
    - 趨勢摘要統計（價差、波動率等）
    """
    # 設置默認日期範圍
    if end_date is None:
        end_date = date.today()
    if start_date is None:
        start_date = end_date - timedelta(days=30)

    # 自動決定聚合粒度
    if interval is None:
        interval = determine_interval(start_date, end_date)

    # 轉換為 datetime
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())

    # 1. 獲取自家產品信息
    product_result = await db.execute(
        select(Product).where(Product.id == product_id)
    )
    product = product_result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="產品不存在")

    own_product = OwnProductInfo(
        id=product.id,
        sku=product.sku,
        name=product.name,
        category=product.category,
        current_price=product.price,
    )

    # 2. 獲取自家產品價格歷史
    own_snapshots_result = await db.execute(
        select(OwnPriceSnapshot)
        .where(
            and_(
                OwnPriceSnapshot.product_id == product_id,
                OwnPriceSnapshot.recorded_at >= start_datetime,
                OwnPriceSnapshot.recorded_at <= end_datetime,
            )
        )
        .order_by(OwnPriceSnapshot.recorded_at)
    )
    own_snapshots = own_snapshots_result.scalars().all()

    own_prices = [
        PriceDataPoint(
            date=s.recorded_at,
            price=s.price,
            original_price=s.original_price,
            discount_percent=s.discount_percent,
            stock_status=s.stock_status,
            promotion_text=s.promotion_text,
        )
        for s in own_snapshots
    ]

    # 3. 獲取競爭對手映射
    mappings_result = await db.execute(
        select(ProductCompetitorMapping)
        .options(
            selectinload(ProductCompetitorMapping.competitor_product)
            .selectinload(CompetitorProduct.competitor)
        )
        .where(ProductCompetitorMapping.product_id == product_id)
    )
    mappings = mappings_result.scalars().all()

    # 4. 獲取競爭對手信息和價格歷史
    competitors_info = []
    competitor_prices: Dict[str, List[PriceDataPoint]] = {}

    for mapping in mappings:
        if not mapping.competitor_product:
            continue

        comp_product = mapping.competitor_product
        competitor = comp_product.competitor

        # 競爭對手信息
        comp_info = CompetitorInfo(
            id=comp_product.id,
            name=competitor.name if competitor else "Unknown",
            platform=competitor.platform if competitor else "unknown",
            product_name=comp_product.name,
            current_price=None,  # 稍後從快照獲取
        )

        # 獲取價格快照
        snapshots_result = await db.execute(
            select(PriceSnapshot)
            .where(
                and_(
                    PriceSnapshot.competitor_product_id == comp_product.id,
                    PriceSnapshot.scraped_at >= start_datetime,
                    PriceSnapshot.scraped_at <= end_datetime,
                )
            )
            .order_by(PriceSnapshot.scraped_at)
        )
        snapshots = snapshots_result.scalars().all()

        if snapshots:
            comp_info.current_price = snapshots[-1].price

        prices = [
            PriceDataPoint(
                date=s.scraped_at,
                price=s.price,
                original_price=s.original_price,
                discount_percent=s.discount_percent,
                stock_status=s.stock_status,
                promotion_text=s.promotion_text,
            )
            for s in snapshots
        ]

        competitors_info.append(comp_info)
        competitor_prices[str(comp_product.id)] = prices

    # 5. 計算摘要統計
    summary = calculate_summary(own_prices, competitor_prices)

    # 6. 組裝趨勢數據
    trends = {"own": own_prices}
    trends.update(competitor_prices)

    return PriceTrendResponse(
        own_product=own_product,
        competitors=competitors_info,
        trends=trends,
        summary=summary,
        start_date=start_date,
        end_date=end_date,
        interval=interval,
    )
