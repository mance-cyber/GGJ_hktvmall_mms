# =============================================
# Telegram 通知服務
# =============================================
# 用途：向管理者發送系統通知
# 場景：價格變動、爬取完成、錯誤警告等
# =============================================

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from decimal import Decimal

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Telegram 通知服務"""

    BASE_URL = "https://api.telegram.org/bot{token}"

    def __init__(self, bot_token: Optional[str] = None, chat_id: Optional[str] = None):
        settings = get_settings()
        self.bot_token = bot_token or settings.telegram_bot_token
        self.chat_id = chat_id or settings.telegram_chat_id
        self.enabled = settings.telegram_enabled and bool(self.bot_token) and bool(self.chat_id)

        if self.enabled:
            self.api_url = self.BASE_URL.format(token=self.bot_token)
            logger.info("Telegram 通知服務已啟用")
        else:
            self.api_url = ""
            logger.info("Telegram 通知服務未啟用（缺少配置）")

    # ==================== 核心發送方法 ====================

    async def send_message_with_buttons(
        self,
        text: str,
        buttons: List[List[Dict[str, str]]],
        parse_mode: str = "HTML",
        disable_notification: bool = False,
        chat_id: Optional[str] = None
    ) -> dict:
        """
        發送帶有 Inline Keyboard 按鈕的消息

        Args:
            text: 消息內容（支援 HTML 格式）
            buttons: 按鈕配置，二維列表
                     每行是一個列表 [{"text": "按鈕文字", "callback_data": "callback_id"}]
            parse_mode: 解析模式 (HTML / Markdown)
            disable_notification: 是否靜音發送
            chat_id: 指定聊天 ID（覆蓋默認值）

        Returns:
            Telegram API 響應
        """
        if not self.enabled:
            logger.warning("Telegram 未啟用，消息未發送")
            return {"ok": False, "error": "Telegram 未啟用"}

        target_chat = chat_id or self.chat_id
        url = f"{self.api_url}/sendMessage"

        # 構建 Inline Keyboard
        inline_keyboard = []
        for row in buttons:
            keyboard_row = []
            for btn in row:
                keyboard_row.append({
                    "text": btn.get("text", ""),
                    "callback_data": btn.get("callback_data", "")
                })
            inline_keyboard.append(keyboard_row)

        payload = {
            "chat_id": target_chat,
            "text": text,
            "parse_mode": parse_mode,
            "disable_notification": disable_notification,
            "reply_markup": {
                "inline_keyboard": inline_keyboard
            }
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload)
                result = response.json()

                if not result.get("ok"):
                    logger.error(f"Telegram 發送失敗: {result}")
                else:
                    logger.info(f"Telegram 消息（帶按鈕）已發送至 {target_chat}")

                return result

        except httpx.TimeoutException:
            logger.error("Telegram API 請求超時")
            return {"ok": False, "error": "請求超時"}
        except Exception as e:
            logger.error(f"Telegram 發送異常: {e}")
            return {"ok": False, "error": str(e)}

    async def answer_callback_query(
        self,
        callback_query_id: str,
        text: Optional[str] = None,
        show_alert: bool = False
    ) -> dict:
        """
        回應 Callback Query（按鈕點擊）

        Args:
            callback_query_id: Callback Query ID
            text: 顯示給用戶的提示文字
            show_alert: 是否以彈窗形式顯示

        Returns:
            Telegram API 響應
        """
        if not self.enabled:
            return {"ok": False, "error": "Telegram 未啟用"}

        url = f"{self.api_url}/answerCallbackQuery"

        payload = {
            "callback_query_id": callback_query_id,
            "show_alert": show_alert
        }
        if text:
            payload["text"] = text

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, json=payload)
                return response.json()
        except Exception as e:
            logger.error(f"Telegram 回應 Callback 失敗: {e}")
            return {"ok": False, "error": str(e)}

    async def edit_message_reply_markup(
        self,
        chat_id: str,
        message_id: int,
        buttons: Optional[List[List[Dict[str, str]]]] = None
    ) -> dict:
        """
        編輯消息的按鈕（用於禁用已點擊的按鈕）

        Args:
            chat_id: 聊天 ID
            message_id: 消息 ID
            buttons: 新的按鈕配置（None 則移除所有按鈕）

        Returns:
            Telegram API 響應
        """
        if not self.enabled:
            return {"ok": False, "error": "Telegram 未啟用"}

        url = f"{self.api_url}/editMessageReplyMarkup"

        payload = {
            "chat_id": chat_id,
            "message_id": message_id
        }

        if buttons:
            inline_keyboard = []
            for row in buttons:
                keyboard_row = []
                for btn in row:
                    keyboard_row.append({
                        "text": btn.get("text", ""),
                        "callback_data": btn.get("callback_data", "")
                    })
                inline_keyboard.append(keyboard_row)
            payload["reply_markup"] = {"inline_keyboard": inline_keyboard}
        else:
            payload["reply_markup"] = {"inline_keyboard": []}

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, json=payload)
                return response.json()
        except Exception as e:
            logger.error(f"Telegram 編輯按鈕失敗: {e}")
            return {"ok": False, "error": str(e)}

    async def send_message(
        self,
        text: str,
        parse_mode: str = "HTML",
        disable_notification: bool = False,
        chat_id: Optional[str] = None
    ) -> dict:
        """
        發送 Telegram 消息

        Args:
            text: 消息內容（支援 HTML 格式）
            parse_mode: 解析模式 (HTML / Markdown)
            disable_notification: 是否靜音發送
            chat_id: 指定聊天 ID（覆蓋默認值）

        Returns:
            Telegram API 響應
        """
        if not self.enabled:
            logger.warning("Telegram 未啟用，消息未發送")
            return {"ok": False, "error": "Telegram 未啟用"}

        target_chat = chat_id or self.chat_id
        url = f"{self.api_url}/sendMessage"

        payload = {
            "chat_id": target_chat,
            "text": text,
            "parse_mode": parse_mode,
            "disable_notification": disable_notification
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload)
                result = response.json()

                if not result.get("ok"):
                    logger.error(f"Telegram 發送失敗: {result}")
                else:
                    logger.info(f"Telegram 消息已發送至 {target_chat}")

                return result

        except httpx.TimeoutException:
            logger.error("Telegram API 請求超時")
            return {"ok": False, "error": "請求超時"}
        except Exception as e:
            logger.error(f"Telegram 發送異常: {e}")
            return {"ok": False, "error": str(e)}

    async def test_connection(self) -> dict:
        """測試 Telegram 連接"""
        if not self.bot_token:
            return {"ok": False, "error": "未配置 Bot Token"}

        url = f"{self.api_url}/getMe"

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                result = response.json()

                if result.get("ok"):
                    bot_info = result.get("result", {})
                    logger.info(f"Telegram Bot 連接成功: @{bot_info.get('username')}")

                return result

        except Exception as e:
            logger.error(f"Telegram 連接測試失敗: {e}")
            return {"ok": False, "error": str(e)}

    # ==================== 業務通知方法 ====================

    async def notify_scrape_complete(
        self,
        category_name: str,
        product_count: int,
        new_products: int = 0,
        updated_products: int = 0,
        duration_seconds: float = 0
    ) -> dict:
        """
        通知：類別爬取完成

        Args:
            category_name: 類別名稱
            product_count: 總產品數
            new_products: 新增產品數
            updated_products: 更新產品數
            duration_seconds: 耗時（秒）
        """
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        duration_str = f"{duration_seconds:.1f}秒" if duration_seconds else "未知"

        message = f"""
