# =============================================
# SEO 排名追蹤任務（純 async，無 Celery 依賴）
# =============================================

import logging
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from app.models.database import async_session_maker
from app.models.seo_ranking import (
    KeywordConfig, KeywordRanking, SEOReport, RankingScrapeJob,
    KeywordType, ReportType
)
from app.services.seo_ranking_service import SEORankingService

logger = logging.getLogger(__name__)


# =============================================
# 排名追蹤
# =============================================

async def track_all_keywords_async(product_id: Optional[str] = None) -> dict:
    """追蹤所有啟用的關鍵詞排名"""
    logger.info("開始執行關鍵詞排名追蹤任務")

    async with async_session_maker() as db:
        service = SEORankingService(db)
        job = await service.track_all_keywords(
            product_id=UUID(product_id) if product_id else None
        )

        result = {
            "job_id": str(job.id),
            "status": job.status,
            "total": job.total_keywords,
            "successful": job.successful_keywords,
            "failed": job.failed_keywords,
            "duration_seconds": job.duration_seconds,
        }
        logger.info(f"排名追蹤任務完成: {result}")
        return result


async def track_single_keyword_async(keyword_config_id: str) -> dict:
    """追蹤單個關鍵詞排名"""
    logger.info(f"追蹤關鍵詞: {keyword_config_id}")

    async with async_session_maker() as db:
        config = await db.get(KeywordConfig, UUID(keyword_config_id))
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
            "tracked_at": ranking.tracked_at.isoformat(),
        }


# =============================================
# 報告生成
# =============================================

async def generate_weekly_reports_async() -> dict:
    """生成每週 SEO 報告"""
    logger.info("開始生成週報")

    from sqlalchemy import select, distinct

    async with async_session_maker() as db:
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

        # 整體報告
        try:
            await _generate_product_report(db, None, ReportType.WEEKLY, 7)
            reports_created += 1
        except Exception as e:
            logger.error(f"生成整體週報失敗: {e}")

        result = {"reports_created": reports_created, "errors": errors}
        logger.info(f"週報生成完成: {result}")
        return result


async def generate_report_async(
    product_id: Optional[str] = None,
    report_type: str = "weekly",
    period_days: int = 7,
) -> dict:
    """手動生成 SEO 報告"""
    logger.info(f"生成 SEO 報告: product={product_id}, type={report_type}")

    async with async_session_maker() as db:
        report = await _generate_product_report(
            db,
            UUID(product_id) if product_id else None,
            ReportType(report_type),
            period_days,
        )
        return {
            "report_id": str(report.id),
            "title": report.report_title,
            "status": report.status,
        }


# =============================================
# 內部輔助函數（保持不變）
# =============================================

async def _generate_product_report(
    db,
    product_id: Optional[UUID],
    report_type: ReportType,
    period_days: int,
) -> SEOReport:
    """生成產品 SEO 報告"""
    from sqlalchemy import select

    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=period_days)

    config_query = select(KeywordConfig).where(KeywordConfig.is_active == True)
    if product_id:
        config_query = config_query.where(KeywordConfig.product_id == product_id)

    config_result = await db.execute(config_query)
    configs = config_result.scalars().all()

    ranking_query = (
        select(KeywordRanking)
        .where(KeywordRanking.tracked_at >= start_date)
        .where(KeywordRanking.tracked_at <= end_date)
    )
    if product_id:
        ranking_query = ranking_query.where(KeywordRanking.product_id == product_id)

    ranking_result = await db.execute(ranking_query)
    rankings = ranking_result.scalars().all()

    google_summary = _calculate_source_summary(configs, rankings, "google")
    hktvmall_summary = _calculate_source_summary(configs, rankings, "hktvmall")

    keyword_details = []
    for config in configs:
        config_rankings = [r for r in rankings if r.keyword_config_id == config.id]

        google_ranks = [r.google_rank for r in config_rankings if r.google_rank]
        hktvmall_ranks = [r.hktvmall_rank for r in config_rankings if r.hktvmall_rank]

        google_change = None
        if len(google_ranks) >= 2:
            google_change = google_ranks[0] - google_ranks[-1]

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
            "target_hktvmall": config.target_hktvmall_rank,
        })

    recommendations = _generate_recommendations(configs, keyword_details)
    improvement_score = _calculate_improvement_score(keyword_details)

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
        published_at=datetime.utcnow(),
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

    improved = 0
    declined = 0
    for config in configs:
        config_rankings = [
            getattr(r, rank_field)
            for r in rankings
            if r.keyword_config_id == config.id and getattr(r, rank_field)
        ]
        if len(config_rankings) >= 2:
            if config_rankings[0] < config_rankings[-1]:
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
        "unchanged_count": ranked - improved - declined,
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

        if google_rank:
            if google_rank > 30:
                recommendations.append({
                    "priority": "high",
                    "category": "google_ranking",
                    "keyword": keyword,
                    "current_issue": f"關鍵詞 '{keyword}' 在 Google 排名第 {google_rank}，未進入前 30",
                    "suggestion": "建議優化產品標題和描述，加入更多相關關鍵詞，考慮建立外部連結",
                    "expected_impact": "預計可提升 10-20 名排名",
                })
            elif google_rank > 10 and target_google and target_google <= 10:
                recommendations.append({
                    "priority": "medium",
                    "category": "google_ranking",
                    "keyword": keyword,
                    "current_issue": f"關鍵詞 '{keyword}' 在 Google 排名第 {google_rank}，距離目標 Top {target_google} 還差 {google_rank - target_google} 名",
                    "suggestion": "建議優化內容質量，增加用戶互動信號，提升頁面載入速度",
                    "expected_impact": "預計可提升 5-10 名排名",
                })

        if hktvmall_rank:
            if hktvmall_rank > 20:
                recommendations.append({
                    "priority": "high",
                    "category": "hktvmall_ranking",
                    "keyword": keyword,
                    "current_issue": f"關鍵詞 '{keyword}' 在 HKTVmall 站內排名第 {hktvmall_rank}",
                    "suggestion": "建議優化產品標題關鍵詞匹配度，檢查產品屬性標籤，考慮調整價格策略",
                    "expected_impact": "預計可提升站內曝光度 30%",
                })

        if not google_rank and not hktvmall_rank:
            recommendations.append({
                "priority": "high",
                "category": "no_ranking",
                "keyword": keyword,
                "current_issue": f"關鍵詞 '{keyword}' 未獲得任何排名數據",
                "suggestion": "確保關鍵詞出現在產品標題中，檢查產品頁面是否被正確索引",
                "expected_impact": "獲得基礎排名後可持續優化",
            })

    priority_order = {"high": 0, "medium": 1, "low": 2}
    recommendations.sort(key=lambda x: priority_order.get(x["priority"], 3))

    return recommendations[:10]


def _calculate_improvement_score(keyword_details: list) -> int:
    """計算改進分數 (-100 到 100)"""
    if not keyword_details:
        return 0

    total_change = 0
    count = 0

    for detail in keyword_details:
        google_change = detail.get("google_change")
        hktvmall_change = detail.get("hktvmall_change")

        if google_change is not None:
            total_change += google_change
            count += 1
        if hktvmall_change is not None:
            total_change += hktvmall_change
            count += 1

    if count == 0:
        return 0

    avg_change = total_change / count
    score = int(min(100, max(-100, avg_change * 5)))

    return score
