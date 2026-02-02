# =============================================
# 工作流工具
# AI Agent 觸發業務工作流
# =============================================

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .base import BaseTool, ToolResult
from app.models.product import Product
from app.models.pricing import PriceProposal, ProposalStatus
from app.services.workflow.actions import (
    create_pricing_proposal,
    send_telegram_notification,
    handle_pricing_approval_trigger
)
from app.services.workflow.engine import WorkflowEngine, TriggerType

logger = logging.getLogger(__name__)


class CreateApprovalTaskTool(BaseTool):
    """
    創建改價審批任務工具

    當用戶在對話中確認要創建改價提案時調用
    """

    name = "create_approval_task"
    description = "創建改價審批任務，將 AI 建議嘅價格變動提交審批"
    parameters = {
        "product_id": {
            "type": "str",
            "required": True,
            "description": "產品 ID"
        },
        "proposed_price": {
            "type": "float",
            "required": True,
            "description": "建議價格"
        },
        "reason": {
            "type": "str",
            "required": False,
            "description": "改價原因"
        },
        "conversation_id": {
            "type": "str",
            "required": False,
            "description": "來源對話 ID"
        }
    }

    async def execute(
        self,
        product_id: str,
        proposed_price: float,
        reason: str = None,
        conversation_id: str = None,
        send_notification: bool = True,
        **kwargs
    ) -> ToolResult:
        """
        執行創建審批任務

        Args:
            product_id: 產品 ID
            proposed_price: 建議價格
            reason: 改價原因
            conversation_id: 來源對話 ID
            send_notification: 是否發送 Telegram 通知

        Returns:
            ToolResult
        """
        try:
            result = await handle_pricing_approval_trigger(
                db=self.db,
                conversation_id=conversation_id,
                product_id=product_id,
                proposed_price=proposed_price,
                reason=reason,
                send_notification=send_notification
            )

            if result.get("success"):
                proposal_data = result.get("proposal", {})
                return ToolResult(
                    tool_name=self.name,
                    success=True,
                    data={
                        "proposal_id": proposal_data.get("proposal_id"),
                        "product_name": proposal_data.get("product_name"),
                        "product_sku": proposal_data.get("product_sku"),
                        "current_price": proposal_data.get("current_price"),
                        "proposed_price": proposal_data.get("proposed_price"),
                        "notification_sent": result.get("notification", {}).get("success", False),
                        "message": "改價提案已創建，等待審批"
                    }
                )
            else:
                return ToolResult(
                    tool_name=self.name,
                    success=False,
                    error=result.get("error", "創建提案失敗")
                )

        except Exception as e:
            logger.error(f"CreateApprovalTaskTool failed: {e}")
            return ToolResult(
                tool_name=self.name,
                success=False,
                error=str(e)
            )


class GetPendingProposalsTool(BaseTool):
    """
    獲取待審批提案工具
    """

    name = "get_pending_proposals"
    description = "獲取當前所有待審批嘅改價提案"
    parameters = {
        "product_id": {
            "type": "str",
            "required": False,
            "description": "可選：篩選特定產品"
        },
        "limit": {
            "type": "int",
            "required": False,
            "description": "返回數量限制，默認 10"
        }
    }

    async def execute(
        self,
        product_id: str = None,
        limit: int = 10,
        **kwargs
    ) -> ToolResult:
        """獲取待審批提案"""
        try:
            from uuid import UUID

            query = select(PriceProposal).where(
                PriceProposal.status == ProposalStatus.PENDING
            )

            if product_id:
                query = query.where(PriceProposal.product_id == UUID(product_id))

            query = query.order_by(PriceProposal.created_at.desc()).limit(limit)

            result = await self.db.execute(query)
            proposals = result.scalars().all()

            # 轉換為可序列化格式
            proposal_list = []
            for p in proposals:
                # 獲取產品信息
                product = await self.db.get(Product, p.product_id)
                proposal_list.append({
                    "id": str(p.id),
                    "product_id": str(p.product_id),
                    "product_name": product.name if product else "未知",
                    "product_sku": product.sku if product else "",
                    "current_price": float(p.current_price) if p.current_price else None,
                    "proposed_price": float(p.proposed_price) if p.proposed_price else None,
                    "reason": p.reason,
                    "source_type": p.source_type,
                    "created_at": p.created_at.isoformat() if p.created_at else None
                })

            return ToolResult(
                tool_name=self.name,
                success=True,
                data={
                    "count": len(proposal_list),
                    "proposals": proposal_list
                }
            )

        except Exception as e:
            logger.error(f"GetPendingProposalsTool failed: {e}")
            return ToolResult(
                tool_name=self.name,
                success=False,
                error=str(e)
            )


