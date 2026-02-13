# =============================================
# 智能匹配引擎（預篩 + AI 精判三層關係）
# 根據標籤預篩候選，AI 判定 Level 1/2/3，寫入 DB
# =============================================

import re
import json
import logging
import uuid as _uuid
from decimal import Decimal
from sqlalchemy import select, delete, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.competitor import CompetitorProduct
from app.models.product import Product, ProductCompetitorMapping
from app.config import get_settings

logger = logging.getLogger(__name__)

AI_BATCH_SIZE = 20


# =============================================
# 預篩：用標籤縮小候選範圍
# =============================================

async def _prefilter(
    db: AsyncSession,
    product: Product,
) -> dict[str, list[CompetitorProduct]]:
    """
    預篩：按 category_tag + sub_tag 查詢候選競品

    返回：
      {"same_sub": [...], "same_cat": [...]}
      same_sub = 同大類 + 同細分 → 送 AI 判 Level 1 or 2
      same_cat = 同大類 + 不同細分 → 送 AI 判 Level 3 or 無關
    """
    cat = product.category_tag
    if not cat:
        return {"same_sub": [], "same_cat": []}

    sub = product.sub_tag

    # 同大類的所有活躍競品
    stmt = (
        select(CompetitorProduct)
        .where(
            CompetitorProduct.is_active == True,
            CompetitorProduct.category_tag == cat,
        )
    )
    result = await db.execute(stmt)
    all_same_cat = list(result.scalars().all())

    same_sub = []
    same_cat = []
    for cp in all_same_cat:
        if sub and cp.sub_tag == sub:
            same_sub.append(cp)
        else:
            same_cat.append(cp)

    return {"same_sub": same_sub, "same_cat": same_cat}


# =============================================
# AI 精判
# =============================================

_MATCH_PROMPT = """你是食品競品分析專家。我的商品是「{product_name}」({category_tag}/{sub_tag})。

以下是 {n} 個候選競品，請判斷每個與我的商品的競爭關係：

Level 1 (DIRECT 直接替代品)：同切割+同品種+同形態，消費者會直接比價
  例：「A5和牛西冷」vs「和牛西冷」
Level 2 (SIMILAR 近似競品)：同切割+不同品種/產地，消費者會考慮替代
  例：「A5和牛西冷」vs「澳洲安格斯西冷」
Level 3 (CATEGORY 品類競品)：同大類+不同切割/形態
  例：「A5和牛西冷」vs「牛仔骨」
無關：不是競品（加工食品、調味料、完全不同品類等）

注意：
- 形態差異很重要：牛排 vs 火鍋片 vs 肉碎 是不同形態，應降一級
- 規格差異超過 3 倍也應降一級
- 加工品（漢堡扒、餃子、香腸等）通常是 Level 3 或無關

候選列表：
{candidates_json}

返回 JSON 陣列：
[{{"index": 0, "level": 1, "confidence": 0.85, "reason": "同為和牛西冷..."}}, ...]
level 為 null 表示無關。

只輸出 JSON 數組，不要其他內容。"""


async def _ai_judge(
    product_name: str,
    category_tag: str,
    sub_tag: str,
    candidates: list[dict],
) -> list[dict]:
    """
    AI 精判一批候選

    candidates: [{"index": 0, "name": "...", "sub_tag": "..."}, ...]
    返回: [{"index": 0, "level": 1|2|3|None, "confidence": 0.85, "reason": "..."}, ...]
    """
    if not candidates:
        return []

    from app.connectors.claude import ClaudeConnector

    settings = get_settings()
    model = settings.ai_model_simple
    connector = ClaudeConnector(model=model)

    if not connector.client:
        logger.warning("AI 精判失敗：無可用的 Claude API 客戶端")
        return []

    candidates_json = json.dumps(candidates, ensure_ascii=False, indent=2)

    prompt = _MATCH_PROMPT.format(
        product_name=product_name,
        category_tag=category_tag,
        sub_tag=sub_tag,
        n=len(candidates),
        candidates_json=candidates_json,
    )

    try:
        max_tokens = 8000 if "thinking" in model else 3000
        message = connector.client.messages.create(
            model=connector.model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )

        # thinking 模型返回多個 block，取最後一個 text block
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
        if not isinstance(results, list):
            logger.warning(f"AI 精判返回非數組: {type(results)}")
            return []

        return results

    except Exception as e:
        logger.error(f"AI 精判異常: {e}", exc_info=True)
        return []


