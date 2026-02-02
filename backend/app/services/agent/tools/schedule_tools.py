# =============================================
# 排程管理工具
# AI Agent 管理定時報告排程
# =============================================

import logging
from typing import Any, Dict, List, Optional
from uuid import UUID
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .base import BaseTool, ToolResult
from app.models.workflow import ScheduledReport, ScheduleStatus, ReportType
from app.services.workflow.scheduler import SchedulerService

logger = logging.getLogger(__name__)


class CreateScheduleTool(BaseTool):
    """
    創建排程報告工具
    """

    name = "create_schedule"
    description = "創建定時報告排程"
    parameters = {
        "name": {
            "type": "str",
            "required": True,
            "description": "排程名稱"
        },
        "report_type": {
            "type": "str",
            "required": False,
            "description": "報告類型 (price_analysis, competitor_report, sales_summary)"
        },
        "frequency": {
            "type": "str",
            "required": True,
            "description": "頻率 (daily, weekly, monthly)"
        },
        "schedule_time": {
            "type": "str",
            "required": False,
            "description": "執行時間 HH:MM"
        },
        "schedule_day": {
            "type": "int",
            "required": False,
            "description": "執行日 (週幾 1-7 或月幾號 1-31)"
        },
        "products": {
            "type": "list",
            "required": False,
            "description": "產品列表"
        },
        "conversation_id": {
            "type": "str",
            "required": False,
            "description": "來源對話 ID"
        }
    }

    async def execute(
        self,
        name: str,
        frequency: str,
        report_type: str = "price_analysis",
        schedule_time: str = "09:00",
        schedule_day: int = None,
        products: List[str] = None,
        conversation_id: str = None,
        delivery_channel: str = "telegram",
        **kwargs
    ) -> ToolResult:
        """創建排程"""
        try:
            scheduler = SchedulerService(self.db)

            # 構建報告配置
            report_config = {}
            if products:
                report_config["products"] = products

            # 構建交付渠道配置
            delivery_channels = {}
            if delivery_channel == "telegram":
                delivery_channels["telegram"] = {"enabled": True}
            elif delivery_channel == "email":
                delivery_channels["email"] = {"enabled": True}

            schedule = await scheduler.create_schedule(
                name=name,
                report_type=report_type,
                report_config=report_config,
                frequency=frequency,
                schedule_time=schedule_time,
                schedule_day=schedule_day,
                delivery_channels=delivery_channels,
                source_conversation_id=conversation_id,
            )

            return ToolResult(
                tool_name=self.name,
                success=True,
                data={
                    "schedule_id": str(schedule.id),
                    "name": schedule.name,
                    "frequency": schedule.frequency,
                    "schedule_time": schedule.schedule_time,
                    "next_run_at": schedule.next_run_at.isoformat() if schedule.next_run_at else None,
                    "status": schedule.status,
                    "message": f"排程「{name}」已創建"
                }
            )

        except Exception as e:
            logger.error(f"CreateScheduleTool failed: {e}")
            return ToolResult(
                tool_name=self.name,
                success=False,
                error=str(e)
            )


class ListSchedulesTool(BaseTool):
    """
    列出排程工具
    """

    name = "list_schedules"
    description = "列出用戶的排程報告"
    parameters = {
        "status": {
            "type": "str",
            "required": False,
            "description": "篩選狀態 (active, paused)"
        },
        "conversation_id": {
            "type": "str",
            "required": False,
            "description": "篩選對話 ID"
        },
        "limit": {
            "type": "int",
            "required": False,
            "description": "返回數量"
        }
    }

    async def execute(
        self,
        status: str = None,
        conversation_id: str = None,
        limit: int = 10,
        **kwargs
    ) -> ToolResult:
        """列出排程"""
        try:
            scheduler = SchedulerService(self.db)

            schedules = await scheduler.list_schedules(
                status=status,
                conversation_id=conversation_id,
                limit=limit,
            )

            schedule_list = []
            for s in schedules:
                schedule_list.append({
                    "id": str(s.id),
                    "name": s.name,
                    "report_type": s.report_type,
                    "frequency": s.frequency,
                    "schedule_time": s.schedule_time,
                    "status": s.status,
                    "next_run_at": s.next_run_at.isoformat() if s.next_run_at else None,
                    "run_count": s.run_count,
                    "success_count": s.success_count,
                })

            return ToolResult(
                tool_name=self.name,
                success=True,
                data={
                    "count": len(schedule_list),
                    "schedules": schedule_list,
                }
            )

        except Exception as e:
            logger.error(f"ListSchedulesTool failed: {e}")
            return ToolResult(
                tool_name=self.name,
                success=False,
                error=str(e)
            )


