# =============================================
# Agent Event Hooks
# =============================================
# 用途：API / Service 層調用，觸發 Agent 事件
# 設計：簡單函數，隱藏 EventBus 細節
# =============================================

import logging
from typing import Optional

logger = logging.getLogger(__name__)


def _get_event_bus():
    """延遲 import 避免循環依賴"""
    from app.agents import get_event_bus
    return get_event_bus()


async def on_product_created(product_id: str, sku: str = "", name: str = "") -> None:
    """商品新增後調用 — 觸發 Scout 搜索競品 + Writer 生成內容"""
    from app.agents.events import Events
    bus = _get_event_bus()
    await bus.emit(
        Events.PRODUCT_CREATED,
        payload={"product_id": product_id, "sku": sku, "name": name},
        source="api",
    )
    logger.info(f"Hook: product.created emitted for {product_id}")


async def on_product_updated(
    product_id: str,
    changed_fields: list[str],
) -> None:
    """商品更新後調用 — 觸發 Writer 判斷是否需刷新內容"""
    from app.agents.events import Events
    bus = _get_event_bus()
    await bus.emit(
        Events.PRODUCT_UPDATED,
        payload={"product_id": product_id, "changed_fields": changed_fields},
        source="api",
    )
    logger.info(f"Hook: product.updated emitted for {product_id}, fields={changed_fields}")


async def on_product_deleted(product_id: str) -> None:
    """商品刪除後調用"""
    from app.agents.events import Events
    bus = _get_event_bus()
    await bus.emit(
        Events.PRODUCT_DELETED,
        payload={"product_id": product_id},
        source="api",
    )


async def on_scrape_completed(
    competitor_id: str,
    alerts_created: int = 0,
    products_scraped: int = 0,
) -> None:
    """爬取完成後調用 — 觸發 Scout 分析價格變動"""
    from app.agents.events import Events
    bus = _get_event_bus()
    await bus.emit(
        Events.SCRAPE_COMPLETED,
        payload={
            "competitor_id": competitor_id,
            "alerts_created": alerts_created,
            "products_scraped": products_scraped,
        },
        source="scraper",
    )
    logger.info(
        f"Hook: scrape.completed emitted for competitor={competitor_id}, "
        f"alerts={alerts_created}"
    )


async def on_scrape_started(competitor_id: str) -> None:
    """爬取開始"""
    from app.agents.events import Events
    bus = _get_event_bus()
    await bus.emit(
        Events.SCRAPE_STARTED,
        payload={"competitor_id": competitor_id},
        source="scraper",
    )