# =============================================
# DB 持久化
# =============================================

async def _save_matches(
    db: AsyncSession,
    product_id: _uuid.UUID,
    matches: list[dict],
    candidate_map: dict[int, CompetitorProduct],
) -> int:
    """
    將匹配結果寫入 product_competitor_mapping（upsert 模式）

    matches: AI 返回的 [{"index": 0, "level": 1, "confidence": 0.85, "reason": "..."}, ...]
    candidate_map: {index: CompetitorProduct} 索引映射
    返回成功寫入的數量。
    """
    saved = 0
    for item in matches:
        idx = item.get("index")
        level = item.get("level")
        if level is None or idx not in candidate_map:
            continue

        cp = candidate_map[idx]
        confidence = float(item.get("confidence", 0.0))
        reason = item.get("reason", "")

        # upsert：查詢已有記錄
        stmt = select(ProductCompetitorMapping).where(
            and_(
                ProductCompetitorMapping.product_id == product_id,
                ProductCompetitorMapping.competitor_product_id == cp.id,
            )
        )
        result = await db.execute(stmt)
        mapping = result.scalar_one_or_none()

        if mapping:
            mapping.match_level = level
            mapping.match_confidence = Decimal(str(round(confidence, 2)))
            mapping.match_reason = reason
        else:
            mapping = ProductCompetitorMapping(
                product_id=product_id,
                competitor_product_id=cp.id,
                match_level=level,
                match_confidence=Decimal(str(round(confidence, 2))),
                match_reason=reason,
                is_verified=False,
            )
            db.add(mapping)
            try:
                await db.flush()
            except IntegrityError:
                await db.rollback()
                logger.warning(
                    f"mapping 衝突: product={product_id} cp={cp.id}，跳過"
                )
                continue

        saved += 1

    return saved


# =============================================
# 主入口
# =============================================

async def match_product(
    db: AsyncSession,
    product_id: str,
) -> dict:
    """
    為單個自家商品匹配所有競品

    流程：
    1. 查詢商品的 category_tag, sub_tag
    2. 預篩：查詢同標籤的 competitor_products
    3. 刪除舊匹配記錄（全量重建）
    4. AI 精判：批量送 20 個候選
    5. 存入 product_competitor_mapping + match_level
    """
    stats = {"matched": 0, "level_1": 0, "level_2": 0, "level_3": 0, "skipped": 0}

    # 查詢自家商品
    pid = _uuid.UUID(product_id)
    stmt = select(Product).where(Product.id == pid)
    result = await db.execute(stmt)
    product = result.scalar_one_or_none()
    if not product:
        logger.warning(f"match_product: 找不到商品 {product_id}")
        return stats

    if not product.category_tag:
        logger.info(f"match_product: 商品未打標 {product_id}，跳過")
        return stats

    product_name = product.name_zh or product.name or ""

    # 預篩
    groups = await _prefilter(db, product)
    same_sub = groups["same_sub"]
    same_cat = groups["same_cat"]
    total_candidates = len(same_sub) + len(same_cat)

    if total_candidates == 0:
        logger.info(f"match_product: 無候選競品 {product_name}")
        return stats

    logger.info(
        f"match_product: {product_name} → "
        f"same_sub={len(same_sub)}, same_cat={len(same_cat)}"
    )

    # 刪除舊匹配記錄（全量重建）
    del_stmt = delete(ProductCompetitorMapping).where(
        ProductCompetitorMapping.product_id == pid
    )
    await db.execute(del_stmt)

    # 構建候選列表（帶全局 index）
    all_candidates: list[dict] = []
    candidate_map: dict[int, CompetitorProduct] = {}

    for cp in same_sub:
        idx = len(all_candidates)
        all_candidates.append({
            "index": idx,
            "name": cp.name,
            "sub_tag": cp.sub_tag or "",
            "hint": "same_sub",
        })
        candidate_map[idx] = cp

    for cp in same_cat:
        idx = len(all_candidates)
        all_candidates.append({
            "index": idx,
            "name": cp.name,
            "sub_tag": cp.sub_tag or "",
            "hint": "same_cat",
        })
        candidate_map[idx] = cp

    # 批量 AI 精判
    all_ai_results: list[dict] = []
    for batch_start in range(0, len(all_candidates), AI_BATCH_SIZE):
        batch = all_candidates[batch_start : batch_start + AI_BATCH_SIZE]
        ai_results = await _ai_judge(
            product_name,
            product.category_tag,
            product.sub_tag or "其他",
            batch,
        )
        all_ai_results.extend(ai_results)

    # 存入 DB
    saved = await _save_matches(db, pid, all_ai_results, candidate_map)

    # 統計
    for item in all_ai_results:
        level = item.get("level")
        if level == 1:
            stats["level_1"] += 1
        elif level == 2:
            stats["level_2"] += 1
        elif level == 3:
            stats["level_3"] += 1
        else:
            stats["skipped"] += 1

    stats["matched"] = stats["level_1"] + stats["level_2"] + stats["level_3"]

    try:
        await db.flush()
    except Exception as e:
        logger.error(f"match_product flush 失敗: {e}", exc_info=True)

    logger.info(
        f"match_product 完成: {product_name} → "
        f"L1={stats['level_1']} L2={stats['level_2']} L3={stats['level_3']} "
        f"skipped={stats['skipped']}"
    )

    return stats


