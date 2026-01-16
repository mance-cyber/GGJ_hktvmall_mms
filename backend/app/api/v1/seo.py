# =============================================
# SEO 優化 API
# =============================================

from typing import Optional, List, Union
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import get_db
from app.models.seo import SEOContent, KeywordResearch
from app.schemas.seo import (
    # SEO 請求
    SEOGenerateRequest,
    SEOBatchGenerateRequest,
    KeywordExtractRequest,
    SEOAnalyzeRequest,
    ContentAuditRequest,
    # SEO 響應
    SEOContentResponse,
    SEOContentData,
    SEOScoreBreakdown,
    SEOScoreResponse,
    SEOBatchSyncResponse,
    SEOBatchAsyncResponse,
    SEOBatchResultItem,
    SEOBatchTaskStatusResponse,
    SEOBatchProgress,
    # 關鍵詞
    KeywordExtractionResponse,
    KeywordSuggestionsResponse,
    KeywordData,
    KeywordResearchResponse,
    # 審計
    ContentAuditResponse,
)
from app.services.seo_service import SEOService


router = APIRouter()


# =============================================
# SEO 內容生成
# =============================================

@router.post("/generate", response_model=SEOContentResponse)
async def generate_seo_content(
    request: SEOGenerateRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    生成 SEO 優化內容

    為產品生成 SEO 標題、描述、關鍵詞等優化內容。
    """
    seo_service = await SEOService.create(db)

    # 構建產品信息
    product_info = None
    if request.product_info:
        product_info = request.product_info.model_dump()

    result = await seo_service.generate_seo_content(
        product_id=request.product_id,
        product_info=product_info,
        target_keywords=request.target_keywords,
        target_languages=request.target_languages,
        include_og=request.include_og,
    )

    if not result.success:
        raise HTTPException(status_code=400, detail=result.error)

    await db.commit()

    return SEOContentResponse(
        id=result.content_id,
        product_id=request.product_id,
        content=SEOContentData(
            meta_title=result.meta_title,
            meta_description=result.meta_description,
            primary_keyword=result.primary_keyword,
            secondary_keywords=result.secondary_keywords or [],
            long_tail_keywords=result.long_tail_keywords or [],
            og_title=result.og_title,
            og_description=result.og_description,
            seo_score=result.seo_score,
            score_breakdown=SEOScoreBreakdown(**result.score_breakdown) if result.score_breakdown else None,
            improvement_suggestions=result.improvement_suggestions or [],
            localized=result.localized_seo,
        ),
        language=request.target_languages[0] if request.target_languages else "zh-HK",
        version=1,
        status="draft",
        generation_metadata={},
        created_at=datetime.utcnow(),
    )


@router.post("/batch-generate", response_model=Union[SEOBatchSyncResponse, SEOBatchAsyncResponse])
async def batch_generate_seo(
    request: SEOBatchGenerateRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    批量生成 SEO 內容

    - 10 個或以下：同步處理，直接返回結果
    - 10 個以上：異步處理，返回任務 ID
    """
    seo_service = await SEOService.create(db)
    items_count = len(request.items)

    # 同步模式（≤10 個）
    if items_count <= 10:
        results = []
        success_count = 0
        failed_count = 0

        for i, item in enumerate(request.items):
            product_info = item.product_info.model_dump() if item.product_info else None

            result = await seo_service.generate_seo_content(
                product_id=item.product_id,
                product_info=product_info,
                target_keywords=item.target_keywords,
                target_languages=request.target_languages,
                include_og=request.include_og,
            )

            if result.success:
                success_count += 1
                results.append(SEOBatchResultItem(
                    index=i,
                    success=True,
                    product_name=product_info.get("name", "") if product_info else "",
                    content_id=result.content_id,
                    content=SEOContentData(
                        meta_title=result.meta_title,
                        meta_description=result.meta_description,
                        primary_keyword=result.primary_keyword,
                        secondary_keywords=result.secondary_keywords or [],
                        long_tail_keywords=result.long_tail_keywords or [],
                        seo_score=result.seo_score,
                    ),
                ))
            else:
                failed_count += 1
                results.append(SEOBatchResultItem(
                    index=i,
                    success=False,
                    product_name=product_info.get("name", "") if product_info else "",
                    error=result.error,
                ))

        await db.commit()

        return SEOBatchSyncResponse(
            mode="sync",
            results=results,
            summary={
                "total": items_count,
                "success": success_count,
                "failed": failed_count,
            },
        )

    # 異步模式（>10 個）
    # TODO: 實現異步任務處理
    import uuid as uuid_module
    task_id = str(uuid_module.uuid4())

    return SEOBatchAsyncResponse(
        mode="async",
        task_id=task_id,
        total=items_count,
        message="批量 SEO 任務已提交，請通過任務 ID 查詢進度",
    )


@router.get("/batch-generate/{task_id}/status", response_model=SEOBatchTaskStatusResponse)
async def get_batch_seo_status(
    task_id: str,
    db: AsyncSession = Depends(get_db),
):
    """查詢批量 SEO 任務狀態"""
    # TODO: 實現任務狀態查詢
    return SEOBatchTaskStatusResponse(
        task_id=task_id,
        status="pending",
        progress=SEOBatchProgress(
            total=0,
            completed=0,
            failed=0,
            percent=0,
        ),
        results=[],
    )


# =============================================
# SEO 評分與分析
# =============================================

@router.get("/{product_id}/score", response_model=SEOScoreResponse)
async def get_seo_score(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """獲取產品的 SEO 評分"""
    seo_service = await SEOService.create(db)
    score_data = await seo_service.get_seo_score(product_id)

    if not score_data:
        raise HTTPException(status_code=404, detail="未找到該產品的 SEO 評分，請先生成 SEO 內容")

    return SEOScoreResponse(
        product_id=score_data["product_id"],
        seo_score=score_data["seo_score"],
        score_breakdown=SEOScoreBreakdown(**score_data["score_breakdown"]),
        improvement_suggestions=score_data["improvement_suggestions"],
        analyzed_at=score_data["analyzed_at"],
    )


@router.post("/analyze", response_model=ContentAuditResponse)
async def analyze_seo(
    request: ContentAuditRequest,
    db: AsyncSession = Depends(get_db),
):
    """分析內容的 SEO 狀況"""
    seo_service = await SEOService.create(db)

    result = await seo_service.audit_content(
        product_id=request.product_id,
        title=request.title,
        description=request.description,
        keywords=request.keywords,
        audit_type=request.audit_type,
    )

    await db.commit()

    return ContentAuditResponse(
        id=result["id"],
        product_id=result["product_id"],
        audit_type=result["audit_type"],
        overall_score=result["overall_score"],
        scores=result["scores"],
        issues=result["issues"],
        recommendations=result["recommendations"],
        audited_at=result["audited_at"],
    )


# =============================================
# 關鍵詞
# =============================================

@router.post("/keywords/extract", response_model=KeywordExtractionResponse)
async def extract_keywords(
    request: KeywordExtractRequest,
    db: AsyncSession = Depends(get_db),
):
    """從產品信息提取 SEO 關鍵詞"""
    seo_service = await SEOService.create(db)

    product_info = None
    if request.product_info:
        product_info = request.product_info.model_dump()

    result = await seo_service.extract_keywords(
        product_id=request.product_id,
        product_info=product_info,
        max_keywords=request.max_keywords,
        include_long_tail=request.include_long_tail,
    )

    if result.get("error"):
        raise HTTPException(status_code=400, detail=result["error"])

    return KeywordExtractionResponse(
        primary_keyword=result.get("primary_keyword", ""),
        secondary_keywords=result.get("secondary_keywords", []),
        long_tail_keywords=result.get("long_tail_keywords", []),
        all_keywords=[
            KeywordData(
                keyword=kw.get("keyword", kw) if isinstance(kw, dict) else kw,
                intent=kw.get("intent") if isinstance(kw, dict) else None,
            )
            for kw in result.get("keyword_analysis", result.get("keywords", []))
        ],
    )


@router.get("/keywords/suggestions", response_model=KeywordSuggestionsResponse)
async def get_keyword_suggestions(
    query: str = Query(..., min_length=1, description="搜索關鍵詞"),
    category: Optional[str] = Query(None, description="分類過濾"),
    limit: int = Query(10, ge=1, le=50, description="返回數量"),
    db: AsyncSession = Depends(get_db),
):
    """獲取關鍵詞建議"""
    seo_service = await SEOService.create(db)

    result = await seo_service.get_keyword_suggestions(
        query=query,
        category=category,
        limit=limit,
    )

    return KeywordSuggestionsResponse(
        query=query,
        suggestions=[
            KeywordData(
                keyword=kw.get("keyword", ""),
                search_volume=kw.get("search_volume"),
                difficulty=kw.get("difficulty"),
                intent=kw.get("intent"),
            )
            for kw in result.get("suggestions", [])
        ],
        related_categories=[],
    )


# =============================================
# SEO 內容管理
# =============================================

@router.get("/{content_id}", response_model=SEOContentResponse)
async def get_seo_content(
    content_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """獲取 SEO 內容詳情"""
    seo_service = await SEOService.create(db)
    content = await seo_service.get_seo_content(content_id)

    if not content:
        raise HTTPException(status_code=404, detail="SEO 內容不存在")

    return SEOContentResponse(
        id=content.id,
        product_id=content.product_id,
        content=SEOContentData(
            meta_title=content.meta_title,
            meta_description=content.meta_description,
            primary_keyword=content.primary_keyword,
            secondary_keywords=content.secondary_keywords or [],
            long_tail_keywords=content.long_tail_keywords or [],
            og_title=content.og_title,
            og_description=content.og_description,
            seo_score=content.seo_score,
            score_breakdown=SEOScoreBreakdown(**content.score_breakdown) if content.score_breakdown else None,
            improvement_suggestions=content.improvement_suggestions or [],
            localized=content.localized_seo,
        ),
        language=content.language,
        version=content.version,
        status=content.status,
        generation_metadata=content.generation_metadata,
        created_at=content.created_at,
    )


@router.get("/", response_model=dict)
async def list_seo_contents(
    product_id: Optional[UUID] = Query(None, description="按產品過濾"),
    status: Optional[str] = Query(None, description="按狀態過濾"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """列出 SEO 內容"""
    seo_service = await SEOService.create(db)

    result = await seo_service.list_seo_contents(
        product_id=product_id,
        status=status,
        limit=limit,
        offset=offset,
    )

    return {
        "data": [
            {
                "id": c.id,
                "product_id": c.product_id,
                "meta_title": c.meta_title,
                "meta_description": c.meta_description,
                "seo_score": c.seo_score,
                "status": c.status,
                "created_at": c.created_at,
            }
            for c in result["data"]
        ],
        "total": result["total"],
    }


@router.patch("/{content_id}/approve")
async def approve_seo_content(
    content_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """審批 SEO 內容"""
    seo_service = await SEOService.create(db)
    content = await seo_service.get_seo_content(content_id)

    if not content:
        raise HTTPException(status_code=404, detail="SEO 內容不存在")

    content.status = "approved"
    content.approved_at = datetime.utcnow()
    await db.commit()

    return {
        "id": content.id,
        "status": content.status,
        "approved_at": content.approved_at,
    }
