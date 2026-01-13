# =============================================
# 圖片生成 API 路由
# =============================================

import logging
import uuid
from pathlib import Path
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.database import get_db
from app.models.image_generation import (
    ImageGenerationTask,
    InputImage,
    OutputImage,
    GenerationMode,
    TaskStatus
)
from app.schemas.image_generation import (
    ImageGenerationCreate,
    ImageGenerationTaskResponse,
    ImageUploadResponse,
    TaskStatusResponse,
    ImageGenerationTaskList
)
from app.models.user import User
from app.api.deps import get_current_user
from app.config import get_settings
from app.tasks.image_generation_tasks import process_image_generation
from app.services.storage_service import get_storage
from sqlalchemy import select, func

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter(tags=["image-generation"])


@router.post("/tasks", response_model=ImageGenerationTaskResponse)
async def create_image_generation_task(
    task_data: ImageGenerationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    創建圖片生成任務

    - **mode**: 生成模式（white_bg_topview 或 professional_photo）
    - **style_description**: 風格描述（可選）
    """
    # 創建任務
    task = ImageGenerationTask(
        user_id=current_user.id,
        mode=task_data.mode,
        style_description=task_data.style_description,
        outputs_per_image=task_data.outputs_per_image,
        status=TaskStatus.PENDING,
        progress=0
    )

    db.add(task)
    await db.commit()
    await db.refresh(task)

    # 重新查詢並預加載關係（避免 MissingGreenlet 錯誤）
    result = await db.execute(
        select(ImageGenerationTask)
        .options(
            selectinload(ImageGenerationTask.input_images),
            selectinload(ImageGenerationTask.output_images)
        )
        .where(ImageGenerationTask.id == task.id)
    )
    task = result.scalar_one()

    logger.info(f"Created image generation task {task.id} for user {current_user.id}")

    return task


@router.post("/tasks/{task_id}/upload", response_model=List[ImageUploadResponse])
async def upload_input_images(
    task_id: uuid.UUID,
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    上傳輸入圖片（最多 5 張）

    - 支持格式：JPG, PNG, WEBP
    - 單張圖片最大 10MB
    - 最多上傳 5 張圖片
    """
    # 驗證任務存在且屬於當前用戶
    result = await db.execute(
        select(ImageGenerationTask).where(
            ImageGenerationTask.id == task_id,
            ImageGenerationTask.user_id == current_user.id
        )
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # 驗證圖片數量
    if len(files) > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 5 images allowed"
        )

    # 驗證圖片格式和大小
    allowed_types = {"image/jpeg", "image/png", "image/webp"}
    max_size = 10 * 1024 * 1024  # 10MB

    uploaded_images = []

    for idx, file in enumerate(files):
        # 檢查 MIME 類型
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File {file.filename}: Invalid format. Allowed: JPG, PNG, WEBP"
            )

        # 讀取文件內容
        content = await file.read()

        # 檢查文件大小
        if len(content) > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File {file.filename}: Size exceeds 10MB"
            )

        # 生成安全的文件名
        file_ext = Path(file.filename).suffix
        safe_filename = f"{uuid.uuid4()}{file_ext}"

        # 使用 StorageService 保存文件
        storage = get_storage()
        relative_path = f"input/{str(task_id)}/{safe_filename}"
        file_url = storage.save_file(file_data=content, file_path=relative_path)

        # 創建數據庫記錄
        input_image = InputImage(
            task_id=task_id,
            file_path=file_url,  # 使用 StorageService 返回的 URL/路徑
            file_name=safe_filename,
            file_size=len(content),
            mime_type=file.content_type,
            upload_order=idx + 1
        )

        db.add(input_image)
        uploaded_images.append(input_image)

    await db.commit()

    # 刷新數據
    for img in uploaded_images:
        await db.refresh(img)

    logger.info(f"Uploaded {len(uploaded_images)} images for task {task_id}")

    return uploaded_images


