# =============================================
# 內容生成任務
# =============================================

import asyncio
from uuid import UUID
from typing import List

from app.tasks.celery_app import celery_app


def run_async(coro):
    """在同步環境中運行異步代碼"""
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coro)


@celery_app.task(bind=True, name="app.tasks.content_tasks.generate_content_async")
def generate_content_async(
    self,
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

    async def _generate():
        connector = get_claude_connector()

        async with async_session_maker() as db:
            # 獲取商品
            result = await db.execute(
                select(Product).where(Product.id == UUID(product_id))
            )
            product = result.scalar_one_or_none()

            if not product:
                return {"error": "商品不存在"}

            # 準備商品資訊
            product_info = {
                "name": product.name,
                "brand": product.brand,
                "category": product.category,
                "features": product.attributes.get("features", []) if product.attributes else [],
                "price": str(product.price) if product.price else None,
            }

            # 生成內容
            generated = connector.generate_content(
                product_info=product_info,
                content_type=content_type,
                style=style,
                language=language,
            )

            # 保存到數據庫
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
                    "task_id": self.request.id,
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

    return run_async(_generate())


@celery_app.task(name="app.tasks.content_tasks.batch_generate_content")
def batch_generate_content(
    product_ids: List[str],
    content_type: str = "full_copy",
    style: str = "professional",
    language: str = "zh-HK",
):
    """
    批量生成商品文案

    Args:
        product_ids: 商品 UUID 列表
        content_type: 內容類型
        style: 風格
        language: 語言
    """
    results = []
    for product_id in product_ids:
        # 為每個商品創建生成任務
        task = generate_content_async.delay(
            product_id=product_id,
            content_type=content_type,
            style=style,
            language=language,
        )
        results.append({
            "product_id": product_id,
            "task_id": task.id,
        })

    return {
        "total": len(product_ids),
        "tasks": results,
    }