<b>✅ 類別爬取完成</b>

📦 <b>類別</b>: {self._escape_html(category_name)}
📊 <b>產品數</b>: {product_count}
🆕 <b>新增</b>: {new_products}
🔄 <b>更新</b>: {updated_products}
⏱ <b>耗時</b>: {duration_str}
🕐 <b>時間</b>: {now}
"""
        return await self.send_message(message.strip())

    async def notify_price_drop(
        self,
        product_name: str,
        old_price: Decimal,
        new_price: Decimal,
        category_name: str = "",
        product_url: str = ""
    ) -> dict:
        """
        通知：價格下降

        Args:
            product_name: 產品名稱
            old_price: 原價格
            new_price: 新價格
            category_name: 類別名稱
            product_url: 產品連結
        """
        drop_amount = old_price - new_price
        drop_percent = (drop_amount / old_price * 100) if old_price > 0 else 0

        message = f"""
<b>📉 價格下降提醒</b>

🏷 <b>產品</b>: {self._escape_html(product_name[:50])}
📁 <b>類別</b>: {self._escape_html(category_name) if category_name else "未知"}
💰 <b>原價</b>: HK${old_price:.2f}
💵 <b>現價</b>: HK${new_price:.2f}
📉 <b>降幅</b>: -HK${drop_amount:.2f} ({drop_percent:.1f}%)
"""
        if product_url:
            message += f'\n🔗 <a href="{product_url}">查看產品</a>'

        return await self.send_message(message.strip())

    async def notify_price_increase(
        self,
        product_name: str,
        old_price: Decimal,
        new_price: Decimal,
        category_name: str = "",
        product_url: str = ""
    ) -> dict:
        """
        通知：價格上升
        """
        increase_amount = new_price - old_price
        increase_percent = (increase_amount / old_price * 100) if old_price > 0 else 0

        message = f"""
