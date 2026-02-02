# =============================================
# AI Agent 模組
# =============================================

# 使用數據庫持久化版本
from .agent_service_db import AgentService

from .intent_classifier import IntentClassifier, IntentType, IntentResult
from .slot_manager import SlotManager, AnalysisSlots, SlotStatus
from .tool_executor import ToolExecutor
from .report_generator import ReportGenerator
from .taxonomy import PRODUCT_TAXONOMY

__all__ = [
    "AgentService",
    "IntentClassifier",
    "IntentType",
    "IntentResult",
    "SlotManager",
    "AnalysisSlots",
    "SlotStatus",
    "ToolExecutor",
    "ReportGenerator",
    "PRODUCT_TAXONOMY",
]
