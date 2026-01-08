# =============================================
# AI 設定與分析 API
# 支持中轉站 (自定義 Base URL)
# =============================================

from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.models.database import get_db
from app.services.ai_service import (
    AISettingsService,
    AVAILABLE_MODELS,
    get_ai_analysis_service,
)

router = APIRouter()


# =============================================
# Pydantic Schemas
# =============================================

class AIConfigResponse(BaseModel):
    """AI 配置響應"""
    api_key_set: bool  # 不返回實際 key，只返回是否已設定
    api_key_preview: str  # 顯示前幾位 + ***
    base_url: str
    insights_model: str
    strategy_model: str


class AIConfigUpdate(BaseModel):
    """更新 AI 配置"""
    api_key: Optional[str] = Field(None, description="API Key")
    base_url: Optional[str] = Field(None, description="API Base URL（中轉站地址）")
    insights_model: Optional[str] = Field(None, description="數據摘要使用的模型")
    strategy_model: Optional[str] = Field(None, description="策略生成使用的模型")


class TestConnectionRequest(BaseModel):
    """測試連接請求"""
    api_key: str
    base_url: str
    model: str = "gpt-3.5-turbo"


class FetchModelsRequest(BaseModel):
    """獲取模型列表請求"""
    api_key: Optional[str] = None  # 可選，不提供則使用已保存的 Key
    base_url: Optional[str] = None  # 可選，不提供則使用已保存的 URL
    use_saved: bool = False  # 是否使用已保存的配置


class AIModel(BaseModel):
    """模型資訊"""
    id: str
    name: str
    description: str


class GenerateInsightsRequest(BaseModel):
    """生成數據摘要請求"""
    data: Dict[str, Any] = Field(..., description="要分析的數據")


class GenerateStrategyRequest(BaseModel):
    """生成策略請求"""
    insights: str = Field(..., description="數據摘要內容")
    context: Dict[str, Any] = Field(default_factory=dict, description="業務背景")


class AIAnalysisResponse(BaseModel):
    """AI 分析響應"""
    success: bool
    content: str
    model: str
    tokens_used: int
    error: Optional[str] = None


# =============================================
# 設定 API
# =============================================

@router.get("/config", response_model=AIConfigResponse)
async def get_ai_config(db: AsyncSession = Depends(get_db)):
    """
    獲取當前 AI 配置
    
    注意：API Key 不會完整返回，只顯示是否已設定
    """
    config = await AISettingsService.get_config(db)

    # 處理 API Key 預覽
    api_key_preview = ""
    if config.api_key:
        if len(config.api_key) > 10:
            api_key_preview = config.api_key[:8] + "..." + config.api_key[-4:]
        else:
            api_key_preview = "***"

    return AIConfigResponse(
        api_key_set=bool(config.api_key),
        api_key_preview=api_key_preview,
        base_url=config.base_url,
        insights_model=config.insights_model,
        strategy_model=config.strategy_model,
    )


