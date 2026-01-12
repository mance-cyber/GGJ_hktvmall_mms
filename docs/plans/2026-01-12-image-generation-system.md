# Image Generation System Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a complete img2img product image generation system using nano-banana (Gemini 2.5 Flash Image) API with async processing, two output modes (white background + professional photography), and user style customization.

**Architecture:** FastAPI backend with Celery async task queue, PostgreSQL for task tracking, nano-banana API for image generation, Next.js frontend with drag-drop upload. User uploads 5 images → backend analyzes with Google Vision → generates prompts → calls nano-banana → saves results → frontend polls for completion.

**Tech Stack:** FastAPI, Celery, Redis, PostgreSQL, SQLAlchemy, nano-banana API, Next.js 14, TypeScript, TailwindCSS

---

## Current Status

**已完成：**
- ✅ API 配置（backend/app/config.py - lines 108-123）
- ✅ 資料庫模型（backend/app/models/image_generation.py）
- ✅ Pydantic Schema（backend/app/schemas/image_generation.py）
- ✅ nano-banana API 客戶端（backend/app/services/nano_banana_client.py）

**待完成：**
- ⏳ 資料庫遷移
- ⏳ Celery 任務處理器
- ⏳ 後端 API 路由
- ⏳ 前端頁面
- ⏳ 端到端測試

---

## Task 1: 資料庫遷移

**Files:**
- Modify: `backend/app/tasks/celery_app.py:17-20`
- Create: `backend/alembic/versions/YYYY_MM_DD_add_image_generation_tables.py`

### Step 1: 更新 Celery include 列表

在 `backend/app/tasks/celery_app.py` 添加新的任務模組：

**修改 line 17-20:**

```python
include=[
    "app.tasks.scrape_tasks",
    "app.tasks.content_tasks",
    "app.tasks.image_generation_tasks",  # 新增
]
```

### Step 2: 創建 Alembic 遷移

**Run:**
```bash
cd backend
python -m alembic revision --autogenerate -m "add image generation tables"
```

**Expected:** Creates new migration file in `backend/alembic/versions/`

### Step 3: 檢查生成的遷移文件

**Run:**
```bash
cat backend/alembic/versions/*_add_image_generation_tables.py
```

**Expected:** 應包含 `image_generation_tasks`, `input_images`, `output_images` 三個表的 CREATE 語句

### Step 4: 執行遷移

**Run:**
```bash
cd backend
python -m alembic upgrade head
```

**Expected:**
```
INFO [alembic.runtime.migration] Running upgrade ... -> ..., add image generation tables
```

### Step 5: 驗證表已創建

**Run:**
```bash
cd backend
python -c "from app.models import Base, get_db; from sqlalchemy import inspect; db = next(get_db()); inspector = inspect(db.bind); print('Tables:', inspector.get_table_names())"
```

**Expected:** 輸出應包含 `image_generation_tasks`, `input_images`, `output_images`

### Step 6: Commit

```bash
git add backend/app/tasks/celery_app.py backend/alembic/versions/*_add_image_generation_tables.py
git commit -m "feat(db): add image generation tables migration"
```

---

## Task 2: Celery 圖片生成任務

**Files:**
- Create: `backend/app/tasks/image_generation_tasks.py`
- Create: `backend/tests/test_image_generation_tasks.py`

### Step 1: 創建測試文件骨架

在 `backend/tests/test_image_generation_tasks.py` 寫入：

```python
# =============================================
# 圖片生成任務測試
# =============================================

import pytest
from unittest.mock import patch, MagicMock
from uuid import uuid4
from app.tasks.image_generation_tasks import process_image_generation
from app.models.image_generation import TaskStatus


@pytest.mark.asyncio
async def test_process_white_bg_task_success(db_session):
    """測試白底圖生成任務成功"""
    # TODO: 實作測試
    pass


@pytest.mark.asyncio
async def test_process_professional_photo_task_success(db_session):
    """測試專業攝影圖生成任務成功"""
    # TODO: 實作測試
    pass


@pytest.mark.asyncio
async def test_process_task_api_failure(db_session):
    """測試 API 調用失敗情況"""
    # TODO: 實作測試
    pass
```

### Step 2: 創建 Celery 任務文件

在 `backend/app/tasks/image_generation_tasks.py` 寫入：

