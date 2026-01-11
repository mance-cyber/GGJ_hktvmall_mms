# =============================================
# 價格相關工具
# =============================================

from typing import Any, Dict, List
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from .base import BaseTool, ToolResult
from .sql_helpers import (
    validate_integer,
    validate_group_by,
    build_product_search_conditions,
    build_product_case_statement,
    build_interval_days,
)


class PriceTrendTool(BaseTool):
    """
    價格趨勢工具

    獲取產品的價格變化趨勢
    """

    name = "price_trend"
    description = "獲取產品價格隨時間變化的趨勢數據"
    parameters = {
        "products": {
            "type": "list",
            "required": True,
            "description": "產品名稱列表"
        },
        "days": {
            "type": "int",
            "required": False,
            "description": "時間範圍（天數），預設 30"
        },
        "group_by": {
            "type": "str",
            "required": False,
            "description": "分組方式: day（每日）或 week（每週），預設 week"
        }
    }

    async def execute(self, **kwargs) -> ToolResult:
        products = kwargs.get("products", [])
        days = validate_integer(kwargs.get("days", 30), default=30, min_val=1, max_val=365)
        group_by = validate_group_by(kwargs.get("group_by", "week"), ["day", "week"])

        if not products:
            return ToolResult(
                tool_name=self.name,
                success=False,
                error="請提供產品名稱"
            )

        # 構建安全的搜索條件
        where_clause, params = build_product_search_conditions(
            products, column="name", table_alias="cp"
        )

        # 構建安全的分類 CASE 語句
        case_sql, _ = build_product_case_statement(
            products, column="name", table_alias="cp"
        )

        # 安全的天數
        safe_days = build_interval_days(days)

        sql = f"""
            SELECT
                DATE_TRUNC(:date_trunc, cps.scraped_at) as period,
                {case_sql} as product_type,
                ROUND(AVG(cps.price)::numeric, 0) as avg_price,
                MIN(cps.price) as min_price,
                MAX(cps.price) as max_price,
                COUNT(DISTINCT cp.id) as product_count
            FROM category_price_snapshots cps
            JOIN category_products cp ON cps.category_product_id = cp.id
            WHERE ({where_clause})
              AND cps.scraped_at > NOW() - INTERVAL '{safe_days} days'
            GROUP BY period, product_type
            ORDER BY period, product_type
        """

        # 添加 date_trunc 參數
        params["date_trunc"] = group_by

        try:
            result = await self.db.execute(text(sql), params)
            rows = result.fetchall()

            # 按產品類型組織數據
            trend_data = {}
            for row in rows:
                row_dict = dict(row._mapping)
                product_type = row_dict["product_type"]

                if product_type not in trend_data:
                    trend_data[product_type] = []

                trend_data[product_type].append({
                    "period": row_dict["period"].isoformat() if row_dict["period"] else None,
                    "avg_price": float(row_dict["avg_price"]) if row_dict["avg_price"] else None,
                    "min_price": float(row_dict["min_price"]) if row_dict["min_price"] else None,
                    "max_price": float(row_dict["max_price"]) if row_dict["max_price"] else None,
                    "product_count": row_dict["product_count"]
                })

            # 計算價格變化
            for product_type, data in trend_data.items():
                if len(data) >= 2:
                    first_price = data[0]["avg_price"]
                    last_price = data[-1]["avg_price"]
                    if first_price and last_price and first_price > 0:
                        change_pct = ((last_price - first_price) / first_price) * 100
                        trend_data[product_type] = {
                            "data": data,
                            "change_pct": round(change_pct, 1),
                            "trend": "up" if change_pct > 0 else "down" if change_pct < 0 else "stable"
                        }
                    else:
                        trend_data[product_type] = {"data": data, "change_pct": 0, "trend": "stable"}
                else:
                    trend_data[product_type] = {"data": data, "change_pct": 0, "trend": "insufficient_data"}

            return ToolResult(
                tool_name=self.name,
                success=True,
                data={
                    "type": "price_trend",
                    "days": days,
                    "group_by": group_by,
                    "results": trend_data
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


class PriceComparisonTool(BaseTool):
    """
    價格比較工具

    比較不同產品的價格
    """

    name = "price_comparison"
    description = "比較多個產品的價格（每 100g 單價等）"
    parameters = {
        "products": {
            "type": "list",
            "required": True,
            "description": "產品名稱列表"
        },
        "compare_by": {
            "type": "str",
            "required": False,
            "description": "比較維度: price（總價）或 unit_price（單價），預設 price"
        }
    }

    async def execute(self, **kwargs) -> ToolResult:
        products = kwargs.get("products", [])
        compare_by = kwargs.get("compare_by", "price")

        if not products:
            return ToolResult(
                tool_name=self.name,
                success=False,
                error="請提供產品名稱"
            )

        # 構建安全的搜索條件
        where_clause, params = build_product_search_conditions(products)

        # 構建安全的分類 CASE 語句
        case_sql, _ = build_product_case_statement(products)

        # 驗證價格欄位（白名單）
        price_col = "unit_price" if compare_by == "unit_price" else "price"

        sql = f"""
            SELECT
                {case_sql} as product_type,
                COUNT(*) as product_count,
                ROUND(AVG({price_col})::numeric, 2) as avg_price,
                ROUND(MIN({price_col})::numeric, 2) as min_price,
                ROUND(MAX({price_col})::numeric, 2) as max_price,
                ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY {price_col})::numeric, 2) as median_price
            FROM category_products
            WHERE ({where_clause})
              AND {price_col} IS NOT NULL
              AND {price_col} > 0
            GROUP BY product_type
            ORDER BY avg_price DESC
        """

        try:
            result = await self.db.execute(text(sql), params)
            rows = result.fetchall()

            data = []
            for row in rows:
                row_dict = dict(row._mapping)
                # 轉換 Decimal
                for key in ['avg_price', 'min_price', 'max_price', 'median_price']:
                    if row_dict.get(key) is not None:
                        row_dict[key] = float(row_dict[key])
                data.append(row_dict)

            return ToolResult(
                tool_name=self.name,
                success=True,
                data={
                    "type": "price_comparison",
                    "compare_by": compare_by,
                    "results": data
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
