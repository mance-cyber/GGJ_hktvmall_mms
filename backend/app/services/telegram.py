# =============================================
# Telegram 通知服務
# =============================================
# 用途：向管理者發送系統通知
# 場景：價格變動、爬取完成、錯誤警告等
# =============================================

import asyncio
import logging
from datetime import datetime
from typing import Optional
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
