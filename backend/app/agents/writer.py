# =============================================
# Writer Agent（文案官）
# =============================================
# 用途：AI 內容自動化 — 文案 + SEO + 多語言
# 封裝：ContentPipelineService
# =============================================

from typing import Any
from uuid import UUID

from app.agents.base import AgentBase
from app.agents.events import Event, Events

# 需要重新生成內容的字段
CONTENT_SENSITIVE_FIELDS = {
    "name", "name_zh", "name_ja", "name_en",
    "description", "category", "brand",
}


class WriterAgent(AgentBase):
    """
    文案官：自動為商品生成完整內容包

    內容包包含：
    - 多語言文案（zh-HK, zh-CN, en）
    - SEO 優化內容
    - FAQ 生成
    - GEO 結構化數據
    """

    @property
    def name(self) -> str:
        return "writer"

    @property
    def description(self) -> str:
        return "文案官：AI 文案生成、SEO 優化、多語言"

    def register_handlers(self) -> dict[str, Any]:
        return {
            Events.PRODUCT_CREATED: self._on_product_created,
            Events.PRODUCT_UPDATED: self._on_product_updated,
        }

    # ==================== 事件處理 ====================

    async def _on_product_created(self, event: Event) -> None:
        """新商品上架 -> 自動生成完整內容包"""
        product_id = event.payload.get("product_id")
        if not product_id:
            return

        self._logger.info(f"新商品 {product_id} -> 生成內容包")

        from app.services.content_pipeline import get_content_pipeline_service

        success = False
        async with self.get_db_session() as session:
            try:
                pipeline = await get_content_pipeline_service(session)
                result = await pipeline.run(
                    product_id=UUID(str(product_id)),
                    languages=["zh-HK", "zh-CN", "en"],
                    include_faq=True,
                    save_to_db=True,
                )
                success = result.success
                if result.success:
                    self._logger.info(
                        f"內容包生成完成: {product_id}, "
                        f"耗時 {result.generation_time_ms}ms"
                    )
                else:
                    self._logger.warning(f"內容包生成失敗: {result.error}")
            except Exception as exc:
                self._logger.error(f"內容流水線出錯: {exc}")
                await self.escalate_to_human(
                    "內容生成失敗",
                    f"商品 {product_id} 的內容自動生成出錯",
                    {"product_id": str(product_id), "error": str(exc)[:200]},
                )
                return

        if success:
            await self.emit(Events.CONTENT_GENERATED, {
                "product_id": str(product_id),
                "languages": ["zh-HK", "zh-CN", "en"],
            })

        await self.emit(Events.AGENT_TASK_COMPLETED, {
            "agent": self.name,
            "task": "generate_content",
            "product_id": str(product_id),
            "success": success,
        })

    async def _on_product_updated(self, event: Event) -> None:
        """商品更新 -> 判斷是否需要刷新內容"""
        product_id = event.payload.get("product_id")
        changed_fields = set(event.payload.get("changed_fields", []))

        if not product_id or not changed_fields:
            return

        # 只有影響內容的字段變更才觸發重新生成
        affected = changed_fields & CONTENT_SENSITIVE_FIELDS
        if not affected:
            self._logger.debug(
                f"商品 {product_id} 變更字段 {changed_fields} "
                f"不影響內容，跳過"
            )
            return

        self._logger.info(
            f"商品 {product_id} 內容相關字段變更: {affected} -> 重新生成"
        )

        from app.services.content_pipeline import get_content_pipeline_service

        success = False
        async with self.get_db_session() as session:
            try:
                pipeline = await get_content_pipeline_service(session)
                result = await pipeline.run(
                    product_id=UUID(str(product_id)),
                    languages=["zh-HK"],  # 更新時只重新生成主語言
                    save_to_db=True,
                )
                success = result.success
            except Exception as exc:
                self._logger.error(f"內容刷新出錯: {exc}")

        await self.emit(Events.AGENT_TASK_COMPLETED, {
            "agent": self.name,
            "task": "refresh_content",
            "product_id": str(product_id),
            "success": success,
        })
