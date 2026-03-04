# =============================================
# 智能匹配引擎 v2（pg_trgm 預篩 + 分拆 AI 精判）
# =============================================
# 核心改進：
# 1. pg_trgm 索引做文本相似度預篩，候選上限 25
# 2. 分拆 prompt：same_sub → L1/L2，cross_sub → L3
# 3. 支持 non-thinking 模型（2-4s vs 8-12s）
# 4. Semaphore 並行匹配（4 路）
# 5. 增量匹配 + Bulk UPSERT（不再刪舊記錄）
# =============================================

import asyncio
import re
import json
import logging
import uuid as _uuid
from decimal import Decimal
from typing import Optional, Callable, Awaitable

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.competitor import CompetitorProduct
from app.models.product import Product
from app.models.database import async_session_maker
from app.config import get_settings

logger = logging.getLogger(__name__)


# =============================================
# 配置常量
# =============================================

SAME_SUB_LIMIT = 15       # 同細分候選上限
CROSS_SUB_LIMIT = 10      # 跨細分候選上限
MATCH_CONCURRENCY = 4     # 並行匹配數
AI_MAX_TOKENS = 2000      # AI 回應 token 上限（non-thinking）

# 進度回調類型
ProgressCallback = Optional[Callable[[int, int, dict, str], Awaitable[None]]]


# =============================================
# 預篩：pg_trgm 文本相似度 + 候選上限
# =============================================

async def _prefilter(
    db: AsyncSession,
    product: Product,
) -> dict[str, list[dict]]:
    """
    pg_trgm 兩輪篩選，最多 25 個候選：
    - 同 sub_tag：trigram 相似度 top 15 → 送 AI 判 L1/L2
    - 跨 sub_tag（同 category）：trigram top 10 → 送 AI 判 L3
    """
    cat = product.category_tag
    if not cat:
        return {"same_sub": [], "cross_sub": []}

    sub = product.sub_tag or ""
    name = product.name_zh or product.name or ""
    if not name:
        return {"same_sub": [], "cross_sub": []}

    same_sub_rows = []

    if sub:
        # 同 sub_tag：similarity top 15
        result = await db.execute(
            text("""
                SELECT id, name, sub_tag,
                       similarity(name, :name) AS sim
                FROM competitor_products
                WHERE sub_tag = :sub_tag AND is_active = true
                ORDER BY sim DESC
                LIMIT :lim
            """),
            {"name": name, "sub_tag": sub, "lim": SAME_SUB_LIMIT},
        )
        same_sub_rows = [
            {"id": str(row.id), "name": row.name, "sub_tag": row.sub_tag or ""}
            for row in result
        ]

        # 跨 sub_tag：同大類但不同細分，similarity top 10
        cross_result = await db.execute(
            text("""
                SELECT id, name, sub_tag,
                       similarity(name, :name) AS sim
                FROM competitor_products
                WHERE category_tag = :cat
                  AND (sub_tag IS DISTINCT FROM :sub_tag)
                  AND is_active = true
                ORDER BY sim DESC
                LIMIT :lim
            """),
            {"name": name, "cat": cat, "sub_tag": sub, "lim": CROSS_SUB_LIMIT},
        )
    else:
        # 無 sub_tag：全品類取 top 25
        cross_result = await db.execute(
            text("""
                SELECT id, name, sub_tag,
                       similarity(name, :name) AS sim
                FROM competitor_products
                WHERE category_tag = :cat AND is_active = true
                ORDER BY sim DESC
                LIMIT :lim
            """),
            {"name": name, "cat": cat, "lim": SAME_SUB_LIMIT + CROSS_SUB_LIMIT},
        )

    cross_sub_rows = [
        {"id": str(row.id), "name": row.name, "sub_tag": row.sub_tag or ""}
        for row in cross_result
    ]

    return {"same_sub": same_sub_rows, "cross_sub": cross_sub_rows}


# =============================================
# AI 精判：分拆 prompt（same_sub → L1/L2, cross_sub → L3）
# =============================================

