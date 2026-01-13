# =============================================
# 圖片生成 Celery 任務
# =============================================

import logging
from typing import Dict, Any, List
from pathlib import Path
from datetime import datetime, timedelta
from celery import Task
from sqlalchemy.orm import Session

from app.tasks.celery_app import celery_app
from app.models.database import Base, engine
from app.models.image_generation import (
    ImageGenerationTask as ImageGenTaskModel,
    InputImage,
    OutputImage,
    TaskStatus,
    GenerationMode
)
from app.services.nano_banana_client import NanoBananaClient
from app.services.storage_service import get_storage
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# 創建同步資料庫 session（用於 Celery 任務）
sync_db_url = settings.database_url.replace("postgresql+asyncpg://", "postgresql://")
sync_engine = create_engine(sync_db_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=sync_engine, autocommit=False, autoflush=False)


class ImageGenTaskBase(Task):
    """圖片生成任務基類（避免與 model 名稱衝突）"""

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """任務失敗處理"""
        logger.error(f"Task {task_id} failed: {exc}")

        # 更新任務狀態為失敗
        db = SessionLocal()
        try:
            gen_task_id = kwargs.get('task_id') or (args[0] if args else None)
            if gen_task_id:
                task = db.query(ImageGenTaskModel).filter(
                    ImageGenTaskModel.id == gen_task_id
                ).first()

                if task:
                    task.status = TaskStatus.FAILED
                    task.error_message = str(exc)
                    db.commit()
        except Exception as e:
            logger.error(f"Failed to update task status: {e}")
            db.rollback()
        finally:
            db.close()


@celery_app.task(base=ImageGenTaskBase, bind=True, name="process_image_generation")
def process_image_generation(self, task_id: str) -> Dict[str, Any]:
    """
    處理圖片生成任務（兩階段連續執行）

    階段 1：AI 分析圖片
      - 使用 Gemini Thinking 模型分析每張輸入圖片
      - 生成針對性的 prompt
      - 保存分析結果到 InputImage.analysis_result

    階段 2：圖片生成
      - 使用分析生成的 prompt 調用 Nano-Banana API
      - 保存生成的圖片

    Args:
        task_id: ImageGenerationTask ID

    Returns:
        任務結果字典
    """
    db = SessionLocal()

    try:
        # 獲取任務
        task = db.query(ImageGenTaskModel).filter(
            ImageGenTaskModel.id == task_id
        ).first()

        if not task:
            raise ValueError(f"Task {task_id} not found")

        # 初始化 Nano-Banana 客戶端
        client = NanoBananaClient()

        # ==================== 階段 1：AI 分析圖片 ====================
        logger.info(f"[Task {task_id}] Starting Stage 1: AI Image Analysis")

        task.status = TaskStatus.ANALYZING
        task.progress = 5
        task.celery_task_id = self.request.id
        db.commit()

        # 獲取輸入圖片
        input_images = db.query(InputImage).filter(
            InputImage.task_id == task_id
        ).order_by(InputImage.upload_order).all()

        if not input_images:
            raise ValueError("No input images found")

        # 分析每張輸入圖片
        total_images = len(input_images)
        analysis_results = []

        for idx, input_img in enumerate(input_images):
            logger.info(f"[Task {task_id}] Analyzing image {idx + 1}/{total_images}: {input_img.file_name}")

            # 調用 AI 分析
            analysis = client.analyze_image_for_generation(
                image_path=input_img.file_path,
                mode=task.mode.value,
                style_description=task.style_description
            )

            # 保存分析結果到 InputImage
            input_img.analysis_result = analysis
            analysis_results.append(analysis)

            # 更新進度（階段 1 佔 5% - 30%）
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

        # 獲取輸出數量配置
        outputs_per_image = task.outputs_per_image or 1
        logger.info(f"[Task {task_id}] Generating {outputs_per_image} output(s) per input image")

        # 收集所有生成的圖片
        all_output_data = []  # [(output_path, prompt_used, input_image_id), ...]

        for idx, input_img in enumerate(input_images):
            # 從分析結果中獲取定制化 prompt
            analysis = input_img.analysis_result or {}
            generated_prompt = analysis.get("generated_prompt")

            # 如果分析失敗，使用默認 prompt
            if not generated_prompt:
                logger.warning(f"[Task {task_id}] No generated prompt for image {idx + 1}, using fallback")
                if task.mode == GenerationMode.WHITE_BG_TOPVIEW:
                    generated_prompt = client._build_white_bg_prompt(None)
                else:
                    generated_prompt = client._build_professional_photo_prompt(task.style_description, None)

            logger.info(f"[Task {task_id}] Generating for image {idx + 1}/{total_images} with AI-generated prompt")

            # 對每張輸入圖片生成指定數量的輸出
            for output_idx in range(outputs_per_image):
                logger.info(f"[Task {task_id}] Generating output {output_idx + 1}/{outputs_per_image} for input {idx + 1}")

                # 調用 API 生成單張圖片
                api_response = client._call_api_single(
                    input_images=[input_img.file_path],
                    prompt=generated_prompt,
                    aspect_ratio="1:1"
                )

                # 保存生成的圖片
                output_dir = f"generated/{str(task_id)}"
                output_filename = f"generated_{idx + 1}_{output_idx + 1}.png"
                output_relative_path = f"{output_dir}/{output_filename}"

                if "data" in api_response and api_response["data"]:
                    item = api_response["data"][0]
                    if "b64_json" in item:
                        import base64
                        b64_string = item["b64_json"].strip()

                        # 去除 Data URL 前綴
                        if b64_string.startswith('data:'):
                            comma_index = b64_string.find(',')
                            if comma_index != -1:
                                b64_string = b64_string[comma_index + 1:]

                        # 修復 padding
                        missing_padding = len(b64_string) % 4
                        if missing_padding:
                            b64_string += '=' * (4 - missing_padding)

                        image_data = base64.b64decode(b64_string)

                        # 使用 StorageService 保存
                        storage = get_storage()
                        file_url = storage.save_file(
                            file_data=image_data,
                            file_path=output_relative_path
                        )

                        all_output_data.append((file_url, generated_prompt, str(input_img.id)))
                        logger.info(f"[Task {task_id}] Saved output: {output_relative_path}")

            # 更新進度（階段 2 佔 35% - 90%）
            stage2_progress = 35 + int((idx + 1) / total_images * 55)
            task.progress = stage2_progress
            db.commit()

        logger.info(f"[Task {task_id}] Stage 2 complete. Generated {len(all_output_data)} images.")

        # ==================== 保存輸出記錄 ====================
        task.progress = 95
        db.commit()

        for output_path, prompt_used, input_image_id in all_output_data:
            # 提取檔名
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
                    "two_stage_generation": True
                }
            )
            db.add(output_image)

        # 更新任務狀態為完成
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
            "two_stage_generation": True
        }

    except Exception as e:
        logger.error(f"[Task {task_id}] Error: {e}", exc_info=True)

        # 更新任務狀態為失敗
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

