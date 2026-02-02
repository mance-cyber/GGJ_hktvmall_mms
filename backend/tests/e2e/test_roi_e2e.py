# =============================================
# ROI 儀表板端到端測試
# 測試 API 到前端完整流程
# =============================================

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import uuid4

from app.models.product import Product
from app.models.pricing import PriceProposal, ProposalStatus
from app.models.competitor import Competitor, CompetitorProduct, PriceAlert


class TestROIApiEndpoints:
    """測試 ROI API 端點的完整流程"""

    @pytest.mark.asyncio
    async def test_roi_summary_endpoint_accessible(self, client: AsyncClient):
        """測試 ROI 摘要端點可訪問（公開端點）"""
        response = await client.get("/api/v1/roi/summary")
        # ROI 端點是公開的，用於展示平台價值
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_roi_summary_with_auth(self, client: AsyncClient, auth_headers: dict):
        """測試認證後可以獲取 ROI 摘要"""
        response = await client.get("/api/v1/roi/summary", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        # 驗證響應結構
        assert "total_value_generated" in data
        assert "ai_pricing_contribution" in data
        assert "competitor_monitoring_value" in data
        assert "risk_avoidance_value" in data
        assert "roi_percentage" in data
        assert "period_start" in data
        assert "period_end" in data

    @pytest.mark.asyncio
    async def test_roi_summary_period_parameter(self, client: AsyncClient, auth_headers: dict):
        """測試 period 參數工作正常"""
        periods = ["today", "week", "month", "quarter"]
        for period in periods:
            response = await client.get(
                f"/api/v1/roi/summary?period={period}",
                headers=auth_headers
            )
            assert response.status_code == 200, f"period={period} 失敗"

    @pytest.mark.asyncio
    async def test_roi_trends_endpoint(self, client: AsyncClient, auth_headers: dict):
        """測試 ROI 趨勢端點"""
        response = await client.get(
            "/api/v1/roi/trends?days=7",
            headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert "trends" in data
        assert "start_date" in data
        assert "end_date" in data
        assert "granularity" in data
        assert isinstance(data["trends"], list)

    @pytest.mark.asyncio
    async def test_roi_trends_with_granularity(self, client: AsyncClient, auth_headers: dict):
        """測試趨勢端點的 granularity 參數"""
        granularities = ["day", "week", "month"]
        for granularity in granularities:
            response = await client.get(
                f"/api/v1/roi/trends?days=30&granularity={granularity}",
                headers=auth_headers
            )
            assert response.status_code == 200, f"granularity={granularity} 失敗"
            assert response.json()["granularity"] == granularity

    @pytest.mark.asyncio
    async def test_roi_pricing_impact_endpoint(self, client: AsyncClient, auth_headers: dict):
        """測試改價影響端點"""
        response = await client.get(
            "/api/v1/roi/pricing-impact",
            headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert "proposals" in data
        assert "summary" in data
        assert isinstance(data["proposals"], list)
        # 驗證 summary 結構
        summary = data["summary"]
        assert "total_proposals" in summary
        assert "executed_count" in summary
        assert "total_impact" in summary

    @pytest.mark.asyncio
    async def test_roi_pricing_impact_limit(self, client: AsyncClient, auth_headers: dict):
        """測試 limit 參數限制結果數量"""
        response = await client.get(
            "/api/v1/roi/pricing-impact?limit=5",
            headers=auth_headers
        )
        assert response.status_code == 200
        # 無數據時應返回空列表，有數據時應不超過 limit
        data = response.json()
        assert len(data["proposals"]) <= 5

    @pytest.mark.asyncio
    async def test_roi_competitor_insights_endpoint(self, client: AsyncClient, auth_headers: dict):
        """測試競品洞察端點"""
        response = await client.get(
            "/api/v1/roi/competitor-insights",
            headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert "price_alerts_triggered" in data
        assert "price_drops_detected" in data
        assert "price_increases_detected" in data
        assert "potential_savings" in data
        assert "period" in data


class TestROIEndToEndWithData:
    """測試有數據時的 E2E 流程"""

    @pytest.mark.asyncio
    async def test_full_roi_flow_with_proposals(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        test_product_e2e: Product
    ):
        """測試完整流程：創建提案 -> 獲取 ROI 數據"""
        # 1. 創建已執行的改價提案
        proposal = PriceProposal(
            id=uuid4(),
            product_id=test_product_e2e.id,
            status=ProposalStatus.EXECUTED,
            current_price=Decimal("100.00"),
            proposed_price=Decimal("120.00"),
            final_price=Decimal("120.00"),
            executed_at=datetime.utcnow() - timedelta(days=1),
            reason="E2E 測試提案"
        )
        db_session.add(proposal)
        await db_session.commit()

        # 2. 調用 summary API
        response = await client.get(
            "/api/v1/roi/summary?period=week",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()

        # 3. 驗證 AI 貢獻被計算
        ai_contribution = float(data["ai_pricing_contribution"])
        assert ai_contribution > 0, "AI 定價貢獻應該大於 0"

        # 4. 調用 pricing-impact API
        impact_response = await client.get(
            "/api/v1/roi/pricing-impact",
            headers=auth_headers
        )
        assert impact_response.status_code == 200
        impact_data = impact_response.json()

        # 5. 驗證提案出現在影響列表中
        assert impact_data["summary"]["executed_count"] >= 1

    @pytest.mark.asyncio
    async def test_full_roi_flow_with_alerts(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        test_competitor_product_e2e: CompetitorProduct
    ):
        """測試完整流程：創建告警 -> 獲取競品洞察"""
        # 1. 創建價格告警
        alert = PriceAlert(
            id=uuid4(),
            competitor_product_id=test_competitor_product_e2e.id,
            alert_type="price_drop",
            old_value="100.00",
            new_value="85.00",
            change_percent=Decimal("-15.00"),
            created_at=datetime.utcnow() - timedelta(hours=1)
        )
        db_session.add(alert)
        await db_session.commit()

        # 2. 調用 competitor-insights API
        response = await client.get(
            "/api/v1/roi/competitor-insights?period=week",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()

        # 3. 驗證告警被統計
        assert data["price_alerts_triggered"] >= 1
        assert data["price_drops_detected"] >= 1


class TestROIPerformance:
    """測試 ROI API 性能"""

    @pytest.mark.asyncio
    async def test_roi_summary_response_time(self, client: AsyncClient, auth_headers: dict):
        """測試 ROI 摘要端點響應時間 < 500ms"""
        import time
        start = time.perf_counter()
        response = await client.get("/api/v1/roi/summary", headers=auth_headers)
        elapsed_ms = (time.perf_counter() - start) * 1000

        assert response.status_code == 200
        assert elapsed_ms < 500, f"響應時間 {elapsed_ms:.0f}ms 超過 500ms 限制"

    @pytest.mark.asyncio
    async def test_roi_trends_response_time(self, client: AsyncClient, auth_headers: dict):
        """測試 ROI 趨勢端點響應時間 < 500ms"""
        import time
        start = time.perf_counter()
        response = await client.get("/api/v1/roi/trends?days=30", headers=auth_headers)
        elapsed_ms = (time.perf_counter() - start) * 1000

        assert response.status_code == 200
        assert elapsed_ms < 500, f"響應時間 {elapsed_ms:.0f}ms 超過 500ms 限制"

    @pytest.mark.asyncio
    async def test_roi_pricing_impact_response_time(self, client: AsyncClient, auth_headers: dict):
        """測試改價影響端點響應時間 < 500ms"""
        import time
        start = time.perf_counter()
        response = await client.get("/api/v1/roi/pricing-impact", headers=auth_headers)
        elapsed_ms = (time.perf_counter() - start) * 1000

        assert response.status_code == 200
        assert elapsed_ms < 500, f"響應時間 {elapsed_ms:.0f}ms 超過 500ms 限制"

    @pytest.mark.asyncio
    async def test_roi_competitor_insights_response_time(self, client: AsyncClient, auth_headers: dict):
        """測試競品洞察端點響應時間 < 500ms"""
        import time
        start = time.perf_counter()
        response = await client.get("/api/v1/roi/competitor-insights", headers=auth_headers)
        elapsed_ms = (time.perf_counter() - start) * 1000

        assert response.status_code == 200
        assert elapsed_ms < 500, f"響應時間 {elapsed_ms:.0f}ms 超過 500ms 限制"


class TestROIApiValidation:
    """測試 API 參數驗證"""

    @pytest.mark.asyncio
    async def test_trends_days_validation(self, client: AsyncClient, auth_headers: dict):
        """測試 days 參數驗證"""
        # 超出範圍應返回 422
        response = await client.get(
            "/api/v1/roi/trends?days=400",
            headers=auth_headers
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_trends_negative_days_validation(self, client: AsyncClient, auth_headers: dict):
        """測試負數 days 參數驗證"""
        response = await client.get(
            "/api/v1/roi/trends?days=-1",
            headers=auth_headers
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_invalid_period_validation(self, client: AsyncClient, auth_headers: dict):
        """測試無效 period 參數"""
        response = await client.get(
            "/api/v1/roi/summary?period=invalid",
            headers=auth_headers
        )
        assert response.status_code == 422


# =============================================
# E2E Test Fixtures
# =============================================

import pytest_asyncio

@pytest_asyncio.fixture
async def test_product_e2e(db_session: AsyncSession) -> Product:
    """創建 E2E 測試商品"""
    product = Product(
        id=uuid4(),
        sku="E2E-ROI-001",
        name="E2E ROI 測試商品",
        price=Decimal("100.00"),
        status="active"
    )
    db_session.add(product)
    await db_session.commit()
    await db_session.refresh(product)
    return product


@pytest_asyncio.fixture
async def test_competitor_e2e(db_session: AsyncSession) -> Competitor:
    """創建 E2E 測試競爭對手"""
    competitor = Competitor(
        id=uuid4(),
        name="E2E 測試競爭對手",
        platform="hktvmall",
        is_active=True
    )
    db_session.add(competitor)
    await db_session.commit()
    await db_session.refresh(competitor)
    return competitor


@pytest_asyncio.fixture
async def test_competitor_product_e2e(
    db_session: AsyncSession,
    test_competitor_e2e: Competitor
) -> CompetitorProduct:
    """創建 E2E 測試競品商品"""
    product = CompetitorProduct(
        id=uuid4(),
        competitor_id=test_competitor_e2e.id,
        name="E2E 競品測試商品",
        url="https://example.com/e2e-test-product",
        is_active=True
    )
    db_session.add(product)
    await db_session.commit()
    await db_session.refresh(product)
    return product
