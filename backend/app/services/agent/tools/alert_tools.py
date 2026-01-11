# =============================================
# 警報工具
# 查詢和管理價格/庫存警報
# =============================================

from typing import Any, Dict, List, Optional
from datetime import datetime
from decimal import Decimal

from sqlalchemy import text

from .base import BaseTool, ToolResult
from .sql_helpers import validate_integer


class AlertQueryTool(BaseTool):
    """
    警報查詢工具

    查詢價格/庫存警報，支持按類型、已讀狀態篩選
    """

    name = "alert_query"
    description = "查詢價格和庫存警報，支持按類型、已讀狀態篩選"

    parameters = {
        "alert_type": {
            "type": "list",
            "description": "警報類型: price_drop, price_increase, out_of_stock, back_in_stock",
            "required": False
        },
        "is_read": {
            "type": "bool",
            "description": "已讀狀態篩選 (true/false)",
            "required": False
        },
        "is_notified": {
            "type": "bool",
            "description": "已通知狀態篩選",
            "required": False
        },
        "date_from": {
            "type": "str",
            "description": "開始日期 YYYY-MM-DD",
            "required": False
        },
        "limit": {
            "type": "int",
            "description": "返回數量，默認 50",
            "required": False
        }
    }

    async def execute(self, **kwargs) -> ToolResult:
        """執行警報查詢"""
        # 解析參數
        alert_type_filter = kwargs.get("alert_type", [])
        is_read = kwargs.get("is_read")
        is_notified = kwargs.get("is_notified")
        date_from = kwargs.get("date_from")
        limit = validate_integer(kwargs.get("limit", 50), default=50, min_val=1, max_val=200)

        # 構建查詢條件
        conditions = ["1=1"]
        params = {"limit": limit}

        if alert_type_filter:
            conditions.append("pa.alert_type = ANY(:alert_types)")
            params["alert_types"] = alert_type_filter

        if is_read is not None:
            conditions.append("pa.is_read = :is_read")
            params["is_read"] = is_read

        if is_notified is not None:
            conditions.append("pa.is_notified = :is_notified")
            params["is_notified"] = is_notified

        if date_from:
            conditions.append("pa.created_at >= :date_from")
            params["date_from"] = date_from

        where_clause = " AND ".join(conditions)

        sql = f"""
            SELECT
                pa.id,
                pa.alert_type,
                pa.old_value,
                pa.new_value,
                pa.change_percent,
                pa.is_read,
                pa.is_notified,
                pa.created_at,
                cp.name as product_name,
                cp.url as product_url,
                c.name as competitor_name
            FROM price_alerts pa
            JOIN competitor_products cp ON pa.competitor_product_id = cp.id
            JOIN competitors c ON cp.competitor_id = c.id
            WHERE {where_clause}
            ORDER BY pa.created_at DESC
            LIMIT :limit
        """

        try:
            result = await self.db.execute(text(sql), params)
            rows = result.fetchall()

            # 處理數據並分組
            alerts = []
            type_counts = {
                "price_drop": 0,
                "price_increase": 0,
                "out_of_stock": 0,
                "back_in_stock": 0
            }
            unread_count = 0

            for row in rows:
                row_dict = dict(row._mapping)

                alert_type = row_dict["alert_type"]
                if alert_type in type_counts:
                    type_counts[alert_type] += 1

                if not row_dict["is_read"]:
                    unread_count += 1

                alerts.append({
                    "id": str(row_dict["id"]),
                    "alert_type": alert_type,
                    "old_value": row_dict["old_value"],
                    "new_value": row_dict["new_value"],
                    "change_percent": float(row_dict["change_percent"]) if row_dict["change_percent"] else None,
                    "is_read": row_dict["is_read"],
                    "is_notified": row_dict["is_notified"],
                    "created_at": row_dict["created_at"].strftime("%Y-%m-%d %H:%M") if row_dict["created_at"] else None,
                    "product_name": row_dict["product_name"],
                    "product_url": row_dict["product_url"],
                    "competitor_name": row_dict["competitor_name"]
                })

            return ToolResult(
                tool_name=self.name,
                success=True,
                data={
                    "type": "alert_query",
                    "alerts": alerts,
                    "count": len(alerts),
                    "unread_count": unread_count,
                    "type_counts": type_counts,
                    "filters": {
                        "alert_type": alert_type_filter,
                        "is_read": is_read,
                        "date_from": date_from
                    }
                }
            )

        except Exception as e:
            # 回滾失敗的事務，避免影響後續數據庫操作
            await self.db.rollback()
            return ToolResult(
                tool_name=self.name,
                success=False,
                error=f"警報查詢失敗: {str(e)}"
            )


class AlertActionTool(BaseTool):
    """
    警報操作工具

    執行警報操作：標記已讀、批量標記等
    """

    name = "alert_action"
    description = "執行警報操作：標記已讀、標記全部已讀"

    parameters = {
        "action": {
            "type": "str",
            "description": "操作類型: mark_read (標記已讀), mark_all_read (全部標記已讀)",
            "required": True
        },
        "alert_ids": {
            "type": "list",
            "description": "警報 ID 列表（mark_read 時使用）",
            "required": False
        },
        "alert_type": {
            "type": "str",
            "description": "警報類型篩選（mark_all_read 時可用於限定範圍）",
            "required": False
        }
    }

    async def execute(self, **kwargs) -> ToolResult:
        """執行警報操作"""
        action = kwargs.get("action")
        alert_ids = kwargs.get("alert_ids", [])
        alert_type = kwargs.get("alert_type")

        if not action:
            return ToolResult(
                tool_name=self.name,
                success=False,
                error="請指定操作類型 (action)"
            )

        try:
            if action == "mark_read":
                # 標記特定警報為已讀
                if not alert_ids:
                    return ToolResult(
                        tool_name=self.name,
                        success=False,
                        error="標記已讀需要提供 alert_ids"
                    )

                sql = """
                    UPDATE price_alerts
                    SET is_read = true
                    WHERE id = ANY(:alert_ids) AND is_read = false
                """
                result = await self.db.execute(text(sql), {"alert_ids": alert_ids})
                await self.db.commit()

                return ToolResult(
                    tool_name=self.name,
                    success=True,
                    data={
                        "type": "alert_action",
                        "action": "mark_read",
                        "affected_count": result.rowcount,
                        "message": f"已將 {result.rowcount} 個警報標記為已讀"
                    }
                )

            elif action == "mark_all_read":
                # 標記全部警報為已讀
                conditions = ["is_read = false"]
                params = {}

                if alert_type:
                    conditions.append("alert_type = :alert_type")
                    params["alert_type"] = alert_type

                where_clause = " AND ".join(conditions)

                sql = f"""
                    UPDATE price_alerts
                    SET is_read = true
                    WHERE {where_clause}
                """
                result = await self.db.execute(text(sql), params)
                await self.db.commit()

                type_msg = f" ({alert_type})" if alert_type else ""
                return ToolResult(
                    tool_name=self.name,
                    success=True,
                    data={
                        "type": "alert_action",
                        "action": "mark_all_read",
                        "affected_count": result.rowcount,
                        "alert_type_filter": alert_type,
                        "message": f"已將 {result.rowcount} 個{type_msg}警報標記為已讀"
                    }
                )

            else:
                return ToolResult(
                    tool_name=self.name,
                    success=False,
                    error=f"不支援的操作類型: {action}"
                )

        except Exception as e:
            # 回滾失敗的事務，避免影響後續數據庫操作
            await self.db.rollback()
            return ToolResult(
                tool_name=self.name,
                success=False,
                error=f"警報操作失敗: {str(e)}"
            )
