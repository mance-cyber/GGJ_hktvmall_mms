# =============================================
# 競品建庫 API
# =============================================
# 手動觸發建庫、打標、匹配，以及競品庫統計
# /pipeline/stream — SSE 串流版完整流程

import asyncio
import json
import logging
import time

from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import get_db, async_session_maker
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
# SSE 串流版完整建庫流程
# =============================================
# 解決反向代理超時問題：每步操作以 asyncio.Task 執行，
# 主 generator 每 10 秒送 heartbeat 保活連線。

PIPELINE_STEPS = [
    ("build", "建庫"),
    ("tag", "打標"),
    ("match", "匹配"),
]


def _sse(event: str, data: dict) -> str:
    """格式化 SSE 事件"""
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


@router.post("/pipeline/stream")
async def pipeline_stream(
    platform: str = Query("all", description="平台：all / hktvmall / wellcome"),
):
    """
    SSE 串流版建庫流程：建庫 → 打標 → 匹配

    事件類型：
    - step_start: 步驟開始 {step, step_number, total_steps}
    - heartbeat:  保活心跳 {step, elapsed}
    - step_done:  步驟完成 {step, result}
    - step_error: 步驟失敗 {step, error}
    - done:       流程結束 {build, tag, match}
    """
    if platform not in ("all", "hktvmall", "wellcome"):
        raise HTTPException(status_code=400, detail=f"不支援的平台: {platform}")

    async def event_stream():
        from app.services.cataloger import CatalogService
        from app.services.tagger import tag_all_untagged
        from app.services.matcher import match_all_pending

        results = {}

        for step_idx, (step_key, step_name) in enumerate(PIPELINE_STEPS):
            yield _sse("step_start", {
                "step": step_key,
                "step_number": step_idx + 1,
                "total_steps": len(PIPELINE_STEPS),
            })

            step_result = None
            step_error = None

            # 用閉包捕獲當前迭代的 step_key，避免 late-binding 問題
            async def run_step(_key=step_key):
                nonlocal step_result, step_error
                try:
                    async with async_session_maker() as session:
                        if _key == "build":
                            step_result = await CatalogService.build_catalog(
                                session, platform=platform,
                            )
                        elif _key == "tag":
                            step_result = await tag_all_untagged(session)
                            await session.commit()
                        elif _key == "match":
                            step_result = await match_all_pending(session)
                            await session.commit()
                except Exception as e:
                    logger.error(
                        f"pipeline_stream {_key} 失敗: {e}",
                        exc_info=True,
                    )
                    step_error = str(e)

            task = asyncio.create_task(run_step())
            start = time.time()

            # 用 asyncio.sleep 取代 wait_for(shield(task))
            # 避免 shield + wait_for 的已知交互問題（task 異常洩漏）
            while not task.done():
                yield _sse("heartbeat", {
                    "step": step_key,
                    "elapsed": round(time.time() - start, 1),
                })
                await asyncio.sleep(5)

            # 收集 task 本身的未預期異常（理論上已被 run_step 捕獲）
            if not step_error and task.done() and not task.cancelled():
                exc = task.exception()
                if exc:
                    step_error = str(exc)

            elapsed_total = round(time.time() - start, 1)

            if step_error:
                yield _sse("step_error", {
                    "step": step_key,
                    "error": step_error,
                    "elapsed": elapsed_total,
                })
                return

            results[step_key] = step_result
            yield _sse("step_done", {
                "step": step_key,
                "result": step_result,
                "elapsed": elapsed_total,
            })

        yield _sse("done", results)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


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
