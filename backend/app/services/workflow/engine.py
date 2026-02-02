# =============================================
# Workflow Engine
# 統一管理觸發器、執行器、狀態追蹤
# =============================================

import logging
from typing import Any, Dict, List, Optional, Callable, Awaitable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class WorkflowStatus(Enum):
    """工作流執行狀態"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class TriggerType(Enum):
    """觸發器類型"""
    PRICING_APPROVAL = "pricing_approval"
    ALERT_RESPONSE = "alert_response"
    SCHEDULED_REPORT = "scheduled_report"


@dataclass
class WorkflowExecution:
    """工作流執行記錄"""
    id: str
    trigger_type: TriggerType
    status: WorkflowStatus
    conversation_id: Optional[str]
    started_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TriggerConfig:
    """觸發器配置"""
    trigger_type: TriggerType
    handler: Callable[..., Awaitable[Any]]
    description: str


class WorkflowEngine:
    """
    工作流引擎

    負責：
    - 註冊和管理觸發器
    - 執行工作流動作
    - 追蹤執行狀態
    - 維護對話來源追溯
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self._triggers: Dict[TriggerType, TriggerConfig] = {}
        self._executions: Dict[str, WorkflowExecution] = {}

    def register_trigger(
        self,
        trigger_type: TriggerType,
        handler: Callable[..., Awaitable[Any]],
        description: str = ""
    ) -> None:
        """
        註冊觸發器

        Args:
            trigger_type: 觸發器類型
            handler: 處理函數（async）
            description: 觸發器描述
        """
        self._triggers[trigger_type] = TriggerConfig(
            trigger_type=trigger_type,
            handler=handler,
            description=description
        )
        logger.info(f"Registered workflow trigger: {trigger_type.value}")

    async def trigger(
        self,
        trigger_type: TriggerType,
        conversation_id: Optional[str] = None,
        **kwargs
    ) -> WorkflowExecution:
        """
        觸發工作流

        Args:
            trigger_type: 觸發器類型
            conversation_id: 來源對話 ID（用於追溯）
            **kwargs: 傳遞給處理函數嘅參數

        Returns:
            WorkflowExecution: 執行記錄
        """
        if trigger_type not in self._triggers:
            raise ValueError(f"Unknown trigger type: {trigger_type}")

        config = self._triggers[trigger_type]

        # 創建執行記錄
        execution = WorkflowExecution(
            id=str(uuid.uuid4()),
            trigger_type=trigger_type,
            status=WorkflowStatus.RUNNING,
            conversation_id=conversation_id,
            started_at=datetime.utcnow(),
            metadata=kwargs
        )
        self._executions[execution.id] = execution

        logger.info(
            f"Workflow triggered: {trigger_type.value}, "
            f"execution_id={execution.id}, conversation_id={conversation_id}"
        )

        try:
            # 執行處理函數
            result = await config.handler(
                db=self.db,
                conversation_id=conversation_id,
                **kwargs
            )

            # 更新執行狀態
            execution.status = WorkflowStatus.COMPLETED
            execution.completed_at = datetime.utcnow()
            execution.result = result if isinstance(result, dict) else {"result": result}

            logger.info(f"Workflow completed: {execution.id}")

        except Exception as e:
            execution.status = WorkflowStatus.FAILED
            execution.completed_at = datetime.utcnow()
            execution.error_message = str(e)

            logger.error(f"Workflow failed: {execution.id}, error={e}")
            raise

        return execution

    def get_execution(self, execution_id: str) -> Optional[WorkflowExecution]:
        """獲取執行記錄"""
        return self._executions.get(execution_id)

    def get_executions_by_conversation(
        self,
        conversation_id: str
    ) -> List[WorkflowExecution]:
        """獲取指定對話嘅所有工作流執行記錄"""
        return [
            e for e in self._executions.values()
            if e.conversation_id == conversation_id
        ]

    def get_registered_triggers(self) -> List[TriggerType]:
        """獲取已註冊嘅觸發器列表"""
        return list(self._triggers.keys())
