# =============================================
# SEO 排名追蹤 Celery 任務
# =============================================
#
# 定時任務：
#   - 每日追蹤關鍵詞排名
#   - 每週生成 SEO 報告
# =============================================

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Optional, List
from uuid import UUID

from celery import shared_task

from app.tasks.celery_app import celery_app
from app.models.database import async_session_maker
from app.models.seo_ranking import (
    KeywordConfig, KeywordRanking, SEOReport, RankingScrapeJob,
    KeywordType, ReportType
)
from app.services.seo_ranking_service import SEORankingService

logger = logging.getLogger(__name__)


# =============================================
# 排名追蹤任務
# =============================================

@celery_app.task(
    name="app.tasks.seo_ranking_tasks.track_all_keywords",
    bind=True,
    max_retries=3,
    default_retry_delay=300  # 5 分鐘後重試
)
def track_all_keywords(self, product_id: Optional[str] = None):
    """
    追蹤所有啟用的關鍵詞排名

    Args:
        product_id: 可選，只追蹤特定產品的關鍵詞
    """
    logger.info("開始執行關鍵詞排名追蹤任務")

    try:
        # 使用 asyncio 運行異步任務
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            result = loop.run_until_complete(
                _async_track_all_keywords(
                    UUID(product_id) if product_id else None
                )
            )
            logger.info(f"排名追蹤任務完成: {result}")
            return result
        finally:
            loop.close()

    except Exception as e:
        logger.error(f"排名追蹤任務失敗: {e}")
        # 重試
        raise self.retry(exc=e)


async def _async_track_all_keywords(product_id: Optional[UUID] = None) -> dict:
    """異步執行關鍵詞追蹤"""
    async with async_session_maker() as db:
        service = SEORankingService(db)
        job = await service.track_all_keywords(product_id=product_id)

        return {
            "job_id": str(job.id),
            "status": job.status,
            "total": job.total_keywords,
            "successful": job.successful_keywords,
            "failed": job.failed_keywords,
            "duration_seconds": job.duration_seconds
        }


@celery_app.task(
    name="app.tasks.seo_ranking_tasks.track_single_keyword",
    bind=True,
    max_retries=3,
    default_retry_delay=60
)
def track_single_keyword(self, keyword_config_id: str):
    """
    追蹤單個關鍵詞排名

    Args:
        keyword_config_id: 關鍵詞配置 ID
    """
    logger.info(f"追蹤關鍵詞: {keyword_config_id}")

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            result = loop.run_until_complete(
                _async_track_single_keyword(UUID(keyword_config_id))
            )
            return result
        finally:
            loop.close()

    except Exception as e:
        logger.error(f"追蹤關鍵詞失敗: {keyword_config_id}, 錯誤: {e}")
        raise self.retry(exc=e)


async def _async_track_single_keyword(keyword_config_id: UUID) -> dict:
    """異步追蹤單個關鍵詞"""
    async with async_session_maker() as db:
        # 獲取關鍵詞配置
        config = await db.get(KeywordConfig, keyword_config_id)
        if not config:
            return {"error": "關鍵詞配置不存在"}

        if not config.is_active:
            return {"error": "關鍵詞配置已停用"}

        service = SEORankingService(db)
        ranking = await service.track_keyword(config)

        return {
            "keyword": config.keyword,
            "google_rank": ranking.google_rank,
            "hktvmall_rank": ranking.hktvmall_rank,
            "tracked_at": ranking.tracked_at.isoformat()
        }


# =============================================
# 報告生成任務
# =============================================

@celery_app.task(
    name="app.tasks.seo_ranking_tasks.generate_weekly_reports",
    bind=True,
    max_retries=2
)
def generate_weekly_reports(self):
    """
    生成每週 SEO 報告

    為所有有追蹤數據的產品生成週報
    """
    logger.info("開始生成週報")

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            result = loop.run_until_complete(_async_generate_weekly_reports())
            logger.info(f"週報生成完成: {result}")
            return result
        finally:
            loop.close()

    except Exception as e:
        logger.error(f"週報生成失敗: {e}")
        raise self.retry(exc=e)


async def _async_generate_weekly_reports() -> dict:
    """異步生成週報"""
    from sqlalchemy import select, func, distinct

    async with async_session_maker() as db:
        # 查找所有有關鍵詞配置的產品
        product_query = (
            select(distinct(KeywordConfig.product_id))
            .where(KeywordConfig.is_active == True)
            .where(KeywordConfig.product_id.isnot(None))
        )
        result = await db.execute(product_query)
        product_ids = [row[0] for row in result.fetchall()]

        reports_created = 0
        errors = []

        for product_id in product_ids:
            try:
                await _generate_product_report(db, product_id, ReportType.WEEKLY, 7)
                reports_created += 1
            except Exception as e:
                logger.error(f"生成產品週報失敗: {product_id}, 錯誤: {e}")
                errors.append({"product_id": str(product_id), "error": str(e)})

        # 生成整體報告（無產品關聯）
        try:
            await _generate_product_report(db, None, ReportType.WEEKLY, 7)
            reports_created += 1
        except Exception as e:
            logger.error(f"生成整體週報失敗: {e}")

        return {
            "reports_created": reports_created,
            "errors": errors
        }


