# =============================================
# Monitor - 每日監測模塊
# =============================================
# 職責：追蹤「有什麼變化」— 下架判定 + 價格異動檢測。
#
# 下架判定：last_seen_at < (now - 3 days) AND is_active → is_active = False
# 價格異動：比較最新兩筆 price_snapshots，結合 match_level 決定 alert 優先級
#
# 不 commit — 由 caller 控制事務邊界。

import logging
from datetime import datetime, timezone, timedelta
from decimal import Decimal

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.competitor import CompetitorProduct, PriceSnapshot, PriceAlert
from app.models.product import ProductCompetitorMapping

logger = logging.getLogger(__name__)

# 連續 N 天未出現才標記下架
DELIST_THRESHOLD_DAYS = 3

# 價格變動 alert 閾值
PRICE_CHANGE_THRESHOLD_PCT = Decimal("10.0")


# =============================================
# MonitorService
# =============================================

class MonitorService:
    """
    每日監測服務

    check_delistings()       — 標記連續 3 天未出現的商品為下架
    detect_price_changes()   — 檢測價格異動，生成 PriceAlert
    run_daily_check()        — 每日檢查入口
    """

    # ==================== 下架判定 ====================

    @staticmethod
    async def check_delistings(db: AsyncSession) -> dict:
        """
        檢查連續 3 天未出現的商品，標記為下架

        條件：is_active = True AND last_seen_at < (now - 3 days)
        last_seen_at 為 None 的活躍商品不處理（可能是未完成首次建庫的數據）
        """
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        cutoff = now - timedelta(days=DELIST_THRESHOLD_DAYS)

        stmt = (
            select(CompetitorProduct)
            .where(
                CompetitorProduct.is_active == True,
                CompetitorProduct.last_seen_at.isnot(None),
                CompetitorProduct.last_seen_at < cutoff,
            )
        )
        result = await db.execute(stmt)
        stale_products = result.scalars().all()

        delisted_names = []
        for cp in stale_products:
            cp.is_active = False
            delisted_names.append(cp.name)

        if delisted_names:
            logger.info(
                f"下架判定: {len(delisted_names)} 商品已標記下架 "
                f"(>{DELIST_THRESHOLD_DAYS} 天未出現)"
            )
        else:
            logger.info("下架判定: 無需下架的商品")

        return {
            "delisted": len(delisted_names),
            "products": delisted_names[:50],  # 只返回前 50 個名稱，避免響應過大
        }

    # ==================== 價格異動檢測 ====================

    @staticmethod
    async def detect_price_changes(db: AsyncSession) -> dict:
        """
        檢測價格異動，生成 PriceAlert

        邏輯：
        1. 查詢所有活躍競品商品的最新兩筆 price_snapshots
        2. 計算價格變動百分比
        3. 結合 match_level 決定 alert 類型：
           - match_level=1 且降價 >10% → price_drop（高優先級）
           - match_level=2 且降價 >10% → price_drop（中優先級）
           - 其他漲跌 >10% → price_increase / price_drop（資訊通知）
        """
        # 用 lateral subquery 取每個競品的最新兩筆快照
        # 為了兼容性和可讀性，改用兩步查詢

        # Step 1: 找出有至少 2 筆快照的活躍競品
        count_stmt = (
            select(
                PriceSnapshot.competitor_product_id,
                func.count(PriceSnapshot.id).label("cnt"),
            )
            .join(
                CompetitorProduct,
                PriceSnapshot.competitor_product_id == CompetitorProduct.id,
            )
            .where(CompetitorProduct.is_active == True)
            .group_by(PriceSnapshot.competitor_product_id)
            .having(func.count(PriceSnapshot.id) >= 2)
        )
        count_result = await db.execute(count_stmt)
        product_ids = [row.competitor_product_id for row in count_result]

        if not product_ids:
            logger.info("價格異動: 無足夠快照進行比較")
            return {"alerts_created": 0}

        alerts_created = 0

        # Step 2: 逐個競品取最新兩筆快照比較
        for cp_id in product_ids:
            snapshots_stmt = (
                select(PriceSnapshot)
                .where(PriceSnapshot.competitor_product_id == cp_id)
                .order_by(PriceSnapshot.scraped_at.desc())
                .limit(2)
            )
            snap_result = await db.execute(snapshots_stmt)
            snapshots = snap_result.scalars().all()

            if len(snapshots) < 2:
                continue

            latest = snapshots[0]
            previous = snapshots[1]

            if latest.price is None or previous.price is None:
                continue
            if previous.price == 0:
                continue

            change_pct = ((latest.price - previous.price) / previous.price) * 100

            if abs(change_pct) < PRICE_CHANGE_THRESHOLD_PCT:
                continue

            # 決定 alert 類型
            alert_type = "price_drop" if change_pct < 0 else "price_increase"

            # 查詢該競品的最高 match_level（最直接的競爭關係）
            level_stmt = (
                select(func.min(ProductCompetitorMapping.match_level))
                .where(ProductCompetitorMapping.competitor_product_id == cp_id)
            )
            level_result = await db.execute(level_stmt)
            best_level = level_result.scalar()

            # 避免重複 alert：檢查今天是否已為同一商品建過同類型 alert
            today_start = datetime.now(timezone.utc).replace(
                hour=0, minute=0, second=0, microsecond=0, tzinfo=None,
            )
            dup_stmt = (
                select(func.count())
                .select_from(PriceAlert)
                .where(
                    PriceAlert.competitor_product_id == cp_id,
                    PriceAlert.alert_type == alert_type,
                    PriceAlert.created_at >= today_start,
                )
            )
            dup_result = await db.execute(dup_stmt)
            if (dup_result.scalar() or 0) > 0:
                continue

            alert = PriceAlert(
                competitor_product_id=cp_id,
                alert_type=alert_type,
                old_value=str(previous.price),
                new_value=str(latest.price),
                change_percent=abs(change_pct),
            )
            db.add(alert)
            alerts_created += 1

            level_label = {1: "直接對手", 2: "近似競品", 3: "品類競品"}.get(
                best_level, "未匹配"
            )
            logger.info(
                f"價格異動: {alert_type} {change_pct:+.1f}% "
                f"({previous.price}→{latest.price}) "
                f"[{level_label}] cp_id={cp_id}"
            )

        logger.info(f"價格異動檢測完成: 生成 {alerts_created} 條 alert")
        return {"alerts_created": alerts_created}

    # ==================== 每日檢查入口 ====================

    @staticmethod
    async def run_daily_check(db: AsyncSession) -> dict:
        """每日檢查入口：下架判定 + 價格異動"""
        delistings = await MonitorService.check_delistings(db)
        price_changes = await MonitorService.detect_price_changes(db)

        logger.info(
            f"每日監測完成: 下架 {delistings['delisted']}, "
            f"價格 alert {price_changes['alerts_created']}"
        )
        return {
            "delistings": delistings,
            "price_changes": price_changes,
        }
