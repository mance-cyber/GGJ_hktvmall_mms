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
    處理圖片生成任務

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

        # 更新狀態為處理中
        task.status = TaskStatus.PROCESSING
        task.progress = 10
        task.celery_task_id = self.request.id
        db.commit()

        # 獲取輸入圖片
        input_images = db.query(InputImage).filter(
            InputImage.task_id == task_id
        ).order_by(InputImage.upload_order).all()

        if not input_images:
            raise ValueError("No input images found")

        input_image_paths = [img.file_path for img in input_images]

        # 更新進度：準備 API 調用
        task.progress = 20
        db.commit()

        # 初始化 Nano-Banana 客戶端
        client = NanoBananaClient()

        # 根據模式調用不同的生成方法
        task.progress = 30
        db.commit()

        # 獲取輸出數量配置
        outputs_per_image = task.outputs_per_image or 1
        logger.info(f"Configured to generate {outputs_per_image} image(s) per input")

        if task.mode == GenerationMode.WHITE_BG_TOPVIEW:
            # 生成白底圖
            logger.info(f"Generating white background top-view for task {task_id}")

            # 獲取產品分析結果（如果有）
            product_analysis = input_images[0].analysis_result if input_images else None

            api_response = client.generate_white_bg_topview(
                input_images=input_image_paths,
                product_analysis=product_analysis,
                num_outputs=outputs_per_image
            )

        elif task.mode == GenerationMode.PROFESSIONAL_PHOTO:
            # 生成專業攝影圖
            logger.info(f"Generating professional photos for task {task_id}")

            product_analysis = input_images[0].analysis_result if input_images else None

            api_response = client.generate_professional_photos(
                input_images=input_image_paths,
                style_description=task.style_description,
                product_analysis=product_analysis,
                num_outputs=outputs_per_image
            )
        else:
            raise ValueError(f"Unknown generation mode: {task.mode}")

        # 更新進度：API 調用完成
        task.progress = 60
        db.commit()

        # 保存生成的圖片（使用相對路徑）
        output_dir = f"generated/{str(task_id)}"
        output_paths = client.save_generated_images(
            api_response=api_response,
            output_dir=output_dir
        )

        # 更新進度：保存圖片完成
        task.progress = 80
        db.commit()

        # 創建 OutputImage 記錄
        for idx, output_path in enumerate(output_paths):
            # 提取檔名（支持 URL 和本地路徑）
            if output_path.startswith('http'):
                # R2 URL 格式：https://domain.com/generated/task-id/generated_1.png
                file_name = output_path.split('/')[-1]
            else:
                # 本地路徑
                file_name = Path(output_path).name

            output_image = OutputImage(
                task_id=task_id,
                file_path=output_path,
                file_name=file_name,
                file_size=None,  # 文件大小可選（R2 模式下無法直接獲取）
                prompt_used=client._build_white_bg_prompt(None) if task.mode == GenerationMode.WHITE_BG_TOPVIEW else client._build_professional_photo_prompt(task.style_description, None),
                generation_params={
                    "mode": task.mode.value,
                    "num_outputs": len(output_paths),
                    "index": idx + 1
                }
            )
            db.add(output_image)

        # 更新任務狀態為完成
        task.status = TaskStatus.COMPLETED
        task.progress = 100
        db.commit()

        logger.info(f"Task {task_id} completed successfully. Generated {len(output_paths)} images.")

        return {
            "task_id": str(task_id),
            "status": "completed",
            "output_count": len(output_paths),
            "output_paths": output_paths
        }

    except Exception as e:
        logger.error(f"Error processing task {task_id}: {e}", exc_info=True)

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
