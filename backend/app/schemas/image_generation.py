# =============================================
# 圖片生成 Schema
# =============================================

from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from app.models.image_generation import GenerationMode, TaskStatus


# ==================== 請求 Schema ====================

class ImageGenerationCreate(BaseModel):
    """創建圖片生成任務"""
    mode: GenerationMode = Field(..., description="生成模式：white_bg_topview 或 professional_photo")
    style_description: Optional[str] = Field(None, description="風格描述（可選）")


class ImageUploadResponse(BaseModel):
    """圖片上傳響應"""
    id: UUID
    file_name: str
    file_size: int
    upload_order: int


# ==================== 響應 Schema ====================

class InputImageResponse(BaseModel):
    """輸入圖片響應"""
    id: UUID
    file_name: str
    file_size: int
    upload_order: int
    analysis_result: Optional[dict] = None
    created_at: datetime

    class Config:
        from_attributes = True


class OutputImageResponse(BaseModel):
    """輸出圖片響應"""
    id: UUID
    file_name: str
    file_path: str
    file_size: Optional[int] = None
    prompt_used: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ImageGenerationTaskResponse(BaseModel):
    """圖片生成任務響應"""
    id: UUID
    mode: GenerationMode
    style_description: Optional[str] = None
    status: TaskStatus
    progress: int = 0
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    input_images: List[InputImageResponse] = []
    output_images: List[OutputImageResponse] = []

    class Config:
        from_attributes = True


class ImageGenerationTaskList(BaseModel):
    """圖片生成任務列表響應"""
    tasks: List[ImageGenerationTaskResponse]
    total: int
    page: int
    page_size: int


# ==================== 狀態更新 ====================

class TaskStatusResponse(BaseModel):
    """任務狀態響應（用於輪詢）"""
    id: UUID
    status: TaskStatus
    progress: int
    error_message: Optional[str] = None
    output_images: List[OutputImageResponse] = []

    class Config:
        from_attributes = True
