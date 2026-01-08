# =============================================
# 競爭對手相關工具
# =============================================

from typing import Dict
from sqlalchemy import text

from .base import BaseTool, ToolResult
from .sql_helpers import (
    escape_identifier,
    build_product_search_conditions,
    build_product_case_statement,
)


class CompetitorCompareTool(BaseTool):
    """
    競爭對手比較工具

    比較我們和競爭對手的產品價格
    """

    name = "competitor_compare"
    description = "比較 HKTVmall 和其他平台（如百佳、惠康）的產品價格"
    parameters = {
        "products": {
            "type": "list",
            "required": True,
            "description": "產品名稱列表"
        },
        "competitors": {
            "type": "list",
            "required": False,
            "description": "競爭對手列表（留空則比較所有競爭對手）"
        }
    }

    async def execute(self, **kwargs) -> ToolResult:
        products = kwargs.get("products", [])
        competitors = kwargs.get("competitors", [])

        if not products:
            return ToolResult(
                tool_name=self.name,
                success=False,
                error="請提供產品名稱"
            )

        # 構建安全的產品搜索條件
        product_where, product_params = build_product_search_conditions(products)

        # 構建安全的分類 CASE 語句
        case_sql, _ = build_product_case_statement(products)

        results = {
            "our_data": [],
            "competitor_data": []
        }

        # 查詢我們的數據（category_products）
        our_sql = f"""
            SELECT
                'HKTVmall' as platform,
                {case_sql} as product_type,
                COUNT(*) as sku_count,
                ROUND(AVG(price)::numeric, 0) as avg_price,
                MIN(price) as min_price,
                MAX(price) as max_price
            FROM category_products
            WHERE ({product_where})
              AND price IS NOT NULL
              AND price > 0
            GROUP BY product_type
        """

        try:
            result = await self.db.execute(text(our_sql), product_params)
            for row in result.fetchall():
                row_dict = dict(row._mapping)
                for key in ['avg_price', 'min_price', 'max_price']:
                    if row_dict.get(key) is not None:
                        row_dict[key] = float(row_dict[key])
                results["our_data"].append(row_dict)
        except Exception:
            # 如果查詢失敗，繼續嘗試競爭對手數據
            pass

        # 構建競爭對手過濾條件（安全方式）
        competitor_params = dict(product_params)  # 複製產品參數
        competitor_where_clause = ""

        if competitors:
            # 使用參數化查詢處理競爭對手名稱
            competitor_placeholders = []
            for i, comp in enumerate(competitors):
                param_name = f"competitor_{i}"
                safe_comp = escape_identifier(comp)
                competitor_params[param_name] = safe_comp
                competitor_placeholders.append(f":{param_name}")

            competitor_where_clause = f"AND c.name IN ({', '.join(competitor_placeholders)})"

        # 調整 CASE 語句以使用 cp 別名
        product_where_cp, cp_params = build_product_search_conditions(
            products, column="name", table_alias="cp"
        )
        case_sql_cp, _ = build_product_case_statement(
            products, column="name", table_alias="cp"
        )

        # 合併參數
        for key, val in cp_params.items():
            competitor_params[f"cp_{key}"] = val

        # 更新 WHERE 條件中的參數名
        product_where_cp_renamed = product_where_cp
        for key in cp_params.keys():
            product_where_cp_renamed = product_where_cp_renamed.replace(
                f":{key}", f":cp_{key}"
            )

        competitor_sql = f"""
            SELECT
                c.name as platform,
                {case_sql_cp} as product_type,
                COUNT(*) as sku_count,
                ROUND(AVG(ps.price)::numeric, 0) as avg_price,
                MIN(ps.price) as min_price,
                MAX(ps.price) as max_price
            FROM competitor_products cp
            JOIN competitors c ON cp.competitor_id = c.id
            JOIN price_snapshots ps ON cp.id = ps.competitor_product_id
            WHERE ({product_where_cp_renamed})
              AND ps.price IS NOT NULL
              AND ps.price > 0
              {competitor_where_clause}
              AND ps.scraped_at = (
                  SELECT MAX(scraped_at)
                  FROM price_snapshots
                  WHERE competitor_product_id = cp.id
              )
            GROUP BY c.name, product_type
            ORDER BY c.name, product_type
        """

        try:
            result = await self.db.execute(text(competitor_sql), competitor_params)
            for row in result.fetchall():
                row_dict = dict(row._mapping)
                for key in ['avg_price', 'min_price', 'max_price']:
                    if row_dict.get(key) is not None:
                        row_dict[key] = float(row_dict[key])
                results["competitor_data"].append(row_dict)
        except Exception:
            pass

        # 計算價格差異
        comparison = self._calculate_comparison(results)

        return ToolResult(
            tool_name=self.name,
            success=True,
            data={
                "type": "competitor_compare",
                "products": products,
                "our_data": results["our_data"],
                "competitor_data": results["competitor_data"],
                "comparison": comparison
            }
        )

    def _calculate_comparison(self, results: Dict) -> Dict:
        """計算價格差異比較"""
        comparison = {}

        # 以 HKTVmall 為基準
        our_prices = {}
        for item in results.get("our_data", []):
            product_type = item.get("product_type")
            our_prices[product_type] = item.get("avg_price", 0)

        # 與競爭對手比較
        for item in results.get("competitor_data", []):
            platform = item.get("platform")
            product_type = item.get("product_type")
            their_price = item.get("avg_price", 0)
            our_price = our_prices.get(product_type, 0)

            if platform not in comparison:
                comparison[platform] = {}

            if our_price and their_price:
                diff = their_price - our_price
                diff_pct = (diff / our_price) * 100
                comparison[platform][product_type] = {
                    "our_price": our_price,
                    "their_price": their_price,
                    "diff": round(diff, 0),
                    "diff_pct": round(diff_pct, 1),
                    "we_are_cheaper": diff > 0
                }

        return comparison
