# =============================================
# 競品建庫 API
# =============================================
# 手動觸發建庫、打標、匹配，以及競品庫統計
# /pipeline/start  + /pipeline/progress — 後台任務 + 輪詢模式（DB 持久化）
# /pipeline/stream — SSE 串流版（保留向後相容）

import asyncio
import json
import logging
import time
import uuid as _uuid

from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import get_db, async_session_maker, utcnow
from app.models.competitor import Competitor, CompetitorProduct
from app.models.pipeline_task import PipelineTask as PipelineTaskModel
from app.models.product import Product, ProductCompetitorMapping

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
    """手動觸發匹配（pg_trgm 預篩 + AI 精判三層匹配）"""
    from app.services.matcher import match_product, match_all_pending
    if product_id:
        result = await match_product(db, product_id)
        await db.commit()
    else:
        # match_all_pending 自行管理 session（並行匹配）
        result = await match_all_pending()
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
# 後台任務 + 輪詢模式（DB 持久化）
# =============================================
# 徹底解決反向代理超時 + 伺服器重啟狀態丟失：
# 1. 用短請求輪詢後台任務進度，每次 < 1 秒
# 2. 任務狀態持久化到 DB，進程重啟後可恢復查詢


async def _save_task(task_id: str, **fields) -> None:
    """更新 DB 中的任務狀態（獨立 session，用完即關）"""
    try:
        async with async_session_maker() as session:
            task = await session.get(PipelineTaskModel, task_id)
            if task:
                for k, v in fields.items():
                    setattr(task, k, v)
                task.updated_at = utcnow()
                await session.commit()
    except Exception as e:
        logger.warning(f"_save_task {task_id} 寫入失敗（不影響管線）: {e}")


async def _cleanup_old_tasks() -> None:
    """清理 24 小時前的過期任務"""
    try:
        from datetime import timedelta
        cutoff = utcnow() - timedelta(hours=24)
        async with async_session_maker() as session:
            await session.execute(
                delete(PipelineTaskModel).where(PipelineTaskModel.created_at < cutoff),
            )
            await session.commit()
    except Exception as e:
        logger.warning(f"_cleanup_old_tasks 失敗: {e}")


@router.post("/pipeline/start")
async def pipeline_start(
    platform: str = Query("all", description="平台：all / hktvmall / wellcome"),
):
    """
    啟動管線後台任務，立即返回 task_id

    前端用 GET /pipeline/progress/{task_id} 輪詢進度。
    任務狀態持久化到 DB，伺服器重啟不會丟失。
    """
    if platform not in ("all", "hktvmall", "wellcome"):
        raise HTTPException(status_code=400, detail=f"不支援的平台: {platform}")

    await _cleanup_old_tasks()

    task_id = _uuid.uuid4().hex[:8]

    # 寫入 DB
    async with async_session_maker() as session:
        db_task = PipelineTaskModel(
            id=task_id,
            platform=platform,
            status="running",
            step_results={},
            step_errors={},
            step_durations={},
        )
        session.add(db_task)
        await session.commit()

    asyncio.create_task(_run_pipeline_task(task_id, platform))
    logger.info(f"pipeline task {task_id} 已啟動, platform={platform}")

    return {"task_id": task_id}


@router.get("/pipeline/progress/{task_id}")
async def pipeline_progress(task_id: str):
    """查詢管線任務進度（從 DB 讀取，伺服器重啟後依然有效）"""
    async with async_session_maker() as session:
        task = await session.get(PipelineTaskModel, task_id)

    if not task:
        raise HTTPException(status_code=404, detail="任務不存在或已過期")

    # 計算當前步驟的即時耗時
    elapsed = 0.0
    if task.current_step and task.step_started_at:
        elapsed = round((utcnow() - task.step_started_at).total_seconds(), 1)

    return {
        "task_id": task.id,
        "status": task.status,
        "current_step": task.current_step,
        "current_step_number": task.current_step_number,
        "total_steps": len(PIPELINE_STEPS),
        "elapsed": elapsed,
        "step_results": task.step_results or {},
        "step_errors": task.step_errors or {},
        "step_durations": task.step_durations or {},
        "progress": task.progress,
    }


async def _run_pipeline_task(task_id: str, platform: str) -> None:
    """
    後台執行管線全流程（asyncio.Task 內跑）

    頂層 try/except 防止任何未預期異常導致任務狀態懸停。
    每步驟完成後立即同步到 DB，伺服器重啟後前端可查到最新狀態。
    """
    from app.services.cataloger import CatalogService
    from app.services.tagger import tag_all_untagged

    try:
        step_results: dict = {}
        step_durations: dict = {}

        for step_key, _step_name in PIPELINE_STEPS:
            step_start = time.time()

            # 更新 DB：當前步驟 → running，清除上一步的 progress
            await _save_task(
                task_id,
                current_step=step_key,
                current_step_number=STEP_NUMBERS[step_key],
                step_started_at=utcnow(),
                progress=None,
            )

            try:
                if step_key == "match":
                    result = await _match_with_fresh_sessions(task_id)
                else:
                    async with async_session_maker() as session:
                        if step_key == "build":
                            result = await CatalogService.build_catalog(
                                session, platform=platform,
                            )
                        elif step_key == "tag":
                            result = await tag_all_untagged(session)
                            await session.commit()

                duration = round(time.time() - step_start, 1)
                step_results[step_key] = result
                step_durations[step_key] = duration

                # 更新 DB：步驟完成
                await _save_task(
                    task_id,
                    step_results={**step_results},
                    step_durations={**step_durations},
                )

            except Exception as e:
                logger.error(
                    f"pipeline task {task_id} {step_key} 失敗: {e}",
                    exc_info=True,
                )
                duration = round(time.time() - step_start, 1)
                step_durations[step_key] = duration

                await _save_task(
                    task_id,
                    status="error",
                    current_step=None,
                    step_errors={step_key: str(e)},
                    step_durations={**step_durations},
                )
                return

        # 全部完成
        await _save_task(task_id, status="done", current_step=None)
        logger.info(f"pipeline task {task_id} 全部完成")

    except Exception as e:
        # 頂層兜底：任何未預期錯誤都不會讓任務狀態懸停
        logger.error(f"pipeline task {task_id} 頂層異常: {e}", exc_info=True)
        try:
            await _save_task(
                task_id,
                status="error",
                current_step=None,
                step_errors={"_fatal": str(e)},
            )
        except Exception:
            pass


async def _match_with_fresh_sessions(task_id: str) -> dict:
    """
    匹配步驟：委託給 matcher 的並行匹配引擎，透過回調回報進度

    matcher v2 內部管理獨立 session + Semaphore(4) 並行，
    不再需要此處手動逐商品建 session。
    """
    from app.services.matcher import match_all_pending

    async def on_progress(current: int, total: int, match_stats: dict, message: str):
        await _save_task(task_id, progress={
            "current": current,
            "total": total,
            "failed": match_stats.get("products_failed", 0),
            "message": f"({current}/{total}) {message}" if total > 0 else message,
            "stats": match_stats,
        })

    return await match_all_pending(progress_callback=on_progress)


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
                    if _key == "match":
                        # match_all_pending 自行管理 session（並行匹配）
                        step_result = await match_all_pending()
                    else:
                        async with async_session_maker() as session:
                            if _key == "build":
                                step_result = await CatalogService.build_catalog(
                                    session, platform=platform,
                                )
                            elif _key == "tag":
                                step_result = await tag_all_untagged(session)
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
