# =============================================
# 統一內容生成流水線 API
# =============================================

from typing import Optional, List, Set
from uuid import UUID
from enum import Enum

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import get_db
from app.services.content_pipeline import (
    ContentPipelineService,
    PipelineStage,
    PipelineResult,
    BatchPipelineResult,
    get_content_pipeline_service,
)

router = APIRouter()


# =============================================
# 請求/響應模型
# =============================================

class ProductInfoInput(BaseModel):
    """產品信息輸入"""
    name: str = Field(..., description="產品名稱")
    brand: str = Field(default="GoGoJap", description="品牌")
    category: Optional[str] = Field(default=None, description="分類")
    description: Optional[str] = Field(default=None, description="原有描述")
    features: Optional[List[str]] = Field(default=None, description="產品特點")
    price: Optional[float] = Field(default=None, description="價格")
    origin: Optional[str] = Field(default=None, description="產地")


class PipelineStageEnum(str, Enum):
    """可選階段"""
    content = "content"   # 內容生成（包含文案 + SEO）
    geo = "geo"           # GEO 結構化數據


class PipelineRequest(BaseModel):
    """流水線請求"""
    product_id: Optional[UUID] = Field(default=None, description="產品 ID（從數據庫獲取）")
    product_info: Optional[ProductInfoInput] = Field(default=None, description="產品信息（手動輸入）")
    stages: Optional[List[PipelineStageEnum]] = Field(
        default=None,
        description="要執行的階段，默認全部 [content, geo]"
    )
    language: str = Field(default="zh-HK", description="目標語言")
    tone: str = Field(default="professional", description="文案語氣: professional/casual/luxury")
    include_faq: bool = Field(default=False, description="是否生成 FAQ Schema")
    save_to_db: bool = Field(default=True, description="是否保存到數據庫")


class ContentResultResponse(BaseModel):
    """內容生成結果（文案 + SEO 合併）"""
    # 文案部分
    title: str
    selling_points: List[str]
    description: str
    tone: str

    # SEO 部分
    meta_title: str
    meta_description: str
    primary_keyword: str
    secondary_keywords: List[str]
    long_tail_keywords: List[str]
    seo_score: int
    score_breakdown: dict
    og_title: str
    og_description: str


class GEOResultResponse(BaseModel):
    """GEO 結果"""
    product_schema: dict
    faq_schema: Optional[dict] = None
    breadcrumb_schema: Optional[dict] = None
    ai_summary: str
    ai_facts: List[str]


class PipelineResponse(BaseModel):
    """流水線響應"""
    success: bool
    product_info: dict

    # 各階段結果（content 已包含 SEO）
    content: Optional[ContentResultResponse] = None
    geo: Optional[GEOResultResponse] = None

    # 執行信息
    stages_executed: List[str]
    content_id: Optional[str] = None
    seo_content_id: Optional[str] = None
    structured_data_id: Optional[str] = None

    # 元數據
    generation_time_ms: int
    model_used: str
    error: Optional[str] = None


# =============================================
# API 端點
# =============================================