@celery_app.task(name="app.tasks.seo_ranking_tasks.generate_report")
def generate_report(
    product_id: Optional[str] = None,
    report_type: str = "weekly",
    period_days: int = 7
):
    """
    手動生成 SEO 報告

    Args:
        product_id: 產品 ID（可選）
        report_type: 報告類型 (daily, weekly, monthly)
        period_days: 報告週期天數
    """
    logger.info(f"生成 SEO 報告: product={product_id}, type={report_type}")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        result = loop.run_until_complete(
            _async_generate_report(
                UUID(product_id) if product_id else None,
                ReportType(report_type),
                period_days
            )
        )
        return result
    finally:
        loop.close()


async def _async_generate_report(
    product_id: Optional[UUID],
    report_type: ReportType,
    period_days: int
) -> dict:
    """異步生成報告"""
    async with async_session_maker() as db:
        report = await _generate_product_report(db, product_id, report_type, period_days)
        return {
            "report_id": str(report.id),
            "title": report.report_title,
            "status": report.status
        }


async def _generate_product_report(
    db,
    product_id: Optional[UUID],
    report_type: ReportType,
    period_days: int
) -> SEOReport:
    """
    生成產品 SEO 報告

    分析指定週期內的排名數據，生成優化建議
    """
    from sqlalchemy import select, func, and_

    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=period_days)

    # 查詢該產品的關鍵詞配置
    config_query = select(KeywordConfig).where(KeywordConfig.is_active == True)
    if product_id:
        config_query = config_query.where(KeywordConfig.product_id == product_id)

    config_result = await db.execute(config_query)
    configs = config_result.scalars().all()

    # 查詢排名記錄
    ranking_query = (
        select(KeywordRanking)
        .where(KeywordRanking.tracked_at >= start_date)
        .where(KeywordRanking.tracked_at <= end_date)
    )
    if product_id:
        ranking_query = ranking_query.where(KeywordRanking.product_id == product_id)

    ranking_result = await db.execute(ranking_query)
    rankings = ranking_result.scalars().all()

    # 計算 Google 摘要
    google_summary = _calculate_source_summary(configs, rankings, "google")

    # 計算 HKTVmall 摘要
    hktvmall_summary = _calculate_source_summary(configs, rankings, "hktvmall")

    # 生成關鍵詞詳情
    keyword_details = []
    for config in configs:
        config_rankings = [r for r in rankings if r.keyword_config_id == config.id]

        google_ranks = [r.google_rank for r in config_rankings if r.google_rank]
        hktvmall_ranks = [r.hktvmall_rank for r in config_rankings if r.hktvmall_rank]

        # 計算變化
        google_change = None
        if len(google_ranks) >= 2:
            google_change = google_ranks[0] - google_ranks[-1]  # 最新 - 最早

        hktvmall_change = None
        if len(hktvmall_ranks) >= 2:
            hktvmall_change = hktvmall_ranks[0] - hktvmall_ranks[-1]

        keyword_details.append({
            "keyword": config.keyword,
            "type": config.keyword_type.value,
            "google_rank": config.latest_google_rank,
            "google_change": google_change,
            "hktvmall_rank": config.latest_hktvmall_rank,
            "hktvmall_change": hktvmall_change,
            "target_google": config.target_google_rank,
            "target_hktvmall": config.target_hktvmall_rank
        })

    # 生成優化建議
    recommendations = _generate_recommendations(configs, keyword_details)

    # 計算改進分數
    improvement_score = _calculate_improvement_score(keyword_details)

    # 創建報告
    report = SEOReport(
        product_id=product_id,
        report_type=report_type,
        report_title=f"SEO 優化報告 - {start_date.strftime('%Y-%m-%d')} 至 {end_date.strftime('%Y-%m-%d')}",
        report_period_start=start_date,
        report_period_end=end_date,
        google_summary=google_summary,
        hktvmall_summary=hktvmall_summary,
        keyword_details=keyword_details,
        recommendations=recommendations,
        improvement_score=improvement_score,
        status="published",
        published_at=datetime.utcnow()
    )

    db.add(report)
    await db.commit()
    await db.refresh(report)

    return report


