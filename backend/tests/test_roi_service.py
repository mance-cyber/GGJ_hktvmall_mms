# =============================================
# ROI 服務單元測試
# 測試 ROI 計算邏輯的正確性
# =============================================

import pytest
import pytest_asyncio
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product
from app.models.pricing import PriceProposal, ProposalStatus
from app.models.competitor import Competitor, CompetitorProduct, PriceAlert
from app.services.roi_service import ROIService


class TestROIServiceDateRange:
    """測試日期範圍計算"""

    @pytest.mark.asyncio
    async def test_get_date_range_today(self, db_session: AsyncSession):
        """測試 today 參數返回今日範圍"""
        service = ROIService(db_session)
        start, end = service._get_date_range("today")

        now = datetime.utcnow()
        assert start.date() == now.date()
        assert start.hour == 0
        assert start.minute == 0

    @pytest.mark.asyncio
    async def test_get_date_range_week(self, db_session: AsyncSession):
        """測試 week 參數返回 7 天範圍"""
        service = ROIService(db_session)
        start, end = service._get_date_range("week")

        delta = end - start
        assert delta.days == 7

    @pytest.mark.asyncio
    async def test_get_date_range_month(self, db_session: AsyncSession):
        """測試 month 參數返回 30 天範圍"""
        service = ROIService(db_session)
        start, end = service._get_date_range("month")

        delta = end - start
        assert delta.days == 30

    @pytest.mark.asyncio
    async def test_get_date_range_quarter(self, db_session: AsyncSession):
        """測試 quarter 參數返回 90 天範圍"""
        service = ROIService(db_session)
        start, end = service._get_date_range("quarter")

        delta = end - start
        assert delta.days == 90


class TestROISummary:
    """測試 ROI 摘要計算"""

    @pytest.mark.asyncio
    async def test_get_summary_empty_data(self, db_session: AsyncSession):
        """測試無數據時返回零值 (Spec: No data in period)"""
        service = ROIService(db_session)
        summary = await service.get_summary(period="month")

        assert summary.total_value_generated == Decimal("0")
        assert summary.ai_pricing_contribution == Decimal("0")
        assert summary.competitor_monitoring_value == Decimal("0")
        # ROI = (0 - 服務成本) / 服務成本 = -100%
        # 這是正確的數學計算：無價值創造時，投資全部損失
        assert summary.roi_percentage == -100.0

    @pytest.mark.asyncio
    async def test_get_summary_with_executed_proposals(self, db_session: AsyncSession, test_product: Product):
        """測試有已執行提案時計算 AI 定價貢獻"""
        # 創建已執行的改價提案
        proposal = PriceProposal(
            id=uuid4(),
            product_id=test_product.id,
            status=ProposalStatus.EXECUTED,
            current_price=Decimal("100.00"),
            proposed_price=Decimal("120.00"),
            final_price=Decimal("120.00"),
            executed_at=datetime.utcnow() - timedelta(days=1),
            reason="AI 建議提價"
        )
        db_session.add(proposal)
        await db_session.commit()

        service = ROIService(db_session)
        summary = await service.get_summary(period="month")

        # AI 貢獻 = (120 - 100) × 10 (預設銷量) = 200
        assert summary.ai_pricing_contribution == Decimal("200.00")
        assert summary.total_value_generated > Decimal("0")

    @pytest.mark.asyncio
    async def test_get_summary_ignores_pending_proposals(self, db_session: AsyncSession, test_product: Product):
        """測試未執行的提案不計入 ROI"""
        proposal = PriceProposal(
            id=uuid4(),
            product_id=test_product.id,
            status=ProposalStatus.PENDING,
            current_price=Decimal("100.00"),
            proposed_price=Decimal("150.00"),
            final_price=None,
            reason="待審批"
        )
        db_session.add(proposal)
        await db_session.commit()

        service = ROIService(db_session)
        summary = await service.get_summary(period="month")

        # 待審批的提案不應計入
        assert summary.ai_pricing_contribution == Decimal("0")

    @pytest.mark.asyncio
    async def test_get_summary_ignores_price_decrease(self, db_session: AsyncSession, test_product: Product):
        """測試降價提案不計入正向 ROI"""
        proposal = PriceProposal(
            id=uuid4(),
            product_id=test_product.id,
            status=ProposalStatus.EXECUTED,
            current_price=Decimal("100.00"),
            proposed_price=Decimal("80.00"),
            final_price=Decimal("80.00"),
            executed_at=datetime.utcnow() - timedelta(days=1),
            reason="清倉降價"
        )
        db_session.add(proposal)
        await db_session.commit()

        service = ROIService(db_session)
        summary = await service.get_summary(period="month")

        # 降價不計入 (final_price <= current_price)
        assert summary.ai_pricing_contribution == Decimal("0")


