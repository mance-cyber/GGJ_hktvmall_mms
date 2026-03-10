# =============================================
# Telegram 通知管理 API
# =============================================

from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.config import get_settings
from app.models.database import get_db
from app.services.telegram import get_telegram_notifier, TelegramNotifier

logger = logging.getLogger(__name__)

router = APIRouter()


# =============================================
# Schema 定義
# =============================================

class TelegramConfigResponse(BaseModel):
    """Telegram 配置狀態"""
    enabled: bool
    bot_configured: bool
    chat_configured: bool
    bot_username: Optional[str] = None


class TelegramTestRequest(BaseModel):
    """測試消息請求"""
    message: str = Field(default="🔔 這是一條測試消息，來自 HKTVmall AI 系統")


class TelegramTestResponse(BaseModel):
    """測試響應"""
    success: bool
    message: str
    bot_info: Optional[dict] = None


class TelegramSendRequest(BaseModel):
    """發送自定義消息請求"""
    message: str = Field(..., min_length=1, max_length=4000)
    parse_mode: str = Field(default="HTML", pattern="^(HTML|Markdown)$")
    disable_notification: bool = Field(default=False)


class TelegramSendResponse(BaseModel):
    """發送響應"""
    success: bool
    message_id: Optional[int] = None
    error: Optional[str] = None


# =============================================
# API 端點
# =============================================

@router.get("/config", response_model=TelegramConfigResponse)
async def get_telegram_config():
    """
    獲取 Telegram 配置狀態

    返回當前 Telegram 通知的配置狀態（不暴露敏感信息）
    """
    settings = get_settings()
    notifier = get_telegram_notifier()

    bot_username = None

    # 如果配置了 bot，嘗試獲取 bot 信息
    if settings.telegram_bot_token:
        try:
            result = await notifier.test_connection()
            if result.get("ok"):
                bot_info = result.get("result", {})
                bot_username = bot_info.get("username")
        except Exception:
            pass

    return TelegramConfigResponse(
        enabled=notifier.enabled,
        bot_configured=bool(settings.telegram_bot_token),
        chat_configured=bool(settings.telegram_chat_id),
        bot_username=bot_username,
    )


@router.post("/test", response_model=TelegramTestResponse)
async def test_telegram_connection():
    """
    測試 Telegram Bot 連接

    驗證 Bot Token 是否有效，並返回 Bot 信息
    """
    settings = get_settings()

    if not settings.telegram_bot_token:
        return TelegramTestResponse(
            success=False,
            message="未配置 Telegram Bot Token，請在 .env 中設置 TELEGRAM_BOT_TOKEN"
        )

    notifier = get_telegram_notifier()
    result = await notifier.test_connection()

    if result.get("ok"):
        bot_info = result.get("result", {})
        return TelegramTestResponse(
            success=True,
            message=f"連接成功！Bot: @{bot_info.get('username')}",
            bot_info={
                "id": bot_info.get("id"),
                "username": bot_info.get("username"),
                "first_name": bot_info.get("first_name"),
                "can_join_groups": bot_info.get("can_join_groups"),
                "can_read_all_group_messages": bot_info.get("can_read_all_group_messages"),
            }
        )
    else:
        return TelegramTestResponse(
            success=False,
            message=f"連接失敗: {result.get('error', '未知錯誤')}"
        )


@router.post("/test-message", response_model=TelegramSendResponse)
async def send_test_message(request: TelegramTestRequest):
    """
    發送測試消息

    向配置的 Chat ID 發送一條測試消息
    """
    settings = get_settings()

    if not settings.telegram_bot_token:
        return TelegramSendResponse(
            success=False,
            error="未配置 Telegram Bot Token"
        )

    if not settings.telegram_chat_id:
        return TelegramSendResponse(
            success=False,
            error="未配置 Telegram Chat ID，請在 .env 中設置 TELEGRAM_CHAT_ID"
        )

    notifier = get_telegram_notifier()
    result = await notifier.send_message(request.message)

    if result.get("ok"):
        message_result = result.get("result", {})
        return TelegramSendResponse(
            success=True,
            message_id=message_result.get("message_id")
        )
    else:
        return TelegramSendResponse(
            success=False,
            error=result.get("error", "發送失敗")
        )


