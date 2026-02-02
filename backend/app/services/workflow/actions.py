# =============================================
# Workflow Actions
# 工作流執行器 - 處理具體業務動作
# =============================================

import logging
from typing import Any, Dict, Optional
from decimal import Decimal
from datetime import datetime, timedelta
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.pricing import PriceProposal, ProposalStatus, ProposalType, SourceType
from app.models.product import Product
from app.services.telegram import TelegramNotifier, get_telegram_notifier

logger = logging.getLogger(__name__)


@dataclass
class ActionResult:
    """動作執行結果"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None


class ActionExecutor:
    """
    動作執行器

    負責執行工作流中嘅具體業務動作：
    - 創建改價提案
    - 發送 Telegram 通知
    - 其他業務動作（未來擴展）
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self._telegram: Optional[TelegramNotifier] = None

    @property
    def telegram(self) -> TelegramNotifier:
        """懶加載 Telegram 通知器"""
        if self._telegram is None:
            self._telegram = get_telegram_notifier()
        return self._telegram


# =============================================
# 改價提案動作
# =============================================

async def create_pricing_proposal(
    db: AsyncSession,
    conversation_id: Optional[str] = None,
    product_id: Optional[str] = None,
    proposed_price: Optional[float] = None,
    reason: Optional[str] = None,
    assigned_to: Optional[str] = None,
    due_date: Optional[datetime] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    創建改價提案（由 AI 對話觸發）

    Args:
        db: 數據庫 session
        conversation_id: 來源對話 ID
        product_id: 產品 ID
        proposed_price: 建議價格
        reason: AI 建議原因
        assigned_to: 指定審批人 UUID
        due_date: 審批期限

    Returns:
        Dict 包含 proposal_id, product_name, status 等
    """
    if not product_id:
        raise ValueError("product_id is required")
    if proposed_price is None:
        raise ValueError("proposed_price is required")

    # 1. 獲取產品信息
    from uuid import UUID
    product_uuid = UUID(product_id) if isinstance(product_id, str) else product_id

    product = await db.get(Product, product_uuid)
    if not product:
        raise ValueError(f"Product {product_id} not found")

    current_price = product.price

    # 2. 檢查是否已有待審批提案
    existing_query = select(PriceProposal).where(
        PriceProposal.product_id == product_uuid,
        PriceProposal.status == ProposalStatus.PENDING
    )
    existing_result = await db.execute(existing_query)
    existing_proposal = existing_result.scalar_one_or_none()

    if existing_proposal:
        logger.warning(f"Product {product_id} already has pending proposal {existing_proposal.id}")
        return {
            "success": False,
            "message": "產品已有待審批提案",
            "existing_proposal_id": str(existing_proposal.id)
        }

    # 3. 創建提案
    assigned_uuid = None
    if assigned_to:
        assigned_uuid = UUID(assigned_to) if isinstance(assigned_to, str) else assigned_to

    proposal = PriceProposal(
        product_id=product_uuid,
        proposal_type=ProposalType.PRICE_UPDATE,
        status=ProposalStatus.PENDING,
        current_price=current_price,
        proposed_price=Decimal(str(proposed_price)),
        reason=reason or "AI 對話建議",
        ai_model_used="claude-agent",
        # Workflow 擴展欄位
        source_conversation_id=conversation_id,
        source_type=SourceType.AI_SUGGESTION,
        assigned_to=assigned_uuid,
        due_date=due_date,
        reminder_sent=False
    )

    db.add(proposal)
    await db.commit()
    await db.refresh(proposal)

    logger.info(
        f"Created pricing proposal {proposal.id} for product {product.sku}, "
        f"conversation_id={conversation_id}"
    )

    return {
        "success": True,
        "message": "改價提案已創建",
        "proposal_id": str(proposal.id),
        "product_id": str(product.id),
        "product_name": product.name,
        "product_sku": product.sku,
        "current_price": float(current_price) if current_price else None,
        "proposed_price": float(proposed_price),
        "source_type": SourceType.AI_SUGGESTION
    }


# =============================================
# Telegram 通知動作
# =============================================

async def send_telegram_notification(
    db: AsyncSession,
    conversation_id: Optional[str] = None,
    notification_type: str = "general",
    **kwargs
) -> Dict[str, Any]:
    """
    發送 Telegram 通知

    Args:
        db: 數據庫 session（保持接口一致）
        conversation_id: 來源對話 ID
        notification_type: 通知類型
            - "proposal_created": 新提案創建
            - "alert_triggered": 告警觸發
            - "report_ready": 報告生成完成
            - "general": 通用消息
        **kwargs: 依通知類型不同嘅參數

    Returns:
        Dict 包含 success, message_id 等
    """
    notifier = get_telegram_notifier()

    if notification_type == "proposal_created":
        return await _send_proposal_notification(notifier, **kwargs)
    elif notification_type == "alert_triggered":
        return await _send_alert_notification(notifier, **kwargs)
    elif notification_type == "report_ready":
        return await _send_report_notification(notifier, **kwargs)
    else:
        # 通用消息
        message = kwargs.get("message", "")
        if not message:
            return {"success": False, "message": "No message provided"}

        result = await notifier.send_message(message)
        return {
            "success": result.get("ok", False),
            "message_id": result.get("result", {}).get("message_id"),
            "error": result.get("error")
        }


async def _send_proposal_notification(
    notifier: TelegramNotifier,
    product_name: str = "",
    product_sku: str = "",
    current_price: float = 0,
    proposed_price: float = 0,
    reason: str = "",
    proposal_id: str = "",
    conversation_id: str = "",
    **kwargs
) -> Dict[str, Any]:
    """發送改價提案通知"""
    price_change = proposed_price - current_price
    change_percent = (price_change / current_price * 100) if current_price > 0 else 0
    change_emoji = "📉" if price_change < 0 else "📈"

    message = f"""
<b>🤖 AI 改價建議</b>

🏷 <b>產品</b>: {notifier._escape_html(product_name[:50])}
📦 <b>SKU</b>: {product_sku}
💰 <b>現價</b>: HK${current_price:.2f}
💵 <b>建議價</b>: HK${proposed_price:.2f}
{change_emoji} <b>變動</b>: {'+' if price_change > 0 else ''}HK${price_change:.2f} ({change_percent:+.1f}%)

📝 <b>原因</b>:
{notifier._escape_html(reason[:200]) if reason else '未提供'}

🔗 <a href="https://app.gogojap.com/pricing-approval">前往審批</a>
""".strip()

    result = await notifier.send_message(message)

    return {
        "success": result.get("ok", False),
        "message_id": result.get("result", {}).get("message_id"),
        "notification_type": "proposal_created",
        "error": result.get("error")
    }


async def _send_alert_notification(
    notifier: TelegramNotifier,
    alert_type: str = "",
    product_name: str = "",
    alert_message: str = "",
    analysis_summary: str = "",
    **kwargs
) -> Dict[str, Any]:
    """發送告警通知"""
    alert_emoji = {
        "price_drop": "📉",
        "price_increase": "📈",
        "competitor_change": "🔔",
        "stock_warning": "📦"
    }.get(alert_type, "⚠️")

    message = f"""
<b>{alert_emoji} 價格告警</b>

🏷 <b>產品</b>: {notifier._escape_html(product_name[:50])}
📝 <b>告警</b>: {notifier._escape_html(alert_message[:200])}
""".strip()

    if analysis_summary:
        message += f"\n\n🤖 <b>AI 分析</b>:\n{notifier._escape_html(analysis_summary[:300])}"

    result = await notifier.send_message(message)

    return {
        "success": result.get("ok", False),
        "message_id": result.get("result", {}).get("message_id"),
        "notification_type": "alert_triggered",
        "error": result.get("error")
    }


async def _send_report_notification(
    notifier: TelegramNotifier,
    report_type: str = "",
    report_title: str = "",
    summary: str = "",
    report_url: str = "",
    **kwargs
) -> Dict[str, Any]:
    """發送報告完成通知"""
    message = f"""
<b>📊 排程報告已生成</b>

📋 <b>報告</b>: {notifier._escape_html(report_title[:50])}
📝 <b>類型</b>: {report_type}

<b>摘要</b>:
{notifier._escape_html(summary[:400]) if summary else '無摘要'}
""".strip()

    if report_url:
        message += f'\n\n🔗 <a href="{report_url}">查看完整報告</a>'

    result = await notifier.send_message(message)

    return {
        "success": result.get("ok", False),
        "message_id": result.get("result", {}).get("message_id"),
        "notification_type": "report_ready",
        "error": result.get("error")
    }


# =============================================
# 工作流觸發器處理函數
# =============================================

async def handle_pricing_approval_trigger(
    db: AsyncSession,
    conversation_id: Optional[str] = None,
    product_id: Optional[str] = None,
    proposed_price: Optional[float] = None,
    reason: Optional[str] = None,
    send_notification: bool = True,
    **kwargs
) -> Dict[str, Any]:
    """
    處理改價審批工作流觸發

    完整流程：
    1. 創建改價提案
    2. 發送 Telegram 通知（可選）

    Returns:
        完整執行結果
    """
    results = {
        "proposal": None,
        "notification": None,
        "success": False
    }

    # Step 1: 創建提案
    try:
        proposal_result = await create_pricing_proposal(
            db=db,
            conversation_id=conversation_id,
            product_id=product_id,
            proposed_price=proposed_price,
            reason=reason,
            **kwargs
        )
        results["proposal"] = proposal_result

        if not proposal_result.get("success"):
            results["error"] = proposal_result.get("message")
            return results

    except Exception as e:
        logger.error(f"Failed to create proposal: {e}")
        results["error"] = str(e)
        return results

    # Step 2: 發送通知（如果啟用）
    if send_notification:
        try:
            notification_result = await send_telegram_notification(
                db=db,
                conversation_id=conversation_id,
                notification_type="proposal_created",
                product_name=proposal_result.get("product_name", ""),
                product_sku=proposal_result.get("product_sku", ""),
                current_price=proposal_result.get("current_price", 0),
                proposed_price=proposal_result.get("proposed_price", 0),
                reason=reason,
                proposal_id=proposal_result.get("proposal_id", ""),
            )
            results["notification"] = notification_result
        except Exception as e:
            logger.warning(f"Failed to send notification: {e}")
            results["notification"] = {"success": False, "error": str(e)}

    results["success"] = True
    return results