class TestCompetitorMonitoringValue:
    """測試競品監測價值計算"""

    @pytest.mark.asyncio
    async def test_monitoring_value_with_alerts(
        self,
        db_session: AsyncSession,
        test_competitor: Competitor,
        test_competitor_product: CompetitorProduct
    ):
        """測試有告警時計算監測價值"""
        # 創建價格告警
        alert1 = PriceAlert(
            id=uuid4(),
            competitor_product_id=test_competitor_product.id,
            alert_type="price_drop",
            old_value="100.00",
            new_value="80.00",
            change_percent=Decimal("-20.00"),
            created_at=datetime.utcnow() - timedelta(days=1)
        )
        alert2 = PriceAlert(
            id=uuid4(),
            competitor_product_id=test_competitor_product.id,
            alert_type="price_increase",
            old_value="80.00",
            new_value="90.00",
            change_percent=Decimal("12.50"),
            created_at=datetime.utcnow() - timedelta(days=2)
        )
        db_session.add_all([alert1, alert2])
        await db_session.commit()

        service = ROIService(db_session)
        summary = await service.get_summary(period="month")

        # 應該有正的監測價值
        assert summary.competitor_monitoring_value > Decimal("0")

    @pytest.mark.asyncio
    async def test_monitoring_value_excludes_other_alert_types(
        self,
        db_session: AsyncSession,
        test_competitor_product: CompetitorProduct
    ):
        """測試只計算價格變動類型的告警"""
        # 創建庫存告警 (不應計入)
        alert = PriceAlert(
            id=uuid4(),
            competitor_product_id=test_competitor_product.id,
            alert_type="out_of_stock",
            old_value="in_stock",
            new_value="out_of_stock",
            change_percent=None,
            created_at=datetime.utcnow() - timedelta(days=1)
        )
        db_session.add(alert)
        await db_session.commit()

        service = ROIService(db_session)
        summary = await service.get_summary(period="month")

        # 庫存告警不計入監測價值
        assert summary.competitor_monitoring_value == Decimal("0")


class TestROITrends:
    """測試 ROI 趨勢數據"""

    @pytest.mark.asyncio
    async def test_get_trends_returns_correct_days(self, db_session: AsyncSession):
        """測試趨勢數據返回正確天數"""
        service = ROIService(db_session)
        response = await service.get_trends(days=7)

        # 應返回 7 天的數據點 (+1 因為包含當天)
        assert len(response.trends) >= 7

    @pytest.mark.asyncio
    async def test_get_trends_cumulative_value(self, db_session: AsyncSession, test_product: Product):
        """測試趨勢數據累計值正確"""
        # 創建兩個不同日期的提案
        proposal1 = PriceProposal(
            id=uuid4(),
            product_id=test_product.id,
            status=ProposalStatus.EXECUTED,
            current_price=Decimal("100.00"),
            final_price=Decimal("110.00"),
            executed_at=datetime.utcnow() - timedelta(days=2)
        )
        proposal2 = PriceProposal(
            id=uuid4(),
            product_id=test_product.id,
            status=ProposalStatus.EXECUTED,
            current_price=Decimal("100.00"),
            final_price=Decimal("115.00"),
            executed_at=datetime.utcnow() - timedelta(days=1)
        )
        db_session.add_all([proposal1, proposal2])
        await db_session.commit()

        service = ROIService(db_session)
        response = await service.get_trends(days=7)

        # 累計值應該遞增
        values = [t.cumulative_value for t in response.trends]
        for i in range(1, len(values)):
            assert values[i] >= values[i - 1], "累計值應該遞增"

    @pytest.mark.asyncio
    async def test_get_trends_fills_missing_days(self, db_session: AsyncSession):
        """測試沒有數據的日子也填充零值 (Spec: Sparse data handling)"""
        service = ROIService(db_session)
        response = await service.get_trends(days=7)

        # 即使沒有數據，也應返回連續日期序列
        dates = [t.date for t in response.trends]
        assert len(dates) == len(set(dates)), "日期應該唯一"

        # 檢查所有點都有值 (即使是零)
        for trend in response.trends:
            assert trend.ai_pricing is not None
            assert trend.monitoring is not None
            assert trend.cumulative_value is not None