_SAME_SUB_PROMPT = """你是食品競品分析專家。我的商品是「{product_name}」({category_tag}/{sub_tag})。

以下 {n} 個候選都是同細分類（{sub_tag}），請判斷每個的競爭級別：

Level 1 (DIRECT 直接替代品)：同切割+同品種+同形態，消費者會直接比價
  例：「A5和牛西冷」vs「和牛西冷」
Level 2 (SIMILAR 近似競品)：同切割+不同品種/產地，消費者會考慮替代
  例：「A5和牛西冷」vs「澳洲安格斯西冷」

注意：
- 形態差異（牛排 vs 火鍋片 vs 肉碎）應判為 Level 2 或無關
- 規格差異超過 3 倍也應降一級
- 加工品（漢堡扒、餃子、香腸等）通常無關

候選列表：
{candidates_json}

返回 JSON 陣列：[{{"id": "xxx", "level": 1, "confidence": 0.85, "reason": "同為和牛西冷..."}}, ...]
level 為 null 表示無關。只輸出 JSON 數組，不要其他內容。"""


_CROSS_SUB_PROMPT = """你是食品競品分析專家。我的商品是「{product_name}」({category_tag}/{sub_tag})。

以下 {n} 個候選是同大類（{category_tag}）但不同細分，請判斷是否為品類競品：

Level 3 (CATEGORY 品類競品)：同大類+不同切割/形態，消費者在同品類中選擇
  例：「A5和牛西冷」vs「牛仔骨」

注意：
- 加工品（漢堡扒、餃子、香腸等）通常無關
- 完全不同品類一定是無關

候選列表：
{candidates_json}

返回 JSON 陣列：[{{"id": "xxx", "level": 3, "confidence": 0.7, "reason": "同為牛肉品類..."}}, ...]
level 為 null 表示無關。只輸出 JSON 數組，不要其他內容。"""


async def _ai_call(prompt: str) -> list[dict]:
    """通用 AI 調用：發送 prompt，解析 JSON 數組回應"""
    from app.connectors.claude import ClaudeConnector

    settings = get_settings()
    model = settings.ai_model_simple
    connector = ClaudeConnector(model=model)

    if not connector.client:
        logger.warning("AI 精判失敗：無可用的 Claude API 客戶端")
        return []

    try:
        max_tokens = 8000 if "thinking" in model else AI_MAX_TOKENS

        # 同步 Anthropic SDK → 卸載到線程池，避免阻塞事件循環
        message = await asyncio.to_thread(
            connector.client.messages.create,
            model=connector.model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )

        # 取最後一個 text block（兼容 thinking 模型）
        response_text = ""
        for block in message.content:
            if getattr(block, "type", None) == "text":
                response_text = block.text
        if not response_text:
            response_text = message.content[0].text if message.content else "[]"

        json_match = re.search(r'\[[\s\S]*\]', response_text)
        if not json_match:
            logger.warning(f"AI 精判返回格式異常: {response_text[:300]}")
            return []

        results = json.loads(json_match.group())
        return results if isinstance(results, list) else []

    except Exception as e:
        logger.error(f"AI 精判異常: {e}", exc_info=True)
        return []


async def _ai_judge_same_sub(
    product_name: str,
    category_tag: str,
    sub_tag: str,
    candidates: list[dict],
) -> list[dict]:
    """同 sub_tag 候選 → 判斷 L1 或 L2"""
    if not candidates:
        return []

    cands_for_ai = [
        {"id": c["id"], "name": c["name"], "sub_tag": c["sub_tag"]}
        for c in candidates
    ]
    prompt = _SAME_SUB_PROMPT.format(
        product_name=product_name,
        category_tag=category_tag,
        sub_tag=sub_tag,
        n=len(cands_for_ai),
        candidates_json=json.dumps(cands_for_ai, ensure_ascii=False, indent=2),
    )
    return await _ai_call(prompt)


async def _ai_judge_cross_sub(
    product_name: str,
    category_tag: str,
    sub_tag: str,
    candidates: list[dict],
) -> list[dict]:
    """跨 sub_tag 候選 → 判斷是否 L3"""
    if not candidates:
        return []

    cands_for_ai = [
        {"id": c["id"], "name": c["name"], "sub_tag": c["sub_tag"]}
        for c in candidates
    ]
    prompt = _CROSS_SUB_PROMPT.format(
        product_name=product_name,
        category_tag=category_tag,
        sub_tag=sub_tag or "其他",
        n=len(cands_for_ai),
        candidates_json=json.dumps(cands_for_ai, ensure_ascii=False, indent=2),
    )
    return await _ai_call(prompt)


