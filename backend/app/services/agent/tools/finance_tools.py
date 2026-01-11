# =============================================
# 財務工具
# 銷售查詢、財務摘要、結算單查詢
# =============================================

from typing import Dict, Any, List
from sqlalchemy import select, func, desc, text
from datetime import datetime, timedelta
from decimal import Decimal

from app.services.agent.tools.base import BaseTool, ToolResult
from app.models.finance import Settlement
from app.models.order import Order

class QuerySalesTool(BaseTool):
    name = "query_sales"
    description = "查詢銷售數據，支持按天/週/月聚合，可查詢營收(revenue)或利潤(profit)"
    parameters = {
        "metric": {
            "type": "string",
            "description": "指標類型: revenue (營收) 或 profit (利潤)",
            "required": True
        },
        "period": {
            "type": "string",
            "description": "時間範圍: last_7_days, last_30_days, this_month, last_month",
            "required": True
        }
    }

    async def execute(self, metric: str, period: str) -> ToolResult:
        # Determine date range
        now = datetime.now()
        start_date = now - timedelta(days=30)
        
        if period == "last_7_days":
            start_date = now - timedelta(days=7)
        elif period == "last_30_days":
            start_date = now - timedelta(days=30)
        elif period == "this_month":
            start_date = now.replace(day=1, hour=0, minute=0, second=0)
        elif period == "last_month":
            # First day of this month
            this_month_start = now.replace(day=1, hour=0, minute=0, second=0)
            # Last day of prev month
            last_month_end = this_month_start - timedelta(seconds=1)
            # First day of prev month
            start_date = last_month_end.replace(day=1, hour=0, minute=0, second=0)
            now = last_month_end

        # Query
        if metric == "revenue":
            query = select(
                func.sum(Settlement.total_sales_amount)
            ).where(
                Settlement.settlement_date >= start_date,
                Settlement.settlement_date <= now
            )
        else:
            query = select(
                func.sum(Settlement.net_settlement_amount)
            ).where(
                Settlement.settlement_date >= start_date,
                Settlement.settlement_date <= now
            )
            
        result = await self.db.execute(query)
        total = result.scalar() or 0
        
        return ToolResult(
            tool_name=self.name,
            success=True,
            data={
                "value": float(total),
                "currency": "HKD",
                "period": period,
                "metric": metric
            }
        )

class QueryTopProductsTool(BaseTool):
    name = "query_top_products"
    description = "查詢銷量最高或利潤最高的產品"
    parameters = {
        "by": {
            "type": "string",
            "description": "排序依據: sales (銷量), revenue (營收)",
            "required": True
        },
        "limit": {
            "type": "int",
            "description": "返回數量，默認 5",
            "required": False
        }
    }

    async def execute(self, by: str, limit: int = 5) -> ToolResult:
        # 由於 SettlementItem 才有具體產品銷售數據，我們查詢 SettlementItem
        from app.models.finance import SettlementItem
        
        if by == "sales":
            query = select(
                SettlementItem.product_name,
                func.sum(SettlementItem.quantity).label("total_qty")
            ).group_by(
                SettlementItem.product_name
            ).order_by(
                desc("total_qty")
            ).limit(limit)
            
            result = await self.db.execute(query)
            rows = result.all()
            
            data = [{"name": r.product_name, "value": r.total_qty} for r in rows]
            
        else: # revenue
            query = select(
                SettlementItem.product_name,
                func.sum(SettlementItem.item_price * SettlementItem.quantity).label("total_rev")
            ).group_by(
                SettlementItem.product_name
            ).order_by(
                desc("total_rev")
            ).limit(limit)
            
            result = await self.db.execute(query)
            rows = result.all()
            
            data = [{"name": r.product_name, "value": float(r.total_rev)} for r in rows]

        return ToolResult(
            tool_name=self.name,
            success=True,
            data={
                "items": data,
                "chart_type": "bar", # Hint for frontend
                "x_key": "name",
                "y_key": "value",
                "title": f"Top {limit} Products by {by}"
            }
        )