class TestPricingImpact:
    """測試 AI 改價影響分析"""

    @pytest.mark.asyncio
    async def test_get_pricing_impact_empty(self, db_session: AsyncSession):
        """測試無數據時返回空列表"""
        service = ROIService(db_session)
        response = await service.get_pricing_impact(limit=10)

        assert response.proposals == []
        assert response.summary.total_proposals == 0
        assert response.summary.total_impact == Decimal("0")

    @pytest.mark.asyncio
    async def test_get_pricing_impact_sorted_by_impact(self, db_session: AsyncSession, test_product: Product):
        """測試結果按影響金額降序排列 (Spec: sorted by impact descending)"""
        # 創建多個影響不同的提案
        proposals = [
            PriceProposal(
                id=uuid4(),
                product_id=test_product.id,
                status=ProposalStatus.EXECUTED,
                current_price=Decimal("100.00"),
                final_price=Decimal("110.00"),  # 差異 10
                executed_at=datetime.utcnow()
            ),
            PriceProposal(
                id=uuid4(),
                product_id=test_product.id,
                status=ProposalStatus.EXECUTED,
                current_price=Decimal("100.00"),
                final_price=Decimal("150.00"),  # 差異 50
                executed_at=datetime.utcnow()
            ),
            PriceProposal(
                id=uuid4(),
                product_id=test_product.id,
                status=ProposalStatus.EXECUTED,
                current_price=Decimal("100.00"),
                final_price=Decimal("130.00"),  # 差異 30
                executed_at=datetime.utcnow()
            ),
        ]
        db_session.add_all(proposals)
        await db_session.commit()

        service = ROIService(db_session)
        response = await service.get_pricing_impact(limit=10)

        # 驗證降序排列
        impacts = [p.impact for p in response.proposals]
        assert impacts == sorted(impacts, reverse=True)

    @pytest.mark.asyncio
    async def test_get_pricing_impact_respects_limit(self, db_session: AsyncSession, test_product: Product):
        """測試 limit 參數正確限制結果數量"""
        # 創建 5 個提案
        for i in range(5):
            proposal = PriceProposal(
                id=uuid4(),
                product_id=test_product.id,
                status=ProposalStatus.EXECUTED,
                current_price=Decimal("100.00"),
                final_price=Decimal(f"{110 + i}.00"),
                executed_at=datetime.utcnow()
            )
            db_session.add(proposal)
        await db_session.commit()

        service = ROIService(db_session)
        response = await service.get_pricing_impact(limit=3)

        assert len(response.proposals) == 3


class TestCompetitorInsights:
    """測試競品監測洞察"""

    @pytest.mark.asyncio
    async def test_get_competitor_insights_empty(self, db_session: AsyncSession):
        """測試無數據時返回零值"""
        service = ROIService(db_session)
        insights = await service.get_competitor_insights(period="month")

        assert insights.price_alerts_triggered == 0
        assert insights.price_drops_detected == 0
        assert insights.price_increases_detected == 0
        assert insights.potential_savings == Decimal("0")

    @pytest.mark.asyncio
    async def test_get_competitor_insights_counts_correctly(
        self,
        db_session: AsyncSession,
        test_competitor_product: CompetitorProduct
    ):
        """測試正確統計各類告警"""
        alerts = [
            PriceAlert(
                id=uuid4(),
                competitor_product_id=test_competitor_product.id,
                alert_type="price_drop",
                change_percent=Decimal("-10.00"),
                created_at=datetime.utcnow()
            ),
            PriceAlert(
                id=uuid4(),
                competitor_product_id=test_competitor_product.id,
                alert_type="price_drop",
                change_percent=Decimal("-15.00"),
                created_at=datetime.utcnow()
            ),
            PriceAlert(
                id=uuid4(),
                competitor_product_id=test_competitor_product.id,
                alert_type="price_increase",
                change_percent=Decimal("5.00"),
                created_at=datetime.utcnow()
            ),
        ]
        db_session.add_all(alerts)
        await db_session.commit()

        service = ROIService(db_session)
        insights = await service.get_competitor_insights(period="month")

        assert insights.price_alerts_triggered == 3
        assert insights.price_drops_detected == 2
        assert insights.price_increases_detected == 1


# =============================================
# Test Fixtures
# =============================================

@pytest_asyncio.fixture
async def test_product(db_session: AsyncSession) -> Product:
    """創建測試商品"""
    product = Product(
        id=uuid4(),
        sku="TEST-ROI-001",
        name="ROI 測試商品",
        price=Decimal("100.00"),
        status="active"
    )
    db_session.add(product)
    await db_session.commit()
    await db_session.refresh(product)
    return product


@pytest_asyncio.fixture
async def test_competitor(db_session: AsyncSession) -> Competitor:
    """創建測試競爭對手"""
    competitor = Competitor(
        id=uuid4(),
        name="測試競爭對手",
        platform="hktvmall",
        is_active=True
    )
    db_session.add(competitor)
    await db_session.commit()
    await db_session.refresh(competitor)
    return competitor


@pytest_asyncio.fixture
async def test_competitor_product(db_session: AsyncSession, test_competitor: Competitor) -> CompetitorProduct:
    """創建測試競品商品"""
    product = CompetitorProduct(
        id=uuid4(),
        competitor_id=test_competitor.id,
        name="競品測試商品",
        url="https://example.com/test-product",
        is_active=True
    )
    db_session.add(product)
    await db_session.commit()
    await db_session.refresh(product)
    return product
