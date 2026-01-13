# =============================================
# 快速回覆模板
# =============================================
#
# 為 QuickCacheService 提供格式化的回覆模板
#

from typing import Any, Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass


@dataclass
class QuickResponse:
    """快取回覆結構"""
    message: str
    data: Dict[str, Any]
    suggestions: Optional[List[Dict]] = None
    updated_at: datetime = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "message": self.message,
            "data": self.data,
            "suggestions": self.suggestions,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


# =============================================
# 回覆模板
# =============================================

QUICK_TEMPLATES = {
    "order_stats": """📦 **今日訂單**

• 總訂單：**{count}** 單
• 營收：**${revenue:,.0f}**
• 平均單價：${avg_price:,.0f}

---
⏳ **待處理**
• 待確認：{pending} 單
• 待出貨：{to_ship} 單

{status_note}""",

    "finance_summary": """💰 **財務摘要**

📅 **今日**
• 營收：**${today_revenue:,.0f}**
• 訂單：{today_orders} 單

📊 **本月**
• 營收：**${month_revenue:,.0f}**
• 訂單：{month_orders} 單
• 平均單價：${avg_order:,.0f}

{trend_note}""",

    "alert_query": """🚨 **警報摘要**

• 總警報：**{total}** 個
• 緊急：**{urgent}** 個
• 價格變動：{price_alerts} 個
• 缺貨提醒：{stockout_alerts} 個

{urgent_note}""",
}


# =============================================
# 後續建議按鈕
# =============================================

QUICK_SUGGESTIONS = {
    "order_stats": [
        {"text": "查看待處理訂單", "icon": "📋"},
        {"text": "今日營收詳情", "icon": "💰"},
        {"text": "本週訂單趨勢", "icon": "📈"},
    ],
    "finance_summary": [
        {"text": "本月利潤分析", "icon": "📊"},
        {"text": "對比上月表現", "icon": "📉"},
        {"text": "查看結算單", "icon": "📄"},
    ],
    "alert_query": [
        {"text": "查看緊急警報", "icon": "🔴"},
        {"text": "全部標記已讀", "icon": "✅"},
        {"text": "設定警報規則", "icon": "⚙️"},
    ],
}


# =============================================
# 格式化函數
# =============================================

def format_quick_response(intent: str, cached_data: Dict[str, Dict]) -> QuickResponse:
    """
    格式化快取數據為用戶友好的回覆

    Args:
        intent: 意圖類型
        cached_data: 快取數據（key -> data 字典）

    Returns:
        QuickResponse 對象
    """
    template = QUICK_TEMPLATES.get(intent)
    suggestions = QUICK_SUGGESTIONS.get(intent)

    if not template:
        # 沒有模板，返回原始數據
        return QuickResponse(
            message=f"快取數據：{cached_data}",
            data=cached_data,
            suggestions=suggestions,
            updated_at=datetime.now(),
        )

    # 根據意圖格式化
    if intent == "order_stats":
        return _format_order_stats(cached_data, template, suggestions)
    elif intent == "finance_summary":
        return _format_finance_summary(cached_data, template, suggestions)
    elif intent == "alert_query":
        return _format_alert_query(cached_data, template, suggestions)

    # 默認返回
    return QuickResponse(
        message=f"數據已準備好",
        data=cached_data,
        suggestions=suggestions,
        updated_at=datetime.now(),
    )


def _format_order_stats(
    cached_data: Dict[str, Dict],
    template: str,
    suggestions: List[Dict]
) -> QuickResponse:
    """格式化訂單統計"""
    orders_today = cached_data.get("orders_today", {})
    orders_pending = cached_data.get("orders_pending", {})

    count = orders_today.get("count", 0)
    revenue = orders_today.get("revenue", 0)
    avg_price = orders_today.get("avg_price", 0)
    pending = orders_pending.get("pending", 0)
    to_ship = orders_pending.get("to_ship", 0)

    # 狀態提示
    if pending > 5:
        status_note = "⚠️ 待處理訂單較多，建議盡快處理！"
    elif count == 0:
        status_note = "今日暫無訂單，加油！💪"
    else:
        status_note = "✅ 一切正常！"

    message = template.format(
        count=count,
        revenue=revenue,
        avg_price=avg_price,
        pending=pending,
        to_ship=to_ship,
        status_note=status_note,
    )

    return QuickResponse(
        message=message,
        data={
            "orders_today": orders_today,
            "orders_pending": orders_pending,
        },
        suggestions=suggestions,
        updated_at=datetime.now(),
    )


def _format_finance_summary(
    cached_data: Dict[str, Dict],
    template: str,
    suggestions: List[Dict]
) -> QuickResponse:
    """格式化財務摘要"""
    finance_today = cached_data.get("finance_today", {})
    finance_month = cached_data.get("finance_month", {})

    today_revenue = finance_today.get("revenue", 0)
    today_orders = finance_today.get("orders", 0)
    month_revenue = finance_month.get("revenue", 0)
    month_orders = finance_month.get("orders", 0)
    avg_order = finance_month.get("avg_order", 0)

    # 趨勢提示
    if month_revenue > 100000:
        trend_note = "📈 本月表現不錯，繼續加油！"
    elif month_revenue > 50000:
        trend_note = "💪 穩步增長中！"
    else:
        trend_note = "🎯 努力衝刺中！"

    message = template.format(
        today_revenue=today_revenue,
        today_orders=today_orders,
        month_revenue=month_revenue,
        month_orders=month_orders,
        avg_order=avg_order,
        trend_note=trend_note,
    )

    return QuickResponse(
        message=message,
        data={
            "finance_today": finance_today,
            "finance_month": finance_month,
        },
        suggestions=suggestions,
        updated_at=datetime.now(),
    )


def _format_alert_query(
    cached_data: Dict[str, Dict],
    template: str,
    suggestions: List[Dict]
) -> QuickResponse:
    """格式化警報摘要"""
    alerts = cached_data.get("alerts_summary", {})

    total = alerts.get("total", 0)
    urgent = alerts.get("urgent", 0)
    price_alerts = alerts.get("price_alerts", 0)
    stockout_alerts = alerts.get("stockout_alerts", 0)

    # 緊急提示
    if urgent > 0:
        urgent_note = f"🔴 有 {urgent} 個緊急警報需要立即處理！"
    elif total > 0:
        urgent_note = "📋 有新警報，記得查看！"
    else:
        urgent_note = "✅ 冇警報，一切正常！"

    message = template.format(
        total=total,
        urgent=urgent,
        price_alerts=price_alerts,
        stockout_alerts=stockout_alerts,
        urgent_note=urgent_note,
    )

    return QuickResponse(
        message=message,
        data={"alerts_summary": alerts},
        suggestions=suggestions,
        updated_at=datetime.now(),
    )