```python
# =============================================
# 圖片生成 Celery 任務
# =============================================

from celery import Task
from sqlalchemy.orm import Session
import logging
from pathlib import Path
from typing import List
from uuid import UUID

from app.tasks.celery_app import celery_app
from app.models.database import get_db
from app.models.image_generation import (
    ImageGenerationTask,
    InputImage,
    OutputImage,
    GenerationMode,
    TaskStatus
)
from app.services.nano_banana_client import NanoBananaClient

logger = logging.getLogger(__name__)


class ImageGenerationTask(Task):
    """圖片生成任務基類"""

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """任務失敗時的回調"""
        logger.error(f"Image generation task {task_id} failed: {exc}")
        # 更新資料庫狀態
        task_uuid = kwargs.get('task_id')
        if task_uuid:
            db = next(get_db())
            try:
                task = db.query(ImageGenerationTask).filter_by(id=task_uuid).first()
                if task:
                    task.status = TaskStatus.FAILED
                    task.error_message = str(exc)
                    task.progress = 0
                    db.commit()
            finally:
                db.close()


@celery_app.task(base=ImageGenerationTask, bind=True)
def process_image_generation(self, task_id: str):
    """
    處理圖片生成任務

    Args:
        task_id: ImageGenerationTask UUID
    """
    logger.info(f"Starting image generation task {task_id}")

    db = next(get_db())

    try:
        # 獲取任務
        task = db.query(ImageGenerationTask).filter_by(id=task_id).first()
        if not task:
            raise ValueError(f"Task {task_id} not found")

        # 更新狀態
        task.status = TaskStatus.PROCESSING
        task.progress = 10
        db.commit()

        # 獲取輸入圖片路徑
        input_image_paths = [
            img.file_path
            for img in sorted(task.input_images, key=lambda x: x.upload_order)
        ]

        logger.info(f"Processing {len(input_image_paths)} input images")
        task.progress = 20
        db.commit()

        # 初始化 API 客戶端
        client = NanoBananaClient()

        # 根據模式調用不同的生成方法
        if task.mode == GenerationMode.WHITE_BG_TOPVIEW:
            logger.info("Generating white background top-view image")
            task.progress = 30
            db.commit()

            # 調用白底圖生成
            api_response = await client.generate_white_bg_topview(
                input_images=input_image_paths,
                product_analysis=task.input_images[0].analysis_result if task.input_images else None
            )

        elif task.mode == GenerationMode.PROFESSIONAL_PHOTO:
            logger.info("Generating professional photography images")
            task.progress = 30
            db.commit()

            # 調用專業攝影圖生成
            api_response = await client.generate_professional_photos(
                input_images=input_image_paths,
                style_description=task.style_description,
                product_analysis=task.input_images[0].analysis_result if task.input_images else None
            )

        else:
            raise ValueError(f"Unknown generation mode: {task.mode}")

        task.progress = 70
        db.commit()

        # 保存生成的圖片
        output_dir = Path(f"storage/generated/{task_id}")
        output_paths = await client.save_generated_images(api_response, str(output_dir))

        logger.info(f"Saved {len(output_paths)} generated images")
        task.progress = 90
        db.commit()

        # 創建 OutputImage 記錄
        for idx, output_path in enumerate(output_paths):
            output_img = OutputImage(
                task_id=task.id,
                file_path=output_path,
                file_name=Path(output_path).name,
                file_size=Path(output_path).stat().st_size,
                mime_type="image/png",
                prompt_used=client._build_white_bg_prompt(None) if task.mode == GenerationMode.WHITE_BG_TOPVIEW else client._build_professional_photo_prompt(task.style_description, None)
            )
            db.add(output_img)

        # 完成任務
        task.status = TaskStatus.COMPLETED
        task.progress = 100
        from datetime import datetime
        task.completed_at = datetime.utcnow()
        db.commit()

        logger.info(f"Image generation task {task_id} completed successfully")
        return {"status": "success", "task_id": str(task_id), "output_count": len(output_paths)}

    except Exception as e:
        logger.error(f"Image generation task {task_id} failed: {str(e)}")
        task.status = TaskStatus.FAILED
        task.error_message = str(e)
        task.progress = 0
        db.commit()
        raise

    finally:
        db.close()
```

### Step 3: Run placeholder test

**Run:**
```bash
cd backend
pytest tests/test_image_generation_tasks.py -v
```

**Expected:** 3 tests PASS (因為是 pass)

### Step 4: 實作第一個實際測試

修改 `backend/tests/test_image_generation_tasks.py` 的第一個測試：

```python
@pytest.mark.asyncio
async def test_process_white_bg_task_success(db_session):
    """測試白底圖生成任務成功"""
    from app.models.image_generation import ImageGenerationTask, GenerationMode, TaskStatus
    from app.tasks.image_generation_tasks import process_image_generation

    # 創建測試任務
    task = ImageGenerationTask(
        user_id=uuid4(),
        mode=GenerationMode.WHITE_BG_TOPVIEW,
        status=TaskStatus.PENDING
    )
    db_session.add(task)
    db_session.commit()

    # Mock nano-banana client
    with patch('app.tasks.image_generation_tasks.NanoBananaClient') as mock_client:
        mock_instance = MagicMock()
        mock_instance.generate_white_bg_topview.return_value = {"data": [{"b64_json": "fake_base64"}]}
        mock_instance.save_generated_images.return_value = ["storage/generated/test.png"]
        mock_client.return_value = mock_instance

        # 執行任務
        result = process_image_generation.apply(args=[str(task.id)]).get()

    # 驗證
    db_session.refresh(task)
    assert task.status == TaskStatus.COMPLETED
    assert task.progress == 100
    assert result["status"] == "success"
```

### Step 5: Run test to verify it works

**Run:**
```bash
cd backend
pytest tests/test_image_generation_tasks.py::test_process_white_bg_task_success -v
```

**Expected:** PASS

### Step 6: Commit

```bash
git add backend/app/tasks/image_generation_tasks.py backend/tests/test_image_generation_tasks.py
git commit -m "feat(tasks): add image generation Celery task with tests"
```

---