@router.post("/generate", response_model=PipelineResponse)
async def generate_content_pipeline(
    request: PipelineRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    統一內容生成流水線

    一次生成：
    - **文案** (content): 標題、賣點、描述、關鍵詞
    - **SEO** (seo): Meta 標籤、關鍵詞優化、評分
    - **GEO** (geo): Schema.org JSON-LD、AI 摘要

    各階段結果自動傳遞，減少重複輸入。
    """

    # 驗證輸入
    if not request.product_id and not request.product_info:
        raise HTTPException(
            status_code=400,
            detail="必須提供 product_id 或 product_info"
        )

    # 轉換階段
    stages: Optional[Set[PipelineStage]] = None
    if request.stages:
        stages = {PipelineStage(s.value) for s in request.stages}

    # 轉換產品信息
    product_info = None
    if request.product_info:
        product_info = request.product_info.model_dump()

    # 創建服務並執行
    service = await get_content_pipeline_service(db)
    result = await service.run(
        product_id=request.product_id,
        product_info=product_info,
        stages=stages,
        language=request.language,
        tone=request.tone,
        include_faq=request.include_faq,
        save_to_db=request.save_to_db,
    )

    # 轉換響應
    return _convert_to_response(result)


@router.post("/generate/content-only", response_model=PipelineResponse)
async def generate_content_only(
    request: PipelineRequest,
    db: AsyncSession = Depends(get_db),
):
    """只生成內容（文案 + SEO，不含 GEO 結構化數據）"""

    if not request.product_id and not request.product_info:
        raise HTTPException(status_code=400, detail="必須提供 product_id 或 product_info")

    product_info = request.product_info.model_dump() if request.product_info else None

    service = await get_content_pipeline_service(db)
    result = await service.run(
        product_id=request.product_id,
        product_info=product_info,
        stages={PipelineStage.CONTENT},
        language=request.language,
        tone=request.tone,
        save_to_db=request.save_to_db,
    )

    return _convert_to_response(result)


@router.post("/generate/geo-only", response_model=PipelineResponse)
async def generate_geo_only(
    request: PipelineRequest,
    db: AsyncSession = Depends(get_db),
):
    """只生成 GEO（結構化數據，不含內容生成）"""

    if not request.product_id and not request.product_info:
        raise HTTPException(status_code=400, detail="必須提供 product_id 或 product_info")

    product_info = request.product_info.model_dump() if request.product_info else None

    service = await get_content_pipeline_service(db)
    result = await service.run(
        product_id=request.product_id,
        product_info=product_info,
        stages={PipelineStage.GEO},
        include_faq=request.include_faq,
        save_to_db=request.save_to_db,
    )

    return _convert_to_response(result)


# =============================================
# 輔助函數
# =============================================

def _convert_to_response(result: PipelineResult) -> PipelineResponse:
    """轉換內部結果為 API 響應"""

    content_response = None
    if result.content:
        content_response = ContentResultResponse(
            # 文案部分
            title=result.content.title,
            selling_points=result.content.selling_points,
            description=result.content.description,
            tone=result.content.tone,
            # SEO 部分
            meta_title=result.content.meta_title,
            meta_description=result.content.meta_description,
            primary_keyword=result.content.primary_keyword,
            secondary_keywords=result.content.secondary_keywords,
            long_tail_keywords=result.content.long_tail_keywords,
            seo_score=result.content.seo_score,
            score_breakdown=result.content.score_breakdown,
            og_title=result.content.og_title,
            og_description=result.content.og_description,
        )

    geo_response = None
    if result.geo:
        geo_response = GEOResultResponse(
            product_schema=result.geo.product_schema,
            faq_schema=result.geo.faq_schema,
            breadcrumb_schema=result.geo.breadcrumb_schema,
            ai_summary=result.geo.ai_summary,
            ai_facts=result.geo.ai_facts,
        )

    return PipelineResponse(
        success=result.success,
        product_info=result.product_info,
        content=content_response,
        geo=geo_response,
        stages_executed=result.stages_executed,
        content_id=str(result.content_id) if result.content_id else None,
        seo_content_id=str(result.seo_content_id) if result.seo_content_id else None,
        structured_data_id=str(result.structured_data_id) if result.structured_data_id else None,
        generation_time_ms=result.generation_time_ms,
        model_used=result.model_used,
        error=result.error,
    )


# =============================================
# 批量生成 API
# =============================================

class BatchPipelineRequest(BaseModel):
    """批量流水線請求"""
    products: List[ProductInfoInput] = Field(
        ...,
        min_length=1,
        max_length=20,
        description="產品信息列表（最多 20 個）"
    )
    stages: Optional[List[PipelineStageEnum]] = Field(
        default=None,
        description="要執行的階段，默認全部"
    )
    language: str = Field(default="zh-HK", description="目標語言")
    tone: str = Field(default="professional", description="文案語氣")
    include_faq: bool = Field(default=False, description="是否生成 FAQ")
    save_to_db: bool = Field(default=True, description="是否保存到數據庫")


class BatchErrorItem(BaseModel):
    """批量錯誤項"""
    index: int
    product_name: str
    error: str


class BatchPipelineResponse(BaseModel):
    """批量流水線響應"""
    success: bool
    total_products: int
    successful_count: int
    failed_count: int
    results: List[PipelineResponse]
    errors: List[BatchErrorItem]
    total_time_ms: int
    stages_executed: List[str]


@router.post("/batch", response_model=BatchPipelineResponse)
async def batch_generate(
    request: BatchPipelineRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    批量生成內容流水線

    一次處理多個產品，最多 20 個。
    並發處理，提高效率。
    """

    if not request.products:
        raise HTTPException(status_code=400, detail="必須提供至少一個產品")

    # 轉換階段
    stages = None
    if request.stages:
        stages = {PipelineStage(s.value) for s in request.stages}

    # 轉換產品信息
    products = [p.model_dump() for p in request.products]

    # 執行批量生成
    service = await get_content_pipeline_service(db)
    batch_result = await service.run_batch(
        products=products,
        stages=stages,
        language=request.language,
        tone=request.tone,
        include_faq=request.include_faq,
        save_to_db=request.save_to_db,
    )

    # 轉換結果
    return BatchPipelineResponse(
        success=batch_result.success,
        total_products=batch_result.total_products,
        successful_count=batch_result.successful_count,
        failed_count=batch_result.failed_count,
        results=[_convert_to_response(r) for r in batch_result.results],
        errors=[
            BatchErrorItem(
                index=e["index"],
                product_name=e["product_name"],
                error=e["error"]
            )
            for e in batch_result.errors
        ],
        total_time_ms=batch_result.total_time_ms,
        stages_executed=batch_result.stages_executed,
    )