# =============================================
# DB 持久化：Bulk UPSERT
# =============================================

_UPSERT_SQL = text("""
    INSERT INTO product_competitor_mapping
        (id, product_id, competitor_product_id,
         match_level, match_confidence, match_reason,
         is_verified, created_at)
    VALUES
        (gen_random_uuid(), :product_id, CAST(:cp_id AS UUID),
         :level, :confidence, :reason,
         false, NOW())
    ON CONFLICT (product_id, competitor_product_id)
    DO UPDATE SET
        match_level = EXCLUDED.match_level,
        match_confidence = EXCLUDED.match_confidence,
        match_reason = EXCLUDED.match_reason
""")


async def _bulk_upsert_mappings(
    db: AsyncSession,
    product_id: _uuid.UUID,
    ai_results: list[dict],
) -> dict:
    """
    增量寫入匹配結果（INSERT ON CONFLICT DO UPDATE）

    ai_results: [{"id": "cp-uuid", "level": 1|2|3|null, "confidence": 0.85, "reason": "..."}, ...]
    """
    stats = {"matched": 0, "level_1": 0, "level_2": 0, "level_3": 0, "skipped": 0}

    pid_str = str(product_id)

    for item in ai_results:
        level = item.get("level")
        cp_id = item.get("id")

        if level is None or cp_id is None or level not in (1, 2, 3):
            stats["skipped"] += 1
            continue

        confidence = min(max(float(item.get("confidence", 0.0)), 0.0), 1.0)
        reason = str(item.get("reason", ""))[:500]

        try:
            await db.execute(_UPSERT_SQL, {
                "product_id": pid_str,
                "cp_id": cp_id,
                "level": level,
                "confidence": round(confidence, 2),
                "reason": reason,
            })
            stats[f"level_{level}"] += 1
        except Exception as e:
            logger.warning(f"upsert mapping 失敗: product={product_id} cp={cp_id}: {e}")
            stats["skipped"] += 1

    stats["matched"] = stats["level_1"] + stats["level_2"] + stats["level_3"]
    return stats


# =============================================
# 主入口：單商品匹配
# =============================================

async def match_product(
    db: AsyncSession,
    product_id: str,
) -> dict:
    """
    為單個自家商品匹配競品（增量模式，不刪舊記錄）

    流程：
    1. 查詢商品 category_tag, sub_tag
    2. pg_trgm 預篩（最多 25 候選）
    3. 兩路 AI 並行精判（same_sub → L1/L2, cross_sub → L3）
    4. Bulk UPSERT 到 product_competitor_mapping
    """
    stats = {"matched": 0, "level_1": 0, "level_2": 0, "level_3": 0, "skipped": 0}

    pid = _uuid.UUID(product_id)
    result = await db.execute(select(Product).where(Product.id == pid))
    product = result.scalar_one_or_none()

    if not product:
        logger.warning(f"match_product: 找不到商品 {product_id}")
        return stats

    if not product.category_tag:
        logger.info(f"match_product: 商品未打標 {product_id}，跳過")
        return stats

    product_name = product.name_zh or product.name or ""

    # pg_trgm 預篩
    groups = await _prefilter(db, product)
    same_sub = groups["same_sub"]
    cross_sub = groups["cross_sub"]

    if not same_sub and not cross_sub:
        logger.info(f"match_product: 無候選競品 {product_name}")
        return stats

    logger.info(
        f"match_product: {product_name} → "
        f"same_sub={len(same_sub)}, cross_sub={len(cross_sub)}"
    )

    # 兩路 AI 並行精判
    same_results, cross_results = await asyncio.gather(
        _ai_judge_same_sub(
            product_name, product.category_tag, product.sub_tag or "其他", same_sub,
        ),
        _ai_judge_cross_sub(
            product_name, product.category_tag, product.sub_tag or "其他", cross_sub,
        ),
    )

    # Bulk UPSERT
    all_ai_results = same_results + cross_results
    stats = await _bulk_upsert_mappings(db, pid, all_ai_results)

    await db.flush()

    logger.info(
        f"match_product 完成: {product_name} → "
        f"L1={stats['level_1']} L2={stats['level_2']} L3={stats['level_3']} "
        f"skipped={stats['skipped']}"
    )

    return stats


