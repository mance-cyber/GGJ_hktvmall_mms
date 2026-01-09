# =============================================
# 工具執行器
# 根據意圖和槽位執行相應的工具
# =============================================

from typing import Any, Dict, List, Optional
import asyncio
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from .intent_classifier import IntentType
from .slot_manager import AnalysisSlots
from .tools import (
    BaseTool,
    ToolResult,
    ProductOverviewTool,
    ProductSearchTool,
    TopProductsTool,
    PriceTrendTool,
    PriceComparisonTool,
    CompetitorCompareTool,
    QuerySalesTool,
    QueryTopProductsTool,
    # 新增工具
    FinanceSummaryTool,
    SettlementQueryTool,
    OrderStatsTool,
    OrderSearchTool,
    AlertQueryTool,
    AlertActionTool,
    NotificationSendTool,
)


@dataclass
class ExecutionPlan:
    """執行計劃"""
    tools: List[str]
    parallel: bool = True
    context: Dict[str, Any] = None


class ToolExecutor:
    """
    工具執行器
    
    根據意圖和槽位決定執行哪些工具，並管理執行流程
    """
    
    # 意圖 -> 工具映射
    INTENT_TOOL_MAPPING = {
        # 產品相關
        IntentType.PRODUCT_SEARCH: ["product_search"],
        IntentType.PRODUCT_DETAIL: ["product_search"],
        IntentType.PRICE_ANALYSIS: ["product_overview", "price_comparison"],
        IntentType.TREND_ANALYSIS: ["price_trend", "product_overview"],
        IntentType.COMPETITOR_ANALYSIS: ["competitor_compare", "product_overview"],
        IntentType.BRAND_ANALYSIS: ["top_products", "product_overview"],
        IntentType.MARKET_OVERVIEW: ["product_overview", "price_trend", "top_products", "competitor_compare"],
        IntentType.GENERATE_REPORT: ["product_overview", "price_trend", "competitor_compare", "top_products"],
        IntentType.MARKETING_STRATEGY: ["product_overview", "price_trend", "competitor_compare", "top_products"],

        # 訂單相關
        IntentType.ORDER_STATS: ["order_stats"],
        IntentType.ORDER_SEARCH: ["order_search"],

        # 財務相關
        IntentType.FINANCE_SUMMARY: ["finance_summary"],
        IntentType.SETTLEMENT_QUERY: ["settlement_query"],

        # 警報相關
        IntentType.ALERT_QUERY: ["alert_query"],
        IntentType.ALERT_ACTION: ["alert_action"],

        # 通知相關
        IntentType.SEND_NOTIFICATION: ["notification_send"],

        # 舊意圖 (保留向後兼容)
        IntentType.FINANCE_ANALYSIS: ["finance_summary", "query_sales"],
        IntentType.ORDER_QUERY: ["order_stats"],
        IntentType.INVENTORY_QUERY: ["query_top_products"],
    }
    
    def __init__(self, db: AsyncSession):
        self.db = db

        # 初始化所有工具
        self.tools: Dict[str, BaseTool] = {
            # 產品工具
            "product_overview": ProductOverviewTool(db),
            "product_search": ProductSearchTool(db),
            "top_products": TopProductsTool(db),
            "price_trend": PriceTrendTool(db),
            "price_comparison": PriceComparisonTool(db),
            "competitor_compare": CompetitorCompareTool(db),
            "query_sales": QuerySalesTool(db),
            "query_top_products": QueryTopProductsTool(db),
            # 訂單工具
            "order_stats": OrderStatsTool(db),
            "order_search": OrderSearchTool(db),
            # 財務工具
            "finance_summary": FinanceSummaryTool(db),
            "settlement_query": SettlementQueryTool(db),
            # 警報工具
            "alert_query": AlertQueryTool(db),
            "alert_action": AlertActionTool(db),
            # 通知工具 (不需要 db)
            "notification_send": NotificationSendTool(),
        }
    
    def get_execution_plan(
        self,
        intent: IntentType,
        slots: AnalysisSlots
    ) -> ExecutionPlan:
        """獲取執行計劃"""
        # 獲取該意圖需要的工具
        tools = self.INTENT_TOOL_MAPPING.get(intent, [])
        
        # 根據槽位調整
        if not slots.include_competitors and "competitor_compare" in tools:
            tools = [t for t in tools if t != "competitor_compare"]
        
        # 根據分析維度調整 (僅適用於產品分析意圖)
        if slots.analysis_dimensions and intent in [IntentType.MARKET_OVERVIEW, IntentType.PRICE_ANALYSIS]:
            dimension_tools = {
                "price_overview": ["product_overview"],
                "price_trend": ["price_trend"],
                "competitor_compare": ["competitor_compare"],
                "brand_analysis": ["top_products"],
                "top_products": ["top_products"],
            }
            
            filtered_tools = []
            for dim in slots.analysis_dimensions:
                for tool in dimension_tools.get(dim, []):
                    if tool not in filtered_tools and tool in self.tools:
                        filtered_tools.append(tool)
            
            if filtered_tools:
                tools = filtered_tools
        
        return ExecutionPlan(
            tools=tools,
            parallel=True,
            context={"intent": intent.value, "slots": slots.to_dict()}
        )
    
    async def execute(
        self,
        intent: IntentType,
        slots: AnalysisSlots
    ) -> Dict[str, ToolResult]:
        """執行工具並返回結果"""
        plan = self.get_execution_plan(intent, slots)
        
        if not plan.tools:
            return {}
        
        # 準備參數
        base_params = self._prepare_params(slots, intent)
        
        if plan.parallel:
            # 並行執行
            results = await self._execute_parallel(plan.tools, base_params)
        else:
            # 順序執行
            results = await self._execute_sequential(plan.tools, base_params)
        
        return results
    
    def _prepare_params(self, slots: AnalysisSlots, intent: IntentType) -> Dict[str, Any]:
        """準備工具參數"""
        params = {
            "products": slots.products,
        }
        
        # 時間範圍映射
        time_days = {
            "7d": 7,
            "30d": 30,
            "90d": 90,
            "1y": 365,
            "all": 3650,
        }
        params["days"] = time_days.get(slots.time_range, 30)
        
        # Finance Tool Params
        if intent == IntentType.FINANCE_ANALYSIS:
            params["metric"] = "revenue" # Default
            params["period"] = "last_30_days" # Default
            params["by"] = "revenue"
            
            # Simple heuristic for metric based on keywords in potential future slots
            # For now default to revenue
        
        if intent == IntentType.ORDER_QUERY:
            params["metric"] = "revenue"
            params["period"] = "this_month"
            
        if intent == IntentType.INVENTORY_QUERY:
            params["by"] = "sales" # Show top selling implies stock movement
            params["limit"] = 10
        
        # 產品細節
        if slots.product_details:
            for product, detail in slots.product_details.items():
                if detail.parts:
                    params.setdefault("parts", []).extend(detail.parts)
                if detail.types:
                    params.setdefault("types", []).extend(detail.types)
        
        return params
    
    async def _execute_parallel(
        self,
        tool_names: List[str],
        params: Dict[str, Any]
    ) -> Dict[str, ToolResult]:
        """並行執行工具"""
        tasks = []
        
        for name in tool_names:
            tool = self.tools.get(name)
            if tool:
                # Filter params based on tool requirements
                tool_params = {}
                schema = tool.get_schema()
                required_params = schema.get("parameters", {}).get("required", [])
                all_param_names = schema.get("parameters", {}).get("properties", {}).keys()
                
                for p in all_param_names:
                    if p in params:
                        tool_params[p] = params[p]
                
                # If specific tool params missing, use defaults or skip (in real system, would ask user)
                # Hack for now: QuerySalesTool needs metric/period
                if name == "query_sales":
                    tool_params.setdefault("metric", "revenue")
                    tool_params.setdefault("period", "last_30_days")
                if name == "query_top_products":
                    tool_params.setdefault("by", "sales")
                    tool_params.setdefault("limit", 5)
                
                # Base params for product tools
                if "days" in all_param_names:
                    tool_params["days"] = params["days"]
                if "products" in all_param_names:
                    tool_params["products"] = params["products"]

                tasks.append(self._execute_tool(name, tool, tool_params))
        
        if not tasks:
            return {}
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        result_dict = {}
        for i, name in enumerate(tool_names):
            if i < len(results):
                result = results[i]
                if isinstance(result, Exception):
                    result_dict[name] = ToolResult(
                        tool_name=name,
                        success=False,
                        error=str(result)
                    )
                else:
                    result_dict[name] = result

        return result_dict

    async def _execute_tool(
        self,
        name: str,
        tool: BaseTool,
        params: Dict[str, Any]
    ) -> ToolResult:
        """執行單個工具"""
        try:
            return await tool.execute(**params)
        except Exception as e:
            return ToolResult(
                tool_name=name,
                success=False,
                error=f"工具執行失敗: {str(e)}"
            )

    async def _execute_sequential(
        self,
        tool_names: List[str],
        params: Dict[str, Any]
    ) -> Dict[str, ToolResult]:
        """順序執行工具"""
        results = {}

        for name in tool_names:
            tool = self.tools.get(name)
            if tool:
                # 與 _execute_parallel 相同的參數處理邏輯
                tool_params = {}
                schema = tool.get_schema()
                all_param_names = schema.get("parameters", {}).get("properties", {}).keys()

                for p in all_param_names:
                    if p in params:
                        tool_params[p] = params[p]

                # 工具特定預設值
                if name == "query_sales":
                    tool_params.setdefault("metric", "revenue")
                    tool_params.setdefault("period", "last_30_days")
                if name == "query_top_products":
                    tool_params.setdefault("by", "sales")
                    tool_params.setdefault("limit", 5)

                if "days" in all_param_names:
                    tool_params["days"] = params.get("days", 30)
                if "products" in all_param_names:
                    tool_params["products"] = params.get("products", [])

                results[name] = await self._execute_tool(name, tool, tool_params)

        return results

    def aggregate_results(self, results: Dict[str, ToolResult]) -> Dict[str, Any]:
        """聚合工具執行結果"""
        aggregated = {
            "success": all(r.success for r in results.values()),
            "data": {},
            "errors": []
        }

        for name, result in results.items():
            if result.success:
                aggregated["data"][name] = result.data
            else:
                aggregated["errors"].append({
                    "tool": name,
                    "error": result.error
                })

        return aggregated

