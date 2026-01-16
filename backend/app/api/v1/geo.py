# =============================================
# GEO 結構化數據 API
# =============================================

from typing import Optional, List
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import get_db
from app.models.seo import StructuredData, BrandKnowledge
from app.schemas.seo import (
    # GEO 請求
    ProductSchemaRequest,
    FAQSchemaRequest,
    BreadcrumbSchemaRequest,
    BatchSchemaRequest,
    AISummaryRequest,
    SchemaValidationRequest,
    # GEO 響應
    StructuredDataResponse,
    BatchSchemaResponse,
    SchemaValidationResponse,
    AISummaryResponse,
    # 品牌知識
    BrandKnowledgeCreate,
    BrandKnowledgeUpdate,
    BrandKnowledgeResponse,
    BrandKnowledgeListResponse,
    ExpertContentRequest,
)
from app.services.geo_service import GEOService


router = APIRouter()


# =============================================
# Schema.org 結構化數據生成
# =============================================

@router.post("/schema/product", response_model=StructuredDataResponse)
async def generate_product_schema(
    request: ProductSchemaRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    生成 Product Schema.org JSON-LD

    為產品生成符合 Google Rich Results 標準的結構化數據。
    """
    geo_service = await GEOService.create(db)

    product_info = None
    if request.product_info:
        product_info = request.product_info.model_dump()

    result = await geo_service.generate_product_schema(
        product_id=request.product_id,
        product_info=product_info,
        include_reviews=request.include_reviews,
        include_offers=request.include_offers,
    )

    if not result.success:
        raise HTTPException(status_code=400, detail=result.error)

    await db.commit()

    return StructuredDataResponse(
        id=result.schema_id,
        product_id=request.product_id,
        schema_type=result.schema_type,
        json_ld=result.json_ld,
        ai_summary=result.ai_summary,
        ai_facts=result.ai_facts or [],
        is_valid=result.is_valid,
        validation_errors=result.validation_errors or [],
        created_at=datetime.utcnow(),
    )


@router.post("/schema/faq", response_model=StructuredDataResponse)
async def generate_faq_schema(
    request: FAQSchemaRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    生成 FAQ Schema.org JSON-LD

    為產品生成常見問題結構化數據，提升搜索結果展示效果。
    如果不提供 FAQ 列表，將使用 AI 自動生成。
    """
    geo_service = await GEOService.create(db)

    result = await geo_service.generate_faq_schema(
        product_id=request.product_id,
        faqs=request.faqs,
        max_faqs=request.max_faqs,
    )

    if not result.success:
        raise HTTPException(status_code=400, detail=result.error)

    await db.commit()

    return StructuredDataResponse(
        id=result.schema_id,
        product_id=request.product_id,
        schema_type=result.schema_type,
        json_ld=result.json_ld,
        is_valid=result.is_valid,
        validation_errors=result.validation_errors or [],
        created_at=datetime.utcnow(),
    )


@router.post("/schema/breadcrumb", response_model=StructuredDataResponse)
async def generate_breadcrumb_schema(
    request: BreadcrumbSchemaRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    生成 BreadcrumbList Schema.org JSON-LD

    為產品頁面生成麵包屑導航結構化數據。
    """
    geo_service = await GEOService.create(db)

    result = await geo_service.generate_breadcrumb_schema(
        product_id=request.product_id,
        breadcrumb_path=request.breadcrumb_path,
    )

    if not result.success:
        raise HTTPException(status_code=400, detail=result.error)

    await db.commit()

    return StructuredDataResponse(
        id=result.schema_id,
        product_id=request.product_id,
        schema_type=result.schema_type,
        json_ld=result.json_ld,
        is_valid=result.is_valid,
        validation_errors=result.validation_errors or [],
        created_at=datetime.utcnow(),
    )


@router.post("/schema/batch", response_model=BatchSchemaResponse)
async def batch_generate_schemas(
    request: BatchSchemaRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    批量生成結構化數據

    為多個產品批量生成指定類型的 Schema.org 數據。
    """
    geo_service = await GEOService.create(db)
    results = []

    for product_id in request.product_ids:
        for schema_type in request.schema_types:
            if schema_type == "Product":
                result = await geo_service.generate_product_schema(product_id=product_id)
            elif schema_type == "FAQPage":
                result = await geo_service.generate_faq_schema(product_id=product_id)
            elif schema_type == "BreadcrumbList":
                result = await geo_service.generate_breadcrumb_schema(product_id=product_id)
            else:
                continue

            if result.success:
                results.append(StructuredDataResponse(
                    id=result.schema_id,
                    product_id=product_id,
                    schema_type=result.schema_type,
                    json_ld=result.json_ld,
                    ai_summary=result.ai_summary,
                    ai_facts=result.ai_facts or [],
                    is_valid=result.is_valid,
                    validation_errors=result.validation_errors or [],
                    created_at=datetime.utcnow(),
                ))

    await db.commit()

    return BatchSchemaResponse(
        results=results,
        summary={
            "total_products": len(request.product_ids),
            "total_schemas": len(results),
            "schema_types": request.schema_types,
        },
    )


# =============================================
# AI 搜索引擎優化
# =============================================

@router.post("/ai-summary", response_model=AISummaryResponse)
async def generate_ai_summary(
    request: AISummaryRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    生成 AI 搜索引擎友好摘要

    為產品生成適合 ChatGPT、Perplexity、Google AI Overview 等
    AI 搜索引擎引用的結構化摘要。
    """
    geo_service = await GEOService.create(db)

    product_info = None
    if request.product_info:
        product_info = request.product_info.model_dump()

    result = await geo_service.generate_ai_summary(
        product_id=request.product_id,
        product_info=product_info,
        max_facts=request.max_facts,
    )

    if result.get("error"):
        raise HTTPException(status_code=400, detail=result["error"])

    return AISummaryResponse(
        product_id=request.product_id,
        summary=result.get("summary", ""),
        facts=result.get("facts", []),
        entities=result.get("entities", {}),
    )


# =============================================
# Schema 驗證
# =============================================

@router.post("/validate", response_model=SchemaValidationResponse)
async def validate_schema(
    request: SchemaValidationRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    驗證 Schema.org JSON-LD 數據

    檢查結構化數據是否符合 Schema.org 規範。
    """
    geo_service = await GEOService.create(db)
    result = geo_service.validate_schema(request.json_ld)

    return SchemaValidationResponse(
        is_valid=result["is_valid"],
        errors=result["errors"],
        warnings=result["warnings"],
        suggestions=result["suggestions"],
    )


# =============================================
# 結構化數據管理
# =============================================

@router.get("/schema/{data_id}", response_model=StructuredDataResponse)
async def get_structured_data(
    data_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """獲取結構化數據詳情"""
    geo_service = await GEOService.create(db)
    data = await geo_service.get_structured_data(data_id)

    if not data:
        raise HTTPException(status_code=404, detail="結構化數據不存在")

    return StructuredDataResponse(
        id=data.id,
        product_id=data.product_id,
        schema_type=data.schema_type,
        json_ld=data.json_ld,
        ai_summary=data.ai_summary,
        ai_facts=data.ai_facts or [],
        is_valid=data.is_valid,
        validation_errors=data.validation_errors or [],
        created_at=data.created_at,
    )


@router.get("/schema", response_model=dict)
async def list_structured_data(
    product_id: Optional[UUID] = Query(None, description="按產品過濾"),
    schema_type: Optional[str] = Query(None, description="按類型過濾"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """列出結構化數據"""
    geo_service = await GEOService.create(db)

    result = await geo_service.list_structured_data(
        product_id=product_id,
        schema_type=schema_type,
        limit=limit,
        offset=offset,
    )

    return {
        "data": [
            {
                "id": d.id,
                "product_id": d.product_id,
                "schema_type": d.schema_type,
                "is_valid": d.is_valid,
                "created_at": d.created_at,
            }
            for d in result["data"]
        ],
        "total": result["total"],
    }


# =============================================
# 品牌知識圖譜
# =============================================

@router.post("/knowledge", response_model=BrandKnowledgeResponse)
async def create_brand_knowledge(
    request: BrandKnowledgeCreate,
    db: AsyncSession = Depends(get_db),
):
    """創建品牌知識條目"""
    geo_service = await GEOService.create(db)

    knowledge = await geo_service.create_brand_knowledge(
        knowledge_type=request.knowledge_type,
        title=request.title,
        content=request.content,
        summary=request.summary,
        related_products=request.related_products,
        related_categories=request.related_categories,
        source_type=request.source_type,
        source_reference=request.source_reference,
        author=request.author,
        tags=request.tags,
    )

    await db.commit()

    return BrandKnowledgeResponse(
        id=knowledge.id,
        knowledge_type=knowledge.knowledge_type,
        title=knowledge.title,
        content=knowledge.content,
        summary=knowledge.summary,
        related_products=[UUID(p) for p in (knowledge.related_products or [])],
        related_categories=knowledge.related_categories or [],
        credibility_score=knowledge.credibility_score,
        source_type=knowledge.source_type,
        source_reference=knowledge.source_reference,
        author=knowledge.author,
        tags=knowledge.tags or [],
        is_active=knowledge.is_active,
        is_featured=knowledge.is_featured,
        created_at=knowledge.created_at,
        updated_at=knowledge.updated_at,
    )


@router.get("/knowledge/search", response_model=BrandKnowledgeListResponse)
async def search_brand_knowledge(
    query: str = Query(..., min_length=1, description="搜索關鍵詞"),
    knowledge_type: Optional[str] = Query(None, description="知識類型過濾"),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """搜索品牌知識"""
    geo_service = await GEOService.create(db)

    knowledge_list = await geo_service.search_brand_knowledge(
        query=query,
        knowledge_type=knowledge_type,
        limit=limit,
    )

    return BrandKnowledgeListResponse(
        data=[
            BrandKnowledgeResponse(
                id=k.id,
                knowledge_type=k.knowledge_type,
                title=k.title,
                content=k.content,
                summary=k.summary,
                related_products=[UUID(p) for p in (k.related_products or [])],
                related_categories=k.related_categories or [],
                credibility_score=k.credibility_score,
                source_type=k.source_type,
                source_reference=k.source_reference,
                author=k.author,
                tags=k.tags or [],
                is_active=k.is_active,
                is_featured=k.is_featured,
                created_at=k.created_at,
                updated_at=k.updated_at,
            )
            for k in knowledge_list
        ],
        total=len(knowledge_list),
    )


@router.get("/knowledge/product/{product_id}", response_model=BrandKnowledgeListResponse)
async def get_product_knowledge(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """獲取產品相關的品牌知識"""
    geo_service = await GEOService.create(db)

    knowledge_list = await geo_service.get_product_knowledge(product_id)

    return BrandKnowledgeListResponse(
        data=[
            BrandKnowledgeResponse(
                id=k.id,
                knowledge_type=k.knowledge_type,
                title=k.title,
                content=k.content,
                summary=k.summary,
                related_products=[UUID(p) for p in (k.related_products or [])],
                related_categories=k.related_categories or [],
                credibility_score=k.credibility_score,
                source_type=k.source_type,
                source_reference=k.source_reference,
                author=k.author,
                tags=k.tags or [],
                is_active=k.is_active,
                is_featured=k.is_featured,
                created_at=k.created_at,
                updated_at=k.updated_at,
            )
            for k in knowledge_list
        ],
        total=len(knowledge_list),
    )


@router.post("/knowledge/generate-expert", response_model=BrandKnowledgeResponse)
async def generate_expert_content(
    request: ExpertContentRequest,
    db: AsyncSession = Depends(get_db),
):
    """AI 生成專家級內容"""
    geo_service = await GEOService.create(db)

    try:
        knowledge = await geo_service.generate_expert_content(
            topic=request.topic,
            product_id=request.product_id,
            knowledge_type=request.knowledge_type,
            tone=request.tone,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    await db.commit()

    return BrandKnowledgeResponse(
        id=knowledge.id,
        knowledge_type=knowledge.knowledge_type,
        title=knowledge.title,
        content=knowledge.content,
        summary=knowledge.summary,
        related_products=[UUID(p) for p in (knowledge.related_products or [])],
        related_categories=knowledge.related_categories or [],
        credibility_score=knowledge.credibility_score,
        source_type=knowledge.source_type,
        source_reference=knowledge.source_reference,
        author=knowledge.author,
        tags=knowledge.tags or [],
        is_active=knowledge.is_active,
        is_featured=knowledge.is_featured,
        created_at=knowledge.created_at,
        updated_at=knowledge.updated_at,
    )


@router.get("/knowledge/{knowledge_id}", response_model=BrandKnowledgeResponse)
async def get_brand_knowledge(
    knowledge_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """獲取品牌知識詳情"""
    knowledge = await db.get(BrandKnowledge, knowledge_id)

    if not knowledge:
        raise HTTPException(status_code=404, detail="品牌知識不存在")

    return BrandKnowledgeResponse(
        id=knowledge.id,
        knowledge_type=knowledge.knowledge_type,
        title=knowledge.title,
        content=knowledge.content,
        summary=knowledge.summary,
        related_products=[UUID(p) for p in (knowledge.related_products or [])],
        related_categories=knowledge.related_categories or [],
        credibility_score=knowledge.credibility_score,
        source_type=knowledge.source_type,
        source_reference=knowledge.source_reference,
        author=knowledge.author,
        tags=knowledge.tags or [],
        is_active=knowledge.is_active,
        is_featured=knowledge.is_featured,
        created_at=knowledge.created_at,
        updated_at=knowledge.updated_at,
    )
