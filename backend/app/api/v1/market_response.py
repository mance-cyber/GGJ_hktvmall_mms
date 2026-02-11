# =============================================
# Market Response Center (MRC) API
# 市場應對中心 - 核心 API 端點
# =============================================

import logging
from typing import List, Optional
from datetime import datetime, date
from uuid import UUID
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, case, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.models.database import get_db
from app.models.product import Product, ProductCompetitorMapping
from app.models.competitor import CompetitorProduct, PriceSnapshot, PriceAlert

router = APIRouter()
logger = logging.getLogger(__name__)


# =============================================
# Pydantic Schemas
# =============================================

class SeasonalProduct(BaseModel):
    """季節性商品"""
    id: UUID
    sku: str
    name_zh: Optional[str]
    name_ja: Optional[str]
    name_en: Optional[str]
    category_main: Optional[str]
    category_sub: Optional[str]
    season_tag: Optional[str]
    unit: Optional[str]
    competitor_count: int = 0
    has_price_alert: bool = False

    class Config:
        from_attributes = True


class PriceGapItem(BaseModel):
    """價格差距分析項目"""
    product_id: UUID
    product_name: str
    our_price: Optional[Decimal]
    competitor_name: str
    competitor_price: Optional[Decimal]
    price_gap: Optional[Decimal]
    price_gap_percent: Optional[float]
    recommendation: str


class OpportunityItem(BaseModel):
    """機會雷達項目"""
    product_id: UUID
    product_name: str
    opportunity_type: str  # "competitor_out_of_stock", "price_advantage", "seasonal_exclusive"
    description: str
    action_suggestion: str
    priority: str  # "high", "medium", "low"


class MRCDashboardStats(BaseModel):
    """MRC 儀表板統計"""
    total_products: int
    products_with_competitors: int
    seasonal_products_this_month: int
    price_alerts_unread: int
    opportunities_count: int
    categories_breakdown: dict


class MRCDashboardResponse(BaseModel):
    """MRC 儀表板完整響應"""
    stats: MRCDashboardStats
    seasonal_products: List[SeasonalProduct]
    price_alerts: List[dict]
    opportunities: List[OpportunityItem]


# =============================================
# Helper Functions
# =============================================

def get_current_season() -> List[str]:
    """獲取當前季節標籤"""
    month = datetime.now().month
    
    # 月份到季節的映射
    if month in [12, 1, 2]:
        return ["WINTER", "ALL", "WINTER-SPRING", "AUTUMN-WINTER", "NOV-MAY", "DEC-JUN"]
    elif month in [3, 4, 5]:
        return ["SPRING", "ALL", "SPRING-SUMMER", "WINTER-SPRING", "MARCH-MAY", "FEB-JUNE", "MARCH-APRIL"]
    elif month in [6, 7, 8]:
        return ["SUMMER", "ALL", "SPRING-SUMMER", "SUMMER-AUTUMN", "MAY-AUGUST", "APRIL-SEP"]
    else:  # 9, 10, 11
        return ["AUTUMN", "ALL", "SUMMER-AUTUMN", "AUTUMN-WINTER", "AUG-DEC", "JULY-OCT"]


# =============================================
# API Endpoints
# =============================================

