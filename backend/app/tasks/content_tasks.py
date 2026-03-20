# =============================================
# 內容生成任務（純 async，無 Celery 依賴）
# =============================================

import asyncio
import logging
from uuid import UUID
from typing import List

logger = logging.getLogger(__name__)


async def generate_content_async(
    product_id: str,
    content_type: str = "full_copy",
    style: str = "professional",
    language: str = "zh-HK",
):
    """
    異步生成商品文案

    Args:
        product_id: 商品 UUID
        content_type: 內容類型
        style: 風格
        language: 語言
    """
    from app.models.database import async_session_maker
    from app.models.product import Product
    from app.models.content import AIContent
    from app.connectors.claude import get_claude_connector
    from sqlalchemy import select

    connector = get_claude_connector()

    async with async_session_maker() as db:
        result = await db.execute(
            select(Product).where(Product.id == UUID(product_id))
        )
        product = result.scalar_one_or_none()

        if not product:
            return {"error": "商品不存在"}

        product_info = {
            "name": product.name,
            "brand": product.brand,
            "category": product.category,
            "features": product.attributes.get("features", []) if product.attributes else [],
            "price": str(product.price) if product.price else None,
        }

        generated = connector.generate_content(
            product_info=product_info,
            content_type=content_type,
            style=style,
            language=language,
        )

        content = AIContent(
            product_id=product.id,
            content_type=content_type,
            style=style,
            language=language,
            content=generated.full_copy or generated.description or "",
            content_json={
                "title": generated.title,
                "selling_points": generated.selling_points,
                "description": generated.description,
            },
            status="draft",
            metadata={
                "model": generated.model,
                "tokens_used": generated.tokens_used,
            },
        )
        db.add(content)
        await db.commit()
        await db.refresh(content)

        return {
            "success": True,
            "content_id": str(content.id),
            "tokens_used": generated.tokens_used,
        }


async def batch_generate_content_async(
    product_ids: List[str],
    content_type: str = "full_copy",
    style: str = "professional",
    language: str = "zh-HK",
):
    """
    批量生成商品文案（為每個商品創建背景任務）

    Args:
        product_ids: 商品 UUID 列表
        content_type: 內容類型
        style: 風格
        language: 語言
    """
    tasks = []
    for product_id in product_ids:
        task = asyncio.create_task(
            generate_content_async(
                product_id=product_id,
                content_type=content_type,
                style=style,
                language=language,
            )
        )
        tasks.append({"product_id": product_id, "task": task})

    return {
        "total": len(product_ids),
        "tasks_created": len(tasks),
    }