## Task 3: 後端 API 路由

**Files:**
- Create: `backend/app/api/v1/image_generation.py`
- Modify: `backend/app/api/v1/router.py`
- Create: `backend/tests/test_api_image_generation.py`

### Step 1: 創建 API 測試骨架

在 `backend/tests/test_api_image_generation.py` 寫入：

```python
# =============================================
# 圖片生成 API 測試
# =============================================

import pytest
from fastapi.testclient import TestClient
from uuid import uuid4


def test_create_generation_task(client: TestClient, auth_headers):
    """測試創建生成任務"""
    # TODO: 實作
    pass


def test_upload_images(client: TestClient, auth_headers):
    """測試上傳圖片"""
    # TODO: 實作
    pass


def test_get_task_status(client: TestClient, auth_headers):
    """測試獲取任務狀態"""
    # TODO: 實作
    pass
```

### Step 2: 創建 API 路由文件

在 `backend/app/api/v1/image_generation.py` 寫入：

```python
# =============================================
# 圖片生成 API
# =============================================

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
import logging
from pathlib import Path
import shutil

from app.models.database import get_db
from app.models.user import User
from app.models.image_generation import (
    ImageGenerationTask,
    InputImage,
    GenerationMode,
    TaskStatus
)
from app.schemas.image_generation import (
    ImageGenerationCreate,
    ImageGenerationTaskResponse,
    TaskStatusResponse,
    ImageUploadResponse
)
from app.api.v1.auth import get_current_active_user
from app.tasks.image_generation_tasks import process_image_generation

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/image-generation", tags=["image-generation"])


@router.post("/tasks", response_model=ImageGenerationTaskResponse)
async def create_generation_task(
    task_data: ImageGenerationCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    創建圖片生成任務

    - **mode**: 生成模式 (white_bg_topview 或 professional_photo)
    - **style_description**: 風格描述（可選）
    """
    try:
        # 創建任務
        task = ImageGenerationTask(
            user_id=current_user.id,
            mode=task_data.mode,
            style_description=task_data.style_description,
            status=TaskStatus.PENDING
        )

        db.add(task)
        db.commit()
        db.refresh(task)

        logger.info(f"Created image generation task {task.id} for user {current_user.id}")

        return task

    except Exception as e:
        logger.error(f"Failed to create generation task: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tasks/{task_id}/upload", response_model=List[ImageUploadResponse])
async def upload_images(
    task_id: UUID,
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    上傳圖片到指定任務（最多 5 張）

    - **task_id**: 任務 ID
    - **files**: 圖片文件列表（最多 5 張）
    """
    try:
        # 獲取任務
        task = db.query(ImageGenerationTask).filter_by(
            id=task_id,
            user_id=current_user.id
        ).first()

        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        if task.status != TaskStatus.PENDING:
            raise HTTPException(status_code=400, detail="Task is not in pending state")

        if len(files) > 5:
            raise HTTPException(status_code=400, detail="Maximum 5 images allowed")

        # 創建上傳目錄
        upload_dir = Path(f"storage/uploads/{task_id}")
        upload_dir.mkdir(parents=True, exist_ok=True)

        uploaded_images = []

        for idx, file in enumerate(files):
            # 驗證文件類型
            if not file.content_type.startswith("image/"):
                raise HTTPException(status_code=400, detail=f"File {file.filename} is not an image")

            # 保存文件
            file_path = upload_dir / f"{idx + 1}_{file.filename}"
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            # 創建 InputImage 記錄
            input_img = InputImage(
                task_id=task.id,
                file_path=str(file_path),
                file_name=file.filename,
                file_size=file_path.stat().st_size,
                mime_type=file.content_type,
                upload_order=idx + 1
            )

            db.add(input_img)
            uploaded_images.append(input_img)

        db.commit()

        logger.info(f"Uploaded {len(files)} images for task {task_id}")

        return uploaded_images

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to upload images: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tasks/{task_id}/start")
async def start_generation(
    task_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    啟動圖片生成任務

    - **task_id**: 任務 ID
    """
    try:
        # 獲取任務
        task = db.query(ImageGenerationTask).filter_by(
            id=task_id,
            user_id=current_user.id
        ).first()

        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        if task.status != TaskStatus.PENDING:
            raise HTTPException(status_code=400, detail="Task is not in pending state")

        # 檢查是否有上傳圖片
        if not task.input_images:
            raise HTTPException(status_code=400, detail="No images uploaded")

        # 發送到 Celery 隊列
        celery_task = process_image_generation.delay(str(task_id))

        # 更新任務
        task.celery_task_id = celery_task.id
        db.commit()

        logger.info(f"Started generation task {task_id} (Celery task: {celery_task.id})")

        return {"message": "Generation started", "task_id": str(task_id), "celery_task_id": celery_task.id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start generation: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks/{task_id}/status", response_model=TaskStatusResponse)
async def get_task_status(
    task_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    獲取任務狀態（用於前端輪詢）

    - **task_id**: 任務 ID
    """
    try:
        task = db.query(ImageGenerationTask).filter_by(
            id=task_id,
            user_id=current_user.id
        ).first()

        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        return task

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get task status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks/{task_id}", response_model=ImageGenerationTaskResponse)
async def get_task(
    task_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    獲取任務詳情

    - **task_id**: 任務 ID
    """
    try:
        task = db.query(ImageGenerationTask).filter_by(
            id=task_id,
            user_id=current_user.id
        ).first()

        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        return task

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks/{task_id}/outputs/{image_id}")
async def download_output_image(
    task_id: UUID,
    image_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    下載生成的圖片

    - **task_id**: 任務 ID
    - **image_id**: 圖片 ID
    """
    try:
        from app.models.image_generation import OutputImage

        # 獲取任務
        task = db.query(ImageGenerationTask).filter_by(
            id=task_id,
            user_id=current_user.id
        ).first()

        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        # 獲取圖片
        output_img = db.query(OutputImage).filter_by(
            id=image_id,
            task_id=task_id
        ).first()

        if not output_img:
            raise HTTPException(status_code=404, detail="Image not found")

        # 返回文件
        file_path = Path(output_img.file_path)
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found on disk")

        return FileResponse(
            path=str(file_path),
            media_type=output_img.mime_type,
            filename=output_img.file_name
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to download output image: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

### Step 3: 註冊路由

修改 `backend/app/api/v1/router.py`，添加：

```python
from app.api.v1 import image_generation

