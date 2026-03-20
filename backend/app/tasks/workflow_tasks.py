# =============================================
# 工作流任務（純 async，無 Celery 依賴）
# =============================================

import asyncio
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID

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
# 排程報告檢查（每分鐘）
# =============================================

async def check_and_execute_due_schedules_async() -> Dict[str, Any]:
    """檢查並執行所有到期的排程"""
    logger.info("檢查到期的排程報告...")

    async with async_session_maker() as db:
        scheduler = SchedulerService(db)
        due_schedules = await scheduler.get_due_schedules()

        if not due_schedules:
            return {"checked": 0, "triggered": 0}

        triggered = 0
        for schedule in due_schedules:
            asyncio.create_task(execute_scheduled_report_async(str(schedule.id)))
            triggered += 1

        result = {"checked": len(due_schedules), "triggered": triggered}
        logger.info(f"排程檢查完成: {result}")
        return result


# =============================================
# 執行排程報告
# =============================================

async def execute_scheduled_report_async(schedule_id: str) -> Dict[str, Any]:
    """執行單個排程報告"""
    logger.info(f"執行排程報告: {schedule_id}")

    try:
        async with async_session_maker() as db:
            scheduler = SchedulerService(db)

            schedule = await scheduler.get_schedule(UUID(schedule_id))
            if not schedule:
                return {"success": False, "error": "Schedule not found"}

            if schedule.status != ScheduleStatus.ACTIVE.value:
                return {"success": False, "error": f"Schedule is {schedule.status}"}

            execution = await scheduler.create_execution(
                schedule_id=UUID(schedule_id),
                scheduled_at=schedule.next_run_at or datetime.utcnow(),
            )

            await scheduler.mark_execution_started(execution.id)

            try:
                report_content, report_data = await _generate_report(schedule, db)
                delivery_status = await _deliver_report(schedule, report_content)

                await scheduler.mark_execution_completed(
                    execution.id,
                    report_content=report_content,
                    report_data=report_data,
                    delivery_status=delivery_status,
                )

                await scheduler.update_schedule_after_execution(UUID(schedule_id), success=True)

                result = {
                    "success": True,
                    "execution_id": str(execution.id),
                    "delivery_status": delivery_status,
                }
                logger.info(f"排程報告執行完成: {schedule_id}, result={result}")
                return result

            except Exception as e:
                logger.error(f"報告生成失敗: {e}")

                await scheduler.mark_execution_failed(
                    execution.id,
                    error_message=str(e),
                    error_details={"exception_type": type(e).__name__},
                )

                await scheduler.update_schedule_after_execution(UUID(schedule_id), success=False)

                return {
                    "success": False,
                    "execution_id": str(execution.id),
                    "error": str(e),
                }

    except Exception as e:
        logger.error(f"排程報告執行失敗: {schedule_id}, error={e}")
        return {
            "schedule_id": schedule_id,
            "success": False,
            "error": str(e),
        }


# =============================================
# 手動觸發
# =============================================

async def trigger_report_now_async(schedule_id: str):
    """立即觸發一次報告執行"""
    logger.info(f"手動觸發報告: {schedule_id}")
    asyncio.create_task(execute_scheduled_report_async(schedule_id))


# =============================================
# 告警工作流
# =============================================

async def execute_alert_workflow_async(alert_data: Dict[str, Any]) -> Dict[str, Any]:
    """執行告警工作流"""
    logger.info(f"執行告警工作流: {alert_data.get('product_name')}")

    try:
        from app.services.workflow.triggers import process_price_alert

        async with async_session_maker() as db:
            results = await process_price_alert(db, alert_data)

        logger.info(f"告警工作流執行完成: {len(results)} 個配置被觸發")
        return {
            "success": True,
            "triggered_configs": len(results),
            "results": results,
        }

    except Exception as e:
        logger.error(f"告警工作流執行失敗: {e}")
        return {
            "success": False,
            "error": str(e),
        }


async def process_single_alert_config_async(
    config_id: str,
    alert_data: Dict[str, Any],
) -> Dict[str, Any]:
    """處理單個告警配置"""
    logger.info(f"處理告警配置 {config_id}: {alert_data.get('product_name')}")

    try:
        from app.services.workflow.triggers import AlertTrigger

        async with async_session_maker() as db:
            trigger = AlertTrigger(db)
            config = await trigger.get_config(UUID(config_id))

            if not config:
                return {
                    "success": False,
                    "config_id": config_id,
                    "error": "Config not found",
                }

            if await trigger.should_trigger(config, alert_data):
                return await trigger.execute_workflow(config, alert_data)

            return {
                "success": True,
                "config_id": config_id,
                "triggered": False,
                "reason": "Conditions not met or in quiet hours",
            }

    except Exception as e:
        logger.error(f"處理告警配置失敗 {config_id}: {e}")
        return {
            "success": False,
            "config_id": config_id,
            "error": str(e),
        }