async def match_all_pending(db: AsyncSession) -> dict:
    """
    掃描所有 needs_matching=True 的競品，為相關自家商品重新匹配

    流程：
    1. 查詢 needs_matching=True 的 competitor_products
    2. 收集這些競品的 category_tag 集合
    3. 找到具有這些 category_tag 的自家商品
    4. 對每個自家商品調用 match_product
    5. 更新 needs_matching=False
    """
    stats = {
        "products_matched": 0,
        "competitors_processed": 0,
        "total_level_1": 0,
        "total_level_2": 0,
        "total_level_3": 0,
    }

    # 查詢待匹配的競品
    stmt = select(CompetitorProduct).where(
        CompetitorProduct.needs_matching == True,
        CompetitorProduct.is_active == True,
        CompetitorProduct.category_tag.isnot(None),
    )
    result = await db.execute(stmt)
    pending_cps = list(result.scalars().all())

    if not pending_cps:
        logger.info("match_all_pending: 無待匹配的競品")
        return stats

    # 收集受影響的 category_tag
    affected_tags = {cp.category_tag for cp in pending_cps if cp.category_tag}

    logger.info(
        f"match_all_pending: {len(pending_cps)} 個待匹配競品, "
        f"涉及品類: {affected_tags}"
    )

    # 找到具有這些標籤的自家商品
    stmt = select(Product).where(
        Product.category_tag.in_(affected_tags),
    )
    result = await db.execute(stmt)
    products = list(result.scalars().all())

    if not products:
        logger.info("match_all_pending: 無相關自家商品需要匹配")
        # 仍然要清除 needs_matching 標記
        for cp in pending_cps:
            cp.needs_matching = False
        await db.flush()
        stats["competitors_processed"] = len(pending_cps)
        return stats

    # 對每個自家商品匹配
    for product in products:
        product_stats = await match_product(db, str(product.id))
        stats["products_matched"] += 1
        stats["total_level_1"] += product_stats["level_1"]
        stats["total_level_2"] += product_stats["level_2"]
        stats["total_level_3"] += product_stats["level_3"]

    # 更新 needs_matching = False
    for cp in pending_cps:
        cp.needs_matching = False

    try:
        await db.flush()
    except Exception as e:
        logger.error(f"match_all_pending flush 失敗: {e}", exc_info=True)

    stats["competitors_processed"] = len(pending_cps)

    logger.info(
        f"match_all_pending 完成: "
        f"products={stats['products_matched']}, "
        f"competitors={stats['competitors_processed']}, "
        f"L1={stats['total_level_1']} L2={stats['total_level_2']} L3={stats['total_level_3']}"
    )

    return stats
