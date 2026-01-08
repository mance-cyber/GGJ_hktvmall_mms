# =============================================
# Firecrawl 配額監控服務
# =============================================
# 整合 Firecrawl API 配額查詢，實現實時監控

import httpx
from typing import Optional, Dict, Any
from datetime import datetime
from dataclasses import dataclass
import logging

from app.config import get_settings

logger = logging.getLogger(__name__)


# =============================================
# 數據模型
# =============================================

@dataclass
class FirecrawlQuota:
    """Firecrawl 配額信息"""
    remaining_credits: int              # 剩餘配額
    plan_credits: int                   # 計劃總配額
    billing_period_start: datetime      # 計費週期開始
    billing_period_end: datetime        # 計費週期結束
    usage_percent: float                # 使用百分比
    days_remaining: int                 # 剩餘天數

    def to_dict(self) -> Dict[str, Any]:
        return {
            "remaining_credits": self.remaining_credits,
            "plan_credits": self.plan_credits,
            "used_credits": self.plan_credits - self.remaining_credits,
            "usage_percent": round(self.usage_percent, 1),
            "billing_period_start": self.billing_period_start.isoformat(),
            "billing_period_end": self.billing_period_end.isoformat(),
            "days_remaining": self.days_remaining,
        }


@dataclass
class QuotaStatus:
    """配額狀態"""
    success: bool
    quota: Optional[FirecrawlQuota] = None
    error_message: Optional[str] = None
    is_low: bool = False                # 配額偏低警告
    is_critical: bool = False           # 配額緊急警告


# =============================================
# Firecrawl 配額服務
# =============================================

class FirecrawlQuotaService:
    """
    Firecrawl 配額監控服務

    功能：
    1. 查詢 Firecrawl API 配額
    2. 計算使用率和剩餘時間
    3. 提供配額警告
    """

    API_BASE = "https://api.firecrawl.dev/v2"
    CREDIT_USAGE_ENDPOINT = "/team/credit-usage"

    # 警告閾值
    LOW_QUOTA_PERCENT = 20        # 剩餘 < 20% 為低配額
    CRITICAL_QUOTA_PERCENT = 5    # 剩餘 < 5% 為緊急

    def __init__(self):
        settings = get_settings()
        self.api_key = settings.firecrawl_api_key

    async def get_quota(self) -> QuotaStatus:
        """
        獲取 Firecrawl 配額信息

        Returns:
            QuotaStatus 包含配額信息和狀態
        """
        if not self.api_key:
            return QuotaStatus(
                success=False,
                error_message="Firecrawl API Key 未設定"
            )

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.API_BASE}{self.CREDIT_USAGE_ENDPOINT}",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    timeout=10.0
                )

                if response.status_code == 200:
                    data = response.json()

                    if data.get("success"):
                        return self._parse_quota_response(data.get("data", {}))
                    else:
                        return QuotaStatus(
                            success=False,
                            error_message=data.get("error", "未知錯誤")
                        )

                elif response.status_code == 401:
                    return QuotaStatus(
                        success=False,
                        error_message="API Key 無效或已過期"
                    )

                elif response.status_code == 402:
                    # Payment Required - 配額已用完
                    return QuotaStatus(
                        success=True,
                        quota=FirecrawlQuota(
                            remaining_credits=0,
                            plan_credits=0,
                            billing_period_start=datetime.utcnow(),
                            billing_period_end=datetime.utcnow(),
                            usage_percent=100.0,
                            days_remaining=0,
                        ),
                        is_critical=True,
                        error_message="配額已用完，請升級計劃"
                    )

                else:
                    return QuotaStatus(
                        success=False,
                        error_message=f"API 請求失敗: HTTP {response.status_code}"
                    )

        except httpx.TimeoutException:
            return QuotaStatus(
                success=False,
                error_message="API 請求超時"
            )
        except Exception as e:
            logger.error(f"獲取 Firecrawl 配額失敗: {e}")
            return QuotaStatus(
                success=False,
                error_message=str(e)
            )

    def _parse_quota_response(self, data: Dict[str, Any]) -> QuotaStatus:
        """解析配額響應"""
        try:
            remaining = data.get("remainingCredits", 0)
            plan = data.get("planCredits", 0)

            # 解析時間
            period_start = datetime.fromisoformat(
                data.get("billingPeriodStart", "").replace("Z", "+00:00")
            )
            period_end = datetime.fromisoformat(
                data.get("billingPeriodEnd", "").replace("Z", "+00:00")
            )

            # 計算使用百分比
            usage_percent = 0.0
            if plan > 0:
                usage_percent = ((plan - remaining) / plan) * 100

            # 計算剩餘天數
            now = datetime.utcnow()
            if period_end.tzinfo:
                now = now.replace(tzinfo=period_end.tzinfo)
            days_remaining = max(0, (period_end - now).days)

            # 計算剩餘百分比
            remaining_percent = 100 - usage_percent

            quota = FirecrawlQuota(
                remaining_credits=remaining,
                plan_credits=plan,
                billing_period_start=period_start,
                billing_period_end=period_end,
                usage_percent=usage_percent,
                days_remaining=days_remaining,
            )

            return QuotaStatus(
                success=True,
                quota=quota,
                is_low=remaining_percent < self.LOW_QUOTA_PERCENT,
                is_critical=remaining_percent < self.CRITICAL_QUOTA_PERCENT,
            )

        except Exception as e:
            logger.error(f"解析配額響應失敗: {e}")
            return QuotaStatus(
                success=False,
                error_message=f"解析響應失敗: {e}"
            )

    def get_quota_sync(self) -> QuotaStatus:
        """
        同步獲取配額（用於非異步環境）
        """
        import asyncio
        return asyncio.run(self.get_quota())


# =============================================
# 單例工廠
# =============================================

_service: Optional[FirecrawlQuotaService] = None


def get_firecrawl_quota_service() -> FirecrawlQuotaService:
    """獲取 Firecrawl 配額服務單例"""
    global _service
    if _service is None:
        _service = FirecrawlQuotaService()
    return _service


# =============================================
# 便捷函數
# =============================================

async def check_quota() -> QuotaStatus:
    """便捷函數：檢查配額"""
    service = get_firecrawl_quota_service()
    return await service.get_quota()


async def has_sufficient_quota(required_credits: int = 1) -> bool:
    """
    檢查是否有足夠配額

    Args:
        required_credits: 需要的配額數量

    Returns:
        True 如果配額足夠
    """
    status = await check_quota()
    if not status.success or not status.quota:
        return False
    return status.quota.remaining_credits >= required_credits
