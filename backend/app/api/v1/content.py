# =============================================
# AI 內容生成 API
# =============================================

import csv
import io
import json
from typing import Optional, List, Union
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
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
    BatchGenerateSyncResponse,
    BatchGenerateAsyncResponse,
    BatchTaskStatusResponse,
    BatchProgress,
)
from app.services.ai_service import get_ai_analysis_service
from app.services.content_optimizer import ContentOptimizer, QUICK_OPTIMIZATION_SUGGESTIONS
from app.services.batch_content_service import get_batch_content_service, BatchContentService

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


@router.post("/batch-generate", response_model=Union[BatchGenerateSyncResponse, BatchGenerateAsyncResponse])
async def batch_generate_content(
    request: ContentBatchGenerateRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    批量生成 AI 文案

    智能判斷處理模式：
    - ≤10 個商品：同步處理，直接返回結果
    - >10 個商品：異步處理，返回任務ID供查詢進度
    """
    # 驗證請求
    if not request.items:
        raise HTTPException(status_code=400, detail="請提供至少一個商品")

    if len(request.items) > 100:
        raise HTTPException(status_code=400, detail="單次最多支持 100 個商品")

    # 驗證 product_id 存在性
    for i, item in enumerate(request.items):
        if item.product_id:
            result = await db.execute(
                select(Product).where(Product.id == item.product_id)
            )
            if not result.scalar_one_or_none():
                raise HTTPException(
                    status_code=404,
                    detail=f"第 {i+1} 項的商品 {item.product_id} 不存在"
                )
        elif not item.product_info:
            raise HTTPException(
                status_code=400,
                detail=f"第 {i+1} 項必須提供 product_id 或 product_info"
            )

    # 調用批量生成服務
    batch_service = await get_batch_content_service(db)
    result = await batch_service.generate_batch(request)

    # 根據模式返回不同響應
    if result["mode"] == "sync":
        return BatchGenerateSyncResponse(**result)
    else:
        return BatchGenerateAsyncResponse(**result)


@router.get("/batch-generate/{task_id}/status", response_model=BatchTaskStatusResponse)
async def get_batch_task_status(task_id: str):
    """
    查詢批量生成任務狀態

    用於異步模式下查詢任務進度和結果
    """
    status = BatchContentService.get_task_status(task_id)
    if not status:
        raise HTTPException(status_code=404, detail="任務不存在或已過期")

    return BatchTaskStatusResponse(
        task_id=status["task_id"],
        status=status["status"],
        progress=BatchProgress(**status["progress"]),
        results=status["results"],
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


# =============================================
# 批量導出與模板 API
# =============================================

@router.get("/export")
async def export_content_csv(
    content_ids: str = Query(..., description="內容ID列表，逗號分隔"),
    db: AsyncSession = Depends(get_db),
):
    """
    導出生成內容為 CSV 文件

    Args:
        content_ids: 逗號分隔的內容ID列表
    """
    # 解析 content_ids
    try:
        id_list = [UUID(id.strip()) for id in content_ids.split(",") if id.strip()]
    except ValueError:
        raise HTTPException(status_code=400, detail="無效的內容ID格式")

    if not id_list:
        raise HTTPException(status_code=400, detail="請提供至少一個內容ID")

    if len(id_list) > 500:
        raise HTTPException(status_code=400, detail="單次最多導出 500 條記錄")

    # 查詢內容
    result = await db.execute(
        select(AIContent).where(AIContent.id.in_(id_list))
    )
    contents = result.scalars().all()

    if not contents:
        raise HTTPException(status_code=404, detail="未找到任何內容")

    # 獲取關聯的商品名稱
    content_map = {}
    for content in contents:
        product_name = ""
        if content.product_id:
            product_result = await db.execute(
                select(Product.name).where(Product.id == content.product_id)
            )
            product_name = product_result.scalar() or ""

        # 從 content_json 或 input_data 獲取商品名稱
        if not product_name:
            if content.content_json and content.content_json.get("title"):
                product_name = content.content_json.get("title", "")
            elif content.input_data and content.input_data.get("product_info"):
                product_name = content.input_data["product_info"].get("name", "")

        content_map[content.id] = {
            "content": content,
            "product_name": product_name,
        }

    # 生成 CSV
    output = io.StringIO()
    writer = csv.writer(output)

    # 寫入表頭
    writer.writerow([
        "商品名稱",
        "標題",
        "賣點",
        "描述",
        "內容類型",
        "風格",
        "狀態",
        "生成時間",
    ])

    # 寫入數據
    for content_id in id_list:
        if content_id not in content_map:
            continue

        item = content_map[content_id]
        content = item["content"]
        product_name = item["product_name"]

        # 從 content_json 解析
        content_json = content.content_json or {}
        title = content_json.get("title", "")
        selling_points = content_json.get("selling_points", [])
        description = content_json.get("description", content.content or "")

        # 賣點轉為換行分隔的字符串
        selling_points_str = "\n".join(selling_points) if isinstance(selling_points, list) else ""

        writer.writerow([
            product_name,
            title,
            selling_points_str,
            description,
            content.content_type,
            content.style or "",
            content.status,
            content.generated_at.strftime("%Y-%m-%d %H:%M:%S") if content.generated_at else "",
        ])

    # 返回 CSV 文件
    output.seek(0)

    # 添加 BOM 以支持 Excel 正確識別 UTF-8
    bom = '\ufeff'
    csv_content = bom + output.getvalue()

    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f"attachment; filename=content_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        },
    )


@router.get("/template/download")
async def download_template():
    """
    下載批量導入 CSV 模板

    模板包含以下字段：
    - name: 商品名稱（必填）
    - brand: 品牌
    - features: 特點（逗號分隔多個）
    - target_audience: 目標受眾
    - price: 價格
    - category: 分類
    """
    output = io.StringIO()
    writer = csv.writer(output)

    # 寫入表頭
    writer.writerow([
        "name",
        "brand",
        "features",
        "target_audience",
        "price",
        "category",
    ])

    # 寫入示例數據
    writer.writerow([
        "日本A5和牛西冷 200g",
        "GogoJap",
        "日本鹿兒島產,A5等級,油花均勻,入口即化",
        "注重品質的美食愛好者",
        "388",
        "和牛",
    ])
    writer.writerow([
        "北海道帶子刺身 500g",
        "GogoJap",
        "北海道產,刺身級,鮮甜爽口",
        "海鮮愛好者",
        "268",
        "海鮮",
    ])

    output.seek(0)

    # 添加 BOM
    bom = '\ufeff'
    csv_content = bom + output.getvalue()

    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": "attachment; filename=batch_import_template.csv"
        },
    )