class FinanceSummaryTool(BaseTool):
    """
    財務摘要工具

    獲取財務摘要：營收、佣金、利潤等核心指標
    """

    name = "finance_summary"
    description = "獲取財務摘要：營收、佣金、淨利潤、訂單量等核心指標"

    parameters = {
        "period": {
            "type": "str",
            "description": "時間範圍: today, this_week, this_month, last_month, last_30_days, this_year",
            "required": True
        },
        "compare_period": {
            "type": "bool",
            "description": "是否與上期對比",
            "required": False
        }
    }

    def _get_date_range(self, period: str):
        """根據期間獲取日期範圍"""
        now = datetime.now()

        if period == "today":
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = now
        elif period == "this_week":
            start = now - timedelta(days=now.weekday())
            start = start.replace(hour=0, minute=0, second=0, microsecond=0)
            end = now
        elif period == "this_month":
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end = now
        elif period == "last_month":
            first_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end = first_of_month - timedelta(seconds=1)
            start = end.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif period == "last_30_days":
            start = now - timedelta(days=30)
            end = now
        elif period == "this_year":
            start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end = now
        else:
            # 默認最近 30 天
            start = now - timedelta(days=30)
            end = now

        return start, end

    async def execute(self, **kwargs) -> ToolResult:
        """執行財務摘要查詢"""
        period = kwargs.get("period", "last_30_days")
        compare_period = kwargs.get("compare_period", False)

        start_date, end_date = self._get_date_range(period)

        try:
            # 查詢結算數據
            settlement_sql = """
                SELECT
                    COALESCE(SUM(total_sales_amount), 0) as total_revenue,
                    COALESCE(SUM(total_commission), 0) as total_commission,
                    COALESCE(SUM(total_shipping_fee), 0) as total_shipping,
                    COALESCE(SUM(other_deductions), 0) as total_deductions,
                    COALESCE(SUM(net_settlement_amount), 0) as net_profit,
                    COUNT(*) as settlement_count
                FROM settlements
                WHERE settlement_date >= :start_date
                  AND settlement_date <= :end_date
            """

            settlement_result = await self.db.execute(
                text(settlement_sql),
                {"start_date": start_date, "end_date": end_date}
            )
            settlement_row = settlement_result.fetchone()

            # 查詢訂單數據
            order_sql = """
                SELECT
                    COUNT(*) as total_orders,
                    COALESCE(SUM(total_amount), 0) as gross_sales,
                    COALESCE(SUM(commission), 0) as platform_commission,
                    COALESCE(AVG(total_amount), 0) as avg_order_value
                FROM orders
                WHERE order_date >= :start_date
                  AND order_date <= :end_date
                  AND status NOT IN ('Cancelled', 'Returned')
            """

            order_result = await self.db.execute(
                text(order_sql),
                {"start_date": start_date, "end_date": end_date}
            )
            order_row = order_result.fetchone()

            # 組裝數據
            settlement_data = dict(settlement_row._mapping) if settlement_row else {}
            order_data = dict(order_row._mapping) if order_row else {}

            total_revenue = float(settlement_data.get("total_revenue", 0) or order_data.get("gross_sales", 0))
            total_commission = float(settlement_data.get("total_commission", 0) or order_data.get("platform_commission", 0))
            net_profit = float(settlement_data.get("net_profit", 0))

            # 計算利潤率
            profit_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0

            summary = {
                "period": period,
                "date_range": {
                    "from": start_date.strftime("%Y-%m-%d"),
                    "to": end_date.strftime("%Y-%m-%d")
                },
                "revenue": {
                    "total": total_revenue,
                    "currency": "HKD"
                },
                "commission": {
                    "total": total_commission,
                    "rate": (total_commission / total_revenue * 100) if total_revenue > 0 else 0
                },
                "profit": {
                    "net": net_profit,
                    "margin": round(profit_margin, 2)
                },
                "orders": {
                    "count": int(order_data.get("total_orders", 0)),
                    "avg_value": float(order_data.get("avg_order_value", 0))
                },
                "settlements": {
                    "count": int(settlement_data.get("settlement_count", 0))
                }
            }

            return ToolResult(
                tool_name=self.name,
                success=True,
                data={
                    "type": "finance_summary",
                    "summary": summary
                }
            )

        except Exception as e:
            # 回滾失敗的事務，避免影響後續數據庫操作
            await self.db.rollback()
            return ToolResult(
                tool_name=self.name,
                success=False,
                error=f"財務摘要查詢失敗: {str(e)}"
            )