@router.get("/dashboard", response_model=MRCDashboardResponse)
async def get_mrc_dashboard(
    db: AsyncSession = Depends(get_db)
):
    """
    獲取 Market Response Center 儀表板數據
    
    包含：
    - 統計概覽
    - 當季商品列表
    - 價格警報
    - 機會雷達
    """
    # 1. 基礎統計
    total_products = await db.scalar(
        select(func.count(Product.id)).where(Product.source == 'gogojap_csv')
    ) or 0
    
    products_with_competitors = await db.scalar(
        select(func.count(func.distinct(ProductCompetitorMapping.product_id)))
    ) or 0
    
    # 2. 當季商品
    current_seasons = get_current_season()
    seasonal_query = select(Product).where(
        and_(
            Product.source == 'gogojap_csv',
            Product.season_tag.in_(current_seasons)
        )
    ).limit(20)
    
    seasonal_result = await db.execute(seasonal_query)
    seasonal_products_raw = seasonal_result.scalars().all()
    
    seasonal_products = [
        SeasonalProduct(
            id=p.id,
            sku=p.sku,
            name_zh=p.name_zh,
            name_ja=p.name_ja,
            name_en=p.name_en,
            category_main=p.category_main,
            category_sub=p.category_sub,
            season_tag=p.season_tag,
            unit=p.unit,
            competitor_count=0,
            has_price_alert=False
        )
        for p in seasonal_products_raw
    ]
    
    # 3. 未讀警報數量
    price_alerts_unread = await db.scalar(
        select(func.count(PriceAlert.id)).where(PriceAlert.is_read == False)
    ) or 0
    
    # 4. 分類統計
    category_query = select(
        Product.category_main,
        func.count(Product.id).label('count')
    ).where(
        Product.source == 'gogojap_csv'
    ).group_by(Product.category_main)
    
    category_result = await db.execute(category_query)
    categories_breakdown = {
        row.category_main or "未分類": row.count 
        for row in category_result
    }
    
    # 5. 機會雷達：競品缺貨機會
    opportunities = await _get_stockout_opportunities(db, limit=10)

    # 6. 最近價格告警（未讀）
    price_alerts_query = (
        select(PriceAlert)
        .join(CompetitorProduct)
        .where(PriceAlert.is_read == False)
        .order_by(PriceAlert.created_at.desc())
        .limit(10)
    )
    price_alerts_result = await db.execute(price_alerts_query)
    price_alerts_data = [
        {
            "id": alert.id,
            "competitor_product_id": alert.competitor_product_id,
            "alert_type": alert.alert_type,
            "old_value": alert.old_value,
            "new_value": alert.new_value,
            "change_percent": float(alert.change_percent) if alert.change_percent else None,
            "created_at": alert.created_at.isoformat() if alert.created_at else None,
        }
        for alert in price_alerts_result.scalars().all()
    ]

    # 7. 組裝響應
    stats = MRCDashboardStats(
        total_products=total_products,
        products_with_competitors=products_with_competitors,
        seasonal_products_this_month=len(seasonal_products),
        price_alerts_unread=price_alerts_unread,
        opportunities_count=len(opportunities),
        categories_breakdown=categories_breakdown
    )

    return MRCDashboardResponse(
        stats=stats,
        seasonal_products=seasonal_products,
        price_alerts=price_alerts_data,
        opportunities=opportunities
    )


@router.get("/products/seasonal", response_model=List[SeasonalProduct])
async def get_seasonal_products(
    season: Optional[str] = Query(None, description="指定季節: WINTER, SPRING, SUMMER, AUTUMN"),
    category_main: Optional[str] = Query(None, description="篩選大分類"),
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db)
):
    """獲取季節性商品列表"""
    if season:
        seasons = [season.upper()]
    else:
        seasons = get_current_season()
    
    query = select(Product).where(
        and_(
            Product.source == 'gogojap_csv',
            Product.season_tag.in_(seasons)
        )
    )
    
    if category_main:
        query = query.where(Product.category_main == category_main)
    
    query = query.limit(limit)
    
    result = await db.execute(query)
    products = result.scalars().all()
    
    return [
        SeasonalProduct(
            id=p.id,
            sku=p.sku,
            name_zh=p.name_zh,
            name_ja=p.name_ja,
            name_en=p.name_en,
            category_main=p.category_main,
            category_sub=p.category_sub,
            season_tag=p.season_tag,
            unit=p.unit,
            competitor_count=0,
            has_price_alert=False
        )
        for p in products
    ]