@router.put("/config", response_model=AIConfigResponse)
async def update_ai_config(
    update: AIConfigUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    更新 AI 配置
    
    可以單獨更新任意欄位：
    - api_key: API Key
    - base_url: API Base URL（中轉站地址）
    - insights_model: 數據摘要使用的模型
    - strategy_model: 策略生成使用的模型
    """
    config = await AISettingsService.save_config(
        db=db,
        api_key=update.api_key,
        base_url=update.base_url,
        insights_model=update.insights_model,
        strategy_model=update.strategy_model,
    )

    api_key_preview = ""
    if config.api_key:
        if len(config.api_key) > 10:
            api_key_preview = config.api_key[:8] + "..." + config.api_key[-4:]
        else:
            api_key_preview = "***"

    return AIConfigResponse(
        api_key_set=bool(config.api_key),
        api_key_preview=api_key_preview,
        base_url=config.base_url,
        insights_model=config.insights_model,
        strategy_model=config.strategy_model,
    )


@router.post("/test-connection")
async def test_connection(request: TestConnectionRequest):
    """
    測試 API 連接是否有效

    會實際調用 API 進行測試
    """
    result = await AISettingsService.test_connection(
        api_key=request.api_key,
        base_url=request.base_url,
        model=request.model
    )
    return result


@router.post("/fetch-models")
async def fetch_models_from_api(
    request: FetchModelsRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    從 API 動態獲取可用模型列表

    調用中轉站的 /models 端點獲取實際可用的模型

    可以：
    - 提供 api_key 和 base_url 使用新的配置
    - 設置 use_saved=true 使用已保存的配置
    """
    api_key = request.api_key
    base_url = request.base_url

    # 如果使用已保存的配置
    if request.use_saved or (not api_key and not base_url):
        config = await AISettingsService.get_config(db)
        if not config.api_key:
            return {
                "success": False,
                "models": [],
                "error": "尚未設定 API Key，請先在上方設定"
            }
        api_key = config.api_key
        base_url = base_url or config.base_url

    if not api_key:
        return {
            "success": False,
            "models": [],
            "error": "請提供 API Key"
        }
    if not base_url:
        return {
            "success": False,
            "models": [],
            "error": "請提供 Base URL"
        }

    result = await AISettingsService.fetch_models_from_api(
        api_key=api_key,
        base_url=base_url
    )
    return result


@router.get("/models", response_model=List[AIModel])
async def get_available_models():
    """
    獲取預設的模型列表

    返回常用模型列表，用於 API 不支持 /models 端點時的備選
    """
    models = AISettingsService.get_available_models()
    return [AIModel(**m) for m in models]


# =============================================
# 分析 API
# =============================================

@router.post("/generate-insights", response_model=AIAnalysisResponse)
async def generate_data_insights(
    request: GenerateInsightsRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    生成數據摘要
    
    AI #1: 分析數據 → 出數據摘要
    """
    service = await get_ai_analysis_service(db)
    result = service.generate_data_insights(request.data)

    return AIAnalysisResponse(
        success=result.success,
        content=result.content,
        model=result.model,
        tokens_used=result.tokens_used,
        error=result.error,
    )


@router.post("/generate-strategy", response_model=AIAnalysisResponse)
async def generate_marketing_strategy(
    request: GenerateStrategyRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    生成 Marketing 策略建議
    
    AI #2: 讀取摘要 → 出 Marketing 策略建議
    """
    service = await get_ai_analysis_service(db)
    result = service.generate_marketing_strategy(request.insights, request.context)

    return AIAnalysisResponse(
        success=result.success,
        content=result.content,
        model=result.model,
        tokens_used=result.tokens_used,
        error=result.error,
    )


@router.post("/analyze-full")
async def full_analysis_pipeline(
    data: Dict[str, Any] = Body(..., description="要分析的數據"),
    context: Dict[str, Any] = Body(default_factory=dict, description="業務背景"),
    db: AsyncSession = Depends(get_db)
):
    """
    完整分析流程（兩個 AI 串聯）
    
    一鍵執行：
    1. AI #1 分析數據 → 生成數據摘要
    2. AI #2 基於摘要 → 生成 Marketing 策略
    
    返回兩個 AI 的輸出結果
    """
    service = await get_ai_analysis_service(db)

    # Step 1: 數據摘要
    insights_result = service.generate_data_insights(data)

    if not insights_result.success:
        return {
            "success": False,
            "stage": "insights",
            "error": insights_result.error,
            "insights": None,
            "strategy": None,
        }

    # Step 2: Marketing 策略
    strategy_result = service.generate_marketing_strategy(
        insights=insights_result.content,
        context=context
    )

    return {
        "success": strategy_result.success,
        "insights": {
            "content": insights_result.content,
            "model": insights_result.model,
            "tokens_used": insights_result.tokens_used,
        },
        "strategy": {
            "content": strategy_result.content if strategy_result.success else None,
            "model": strategy_result.model,
            "tokens_used": strategy_result.tokens_used,
            "error": strategy_result.error,
        },
        "total_tokens": insights_result.tokens_used + strategy_result.tokens_used,
    }
