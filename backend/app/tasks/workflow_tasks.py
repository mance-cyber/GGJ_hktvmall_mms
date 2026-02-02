# =============================================
# 工作流 Celery 任務
# =============================================
#
# 定時任務：
#   - 檢查到期的排程報告並執行
#   - 執行單個排程報告
# =============================================

import logging
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID

from celery import shared_task

from app.tasks.celery_app import celery_app
from app.models.database import async_session_maker
from app.models.workflow import (
    ScheduledReport,
    ReportExecution,
    ExecutionStatus,
    ScheduleStatus,
    ReportType,
)
from app.services.workflow.scheduler import SchedulerService
from app.services.telegram import get_telegram_notifier

logger = logging.getLogger(__name__)


# =============================================
# 排程報告執行任務
# =============================================

@celery_app.task(
    name="app.tasks.workflow_tasks.check_and_execute_due_schedules",
    bind=True,
    max_retries=3,
    default_retry_delay=60
)
def check_and_execute_due_schedules(self):
    """
    檢查並執行所有到期的排程

    這個任務應該由 Celery Beat 每分鐘調用一次
    """
    logger.info("檢查到期的排程報告...")

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            result = loop.run_until_complete(_async_check_due_schedules())
            logger.info(f"排程檢查完成: {result}")
            return result
        finally:
            loop.close()

    except Exception as e:
        logger.error(f"排程檢查失敗: {e}")
        raise self.retry(exc=e)


async def _async_check_due_schedules() -> Dict[str, Any]:
    """異步檢查到期排程"""
    async with async_session_maker() as db:
        scheduler = SchedulerService(db)

        # 獲取到期的排程
        due_schedules = await scheduler.get_due_schedules()

        if not due_schedules:
            return {"checked": 0, "triggered": 0}

        triggered = 0
        for schedule in due_schedules:
            # 為每個到期排程觸發執行任務
            execute_scheduled_report.delay(str(schedule.id))
            triggered += 1

        return {
            "checked": len(due_schedules),
            "triggered": triggered
        }


@celery_app.task(
    name="app.tasks.workflow_tasks.execute_scheduled_report",
    bind=True,
    max_retries=2,
    default_retry_delay=300,  # 5 分鐘後重試
    time_limit=600,  # 10 分鐘超時
)
def execute_scheduled_report(self, schedule_id: str):
    """
    執行單個排程報告

    Args:
        schedule_id: 排程 ID
    """
    logger.info(f"執行排程報告: {schedule_id}")

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            result = loop.run_until_complete(
                _async_execute_scheduled_report(UUID(schedule_id))
            )
            logger.info(f"排程報告執行完成: {schedule_id}, result={result}")
            return result
        finally:
            loop.close()

    except Exception as e:
        logger.error(f"排程報告執行失敗: {schedule_id}, error={e}")
        # 記錄失敗但不重試（由 _async_execute_scheduled_report 內部處理）
        return {
            "schedule_id": schedule_id,
            "success": False,
            "error": str(e)
        }


async def _async_execute_scheduled_report(schedule_id: UUID) -> Dict[str, Any]:
    """異步執行排程報告"""
    async with async_session_maker() as db:
        scheduler = SchedulerService(db)

        # 獲取排程
        schedule = await scheduler.get_schedule(schedule_id)
        if not schedule:
            return {"success": False, "error": "Schedule not found"}

        if schedule.status != ScheduleStatus.ACTIVE.value:
            return {"success": False, "error": f"Schedule is {schedule.status}"}

        # 創建執行記錄
        execution = await scheduler.create_execution(
            schedule_id=schedule_id,
            scheduled_at=schedule.next_run_at or datetime.utcnow()
        )

        # 標記開始
        await scheduler.mark_execution_started(execution.id)

        try:
            # 執行報告生成
            report_content, report_data = await _generate_report(schedule, db)

            # 交付報告
            delivery_status = await _deliver_report(schedule, report_content)

            # 標記完成
            await scheduler.mark_execution_completed(
                execution.id,
                report_content=report_content,
                report_data=report_data,
                delivery_status=delivery_status,
            )

            # 更新排程統計
            await scheduler.update_schedule_after_execution(schedule_id, success=True)

            return {
                "success": True,
                "execution_id": str(execution.id),
                "delivery_status": delivery_status,
            }

        except Exception as e:
            logger.error(f"報告生成失敗: {e}")

            # 標記失敗
            await scheduler.mark_execution_failed(
                execution.id,
                error_message=str(e),
                error_details={"exception_type": type(e).__name__}
            )

            # 更新排程統計（失敗）
            await scheduler.update_schedule_after_execution(schedule_id, success=False)

            return {
                "success": False,
                "execution_id": str(execution.id),
                "error": str(e)
            }


