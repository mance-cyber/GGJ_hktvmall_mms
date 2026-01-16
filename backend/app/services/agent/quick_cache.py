# =============================================
# 快速回覆快取服務
# =============================================
#
# 為常用查詢提供預計算/快取的即時回覆
# 目標：<100ms 回覆時間
#

import json
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order

logger = logging.getLogger(__name__)


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


class QuickCacheService:
    """
    快速回覆快取服務

    Layer 1: 預計算快取
    - 訂單統計、財務數據、警報摘要等
    - 由事件觸發更新或定時刷新
    - 直接從內存/Redis 讀取，<50ms

    Layer 2: 查詢快取
    - 產品價格、競品數據等
    - 首次查詢時快取，5 分鐘過期
    - 100-500ms
    """

    # 內存快取（簡易實現，生產環境應用 Redis）
    _cache: Dict[str, Dict[str, Any]] = {}
    _cache_ttl: Dict[str, datetime] = {}

    # 快取 Key 定義
    CACHE_KEYS = {
        "orders_today": "quick:orders:today",
        "orders_pending": "quick:orders:pending",
        "orders_week": "quick:orders:week",
        "orders_month": "quick:orders:month",
        "finance_today": "quick:finance:today",
        "finance_month": "quick:finance:month",
        "alerts_summary": "quick:alerts:summary",
        "alerts_urgent": "quick:alerts:urgent",
        "competitors_changes": "quick:competitors:changes",
        "competitors_stockout": "quick:competitors:stockout",
        "products_top10": "quick:products:top10",
        "products_lowstock": "quick:products:lowstock",
    }

    # Intent 到快取 Key 的映射
    INTENT_CACHE_MAP = {
        "order_stats": ["orders_today", "orders_pending"],
        "order_query": ["orders_today"],
        "finance_summary": ["finance_today", "finance_month"],
        "finance_analysis": ["finance_month"],
        "alert_query": ["alerts_summary"],
        "navigate": None,  # 硬編碼回覆
        "add_competitor": None,  # 硬編碼回覆
        "add_product": None,  # 硬編碼回覆
    }

    # 快取 TTL（秒）
    CACHE_TTL = {
        "orders_today": 60,       # 1 分鐘
        "orders_pending": 60,     # 1 分鐘
        "orders_week": 3600,      # 1 小時
        "orders_month": 3600,     # 1 小時
        "finance_today": 60,      # 1 分鐘
        "finance_month": 3600,    # 1 小時
        "alerts_summary": 60,     # 1 分鐘
        "alerts_urgent": 30,      # 30 秒
        "competitors_changes": 600,    # 10 分鐘
        "competitors_stockout": 600,   # 10 分鐘
        "products_top10": 300,    # 5 分鐘
        "products_lowstock": 300, # 5 分鐘
    }

    def __init__(self, db: AsyncSession):
        self.db = db

    # =============================================
    # 快取讀取
    # =============================================

    def _get_cache(self, key: str) -> Optional[Dict[str, Any]]:
        """讀取快取（檢查 TTL）"""
        full_key = self.CACHE_KEYS.get(key, key)

        if full_key not in self._cache:
            return None

        # 檢查 TTL
        if full_key in self._cache_ttl:
            if datetime.now() > self._cache_ttl[full_key]:
                # 過期，刪除快取
                del self._cache[full_key]
                del self._cache_ttl[full_key]
                return None

        return self._cache.get(full_key)

    def _set_cache(self, key: str, data: Dict[str, Any], ttl_seconds: int = None) -> None:
        """設置快取"""
        full_key = self.CACHE_KEYS.get(key, key)

        self._cache[full_key] = data

        # 設置 TTL
        if ttl_seconds is None:
            ttl_seconds = self.CACHE_TTL.get(key, 300)

        self._cache_ttl[full_key] = datetime.now() + timedelta(seconds=ttl_seconds)

    # =============================================
    # 快速回覆入口
    # =============================================

    async def get_quick_response(self, intent: str) -> Optional[QuickResponse]:
        """
        根據意圖獲取快速回覆

        Args:
            intent: 意圖類型（如 order_stats, alert_query）

        Returns:
            QuickResponse 或 None（如果不支持快取回覆）
        """
        # 硬編碼回覆
        if intent in ["navigate", "add_competitor", "add_product"]:
            return None  # 這些由原有邏輯處理

        # 檢查是否支持快取
        cache_keys = self.INTENT_CACHE_MAP.get(intent)
        if cache_keys is None:
            return None

        # 嘗試讀取快取
        cached_data = {}
        need_refresh = False

        for key in cache_keys:
            data = self._get_cache(key)
            if data:
                cached_data[key] = data
            else:
                need_refresh = True

        # 如果有缺失，刷新快取
        if need_refresh:
            await self._refresh_for_intent(intent)
            # 重新讀取
            for key in cache_keys:
                data = self._get_cache(key)
                if data:
                    cached_data[key] = data

        # 生成回覆
        if not cached_data:
            return None

        return self._format_response(intent, cached_data)

    # =============================================
    # 快取刷新
    # =============================================

    async def _refresh_for_intent(self, intent: str) -> None:
        """根據意圖刷新相關快取"""
        cache_keys = self.INTENT_CACHE_MAP.get(intent, [])

        for key in cache_keys:
            await self.refresh_cache(key)

    async def refresh_cache(self, key: str) -> None:
        """刷新特定快取"""
        refresh_method = getattr(self, f"_refresh_{key}", None)
        if refresh_method:
            await refresh_method()

    async def refresh_all(self) -> None:
        """刷新所有快取"""
        for key in self.CACHE_KEYS.keys():
            await self.refresh_cache(key)

    # =============================================
    # 數據刷新方法
    # =============================================

    async def _refresh_orders_today(self) -> None:
        """刷新今日訂單統計"""
        today = datetime.now().date()
        today_start = datetime.combine(today, datetime.min.time())

        try:
            # 查詢今日訂單
            result = await self.db.execute(
                select(
                    func.count(Order.id).label('count'),
                    func.sum(Order.total_amount).label('revenue'),
                ).where(Order.created_at >= today_start)
            )
            row = result.first()

            data = {
                "count": row.count or 0,
                "revenue": float(row.revenue or 0),
                "avg_price": float(row.revenue or 0) / max(row.count or 1, 1),
                "updated_at": datetime.now().isoformat(),
            }

            self._set_cache("orders_today", data)

        except Exception as e:
            logger.warning(f"刷新 orders_today 失敗: {e}")
            # 設置空數據避免重複查詢
            self._set_cache("orders_today", {
                "count": 0,
                "revenue": 0,
                "avg_price": 0,
                "error": str(e),
                "updated_at": datetime.now().isoformat(),
            }, ttl_seconds=30)  # 錯誤時短 TTL

    async def _refresh_orders_pending(self) -> None:
        """刷新待處理訂單"""
        try:
            # 查詢待處理訂單（狀態為 pending 或 processing）
            result = await self.db.execute(
                select(func.count(Order.id)).where(
                    Order.status.in_(["pending", "processing", "confirmed"])
                )
            )
            pending_count = result.scalar() or 0

            # 查詢待出貨（已確認但未發貨）
            result2 = await self.db.execute(
                select(func.count(Order.id)).where(
                    Order.status == "confirmed"
                )
            )
            to_ship_count = result2.scalar() or 0

            data = {
                "pending": pending_count,
                "to_ship": to_ship_count,
                "updated_at": datetime.now().isoformat(),
            }

            self._set_cache("orders_pending", data)

        except Exception as e:
            logger.warning(f"刷新 orders_pending 失敗: {e}")
            self._set_cache("orders_pending", {
                "pending": 0,
                "to_ship": 0,
                "error": str(e),
                "updated_at": datetime.now().isoformat(),
            }, ttl_seconds=30)

    async def _refresh_finance_today(self) -> None:
        """刷新今日財務數據"""
        # 暫時復用訂單數據
        today_data = self._get_cache("orders_today")
        if not today_data:
            await self._refresh_orders_today()
            today_data = self._get_cache("orders_today") or {}

        data = {
            "revenue": today_data.get("revenue", 0),
            "orders": today_data.get("count", 0),
            "updated_at": datetime.now().isoformat(),
        }

        self._set_cache("finance_today", data)

    async def _refresh_finance_month(self) -> None:
        """刷新本月財務數據"""
        today = datetime.now().date()
        month_start = today.replace(day=1)
        month_start_dt = datetime.combine(month_start, datetime.min.time())

        try:
            result = await self.db.execute(
                select(
                    func.count(Order.id).label('count'),
                    func.sum(Order.total_amount).label('revenue'),
                ).where(Order.created_at >= month_start_dt)
            )
            row = result.first()

            data = {
                "revenue": float(row.revenue or 0),
                "orders": row.count or 0,
                "avg_order": float(row.revenue or 0) / max(row.count or 1, 1),
                "updated_at": datetime.now().isoformat(),
            }

            self._set_cache("finance_month", data)

        except Exception as e:
            logger.warning(f"刷新 finance_month 失敗: {e}")
            self._set_cache("finance_month", {
                "revenue": 0,
                "orders": 0,
                "avg_order": 0,
                "error": str(e),
                "updated_at": datetime.now().isoformat(),
            }, ttl_seconds=60)

    async def _refresh_alerts_summary(self) -> None:
        """刷新警報摘要"""
        # 暫時使用 mock 數據（因為 Alert model 可能不存在）
        data = {
            "total": 0,
            "urgent": 0,
            "price_alerts": 0,
            "stockout_alerts": 0,
            "updated_at": datetime.now().isoformat(),
        }

        try:
            # 嘗試查詢真實數據
            from app.models.alert import Alert

            result = await self.db.execute(
                select(func.count(Alert.id)).where(Alert.is_read == False)
            )
            total = result.scalar() or 0

            result2 = await self.db.execute(
                select(func.count(Alert.id)).where(
                    and_(Alert.is_read == False, Alert.priority == "high")
                )
            )
            urgent = result2.scalar() or 0

            data = {
                "total": total,
                "urgent": urgent,
                "price_alerts": 0,  # TODO: 分類統計
                "stockout_alerts": 0,
                "updated_at": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.warning(f"刷新 alerts_summary 失敗: {e}")

        self._set_cache("alerts_summary", data)

    # =============================================
    # 回覆格式化
    # =============================================

    def _format_response(self, intent: str, cached_data: Dict[str, Dict]) -> QuickResponse:
        """格式化快取數據為用戶友好的回覆"""
        from .quick_templates import format_quick_response

        return format_quick_response(intent, cached_data)


# 單例模式（簡化實現）
_instance: Optional[QuickCacheService] = None


async def get_quick_cache_service(db: AsyncSession) -> QuickCacheService:
    """獲取 QuickCacheService 實例"""
    global _instance
    if _instance is None or _instance.db != db:
        _instance = QuickCacheService(db)
    return _instance
