# =============================================
# Agent 工具模組
# =============================================

from .base import BaseTool, ToolResult
from .product_tools import (
    ProductOverviewTool,
    ProductSearchTool,
    TopProductsTool,
)
from .price_tools import (
    PriceTrendTool,
    PriceComparisonTool,
)
from .competitor_tools import (
    CompetitorCompareTool,
)

# 所有可用工具
ALL_TOOLS = [
    ProductOverviewTool,
    ProductSearchTool,
    TopProductsTool,
    PriceTrendTool,
    PriceComparisonTool,
    CompetitorCompareTool,
]

__all__ = [
    "BaseTool",
    "ToolResult",
    "ProductOverviewTool",
    "ProductSearchTool",
    "TopProductsTool",
    "PriceTrendTool",
    "PriceComparisonTool",
    "CompetitorCompareTool",
    "ALL_TOOLS",
]
