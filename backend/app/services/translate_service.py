# =============================================
# 商品名稱翻譯服務
# =============================================
# 用途：將中文商品名翻譯為英文，填充 name_en 欄位
# 觸發時機：
#   1. 抓取完成後（scrape.completed 事件）
#   2. 每日排程補漏（schedule.translate）
# =============================================

import logging
from typing import Optional

import httpx
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.competitor import CompetitorProduct
from app.models.product import Product

logger = logging.getLogger(__name__)

TRANSLATE_PROMPT = (
    "Translate this HKTVmall product name to concise English. "
    "Keep brand names, weights, and specs. Return ONLY the English name:\n{name}"
)


async def _call_anthropic(name: str) -> Optional[str]:
    """調用 Anthropic API 翻譯單個商品名。"""
    settings = get_settings()
    api_key = settings.anthropic_api_key
    if not api_key:
        logger.warning("ANTHROPIC_API_KEY 未設定，跳過翻譯")
        return None

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": "claude-haiku-4-5-20251001",
                    "max_tokens": 150,
                    "messages": [{"role": "user", "content": TRANSLATE_PROMPT.format(name=name)}],
                },
            )
            if resp.status_code == 200:
                return resp.json()["content"][0]["text"].strip().strip('"')
            else:
                logger.warning(f"翻譯 API {resp.status_code}: {resp.text[:120]}")
                return None
    except Exception as e:
        logger.error(f"翻譯失敗: {e}")
        return None


async def translate_new_competitor_products(
    db: AsyncSession,
    competitor_id: Optional[str] = None,
    limit: int = 50,
) -> int:
    """
    翻譯尚無 name_en 的競品商品。

    Args:
        db: 數據庫 session
        competitor_id: 可選，只翻譯指定商戶的商品
        limit: 單次最多翻譯數量

    Returns:
        成功翻譯的數量
    """
    query = select(CompetitorProduct).where(
        CompetitorProduct.name_en.is_(None),
        CompetitorProduct.is_active.is_(True),
    )
    if competitor_id:
        from uuid import UUID
        query = query.where(CompetitorProduct.competitor_id == UUID(competitor_id))
    query = query.order_by(CompetitorProduct.created_at.desc()).limit(limit)

    result = await db.execute(query)
    products = result.scalars().all()

    if not products:
        return 0

    translated = 0
    for product in products:
        name_en = await _call_anthropic(product.name)
        if name_en:
            product.name_en = name_en
            translated += 1

    if translated > 0:
        await db.flush()

    logger.info(f"競品翻譯完成: {translated}/{len(products)}")
    return translated


async def translate_new_own_products(
    db: AsyncSession,
    limit: int = 50,
) -> int:
    """
    翻譯尚無 name_en 的自家商品。

    Returns:
        成功翻譯的數量
    """
    query = (
        select(Product)
        .where(
            Product.name_en.is_(None),
            Product.status == "active",
        )
        .order_by(Product.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(query)
    products = result.scalars().all()

    if not products:
        return 0

    translated = 0
    for product in products:
        name_en = await _call_anthropic(product.name)
        if name_en:
            product.name_en = name_en
            translated += 1

    if translated > 0:
        await db.flush()

    logger.info(f"自家商品翻譯完成: {translated}/{len(products)}")
    return translated


async def translate_all_missing(db: AsyncSession, limit: int = 100) -> dict:
    """
    翻譯所有缺失 name_en 的商品（競品 + 自家）。
    用於每日排程補漏。

    Returns:
        {"competitor": n, "own": m}
    """
    cp_count = await translate_new_competitor_products(db, limit=limit)
    own_count = await translate_new_own_products(db, limit=limit)
    return {"competitor": cp_count, "own": own_count}
