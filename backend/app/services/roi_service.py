# =============================================
# ROI 分析服務
# 計算並展示 GoGoJap 為用戶創造的價值
# =============================================

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, case
from typing import List, Optional
from datetime import datetime, timedelta
from decimal import Decimal

from app.models.pricing import PriceProposal, ProposalStatus
from app.models.competitor import PriceAlert
from app.models.order import Order, OrderItem
from app.schemas.roi import (
    ROISummary, ROITrendPoint, ROITrendsResponse,
    PricingProposalImpact, PricingImpactSummary, PricingImpactResponse,
    CompetitorInsights
)


class ROIService:
    """
    ROI 儀表板核心服務
    職責: 計算、聚合、展示所有 ROI 相關指標
    """

    # 預設估算銷量 (當無訂單數據時使用)
    DEFAULT_ESTIMATED_QUANTITY = 10
    # 預設平均訂單金額
    DEFAULT_AVG_ORDER_VALUE = Decimal("200.00")
    # 預設服務成本 (用於 ROI 計算)
    DEFAULT_SERVICE_COST = Decimal("299.00")

    def __init__(self, db: AsyncSession):
        self.db = db

    def _get_date_range(self, period: str) -> tuple[datetime, datetime]:
        """根據 period 參數計算日期範圍"""
        now = datetime.utcnow()
        end_date = now

        if period == "today":
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "week":
            start_date = now - timedelta(days=7)
        elif period == "month":
            start_date = now - timedelta(days=30)
        elif period == "quarter":
            start_date = now - timedelta(days=90)
        else:
            # 預設 30 天
            start_date = now - timedelta(days=30)

        return start_date, end_date

    async def get_summary(
        self,
        period: str = "month",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> ROISummary:
        """計算期間內的 ROI 總覽"""

        if not start_date or not end_date:
            start_date, end_date = self._get_date_range(period)

        # 1. AI 定價貢獻
        ai_contribution = await self._calculate_ai_pricing_contribution(start_date, end_date)

        # 2. 競品監測價值
        monitoring_value = await self._calculate_competitor_monitoring_value(start_date, end_date)

        # 3. 風險規避價值 (簡化: 監測價值的 30%)
        risk_avoidance = monitoring_value * Decimal("0.3")

        # 4. 總價值
        total_value = ai_contribution + monitoring_value + risk_avoidance

        # 5. ROI 計算
        service_cost = self.DEFAULT_SERVICE_COST
        if service_cost > 0:
            roi_percentage = float((total_value - service_cost) / service_cost * 100)
        else:
            roi_percentage = 0.0

        return ROISummary(
            total_value_generated=total_value,
            ai_pricing_contribution=ai_contribution,
            competitor_monitoring_value=monitoring_value,
            risk_avoidance_value=risk_avoidance,
            roi_percentage=round(roi_percentage, 2),
            period_start=start_date,
            period_end=end_date
        )

    async def _calculate_ai_pricing_contribution(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Decimal:
        """
        計算 AI 定價貢獻
        公式: SUM((final_price - current_price) × estimated_quantity)
        條件: status = 'executed' AND final_price > current_price
        """
        query = select(
            func.sum(
                (PriceProposal.final_price - PriceProposal.current_price) * self.DEFAULT_ESTIMATED_QUANTITY
            )
        ).where(
            and_(
                PriceProposal.status == ProposalStatus.EXECUTED,
                PriceProposal.executed_at >= start_date,
                PriceProposal.executed_at <= end_date,
                PriceProposal.final_price > PriceProposal.current_price
            )
        )

        result = await self.db.scalar(query)
        return Decimal(str(result)) if result else Decimal("0")

    async def _calculate_competitor_monitoring_value(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Decimal:
        """
        計算競品監測價值
        公式: COUNT(alerts) × AVG(change_percent) × avg_order_value
        """
        query = select(
            func.count(PriceAlert.id).label("alert_count"),
            func.avg(func.abs(PriceAlert.change_percent)).label("avg_change")
        ).where(
            and_(
                PriceAlert.created_at >= start_date,
                PriceAlert.created_at <= end_date,
                PriceAlert.alert_type.in_(["price_drop", "price_increase"])
            )
        )

        result = await self.db.execute(query)
        row = result.one_or_none()

        if row and row.alert_count and row.avg_change:
            # 監測價值 = 警報數 × 平均變化率 × 平均訂單金額
            value = Decimal(str(row.alert_count)) * Decimal(str(row.avg_change)) / 100 * self.DEFAULT_AVG_ORDER_VALUE
            return value

        return Decimal("0")

    async def get_trends(
        self,
        days: int = 30,
        granularity: str = "day"
    ) -> ROITrendsResponse:
        """獲取 ROI 趨勢數據"""

        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        trends: List[ROITrendPoint] = []
        cumulative_value = Decimal("0")

        # 按天聚合
        current_date = start_date
        while current_date <= end_date:
            day_end = current_date.replace(hour=23, minute=59, second=59)

            # 當日 AI 定價貢獻
            ai_pricing = await self._calculate_ai_pricing_contribution(current_date, day_end)

            # 當日競品監測價值
            monitoring = await self._calculate_competitor_monitoring_value(current_date, day_end)

            # 風險規避
            risk_avoidance = monitoring * Decimal("0.3")

            # 累計
            day_total = ai_pricing + monitoring + risk_avoidance
            cumulative_value += day_total

            trends.append(ROITrendPoint(
                date=current_date.strftime("%Y-%m-%d"),
                cumulative_value=cumulative_value,
                ai_pricing=ai_pricing,
                monitoring=monitoring,
                risk_avoidance=risk_avoidance
            ))

            current_date += timedelta(days=1)

        return ROITrendsResponse(
            trends=trends,
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d"),
            granularity=granularity
        )

    async def get_pricing_impact(self, limit: int = 10) -> PricingImpactResponse:
        """分析 AI 改價的實際影響"""

        # 獲取已執行的提案統計
        summary_query = select(
            func.count(PriceProposal.id).label("total"),
            func.count(case((PriceProposal.status == ProposalStatus.EXECUTED, 1))).label("executed"),
            func.count(case((PriceProposal.status == ProposalStatus.APPROVED, 1))).label("approved"),
            func.count(case((PriceProposal.status == ProposalStatus.REJECTED, 1))).label("rejected"),
        )

        summary_result = await self.db.execute(summary_query)
        summary_row = summary_result.one()

        # 獲取影響最大的提案列表
        proposals_query = (
            select(PriceProposal)
            .where(
                and_(
                    PriceProposal.status == ProposalStatus.EXECUTED,
                    PriceProposal.final_price > PriceProposal.current_price
                )
            )
            .order_by(
                (PriceProposal.final_price - PriceProposal.current_price).desc()
            )
            .limit(limit)
        )

        proposals_result = await self.db.execute(proposals_query)
        proposals = proposals_result.scalars().all()

        # 計算總影響金額
        total_impact_query = select(
            func.sum(
                (PriceProposal.final_price - PriceProposal.current_price) * self.DEFAULT_ESTIMATED_QUANTITY
            )
        ).where(
            and_(
                PriceProposal.status == ProposalStatus.EXECUTED,
                PriceProposal.final_price > PriceProposal.current_price
            )
        )
        total_impact = await self.db.scalar(total_impact_query) or Decimal("0")

        # 構建響應
        proposal_impacts = []
        for p in proposals:
            price_diff = (p.final_price or Decimal("0")) - (p.current_price or Decimal("0"))
            impact = price_diff * self.DEFAULT_ESTIMATED_QUANTITY

            # 獲取產品名稱
            product_name = "未知產品"
            if hasattr(p, 'product') and p.product:
                product_name = p.product.name or product_name

            proposal_impacts.append(PricingProposalImpact(
                id=str(p.id),
                product_name=product_name,
                old_price=p.current_price or Decimal("0"),
                new_price=p.final_price or Decimal("0"),
                price_diff=price_diff,
                impact=impact,
                executed_at=p.executed_at or p.created_at
            ))

        return PricingImpactResponse(
            proposals=proposal_impacts,
            summary=PricingImpactSummary(
                total_proposals=summary_row.total or 0,
                executed_count=summary_row.executed or 0,
                approved_count=summary_row.approved or 0,
                rejected_count=summary_row.rejected or 0,
                total_impact=Decimal(str(total_impact)) if total_impact else Decimal("0")
            )
        )

    async def get_competitor_insights(self, period: str = "month") -> CompetitorInsights:
        """競品監測價值分析"""

        start_date, end_date = self._get_date_range(period)

        # 統計各類型告警
        query = select(
            func.count(PriceAlert.id).label("total"),
            func.count(case((PriceAlert.alert_type == "price_drop", 1))).label("drops"),
            func.count(case((PriceAlert.alert_type == "price_increase", 1))).label("increases"),
            func.avg(func.abs(PriceAlert.change_percent)).label("avg_change")
        ).where(
            and_(
                PriceAlert.created_at >= start_date,
                PriceAlert.created_at <= end_date
            )
        )

        result = await self.db.execute(query)
        row = result.one()

        # 計算潛在節省
        total_alerts = row.total or 0
        avg_change = Decimal(str(row.avg_change)) if row.avg_change else Decimal("0")
        potential_savings = Decimal(str(total_alerts)) * avg_change / 100 * self.DEFAULT_AVG_ORDER_VALUE

        return CompetitorInsights(
            price_alerts_triggered=total_alerts,
            price_drops_detected=row.drops or 0,
            price_increases_detected=row.increases or 0,
            avg_response_time_hours=None,  # 需要更複雜的計算，暫不實現
            potential_savings=potential_savings,
            period=period
        )