class SuggestPriceChangeTool(BaseTool):
    """
    AI 價格建議工具

    分析產品和競品數據，生成改價建議
    """

    name = "suggest_price_change"
    description = "分析產品和競品數據，生成智能改價建議"
    parameters = {
        "product_id": {
            "type": "str",
            "required": True,
            "description": "產品 ID"
        }
    }

    async def execute(
        self,
        product_id: str,
        **kwargs
    ) -> ToolResult:
        """生成改價建議"""
        try:
            from uuid import UUID
            from app.models.competitor import CompetitorProduct
            from app.models.product import ProductCompetitorMapping

            product_uuid = UUID(product_id)
            product = await self.db.get(Product, product_uuid)

            if not product:
                return ToolResult(
                    tool_name=self.name,
                    success=False,
                    error=f"找不到產品 {product_id}"
                )

            # 獲取競品信息
            mappings_query = (
                select(CompetitorProduct)
                .join(ProductCompetitorMapping, ProductCompetitorMapping.competitor_product_id == CompetitorProduct.id)
                .where(ProductCompetitorMapping.product_id == product_uuid)
            )
            mappings_result = await self.db.execute(mappings_query)
            competitors = mappings_result.scalars().all()

            current_price = product.price
            suggestion = {
                "product_id": str(product.id),
                "product_name": product.name,
                "product_sku": product.sku,
                "current_price": float(current_price) if current_price else None,
                "suggested_price": None,
                "reason": None,
                "competitors": [],
                "recommendation": None
            }

            if not competitors:
                suggestion["recommendation"] = "暫無競品數據，無法生成自動建議"
                return ToolResult(
                    tool_name=self.name,
                    success=True,
                    data=suggestion
                )

            # 分析競品價格
            min_competitor_price = None
            target_competitor = None

            for comp in competitors:
                if comp.price:
                    suggestion["competitors"].append({
                        "name": comp.name,
                        "price": float(comp.price),
                        "platform": comp.platform
                    })
                    if min_competitor_price is None or comp.price < min_competitor_price:
                        min_competitor_price = comp.price
                        target_competitor = comp

            if not min_competitor_price or not current_price:
                suggestion["recommendation"] = "缺少價格數據，無法生成建議"
                return ToolResult(
                    tool_name=self.name,
                    success=True,
                    data=suggestion
                )

            # 生成建議
            if min_competitor_price < current_price:
                # 競品更便宜，建議跟進
                suggested_price = min_competitor_price - Decimal('1.0')

                # 檢查底線
                cost_floor = (product.cost or Decimal('0')) * Decimal('1.05')
                hard_floor = product.min_price or Decimal('0')
                final_floor = max(cost_floor, hard_floor)

                if final_floor > 0 and suggested_price < final_floor:
                    suggested_price = final_floor

                suggestion["suggested_price"] = float(suggested_price)
                suggestion["reason"] = (
                    f"競爭對手 {target_competitor.name} ({target_competitor.platform}) "
                    f"價格為 ${float(min_competitor_price):.2f}，"
                    f"建議調整至 ${float(suggested_price):.2f} 以保持競爭力"
                )
                suggestion["recommendation"] = "建議降價"

            elif min_competitor_price > current_price * Decimal('1.1'):
                # 競品貴很多，可考慮漲價
                suggested_price = current_price * Decimal('1.05')
                suggestion["suggested_price"] = float(suggested_price)
                suggestion["reason"] = (
                    f"競爭對手最低價 ${float(min_competitor_price):.2f} "
                    f"比我們高 {((min_competitor_price / current_price - 1) * 100):.1f}%，"
                    f"可考慮適度提價至 ${float(suggested_price):.2f}"
                )
                suggestion["recommendation"] = "可考慮提價"

            else:
                suggestion["recommendation"] = "價格競爭力良好，建議維持"
                suggestion["reason"] = (
                    f"當前價格 ${float(current_price):.2f} "
                    f"與競品最低價 ${float(min_competitor_price):.2f} 相近，無需調整"
                )

            return ToolResult(
                tool_name=self.name,
                success=True,
                data=suggestion
            )

        except Exception as e:
            logger.error(f"SuggestPriceChangeTool failed: {e}")
            return ToolResult(
                tool_name=self.name,
                success=False,
                error=str(e)
            )


# =============================================
# 工具註冊
# =============================================

def get_workflow_tools(db: AsyncSession) -> List[BaseTool]:
    """獲取所有工作流工具實例"""
    return [
        CreateApprovalTaskTool(db),
        GetPendingProposalsTool(db),
        SuggestPriceChangeTool(db),
    ]