# =============================================
# 批量匹配：並行 + 進度回報
# =============================================

async def match_all_pending(
    progress_callback: ProgressCallback = None,
) -> dict:
    """
    掃描所有 needs_matching=True 的競品，為相關自家商品並行匹配

    每個商品使用獨立 DB session（避免 Neon idle timeout）。
    Semaphore(4) 控制並行度，進度回調支持管線整合。
    """
    stats = {
        "products_matched": 0,
        "products_failed": 0,
        "competitors_processed": 0,
        "total_level_1": 0,
        "total_level_2": 0,
        "total_level_3": 0,
    }

    # Phase 1: 查詢待匹配數據（短暫 session，用完即關）
    async with async_session_maker() as session:
        result = await session.execute(
            select(CompetitorProduct.id, CompetitorProduct.category_tag).where(
                CompetitorProduct.needs_matching == True,
                CompetitorProduct.is_active == True,
                CompetitorProduct.category_tag.isnot(None),
            )
        )
        pending_rows = list(result)

        if not pending_rows:
            logger.info("match_all_pending: 無待匹配的競品")
            if progress_callback:
                await progress_callback(0, 0, stats, "無待匹配競品")
            return stats

        pending_cp_ids = [row[0] for row in pending_rows]
        affected_tags = {row[1] for row in pending_rows}

        result = await session.execute(
            select(Product.id, Product.name).where(
                Product.category_tag.in_(affected_tags),
            )
        )
        products = [(str(row[0]), row[1] or "") for row in result]

    if not products:
        # 無相關自家商品，僅清除 needs_matching 標記
        async with async_session_maker() as session:
            result = await session.execute(
                select(CompetitorProduct).where(CompetitorProduct.id.in_(pending_cp_ids))
            )
            for cp in result.scalars().all():
                cp.needs_matching = False
            await session.commit()
        stats["competitors_processed"] = len(pending_cp_ids)
        return stats

    total = len(products)
    logger.info(
        f"match_all_pending: {total} 個商品, "
        f"{len(pending_cp_ids)} 個待匹配競品, 品類: {affected_tags}"
    )

    if progress_callback:
        await progress_callback(0, total, stats, f"準備匹配 {total} 個商品...")

    # Phase 2: Semaphore 並行匹配
    sem = asyncio.Semaphore(MATCH_CONCURRENCY)
    completed = 0
    lock = asyncio.Lock()

    async def _match_one(pid: str, pname: str) -> dict:
        nonlocal completed

        product_stats = {"matched": 0, "level_1": 0, "level_2": 0, "level_3": 0, "skipped": 0}
        error = None

        try:
            async with sem:
                async with async_session_maker() as session:
                    product_stats = await match_product(session, pid)
                    await session.commit()
        except Exception as e:
            error = e
            logger.error(f"match_all_pending: product {pid} 失敗: {e}", exc_info=True)

        # 更新進度（原子操作）
        async with lock:
            completed += 1
            if error:
                stats["products_failed"] += 1
            else:
                stats["products_matched"] += 1
                stats["total_level_1"] += product_stats["level_1"]
                stats["total_level_2"] += product_stats["level_2"]
                stats["total_level_3"] += product_stats["level_3"]

            if progress_callback:
                short_name = pname[:30] + "..." if len(pname) > 30 else pname
                await progress_callback(completed, total, {**stats}, short_name)

        return product_stats

    tasks = [_match_one(pid, pname) for pid, pname in products]
    await asyncio.gather(*tasks, return_exceptions=True)

    # Phase 3: 清除 needs_matching 標記
    if progress_callback:
        await progress_callback(total, total, stats, "清除匹配標記...")

    async with async_session_maker() as session:
        result = await session.execute(
            select(CompetitorProduct).where(CompetitorProduct.id.in_(pending_cp_ids))
        )
        for cp in result.scalars().all():
            cp.needs_matching = False
        await session.commit()

    stats["competitors_processed"] = len(pending_cp_ids)

    logger.info(
        f"match_all_pending 完成: "
        f"products={stats['products_matched']}, failed={stats['products_failed']}, "
        f"L1={stats['total_level_1']} L2={stats['total_level_2']} L3={stats['total_level_3']}"
    )

    return stats
