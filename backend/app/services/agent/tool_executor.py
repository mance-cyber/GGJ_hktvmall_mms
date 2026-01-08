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
        IntentType.PRODUCT_SEARCH: ["product_search"],
        IntentType.PRODUCT_DETAIL: ["product_search"],
        IntentType.PRICE_ANALYSIS: ["product_overview", "price_comparison"],
        IntentType.TREND_ANALYSIS: ["price_trend", "product_overview"],
        IntentType.COMPETITOR_ANALYSIS: ["competitor_compare", "product_overview"],
        IntentType.BRAND_ANALYSIS: ["top_products", "product_overview"],
        IntentType.MARKET_OVERVIEW: ["product_overview", "price_trend", "top_products", "competitor_compare"],
        IntentType.GENERATE_REPORT: ["product_overview", "price_trend", "competitor_compare", "top_products"],
        IntentType.MARKETING_STRATEGY: ["product_overview", "price_trend", "competitor_compare", "top_products"],
    }
    
    def __init__(self, db: AsyncSession):
        self.db = db
        
        # 初始化所有工具
        self.tools: Dict[str, BaseTool] = {
            "product_overview": ProductOverviewTool(db),
            "product_search": ProductSearchTool(db),
            "top_products": TopProductsTool(db),
            "price_trend": PriceTrendTool(db),
            "price_comparison": PriceComparisonTool(db),
            "competitor_compare": CompetitorCompareTool(db),
        }
    
    def get_execution_plan(
        self,
        intent: IntentType,
        slots: AnalysisSlots
    ) -> ExecutionPlan:
        """
        獲取執行計劃
        
        Args:
            intent: 意圖類型
            slots: 槽位
        
        Returns:
            執行計劃
        """
        # 獲取該意圖需要的工具
        tools = self.INTENT_TOOL_MAPPING.get(intent, [])
        
        # 根據槽位調整
        if not slots.include_competitors and "competitor_compare" in tools:
            tools = [t for t in tools if t != "competitor_compare"]
        
        # 根據分析維度調整
        if slots.analysis_dimensions:
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
        """
        執行工具並返回結果
        
        Args:
            intent: 意圖類型
            slots: 槽位
        
        Returns:
            工具執行結果
        """
        plan = self.get_execution_plan(intent, slots)
        
        if not plan.tools:
            return {}
        
        # 準備參數
        base_params = self._prepare_params(slots)
        
        if plan.parallel:
            # 並行執行
            results = await self._execute_parallel(plan.tools, base_params)
        else:
            # 順序執行
            results = await self._execute_sequential(plan.tools, base_params)
        
        return results
    
    def _prepare_params(self, slots: AnalysisSlots) -> Dict[str, Any]:
        """準備工具參數"""
        params = {
            "products": slots.products,
        }
        
        # 時間範圍
        time_days = {
            "7d": 7,
            "30d": 30,
            "90d": 90,
            "1y": 365,
            "all": 3650,
        }
        params["days"] = time_days.get(slots.time_range, 30)
        
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
                tasks.append(self._execute_tool(name, tool, params))
        
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
                result = await self._execute_tool(name, tool, params)
                results[name] = result
        
        return results
    
    async def _execute_tool(
        self,
        name: str,
        tool: BaseTool,
        params: Dict[str, Any]
    ) -> ToolResult:
        """執行單個工具"""
        try:
            return await tool.safe_execute(**params)
        except Exception as e:
            return ToolResult(
                tool_name=name,
                success=False,
                error=str(e)
            )
    
    def aggregate_results(
        self,
        results: Dict[str, ToolResult]
    ) -> Dict[str, Any]:
        """
        聚合工具結果
        
        將多個工具的結果合併為統一格式，供報告生成使用
        """
        aggregated = {
            "success": True,
            "data": {},
            "errors": [],
            "metadata": {
                "tools_executed": list(results.keys()),
                "total_execution_time_ms": 0,
            }
        }
        
        for name, result in results.items():
            if result.success:
                aggregated["data"][name] = result.data
            else:
                aggregated["errors"].append({
                    "tool": name,
                    "error": result.error
                })
            
            aggregated["metadata"]["total_execution_time_ms"] += result.execution_time_ms
        
        if aggregated["errors"]:
            aggregated["success"] = len(aggregated["errors"]) < len(results)
        
        return aggregated