<b>📈 價格上升提醒</b>

🏷 <b>產品</b>: {self._escape_html(product_name[:50])}
📁 <b>類別</b>: {self._escape_html(category_name) if category_name else "未知"}
💰 <b>原價</b>: HK${old_price:.2f}
💵 <b>現價</b>: HK${new_price:.2f}
📈 <b>漲幅</b>: +HK${increase_amount:.2f} ({increase_percent:.1f}%)
"""
        if product_url:
            message += f'\n🔗 <a href="{product_url}">查看產品</a>'

        return await self.send_message(message.strip())

    async def notify_significant_price_changes(
        self,
        category_name: str,
        changes: list[dict],
        threshold_percent: float = 10.0
    ) -> dict:
        """
        通知：批量顯著價格變動

        Args:
            category_name: 類別名稱
            changes: 價格變動列表 [{"name": str, "old": Decimal, "new": Decimal, "url": str}]
            threshold_percent: 觸發閾值（百分比）
        """
        if not changes:
            return {"ok": True, "message": "無顯著價格變動"}

        drops = []
        increases = []

        for item in changes:
            old_price = item.get("old", 0)
            new_price = item.get("new", 0)
            if old_price == 0:
                continue

            change_percent = ((new_price - old_price) / old_price) * 100

            if abs(change_percent) >= threshold_percent:
                entry = {
                    "name": item.get("name", "未知產品")[:30],
                    "old": old_price,
                    "new": new_price,
                    "percent": change_percent
                }
                if change_percent < 0:
                    drops.append(entry)
                else:
                    increases.append(entry)

        if not drops and not increases:
            return {"ok": True, "message": "無超過閾值的價格變動"}

        message = f"<b>📊 {self._escape_html(category_name)} 價格變動報告</b>\n"

        if drops:
            message += f"\n<b>📉 下降 ({len(drops)}個)</b>:\n"
            for item in drops[:5]:  # 最多顯示5個
                message += f"• {self._escape_html(item['name'])}: {item['percent']:.1f}%\n"
            if len(drops) > 5:
                message += f"  ...及 {len(drops) - 5} 個其他產品\n"

        if increases:
            message += f"\n<b>📈 上升 ({len(increases)}個)</b>:\n"
            for item in increases[:5]:
                message += f"• {self._escape_html(item['name'])}: +{item['percent']:.1f}%\n"
            if len(increases) > 5:
                message += f"  ...及 {len(increases) - 5} 個其他產品\n"

        return await self.send_message(message.strip())

    async def notify_error(
        self,
        error_type: str,
        error_message: str,
        context: str = ""
    ) -> dict:
        """
        通知：系統錯誤

        Args:
            error_type: 錯誤類型
            error_message: 錯誤訊息
            context: 上下文資訊
        """
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        message = f"""
<b>⚠️ 系統錯誤警告</b>

