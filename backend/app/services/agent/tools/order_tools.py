# =============================================
# 訂單工具
# 訂單統計和搜索功能
# =============================================

from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy import text

from .base import BaseTool, ToolResult
from .sql_helpers import escape_like_pattern, validate_integer


class OrderStatsTool(BaseTool):
    """
    訂單統計工具

    統計訂單數據，支持按狀態、日期範圍篩選和分組
    """

    name = "order_stats"
    description = "統計訂單數據：訂單數量、金額、按狀態分組"

    parameters = {
        "status": {
            "type": "list",
            "description": "訂單狀態列表: Pending, Confirmed, Packing, Packed, Shipped, Delivered, Cancelled, Returned",
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
        "group_by": {
            "type": "str",
            "description": "分組方式: status (狀態), date (日期), delivery_mode (配送方式)",
            "required": False
        }
    }

    async def execute(self, **kwargs) -> ToolResult:
        """執行訂單統計"""
        # 解析參數
        status_filter = kwargs.get("status", [])
        date_from = kwargs.get("date_from")
        date_to = kwargs.get("date_to")
        group_by = kwargs.get("group_by", "status")

        # 默認日期範圍：今日
        if not date_from:
            date_from = datetime.now().strftime("%Y-%m-%d")
        if not date_to:
            date_to = datetime.now().strftime("%Y-%m-%d")

        # 構建查詢條件
        conditions = ["order_date >= :date_from", "order_date <= :date_to + INTERVAL '1 day'"]
        params = {
            "date_from": date_from,
            "date_to": date_to
        }

        if status_filter:
            conditions.append("status = ANY(:status_list)")
            params["status_list"] = status_filter

        where_clause = " AND ".join(conditions)

        # 根據分組方式構建 SQL
        if group_by == "date":
            sql = f"""
                SELECT
                    DATE(order_date) as group_key,
                    COUNT(*) as order_count,
                    COALESCE(SUM(total_amount), 0) as total_amount,
                    COALESCE(SUM(commission), 0) as total_commission
                FROM orders
                WHERE {where_clause}
                GROUP BY DATE(order_date)
                ORDER BY group_key DESC
            """
        elif group_by == "delivery_mode":
            sql = f"""
                SELECT
                    COALESCE(delivery_mode, '未知') as group_key,
                    COUNT(*) as order_count,
                    COALESCE(SUM(total_amount), 0) as total_amount,
                    COALESCE(SUM(commission), 0) as total_commission
                FROM orders
                WHERE {where_clause}
                GROUP BY delivery_mode
                ORDER BY order_count DESC
            """
        else:  # 默認按狀態分組
            sql = f"""
                SELECT
                    status as group_key,
                    COUNT(*) as order_count,
                    COALESCE(SUM(total_amount), 0) as total_amount,
                    COALESCE(SUM(commission), 0) as total_commission
                FROM orders
                WHERE {where_clause}
                GROUP BY status
                ORDER BY order_count DESC
            """

        try:
            result = await self.db.execute(text(sql), params)
            rows = result.fetchall()

            # 處理數據
            groups = []
            total_orders = 0
            total_amount = Decimal("0")
            total_commission = Decimal("0")

            for row in rows:
                row_dict = dict(row._mapping)
                # 轉換類型
                group_key = row_dict["group_key"]
                if isinstance(group_key, datetime):
                    group_key = group_key.strftime("%Y-%m-%d")

                order_count = int(row_dict["order_count"])
                amount = Decimal(str(row_dict["total_amount"]))
                commission = Decimal(str(row_dict["total_commission"]))

                groups.append({
                    "group": str(group_key),
                    "order_count": order_count,
                    "total_amount": float(amount),
                    "total_commission": float(commission)
                })

                total_orders += order_count
                total_amount += amount
                total_commission += commission

            # 計算未出貨訂單（特殊統計）
            pending_statuses = ["Pending", "Confirmed", "Packing", "Packed"]
            pending_count = sum(
                g["order_count"] for g in groups
                if g["group"] in pending_statuses
            ) if group_by == "status" else 0

            return ToolResult(
                tool_name=self.name,
                success=True,
                data={
                    "type": "order_stats",
                    "date_range": {"from": date_from, "to": date_to},
                    "group_by": group_by,
                    "groups": groups,
                    "summary": {
                        "total_orders": total_orders,
                        "total_amount": float(total_amount),
                        "total_commission": float(total_commission),
                        "pending_orders": pending_count
                    }
                }
            )

        except Exception as e:
            return ToolResult(
                tool_name=self.name,
                success=False,
                error=f"訂單統計失敗: {str(e)}"
            )


class OrderSearchTool(BaseTool):
    """
    訂單搜索工具

    搜索訂單，支持訂單號、狀態、日期範圍篩選
    """

    name = "order_search"
    description = "搜索訂單，支持訂單號、狀態、日期、金額篩選"

    parameters = {
        "order_number": {
            "type": "str",
            "description": "訂單號（支持模糊匹配）",
            "required": False
        },
        "status": {
            "type": "list",
            "description": "訂單狀態列表",
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
        "min_amount": {
            "type": "float",
            "description": "最低金額",
            "required": False
        },
        "max_amount": {
            "type": "float",
            "description": "最高金額",
            "required": False
        },
        "limit": {
            "type": "int",
            "description": "返回數量上限，默認 20",
            "required": False
        }
    }

    async def execute(self, **kwargs) -> ToolResult:
        """執行訂單搜索"""
        # 解析參數
        order_number = kwargs.get("order_number")
        status_filter = kwargs.get("status", [])
        date_from = kwargs.get("date_from")
        date_to = kwargs.get("date_to")
        min_amount = kwargs.get("min_amount")
        max_amount = kwargs.get("max_amount")
        limit = validate_integer(kwargs.get("limit", 20), default=20, min_val=1, max_val=100)

        # 構建查詢條件
        conditions = ["1=1"]
        params = {"limit": limit}

        if order_number:
            safe_order_num = escape_like_pattern(order_number)
            conditions.append("order_number ILIKE :order_number")
            params["order_number"] = f"%{safe_order_num}%"

        if status_filter:
            conditions.append("status = ANY(:status_list)")
            params["status_list"] = status_filter

        if date_from:
            conditions.append("order_date >= :date_from")
            params["date_from"] = date_from

        if date_to:
            conditions.append("order_date <= :date_to + INTERVAL '1 day'")
            params["date_to"] = date_to

        if min_amount is not None:
            conditions.append("total_amount >= :min_amount")
            params["min_amount"] = min_amount

        if max_amount is not None:
            conditions.append("total_amount <= :max_amount")
            params["max_amount"] = max_amount

        where_clause = " AND ".join(conditions)

        sql = f"""
            SELECT
                o.id,
                o.order_number,
                o.order_date,
                o.ship_by_date,
                o.status,
                o.hktv_status,
                o.total_amount,
                o.commission,
                o.delivery_mode,
                o.customer_region,
                (SELECT COUNT(*) FROM order_items WHERE order_id = o.id) as item_count
            FROM orders o
            WHERE {where_clause}
            ORDER BY o.order_date DESC
            LIMIT :limit
        """

        try:
            result = await self.db.execute(text(sql), params)
            rows = result.fetchall()

            orders = []
            for row in rows:
                row_dict = dict(row._mapping)

                # 轉換類型
                order_data = {
                    "id": str(row_dict["id"]),
                    "order_number": row_dict["order_number"],
                    "order_date": row_dict["order_date"].strftime("%Y-%m-%d %H:%M") if row_dict["order_date"] else None,
                    "ship_by_date": row_dict["ship_by_date"].strftime("%Y-%m-%d") if row_dict["ship_by_date"] else None,
                    "status": row_dict["status"],
                    "hktv_status": row_dict["hktv_status"],
                    "total_amount": float(row_dict["total_amount"]) if row_dict["total_amount"] else 0,
                    "commission": float(row_dict["commission"]) if row_dict["commission"] else 0,
                    "delivery_mode": row_dict["delivery_mode"],
                    "customer_region": row_dict["customer_region"],
                    "item_count": row_dict["item_count"]
                }
                orders.append(order_data)

            return ToolResult(
                tool_name=self.name,
                success=True,
                data={
                    "type": "order_search",
                    "results": orders,
                    "count": len(orders),
                    "filters": {
                        "order_number": order_number,
                        "status": status_filter,
                        "date_from": date_from,
                        "date_to": date_to
                    }
                }
            )

        except Exception as e:
            return ToolResult(
                tool_name=self.name,
                success=False,
                error=f"訂單搜索失敗: {str(e)}"
            )
