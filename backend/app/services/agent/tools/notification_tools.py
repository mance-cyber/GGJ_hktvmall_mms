# =============================================
# 通知工具
# 發送 Telegram 通知
# =============================================

from typing import Any, Dict, Optional

from .base import BaseTool, ToolResult


class NotificationSendTool(BaseTool):
    """
    通知發送工具

    發送 Telegram 通知，支持自定義消息或預設模板
    """

    name = "notification_send"
    description = "發送 Telegram 通知，支持自定義消息或預設模板"
    requires_db = False  # 不需要數據庫連接

    parameters = {
        "message_type": {
            "type": "str",
            "description": "消息類型: custom (自定義), daily_summary (每日摘要), price_alert (價格警報), error (錯誤通知)",
            "required": True
        },
        "content": {
            "type": "str",
            "description": "自定義消息內容（message_type=custom 時必填）",
            "required": False
        },
        "title": {
            "type": "str",
            "description": "消息標題（可選）",
            "required": False
        }
    }

    def __init__(self, db=None):
        # 不需要 db，但保持接口一致
        super().__init__(db)

    async def execute(self, **kwargs) -> ToolResult:
        """執行通知發送"""
        message_type = kwargs.get("message_type", "custom")
        content = kwargs.get("content", "")
        title = kwargs.get("title", "")

        # 延遲導入，避免循環依賴
        try:
            from app.services.telegram import get_telegram_notifier
        except ImportError:
            return ToolResult(
                tool_name=self.name,
                success=False,
                error="無法載入 Telegram 服務"
            )

        notifier = get_telegram_notifier()

        if not notifier or not notifier.enabled:
            return ToolResult(
                tool_name=self.name,
                success=False,
                error="Telegram 通知服務未配置或未啟用。請在設定中配置 TELEGRAM_BOT_TOKEN 和 TELEGRAM_CHAT_ID。"
            )

        try:
            if message_type == "custom":
                # 發送自定義消息
                if not content:
                    return ToolResult(
                        tool_name=self.name,
                        success=False,
                        error="自定義消息需要提供 content 參數"
                    )

                # 格式化消息
                if title:
                    formatted_message = f"📢 <b>{title}</b>\n\n{content}"
                else:
                    formatted_message = f"📢 <b>AI 助手通知</b>\n\n{content}"

                result = await notifier.send_message(
                    text=formatted_message,
                    parse_mode="HTML"
                )

            elif message_type == "daily_summary":
                # 發送每日摘要（使用預設模板）
                # 這裡簡化處理，實際可以整合其他工具數據
                result = await notifier.send_message(
                    text=content or "📊 每日摘要通知已觸發",
                    parse_mode="HTML"
                )

            elif message_type == "price_alert":
                # 發送價格警報通知
                result = await notifier.send_message(
                    text=f"📉 <b>價格警報</b>\n\n{content}" if content else "價格警報通知",
                    parse_mode="HTML"
                )

            elif message_type == "error":
                # 發送錯誤通知
                result = await notifier.send_message(
                    text=f"⚠️ <b>系統警告</b>\n\n{content}" if content else "系統警告通知",
                    parse_mode="HTML"
                )

            else:
                return ToolResult(
                    tool_name=self.name,
                    success=False,
                    error=f"不支援的消息類型: {message_type}"
                )

            # 檢查發送結果
            if result.get("ok"):
                return ToolResult(
                    tool_name=self.name,
                    success=True,
                    data={
                        "type": "notification_send",
                        "message_type": message_type,
                        "message_id": result.get("result", {}).get("message_id"),
                        "message": "Telegram 通知已發送成功"
                    }
                )
            else:
                return ToolResult(
                    tool_name=self.name,
                    success=False,
                    error=f"發送失敗: {result.get('description', '未知錯誤')}"
                )

        except Exception as e:
            return ToolResult(
                tool_name=self.name,
                success=False,
                error=f"通知發送失敗: {str(e)}"
            )