🔴 <b>類型</b>: {self._escape_html(error_type)}
📝 <b>訊息</b>: {self._escape_html(error_message[:200])}
🕐 <b>時間</b>: {now}
"""
        if context:
            message += f"📍 <b>上下文</b>: {self._escape_html(context[:100])}\n"

        return await self.send_message(message.strip())

    async def notify_daily_summary(
        self,
        total_categories: int,
        total_products: int,
        price_drops: int,
        price_increases: int,
        new_products: int,
        errors: int = 0
    ) -> dict:
        """
        通知：每日摘要
        """
        today = datetime.now().strftime("%Y-%m-%d")

        status_emoji = "✅" if errors == 0 else "⚠️"

        message = f"""
<b>📋 每日爬取摘要 - {today}</b>

{status_emoji} <b>狀態</b>: {"正常" if errors == 0 else f"有 {errors} 個錯誤"}

📁 <b>類別數</b>: {total_categories}
📦 <b>產品數</b>: {total_products}
🆕 <b>新增產品</b>: {new_products}
📉 <b>價格下降</b>: {price_drops}
📈 <b>價格上升</b>: {price_increases}
"""
        return await self.send_message(message.strip())

    async def send_alert_notification(
        self,
        alert_data: Dict[str, Any],
        analysis: Optional[Dict[str, Any]] = None,
        proposal: Optional[Dict[str, Any]] = None,
        include_action_buttons: bool = True,
        chat_id: Optional[str] = None
    ) -> dict:
        """
        發送價格告警通知（帶 AI 分析和操作按鈕）

        Args:
            alert_data: 告警數據 {
                product_id, product_name, old_price, new_price,
                change_percent, alert_type, competitor_id
            }
            analysis: AI 分析結果 (optional)
            proposal: 已創建的改價提案 (optional)
            include_action_buttons: 是否包含操作按鈕
            chat_id: 指定聊天 ID（覆蓋默認值）

        Returns:
            Telegram API 響應
        """
        product_name = alert_data.get("product_name", "未知產品")
        old_price = alert_data.get("old_price", 0)
        new_price = alert_data.get("new_price", 0)
        change_percent = alert_data.get("change_percent", 0)
        product_id = alert_data.get("product_id", "")

        # 確定方向和圖標
        if change_percent < 0:
            direction = "📉 降價"
            change_display = f"-{abs(change_percent):.1f}%"
        else:
            direction = "📈 漲價"
            change_display = f"+{change_percent:.1f}%"

        # 構建基本消息
        message_parts = [
            f"<b>⚠️ 價格告警: {direction}</b>",
            "",
            f"🏷 <b>產品</b>: {self._escape_html(product_name[:50])}",
            f"💰 <b>原價</b>: HK${float(old_price):.2f}",
            f"💵 <b>現價</b>: HK${float(new_price):.2f}",
            f"📊 <b>變動</b>: {change_display}",
        ]

        # 添加 AI 分析結果
        if analysis:
            message_parts.append("")
            message_parts.append("<b>🤖 AI 分析</b>")
            impact = analysis.get("impact_assessment", "")
            if impact:
                message_parts.append(f"• {self._escape_html(impact)}")
            recommendations = analysis.get("recommendations", [])
            if recommendations:
                message_parts.append(f"• {self._escape_html(recommendations[0])}")

        # 添加提案信息
        if proposal:
            message_parts.append("")
            message_parts.append("<b>📋 改價提案已創建</b>")
            proposed_price = proposal.get("proposed_price")
            if proposed_price:
                message_parts.append(f"• 建議價格: HK${proposed_price:.2f}")
            proposal_id = proposal.get("id")
            if proposal_id:
                message_parts.append(f"• 提案編號: {proposal_id[:8]}...")

        message_parts.append("")
        message_parts.append(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M')}")

        message = "\n".join(message_parts)

        # 決定是否發送帶按鈕的消息
        if include_action_buttons and not proposal:
            # 只有在沒有自動創建提案時才顯示創建按鈕
            buttons = [
                [
                    {
                        "text": "📝 創建改價任務",
                        "callback_data": f"create_proposal:{product_id}"
                    },
                    {
                        "text": "🔍 查看詳情",
                        "callback_data": f"view_alert:{product_id}"
                    }
                ],
                [
                    {
                        "text": "⏸ 暫時忽略",
                        "callback_data": f"ignore_alert:{product_id}"
                    }
                ]
            ]
            return await self.send_message_with_buttons(
                text=message,
                buttons=buttons,
                chat_id=chat_id
            )
        elif include_action_buttons and proposal:
            # 有提案時顯示不同按鈕
            buttons = [
                [
                    {
                        "text": "✅ 批准提案",
                        "callback_data": f"approve_proposal:{proposal.get('id', '')}"
                    },
                    {
                        "text": "❌ 拒絕提案",
                        "callback_data": f"reject_proposal:{proposal.get('id', '')}"
                    }
                ],
                [
                    {
                        "text": "🔍 查看詳情",
                        "callback_data": f"view_proposal:{proposal.get('id', '')}"
                    }
                ]
            ]
            return await self.send_message_with_buttons(
                text=message,
                buttons=buttons,
                chat_id=chat_id
            )
        else:
            return await self.send_message(
                text=message,
                chat_id=chat_id
            )

    async def send_scheduled_report(
        self,
        schedule_name: str,
        report_type: str,
        report_content: str,
        chat_id: Optional[str] = None
    ) -> dict:
        """
        發送排程報告

        Args:
            schedule_name: 排程名稱
            report_type: 報告類型
            report_content: 報告內容（Markdown 格式）
            chat_id: 指定聊天 ID（覆蓋默認值）

        Returns:
            Telegram API 響應
        """
        now = datetime.now().strftime("%Y-%m-%d %H:%M")

        # 報告類型圖標
        type_icons = {
            "price_analysis": "📊",
            "competitor_report": "⚔️",
            "sales_summary": "💰",
            "inventory_alert": "📦",
            "custom": "📋",
        }
        icon = type_icons.get(report_type, "📋")

        # 構建消息頭
        header = f"""<b>{icon} 排程報告: {self._escape_html(schedule_name)}</b>

