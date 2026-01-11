# =============================================
# 產品相關工具
# =============================================

from typing import Any, Dict
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from .base import BaseTool, ToolResult
from .sql_helpers import (
    escape_like_pattern,
    validate_integer,
    validate_float,
    validate_sort_column,
    build_product_search_conditions,
    build_product_case_statement,
)


class ProductOverviewTool(BaseTool):
    """
    產品概覽工具

    獲取產品的統計數據：SKU 數量、價格範圍、評分等
    """

    name = "product_overview"
    description = "獲取產品概覽數據，包括 SKU 數量、價格範圍、評分、庫存狀態等統計信息"
    parameters = {
        "products": {
            "type": "list",
            "required": True,
            "description": "產品名稱列表，如 ['和牛', '三文魚']"
        },
        "parts": {
            "type": "list",
            "required": False,
            "description": "部位篩選（適用於和牛等）"
        },
        "types": {
            "type": "list",
            "required": False,
            "description": "類型篩選（適用於海鮮等）"
        },
        "origin": {
            "type": "list",
            "required": False,
            "description": "產地篩選"
        }
    }

    async def execute(self, **kwargs) -> ToolResult:
        products = kwargs.get("products", [])

        if not products:
            return ToolResult(
                tool_name=self.name,
                success=False,
                error="請提供至少一個產品名稱"
            )

        # 構建安全的搜索條件
        where_clause, params = build_product_search_conditions(products)

        if not where_clause or where_clause == "1=1":
            return ToolResult(
                tool_name=self.name,
                success=False,
                error="無法構建搜索條件"
            )

        # 構建安全的產品分類 CASE 語句
        case_sql, _ = build_product_case_statement(products)

        query = f"""
            SELECT
                {case_sql} as product_type,
                COUNT(*) as sku_count,
                ROUND(AVG(price)::numeric, 0) as avg_price,
                MIN(price) as min_price,
                MAX(price) as max_price,
                ROUND(AVG(rating)::numeric, 2) as avg_rating,
                COALESCE(SUM(review_count), 0) as total_reviews,
                COUNT(*) FILTER (WHERE stock_status = 'in_stock' OR is_available = true) as in_stock_count,
                COUNT(*) FILTER (WHERE discount_percent > 0) as on_sale_count
            FROM category_products
            WHERE {where_clause}
            GROUP BY product_type
            ORDER BY sku_count DESC
        """

        try:
            result = await self.db.execute(text(query), params)
            rows = result.fetchall()

            data = []
            for row in rows:
                row_dict = dict(row._mapping)
                # 轉換 Decimal 為 float
                for key in ['avg_price', 'min_price', 'max_price', 'avg_rating']:
                    if row_dict.get(key) is not None:
                        row_dict[key] = float(row_dict[key])
                data.append(row_dict)

            return ToolResult(
                tool_name=self.name,
                success=True,
                data={
                    "type": "product_overview",
                    "products": products,
                    "results": data,
                    "total_skus": sum(d["sku_count"] for d in data)
                },
                metadata={"query_products": products}
            )
        except Exception as e:
            # 回滾失敗的事務，避免影響後續數據庫操作
            await self.db.rollback()
            return ToolResult(
                tool_name=self.name,
                success=False,
                error=f"查詢失敗: {str(e)}"
            )


