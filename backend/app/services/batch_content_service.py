# =============================================
# AI 文案批量生成服務
# =============================================
#
# 支持兩種模式：
# - 同步模式（≤10 個）：直接返回結果
# - 異步模式（>10 個）：後台處理 + 進度追蹤
#

import asyncio
import json
import uuid
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.product import Product
from app.models.content import AIContent
from app.services.ai_service import get_ai_analysis_service
from app.schemas.content import (
    BatchGenerateItem,
    ContentBatchGenerateRequest,
    BatchResultItem,
    BatchSummary,
    BatchProgress,
    GeneratedContent,
)


# =============================================
# 常量配置
# =============================================

SYNC_THRESHOLD = 10          # 同步/異步閾值
MAX_CONCURRENT = 3           # 最大並發數
TASK_TTL_HOURS = 24         # 任務快取 TTL


# =============================================
# 任務狀態管理（內存實現，可升級 Redis）
# =============================================

@dataclass
class BatchTaskState:
    """批量任務狀態"""
    task_id: str
    status: str  # pending / processing / completed / failed
    total: int
    completed: int = 0
    failed: int = 0
    items: List[Dict] = field(default_factory=list)
    config: Dict = field(default_factory=dict)
    results: List[Dict] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    error: Optional[str] = None

    @property
    def percent(self) -> int:
        if self.total == 0:
            return 0
        return int((self.completed + self.failed) / self.total * 100)


class BatchTaskStore:
    """
    批量任務存儲（內存實現）

    生產環境可替換為 Redis 實現
    """
    _tasks: Dict[str, BatchTaskState] = {}
    _task_expiry: Dict[str, datetime] = {}

    @classmethod
    def create_task(
        cls,
        items: List[Dict],
        config: Dict,
    ) -> str:
        """創建新任務"""
        task_id = str(uuid.uuid4())
        task = BatchTaskState(
            task_id=task_id,
            status="pending",
            total=len(items),
            items=items,
            config=config,
        )
        cls._tasks[task_id] = task
        cls._task_expiry[task_id] = datetime.now() + timedelta(hours=TASK_TTL_HOURS)
        return task_id

    @classmethod
    def get_task(cls, task_id: str) -> Optional[BatchTaskState]:
        """獲取任務狀態"""
        cls._cleanup_expired()
        return cls._tasks.get(task_id)

    @classmethod
    def update_task(
        cls,
        task_id: str,
        status: Optional[str] = None,
        completed: Optional[int] = None,
        failed: Optional[int] = None,
        result: Optional[Dict] = None,
        error: Optional[str] = None,
    ) -> None:
        """更新任務狀態"""
        task = cls._tasks.get(task_id)
        if not task:
            return

        if status:
            task.status = status
        if completed is not None:
            task.completed = completed
        if failed is not None:
            task.failed = failed
        if result:
            task.results.append(result)
        if error:
            task.error = error

    @classmethod
    def _cleanup_expired(cls) -> None:
        """清理過期任務"""
        now = datetime.now()
        expired = [
            task_id for task_id, expiry in cls._task_expiry.items()
            if now > expiry
        ]
        for task_id in expired:
            cls._tasks.pop(task_id, None)
            cls._task_expiry.pop(task_id, None)

        if expired:
            logger.debug(f"清理了 {len(expired)} 個過期的批量任務")


# =============================================
# 批量生成服務
# =============================================