# =============================================
# 報告生成（內部函數，保持不變）
# =============================================

async def _generate_report(
    schedule: ScheduledReport,
    db,
) -> tuple[str, Dict[str, Any]]:
    """生成報告內容"""
    report_type = schedule.report_type
    config = schedule.report_config or {}

    if report_type == ReportType.PRICE_ANALYSIS.value:
        return await _generate_price_analysis_report(config, db)
    elif report_type == ReportType.COMPETITOR_REPORT.value:
        return await _generate_competitor_report(config, db)
    elif report_type == ReportType.SALES_SUMMARY.value:
        return await _generate_sales_summary_report(config, db)
    else:
        return await _generate_default_report(config, db)


async def _generate_price_analysis_report(config: Dict, db) -> tuple[str, Dict]:
    """生成價格分析報告"""
    from sqlalchemy import select
    from app.models.product import Product

    products = config.get("products", [])

    product_query = select(Product)
    if products:
        product_query = product_query.where(Product.name.in_(products))
    product_query = product_query.limit(10)

    result = await db.execute(product_query)
    product_list = result.scalars().all()

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
    report_content: str,
) -> Dict[str, Any]:
    """交付報告到各渠道"""
    delivery_status = {}
    channels = schedule.delivery_channels or {}

    if not channels:
        channels = {"telegram": {"enabled": True}}

    # Telegram 交付
    telegram_config = channels.get("telegram", {})
    telegram_enabled = telegram_config.get("enabled", True) if isinstance(telegram_config, dict) else bool(telegram_config)

    if telegram_enabled:
        try:
            notifier = get_telegram_notifier()

            from app.models.notification import ReportSubscriber
            from app.models.database import async_session_maker as _asm
            from sqlalchemy import select, update as sql_update

            subscriber_chat_ids = []
            async with _asm() as sub_db:
                sub_result = await sub_db.execute(
                    select(ReportSubscriber.chat_id).where(ReportSubscriber.is_active == True)
                )
                subscriber_chat_ids = [row[0] for row in sub_result.all()]

                config_chat_id = telegram_config.get("chat_id") if isinstance(telegram_config, dict) else None
                if config_chat_id and config_chat_id not in subscriber_chat_ids:
                    subscriber_chat_ids.append(config_chat_id)

                if not subscriber_chat_ids and notifier.chat_id:
                    subscriber_chat_ids = [notifier.chat_id]

            sent_count = 0
            failed_ids = []
            for cid in subscriber_chat_ids:
                result = await notifier.send_scheduled_report(
                    schedule_name=schedule.name,
                    report_type=schedule.report_type,
                    report_content=report_content,
                    chat_id=cid,
                )
                if result.get("ok"):
                    sent_count += 1
                else:
                    failed_ids.append(cid)

            if sent_count > 0:
                async with _asm() as sub_db:
                    await sub_db.execute(
                        sql_update(ReportSubscriber)
                        .where(ReportSubscriber.chat_id.in_(
                            [c for c in subscriber_chat_ids if c not in failed_ids]
                        ))
                        .values(last_delivered_at=datetime.utcnow())
                    )
                    await sub_db.commit()

            delivery_status["telegram"] = {
                "sent": sent_count > 0,
                "sent_count": sent_count,
                "total_subscribers": len(subscriber_chat_ids),
                "failed_ids": failed_ids if failed_ids else None,
            }

            logger.info(
                f"Telegram 報告已發送: {schedule.name} → {sent_count}/{len(subscriber_chat_ids)} 訂閱者"
            )

        except Exception as e:
            logger.error(f"Telegram 交付失敗: {e}")
            delivery_status["telegram"] = {"sent": False, "error": str(e)}

    # Email（未實現）
    email_config = channels.get("email", {})
    email_enabled = email_config.get("enabled", False) if isinstance(email_config, dict) else bool(email_config)

    if email_enabled:
        delivery_status["email"] = {"sent": False, "error": "Email delivery not implemented yet"}

    # Webhook（未實現）
    webhook_config = channels.get("webhook", {})
    webhook_enabled = webhook_config.get("enabled", False) if isinstance(webhook_config, dict) else bool(webhook_config)

    if webhook_enabled:
        delivery_status["webhook"] = {"sent": False, "error": "Webhook delivery not implemented yet"}

    return delivery_status
