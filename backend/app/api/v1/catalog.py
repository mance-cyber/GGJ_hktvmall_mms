# =============================================
# 競品建庫 API
# =============================================
# 手動觸發建庫、打標、匹配，以及競品庫統計
# /pipeline/start  + /pipeline/progress — 後台任務 + 輪詢模式
# /pipeline/stream — SSE 串流版（保留向後相容）

import asyncio
import json
import logging
import time
import uuid as _uuid
from dataclasses import dataclass, field
from typing import Any

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
# 管線步驟定義
# =============================================

PIPELINE_STEPS = [
    ("build", "建庫"),
    ("tag", "打標"),
    ("match", "匹配"),
]

STEP_NUMBERS = {k: i + 1 for i, (k, _) in enumerate(PIPELINE_STEPS)}
VALID_STEP_KEYS = set(STEP_NUMBERS.keys())


# =============================================
# 後台任務 + 輪詢模式（取代 SSE 長連線）
# =============================================
# 徹底解決反向代理超時：不再依賴長連線，
# 改用短請求輪詢後台任務進度，每次 < 1 秒。

@dataclass
class PipelineTask:
    """管線任務狀態（記憶體內，進程重啟後清空）"""
    id: str
    platform: str
    status: str = "running"          # running | done | error
    current_step: str | None = None
    current_step_number: int = 0
    step_results: dict[str, Any] = field(default_factory=dict)
    step_errors: dict[str, str] = field(default_factory=dict)
    step_durations: dict[str, float] = field(default_factory=dict)
    start_time: float = 0.0
    step_start_time: float = 0.0


# 記憶體中的任務表
_tasks: dict[str, PipelineTask] = {}


def _cleanup_old_tasks():
    """清理 1 小時前的過期任務"""
    cutoff = time.time() - 3600
    for tid in list(_tasks.keys()):
        if _tasks[tid].start_time < cutoff:
            del _tasks[tid]


@router.post("/pipeline/start")
async def pipeline_start(
    platform: str = Query("all", description="平台：all / hktvmall / wellcome"),
):
    """
    啟動管線後台任務，立即返回 task_id

    前端用 GET /pipeline/progress/{task_id} 輪詢進度。
    """
    if platform not in ("all", "hktvmall", "wellcome"):
        raise HTTPException(status_code=400, detail=f"不支援的平台: {platform}")

    _cleanup_old_tasks()

    task_id = _uuid.uuid4().hex[:8]
    task = PipelineTask(id=task_id, platform=platform, start_time=time.time())
    _tasks[task_id] = task

    asyncio.create_task(_run_pipeline_task(task))
    logger.info(f"pipeline task {task_id} 已啟動, platform={platform}")

    return {"task_id": task_id}


@router.get("/pipeline/progress/{task_id}")
async def pipeline_progress(task_id: str):
    """查詢管線任務進度"""
    task = _tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任務不存在或已過期")

    elapsed = (
        round(time.time() - task.step_start_time, 1)
        if task.current_step else 0
    )

    return {
        "task_id": task.id,
        "status": task.status,
        "current_step": task.current_step,
        "current_step_number": task.current_step_number,
        "total_steps": len(PIPELINE_STEPS),
        "elapsed": elapsed,
        "step_results": task.step_results,
        "step_errors": task.step_errors,
        "step_durations": task.step_durations,
    }


async def _run_pipeline_task(task: PipelineTask):
    """後台執行管線全流程（asyncio.Task 內跑）"""
    from app.services.cataloger import CatalogService
    from app.services.tagger import tag_all_untagged
    from app.services.matcher import match_all_pending

    for step_key, _step_name in PIPELINE_STEPS:
        task.current_step = step_key
        task.current_step_number = STEP_NUMBERS[step_key]
        task.step_start_time = time.time()

        try:
            async with async_session_maker() as session:
                if step_key == "build":
                    result = await CatalogService.build_catalog(
                        session, platform=task.platform,
                    )
                elif step_key == "tag":
                    result = await tag_all_untagged(session)
                    await session.commit()
                elif step_key == "match":
                    result = await match_all_pending(session)
                    await session.commit()

            task.step_results[step_key] = result
            task.step_durations[step_key] = round(
                time.time() - task.step_start_time, 1,
            )
        except Exception as e:
            logger.error(f"pipeline task {task.id} {step_key} 失敗: {e}", exc_info=True)
            task.step_errors[step_key] = str(e)
            task.step_durations[step_key] = round(
                time.time() - task.step_start_time, 1,
            )
            task.status = "error"
            task.current_step = None
            return

    task.status = "done"
    task.current_step = None
    logger.info(f"pipeline task {task.id} 全部完成")


# =============================================
# SSE 串流版（保留向後相容，不再推薦使用）
# =============================================


def _sse(event: str, data: dict) -> str:
    """格式化 SSE 事件"""
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


@router.post("/pipeline/stream")
async def pipeline_stream(
    platform: str = Query("all", description="平台：all / hktvmall / wellcome"),
    step: str = Query(None, description="單步模式：build / tag / match（省略則依序全部執行）"),
):
    """
    SSE 串流版建庫流程：建庫 → 打標 → 匹配

    支援兩種模式：
    - 全量模式（step 省略）：依序執行全部步驟，共用一條 SSE 連線
    - 單步模式（step=build/tag/match）：只執行指定步驟
      前端可分三次呼叫，避免長連線超過反向代理的總連線時長上限

    事件類型：
    - step_start: 步驟開始 {step, step_number, total_steps}
    - heartbeat:  保活心跳 {step, elapsed}
    - step_done:  步驟完成 {step, result}
    - step_error: 步驟失敗 {step, error}
    - done:       流程結束 {build, tag, match}
    """
    if platform not in ("all", "hktvmall", "wellcome"):
        raise HTTPException(status_code=400, detail=f"不支援的平台: {platform}")
    if step and step not in VALID_STEP_KEYS:
        raise HTTPException(status_code=400, detail=f"不支援的步驟: {step}")

    # 單步模式只跑一個步驟；全量模式跑全部
    active_steps = (
        [(k, v) for k, v in PIPELINE_STEPS if k == step]
        if step
        else list(PIPELINE_STEPS)
    )

    async def event_stream():
        from app.services.cataloger import CatalogService
        from app.services.tagger import tag_all_untagged
        from app.services.matcher import match_all_pending

        results = {}

        for step_key, step_name in active_steps:
            yield _sse("step_start", {
                "step": step_key,
                "step_number": STEP_NUMBERS[step_key],
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