class BatchContentService:
    """批量文案生成服務"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self._semaphore = asyncio.Semaphore(MAX_CONCURRENT)

    async def generate_batch(
        self,
        request: ContentBatchGenerateRequest,
    ) -> Dict[str, Any]:
        """
        批量生成文案入口

        根據數量自動選擇同步或異步模式
        """
        item_count = len(request.items)

        if item_count <= SYNC_THRESHOLD:
            # 同步模式：直接處理並返回結果
            return await self._generate_sync(request)
        else:
            # 異步模式：創建任務並後台處理
            return await self._generate_async(request)

    # =============================================
    # 同步模式
    # =============================================

    async def _generate_sync(
        self,
        request: ContentBatchGenerateRequest,
    ) -> Dict[str, Any]:
        """同步批量生成（≤10 個）"""
        results: List[BatchResultItem] = []
        success_count = 0
        failed_count = 0

        # 逐個生成（帶並發控制）
        tasks = [
            self._generate_single_with_limit(
                index=i,
                item=item,
                content_type=request.content_type,
                style=request.style,
                target_languages=request.target_languages,
            )
            for i, item in enumerate(request.items)
        ]

        # 並發執行
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in batch_results:
            if isinstance(result, Exception):
                # 處理異常
                failed_count += 1
                results.append(BatchResultItem(
                    index=len(results),
                    success=False,
                    product_name="未知",
                    error=str(result),
                ))
            else:
                results.append(result)
                if result.success:
                    success_count += 1
                else:
                    failed_count += 1

        return {
            "mode": "sync",
            "results": [r.model_dump() for r in results],
            "summary": {
                "total": len(request.items),
                "success": success_count,
                "failed": failed_count,
            },
        }

    # =============================================
    # 異步模式
    # =============================================

    async def _generate_async(
        self,
        request: ContentBatchGenerateRequest,
    ) -> Dict[str, Any]:
        """異步批量生成（>10 個）"""
        # 序列化 items
        items_data = [
            {
                "product_id": str(item.product_id) if item.product_id else None,
                "product_info": item.product_info.model_dump() if item.product_info else None,
            }
            for item in request.items
        ]

        config = {
            "content_type": request.content_type,
            "style": request.style,
            "target_languages": request.target_languages,
        }

        # 創建任務
        task_id = BatchTaskStore.create_task(items=items_data, config=config)

        # 啟動後台處理
        asyncio.create_task(
            self._process_async_task(task_id)
        )

        return {
            "mode": "async",
            "task_id": task_id,
            "total": len(request.items),
            "message": "批量任務已提交，請通過任務ID查詢進度",
        }

    async def _process_async_task(self, task_id: str) -> None:
        """後台處理異步任務"""
        task = BatchTaskStore.get_task(task_id)
        if not task:
            return

        BatchTaskStore.update_task(task_id, status="processing")

        completed = 0
        failed = 0

        # 逐個處理
        for i, item_data in enumerate(task.items):
            try:
                # 重建 BatchGenerateItem
                from app.schemas.content import ProductInfo

                item = BatchGenerateItem(
                    product_id=uuid.UUID(item_data["product_id"]) if item_data.get("product_id") else None,
                    product_info=ProductInfo(**item_data["product_info"]) if item_data.get("product_info") else None,
                )

                result = await self._generate_single_with_limit(
                    index=i,
                    item=item,
                    content_type=task.config["content_type"],
                    style=task.config["style"],
                    target_languages=task.config["target_languages"],
                )

                if result.success:
                    completed += 1
                else:
                    failed += 1

                BatchTaskStore.update_task(
                    task_id,
                    completed=completed,
                    failed=failed,
                    result=result.model_dump(),
                )

            except Exception as e:
                failed += 1
                logger.error(
                    f"批量任務 {task_id} 第 {i} 項處理失敗: {str(e)}",
                    exc_info=True,
                    extra={
                        "task_id": task_id,
                        "item_index": i,
                        "product_id": item_data.get("product_id"),
                    }
                )
                BatchTaskStore.update_task(
                    task_id,
                    completed=completed,
                    failed=failed,
                    result={
                        "index": i,
                        "success": False,
                        "product_name": "未知",
                        "error": str(e),
                    },
                )

        # 任務完成
        logger.info(
            f"批量任務 {task_id} 完成: 成功 {completed}, 失敗 {failed}, 總計 {len(task.items)}"
        )
        final_status = "completed" if failed < len(task.items) else "failed"
        BatchTaskStore.update_task(task_id, status=final_status)

    # =============================================
    # 單項生成
    # =============================================

    async def _generate_single_with_limit(
        self,
        index: int,
        item: BatchGenerateItem,
        content_type: str,
        style: str,
        target_languages: List[str],
    ) -> BatchResultItem:
        """帶並發控制的單項生成"""
        async with self._semaphore:
            return await self._generate_single(
                index=index,
                item=item,
                content_type=content_type,
                style=style,
                target_languages=target_languages,
            )

    async def _generate_single(
        self,
        index: int,
        item: BatchGenerateItem,
        content_type: str,
        style: str,
        target_languages: List[str],
    ) -> BatchResultItem:
        """生成單個商品文案"""
        product_name = ""
        product_data = {}

        try:
            # 獲取商品資訊
            if item.product_id:
                result = await self.db.execute(
                    select(Product).where(Product.id == item.product_id)
                )
                product = result.scalar_one_or_none()
                if not product:
                    return BatchResultItem(
                        index=index,
                        success=False,
                        product_name=f"商品 {item.product_id}",
                        error="商品不存在",
                    )

                product_name = product.name
                product_data = {
                    "name": product.name,
                    "brand": product.brand,
                    "price": float(product.price) if product.price else None,
                    "original_price": float(product.original_price) if product.original_price else None,
                    "description": product.description,
                    "category": product.category,
                }

            elif item.product_info:
                product_name = item.product_info.name
                product_data = item.product_info.model_dump()

            else:
                return BatchResultItem(
                    index=index,
                    success=False,
                    product_name="未知",
                    error="請提供 product_id 或 product_info",
                )

            # 調用 AI 服務
            ai_service = await get_ai_analysis_service(self.db)
            ai_response = ai_service.generate_product_content(
                product_name=product_name,
                product_info=product_data,
                content_type=content_type,
                style=style,
                target_languages=target_languages,
            )

            if not ai_response.success:
                return BatchResultItem(
                    index=index,
                    success=False,
                    product_name=product_name,
                    error=f"AI 服務錯誤: {ai_response.error}",
                )

            # 解析響應
            try:
                content_json = json.loads(ai_response.content)

                # 處理多語言格式
                is_multilang = len(target_languages) > 1 and any(
                    key in content_json for key in ["TC", "SC", "EN", "multilang"]
                )

                if is_multilang:
                    multilang_data = content_json.get("multilang", {})
                    if not multilang_data:
                        for lang in ["TC", "SC", "EN"]:
                            if lang in content_json:
                                multilang_data[lang] = content_json[lang]

                    primary_lang = target_languages[0]
                    primary_content = multilang_data.get(primary_lang, {})

                    generated = GeneratedContent(
                        title=primary_content.get("title", product_name),
                        selling_points=primary_content.get("selling_points", []),
                        description=primary_content.get("description", ""),
                        short_description=primary_content.get("short_description"),
                        multilang=multilang_data,
                    )
                else:
                    generated = GeneratedContent(
                        title=content_json.get("title", product_name),
                        selling_points=content_json.get("selling_points", []),
                        description=content_json.get("description", ""),
                        short_description=content_json.get("short_description"),
                        hashtags=content_json.get("hashtags"),
                    )

            except json.JSONDecodeError:
                generated = GeneratedContent(
                    title=product_name,
                    selling_points=[],
                    description=ai_response.content,
                )

            # 保存到數據庫
            content = AIContent(
                product_id=item.product_id,
                content_type=content_type,
                style=style,
                language="zh-HK",
                content=generated.description or "",
                content_json=generated.model_dump(),
                status="draft",
                metadata={
                    "model": ai_response.model,
                    "tokens_used": ai_response.tokens_used,
                    "generated_by": "batch",
                },
                input_data=item.product_info.model_dump() if item.product_info else None,
            )
            self.db.add(content)
            await self.db.flush()
            await self.db.refresh(content)

            return BatchResultItem(
                index=index,
                success=True,
                content_id=content.id,
                product_name=product_name,
                content=generated,
            )

        except Exception as e:
            logger.error(
                f"生成文案失敗 [index={index}, product={product_name or '未知'}]: {str(e)}",
                exc_info=True,
                extra={
                    "index": index,
                    "product_name": product_name,
                    "content_type": content_type,
                }
            )
            return BatchResultItem(
                index=index,
                success=False,
                product_name=product_name or "未知",
                error=str(e),
            )

    # =============================================
    # 任務狀態查詢
    # =============================================

    @staticmethod
    def get_task_status(task_id: str) -> Optional[Dict[str, Any]]:
        """獲取任務狀態"""
        task = BatchTaskStore.get_task(task_id)
        if not task:
            return None

        return {
            "task_id": task.task_id,
            "status": task.status,
            "progress": {
                "total": task.total,
                "completed": task.completed,
                "failed": task.failed,
                "percent": task.percent,
            },
            "results": task.results,
        }


# =============================================
# 工廠函數
# =============================================

async def get_batch_content_service(db: AsyncSession) -> BatchContentService:
    """獲取批量生成服務實例"""
    return BatchContentService(db)
