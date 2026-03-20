# =============================================
# 圖片生成任務（純 async，無 Celery 依賴）
# =============================================

import logging
from typing import Dict, Any
from pathlib import Path
from datetime import datetime, timedelta
from uuid import uuid4

from app.models.database import async_session_maker
from app.models.image_generation import (
    ImageGenerationTask as ImageGenTaskModel,
    InputImage,
    OutputImage,
    TaskStatus,
    GenerationMode,
)
from app.services.nano_banana_client import NanoBananaClient
from app.services.storage_service import get_storage
from app.config import get_settings

logger = logging.getLogger(__name__)

# 同步 DB session（圖片生成任務使用同步 API 客戶端）
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

settings = get_settings()
sync_db_url = settings.database_url.replace("postgresql+asyncpg://", "postgresql://")
sync_engine = create_engine(sync_db_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=sync_engine, autocommit=False, autoflush=False)


async def process_image_generation_async(task_id: str) -> Dict[str, Any]:
    """
    處理圖片生成任務（兩階段連續執行）

    階段 1：AI 分析圖片（Gemini Thinking）
    階段 2：圖片生成（Nano-Banana API）

    注意：此任務使用同步 DB session，因為底層 API 客戶端是同步的。
    使用 asyncio.to_thread 避免阻塞事件循環。
    """
    import asyncio
    return await asyncio.to_thread(_process_image_generation_sync, task_id)


def _process_image_generation_sync(task_id: str) -> Dict[str, Any]:
    """同步執行圖片生成（在線程中運行）"""
    db = SessionLocal()

    try:
        task = db.query(ImageGenTaskModel).filter(
            ImageGenTaskModel.id == task_id
        ).first()

        if not task:
            raise ValueError(f"Task {task_id} not found")

        client = NanoBananaClient()

        # ==================== 階段 1：AI 分析圖片 ====================
        logger.info(f"[Task {task_id}] Starting Stage 1: AI Image Analysis")

        task.status = TaskStatus.ANALYZING
        task.progress = 5
        db.commit()

        input_images = db.query(InputImage).filter(
            InputImage.task_id == task_id
        ).order_by(InputImage.upload_order).all()

        if not input_images:
            raise ValueError("No input images found")

        total_images = len(input_images)

        for idx, input_img in enumerate(input_images):
            logger.info(f"[Task {task_id}] Analyzing image {idx + 1}/{total_images}: {input_img.file_name}")

            analysis = client.analyze_image_for_generation(
                image_path=input_img.file_path,
                mode=task.mode.value,
                style_description=task.style_description,
            )

            input_img.analysis_result = analysis

            stage1_progress = 5 + int((idx + 1) / total_images * 25)
            task.progress = stage1_progress
            db.commit()

            logger.info(f"[Task {task_id}] Image {idx + 1} analysis complete. "
                       f"Product type: {analysis.get('product_type', 'unknown')}")

        logger.info(f"[Task {task_id}] Stage 1 complete. All {total_images} images analyzed.")

        # ==================== 階段 2：圖片生成 ====================
        logger.info(f"[Task {task_id}] Starting Stage 2: Image Generation")

        task.status = TaskStatus.PROCESSING
        task.progress = 35
        db.commit()

        outputs_per_image = task.outputs_per_image or 1
        logger.info(f"[Task {task_id}] Generating {outputs_per_image} output(s) per input image")

        all_output_data = []

        for idx, input_img in enumerate(input_images):
            analysis = input_img.analysis_result or {}
            generated_prompt = analysis.get("generated_prompt")

            if not generated_prompt:
                logger.warning(f"[Task {task_id}] No generated prompt for image {idx + 1}, using fallback")
                if task.mode == GenerationMode.WHITE_BG_TOPVIEW:
                    generated_prompt = client._build_white_bg_prompt(None)
                else:
                    generated_prompt = client._build_professional_photo_prompt(task.style_description, None)

            logger.info(f"[Task {task_id}] Generating for image {idx + 1}/{total_images} with AI-generated prompt")

            for output_idx in range(outputs_per_image):
                logger.info(f"[Task {task_id}] Generating output {output_idx + 1}/{outputs_per_image} for input {idx + 1}")

                api_response = client._call_api_single(
                    input_images=[input_img.file_path],
                    prompt=generated_prompt,
                    aspect_ratio="1:1",
                )

                output_dir = f"generated/{str(task_id)}"
                output_filename = f"generated_{idx + 1}_{output_idx + 1}.png"
                output_relative_path = f"{output_dir}/{output_filename}"

                if "data" in api_response and api_response["data"]:
                    item = api_response["data"][0]
                    if "b64_json" in item:
                        import base64
                        b64_string = item["b64_json"].strip()

                        if b64_string.startswith('data:'):
                            comma_index = b64_string.find(',')
                            if comma_index != -1:
                                b64_string = b64_string[comma_index + 1:]

                        missing_padding = len(b64_string) % 4
                        if missing_padding:
                            b64_string += '=' * (4 - missing_padding)

                        image_data = base64.b64decode(b64_string)

                        storage = get_storage()
                        file_url = storage.save_file(
                            file_data=image_data,
                            file_path=output_relative_path,
                        )

                        all_output_data.append((file_url, generated_prompt, str(input_img.id)))
                        logger.info(f"[Task {task_id}] Saved output: {output_relative_path}")

            stage2_progress = 35 + int((idx + 1) / total_images * 55)
            task.progress = stage2_progress
            db.commit()

        logger.info(f"[Task {task_id}] Stage 2 complete. Generated {len(all_output_data)} images.")

        # ==================== 保存輸出記錄 ====================
        task.progress = 95
        db.commit()

        for output_path, prompt_used, input_image_id in all_output_data:
            if output_path.startswith('http'):
                file_name = output_path.split('/')[-1]
            else:
                file_name = Path(output_path).name

            output_image = OutputImage(
                task_id=task_id,
                file_path=output_path,
                file_name=file_name,
                file_size=None,
                prompt_used=prompt_used,
                generation_params={
                    "mode": task.mode.value,
                    "input_image_id": input_image_id,
                    "two_stage_generation": True,
                },
            )
            db.add(output_image)

        task.status = TaskStatus.COMPLETED
        task.progress = 100
        task.completed_at = datetime.utcnow()
        db.commit()

        logger.info(f"[Task {task_id}] Task completed successfully. "
                   f"Generated {len(all_output_data)} images from {total_images} inputs.")

        return {
            "task_id": str(task_id),
            "status": "completed",
            "output_count": len(all_output_data),
            "input_count": total_images,
            "two_stage_generation": True,
        }

    except Exception as e:
        logger.error(f"[Task {task_id}] Error: {e}", exc_info=True)

        try:
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            db.commit()
        except Exception as commit_error:
            logger.error(f"Failed to commit error status: {commit_error}")
            db.rollback()

        raise

    finally:
        db.close()