async def _generate_report(
    schedule: ScheduledReport,
    db
) -> tuple[str, Dict[str, Any]]:
    """
    生成報告內容

    Args:
        schedule: 排程對象
        db: 數據庫 session

    Returns:
        (report_content, report_data)
    """
    report_type = schedule.report_type
    config = schedule.report_config or {}

    # 根據報告類型生成不同內容
    if report_type == ReportType.PRICE_ANALYSIS.value:
        return await _generate_price_analysis_report(config, db)
    elif report_type == ReportType.COMPETITOR_REPORT.value:
        return await _generate_competitor_report(config, db)
    elif report_type == ReportType.SALES_SUMMARY.value:
        return await _generate_sales_summary_report(config, db)
    else:
        # 默認報告
        return await _generate_default_report(config, db)


async def _generate_price_analysis_report(config: Dict, db) -> tuple[str, Dict]:
    """生成價格分析報告"""
    from sqlalchemy import select, func
    from app.models.product import Product
    from app.models.competitor import CompetitorProduct

    products = config.get("products", [])

    # 獲取產品數據
    product_query = select(Product)
    if products:
        product_query = product_query.where(Product.name.in_(products))
    product_query = product_query.limit(10)

    result = await db.execute(product_query)
    product_list = result.scalars().all()

    # 構建報告
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    report_lines = [
        f"# 📊 價格分析報告",
        f"",
        f"**生成時間**: {now}",
        f"**產品數量**: {len(product_list)}",
        f"",
        "---",
        "",
        "## 產品價格概覽",
        "",
    ]

    report_data = {"products": []}

    for product in product_list:
        report_lines.append(f"### {product.name}")
        report_lines.append(f"- **SKU**: {product.sku}")
        report_lines.append(f"- **現價**: HK${float(product.price or 0):.2f}")
        if product.cost:
            margin = ((product.price - product.cost) / product.price * 100) if product.price else 0
            report_lines.append(f"- **利潤率**: {margin:.1f}%")
        report_lines.append("")

        report_data["products"].append({
            "id": str(product.id),
            "name": product.name,
            "sku": product.sku,
            "price": float(product.price or 0),
        })

    report_content = "\n".join(report_lines)
    return report_content, report_data


async def _generate_competitor_report(config: Dict, db) -> tuple[str, Dict]:
    """生成競品報告"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    report_content = f"""# ⚔️ 競品分析報告

**生成時間**: {now}

---

## 競品動態

（此處為模板，實際實現需要查詢競品數據）

- 百佳: 無明顯變動
- 惠康: 部分商品促銷中
"""
    return report_content, {"type": "competitor_report"}


async def _generate_sales_summary_report(config: Dict, db) -> tuple[str, Dict]:
    """生成銷售摘要報告"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    report_content = f"""# 💰 銷售摘要報告

**生成時間**: {now}

---

## 銷售概覽

（此處為模板，實際實現需要查詢銷售數據）

- 總訂單數: --
- 總營收: HK$--
- 平均訂單金額: HK$--
"""
    return report_content, {"type": "sales_summary"}


async def _generate_default_report(config: Dict, db) -> tuple[str, Dict]:
    """生成默認報告"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    report_content = f"""# 📋 自動報告

**生成時間**: {now}

---

