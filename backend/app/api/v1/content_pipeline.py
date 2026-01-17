# =============================================
# 統一內容生成流水線 API
# =============================================

from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import get_db
from app.services.content_pipeline import (
    ContentPipelineService,
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


class PipelineRequest(BaseModel):
    """流水線請求"""
    product_id: Optional[UUID] = Field(default=None, description="產品 ID（從數據庫獲取）")
    product_info: Optional[ProductInfoInput] = Field(default=None, description="產品信息（手動輸入）")
    language: str = Field(default="zh-HK", description="目標語言")
    tone: str = Field(default="professional", description="文案語氣: professional/casual/luxury")
    include_faq: bool = Field(default=False, description="是否生成 FAQ Schema")
    save_to_db: bool = Field(default=True, description="是否保存到數據庫")


class PipelineResponse(BaseModel):
    """流水線響應（一次生成全部內容）"""
    success: bool
    product_info: dict

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

    # GEO 部分
    product_schema: dict
    faq_schema: Optional[dict] = None
    ai_summary: str
    ai_facts: List[str]

    # 存儲 ID
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

    一次 AI 調用生成完整內容包：
    - **文案**: 標題、賣點、描述
    - **SEO**: Meta 標籤、關鍵詞、評分
    - **GEO**: Schema.org JSON-LD、AI 摘要
    """

    # 驗證輸入
    if not request.product_id and not request.product_info:
        raise HTTPException(
            status_code=400,
            detail="必須提供 product_id 或 product_info"
        )

    # 轉換產品信息
    product_info = None
    if request.product_info:
        product_info = request.product_info.model_dump()

    # 創建服務並執行
    service = await get_content_pipeline_service(db)
    result = await service.run(
        product_id=request.product_id,
        product_info=product_info,
        language=request.language,
        tone=request.tone,
        include_faq=request.include_faq,
        save_to_db=request.save_to_db,
    )

    # 轉換響應
    return _convert_to_response(result)


# =============================================
# 輔助函數
# =============================================

def _convert_to_response(result: PipelineResult) -> PipelineResponse:
    """轉換內部結果為 API 響應"""

    return PipelineResponse(
        success=result.success,
        product_info=result.product_info,
        # 文案部分
        title=result.title,
        selling_points=result.selling_points,
        description=result.description,
        tone=result.tone,
        # SEO 部分
        meta_title=result.meta_title,
        meta_description=result.meta_description,
        primary_keyword=result.primary_keyword,
        secondary_keywords=result.secondary_keywords,
        long_tail_keywords=result.long_tail_keywords,
        seo_score=result.seo_score,
        score_breakdown=result.score_breakdown,
        og_title=result.og_title,
        og_description=result.og_description,
        # GEO 部分
        product_schema=result.product_schema,
        faq_schema=result.faq_schema,
        ai_summary=result.ai_summary,
        ai_facts=result.ai_facts,
        # 存儲 ID
        content_id=str(result.content_id) if result.content_id else None,
        seo_content_id=str(result.seo_content_id) if result.seo_content_id else None,
        structured_data_id=str(result.structured_data_id) if result.structured_data_id else None,
        # 元數據
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

    # 轉換產品信息
    products = [p.model_dump() for p in request.products]

    # 執行批量生成
    service = await get_content_pipeline_service(db)
    batch_result = await service.run_batch(
        products=products,
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
    )