class SettlementQueryTool(BaseTool):
    """
    結算單查詢工具

    查詢結算單，支持按日期範圍、結算單號篩選
    """

    name = "settlement_query"
    description = "查詢結算單列表，支持按日期範圍篩選"

    parameters = {
        "statement_no": {
            "type": "str",
            "description": "結算單號（精確匹配）",
            "required": False
        },
        "date_from": {
            "type": "str",
            "description": "開始日期 YYYY-MM-DD",
            "required": False
        },
        "date_to": {
            "type": "str",
            "description": "結束日期 YYYY-MM-DD",
            "required": False
        },
        "limit": {
            "type": "int",
            "description": "返回數量，默認 10",
            "required": False
        }
    }

    async def execute(self, **kwargs) -> ToolResult:
        """執行結算單查詢"""
        statement_no = kwargs.get("statement_no")
        date_from = kwargs.get("date_from")
        date_to = kwargs.get("date_to")
        limit = kwargs.get("limit", 10)

        if limit > 50:
            limit = 50

        # 構建查詢條件
        conditions = ["1=1"]
        params = {"limit": limit}

        if statement_no:
            conditions.append("statement_no = :statement_no")
            params["statement_no"] = statement_no

        if date_from:
            conditions.append("settlement_date >= :date_from")
            params["date_from"] = date_from

        if date_to:
            conditions.append("settlement_date <= :date_to")
            params["date_to"] = date_to

        where_clause = " AND ".join(conditions)

        sql = f"""
            SELECT
                id,
                statement_no,
                cycle_start,
                cycle_end,
                settlement_date,
                total_sales_amount,
                total_commission,
                total_shipping_fee,
                other_deductions,
                net_settlement_amount,
                currency,
                status
            FROM settlements
            WHERE {where_clause}
            ORDER BY settlement_date DESC
            LIMIT :limit
        """

        try:
            result = await self.db.execute(text(sql), params)
            rows = result.fetchall()

            settlements = []
            for row in rows:
                row_dict = dict(row._mapping)
                settlements.append({
                    "id": str(row_dict["id"]),
                    "statement_no": row_dict["statement_no"],
                    "cycle_start": row_dict["cycle_start"].strftime("%Y-%m-%d") if row_dict["cycle_start"] else None,
                    "cycle_end": row_dict["cycle_end"].strftime("%Y-%m-%d") if row_dict["cycle_end"] else None,
                    "settlement_date": row_dict["settlement_date"].strftime("%Y-%m-%d") if row_dict["settlement_date"] else None,
                    "total_sales_amount": float(row_dict["total_sales_amount"]) if row_dict["total_sales_amount"] else 0,
                    "total_commission": float(row_dict["total_commission"]) if row_dict["total_commission"] else 0,
                    "total_shipping_fee": float(row_dict["total_shipping_fee"]) if row_dict["total_shipping_fee"] else 0,
                    "other_deductions": float(row_dict["other_deductions"]) if row_dict["other_deductions"] else 0,
                    "net_settlement_amount": float(row_dict["net_settlement_amount"]) if row_dict["net_settlement_amount"] else 0,
                    "currency": row_dict["currency"],
                    "status": row_dict["status"]
                })

            return ToolResult(
                tool_name=self.name,
                success=True,
                data={
                    "type": "settlement_query",
                    "settlements": settlements,
                    "count": len(settlements),
                    "filters": {
                        "statement_no": statement_no,
                        "date_from": date_from,
                        "date_to": date_to
                    }
                }
            )

        except Exception as e:
            # 回滾失敗的事務，避免影響後續數據庫操作
            await self.db.rollback()
            return ToolResult(
                tool_name=self.name,
                success=False,
                error=f"結算單查詢失敗: {str(e)}"
            )