@router.get("/products/search")
async def search_products(
    q: str = Query(..., min_length=1, description="搜尋關鍵字 (支援中/日/英)"),
    category_main: Optional[str] = None,
    limit: int = Query(20, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    多語言商品搜尋
    
    搜尋範圍：中文名、日文名、英文名
    """
    search_pattern = f"%{q}%"
    
    query = select(Product).where(
        and_(
            Product.source == 'gogojap_csv',
            or_(
                Product.name_zh.ilike(search_pattern),
                Product.name_ja.ilike(search_pattern),
                Product.name_en.ilike(search_pattern)
            )
        )
    )
    
    if category_main:
        query = query.where(Product.category_main == category_main)
    
    query = query.limit(limit)
    
    result = await db.execute(query)
    products = result.scalars().all()
    
    return [
        {
            "id": str(p.id),
            "sku": p.sku,
            "name_zh": p.name_zh,
            "name_ja": p.name_ja,
            "name_en": p.name_en,
            "category": p.category,
            "season_tag": p.season_tag,
            "unit": p.unit
        }
        for p in products
    ]


@router.get("/categories")
async def get_categories(
    db: AsyncSession = Depends(get_db)
):
    """獲取所有分類及其商品數量"""
    query = select(
        Product.category_main,
        func.count(Product.id).label('count')
    ).group_by(Product.category_main).order_by(func.count(Product.id).desc())
    
    result = await db.execute(query)
    rows = result.all()
    
    return [
        {"name": row.category_main or "未分類", "count": row.count}
        for row in rows
    ]


# =============================================
# Competitor Search Endpoints
# =============================================

@router.post("/products/{product_id}/find-competitors")
async def find_competitors_for_product(
    product_id: UUID,
    platform: str = Query("hktvmall", description="搜索平台"),
    max_candidates: int = Query(5, le=10),
    db: AsyncSession = Depends(get_db)
):
    """
    為指定商品自動搜索並匹配競品
    
    流程：
    1. 使用商品的 日文名/英文名 搜索競品網站
    2. 使用 AI 判斷是否為同級商品
    3. 自動建立關聯
    """
    from app.services.competitor_matcher import get_competitor_matcher_service
    
    # 獲取商品
    product = await db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # 搜索並匹配
    service = get_competitor_matcher_service()
    results = await service.find_competitors_for_product(
        db=db,
        product=product,
        platform=platform,
        max_candidates=max_candidates
    )
    
    # 保存匹配結果
    saved_count = 0
    for result in results:
        if result.is_match and result.match_confidence >= 0.6:
            mapping = await service.save_match_to_db(
                db=db,
                product_id=str(product_id),
                match_result=result
            )
            if mapping:
                saved_count += 1
    
    return {
        "product_id": str(product_id),
        "product_name": product.name_zh,
        "search_queries": service.generate_search_queries(product),
        "candidates_found": len(results),
        "matches_saved": saved_count,
        "results": [
            {
                "candidate_name": r.candidate_name,
                "candidate_url": r.candidate_url,
                "confidence": r.match_confidence,
                "is_match": r.is_match,
                "reason": r.match_reason
            }
            for r in results
        ]
    }


@router.post("/batch/find-competitors")
async def batch_find_competitors(
    category_main: Optional[str] = Query(None, description="篩選大分類"),
    category_sub: Optional[str] = Query(None, description="篩選小分類"),
    limit: int = Query(10, le=50, description="處理商品數量"),
    db: AsyncSession = Depends(get_db)
):
    """
    批量為商品搜索競品

    注意：此操作會消耗 API 配額，請謹慎使用
    """
    try:
        from app.services.competitor_matcher import CompetitorMatcherService

        # 查詢尚未有競品關聯的商品（所有來源）
        subquery = select(ProductCompetitorMapping.product_id)

        query = select(Product).where(
            ~Product.id.in_(subquery)
        )

        if category_main:
            query = query.where(Product.category_main == category_main)
        if category_sub:
            query = query.where(Product.category_sub == category_sub)

        query = query.limit(limit)

        result = await db.execute(query)
        products = result.scalars().all()

        if not products:
            return {
                "processed": 0,
                "results": [],
                "message": "沒有待處理的商品（所有商品都已有競品映射）"
            }

        # 直接實例化服務
        service = CompetitorMatcherService()

        batch_results = []
        for product in products:
            try:
                results = await service.find_competitors_for_product(
                    db=db,
                    product=product,
                    max_candidates=3
                )

                matches = [r for r in results if r.is_match and r.match_confidence >= 0.6]

                for match in matches[:1]:  # 每個商品最多保存一個最佳匹配
                    await service.save_match_to_db(
                        db=db,
                        product_id=str(product.id),
                        match_result=match
                    )

                batch_results.append({
                    "product_id": str(product.id),
                    "product_name": product.name_zh,
                    "candidates": len(results),
                    "matches": len(matches)
                })

            except Exception as e:
                logger.error(f"處理商品失敗: {product.name_zh} - {str(e)}", exc_info=True)
                batch_results.append({
                    "product_id": str(product.id),
                    "product_name": product.name_zh,
                    "error": str(e)
                })

        await db.commit()

        return {
            "processed": len(batch_results),
            "results": batch_results
        }

    except Exception as e:
        logger.error(f"批量競品匹配失敗: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"批量匹配失敗: {str(e)}"
        )


@router.get("/debug/test-by-sku/{sku}")
async def debug_test_by_sku(
    sku: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Debug 端點：用 SKU 測試單個商品的完整搜索流程

    返回詳細的中間步驟信息，用於診斷為何搜索失敗
    """
    try:
        from app.services.competitor_matcher import CompetitorMatcherService
        import urllib.parse

        # 用 SKU 查詢商品
        result = await db.execute(select(Product).where(Product.sku == sku))
        product = result.scalar_one_or_none()

        if not product:
            raise HTTPException(status_code=404, detail=f"找不到 SKU: {sku} 的商品")

        return await _debug_test_product(product, db)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Debug test failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"測試失敗: {str(e)}"
        )


@router.get("/debug/test-single-product/{product_id}")
async def debug_test_single_product(
    product_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Debug 端點：測試單個商品的完整搜索流程

    返回詳細的中間步驟信息，用於診斷為何搜索失敗
    """
    try:
        from app.services.competitor_matcher import CompetitorMatcherService
        import urllib.parse

        # 查詢商品
        result = await db.execute(select(Product).where(Product.id == product_id))
        product = result.scalar_one_or_none()

        if not product:
            raise HTTPException(status_code=404, detail="商品不存在")

        return await _debug_test_product(product, db)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Debug test failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"測試失敗: {str(e)}"
        )


async def _debug_test_product(product: Product, db: AsyncSession):
    """共用的 debug 測試邏輯"""
    from app.services.competitor_matcher import CompetitorMatcherService
    import urllib.parse

    service = CompetitorMatcherService()

    # Step 1: 生成搜索關鍵詞
    search_queries = service.generate_search_queries(product)

    # Step 2: 構造搜索 URL
    search_urls = []
    for query in search_queries[:2]:  # 只測試前兩個
        encoded_query = urllib.parse.quote(query)
        search_url = f"https://www.hktvmall.com/hktv/zh/search?q={encoded_query}"
        search_urls.append({
            "query": query,
            "url": search_url
        })

    # Step 3: 測試 Firecrawl 搜索（只測試第一個關鍵詞）
    firecrawl_result = None
    firecrawl_error = None
    extracted_urls = []

    if search_queries:
        try:
            first_query = search_queries[0]
            logger.info(f"Testing Firecrawl search with query: {first_query}")

            # 使用 HKTVMallSearchStrategy 的搜索方法
            search_url = service.hktv_strategy.build_search_url(first_query)
            urls = service.hktv_strategy.extract_product_urls_from_search(search_url, limit=5)

            extracted_urls = urls
            firecrawl_result = {
                "search_url": search_url,
                "urls_found": len(urls),
                "urls": urls[:5]  # 最多返回 5 個
            }
        except Exception as e:
            firecrawl_error = str(e)
            logger.error(f"Firecrawl test failed: {e}", exc_info=True)

    return {
        "product": {
            "id": str(product.id),
            "sku": product.sku,
            "name_zh": product.name_zh,
            "name_ja": getattr(product, 'name_ja', None),
            "name_en": getattr(product, 'name_en', None),
            "category_main": getattr(product, 'category_main', None),
            "category_sub": getattr(product, 'category_sub', None),
        },
        "step1_search_queries": search_queries,
        "step2_search_urls": search_urls,
        "step3_firecrawl_test": {
            "success": firecrawl_result is not None,
            "result": firecrawl_result,
            "error": firecrawl_error
        }
    }


# =============================================
# Helper Functions
# =============================================

async def _get_stockout_opportunities(db: AsyncSession, limit: int = 10) -> List[dict]:
    """
    查詢競品缺貨機會

    邏輯：
    1. 找出所有有競品映射的商品
    2. 檢查每個商品的競品是否「都」缺貨
    3. 返回機會清單（我們是唯一有貨的賣家）
    """
    from sqlalchemy import select, func
    from app.models.product import Product, ProductCompetitorMapping
    from app.models.competitor import PriceSnapshot

    opportunities = []

    # 獲取所有有競品映射的商品
    stmt = (
        select(Product.id, Product.sku, Product.name_zh, Product.price)
        .join(ProductCompetitorMapping)
        .distinct()
        .limit(limit * 3)  # 查詢更多候選，因為不是所有商品都符合條件
    )
    result = await db.execute(stmt)
    products = result.all()

    for product_row in products:
        product_id = product_row.id
        sku = product_row.sku
        name_zh = product_row.name_zh
        price = product_row.price

        # 檢查此商品的所有競品是否都缺貨
        all_stockout = await _check_all_competitors_stockout(db, product_id)

        if all_stockout:
            # 計算有多少個競品
            competitor_count_stmt = (
                select(func.count(ProductCompetitorMapping.id))
                .where(ProductCompetitorMapping.product_id == product_id)
            )
            competitor_count = await db.scalar(competitor_count_stmt) or 0

            opportunities.append({
                "product_id": str(product_id),
                "sku": sku,
                "name": name_zh or sku,
                "current_price": float(price) if price else None,
                "opportunity_type": "all_competitors_stockout",
                "competitor_count": competitor_count,
                "description": f"{competitor_count} 個競品都缺貨，搶市機會！",
            })

            if len(opportunities) >= limit:
                break

    return opportunities


async def _check_all_competitors_stockout(db: AsyncSession, product_id: UUID) -> bool:
    """檢查商品的所有競品是否都缺貨"""
    from sqlalchemy import select
    from app.models.product import ProductCompetitorMapping
    from app.models.competitor import PriceSnapshot

    # 找到所有競品映射
    stmt = (
        select(ProductCompetitorMapping.competitor_product_id)
        .where(ProductCompetitorMapping.product_id == product_id)
    )
    result = await db.execute(stmt)
    competitor_product_ids = result.scalars().all()

    if not competitor_product_ids:
        return False  # 沒有競品映射

    # 檢查每個競品的最新庫存狀態
    for cp_id in competitor_product_ids:
        # 最新的價格快照
        stmt = (
            select(PriceSnapshot.stock_status)
            .where(PriceSnapshot.competitor_product_id == cp_id)
            .order_by(PriceSnapshot.scraped_at.desc())
            .limit(1)
        )
        result = await db.execute(stmt)
        latest_stock = result.scalar_one_or_none()

        # 如果有任何一個競品有貨，就不是機會窗口
        if latest_stock and latest_stock != "out_of_stock":
            return False

    # 所有競品都缺貨！
    return True
