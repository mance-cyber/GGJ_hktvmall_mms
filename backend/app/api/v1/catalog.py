# =============================================
# 競品建庫 API
# =============================================
# 手動觸發建庫、打標、匹配，以及競品庫統計

import logging

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import get_db
from app.models.competitor import Competitor, CompetitorProduct
from app.models.product import ProductCompetitorMapping

logger = logging.getLogger(__name__)

router = APIRouter()


# =============================================
# 建庫
# =============================================

@router.post("/build")
async def build_catalog(
    platform: str = Query("all", description="平台：all / hktvmall / wellcome"),
    db: AsyncSession = Depends(get_db),
):
    """手動觸發完整建庫（首次使用或重建）"""
    if platform not in ("all", "hktvmall", "wellcome"):
        raise HTTPException(status_code=400, detail=f"不支援的平台: {platform}")

    from app.services.cataloger import CatalogService
    result = await CatalogService.build_catalog(db, platform=platform)
    return {"status": "ok", "result": result}


@router.post("/update")
async def update_catalog(
    platform: str = Query("all", description="平台：all / hktvmall / wellcome"),
    db: AsyncSession = Depends(get_db),
):
    """每日增量更新（與 build 邏輯相同，upsert 自動處理差異）"""
    if platform not in ("all", "hktvmall", "wellcome"):
        raise HTTPException(status_code=400, detail=f"不支援的平台: {platform}")

    from app.services.cataloger import CatalogService
    result = await CatalogService.update_catalog(db, platform=platform)
    return {"status": "ok", "result": result}


# =============================================
# 打標
# =============================================

@router.post("/tag")
async def tag_products(
    db: AsyncSession = Depends(get_db),
):
    """手動觸發打標（規則引擎 + AI 兜底）"""
    from app.services.tagger import tag_all_untagged
    result = await tag_all_untagged(db)
    await db.commit()
    return {"status": "ok", "result": result}


# =============================================
# 匹配
# =============================================

@router.post("/match")
async def match_products(
    product_id: str = Query(None, description="指定商品 ID（不填則匹配所有 pending）"),
    db: AsyncSession = Depends(get_db),
):
    """手動觸發匹配（預篩 + AI 精判三層匹配）"""
    from app.services.matcher import match_product, match_all_pending
    if product_id:
        result = await match_product(db, product_id)
    else:
        result = await match_all_pending(db)
    await db.commit()
    return {"status": "ok", "result": result}


# =============================================
# 監測
# =============================================

@router.post("/monitor")
async def run_monitor(
    db: AsyncSession = Depends(get_db),
):
    """手動觸發監測檢查（下架判定 + 價格異動）"""
    from app.services.monitor import MonitorService
    result = await MonitorService.run_daily_check(db)
    await db.commit()
    return {"status": "ok", "result": result}


# =============================================
# 競品庫統計
# =============================================

@router.get("/stats")
async def catalog_stats(
    db: AsyncSession = Depends(get_db),
):
    """競品庫概覽統計"""

    # 各平台商品數
    platform_stmt = (
        select(
            Competitor.platform,
            func.count(CompetitorProduct.id).label("count"),
        )
        .join(CompetitorProduct, CompetitorProduct.competitor_id == Competitor.id)
        .where(CompetitorProduct.is_active == True)
        .group_by(Competitor.platform)
    )
    platform_result = await db.execute(platform_stmt)
    platforms = {row.platform: row.count for row in platform_result}

    # 已打標數
    tagged_stmt = (
        select(func.count())
        .select_from(CompetitorProduct)
        .where(
            CompetitorProduct.is_active == True,
            CompetitorProduct.category_tag.isnot(None),
        )
    )
    tagged_result = await db.execute(tagged_stmt)
    tagged_count = tagged_result.scalar() or 0

    # needs_matching 數
    needs_matching_stmt = (
        select(func.count())
        .select_from(CompetitorProduct)
        .where(
            CompetitorProduct.is_active == True,
            CompetitorProduct.needs_matching == True,
        )
    )
    needs_matching_result = await db.execute(needs_matching_stmt)
    needs_matching_count = needs_matching_result.scalar() or 0

    # 已匹配數（有 mapping 記錄的競品商品）
    matched_stmt = (
        select(func.count(func.distinct(ProductCompetitorMapping.competitor_product_id)))
        .select_from(ProductCompetitorMapping)
    )
    matched_result = await db.execute(matched_stmt)
    matched_count = matched_result.scalar() or 0

    # 活躍商品總數
    total_active = sum(platforms.values())

    return {
        "total_active": total_active,
        "by_platform": platforms,
        "tagged": tagged_count,
        "untagged": total_active - tagged_count,
        "needs_matching": needs_matching_count,
        "matched": matched_count,
    }