class ProductSearchTool(BaseTool):
    """
    產品搜索工具

    搜索符合條件的具體產品
    """

    name = "product_search"
    description = "搜索符合條件的具體產品，返回產品列表"
    parameters = {
        "query": {
            "type": "str",
            "required": True,
            "description": "搜索關鍵詞"
        },
        "limit": {
            "type": "int",
            "required": False,
            "description": "返回數量上限，預設 20"
        },
        "min_price": {
            "type": "float",
            "required": False,
            "description": "最低價格"
        },
        "max_price": {
            "type": "float",
            "required": False,
            "description": "最高價格"
        },
        "in_stock_only": {
            "type": "bool",
            "required": False,
            "description": "只顯示有貨產品"
        }
    }

    async def execute(self, **kwargs) -> ToolResult:
        query = kwargs.get("query", "")
        limit = validate_integer(kwargs.get("limit", 20), default=20, min_val=1, max_val=100)
        min_price = kwargs.get("min_price")
        max_price = kwargs.get("max_price")
        in_stock_only = kwargs.get("in_stock_only", False)

        if not query:
            return ToolResult(
                tool_name=self.name,
                success=False,
                error="請提供搜索關鍵詞"
            )

        # 構建安全的 WHERE 條件
        safe_query = escape_like_pattern(query)
        conditions = ["name ILIKE :search_query"]
        params = {"search_query": f"%{safe_query}%", "limit": limit}

        if min_price is not None:
            safe_min = validate_float(min_price, default=0)
            conditions.append("price >= :min_price")
            params["min_price"] = safe_min

        if max_price is not None:
            safe_max = validate_float(max_price, default=999999)
            conditions.append("price <= :max_price")
            params["max_price"] = safe_max

        if in_stock_only:
            conditions.append("(stock_status = 'in_stock' OR is_available = true)")

        where_clause = " AND ".join(conditions)

        sql = f"""
            SELECT
                id,
                name,
                brand,
                price,
                original_price,
                discount_percent,
                rating,
                review_count,
                stock_status,
                is_available,
                image_url
            FROM category_products
            WHERE {where_clause}
            ORDER BY review_count DESC NULLS LAST
            LIMIT :limit
        """

        try:
            result = await self.db.execute(text(sql), params)
            rows = result.fetchall()

            data = []
            for row in rows:
                row_dict = dict(row._mapping)
                # 轉換類型
                for key in ['price', 'original_price', 'discount_percent', 'rating']:
                    if row_dict.get(key) is not None:
                        row_dict[key] = float(row_dict[key])
                row_dict['id'] = str(row_dict['id'])
                data.append(row_dict)

            return ToolResult(
                tool_name=self.name,
                success=True,
                data={
                    "type": "product_search",
                    "query": query,
                    "results": data,
                    "count": len(data)
                }
            )
        except Exception as e:
            # 回滾失敗的事務，避免影響後續數據庫操作
            await self.db.rollback()
            return ToolResult(
                tool_name=self.name,
                success=False,
                error=f"搜索失敗: {str(e)}"
            )


class TopProductsTool(BaseTool):
    """
    熱門產品工具

    獲取評論最多或評分最高的產品
    """

    name = "top_products"
    description = "獲取熱門產品（按評論數或評分排序）"
    parameters = {
        "products": {
            "type": "list",
            "required": True,
            "description": "產品類別列表"
        },
        "sort_by": {
            "type": "str",
            "required": False,
            "description": "排序方式: review_count（評論數）或 rating（評分），預設 review_count"
        },
        "limit": {
            "type": "int",
            "required": False,
            "description": "返回數量，預設 5"
        }
    }

    async def execute(self, **kwargs) -> ToolResult:
        products = kwargs.get("products", [])
        sort_by = validate_sort_column(
            kwargs.get("sort_by", "review_count"),
            allowed=["review_count", "rating"],
            default="review_count"
        )
        limit = validate_integer(kwargs.get("limit", 5), default=5, min_val=1, max_val=50)

        if not products:
            return ToolResult(
                tool_name=self.name,
                success=False,
                error="請提供產品類別"
            )

        # 構建安全的搜索條件
        where_clause, params = build_product_search_conditions(products)

        # 構建安全的分類 CASE 語句
        case_sql, _ = build_product_case_statement(products)

        # 計算總限制數量
        total_limit = limit * len(products)
        params["total_limit"] = total_limit

        sql = f"""
            SELECT
                {case_sql} as product_type,
                name,
                brand,
                price,
                original_price,
                discount_percent,
                rating,
                review_count,
                stock_status
            FROM category_products
            WHERE ({where_clause})
              AND {sort_by} IS NOT NULL
            ORDER BY {sort_by} DESC
            LIMIT :total_limit
        """

        try:
            result = await self.db.execute(text(sql), params)
            rows = result.fetchall()

            # 按產品類型分組
            grouped = {}
            for row in rows:
                row_dict = dict(row._mapping)
                product_type = row_dict.pop('product_type')

                # 轉換類型
                for key in ['price', 'original_price', 'discount_percent', 'rating']:
                    if row_dict.get(key) is not None:
                        row_dict[key] = float(row_dict[key])

                if product_type not in grouped:
                    grouped[product_type] = []

                if len(grouped[product_type]) < limit:
                    grouped[product_type].append(row_dict)

            return ToolResult(
                tool_name=self.name,
                success=True,
                data={
                    "type": "top_products",
                    "sort_by": sort_by,
                    "limit": limit,
                    "results": grouped
                }
            )
        except Exception as e:
            # 回滾失敗的事務，避免影響後續數據庫操作
            await self.db.rollback()
            return ToolResult(
                tool_name=self.name,
                success=False,
                error=f"查詢失敗: {str(e)}"
            )
