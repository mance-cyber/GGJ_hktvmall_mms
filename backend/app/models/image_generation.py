# =============================================
# 圖片生成數據庫模型
# =============================================

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON, Integer, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from enum import Enum
from .database import Base, utcnow


class GenerationMode(str, Enum):
    """生成模式"""
    WHITE_BG_TOPVIEW = "white_bg_topview"  # 白底 TopView 正面圖
    PROFESSIONAL_PHOTO = "professional_photo"  # 專業美食攝影圖


class TaskStatus(str, Enum):
    """任務狀態"""
    PENDING = "pending"  # 等待處理
    ANALYZING = "analyzing"  # AI 分析圖片中（第一階段）
    PROCESSING = "processing"  # 生成圖片中（第二階段）
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"  # 失敗


class ImageGenerationTask(Base):
    """圖片生成任務"""
    __tablename__ = "image_generation_tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # 用戶信息
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))

    # 任務配置
    mode = Column(SQLEnum(GenerationMode), nullable=False)
    style_description = Column(Text, nullable=True)  # 用戶輸入的風格描述
    outputs_per_image = Column(Integer, default=1)  # 每張輸入圖片生成的輸出數量（1-5）

    # 任務狀態
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.PENDING)
    progress = Column(Integer, default=0)  # 進度 0-100
    error_message = Column(Text, nullable=True)

    # Celery 任務 ID
    celery_task_id = Column(String(255), nullable=True)

    # 時間戳
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # 關聯
    input_images = relationship(
        "InputImage",
        back_populates="task",
        cascade="all, delete-orphan",
        order_by="InputImage.upload_order"
    )
    output_images = relationship(
        "OutputImage",
        back_populates="task",
        cascade="all, delete-orphan",
        order_by="OutputImage.created_at"
    )
    user = relationship("User", foreign_keys=[user_id])


class InputImage(Base):
    """輸入圖片"""
    __tablename__ = "input_images"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(UUID(as_uuid=True), ForeignKey("image_generation_tasks.id", ondelete="CASCADE"))

    # 圖片信息
    file_path = Column(String(500), nullable=False)  # 本地或 R2 存儲路徑
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)  # bytes
    mime_type = Column(String(50), nullable=False)

    # 上傳順序（1-5）
    upload_order = Column(Integer, nullable=False)

    # Google Vision AI 分析結果
    analysis_result = Column(JSON, nullable=True)

    # 時間戳
    created_at = Column(DateTime(timezone=True), default=utcnow)

    # 關聯
    task = relationship("ImageGenerationTask", back_populates="input_images")


class OutputImage(Base):
    """輸出圖片"""
    __tablename__ = "output_images"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(UUID(as_uuid=True), ForeignKey("image_generation_tasks.id", ondelete="CASCADE"))

    # 圖片信息
    file_path = Column(String(500), nullable=False)  # 本地或 R2 存儲路徑
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=True)  # bytes
    mime_type = Column(String(50), default="image/png")

    # 生成信息
    prompt_used = Column(Text, nullable=True)  # 實際使用的 prompt
    generation_params = Column(JSON, nullable=True)  # 生成參數

    # 時間戳
    created_at = Column(DateTime(timezone=True), default=utcnow)

    # 關聯
    task = relationship("ImageGenerationTask", back_populates="output_images")