報告已自動生成。
"""
    return report_content, {"type": "default"}


async def _deliver_report(
    schedule: ScheduledReport,
    report_content: str
) -> Dict[str, Any]:
    """
    交付報告到各渠道

    Args:
        schedule: 排程對象
        report_content: 報告內容

    Returns:
        交付狀態
    """
    delivery_status = {}
    channels = schedule.delivery_channels or {}

    # 如果沒有配置任何渠道，默認使用 Telegram
    if not channels:
        channels = {"telegram": {"enabled": True}}

    # Telegram 交付
    telegram_config = channels.get("telegram", {})
    telegram_enabled = telegram_config.get("enabled", True) if isinstance(telegram_config, dict) else bool(telegram_config)

    if telegram_enabled:
        try:
            notifier = get_telegram_notifier()
            chat_id = telegram_config.get("chat_id") if isinstance(telegram_config, dict) else None

            # 使用專用的排程報告發送方法
            result = await notifier.send_scheduled_report(
                schedule_name=schedule.name,
                report_type=schedule.report_type,
                report_content=report_content,
                chat_id=chat_id
            )

            delivery_status["telegram"] = {
                "sent": result.get("ok", False),
                "message_id": result.get("result", {}).get("message_id"),
                "error": result.get("error")
            }

            if result.get("ok"):
                logger.info(f"Telegram 報告已發送: {schedule.name}")

        except Exception as e:
            logger.error(f"Telegram 交付失敗: {e}")
            delivery_status["telegram"] = {
                "sent": False,
                "error": str(e)
            }

    # Email 交付（可選）
    email_config = channels.get("email", {})
    email_enabled = email_config.get("enabled", False) if isinstance(email_config, dict) else bool(email_config)

    if email_enabled:
        # TODO: 實現 email 交付
        delivery_status["email"] = {
            "sent": False,
            "error": "Email delivery not implemented yet"
        }

    # Webhook 交付（可選）
    webhook_config = channels.get("webhook", {})
    webhook_enabled = webhook_config.get("enabled", False) if isinstance(webhook_config, dict) else bool(webhook_config)

    if webhook_enabled:
        # TODO: 實現 webhook 交付
        delivery_status["webhook"] = {
            "sent": False,
            "error": "Webhook delivery not implemented yet"
        }

    return delivery_status


# =============================================
# 手動觸發任務
# =============================================

@celery_app.task(
    name="app.tasks.workflow_tasks.trigger_report_now",
    bind=True,
)
def trigger_report_now(self, schedule_id: str):
    """
    立即觸發一次報告執行（用於手動測試）

    Args:
        schedule_id: 排程 ID
    """
    logger.info(f"手動觸發報告: {schedule_id}")
    return execute_scheduled_report.delay(schedule_id)


# =============================================
# 告警工作流任務
# =============================================

@celery_app.task(
    name="app.tasks.workflow_tasks.execute_alert_workflow",
    bind=True,
    max_retries=2,
    default_retry_delay=60,
    time_limit=300,  # 5 分鐘超時
)
def execute_alert_workflow(self, alert_data: Dict[str, Any]):
    """
    執行告警工作流

    當價格告警觸發時，檢查所有啟用的告警配置並執行相應的工作流。

    Args:
        alert_data: 告警數據 {
            product_id, product_name, old_price, new_price,
            change_percent, category_id, alert_type
        }

    Returns:
        執行結果列表
    """
    logger.info(f"執行告警工作流: {alert_data.get('product_name')}")

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            results = loop.run_until_complete(_async_execute_alert_workflow(alert_data))
            logger.info(f"告警工作流執行完成: {len(results)} 個配置被觸發")
            return {
                "success": True,
                "triggered_configs": len(results),
                "results": results,
            }
        finally:
            loop.close()

    except Exception as e:
        logger.error(f"告警工作流執行失敗: {e}")
        return {
            "success": False,
            "error": str(e),
        }


async def _async_execute_alert_workflow(alert_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """異步執行告警工作流"""
    from app.services.workflow.triggers import process_price_alert

    async with async_session_maker() as db:
        results = await process_price_alert(db, alert_data)
        return results


@celery_app.task(
    name="app.tasks.workflow_tasks.process_single_alert_config",
    bind=True,
    max_retries=1,
    default_retry_delay=30,
)
def process_single_alert_config(
    self,
    config_id: str,
    alert_data: Dict[str, Any]
):
    """
    處理單個告警配置

    用於並行處理多個告警配置

    Args:
        config_id: 告警配置 ID
        alert_data: 告警數據
    """
    logger.info(f"處理告警配置 {config_id}: {alert_data.get('product_name')}")

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            result = loop.run_until_complete(
                _async_process_single_config(UUID(config_id), alert_data)
            )
            return result
        finally:
            loop.close()

    except Exception as e:
        logger.error(f"處理告警配置失敗 {config_id}: {e}")
        return {
            "success": False,
            "config_id": config_id,
            "error": str(e),
        }


async def _async_process_single_config(
    config_id: UUID,
    alert_data: Dict[str, Any]
) -> Dict[str, Any]:
    """異步處理單個告警配置"""
    from app.services.workflow.triggers import AlertTrigger

    async with async_session_maker() as db:
        trigger = AlertTrigger(db)
        config = await trigger.get_config(config_id)

        if not config:
            return {
                "success": False,
                "config_id": str(config_id),
                "error": "Config not found",
            }

        if await trigger.should_trigger(config, alert_data):
            result = await trigger.execute_workflow(config, alert_data)
            return result

        return {
            "success": True,
            "config_id": str(config_id),
            "triggered": False,
            "reason": "Conditions not met or in quiet hours",
        }