# ... existing imports ...

api_router.include_router(image_generation.router)
```

### Step 4: Run basic test

**Run:**
```bash
cd backend
pytest tests/test_api_image_generation.py -v
```

**Expected:** 3 tests PASS (placeholder)

### Step 5: 實作實際測試

修改 `backend/tests/test_api_image_generation.py` 第一個測試：

```python
def test_create_generation_task(client: TestClient, auth_headers):
    """測試創建生成任務"""
    response = client.post(
        "/api/v1/image-generation/tasks",
        json={
            "mode": "white_bg_topview",
            "style_description": "Clean and minimal"
        },
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "white_bg_topview"
    assert data["status"] == "pending"
    assert "id" in data
```

### Step 6: Run test

**Run:**
```bash
cd backend
pytest tests/test_api_image_generation.py::test_create_generation_task -v
```

**Expected:** PASS

### Step 7: Commit

```bash
git add backend/app/api/v1/image_generation.py backend/app/api/v1/router.py backend/tests/test_api_image_generation.py
git commit -m "feat(api): add image generation endpoints"
```

---

## Task 4: 前端頁面 - 圖片上傳組件

**Files:**
- Create: `frontend/src/app/image-generator/page.tsx`
- Create: `frontend/src/components/image-generator/upload-zone.tsx`
- Create: `frontend/src/lib/api/image-generation.ts`

### Step 1: 創建 API 客戶端

在 `frontend/src/lib/api/image-generation.ts` 寫入：

```typescript
// =============================================
// 圖片生成 API 客戶端
// =============================================

import { apiClient } from './client'

export interface ImageGenerationTask {
  id: string
  mode: 'white_bg_topview' | 'professional_photo'
  style_description?: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  progress: number
  error_message?: string
  created_at: string
  updated_at: string
  completed_at?: string
  input_images: InputImage[]
  output_images: OutputImage[]
}

export interface InputImage {
  id: string
  file_name: string
  file_size: number
  upload_order: number
  created_at: string
}

export interface OutputImage {
  id: string
  file_name: string
  file_path: string
  file_size?: number
  created_at: string
}

export const imageGenerationApi = {
  /**
   * 創建生成任務
   */
  createTask: async (data: {
    mode: 'white_bg_topview' | 'professional_photo'
    style_description?: string
  }): Promise<ImageGenerationTask> => {
    const response = await apiClient.post('/image-generation/tasks', data)
    return response.data
  },

  /**
   * 上傳圖片
   */
  uploadImages: async (taskId: string, files: File[]): Promise<InputImage[]> => {
    const formData = new FormData()
    files.forEach((file) => {
      formData.append('files', file)
    })

    const response = await apiClient.post(
      `/image-generation/tasks/${taskId}/upload`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    )
    return response.data
  },

  /**
   * 啟動生成
   */
  startGeneration: async (taskId: string): Promise<void> => {
    await apiClient.post(`/image-generation/tasks/${taskId}/start`)
  },

  /**
   * 獲取任務狀態
   */
  getTaskStatus: async (taskId: string): Promise<ImageGenerationTask> => {
    const response = await apiClient.get(`/image-generation/tasks/${taskId}/status`)
    return response.data
  },

  /**
   * 獲取任務詳情
   */
  getTask: async (taskId: string): Promise<ImageGenerationTask> => {
    const response = await apiClient.get(`/image-generation/tasks/${taskId}`)
    return response.data
  },

  /**
   * 下載輸出圖片
   */
  downloadOutput: (taskId: string, imageId: string): string => {
    return `${process.env.NEXT_PUBLIC_API_URL}/api/v1/image-generation/tasks/${taskId}/outputs/${imageId}`
  },
}
```

### Step 2: 創建上傳區組件

在 `frontend/src/components/image-generator/upload-zone.tsx` 寫入：

```typescript
'use client'

import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, X, Image as ImageIcon } from 'lucide-react'

interface UploadZoneProps {
  onFilesSelected: (files: File[]) => void
  maxFiles?: number
}

