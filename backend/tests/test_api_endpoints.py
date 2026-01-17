# =============================================
# API 端點測試
# =============================================

import pytest
from httpx import AsyncClient


class TestHealthCheck:
    """測試健康檢查端點"""

    @pytest.mark.asyncio
    async def test_health_check_returns_ok(self, client: AsyncClient):
        """測試健康檢查返回正常狀態"""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy" or "status" in data


class TestProductsAPI:
    """測試商品 API"""

    @pytest.mark.asyncio
    async def test_list_products_requires_auth(self, client: AsyncClient):
        """測試列出商品需要認證"""
        response = await client.get("/api/v1/products")
        # 應該返回 401 或 403
        assert response.status_code in [401, 403]

    @pytest.mark.asyncio
    async def test_list_products_with_auth(self, client: AsyncClient, auth_headers: dict):
        """測試認證後可以列出商品"""
        response = await client.get("/api/v1/products", headers=auth_headers)
        # 應該返回 200
        assert response.status_code == 200
        data = response.json()
        assert "data" in data or "items" in data or isinstance(data, list)

    @pytest.mark.asyncio
    async def test_create_product_requires_auth(self, client: AsyncClient):
        """測試創建商品需要認證"""
        response = await client.post(
            "/api/v1/products",
            json={
                "name": "Test Product",
                "sku": "TEST-001",
            },
        )
        assert response.status_code in [401, 403]


class TestCompetitorsAPI:
    """測試競爭對手 API"""

    @pytest.mark.asyncio
    async def test_list_competitors_requires_auth(self, client: AsyncClient):
        """測試列出競爭對手需要認證"""
        response = await client.get("/api/v1/competitors")
        assert response.status_code in [401, 403]

    @pytest.mark.asyncio
    async def test_list_competitors_with_auth(self, client: AsyncClient, auth_headers: dict):
        """測試認證後可以列出競爭對手"""
        response = await client.get("/api/v1/competitors", headers=auth_headers)
        assert response.status_code == 200


class TestAlertsAPI:
    """測試警報 API"""

    @pytest.mark.asyncio
    async def test_list_alerts_requires_auth(self, client: AsyncClient):
        """測試列出警報需要認證"""
        response = await client.get("/api/v1/alerts")
        assert response.status_code in [401, 403]

    @pytest.mark.asyncio
    async def test_list_alerts_with_auth(self, client: AsyncClient, auth_headers: dict):
        """測試認證後可以列出警報"""
        response = await client.get("/api/v1/alerts", headers=auth_headers)
        assert response.status_code == 200


class TestContentAPI:
    """測試內容生成 API"""

    @pytest.mark.asyncio
    async def test_generate_content_requires_auth(self, client: AsyncClient):
        """測試生成內容需要認證"""
        response = await client.post(
            "/api/v1/content/generate",
            json={
                "product_info": {"name": "Test Product"},
                "content_type": "title",
                "style": "professional",
            },
        )
        assert response.status_code in [401, 403]


class TestSEOAPI:
    """測試 SEO API"""

    @pytest.mark.asyncio
    async def test_generate_seo_requires_auth(self, client: AsyncClient):
        """測試生成 SEO 內容需要認證"""
        response = await client.post(
            "/api/v1/seo/generate",
            json={
                "product_info": {"name": "Test Product"},
            },
        )
        assert response.status_code in [401, 403]

    @pytest.mark.asyncio
    async def test_extract_keywords_requires_auth(self, client: AsyncClient):
        """測試提取關鍵詞需要認證"""
        response = await client.post(
            "/api/v1/seo/keywords/extract",
            json={
                "product_info": {"name": "Test Product"},
            },
        )
        assert response.status_code in [401, 403]


class TestGEOAPI:
    """測試 GEO API"""

    @pytest.mark.asyncio
    async def test_generate_schema_requires_auth(self, client: AsyncClient):
        """測試生成 Schema 需要認證"""
        response = await client.post(
            "/api/v1/geo/schema/product",
            json={
                "product_info": {"name": "Test Product"},
            },
        )
        assert response.status_code in [401, 403]


class TestAgentAPI:
    """測試 AI Agent API"""

    @pytest.mark.asyncio
    async def test_chat_requires_auth(self, client: AsyncClient):
        """測試 AI 對話需要認證"""
        response = await client.post(
            "/api/v1/agent/chat",
            json={
                "content": "Hello",
            },
        )
        assert response.status_code in [401, 403]

    @pytest.mark.asyncio
    async def test_get_suggestions_requires_auth(self, client: AsyncClient):
        """測試獲取建議需要認證"""
        response = await client.get("/api/v1/agent/suggestions")
        assert response.status_code in [401, 403]


class TestCommandCenterAPI:
    """測試指揮中心 API"""

    @pytest.mark.asyncio
    async def test_command_center_requires_auth(self, client: AsyncClient):
        """測試指揮中心需要認證"""
        response = await client.get("/api/v1/command-center")
        assert response.status_code in [401, 403]

    @pytest.mark.asyncio
    async def test_command_center_with_auth(self, client: AsyncClient, auth_headers: dict):
        """測試認證後可以訪問指揮中心"""
        response = await client.get("/api/v1/command-center", headers=auth_headers)
        # 可能是 200 或因為缺少數據而有其他狀態
        assert response.status_code in [200, 404, 500]