<i>自動生成於 {now}</i>

---

"""
        # 將 Markdown 內容轉為簡單 HTML（基本轉換）
        content = self._markdown_to_html(report_content)

        # 截取長度（Telegram 限制約 4096 字符）
        max_length = 3800 - len(header)
        if len(content) > max_length:
            content = content[:max_length] + "\n\n<i>... (內容過長，已截取)</i>"

        full_message = header + content

        return await self.send_message(
            text=full_message,
            parse_mode="HTML",
            chat_id=chat_id
        )

    def _markdown_to_html(self, text: str) -> str:
        """
        簡單的 Markdown 轉 HTML

        支援：
        - # 標題 -> <b>標題</b>
        - **粗體** -> <b>粗體</b>
        - *斜體* -> <i>斜體</i>
        - - 列表項 -> • 列表項
        """
        import re

        # 先轉義 HTML 特殊字符
        text = self._escape_html(text)

        # 標題轉換 (# ## ###)
        text = re.sub(r'^###\s+(.+)$', r'<b>\1</b>', text, flags=re.MULTILINE)
        text = re.sub(r'^##\s+(.+)$', r'<b>\1</b>', text, flags=re.MULTILINE)
        text = re.sub(r'^#\s+(.+)$', r'<b>\1</b>', text, flags=re.MULTILINE)

        # 粗體轉換 **text** -> <b>text</b>
        text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)

        # 斜體轉換 *text* -> <i>text</i> (注意避免與粗體衝突)
        text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<i>\1</i>', text)

        # 列表項轉換
        text = re.sub(r'^-\s+', '• ', text, flags=re.MULTILINE)

        # 刪除水平線 ---
        text = re.sub(r'^---+$', '', text, flags=re.MULTILINE)

        return text.strip()

    # ==================== 輔助方法 ====================

    @staticmethod
    def _escape_html(text: str) -> str:
        """轉義 HTML 特殊字符"""
        if not text:
            return ""
        return (
            text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )


# ==================== 單例訪問 ====================

_notifier_instance: Optional[TelegramNotifier] = None


def get_telegram_notifier() -> TelegramNotifier:
    """獲取 Telegram 通知服務單例"""
    global _notifier_instance
    if _notifier_instance is None:
        _notifier_instance = TelegramNotifier()
    return _notifier_instance


async def send_telegram_notification(message: str) -> dict:
    """快捷方法：發送 Telegram 通知"""
    notifier = get_telegram_notifier()
    return await notifier.send_message(message)