@router.post("/send", response_model=TelegramSendResponse)
async def send_custom_message(request: TelegramSendRequest):
    """
    發送自定義消息

    向配置的 Chat ID 發送自定義消息（支持 HTML/Markdown 格式）
    """
    notifier = get_telegram_notifier()

    if not notifier.enabled:
        return TelegramSendResponse(
            success=False,
            error="Telegram 通知未啟用，請檢查配置"
        )

    result = await notifier.send_message(
        text=request.message,
        parse_mode=request.parse_mode,
        disable_notification=request.disable_notification
    )

    if result.get("ok"):
        message_result = result.get("result", {})
        return TelegramSendResponse(
            success=True,
            message_id=message_result.get("message_id")
        )
    else:
        return TelegramSendResponse(
            success=False,
            error=result.get("error", "發送失敗")
        )


@router.post("/notify-test-scrape")
async def send_test_scrape_notification():
    """
    發送測試爬取完成通知

    模擬一次爬取完成的通知，用於測試通知格式
    """
    notifier = get_telegram_notifier()

    if not notifier.enabled:
        raise HTTPException(status_code=400, detail="Telegram 通知未啟用")

    result = await notifier.notify_scrape_complete(
        category_name="和牛（測試）",
        product_count=25,
        new_products=5,
        updated_products=20,
        duration_seconds=45.8
    )

    return {
        "success": result.get("ok", False),
        "message": "測試通知已發送" if result.get("ok") else result.get("error")
    }


@router.post("/notify-test-price-change")
async def send_test_price_change_notification():
    """
    發送測試價格變動通知

    模擬價格下降的通知，用於測試通知格式
    """
    from decimal import Decimal

    notifier = get_telegram_notifier()

    if not notifier.enabled:
        raise HTTPException(status_code=400, detail="Telegram 通知未啟用")

    result = await notifier.notify_price_drop(
        product_name="日本 A5 和牛西冷（測試）200g",
        old_price=Decimal("388.00"),
        new_price=Decimal("298.00"),
        category_name="和牛",
        product_url="https://www.hktvmall.com/p/H0000001"
    )

    return {
        "success": result.get("ok", False),
        "message": "測試通知已發送" if result.get("ok") else result.get("error")
    }


# =============================================
# 訂閱者管理
# =============================================

@router.get("/subscribers")
async def list_subscribers(db: AsyncSession = Depends(get_db)):
    """列出所有報告訂閱者"""
    from app.models.notification import ReportSubscriber
    from sqlalchemy import select

    result = await db.execute(
        select(ReportSubscriber).order_by(ReportSubscriber.subscribed_at.desc())
    )
    subscribers = result.scalars().all()

    return {
        "total": len(subscribers),
        "active": sum(1 for s in subscribers if s.is_active),
        "subscribers": [
            {
                "chat_id": s.chat_id,
                "username": s.username,
                "first_name": s.first_name,
                "is_active": s.is_active,
                "subscribed_at": s.subscribed_at.isoformat() if s.subscribed_at else None,
                "last_delivered_at": s.last_delivered_at.isoformat() if s.last_delivered_at else None,
            }
            for s in subscribers
        ],
    }


# =============================================
# Telegram Webhook 處理
# =============================================

class TelegramWebhookUpdate(BaseModel):
    """Telegram Webhook Update 結構"""
    update_id: int
    callback_query: Optional[Dict[str, Any]] = None
    message: Optional[Dict[str, Any]] = None


class CallbackResponse(BaseModel):
    """Callback 處理響應"""
    success: bool
    action: str
    message: str
    data: Optional[Dict[str, Any]] = None