def _calculate_source_summary(configs: list, rankings: list, source: str) -> dict:
    """計算來源摘要統計"""
    if source == "google":
        ranks = [c.latest_google_rank for c in configs if c.latest_google_rank]
        rank_field = "google_rank"
    else:
        ranks = [c.latest_hktvmall_rank for c in configs if c.latest_hktvmall_rank]
        rank_field = "hktvmall_rank"

    total = len(configs)
    ranked = len(ranks)
    top_10 = len([r for r in ranks if r <= 10])
    top_30 = len([r for r in ranks if r <= 30])
    avg = round(sum(ranks) / len(ranks), 1) if ranks else None

    # 計算改進/下降數
    improved = 0
    declined = 0
    for config in configs:
        config_rankings = [
            getattr(r, rank_field)
            for r in rankings
            if r.keyword_config_id == config.id and getattr(r, rank_field)
        ]
        if len(config_rankings) >= 2:
            if config_rankings[0] < config_rankings[-1]:  # 排名數字變小 = 改進
                improved += 1
            elif config_rankings[0] > config_rankings[-1]:
                declined += 1

    return {
        "total_keywords": total,
        "ranked_keywords": ranked,
        "top_10_count": top_10,
        "top_30_count": top_30,
        "avg_rank": avg,
        "improved_count": improved,
        "declined_count": declined,
        "unchanged_count": ranked - improved - declined
    }


def _generate_recommendations(configs: list, keyword_details: list) -> list:
    """生成優化建議"""
    recommendations = []

    for detail in keyword_details:
        keyword = detail["keyword"]
        google_rank = detail.get("google_rank")
        hktvmall_rank = detail.get("hktvmall_rank")
        target_google = detail.get("target_google")
        target_hktvmall = detail.get("target_hktvmall")

        # Google 排名優化建議
        if google_rank:
            if google_rank > 30:
                recommendations.append({
                    "priority": "high",
                    "category": "google_ranking",
                    "keyword": keyword,
                    "current_issue": f"關鍵詞 '{keyword}' 在 Google 排名第 {google_rank}，未進入前 30",
                    "suggestion": "建議優化產品標題和描述，加入更多相關關鍵詞，考慮建立外部連結",
                    "expected_impact": "預計可提升 10-20 名排名"
                })
            elif google_rank > 10 and target_google and target_google <= 10:
                recommendations.append({
                    "priority": "medium",
                    "category": "google_ranking",
                    "keyword": keyword,
                    "current_issue": f"關鍵詞 '{keyword}' 在 Google 排名第 {google_rank}，距離目標 Top {target_google} 還差 {google_rank - target_google} 名",
                    "suggestion": "建議優化內容質量，增加用戶互動信號，提升頁面載入速度",
                    "expected_impact": "預計可提升 5-10 名排名"
                })

        # HKTVmall 排名優化建議
        if hktvmall_rank:
            if hktvmall_rank > 20:
                recommendations.append({
                    "priority": "high",
                    "category": "hktvmall_ranking",
                    "keyword": keyword,
                    "current_issue": f"關鍵詞 '{keyword}' 在 HKTVmall 站內排名第 {hktvmall_rank}",
                    "suggestion": "建議優化產品標題關鍵詞匹配度，檢查產品屬性標籤，考慮調整價格策略",
                    "expected_impact": "預計可提升站內曝光度 30%"
                })

        # 無排名數據建議
        if not google_rank and not hktvmall_rank:
            recommendations.append({
                "priority": "high",
                "category": "no_ranking",
                "keyword": keyword,
                "current_issue": f"關鍵詞 '{keyword}' 未獲得任何排名數據",
                "suggestion": "確保關鍵詞出現在產品標題中，檢查產品頁面是否被正確索引",
                "expected_impact": "獲得基礎排名後可持續優化"
            })

    # 按優先級排序
    priority_order = {"high": 0, "medium": 1, "low": 2}
    recommendations.sort(key=lambda x: priority_order.get(x["priority"], 3))

    return recommendations[:10]  # 最多返回 10 條建議


def _calculate_improvement_score(keyword_details: list) -> int:
    """
    計算改進分數

    範圍: -100 到 100
    正數表示整體改進，負數表示整體下降
    """
    if not keyword_details:
        return 0

    total_change = 0
    count = 0

    for detail in keyword_details:
        google_change = detail.get("google_change")
        hktvmall_change = detail.get("hktvmall_change")

        # 排名變化為正數表示改進（排名數字變小）
        if google_change is not None:
            total_change += google_change
            count += 1
        if hktvmall_change is not None:
            total_change += hktvmall_change
            count += 1

    if count == 0:
        return 0

    # 平均變化，限制在 -100 到 100 範圍
    avg_change = total_change / count
    score = int(min(100, max(-100, avg_change * 5)))  # 乘以 5 放大效果

    return score