@router.post("/tasks/{task_id}/start", response_model=ImageGenerationTaskResponse)
async def start_image_generation(
    task_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    開始圖片生成（調度 Celery 任務）
    """
    # 驗證任務存在且屬於當前用戶
    result = await db.execute(
        select(ImageGenerationTask).where(
            ImageGenerationTask.id == task_id,
            ImageGenerationTask.user_id == current_user.id
        )
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # 驗證任務狀態
    if task.status != TaskStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Task is already {task.status.value}"
        )

    # 驗證是否有上傳的圖片
    input_count_result = await db.execute(
        select(func.count()).select_from(InputImage).where(
            InputImage.task_id == task_id
        )
    )
    input_count = input_count_result.scalar()

    if input_count == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No input images uploaded"
        )

    # 調度 Celery 任務
    celery_task = process_image_generation.delay(str(task_id))

    # 更新任務狀態
    task.celery_task_id = celery_task.id
    task.status = TaskStatus.PROCESSING
    await db.commit()

    # 重新查詢並預加載關係（避免 MissingGreenlet 錯誤）
    result = await db.execute(
        select(ImageGenerationTask)
        .options(
            selectinload(ImageGenerationTask.input_images),
            selectinload(ImageGenerationTask.output_images)
        )
        .where(ImageGenerationTask.id == task_id)
    )
    task = result.scalar_one()

    logger.info(f"Started image generation for task {task_id}, Celery task {celery_task.id}")

    return task


@router.get("/tasks/{task_id}", response_model=ImageGenerationTaskResponse)
async def get_task_status(
    task_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    獲取任務狀態（包含輸入/輸出圖片）
    """
    result = await db.execute(
        select(ImageGenerationTask)
        .options(
            selectinload(ImageGenerationTask.input_images),
            selectinload(ImageGenerationTask.output_images)
        )
        .where(
            ImageGenerationTask.id == task_id,
            ImageGenerationTask.user_id == current_user.id
        )
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return task


@router.get("/tasks", response_model=ImageGenerationTaskList)
async def list_tasks(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    列出當前用戶的圖片生成任務
    """
    # 計算總數
    count_result = await db.execute(
        select(func.count()).select_from(ImageGenerationTask).where(
            ImageGenerationTask.user_id == current_user.id
        )
    )
    total = count_result.scalar()

    # 獲取分頁數據
    offset = (page - 1) * page_size

    result = await db.execute(
        select(ImageGenerationTask)
        .options(
            selectinload(ImageGenerationTask.input_images),
            selectinload(ImageGenerationTask.output_images)
        )
        .where(ImageGenerationTask.user_id == current_user.id)
        .order_by(ImageGenerationTask.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    tasks = result.scalars().all()

    return ImageGenerationTaskList(
        tasks=tasks,
        total=total,
        page=page,
        page_size=page_size
    )


@router.delete("/tasks/{task_id}")
async def delete_task(
    task_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    刪除單個圖片生成任務（包括關聯的圖片文件）
    """
    # 驗證任務存在且屬於當前用戶
    result = await db.execute(
        select(ImageGenerationTask)
        .options(
            selectinload(ImageGenerationTask.input_images),
            selectinload(ImageGenerationTask.output_images)
        )
        .where(
            ImageGenerationTask.id == task_id,
            ImageGenerationTask.user_id == current_user.id
        )
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # 刪除關聯的存儲文件
    storage = get_storage()

    # 刪除輸入圖片
    for img in task.input_images:
        try:
            if img.file_path:
                _delete_storage_file(storage, img.file_path)
        except Exception as e:
            logger.warning(f"Failed to delete input image {img.file_path}: {e}")

    # 刪除輸出圖片
    for img in task.output_images:
        try:
            if img.file_path:
                _delete_storage_file(storage, img.file_path)
        except Exception as e:
            logger.warning(f"Failed to delete output image {img.file_path}: {e}")

    # 刪除數據庫記錄（級聯刪除會處理關聯的圖片記錄）
    await db.delete(task)
    await db.commit()

    logger.info(f"Deleted task {task_id} for user {current_user.id}")

    return {"message": "Task deleted successfully", "task_id": str(task_id)}


@router.delete("/tasks/batch")
async def delete_tasks_batch(
    task_ids: List[uuid.UUID],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    批量刪除圖片生成任務

    Args:
        task_ids: 要刪除的任務 ID 列表
    """
    if not task_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No task IDs provided"
        )

    if len(task_ids) > 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 50 tasks can be deleted at once"
        )

    # 獲取所有要刪除的任務
    result = await db.execute(
        select(ImageGenerationTask)
        .options(
            selectinload(ImageGenerationTask.input_images),
            selectinload(ImageGenerationTask.output_images)
        )
        .where(
            ImageGenerationTask.id.in_(task_ids),
            ImageGenerationTask.user_id == current_user.id
        )
    )
    tasks = result.scalars().all()

    if not tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No tasks found"
        )

    storage = get_storage()
    deleted_count = 0

    for task in tasks:
        # 刪除關聯的存儲文件
        for img in task.input_images:
            try:
                if img.file_path:
                    _delete_storage_file(storage, img.file_path)
            except Exception as e:
                logger.warning(f"Failed to delete input image {img.file_path}: {e}")

        for img in task.output_images:
            try:
                if img.file_path:
                    _delete_storage_file(storage, img.file_path)
            except Exception as e:
                logger.warning(f"Failed to delete output image {img.file_path}: {e}")

        await db.delete(task)
        deleted_count += 1

    await db.commit()

    logger.info(f"Batch deleted {deleted_count} tasks for user {current_user.id}")

    return {
        "message": f"Successfully deleted {deleted_count} tasks",
        "deleted_count": deleted_count,
        "requested_count": len(task_ids)
    }


def _delete_storage_file(storage, file_path: str):
    """
    刪除存儲文件的輔助函數
    """
    if file_path.startswith('http'):
        # R2 URL，提取相對路徑
        if storage.public_url_base and storage.public_url_base in file_path:
            relative_path = file_path.replace(f"{storage.public_url_base}/", "")
            storage.delete_file(relative_path)
    else:
        # 本地路徑
        storage.delete_file(file_path)


@router.get("/presigned-url")
async def get_presigned_url(
    file_url: str,
    expires_in: int = 3600,
    current_user: User = Depends(get_current_user)
):
    """
    獲取 R2 文件的預簽名 URL

    預簽名 URL 可以繞過 CORS 限制，直接在瀏覽器中訪問。

    Args:
        file_url: R2 文件的公開 URL 或相對路徑
        expires_in: URL 過期時間（秒），默認 1 小時，最大 24 小時

    Returns:
        預簽名 URL
    """
    # 限制過期時間最大為 24 小時
    expires_in = min(expires_in, 86400)

    storage = get_storage()
    presigned_url = storage.get_presigned_url(file_url, expires_in)

    return {
        "presigned_url": presigned_url,
        "expires_in": expires_in,
        "original_url": file_url
    }


@router.get("/download")
async def download_file(
    file_url: str,
    current_user: User = Depends(get_current_user)
):
    """
    通過後端代理下載 R2 文件（繞過 CORS）

    Args:
        file_url: R2 文件的公開 URL 或相對路徑

    Returns:
        文件流響應
    """
    from fastapi.responses import StreamingResponse
    import io

    storage = get_storage()

    try:
        # 從 URL 提取 R2 Key
        r2_key = file_url
        if file_url.startswith('http'):
            if storage.public_url_base in file_url:
                r2_key = file_url.replace(f"{storage.public_url_base}/", "")
            else:
                from urllib.parse import urlparse
                parsed = urlparse(file_url)
                r2_key = parsed.path.lstrip('/')

        logger.info(f"Downloading file from R2: {r2_key}")

        # 從 R2 獲取文件
        response = storage.s3_client.get_object(
            Bucket=storage.bucket,
            Key=r2_key
        )

        # 獲取文件名
        file_name = r2_key.split('/')[-1]

        # 獲取 Content-Type
        content_type = response.get('ContentType', 'application/octet-stream')

        # 返回流式響應
        return StreamingResponse(
            io.BytesIO(response['Body'].read()),
            media_type=content_type,
            headers={
                "Content-Disposition": f'attachment; filename="{file_name}"',
                "Access-Control-Expose-Headers": "Content-Disposition"
            }
        )

    except Exception as e:
        logger.error(f"Failed to download file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"下載失敗: {str(e)}"
        )
