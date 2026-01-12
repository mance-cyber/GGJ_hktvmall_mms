# =============================================
# 圖片生成 Celery 任務
# =============================================

import logging
from typing import Dict, Any
from pathlib import Path
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

        if task.mode == GenerationMode.WHITE_BG_TOPVIEW:
            # 生成白底圖（1 張）
            logger.info(f"Generating white background top-view for task {task_id}")

            # 獲取產品分析結果（如果有）
            product_analysis = input_images[0].analysis_result if input_images else None

            api_response = client.generate_white_bg_topview(
                input_images=input_image_paths,
                product_analysis=product_analysis
            )

        elif task.mode == GenerationMode.PROFESSIONAL_PHOTO:
            # 生成專業攝影圖（2-3 張）
            logger.info(f"Generating professional photos for task {task_id}")

            product_analysis = input_images[0].analysis_result if input_images else None

            api_response = client.generate_professional_photos(
                input_images=input_image_paths,
                style_description=task.style_description,
                product_analysis=product_analysis
            )
        else:
            raise ValueError(f"Unknown generation mode: {task.mode}")

        # 更新進度：API 調用完成
        task.progress = 60
        db.commit()

        # 保存生成的圖片
        output_dir = Path(settings.upload_dir) / "generated" / str(task_id)
        output_paths = client.save_generated_images(
            api_response=api_response,
            output_dir=str(output_dir)
        )

        # 更新進度：保存圖片完成
        task.progress = 80
        db.commit()

        # 創建 OutputImage 記錄
        for idx, output_path in enumerate(output_paths):
            output_image = OutputImage(
                task_id=task_id,
                file_path=output_path,
                file_name=Path(output_path).name,
                file_size=Path(output_path).stat().st_size if Path(output_path).exists() else None,
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