@router.post("/webhook", include_in_schema=False)
async def telegram_webhook(
    update: TelegramWebhookUpdate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """
    Telegram Webhook 端點

    處理來自 Telegram 的 Webhook 更新，包括 Callback Query（按鈕點擊）
    """
    notifier = get_telegram_notifier()

    # 處理普通消息（/start, /subscribe, /stop）
    if update.message:
        msg = update.message
        text = (msg.get("text") or "").strip()
        chat = msg.get("chat", {})
        chat_id = str(chat.get("id", ""))
        from_user = msg.get("from", {})

        if text in ("/start", "/subscribe"):
            await _handle_subscribe(db, notifier, chat_id, from_user)
            return {"ok": True, "action": "subscribed"}

        elif text in ("/stop", "/unsubscribe"):
            await _handle_unsubscribe(db, notifier, chat_id)
            return {"ok": True, "action": "unsubscribed"}

    # 處理 Callback Query（按鈕點擊）
    if update.callback_query:
        callback = update.callback_query
        callback_id = callback.get("id")
        callback_data = callback.get("data", "")
        chat_id = str(callback.get("message", {}).get("chat", {}).get("id", ""))
        message_id = callback.get("message", {}).get("message_id")

        # 解析 callback_data
        try:
            result = await _handle_callback(
                db=db,
                notifier=notifier,
                callback_data=callback_data,
                chat_id=chat_id,
                message_id=message_id,
            )

            # 回應 Callback Query
            await notifier.answer_callback_query(
                callback_query_id=callback_id,
                text=result.get("toast_message", "操作已處理"),
                show_alert=result.get("show_alert", False)
            )

            return {"ok": True, "result": result}

        except Exception as e:
            logger.error(f"處理 Callback 失敗: {e}")
            await notifier.answer_callback_query(
                callback_query_id=callback_id,
                text=f"處理失敗: {str(e)[:50]}",
                show_alert=True
            )
            return {"ok": False, "error": str(e)}

    return {"ok": True}


async def _handle_subscribe(
    db: AsyncSession,
    notifier: TelegramNotifier,
    chat_id: str,
    from_user: dict,
):
    """處理 /start 或 /subscribe — 自動訂閱報告"""
    from app.models.notification import ReportSubscriber
    from sqlalchemy import select

    result = await db.execute(
        select(ReportSubscriber).where(ReportSubscriber.chat_id == chat_id)
    )
    existing = result.scalar_one_or_none()

    if existing:
        if not existing.is_active:
            existing.is_active = True
            existing.username = from_user.get("username") or existing.username
            existing.first_name = from_user.get("first_name") or existing.first_name
            await db.flush()
            await notifier.send_message(
                text="✅ 已重新訂閱 GoGoJap 競品報告！\n\n你會收到每日自動報告。\n發送 /stop 取消訂閱。",
                chat_id=chat_id,
            )
        else:
            await notifier.send_message(
                text="👋 你已經訂閱咗 GoGoJap 競品報告。\n\n發送 /stop 取消訂閱。",
                chat_id=chat_id,
            )
    else:
        import uuid
        from datetime import datetime, timezone
        sub = ReportSubscriber(
            id=uuid.uuid4(),
            chat_id=chat_id,
            username=from_user.get("username"),
            first_name=from_user.get("first_name"),
            is_active=True,
            subscribed_at=datetime.now(timezone.utc),
        )
        db.add(sub)
        await db.flush()
        await notifier.send_message(
            text=(
                "🎉 訂閱成功！歡迎使用 GoGoJap 競品監測系統。\n\n"
                "你會收到：\n"
                "• 每日競品價格報告\n"
                "• 重要價格變動通知\n\n"
                "發送 /stop 取消訂閱。"
            ),
            chat_id=chat_id,
        )

    logger.info(f"Subscriber {chat_id} ({from_user.get('username')}) subscribed")


async def _handle_unsubscribe(
    db: AsyncSession,
    notifier: TelegramNotifier,
    chat_id: str,
):
    """處理 /stop 或 /unsubscribe"""
    from app.models.notification import ReportSubscriber
    from sqlalchemy import select

    result = await db.execute(
        select(ReportSubscriber).where(ReportSubscriber.chat_id == chat_id)
    )
    existing = result.scalar_one_or_none()

    if existing and existing.is_active:
        existing.is_active = False
        await db.flush()
        await notifier.send_message(
            text="🔕 已取消訂閱。之後唔會再收到自動報告。\n\n想重新訂閱可以發送 /start。",
            chat_id=chat_id,
        )
    else:
        await notifier.send_message(
            text="你目前冇訂閱。發送 /start 訂閱報告。",
            chat_id=chat_id,
        )

    logger.info(f"Subscriber {chat_id} unsubscribed")


async def _handle_callback(
    db: AsyncSession,
    notifier: TelegramNotifier,
    callback_data: str,
    chat_id: str,
    message_id: int,
) -> Dict[str, Any]:
    """
    處理 Callback Query

    支持的回調：
    - create_proposal:{product_id} - 創建改價提案
    - approve_proposal:{proposal_id} - 批准提案
    - reject_proposal:{proposal_id} - 拒絕提案
    - view_alert:{product_id} - 查看告警詳情
    - view_proposal:{proposal_id} - 查看提案詳情
    - ignore_alert:{product_id} - 忽略告警
    """
    parts = callback_data.split(":", 1)
    action = parts[0]
    entity_id = parts[1] if len(parts) > 1 else ""

    if action == "create_proposal":
        return await _handle_create_proposal(db, notifier, entity_id, chat_id, message_id)
    elif action == "approve_proposal":
        return await _handle_approve_proposal(db, notifier, entity_id, chat_id, message_id)
    elif action == "reject_proposal":
        return await _handle_reject_proposal(db, notifier, entity_id, chat_id, message_id)
    elif action == "view_alert":
        return await _handle_view_alert(db, notifier, entity_id, chat_id)
    elif action == "view_proposal":
        return await _handle_view_proposal(db, notifier, entity_id, chat_id)
    elif action == "ignore_alert":
        return await _handle_ignore_alert(db, notifier, entity_id, chat_id, message_id)
    else:
        return {
            "action": "unknown",
            "toast_message": "未知操作",
            "show_alert": True
        }


async def _handle_create_proposal(
    db: AsyncSession,
    notifier: TelegramNotifier,
    product_id: str,
    chat_id: str,
    message_id: int,
) -> Dict[str, Any]:
    """處理創建改價提案按鈕"""
    from app.models.pricing import PriceProposal, SourceType, ProposalStatus
    from app.models.competitor import CompetitorProduct, PriceSnapshot
    from sqlalchemy import select
    from decimal import Decimal

    try:
        # 獲取產品最新價格信息
        product = await db.get(CompetitorProduct, UUID(product_id))
        if not product:
            return {
                "action": "create_proposal",
                "toast_message": "找不到產品",
                "show_alert": True
            }

        # 獲取最新快照
        snapshot_result = await db.execute(
            select(PriceSnapshot)
            .where(PriceSnapshot.competitor_product_id == UUID(product_id))
            .order_by(PriceSnapshot.scraped_at.desc())
            .limit(1)
        )
        snapshot = snapshot_result.scalar_one_or_none()

        current_price = snapshot.price if snapshot else None

        # 創建提案
        proposal = PriceProposal(
            product_id=None,  # 競品產品，暫無關聯本地產品
            current_price=current_price,
            proposed_price=current_price,  # 初始設為當前價格，待用戶調整
            reason=f"根據競品價格變動創建（來源：Telegram 快捷操作）\n競品產品：{product.name}",
            source_type=SourceType.TELEGRAM,
            status=ProposalStatus.PENDING,
        )

        db.add(proposal)
        await db.commit()
        await db.refresh(proposal)

        # 更新消息按鈕（移除創建按鈕，添加提案操作按鈕）
        new_buttons = [
            [
                {
                    "text": "✅ 批准提案",
                    "callback_data": f"approve_proposal:{proposal.id}"
                },
                {
                    "text": "❌ 拒絕提案",
                    "callback_data": f"reject_proposal:{proposal.id}"
                }
            ],
            [
                {
                    "text": "🔍 查看詳情",
                    "callback_data": f"view_proposal:{proposal.id}"
                }
            ]
        ]

        await notifier.edit_message_reply_markup(chat_id, message_id, new_buttons)

        return {
            "action": "create_proposal",
            "proposal_id": str(proposal.id),
            "toast_message": "✅ 改價提案已創建",
            "show_alert": False
        }

    except Exception as e:
        logger.error(f"創建提案失敗: {e}")
        return {
            "action": "create_proposal",
            "toast_message": f"創建失敗: {str(e)[:30]}",
            "show_alert": True
        }


async def _handle_approve_proposal(
    db: AsyncSession,
    notifier: TelegramNotifier,
    proposal_id: str,
    chat_id: str,
    message_id: int,
) -> Dict[str, Any]:
    """處理批准提案按鈕"""
    from app.models.pricing import PriceProposal, ProposalStatus
    from app.services.pricing_service import PricingService
    from datetime import datetime

    try:
        proposal = await db.get(PriceProposal, UUID(proposal_id))
        if not proposal:
            return {
                "action": "approve_proposal",
                "toast_message": "找不到提案",
                "show_alert": True
            }

        if proposal.status != ProposalStatus.PENDING:
            return {
                "action": "approve_proposal",
                "toast_message": f"提案已處理 ({proposal.status.value})",
                "show_alert": True
            }

        # 調用 PricingService 批准提案（自動執行改價）
        pricing_service = PricingService(db)
        try:
            approved_proposal = await pricing_service.approve_proposal(
                proposal_id=UUID(proposal_id),
                user_id="telegram_bot"
            )
        except Exception as e:
            logger.error(f"PricingService 批准提案失敗: {e}")
            return {
                "action": "approve_proposal",
                "toast_message": f"批准失敗: {str(e)[:30]}",
                "show_alert": True
            }

        # 移除按鈕
        await notifier.edit_message_reply_markup(chat_id, message_id, None)

        # 發送確認消息（根據執行結果）
        if approved_proposal.status == ProposalStatus.EXECUTED:
            message = (
                f"✅ <b>提案已批准並執行</b>\n\n"
                f"提案編號: {proposal_id[:8]}...\n"
                f"新價格: HK${float(approved_proposal.final_price):.2f}\n\n"
                f"價格已更新至 HKTVmall 🎉"
            )
        elif approved_proposal.status == ProposalStatus.FAILED:
            message = (
                f"⚠️ <b>提案已批准但執行失敗</b>\n\n"
                f"提案編號: {proposal_id[:8]}...\n"
                f"錯誤: {approved_proposal.error_message or '未知錯誤'}\n\n"
                f"請手動檢查並執行"
            )
        else:
            message = (
                f"✅ <b>提案已批准</b>\n\n"
                f"提案編號: {proposal_id[:8]}...\n\n"
                f"狀態: {approved_proposal.status.value}"
            )

        await notifier.send_message(
            text=message,
            chat_id=chat_id
        )

        return {
            "action": "approve_proposal",
            "toast_message": "✅ 提案已批准並執行",
            "show_alert": False
        }

    except Exception as e:
        logger.error(f"批准提案失敗: {e}")
        return {
            "action": "approve_proposal",
            "toast_message": f"操作失敗: {str(e)[:30]}",
            "show_alert": True
        }


async def _handle_reject_proposal(
    db: AsyncSession,
    notifier: TelegramNotifier,
    proposal_id: str,
    chat_id: str,
    message_id: int,
) -> Dict[str, Any]:
    """處理拒絕提案按鈕"""
    from app.models.pricing import PriceProposal, ProposalStatus
    from app.services.pricing_service import PricingService
    from datetime import datetime

    try:
        proposal = await db.get(PriceProposal, UUID(proposal_id))
        if not proposal:
            return {
                "action": "reject_proposal",
                "toast_message": "找不到提案",
                "show_alert": True
            }

        if proposal.status != ProposalStatus.PENDING:
            return {
                "action": "reject_proposal",
                "toast_message": f"提案已處理 ({proposal.status.value})",
                "show_alert": True
            }

        # 調用 PricingService 拒絕提案
        pricing_service = PricingService(db)
        try:
            await pricing_service.reject_proposal(
                proposal_id=UUID(proposal_id),
                user_id="telegram_bot"
            )
        except Exception as e:
            logger.error(f"PricingService 拒絕提案失敗: {e}")
            return {
                "action": "reject_proposal",
                "toast_message": f"拒絕失敗: {str(e)[:30]}",
                "show_alert": True
            }

        # 移除按鈕
        await notifier.edit_message_reply_markup(chat_id, message_id, None)

        # 發送確認消息
        await notifier.send_message(
            text=f"❌ <b>提案已拒絕</b>\n\n提案編號: {proposal_id[:8]}...",
            chat_id=chat_id
        )

        return {
            "action": "reject_proposal",
            "toast_message": "❌ 提案已拒絕",
            "show_alert": False
        }

    except Exception as e:
        logger.error(f"拒絕提案失敗: {e}")
        return {
            "action": "reject_proposal",
            "toast_message": f"操作失敗: {str(e)[:30]}",
            "show_alert": True
        }


async def _handle_view_alert(
    db: AsyncSession,
    notifier: TelegramNotifier,
    product_id: str,
    chat_id: str,
) -> Dict[str, Any]:
    """處理查看告警詳情按鈕"""
    from app.models.competitor import CompetitorProduct, PriceSnapshot, PriceAlert
    from sqlalchemy import select

    try:
        product = await db.get(CompetitorProduct, UUID(product_id))
        if not product:
            return {
                "action": "view_alert",
                "toast_message": "找不到產品",
                "show_alert": True
            }

        # 獲取最近的價格快照
        snapshots_result = await db.execute(
            select(PriceSnapshot)
            .where(PriceSnapshot.competitor_product_id == UUID(product_id))
            .order_by(PriceSnapshot.scraped_at.desc())
            .limit(5)
        )
        snapshots = snapshots_result.scalars().all()

        # 構建詳情消息
        message_parts = [
            f"<b>🔍 產品詳情</b>",
            "",
            f"🏷 <b>名稱</b>: {product.name or '未知'}",
            f"🔗 <b>SKU</b>: {product.sku or '無'}",
            f"📅 <b>最後更新</b>: {product.last_scraped_at.strftime('%Y-%m-%d %H:%M') if product.last_scraped_at else '未知'}",
            "",
            "<b>📊 價格歷史（最近5筆）</b>",
        ]

        for i, snapshot in enumerate(snapshots):
            price_str = f"HK${float(snapshot.price):.2f}" if snapshot.price else "無"
            time_str = snapshot.scraped_at.strftime('%m/%d %H:%M') if snapshot.scraped_at else ""
            message_parts.append(f"• {time_str}: {price_str}")

        if product.url:
            message_parts.append("")
            message_parts.append(f'🔗 <a href="{product.url}">查看原網頁</a>')

        await notifier.send_message(
            text="\n".join(message_parts),
            chat_id=chat_id
        )

        return {
            "action": "view_alert",
            "toast_message": "詳情已發送",
            "show_alert": False
        }

    except Exception as e:
        logger.error(f"查看告警詳情失敗: {e}")
        return {
            "action": "view_alert",
            "toast_message": f"查詢失敗: {str(e)[:30]}",
            "show_alert": True
        }


async def _handle_view_proposal(
    db: AsyncSession,
    notifier: TelegramNotifier,
    proposal_id: str,
    chat_id: str,
) -> Dict[str, Any]:
    """處理查看提案詳情按鈕"""
    from app.models.pricing import PriceProposal

    try:
        proposal = await db.get(PriceProposal, UUID(proposal_id))
        if not proposal:
            return {
                "action": "view_proposal",
                "toast_message": "找不到提案",
                "show_alert": True
            }

        # 構建詳情消息
        message_parts = [
            f"<b>📋 提案詳情</b>",
            "",
            f"🆔 <b>編號</b>: {proposal_id[:8]}...",
            f"📊 <b>狀態</b>: {proposal.status}",
            f"💰 <b>當前價格</b>: HK${float(proposal.current_price):.2f}" if proposal.current_price else "💰 <b>當前價格</b>: 無",
            f"💵 <b>建議價格</b>: HK${float(proposal.proposed_price):.2f}" if proposal.proposed_price else "💵 <b>建議價格</b>: 待設定",
            f"📝 <b>來源</b>: {proposal.source_type}",
            f"📅 <b>創建時間</b>: {proposal.created_at.strftime('%Y-%m-%d %H:%M') if proposal.created_at else '未知'}",
        ]

        if proposal.reason:
            message_parts.append("")
            message_parts.append(f"<b>📌 原因</b>:")
            message_parts.append(proposal.reason[:200])

        await notifier.send_message(
            text="\n".join(message_parts),
            chat_id=chat_id
        )

        return {
            "action": "view_proposal",
            "toast_message": "詳情已發送",
            "show_alert": False
        }

    except Exception as e:
        logger.error(f"查看提案詳情失敗: {e}")
        return {
            "action": "view_proposal",
            "toast_message": f"查詢失敗: {str(e)[:30]}",
            "show_alert": True
        }


async def _handle_ignore_alert(
    db: AsyncSession,
    notifier: TelegramNotifier,
    product_id: str,
    chat_id: str,
    message_id: int,
) -> Dict[str, Any]:
    """處理忽略告警按鈕"""
    # 移除按鈕，標記為已忽略
    await notifier.edit_message_reply_markup(chat_id, message_id, None)

    return {
        "action": "ignore_alert",
        "toast_message": "⏸ 告警已忽略",
        "show_alert": False
    }


# =============================================
# 設置指南
# =============================================

@router.get("/setup-guide")
async def get_setup_guide():
    """
    獲取 Telegram Bot 設置指南

    返回如何創建和配置 Telegram Bot 的步驟說明
    """
    return {
        "title": "Telegram Bot 設置指南",
        "steps": [
            {
                "step": 1,
                "title": "創建 Telegram Bot",
                "instructions": [
                    "在 Telegram 中搜索 @BotFather",
                    "發送 /newbot 命令",
                    "按提示設置 Bot 名稱和用戶名",
                    "獲取 Bot Token（類似: 123456789:ABCdefGHI...）"
                ]
            },
            {
                "step": 2,
                "title": "獲取 Chat ID",
                "instructions": [
                    "方法一：向 Bot 發送任意消息，然後訪問 https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates",
                    "方法二：搜索 @userinfobot 並發送 /start 獲取您的 User ID",
                    "如果是群組，將 Bot 添加到群組並獲取群組 Chat ID"
                ]
            },
            {
                "step": 3,
                "title": "配置環境變數",
                "instructions": [
                    "在 .env 文件中添加以下配置：",
                    "TELEGRAM_BOT_TOKEN=your_bot_token_here",
                    "TELEGRAM_CHAT_ID=your_chat_id_here",
                    "TELEGRAM_ENABLED=true"
                ]
            },
            {
                "step": 4,
                "title": "測試連接",
                "instructions": [
                    "調用 POST /api/v1/telegram/test 測試 Bot 連接",
                    "調用 POST /api/v1/telegram/test-message 發送測試消息",
                    "確認收到 Telegram 消息即表示配置成功"
                ]
            },
            {
                "step": 5,
                "title": "設置 Webhook（可選，用於接收按鈕點擊回調）",
                "instructions": [
                    "部署應用到公網可訪問的地址",
                    "調用 Telegram API 設置 Webhook：",
                    "POST https://api.telegram.org/bot<TOKEN>/setWebhook",
                    "body: {\"url\": \"https://your-domain.com/api/v1/telegram/webhook\"}"
                ]
            }
        ],
        "env_example": {
            "TELEGRAM_BOT_TOKEN": "123456789:ABCdefGHIjklMNOpqrsTUVwxyz",
            "TELEGRAM_CHAT_ID": "987654321",
            "TELEGRAM_ENABLED": "true"
        }
    }
