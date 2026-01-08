# =============================================
# Telegram 通知管理 API
# =============================================

from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import logging

from app.config import get_settings
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
            }
        ],
        "env_example": {
            "TELEGRAM_BOT_TOKEN": "123456789:ABCdefGHIjklMNOpqrsTUVwxyz",
            "TELEGRAM_CHAT_ID": "987654321",
            "TELEGRAM_ENABLED": "true"
        }
    }
