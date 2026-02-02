# =============================================
# 告警觸發器服務
# 處理價格變動告警的自動化響應
# =============================================

import logging
from datetime import datetime, time
from typing import Any, Dict, List, Optional
from uuid import UUID
from decimal import Decimal

import pytz
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.workflow import AlertWorkflowConfig
from app.models.pricing import PriceProposal, SourceType, ProposalStatus

logger = logging.getLogger(__name__)


class AlertTrigger:
    """
    告警觸發器

    職責：
    - 檢查告警是否滿足觸發條件
    - 過濾靜默時段
    - 觸發配置的自動化動作
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_active_configs(self) -> List[AlertWorkflowConfig]:
        """獲取所有啟用的告警配置"""
        query = select(AlertWorkflowConfig).where(
            AlertWorkflowConfig.is_active == True
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_config(self, config_id: UUID) -> Optional[AlertWorkflowConfig]:
        """獲取指定告警配置"""
        return await self.db.get(AlertWorkflowConfig, config_id)

    async def should_trigger(
        self,
        config: AlertWorkflowConfig,
        alert_data: Dict[str, Any],
        timezone: str = "Asia/Hong_Kong"
    ) -> bool:
        """
        檢查是否應該觸發告警工作流

        Args:
            config: 告警配置
            alert_data: 告警數據 {
                product_id, product_name, old_price, new_price,
                change_percent, category_id, alert_type
            }
            timezone: 時區

        Returns:
            是否應該觸發
        """
        # 1. 檢查是否在靜默時段
        if self._is_quiet_hours(config, timezone):
            logger.debug(f"Alert config {config.id} is in quiet hours, skipping")
            return False

        # 2. 檢查觸發條件
        if not self._check_trigger_conditions(config, alert_data):
            logger.debug(f"Alert config {config.id} conditions not met")
            return False

        return True

    def _is_quiet_hours(
        self,
        config: AlertWorkflowConfig,
        timezone: str = "Asia/Hong_Kong"
    ) -> bool:
        """
        檢查當前是否在靜默時段

        Args:
            config: 告警配置
            timezone: 時區

        Returns:
            是否在靜默時段
        """
        if not config.quiet_hours_start or not config.quiet_hours_end:
            return False

        tz = pytz.timezone(timezone)
        now = datetime.now(tz).time()

        start = self._parse_time(config.quiet_hours_start)
        end = self._parse_time(config.quiet_hours_end)

        if start is None or end is None:
            return False

        # 處理跨夜情況 (例如 22:00 - 08:00)
        if start > end:
            return now >= start or now < end
        else:
            return start <= now < end

    def _parse_time(self, time_str: str) -> Optional[time]:
        """解析時間字符串 HH:MM"""
        try:
            parts = time_str.split(':')
            return time(int(parts[0]), int(parts[1]))
        except (ValueError, IndexError):
            return None

    def _check_trigger_conditions(
        self,
        config: AlertWorkflowConfig,
        alert_data: Dict[str, Any]
    ) -> bool:
        """
        檢查觸發條件

        Args:
            config: 告警配置
            alert_data: 告警數據

        Returns:
            是否滿足條件
        """
        conditions = config.trigger_conditions or {}

        # 1. 先檢查過濾條件（類別和產品）
        # 類別篩選
        categories = conditions.get("categories", [])
        if categories:
            category_id = alert_data.get("category_id")
            if not category_id or str(category_id) not in [str(c) for c in categories]:
                return False

        # 產品篩選
        products = conditions.get("products", [])
        if products:
            product_id = alert_data.get("product_id")
            if not product_id or str(product_id) not in [str(p) for p in products]:
                return False

        # 2. 再檢查價格變動閾值
        price_drop_threshold = conditions.get("price_drop_threshold")
        price_increase_threshold = conditions.get("price_increase_threshold")
        change_percent = alert_data.get("change_percent", 0)

        # 如果沒有設置任何閾值條件，默認觸發
        if price_drop_threshold is None and price_increase_threshold is None:
            return True

        # 檢查降價閾值
        if price_drop_threshold is not None:
            if change_percent < 0 and abs(change_percent) >= price_drop_threshold:
                return True

        # 檢查漲價閾值
        if price_increase_threshold is not None:
            if change_percent > 0 and change_percent >= price_increase_threshold:
                return True

        return False

    async def execute_workflow(
        self,
        config: AlertWorkflowConfig,
        alert_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        執行告警工作流

        Args:
            config: 告警配置
            alert_data: 告警數據

        Returns:
            執行結果
        """
        results = {
            "config_id": str(config.id),
            "config_name": config.name,
            "actions_executed": [],
            "analysis_result": None,
            "proposal_created": None,
            "notifications_sent": [],
        }

        # 1. 自動 AI 分析
        if config.auto_analyze:
            try:
                analysis = await self._execute_ai_analysis(alert_data)
                results["analysis_result"] = analysis
                results["actions_executed"].append("ai_analysis")
                logger.info(f"AI analysis completed for alert on {alert_data.get('product_name')}")
            except Exception as e:
                logger.error(f"AI analysis failed: {e}")
                results["analysis_error"] = str(e)

        # 2. 自動創建改價提案
        if config.auto_create_proposal:
            try:
                proposal = await self._create_price_proposal(alert_data, results.get("analysis_result"))
                results["proposal_created"] = {
                    "id": str(proposal.id),
                    "proposed_price": float(proposal.proposed_price) if proposal.proposed_price else None,
                }
                results["actions_executed"].append("create_proposal")
                logger.info(f"Price proposal created: {proposal.id}")
            except Exception as e:
                logger.error(f"Create proposal failed: {e}")
                results["proposal_error"] = str(e)

        # 3. 發送通知
        if config.notify_channels:
            try:
                notifications = await self._send_notifications(
                    config.notify_channels,
                    alert_data,
                    results.get("analysis_result"),
                    results.get("proposal_created")
                )
                results["notifications_sent"] = notifications
                results["actions_executed"].append("send_notifications")
            except Exception as e:
                logger.error(f"Send notifications failed: {e}")
                results["notification_error"] = str(e)

        return results

    async def _execute_ai_analysis(
        self,
        alert_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        執行 AI 分析

        分析價格變動的影響和建議
        """
        product_name = alert_data.get("product_name", "未知產品")
        old_price = alert_data.get("old_price", 0)
        new_price = alert_data.get("new_price", 0)
        change_percent = alert_data.get("change_percent", 0)

        # 簡單的分析邏輯（實際實現應調用 Claude API）
        analysis = {
            "product_name": product_name,
            "price_change": {
                "old_price": float(old_price),
                "new_price": float(new_price),
                "change_percent": float(change_percent),
            },
            "impact_assessment": self._assess_impact(change_percent),
            "recommendations": self._generate_recommendations(change_percent, old_price, new_price),
            "analyzed_at": datetime.utcnow().isoformat(),
        }

        return analysis

    def _assess_impact(self, change_percent: float) -> str:
        """評估價格變動影響"""
        abs_change = abs(change_percent)

        if abs_change >= 20:
            return "高影響：競爭對手大幅調價，建議立即評估跟進策略"
        elif abs_change >= 10:
            return "中影響：顯著價格變動，建議密切關注並考慮調整"
        elif abs_change >= 5:
            return "低影響：輕微價格波動，可暫時觀察"
        else:
            return "極低影響：價格變動在正常範圍內"

    def _generate_recommendations(
        self,
        change_percent: float,
        old_price: float,
        new_price: float
    ) -> List[str]:
        """生成建議"""
        recommendations = []

        if change_percent < -10:
            recommendations.append("考慮跟進降價以維持競爭力")
            recommendations.append("評估是否為促銷活動，設定觀察期")
            recommendations.append("檢查該產品利潤率，確保降價後仍有盈利空間")
        elif change_percent < -5:
            recommendations.append("密切監控競爭對手後續動作")
            recommendations.append("評估是否需要小幅調整價格")
        elif change_percent > 10:
            recommendations.append("競爭對手漲價，可考慮維持或小幅上調")
            recommendations.append("檢查市場供需情況，評估漲價空間")
        elif change_percent > 5:
            recommendations.append("市場價格上行，可暫時觀望")

        if not recommendations:
            recommendations.append("價格變動在正常範圍，建議維持現有定價策略")

        return recommendations

    async def _create_price_proposal(
        self,
        alert_data: Dict[str, Any],
        analysis: Optional[Dict[str, Any]]
    ) -> PriceProposal:
        """
        自動創建改價提案
        """
        product_id = alert_data.get("product_id")
        old_price = alert_data.get("old_price", 0)
        new_price = alert_data.get("new_price", 0)
        change_percent = alert_data.get("change_percent", 0)

        # 計算建議價格（簡單邏輯：跟進競爭對手價格的 80%）
        if change_percent < 0:
            # 競爭對手降價，建議小幅跟進
            price_diff = float(old_price) - float(new_price)
            proposed_price = float(old_price) - (price_diff * 0.5)  # 跟進 50%
        else:
            # 競爭對手漲價，可考慮小幅上調
            price_diff = float(new_price) - float(old_price)
            proposed_price = float(old_price) + (price_diff * 0.3)  # 跟進 30%

        # 生成建議原因
        reason_parts = []
        if analysis:
            reason_parts.append(f"影響評估: {analysis.get('impact_assessment', '')}")
            if analysis.get("recommendations"):
                reason_parts.append(f"建議: {analysis['recommendations'][0]}")

        reason_parts.append(
            f"競爭對手價格從 HK${float(old_price):.2f} 變為 HK${float(new_price):.2f} "
            f"({change_percent:+.1f}%)"
        )

        proposal = PriceProposal(
            product_id=UUID(str(product_id)) if product_id else None,
            current_price=Decimal(str(old_price)) if old_price else None,
            proposed_price=Decimal(str(proposed_price)),
            reason="\n".join(reason_parts),
            source_type=SourceType.AUTO_ALERT,
            status=ProposalStatus.PENDING,
            ai_model_used="alert_trigger_v1",
        )

        self.db.add(proposal)
        await self.db.commit()
        await self.db.refresh(proposal)

        return proposal

    async def _send_notifications(
        self,
        channels: Dict[str, Any],
        alert_data: Dict[str, Any],
        analysis: Optional[Dict[str, Any]],
        proposal: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        發送通知到配置的渠道
        """
        from app.services.telegram import get_telegram_notifier

        results = []

        # Telegram 通知
        telegram_config = channels.get("telegram", {})
        if telegram_config.get("enabled", True):
            try:
                notifier = get_telegram_notifier()

                # 使用新的 send_alert_notification 方法（帶操作按鈕）
                include_buttons = telegram_config.get("include_action_buttons", True)
                result = await notifier.send_alert_notification(
                    alert_data=alert_data,
                    analysis=analysis,
                    proposal=proposal,
                    include_action_buttons=include_buttons,
                    chat_id=telegram_config.get("chat_id")
                )

                results.append({
                    "channel": "telegram",
                    "sent": result.get("ok", False),
                    "message_id": result.get("result", {}).get("message_id"),
                })
            except Exception as e:
                results.append({
                    "channel": "telegram",
                    "sent": False,
                    "error": str(e),
                })

        return results

    def _format_alert_message(
        self,
        alert_data: Dict[str, Any],
        analysis: Optional[Dict[str, Any]],
        proposal: Optional[Dict[str, Any]]
    ) -> str:
        """
        格式化告警通知消息
        """
        product_name = alert_data.get("product_name", "未知產品")
        old_price = alert_data.get("old_price", 0)
        new_price = alert_data.get("new_price", 0)
        change_percent = alert_data.get("change_percent", 0)

        # 價格變動方向
        if change_percent < 0:
            direction = "📉 降價"
            change_display = f"-{abs(change_percent):.1f}%"
        else:
            direction = "📈 漲價"
            change_display = f"+{change_percent:.1f}%"

        message_parts = [
            f"<b>⚠️ 價格告警: {direction}</b>",
            "",
            f"🏷 <b>產品</b>: {product_name}",
            f"💰 <b>原價</b>: HK${float(old_price):.2f}",
            f"💵 <b>現價</b>: HK${float(new_price):.2f}",
            f"📊 <b>變動</b>: {change_display}",
        ]

        # 添加 AI 分析結果
        if analysis:
            message_parts.append("")
            message_parts.append("<b>🤖 AI 分析</b>")
            message_parts.append(f"• {analysis.get('impact_assessment', '')}")
            recommendations = analysis.get("recommendations", [])
            if recommendations:
                message_parts.append(f"• {recommendations[0]}")

        # 添加提案信息
        if proposal:
            message_parts.append("")
            message_parts.append("<b>📋 改價提案已創建</b>")
            proposed = proposal.get("proposed_price")
            if proposed:
                message_parts.append(f"• 建議價格: HK${proposed:.2f}")

        message_parts.append("")
        message_parts.append(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M')}")

        return "\n".join(message_parts)


# =============================================
# 便捷函數
# =============================================

async def process_price_alert(
    db: AsyncSession,
    alert_data: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    處理價格告警

    檢查所有啟用的告警配置，執行滿足條件的工作流

    Args:
        db: 數據庫 session
        alert_data: 告警數據

    Returns:
        執行結果列表
    """
    trigger = AlertTrigger(db)
    configs = await trigger.get_active_configs()
    results = []

    for config in configs:
        if await trigger.should_trigger(config, alert_data):
            logger.info(f"Alert config {config.id} triggered for {alert_data.get('product_name')}")
            result = await trigger.execute_workflow(config, alert_data)
            results.append(result)

    return results