# =============================================
# 定時清理任務
# =============================================

async def cleanup_old_image_tasks_async(days: int = 7) -> Dict[str, Any]:
    """清理過期的圖片生成任務"""
    import asyncio
    return await asyncio.to_thread(_cleanup_old_image_tasks_sync, days)


def _cleanup_old_image_tasks_sync(days: int = 7) -> Dict[str, Any]:
    """同步清理（在線程中運行）"""
    db = SessionLocal()
    storage = get_storage()

    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        logger.info(f"Starting cleanup of image tasks older than {cutoff_date}")

        expired_tasks = db.query(ImageGenTaskModel).filter(
            ImageGenTaskModel.created_at < cutoff_date
        ).all()

        if not expired_tasks:
            logger.info("No expired tasks found")
            return {"status": "completed", "deleted_count": 0, "message": "No expired tasks found"}

        deleted_count = 0
        deleted_input_files = 0
        deleted_output_files = 0

        for task in expired_tasks:
            try:
                input_images = db.query(InputImage).filter(InputImage.task_id == task.id).all()
                output_images = db.query(OutputImage).filter(OutputImage.task_id == task.id).all()

                for img in input_images:
                    try:
                        if img.file_path:
                            _delete_storage_file(storage, img.file_path)
                            deleted_input_files += 1
                    except Exception as e:
                        logger.warning(f"Failed to delete input file {img.file_path}: {e}")

                for img in output_images:
                    try:
                        if img.file_path:
                            _delete_storage_file(storage, img.file_path)
                            deleted_output_files += 1
                    except Exception as e:
                        logger.warning(f"Failed to delete output file {img.file_path}: {e}")

                db.delete(task)
                deleted_count += 1

            except Exception as e:
                logger.error(f"Failed to delete task {task.id}: {e}")
                continue

        db.commit()

        logger.info(
            f"Cleanup completed: {deleted_count} tasks, "
            f"{deleted_input_files} input files, "
            f"{deleted_output_files} output files deleted"
        )

        return {
            "status": "completed",
            "deleted_count": deleted_count,
            "deleted_input_files": deleted_input_files,
            "deleted_output_files": deleted_output_files,
            "cutoff_date": cutoff_date.isoformat(),
        }

    except Exception as e:
        logger.error(f"Cleanup task failed: {e}", exc_info=True)
        db.rollback()
        raise

    finally:
        db.close()


def _delete_storage_file(storage, file_path: str):
    """刪除存儲文件"""
    try:
        if file_path.startswith('http'):
            if hasattr(storage, 'public_url_base') and storage.public_url_base and storage.public_url_base in file_path:
                relative_path = file_path.replace(f"{storage.public_url_base}/", "")
                storage.delete_file(relative_path)
        else:
            storage.delete_file(file_path)
    except Exception as e:
        logger.warning(f"Failed to delete file {file_path}: {e}")
