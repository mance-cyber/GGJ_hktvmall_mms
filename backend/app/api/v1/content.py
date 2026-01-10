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
    ContentOptimizeRequest,
    ContentOptimizeResponse,
    QuickSuggestionsResponse,
    QuickSuggestion,
)
from app.services.ai_service import get_ai_analysis_service
from app.services.content_optimizer import ContentOptimizer, QUICK_OPTIMIZATION_SUGGESTIONS

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

    # 使用 target_languages（如果提供），否則使用單一 language
    target_languages = request.target_languages if request.target_languages else ["TC"]

    ai_response = ai_service.generate_product_content(
        product_name=product_name,
        product_info=product_data,
        content_type=request.content_type,
        style=request.style,
        target_languages=target_languages,
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

        # 檢查是否為多語言格式
        is_multilang = len(target_languages) > 1 and any(
            key in content_json for key in ["TC", "SC", "EN", "multilang"]
        )

        if is_multilang:
            # 多語言格式：從 multilang 或頂層語言鍵獲取
            multilang_data = content_json.get("multilang", {})
            if not multilang_data:
                # 嘗試從頂層獲取語言鍵
                for lang in ["TC", "SC", "EN"]:
                    if lang in content_json:
                        multilang_data[lang] = content_json[lang]

            # 使用第一個語言作為主要顯示
            primary_lang = target_languages[0]
            primary_content = multilang_data.get(primary_lang, {})

            generated = GeneratedContent(
                title=primary_content.get("title", product_name),
                selling_points=primary_content.get("selling_points", []),
                description=primary_content.get("description", ""),
                short_description=primary_content.get("short_description"),
                multilang=multilang_data,
            )
        else:
            # 單語言格式
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


# =============================================
# 文案對話式優化 API
# =============================================

@router.post("/{content_id}/optimize", response_model=ContentOptimizeResponse)
async def optimize_content(
    content_id: UUID,
    request: ContentOptimizeRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    對話式優化文案

    通過用戶指令優化現有文案內容，支持多輪對話調整。
    """
    # 獲取現有內容
    result = await db.execute(
        select(AIContent).where(AIContent.id == content_id)
    )
    content = result.scalar_one_or_none()
    if not content:
        raise HTTPException(status_code=404, detail="內容不存在")

    # 獲取 AI 服務和優化器
    ai_service = await get_ai_analysis_service(db)
    optimizer = ContentOptimizer(ai_service=ai_service)

    # 準備產品資訊
    product_info = None
    if request.product_info:
        product_info = request.product_info.model_dump()
    elif content.input_data:
        product_info = content.input_data.get("product_info")

    # 執行優化
    optimization_result = optimizer.optimize(
        current_content=content.content_json or {"description": content.content},
        instruction=request.instruction,
        context=[msg.model_dump() for msg in request.context] if request.context else None,
        target_languages=request.target_languages,
        product_info=product_info,
    )

    if not optimization_result.success:
        raise HTTPException(
            status_code=503,
            detail=f"優化失敗: {optimization_result.error}"
        )

    # 更新內容版本
    new_version = content.version + 1

    # 保存優化歷史到 generation_metadata
    current_metadata = content.generation_metadata or {}
    optimization_history = current_metadata.get("optimization_history", [])
    optimization_history.append({
        "version": new_version,
        "instruction": request.instruction,
        "timestamp": datetime.utcnow().isoformat(),
    })

    # 更新數據庫記錄
    content.content_json = optimization_result.content
    content.content = optimization_result.content.get("description", "")
    content.version = new_version
    content.generation_metadata = {
        **current_metadata,
        "optimization_history": optimization_history,
        "last_optimized_at": datetime.utcnow().isoformat(),
        "tokens_used": optimization_result.tokens_used,
        "model": optimization_result.model,
    }

    await db.flush()
    await db.refresh(content)

    # 構建響應
    generated = GeneratedContent(
        title=optimization_result.content.get("title"),
        selling_points=optimization_result.content.get("selling_points"),
        description=optimization_result.content.get("description"),
        short_description=optimization_result.content.get("short_description"),
    )

    return ContentOptimizeResponse(
        content_id=content.id,
        content=generated,
        suggestions=optimization_result.suggestions,
        version=new_version,
        metadata={
            "tokens_used": optimization_result.tokens_used,
            "model": optimization_result.model,
        },
    )


@router.get("/optimize/suggestions", response_model=QuickSuggestionsResponse)
async def get_quick_suggestions():
    """獲取快捷優化建議列表"""
    suggestions = [
        QuickSuggestion(
            key=key,
            label=value["label"],
            instruction=value["instruction"],
        )
        for key, value in QUICK_OPTIMIZATION_SUGGESTIONS.items()
    ]
    return QuickSuggestionsResponse(suggestions=suggestions)
