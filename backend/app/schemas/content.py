# =============================================
# AI 內容 Schemas
# =============================================

from datetime import datetime
from typing import Optional, List, Any
from uuid import UUID
from pydantic import BaseModel, Field


# =============================================
# 內容生成請求
# =============================================

class ProductInfo(BaseModel):
    """商品資訊（用於生成文案）"""
    name: str = Field(..., min_length=1)
    brand: Optional[str] = None
    features: List[str] = Field(default=[])
    target_audience: Optional[str] = None
    price: Optional[str] = None
    category: Optional[str] = None


class ContentGenerateRequest(BaseModel):
    """生成文案請求"""
    product_id: Optional[UUID] = None
    product_info: Optional[ProductInfo] = None
    content_type: str = Field(default="full_copy", description="title, description, selling_points, full_copy")
    style: str = Field(default="professional", description="formal, casual, playful, professional")
    language: str = Field(default="zh-HK", description="zh-HK, zh-TW, en (deprecated, use target_languages)")
    target_languages: List[str] = Field(default=["TC"], description="目標語言: TC, SC, EN")


class BatchGenerateItem(BaseModel):
    """批量生成單項"""
    product_id: Optional[UUID] = Field(default=None, description="從商品庫選擇時使用")
    product_info: Optional[ProductInfo] = Field(default=None, description="手動輸入/CSV導入時使用")


class ContentBatchGenerateRequest(BaseModel):
    """批量生成文案請求（新版）"""
    items: List[BatchGenerateItem] = Field(..., min_length=1, max_length=100, description="批量生成項目列表")
    content_type: str = Field(default="full_copy", description="title, description, selling_points, full_copy")
    style: str = Field(default="professional", description="formal, casual, playful, professional")
    target_languages: List[str] = Field(default=["TC"], description="目標語言: TC, SC, EN")


# =============================================
# 內容響應
# =============================================

class LanguageContent(BaseModel):
    """單語言內容"""
    title: Optional[str] = None
    selling_points: Optional[List[str]] = None
    description: Optional[str] = None
    short_description: Optional[str] = None


class GeneratedContent(BaseModel):
    """生成的內容"""
    title: Optional[str] = None
    selling_points: Optional[List[str]] = None
    description: Optional[str] = None
    short_description: Optional[str] = None
    hashtags: Optional[List[str]] = None
    multilang: Optional[dict] = Field(default=None, description="多語言內容 {TC: {...}, SC: {...}, EN: {...}}")


class ContentGenerateResponse(BaseModel):
    """生成文案響應"""
    id: UUID
    content_type: str
    content: GeneratedContent
    metadata: dict = Field(default={})


class ContentResponse(BaseModel):
    """內容響應"""
    id: UUID
    product_id: Optional[UUID] = None
    product_name: Optional[str] = None
    content_type: str
    style: Optional[str] = None
    language: str
    content: str
    content_json: Optional[dict] = None
    version: int
    status: str
    generated_at: datetime
    approved_at: Optional[datetime] = None
    approved_by: Optional[str] = None

    model_config = {"from_attributes": True}


class ContentListResponse(BaseModel):
    """內容列表響應"""
    data: List[ContentResponse]
    total: int


class ContentApproveResponse(BaseModel):
    """審批響應"""
    id: UUID
    status: str
    approved_at: datetime


class BatchTaskResponse(BaseModel):
    """批量任務響應（舊版，保留兼容）"""
    task_id: str
    message: str
    product_count: int


# =============================================
# 批量生成響應（新版）
# =============================================

class BatchResultItem(BaseModel):
    """批量生成單項結果"""
    index: int = Field(..., description="在請求列表中的索引")
    success: bool
    content_id: Optional[UUID] = Field(default=None, description="生成成功時的內容ID")
    product_name: str
    content: Optional[GeneratedContent] = Field(default=None, description="生成成功時的內容")
    error: Optional[str] = Field(default=None, description="生成失敗時的錯誤信息")


class BatchSummary(BaseModel):
    """批量生成摘要"""
    total: int
    success: int
    failed: int


class BatchGenerateSyncResponse(BaseModel):
    """批量生成同步響應（≤10個）"""
    mode: str = Field(default="sync", description="處理模式: sync")
    results: List[BatchResultItem]
    summary: BatchSummary


class BatchGenerateAsyncResponse(BaseModel):
    """批量生成異步響應（>10個）"""
    mode: str = Field(default="async", description="處理模式: async")
    task_id: str
    total: int
    message: str = Field(default="批量任務已提交，請通過任務ID查詢進度")


class BatchProgress(BaseModel):
    """批量任務進度"""
    total: int
    completed: int
    failed: int
    percent: int


class BatchTaskStatusResponse(BaseModel):
    """批量任務狀態響應"""
    task_id: str
    status: str = Field(..., description="pending / processing / completed / failed")
    progress: BatchProgress
    results: List[BatchResultItem] = Field(default=[], description="已完成的結果")


# =============================================
# 文案優化請求/響應
# =============================================

class ChatMessage(BaseModel):
    """對話消息"""
    role: str = Field(..., description="user 或 assistant")
    content: str


class ContentOptimizeRequest(BaseModel):
    """文案優化請求"""
    instruction: str = Field(..., min_length=1, description="優化指令")
    context: List[ChatMessage] = Field(default=[], description="對話歷史")
    target_languages: List[str] = Field(default=["TC"], description="目標語言: TC, SC, EN")
    product_info: Optional[ProductInfo] = None


class ContentOptimizeResponse(BaseModel):
    """文案優化響應"""
    content_id: UUID
    content: GeneratedContent
    suggestions: List[str] = Field(default=[], description="後續優化建議")
    version: int
    metadata: dict = Field(default={})


class QuickSuggestion(BaseModel):
    """快捷優化建議"""
    key: str
    label: str
    instruction: str


class QuickSuggestionsResponse(BaseModel):
    """快捷建議列表響應"""
    suggestions: List[QuickSuggestion]