export function UploadZone({ onFilesSelected, maxFiles = 5 }: UploadZoneProps) {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([])

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const newFiles = [...selectedFiles, ...acceptedFiles].slice(0, maxFiles)
    setSelectedFiles(newFiles)
    onFilesSelected(newFiles)
  }, [selectedFiles, maxFiles, onFilesSelected])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.webp']
    },
    maxFiles: maxFiles - selectedFiles.length,
    multiple: true
  })

  const removeFile = (index: number) => {
    const newFiles = selectedFiles.filter((_, i) => i !== index)
    setSelectedFiles(newFiles)
    onFilesSelected(newFiles)
  }

  return (
    <div className="space-y-4">
      {/* 拖放區域 */}
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-lg p-8 text-center cursor-pointer
          transition-colors duration-200
          ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-blue-400'}
          ${selectedFiles.length >= maxFiles ? 'opacity-50 cursor-not-allowed' : ''}
        `}
      >
        <input {...getInputProps()} disabled={selectedFiles.length >= maxFiles} />
        <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
        {isDragActive ? (
          <p className="text-blue-500">放開以上傳圖片...</p>
        ) : (
          <div>
            <p className="text-gray-700 mb-2">
              拖放圖片到此處，或點擊選擇文件
            </p>
            <p className="text-sm text-gray-500">
              最多 {maxFiles} 張圖片，支援 PNG、JPG、WEBP 格式
            </p>
            <p className="text-xs text-gray-400 mt-1">
              已選擇：{selectedFiles.length}/{maxFiles}
            </p>
          </div>
        )}
      </div>

      {/* 預覽區域 */}
      {selectedFiles.length > 0 && (
        <div className="grid grid-cols-5 gap-4">
          {selectedFiles.map((file, index) => (
            <div key={index} className="relative group">
              <div className="aspect-square rounded-lg overflow-hidden border-2 border-gray-200">
                <img
                  src={URL.createObjectURL(file)}
                  alt={`Preview ${index + 1}`}
                  className="w-full h-full object-cover"
                />
              </div>
              <button
                onClick={() => removeFile(index)}
                className="absolute top-1 right-1 p-1 bg-red-500 text-white rounded-full
                           opacity-0 group-hover:opacity-100 transition-opacity"
              >
                <X className="h-4 w-4" />
              </button>
              <p className="text-xs text-gray-600 mt-1 truncate">{file.name}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
```

### Step 3: 創建主頁面

在 `frontend/src/app/image-generator/page.tsx` 寫入：

```typescript
'use client'

import { useState } from 'react'
import { UploadZone } from '@/components/image-generator/upload-zone'
import { imageGenerationApi } from '@/lib/api/image-generation'
import { useToast } from '@/hooks/use-toast'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Textarea } from '@/components/ui/textarea'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'
import { Label } from '@/components/ui/label'

export default function ImageGeneratorPage() {
  const [files, setFiles] = useState<File[]>([])
  const [mode, setMode] = useState<'white_bg_topview' | 'professional_photo'>('white_bg_topview')
  const [styleDescription, setStyleDescription] = useState('')
  const [isUploading, setIsUploading] = useState(false)
  const { toast } = useToast()

  const handleGenerate = async () => {
    if (files.length === 0) {
      toast({
        title: '錯誤',
        description: '請至少上傳一張圖片',
        variant: 'destructive'
      })
      return
    }

    setIsUploading(true)

    try {
      // 1. 創建任務
      const task = await imageGenerationApi.createTask({
        mode,
        style_description: styleDescription || undefined
      })

      // 2. 上傳圖片
      await imageGenerationApi.uploadImages(task.id, files)

      // 3. 啟動生成
      await imageGenerationApi.startGeneration(task.id)

      toast({
        title: '成功',
        description: '圖片生成已啟動，請稍候...'
      })

      // TODO: 導航到結果頁面
      window.location.href = `/image-generator/${task.id}`

    } catch (error: any) {
      toast({
        title: '錯誤',
        description: error.message || '生成失敗',
        variant: 'destructive'
      })
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <div className="container mx-auto py-8 max-w-4xl">
      <Card>
        <CardHeader>
          <CardTitle>AI 產品圖片生成器</CardTitle>
          <CardDescription>
            上傳產品圖片，使用 AI 生成專業的白底圖或美食攝影圖
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* 模式選擇 */}
          <div>
            <Label className="text-base font-semibold mb-3 block">生成模式</Label>
            <RadioGroup value={mode} onValueChange={(v: any) => setMode(v)}>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="white_bg_topview" id="white-bg" />
                <Label htmlFor="white-bg" className="cursor-pointer">
                  白底 TopView 正面圖（適合電商平台）
                </Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="professional_photo" id="professional" />
                <Label htmlFor="professional" className="cursor-pointer">
                  專業美食攝影圖（2-3 張，適合行銷推廣）
                </Label>
              </div>
            </RadioGroup>
          </div>

          {/* 風格描述 */}
          {mode === 'professional_photo' && (
            <div>
              <Label htmlFor="style" className="text-base font-semibold mb-2 block">
                風格描述（可選）
              </Label>
              <Textarea
                id="style"
                placeholder="例如：清新自然、奢華高級、溫馨家居..."
                value={styleDescription}
                onChange={(e) => setStyleDescription(e.target.value)}
                rows={3}
              />
            </div>
          )}

          {/* 上傳區域 */}
          <div>
            <Label className="text-base font-semibold mb-3 block">上傳圖片</Label>
            <UploadZone onFilesSelected={setFiles} maxFiles={5} />
          </div>

          {/* 操作按鈕 */}
          <div className="flex justify-end">
            <Button
              onClick={handleGenerate}
              disabled={files.length === 0 || isUploading}
              size="lg"
            >
              {isUploading ? '處理中...' : '開始生成'}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
```

### Step 4: 安裝依賴

**Run:**
```bash
cd frontend
npm install react-dropzone
```

**Expected:** Package installed successfully

### Step 5: 測試頁面可訪問

**Run:**
```bash
cd frontend
npm run dev
```

**Expected:** Dev server starts on http://localhost:3000

打開瀏覽器訪問 `http://localhost:3000/image-generator`

**Expected:** 看到圖片生成器頁面，可以拖放上傳圖片

### Step 6: Commit

```bash
git add frontend/src/app/image-generator/page.tsx frontend/src/components/image-generator/upload-zone.tsx frontend/src/lib/api/image-generation.ts frontend/package.json
git commit -m "feat(frontend): add image generator upload page"
```

---

## Task 5: 前端頁面 - 結果展示

**Files:**
- Create: `frontend/src/app/image-generator/[taskId]/page.tsx`
- Create: `frontend/src/components/image-generator/result-gallery.tsx`

### Step 1: 創建結果畫廊組件

在 `frontend/src/components/image-generator/result-gallery.tsx` 寫入：

```typescript
'use client'

import { OutputImage } from '@/lib/api/image-generation'
import { Download } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface ResultGalleryProps {
  taskId: string
  images: OutputImage[]
}

export function ResultGallery({ taskId, images }: ResultGalleryProps) {
  const handleDownload = (imageId: string, fileName: string) => {
    const url = `${process.env.NEXT_PUBLIC_API_URL}/api/v1/image-generation/tasks/${taskId}/outputs/${imageId}`
    const a = document.createElement('a')
    a.href = url
    a.download = fileName
    a.click()
  }

  if (images.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        尚未生成圖片
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {images.map((image) => (
        <div key={image.id} className="group relative">
          <div className="aspect-square rounded-lg overflow-hidden border-2 border-gray-200">
            <img
              src={`${process.env.NEXT_PUBLIC_API_URL}/api/v1/image-generation/tasks/${taskId}/outputs/${image.id}`}
              alt={image.file_name}
              className="w-full h-full object-cover"
            />
          </div>
          <div className="mt-2 flex items-center justify-between">
            <p className="text-sm text-gray-600 truncate">{image.file_name}</p>
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleDownload(image.id, image.file_name)}
            >
              <Download className="h-4 w-4" />
            </Button>
          </div>
        </div>
      ))}
    </div>
  )
}
```

### Step 2: 創建結果頁面

在 `frontend/src/app/image-generator/[taskId]/page.tsx` 寫入：

```typescript
'use client'

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import { imageGenerationApi, ImageGenerationTask } from '@/lib/api/image-generation'
import { ResultGallery } from '@/components/image-generator/result-gallery'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Loader2, CheckCircle, XCircle } from 'lucide-react'

export default function TaskResultPage() {
  const params = useParams()
  const taskId = params.taskId as string

  const [task, setTask] = useState<ImageGenerationTask | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    if (!taskId) return

    const fetchTask = async () => {
      try {
        const data = await imageGenerationApi.getTask(taskId)
        setTask(data)
        setIsLoading(false)
      } catch (error) {
        console.error('Failed to fetch task:', error)
        setIsLoading(false)
      }
    }

    fetchTask()

    // 如果任務正在處理中，開始輪詢
    if (task?.status === 'processing' || task?.status === 'pending') {
      const interval = setInterval(async () => {
        try {
          const status = await imageGenerationApi.getTaskStatus(taskId)
          setTask(status)

          // 如果完成或失敗，停止輪詢
          if (status.status === 'completed' || status.status === 'failed') {
            clearInterval(interval)
          }
        } catch (error) {
          console.error('Failed to fetch status:', error)
        }
      }, 2000) // 每 2 秒輪詢一次

      return () => clearInterval(interval)
    }
  }, [taskId, task?.status])

  if (isLoading) {
    return (
      <div className="container mx-auto py-8 flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
      </div>
    )
  }

  if (!task) {
    return (
      <div className="container mx-auto py-8">
        <Alert variant="destructive">
          <XCircle className="h-4 w-4" />
          <AlertTitle>錯誤</AlertTitle>
          <AlertDescription>找不到該任務</AlertDescription>
        </Alert>
      </div>
    )
  }

  return (
    <div className="container mx-auto py-8 max-w-6xl space-y-6">
      {/* 狀態卡片 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            {task.status === 'completed' && <CheckCircle className="h-5 w-5 text-green-500" />}
            {task.status === 'processing' && <Loader2 className="h-5 w-5 animate-spin text-blue-500" />}
            {task.status === 'failed' && <XCircle className="h-5 w-5 text-red-500" />}
            任務狀態：{task.status === 'completed' ? '已完成' : task.status === 'processing' ? '處理中' : task.status === 'failed' ? '失敗' : '等待中'}
          </CardTitle>
          <CardDescription>
            模式：{task.mode === 'white_bg_topview' ? '白底 TopView 圖' : '專業美食攝影圖'}
            {task.style_description && ` · 風格：${task.style_description}`}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {task.status === 'processing' && (
            <div className="space-y-2">
              <Progress value={task.progress} />
              <p className="text-sm text-gray-600 text-center">{task.progress}%</p>
            </div>
          )}
          {task.status === 'failed' && (
            <Alert variant="destructive">
              <AlertDescription>{task.error_message || '生成失敗'}</AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* 結果畫廊 */}
      {task.status === 'completed' && (
        <Card>
          <CardHeader>
            <CardTitle>生成結果</CardTitle>
            <CardDescription>共 {task.output_images.length} 張圖片</CardDescription>
          </CardHeader>
          <CardContent>
            <ResultGallery taskId={taskId} images={task.output_images} />
          </CardContent>
        </Card>
      )}
    </div>
  )
}
```

### Step 3: 測試結果頁面

確保前端 dev server 正在運行：

**Run:**
```bash
cd frontend
npm run dev
```

訪問 `http://localhost:3000/image-generator/test-id`（暫時會顯示「找不到該任務」）

**Expected:** 頁面可正常渲染，顯示錯誤訊息

### Step 4: Commit

```bash
git add frontend/src/app/image-generator/[taskId]/page.tsx frontend/src/components/image-generator/result-gallery.tsx
git commit -m "feat(frontend): add image generator result page with polling"
```

---

## Task 6: 端到端測試

**Files:**
- Create: `backend/tests/test_e2e_image_generation.py`
- Modify: `backend/.env.example` (add nano-banana config)

### Step 1: 創建 E2E 測試

在 `backend/tests/test_e2e_image_generation.py` 寫入：

```python
# =============================================
# 圖片生成端到端測試
# =============================================

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import io
from PIL import Image


def create_test_image():
    """創建測試圖片"""
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes


@pytest.mark.e2e
def test_complete_image_generation_flow(client: TestClient, auth_headers):
    """測試完整的圖片生成流程"""

    # Step 1: 創建任務
    response = client.post(
        "/api/v1/image-generation/tasks",
        json={
            "mode": "white_bg_topview",
            "style_description": "Clean minimal style"
        },
        headers=auth_headers
    )
    assert response.status_code == 200
    task = response.json()
    task_id = task["id"]

    # Step 2: 上傳圖片
    files = [
        ("files", ("test1.png", create_test_image(), "image/png")),
        ("files", ("test2.png", create_test_image(), "image/png")),
    ]

    response = client.post(
        f"/api/v1/image-generation/tasks/{task_id}/upload",
        files=files,
        headers=auth_headers
    )
    assert response.status_code == 200
    uploaded = response.json()
    assert len(uploaded) == 2

    # Step 3: Mock nano-banana API and start generation
    with patch('app.tasks.image_generation_tasks.NanoBananaClient') as mock_client:
        mock_instance = MagicMock()
        mock_instance.generate_white_bg_topview.return_value = {
            "data": [{"b64_json": "fake_base64_data"}]
        }
        mock_instance.save_generated_images.return_value = [
            f"storage/generated/{task_id}/generated_1.png"
        ]
        mock_client.return_value = mock_instance

        response = client.post(
            f"/api/v1/image-generation/tasks/{task_id}/start",
            headers=auth_headers
        )
        assert response.status_code == 200

    # Step 4: 檢查狀態
    response = client.get(
        f"/api/v1/image-generation/tasks/{task_id}/status",
        headers=auth_headers
    )
    assert response.status_code == 200
    status = response.json()
    assert status["status"] in ["pending", "processing", "completed"]

    # Step 5: 獲取完整任務詳情
    response = client.get(
        f"/api/v1/image-generation/tasks/{task_id}",
        headers=auth_headers
    )
    assert response.status_code == 200
    task_detail = response.json()
    assert len(task_detail["input_images"]) == 2
```

### Step 2: 添加環境變數範例

在 `backend/.env.example` 添加：

```bash
# Nano-Banana Image Generation API
NANO_BANANA_API_BASE=https://ai.t8star.cn/v1
NANO_BANANA_API_KEY=your_api_key_here
NANO_BANANA_MODEL=nano-banana
```

### Step 3: Run E2E test

**Run:**
```bash
cd backend
pytest tests/test_e2e_image_generation.py -v -m e2e
```

**Expected:** Test PASS (with mocked nano-banana client)

### Step 4: Commit

```bash
git add backend/tests/test_e2e_image_generation.py backend/.env.example
git commit -m "test(e2e): add end-to-end image generation test"
```

---

## Task 7: 文檔與部署準備

**Files:**
- Create: `docs/features/image-generation.md`
- Modify: `README.md` (add feature documentation)

### Step 1: 創建功能文檔

在 `docs/features/image-generation.md` 寫入：

```markdown
# AI 產品圖片生成系統

## 功能概述

使用 nano-banana (Gemini 2.5 Flash Image) API 將普通產品圖片轉換為專業電商或行銷用圖。

## 功能特性

### 兩種生成模式

1. **白底 TopView 正面圖**
   - 純白背景（RGB 255,255,255）
   - 俯視角度（bird's eye view）
   - 適合電商平台（淘寶、HKTVmall 等）
   - 輸出：1 張圖

2. **專業美食攝影圖**
   - 多角度構圖（特寫、場景、藝術角度）
   - 專業打光和造型
   - 適合社交媒體和行銷推廣
   - 輸出：2-3 張圖

### 工作流程

```
用戶上傳 5 張產品圖
    ↓
創建生成任務
    ↓
後端分析圖片（Google Vision AI - 可選）
    ↓
生成 AI prompt（基於分析 + 用戶風格描述）
    ↓
調用 nano-banana API
    ↓
保存生成結果
    ↓
前端輪詢獲取結果
```

## API 端點

### 創建任務
```http
POST /api/v1/image-generation/tasks
Content-Type: application/json

{
  "mode": "white_bg_topview",
  "style_description": "Clean and minimal"
}
```

### 上傳圖片
```http
POST /api/v1/image-generation/tasks/{task_id}/upload
Content-Type: multipart/form-data

files: [File, File, ...]
```

### 啟動生成
```http
POST /api/v1/image-generation/tasks/{task_id}/start
```

### 查詢狀態（輪詢）
```http
GET /api/v1/image-generation/tasks/{task_id}/status
```

### 獲取任務詳情
```http
GET /api/v1/image-generation/tasks/{task_id}
```

### 下載生成圖片
```http
GET /api/v1/image-generation/tasks/{task_id}/outputs/{image_id}
```

## 環境配置

```bash
# .env
NANO_BANANA_API_BASE=https://ai.t8star.cn/v1
NANO_BANANA_API_KEY=your_api_key_here
NANO_BANANA_MODEL=nano-banana
```

## 資料庫 Schema

### image_generation_tasks
- id (UUID)
- user_id (UUID)
- mode (enum: white_bg_topview, professional_photo)
- style_description (text, nullable)
- status (enum: pending, processing, completed, failed)
- progress (int 0-100)
- error_message (text, nullable)
- celery_task_id (varchar, nullable)
- created_at, updated_at, completed_at

### input_images
- id (UUID)
- task_id (UUID, FK)
- file_path (varchar)
- file_name (varchar)
- file_size (int)
- mime_type (varchar)
- upload_order (int 1-5)
- analysis_result (JSON, nullable)
- created_at

### output_images
- id (UUID)
- task_id (UUID, FK)
- file_path (varchar)
- file_name (varchar)
- file_size (int, nullable)
- mime_type (varchar)
- prompt_used (text, nullable)
- generation_params (JSON, nullable)
- created_at

## Celery 任務

### process_image_generation
- 異步處理圖片生成
- 更新任務進度（10% → 20% → 30% → 70% → 90% → 100%）
- 錯誤處理與重試
- 時間限制：5 分鐘

## 前端頁面

### `/image-generator`
- 上傳介面
- 模式選擇
- 風格描述輸入
- 拖放上傳（最多 5 張）

### `/image-generator/[taskId]`
- 實時進度顯示
- 狀態輪詢（每 2 秒）
- 結果畫廊
- 下載功能

## 成本估算

- nano-banana API: ~$0.039 per image
- 白底模式（1 張）: ~$0.04
- 專業攝影模式（3 張）: ~$0.12

## 限制與注意事項

1. 每次最多上傳 5 張圖片
2. 支援格式：PNG, JPG, JPEG, WEBP
3. 單個任務超時時間：5 分鐘
4. API rate limit: 依 nano-banana 服務限制
5. 儲存空間：需定期清理舊任務的圖片文件

## 未來改進

- [ ] 添加圖片壓縮和優化
- [ ] 支援批量任務
- [ ] 添加任務歷史記錄頁面
- [ ] 集成 Google Vision AI 自動分析
- [ ] 添加更多生成模式（產品細節、組合圖等）
- [ ] 實作 WebSocket 替代輪詢
- [ ] 添加圖片編輯功能（裁剪、調整等）
```

### Step 2: 更新主 README

在 `README.md` 的功能列表中添加：

```markdown
## 主要功能

...existing features...

### 🎨 AI 產品圖片生成
- **白底 TopView 圖生成**：自動生成電商平台標準產品圖
- **專業美食攝影**：生成高質量行銷推廣圖片（2-3 張）
- **風格客製化**：支援用戶自定義風格描述
- **異步處理**：使用 Celery 後台處理，實時進度更新
- **批量上傳**：支援一次上傳最多 5 張產品圖

詳見 [圖片生成文檔](docs/features/image-generation.md)
```

### Step 3: Commit

```bash
git add docs/features/image-generation.md README.md
git commit -m "docs: add image generation feature documentation"
```

---

## 執行計劃完成

**Plan complete and saved to `docs/plans/2026-01-12-image-generation-system.md`.**

**Two execution options:**

**1. Subagent-Driven (this session)** - I dispatch fresh subagent per task, review between tasks, fast iteration

**2. Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints

**Which approach?**