class PauseScheduleTool(BaseTool):
    """
    暫停排程工具
    """

    name = "pause_schedule"
    description = "暫停排程報告"
    parameters = {
        "schedule_id": {
            "type": "str",
            "required": True,
            "description": "排程 ID"
        }
    }

    async def execute(self, schedule_id: str, **kwargs) -> ToolResult:
        """暫停排程"""
        try:
            scheduler = SchedulerService(self.db)

            schedule = await scheduler.pause_schedule(UUID(schedule_id))

            if not schedule:
                return ToolResult(
                    tool_name=self.name,
                    success=False,
                    error="找不到排程"
                )

            return ToolResult(
                tool_name=self.name,
                success=True,
                data={
                    "schedule_id": str(schedule.id),
                    "name": schedule.name,
                    "status": schedule.status,
                    "message": f"排程「{schedule.name}」已暫停"
                }
            )

        except Exception as e:
            logger.error(f"PauseScheduleTool failed: {e}")
            return ToolResult(
                tool_name=self.name,
                success=False,
                error=str(e)
            )


class ResumeScheduleTool(BaseTool):
    """
    恢復排程工具
    """

    name = "resume_schedule"
    description = "恢復排程報告"
    parameters = {
        "schedule_id": {
            "type": "str",
            "required": True,
            "description": "排程 ID"
        }
    }

    async def execute(self, schedule_id: str, **kwargs) -> ToolResult:
        """恢復排程"""
        try:
            scheduler = SchedulerService(self.db)

            schedule = await scheduler.resume_schedule(UUID(schedule_id))

            if not schedule:
                return ToolResult(
                    tool_name=self.name,
                    success=False,
                    error="找不到排程"
                )

            return ToolResult(
                tool_name=self.name,
                success=True,
                data={
                    "schedule_id": str(schedule.id),
                    "name": schedule.name,
                    "status": schedule.status,
                    "next_run_at": schedule.next_run_at.isoformat() if schedule.next_run_at else None,
                    "message": f"排程「{schedule.name}」已恢復"
                }
            )

        except Exception as e:
            logger.error(f"ResumeScheduleTool failed: {e}")
            return ToolResult(
                tool_name=self.name,
                success=False,
                error=str(e)
            )


class DeleteScheduleTool(BaseTool):
    """
    刪除排程工具
    """

    name = "delete_schedule"
    description = "刪除排程報告"
    parameters = {
        "schedule_id": {
            "type": "str",
            "required": True,
            "description": "排程 ID"
        }
    }

    async def execute(self, schedule_id: str, **kwargs) -> ToolResult:
        """刪除排程"""
        try:
            scheduler = SchedulerService(self.db)

            # 先獲取排程名稱
            schedule = await scheduler.get_schedule(UUID(schedule_id))
            if not schedule:
                return ToolResult(
                    tool_name=self.name,
                    success=False,
                    error="找不到排程"
                )

            name = schedule.name
            deleted = await scheduler.delete_schedule(UUID(schedule_id))

            if not deleted:
                return ToolResult(
                    tool_name=self.name,
                    success=False,
                    error="刪除失敗"
                )

            return ToolResult(
                tool_name=self.name,
                success=True,
                data={
                    "schedule_id": schedule_id,
                    "name": name,
                    "message": f"排程「{name}」已刪除"
                }
            )

        except Exception as e:
            logger.error(f"DeleteScheduleTool failed: {e}")
            return ToolResult(
                tool_name=self.name,
                success=False,
                error=str(e)
            )


# =============================================
# 工具註冊
# =============================================

def get_schedule_tools(db: AsyncSession) -> List[BaseTool]:
    """獲取所有排程工具實例"""
    return [
        CreateScheduleTool(db),
        ListSchedulesTool(db),
        PauseScheduleTool(db),
        ResumeScheduleTool(db),
        DeleteScheduleTool(db),
    ]
