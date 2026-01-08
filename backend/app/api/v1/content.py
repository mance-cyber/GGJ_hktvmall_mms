# =============================================
# AI 內容生成 API
# =============================================

import json
from typing import Optional
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import get_db
from app.models.content import AIContent
from app.models.product import Product
from app.schemas.content import (
    ContentGenerateRequest,
    ContentBatchGenerateRequest,
    ContentGenerateResponse,
    ContentResponse,
    ContentListResponse,
    ContentApproveResponse,
    BatchTaskResponse,
    GeneratedContent,
)
from app.services.ai_service import get_ai_analysis_service

router = APIRouter()


@router.post("/generate", response_model=ContentGenerateResponse)
async def generate_content(
    request: ContentGenerateRequest,
    db: AsyncSession = Depends(get_db),
):
    """生成 AI 文案"""
    product = None
    product_info = request.product_info

    # 如果提供了 product_id，獲取商品資訊
    if request.product_id:
        result = await db.execute(
            select(Product).where(Product.id == request.product_id)
        )
        product = result.scalar_one_or_none()
        if not product:
            raise HTTPException(status_code=404, detail="商品不存在")

    # 構建產品資訊
    product_name = ""
    product_data = {}

    if product:
        product_name = product.name
        product_data = {
            "name": product.name,
            "brand": product.brand,
            "price": float(product.price) if product.price else None,
            "original_price": float(product.original_price) if product.original_price else None,
            "description": product.description,
            "category": product.category,
        }
    elif product_info:
        product_name = product_info.name
        product_data = product_info.model_dump()

    if not product_name:
        raise HTTPException(status_code=400, detail="請提供商品資訊")

    # 調用 AI 服務生成內容
    ai_service = await get_ai_analysis_service(db)
    ai_response = ai_service.generate_product_content(
        product_name=product_name,
        product_info=product_data,
        content_type=request.content_type,
        style=request.style,
        language=request.language,
    )

    # 處理 AI 響應
    if not ai_response.success:
        # AI 調用失敗，返回錯誤或使用備用方案
        raise HTTPException(
            status_code=503,
            detail=f"AI 服務暫時不可用: {ai_response.error}"
        )

    # 解析 AI 返回的 JSON
    try:
        content_json = json.loads(ai_response.content)
        generated = GeneratedContent(
            title=content_json.get("title", product_name),
            selling_points=content_json.get("selling_points", []),
            description=content_json.get("description", ""),
            short_description=content_json.get("short_description"),
            hashtags=content_json.get("hashtags"),
        )
    except json.JSONDecodeError:
        # 如果 AI 沒有返回有效 JSON，使用原始內容
        generated = GeneratedContent(
            title=product_name,
            selling_points=[],
            description=ai_response.content,
        )

    # 保存到數據庫
    content = AIContent(
        product_id=request.product_id,
        content_type=request.content_type,
        style=request.style,
        language=request.language,
        content=generated.description or "",
        content_json=generated.model_dump(),
        status="draft",
        metadata={
            "model": ai_response.model,
            "tokens_used": ai_response.tokens_used,
            "generated_by": "ai"
        },
        input_data=request.model_dump() if request.product_info else None,
    )
    db.add(content)
    await db.flush()
    await db.refresh(content)

    return ContentGenerateResponse(
        id=content.id,
        content_type=content.content_type,
        content=generated,
        metadata=content.metadata or {},
    )


@router.post("/batch-generate", response_model=BatchTaskResponse, status_code=202)
async def batch_generate_content(
    request: ContentBatchGenerateRequest,
    db: AsyncSession = Depends(get_db),
):
    """批量生成 AI 文案"""
    # 驗證所有商品存在
    for product_id in request.product_ids:
        result = await db.execute(
            select(Product).where(Product.id == product_id)
        )
        if not result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail=f"商品 {product_id} 不存在")

    # TODO: 觸發 Celery 批量生成任務
    # task = batch_generate_content.delay(...)

    return BatchTaskResponse(
        task_id="pending",
        message="批量生成任務已啟動",
        product_count=len(request.product_ids),
    )


@router.get("/history", response_model=ContentListResponse)
async def list_content_history(
    db: AsyncSession = Depends(get_db),
    product_id: Optional[UUID] = None,
    status: Optional[str] = None,
    content_type: Optional[str] = None,
    limit: int = Query(default=50, ge=1, le=200),
):
    """獲取生成歷史"""
    query = select(AIContent)

    if product_id:
        query = query.where(AIContent.product_id == product_id)
    if status:
        query = query.where(AIContent.status == status)
    if content_type:
        query = query.where(AIContent.content_type == content_type)

    query = query.order_by(AIContent.generated_at.desc()).limit(limit)

    result = await db.execute(query)
    contents = result.scalars().all()

    # 獲取關聯的商品名稱
    data = []
    for content in contents:
        product_name = None
        if content.product_id:
            product_result = await db.execute(
                select(Product.name).where(Product.id == content.product_id)
            )
            product_name = product_result.scalar()

        data.append(ContentResponse(
            id=content.id,
            product_id=content.product_id,
            product_name=product_name,
            content_type=content.content_type,
            style=content.style,
            language=content.language,
            content=content.content,
            content_json=content.content_json,
            version=content.version,
            status=content.status,
            generated_at=content.generated_at,
            approved_at=content.approved_at,
            approved_by=content.approved_by,
        ))

    return ContentListResponse(data=data, total=len(data))


@router.put("/{content_id}/approve", response_model=ContentApproveResponse)
async def approve_content(
    content_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """審批內容"""
    result = await db.execute(
        select(AIContent).where(AIContent.id == content_id)
    )
    content = result.scalar_one_or_none()
    if not content:
        raise HTTPException(status_code=404, detail="內容不存在")

    content.status = "approved"
    content.approved_at = datetime.utcnow()
    # content.approved_by = current_user.email  # TODO: 從認證獲取

    await db.flush()

    return ContentApproveResponse(
        id=content.id,
        status=content.status,
        approved_at=content.approved_at,
    )


@router.put("/{content_id}/reject")
async def reject_content(
    content_id: UUID,
    reason: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """拒絕內容"""
    result = await db.execute(
        select(AIContent).where(AIContent.id == content_id)
    )
    content = result.scalar_one_or_none()
    if not content:
        raise HTTPException(status_code=404, detail="內容不存在")

    content.status = "rejected"
    content.rejected_reason = reason

    await db.flush()

    return {"message": "已拒絕", "reason": reason}