@celery_app.task(name="cleanup_old_image_tasks")
def cleanup_old_image_tasks(days: int = 7) -> Dict[str, Any]:
    """
    清理過期的圖片生成任務（默認 7 天前）

    Args:
        days: 保留天數，超過此天數的任務將被刪除

    Returns:
        清理結果統計
    """
    db = SessionLocal()
    storage = get_storage()

    try:
        # 計算過期時間
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        logger.info(f"Starting cleanup of image tasks older than {cutoff_date}")

        # 查詢過期任務
        expired_tasks = db.query(ImageGenTaskModel).filter(
            ImageGenTaskModel.created_at < cutoff_date
        ).all()

        if not expired_tasks:
            logger.info("No expired tasks found")
            return {
                "status": "completed",
                "deleted_count": 0,
                "message": "No expired tasks found"
            }

        deleted_count = 0
        deleted_input_files = 0
        deleted_output_files = 0

        for task in expired_tasks:
            try:
                # 獲取關聯圖片
                input_images = db.query(InputImage).filter(
                    InputImage.task_id == task.id
                ).all()

                output_images = db.query(OutputImage).filter(
                    OutputImage.task_id == task.id
                ).all()

                # 刪除輸入圖片文件
                for img in input_images:
                    try:
                        if img.file_path:
                            _delete_storage_file(storage, img.file_path)
                            deleted_input_files += 1
                    except Exception as e:
                        logger.warning(f"Failed to delete input file {img.file_path}: {e}")

                # 刪除輸出圖片文件
                for img in output_images:
                    try:
                        if img.file_path:
                            _delete_storage_file(storage, img.file_path)
                            deleted_output_files += 1
                    except Exception as e:
                        logger.warning(f"Failed to delete output file {img.file_path}: {e}")

                # 刪除數據庫記錄
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
            "cutoff_date": cutoff_date.isoformat()
        }

    except Exception as e:
        logger.error(f"Cleanup task failed: {e}", exc_info=True)
        db.rollback()
        raise

    finally:
        db.close()


def _delete_storage_file(storage, file_path: str):
    """
    刪除存儲文件的輔助函數
    """
    try:
        if file_path.startswith('http'):
            # R2 URL，提取相對路徑
            if hasattr(storage, 'public_url_base') and storage.public_url_base and storage.public_url_base in file_path:
                relative_path = file_path.replace(f"{storage.public_url_base}/", "")
                storage.delete_file(relative_path)
        else:
            # 本地路徑
            storage.delete_file(file_path)
    except Exception as e:
        logger.warning(f"Failed to delete file {file_path}: {e}")
