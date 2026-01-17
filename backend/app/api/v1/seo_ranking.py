# =============================================
# SEO 排名追蹤 API
# =============================================
#
# 功能：
#   - 關鍵詞配置管理（CRUD）
#   - 排名查詢與歷史
#   - 排名排行榜
#   - SEO 報告
#   - 排名警報
#   - 抓取任務管理
#   - 儀表板數據
# =============================================

import logging
from datetime import datetime, timedelta
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy import select, func, and_, or_, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.database import get_db
from app.models.seo_ranking import (
    KeywordConfig, KeywordRanking, SEOReport, RankingAlert, RankingScrapeJob,
    KeywordType, RankingSource, ReportType, AlertSeverity
)
from app.models.product import Product
from app.schemas.seo_ranking import (
    # 關鍵詞配置
    KeywordConfigCreate, KeywordConfigUpdate, KeywordConfigResponse,
    KeywordConfigListResponse, KeywordConfigBatchCreate, KeywordConfigBatchResponse,
    # 排名
    KeywordRankingResponse, KeywordRankingHistoryRequest, KeywordRankingHistoryResponse,
    RankingHistorySummary,
    # 排行榜
    RankingLeaderboardRequest, RankingLeaderboardResponse, LeaderboardEntry, LeaderboardSummary,
    # 報告
    SEOReportGenerateRequest, SEOReportResponse, SEOReportListResponse,
    # 警報
    RankingAlertResponse, RankingAlertListResponse, RankingAlertResolve, RankingAlertBatchAction,
    # 抓取任務
    RankingScrapeRequest, RankingScrapeJobResponse, RankingScrapeJobListResponse,
    # 儀表板
    SEODashboardRequest, SEODashboardResponse, DashboardOverview,
    RankingSummaryBySource, RankingTrendPoint,
    # 競品對比
    CompetitorComparisonRequest, CompetitorComparisonResponse,
    # 枚舉
    KeywordTypeEnum, RankingSourceEnum, AlertSeverityEnum, ScrapeJobStatusEnum, ReportTypeEnum
)

logger = logging.getLogger(__name__)

router = APIRouter()


# =============================================
# 關鍵詞配置 API
# =============================================

@router.post("/keywords", response_model=KeywordConfigResponse)
async def create_keyword_config(
    request: KeywordConfigCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    創建關鍵詞追蹤配置

    - 設定要追蹤的關鍵詞
    - 可關聯到特定產品
    - 設定追蹤 Google/HKTVmall 排名
    - 設定目標排名
    """
    # 檢查關鍵詞是否已存在（同一產品下）
    normalized = request.keyword.strip().lower()

    existing_query = select(KeywordConfig).where(
        and_(
            KeywordConfig.keyword_normalized == normalized,
            KeywordConfig.product_id == request.product_id
        )
    )
    existing = await db.execute(existing_query)
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail=f"關鍵詞 '{request.keyword}' 已存在於該產品下"
        )

    # 驗證產品存在（如果有 product_id）
    if request.product_id:
        product = await db.get(Product, request.product_id)
        if not product:
            raise HTTPException(status_code=404, detail="產品不存在")

    # 創建配置
    config = KeywordConfig(
        product_id=request.product_id,
        keyword=request.keyword.strip(),
        keyword_normalized=normalized,
        keyword_type=KeywordType(request.keyword_type.value),
        track_google=request.track_google,
        track_hktvmall=request.track_hktvmall,
        target_google_rank=request.target_google_rank,
        target_hktvmall_rank=request.target_hktvmall_rank,
        track_competitors=request.track_competitors,
        competitor_product_ids=[str(pid) for pid in request.competitor_product_ids],
        notes=request.notes,
        tags=request.tags
    )

    db.add(config)
    await db.commit()
    await db.refresh(config)

    return _build_keyword_config_response(config)


@router.post("/keywords/batch", response_model=KeywordConfigBatchResponse)
async def batch_create_keyword_configs(
    request: KeywordConfigBatchCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    批量創建關鍵詞配置

    - 一次添加多個關鍵詞
    - 自動跳過已存在的關鍵詞
    """
    created_configs = []
    skipped = 0
    errors = []

    for keyword in request.keywords:
        normalized = keyword.strip().lower()

        # 檢查是否已存在
        existing_query = select(KeywordConfig).where(
            and_(
                KeywordConfig.keyword_normalized == normalized,
                KeywordConfig.product_id == request.product_id
            )
        )
        existing = await db.execute(existing_query)
        if existing.scalar_one_or_none():
            skipped += 1
            continue

        try:
            config = KeywordConfig(
                product_id=request.product_id,
                keyword=keyword.strip(),
                keyword_normalized=normalized,
                keyword_type=KeywordType(request.keyword_type.value),
                track_google=request.track_google,
                track_hktvmall=request.track_hktvmall
            )
            db.add(config)
            await db.flush()
            created_configs.append(config)
        except Exception as e:
            errors.append(f"創建 '{keyword}' 失敗: {str(e)}")

    await db.commit()

    return KeywordConfigBatchResponse(
        created=len(created_configs),
        skipped=skipped,
        errors=errors,
        configs=[_build_keyword_config_response(c) for c in created_configs]
    )


@router.get("/keywords", response_model=KeywordConfigListResponse)
async def list_keyword_configs(
    product_id: Optional[UUID] = Query(None, description="按產品篩選"),
    keyword_type: Optional[KeywordTypeEnum] = Query(None, description="按類型篩選"),
    is_active: Optional[bool] = Query(None, description="按啟用狀態篩選"),
    search: Optional[str] = Query(None, description="搜尋關鍵詞"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    列出關鍵詞配置

    支援篩選：
    - 產品 ID
    - 關鍵詞類型
    - 啟用狀態
    - 關鍵詞搜尋
    """
    query = select(KeywordConfig)

    # 篩選條件
    if product_id:
        query = query.where(KeywordConfig.product_id == product_id)
    if keyword_type:
        query = query.where(KeywordConfig.keyword_type == KeywordType(keyword_type.value))
    if is_active is not None:
        query = query.where(KeywordConfig.is_active == is_active)
    if search:
        query = query.where(KeywordConfig.keyword.ilike(f"%{search}%"))

    # 計算總數
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.execute(count_query)
    total = total.scalar() or 0

    # 分頁
    query = query.order_by(desc(KeywordConfig.created_at))
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    configs = result.scalars().all()

    return KeywordConfigListResponse(
        data=[_build_keyword_config_response(c) for c in configs],
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/keywords/{config_id}", response_model=KeywordConfigResponse)
async def get_keyword_config(
    config_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """獲取關鍵詞配置詳情"""
    config = await db.get(KeywordConfig, config_id)
    if not config:
        raise HTTPException(status_code=404, detail="關鍵詞配置不存在")

    return _build_keyword_config_response(config)


@router.patch("/keywords/{config_id}", response_model=KeywordConfigResponse)
async def update_keyword_config(
    config_id: UUID,
    request: KeywordConfigUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新關鍵詞配置"""
    config = await db.get(KeywordConfig, config_id)
    if not config:
        raise HTTPException(status_code=404, detail="關鍵詞配置不存在")

    # 更新字段
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "keyword_type" and value:
            setattr(config, field, KeywordType(value.value))
        elif field == "competitor_product_ids" and value:
            setattr(config, field, [str(pid) for pid in value])
        else:
            setattr(config, field, value)

    await db.commit()
    await db.refresh(config)

    return _build_keyword_config_response(config)


@router.delete("/keywords/{config_id}")
async def delete_keyword_config(
    config_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """刪除關鍵詞配置（及其所有排名記錄）"""
    config = await db.get(KeywordConfig, config_id)
    if not config:
        raise HTTPException(status_code=404, detail="關鍵詞配置不存在")

    await db.delete(config)
    await db.commit()

    return {"message": "關鍵詞配置已刪除", "id": str(config_id)}


# =============================================
# 排名查詢 API
# =============================================

@router.get("/rankings/{config_id}/history", response_model=KeywordRankingHistoryResponse)
async def get_ranking_history(
    config_id: UUID,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    limit: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db)
):
    """
    獲取關鍵詞排名歷史

    - 默認返回最近 30 條記錄
    - 可指定日期範圍
    """
    config = await db.get(KeywordConfig, config_id)
    if not config:
        raise HTTPException(status_code=404, detail="關鍵詞配置不存在")

    query = select(KeywordRanking).where(
        KeywordRanking.keyword_config_id == config_id
    )

    if start_date:
        query = query.where(KeywordRanking.tracked_at >= start_date)
    if end_date:
        query = query.where(KeywordRanking.tracked_at <= end_date)

    query = query.order_by(desc(KeywordRanking.tracked_at)).limit(limit)

    result = await db.execute(query)
    rankings = result.scalars().all()

    # 計算摘要統計
    summary = _calculate_ranking_summary(rankings)

    return KeywordRankingHistoryResponse(
        keyword=config.keyword,
        keyword_config_id=config_id,
        records=[_build_ranking_response(r) for r in rankings],
        summary=summary
    )


@router.get("/rankings/latest")
async def get_latest_rankings(
    product_id: Optional[UUID] = Query(None),
    keyword_type: Optional[KeywordTypeEnum] = Query(None),
    source: Optional[RankingSourceEnum] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db)
):
    """
    獲取最新排名數據

    返回每個關鍵詞的最新排名記錄
    """
    # 子查詢：每個 keyword_config 的最新記錄
    subquery = (
        select(
            KeywordRanking.keyword_config_id,
            func.max(KeywordRanking.tracked_at).label("max_tracked_at")
        )
        .group_by(KeywordRanking.keyword_config_id)
        .subquery()
    )

    query = (
        select(KeywordRanking)
        .join(
            subquery,
            and_(
                KeywordRanking.keyword_config_id == subquery.c.keyword_config_id,
                KeywordRanking.tracked_at == subquery.c.max_tracked_at
            )
        )
        .join(KeywordConfig, KeywordRanking.keyword_config_id == KeywordConfig.id)
    )

    if product_id:
        query = query.where(KeywordConfig.product_id == product_id)
    if keyword_type:
        query = query.where(KeywordConfig.keyword_type == KeywordType(keyword_type.value))

    query = query.limit(limit)

    result = await db.execute(query)
    rankings = result.scalars().all()

    return {
        "data": [_build_ranking_response(r) for r in rankings],
        "total": len(rankings)
    }


# =============================================
# 排名排行榜 API
# =============================================

@router.get("/leaderboard", response_model=RankingLeaderboardResponse)
async def get_ranking_leaderboard(
    source: RankingSourceEnum = Query(RankingSourceEnum.GOOGLE_HK),
    keyword_type: Optional[KeywordTypeEnum] = Query(None),
    product_id: Optional[UUID] = Query(None),
    sort_by: str = Query("rank_asc", description="rank_asc, rank_desc, change_asc, change_desc"),
    limit: int = Query(20, ge=1, le=100),
    include_unranked: bool = Query(False),
    db: AsyncSession = Depends(get_db)
):
    """
    獲取排名排行榜

    - 按 Google 或 HKTVmall 排名排序
    - 顯示排名最好/最差的關鍵詞
    - 顯示排名變化
    """
    query = select(KeywordConfig).where(KeywordConfig.is_active == True)

    if product_id:
        query = query.where(KeywordConfig.product_id == product_id)
    if keyword_type:
        query = query.where(KeywordConfig.keyword_type == KeywordType(keyword_type.value))

    # 根據來源選擇排名字段
    if source == RankingSourceEnum.GOOGLE_HK:
        rank_field = KeywordConfig.latest_google_rank
        if not include_unranked:
            query = query.where(KeywordConfig.latest_google_rank.isnot(None))
    else:
        rank_field = KeywordConfig.latest_hktvmall_rank
        if not include_unranked:
            query = query.where(KeywordConfig.latest_hktvmall_rank.isnot(None))

    # 排序
    if sort_by == "rank_asc":
        query = query.order_by(asc(rank_field.nulls_last()))
    elif sort_by == "rank_desc":
        query = query.order_by(desc(rank_field.nulls_last()))

    query = query.limit(limit)

    result = await db.execute(query)
    configs = result.scalars().all()

    # 構建排行榜條目
    entries = []
    for idx, config in enumerate(configs, 1):
        if source == RankingSourceEnum.GOOGLE_HK:
            current_rank = config.latest_google_rank
            target_rank = config.target_google_rank
            baseline = config.baseline_google_rank
        else:
            current_rank = config.latest_hktvmall_rank
            target_rank = config.target_hktvmall_rank
            baseline = config.baseline_hktvmall_rank

        rank_change = None
        if baseline and current_rank:
            rank_change = baseline - current_rank  # 正數表示排名上升

        target_gap = None
        if target_rank and current_rank:
            target_gap = current_rank - target_rank  # 正數表示還差多少

        entries.append(LeaderboardEntry(
            rank=idx,
            keyword_config_id=config.id,
            keyword=config.keyword,
            keyword_type=config.keyword_type.value,
            product_id=config.product_id,
            current_rank=current_rank,
            previous_rank=baseline,
            rank_change=rank_change,
            target_rank=target_rank,
            target_gap=target_gap,
            last_tracked_at=config.latest_tracked_at
        ))

    # 計算摘要
    total = len(configs)
    ranked = len([e for e in entries if e.current_rank is not None])
    top_10 = len([e for e in entries if e.current_rank and e.current_rank <= 10])
    top_30 = len([e for e in entries if e.current_rank and e.current_rank <= 30])
    ranks = [e.current_rank for e in entries if e.current_rank]
    avg_rank = sum(ranks) / len(ranks) if ranks else None

    improved = len([e for e in entries if e.rank_change and e.rank_change > 0])
    declined = len([e for e in entries if e.rank_change and e.rank_change < 0])

    return RankingLeaderboardResponse(
        source=source.value,
        generated_at=datetime.utcnow(),
        entries=entries,
        summary=LeaderboardSummary(
            total_keywords=total,
            ranked_keywords=ranked,
            unranked_keywords=total - ranked,
            top_10_count=top_10,
            top_30_count=top_30,
            avg_rank=round(avg_rank, 1) if avg_rank else None,
            improved_count=improved,
            declined_count=declined
        )
    )


# =============================================
# 警報 API
# =============================================

@router.get("/alerts", response_model=RankingAlertListResponse)
async def list_alerts(
    is_read: Optional[bool] = Query(None),
    severity: Optional[AlertSeverityEnum] = Query(None),
    product_id: Optional[UUID] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db)
):
    """列出排名警報"""
    query = select(RankingAlert)

    if is_read is not None:
        query = query.where(RankingAlert.is_read == is_read)
    if severity:
        query = query.where(RankingAlert.severity == AlertSeverity(severity.value))
    if product_id:
        query = query.where(RankingAlert.product_id == product_id)

    query = query.order_by(desc(RankingAlert.created_at)).limit(limit)

    result = await db.execute(query)
    alerts = result.scalars().all()

    # 計算未讀數
    unread_query = select(func.count()).select_from(RankingAlert).where(
        RankingAlert.is_read == False
    )
    unread_count = await db.execute(unread_query)
    unread_count = unread_count.scalar() or 0

    return RankingAlertListResponse(
        data=[_build_alert_response(a) for a in alerts],
        total=len(alerts),
        unread_count=unread_count
    )


@router.patch("/alerts/{alert_id}/read")
async def mark_alert_read(
    alert_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """標記警報為已讀"""
    alert = await db.get(RankingAlert, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="警報不存在")

    alert.is_read = True
    await db.commit()

    return {"message": "已標記為已讀"}


@router.patch("/alerts/{alert_id}/resolve")
async def resolve_alert(
    alert_id: UUID,
    request: RankingAlertResolve,
    db: AsyncSession = Depends(get_db)
):
    """解決警報"""
    alert = await db.get(RankingAlert, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="警報不存在")

    alert.is_resolved = True
    alert.resolved_at = datetime.utcnow()
    alert.resolution_notes = request.resolution_notes
    await db.commit()

    return {"message": "警報已解決"}


@router.post("/alerts/batch")
async def batch_alert_action(
    request: RankingAlertBatchAction,
    db: AsyncSession = Depends(get_db)
):
    """批量處理警報"""
    query = select(RankingAlert).where(RankingAlert.id.in_(request.alert_ids))
    result = await db.execute(query)
    alerts = result.scalars().all()

    for alert in alerts:
        if request.action == "mark_read":
            alert.is_read = True
        elif request.action == "mark_unread":
            alert.is_read = False
        elif request.action == "resolve":
            alert.is_resolved = True
            alert.resolved_at = datetime.utcnow()
            alert.resolution_notes = request.resolution_notes

    await db.commit()

    return {"message": f"已處理 {len(alerts)} 個警報"}


# =============================================
# 抓取任務 API
# =============================================

@router.post("/scrape", response_model=RankingScrapeJobResponse)
async def trigger_ranking_scrape(
    request: RankingScrapeRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    觸發排名抓取任務

    - 可指定抓取類型（全部/僅 Google/僅 HKTVmall）
    - 可指定特定關鍵詞或產品
    """
    # 計算要抓取的關鍵詞數量
    query = select(KeywordConfig).where(KeywordConfig.is_active == True)

    if request.keyword_config_ids:
        query = query.where(KeywordConfig.id.in_(request.keyword_config_ids))
    elif request.product_id:
        query = query.where(KeywordConfig.product_id == request.product_id)

    result = await db.execute(query)
    configs = result.scalars().all()

    if not configs:
        raise HTTPException(status_code=400, detail="沒有找到要抓取的關鍵詞")

    # 創建任務記錄
    job = RankingScrapeJob(
        job_type=request.job_type,
        status="pending",
        total_keywords=len(configs),
        triggered_by="api"
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)

    # 啟動後台任務
    # TODO: 實際的抓取邏輯將在 service 層實現
    # background_tasks.add_task(execute_ranking_scrape, job.id, request)

    return _build_scrape_job_response(job)


@router.get("/scrape/jobs", response_model=RankingScrapeJobListResponse)
async def list_scrape_jobs(
    status: Optional[ScrapeJobStatusEnum] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """列出抓取任務"""
    query = select(RankingScrapeJob)

    if status:
        query = query.where(RankingScrapeJob.status == status.value)

    query = query.order_by(desc(RankingScrapeJob.created_at)).limit(limit)

    result = await db.execute(query)
    jobs = result.scalars().all()

    return RankingScrapeJobListResponse(
        data=[_build_scrape_job_response(j) for j in jobs],
        total=len(jobs)
    )


@router.get("/scrape/jobs/{job_id}", response_model=RankingScrapeJobResponse)
async def get_scrape_job(
    job_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """獲取抓取任務詳情"""
    job = await db.get(RankingScrapeJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="任務不存在")

    return _build_scrape_job_response(job)


# =============================================
# SEO 報告 API
# =============================================

@router.post("/reports/generate", response_model=SEOReportResponse)
async def generate_seo_report(
    request: SEOReportGenerateRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    生成 SEO 優化報告

    - 分析排名趨勢
    - 生成 AI 優化建議
    - 與競品對比
    """
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=request.period_days)

    # 創建報告記錄
    report = SEOReport(
        product_id=request.product_id,
        report_type=ReportType(request.report_type.value),
        report_title=f"SEO 優化報告 - {start_date.strftime('%Y-%m-%d')} 至 {end_date.strftime('%Y-%m-%d')}",
        report_period_start=start_date,
        report_period_end=end_date,
        status="draft"
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)

    # TODO: 啟動報告生成任務
    # background_tasks.add_task(generate_report_content, report.id, request)

    return _build_report_response(report)


@router.get("/reports", response_model=SEOReportListResponse)
async def list_reports(
    product_id: Optional[UUID] = Query(None),
    report_type: Optional[ReportTypeEnum] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """列出 SEO 報告"""
    query = select(SEOReport)

    if product_id:
        query = query.where(SEOReport.product_id == product_id)
    if report_type:
        query = query.where(SEOReport.report_type == ReportType(report_type.value))

    query = query.order_by(desc(SEOReport.generated_at)).limit(limit)

    result = await db.execute(query)
    reports = result.scalars().all()

    return SEOReportListResponse(
        data=[_build_report_response(r) for r in reports],
        total=len(reports)
    )


@router.get("/reports/{report_id}", response_model=SEOReportResponse)
async def get_report(
    report_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """獲取報告詳情"""
    report = await db.get(SEOReport, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="報告不存在")

    return _build_report_response(report)


# =============================================
# 儀表板 API
# =============================================

@router.get("/dashboard", response_model=SEODashboardResponse)
async def get_dashboard(
    product_id: Optional[UUID] = Query(None),
    days: int = Query(7, ge=1, le=90),
    db: AsyncSession = Depends(get_db)
):
    """
    獲取 SEO 儀表板數據

    - 概覽指標
    - Google/HKTVmall 排名摘要
    - 排名趨勢圖表數據
    - 最近警報
    - 最近任務
    """
    # 1. 概覽指標
    config_query = select(KeywordConfig)
    if product_id:
        config_query = config_query.where(KeywordConfig.product_id == product_id)

    config_result = await db.execute(config_query)
    configs = config_result.scalars().all()

    total_keywords = len(configs)
    active_keywords = len([c for c in configs if c.is_active])
    keywords_with_data = len([c for c in configs if c.latest_google_rank or c.latest_hktvmall_rank])

    # 計算變化統計
    improved = len([c for c in configs if
                    c.baseline_google_rank and c.latest_google_rank and
                    c.latest_google_rank < c.baseline_google_rank])
    declined = len([c for c in configs if
                    c.baseline_google_rank and c.latest_google_rank and
                    c.latest_google_rank > c.baseline_google_rank])
    unchanged = keywords_with_data - improved - declined

    # 最後抓取時間
    last_job_query = select(RankingScrapeJob).where(
        RankingScrapeJob.status == "completed"
    ).order_by(desc(RankingScrapeJob.completed_at)).limit(1)
    last_job_result = await db.execute(last_job_query)
    last_job = last_job_result.scalar_one_or_none()
    last_scrape_at = last_job.completed_at if last_job else None

    overview = DashboardOverview(
        total_keywords=total_keywords,
        active_keywords=active_keywords,
        keywords_with_data=keywords_with_data,
        improved_keywords=improved,
        declined_keywords=declined,
        unchanged_keywords=unchanged,
        seo_health_score=_calculate_health_score(configs),
        last_scrape_at=last_scrape_at
    )

    # 2. Google 排名摘要
    google_rankings = _build_ranking_summary(configs, "google")

    # 3. HKTVmall 排名摘要
    hktvmall_rankings = _build_ranking_summary(configs, "hktvmall")

    # 4. 排名趨勢（最近 N 天）
    start_date = datetime.utcnow() - timedelta(days=days)
    ranking_trends = await _get_ranking_trends(db, product_id, start_date)

    # 5. 最近警報
    alert_query = select(RankingAlert).order_by(desc(RankingAlert.created_at)).limit(5)
    if product_id:
        alert_query = alert_query.where(RankingAlert.product_id == product_id)
    alert_result = await db.execute(alert_query)
    recent_alerts = [_build_alert_response(a) for a in alert_result.scalars().all()]

    # 6. 最近任務
    job_query = select(RankingScrapeJob).order_by(desc(RankingScrapeJob.created_at)).limit(5)
    job_result = await db.execute(job_query)
    recent_jobs = [_build_scrape_job_response(j) for j in job_result.scalars().all()]

    return SEODashboardResponse(
        overview=overview,
        google_rankings=google_rankings,
        hktvmall_rankings=hktvmall_rankings,
        ranking_trends=ranking_trends,
        recent_alerts=recent_alerts,
        recent_jobs=recent_jobs
    )


# =============================================
# 輔助函數
# =============================================

def _build_keyword_config_response(config: KeywordConfig) -> KeywordConfigResponse:
    """構建關鍵詞配置響應"""
    # 計算與基準的變化
    google_change = None
    if config.baseline_google_rank and config.latest_google_rank:
        google_change = config.baseline_google_rank - config.latest_google_rank

    hktvmall_change = None
    if config.baseline_hktvmall_rank and config.latest_hktvmall_rank:
        hktvmall_change = config.baseline_hktvmall_rank - config.latest_hktvmall_rank

    # 計算與目標的差距
    google_gap = None
    if config.target_google_rank and config.latest_google_rank:
        google_gap = config.latest_google_rank - config.target_google_rank

    hktvmall_gap = None
    if config.target_hktvmall_rank and config.latest_hktvmall_rank:
        hktvmall_gap = config.latest_hktvmall_rank - config.target_hktvmall_rank

    return KeywordConfigResponse(
        id=config.id,
        product_id=config.product_id,
        keyword=config.keyword,
        keyword_normalized=config.keyword_normalized,
        keyword_type=config.keyword_type.value,
        track_google=config.track_google,
        track_hktvmall=config.track_hktvmall,
        is_active=config.is_active,
        target_google_rank=config.target_google_rank,
        target_hktvmall_rank=config.target_hktvmall_rank,
        baseline_google_rank=config.baseline_google_rank,
        baseline_hktvmall_rank=config.baseline_hktvmall_rank,
        latest_google_rank=config.latest_google_rank,
        latest_hktvmall_rank=config.latest_hktvmall_rank,
        latest_tracked_at=config.latest_tracked_at,
        track_competitors=config.track_competitors,
        competitor_product_ids=[UUID(pid) for pid in (config.competitor_product_ids or [])],
        notes=config.notes,
        tags=config.tags or [],
        created_at=config.created_at,
        updated_at=config.updated_at,
        google_rank_change=google_change,
        hktvmall_rank_change=hktvmall_change,
        google_target_gap=google_gap,
        hktvmall_target_gap=hktvmall_gap
    )


def _build_ranking_response(ranking: KeywordRanking) -> KeywordRankingResponse:
    """構建排名記錄響應"""
    return KeywordRankingResponse(
        id=ranking.id,
        keyword_config_id=ranking.keyword_config_id,
        product_id=ranking.product_id,
        keyword=ranking.keyword,
        google_rank=ranking.google_rank,
        google_page=ranking.google_page,
        google_url=ranking.google_url,
        google_rank_change=ranking.google_rank_change,
        hktvmall_rank=ranking.hktvmall_rank,
        hktvmall_page=ranking.hktvmall_page,
        hktvmall_rank_change=ranking.hktvmall_rank_change,
        competitor_rankings=ranking.competitor_rankings,
        serp_features=ranking.serp_features,
        source=ranking.source.value if isinstance(ranking.source, RankingSource) else ranking.source,
        tracked_at=ranking.tracked_at,
        scrape_success=ranking.scrape_success
    )


def _build_alert_response(alert: RankingAlert) -> RankingAlertResponse:
    """構建警報響應"""
    return RankingAlertResponse(
        id=alert.id,
        keyword_config_id=alert.keyword_config_id,
        product_id=alert.product_id,
        alert_type=alert.alert_type,
        severity=alert.severity.value if isinstance(alert.severity, AlertSeverity) else alert.severity,
        keyword=alert.keyword,
        source=alert.source.value if isinstance(alert.source, RankingSource) else alert.source,
        previous_rank=alert.previous_rank,
        current_rank=alert.current_rank,
        rank_change=alert.rank_change,
        message=alert.message,
        details=alert.details,
        is_read=alert.is_read,
        is_resolved=alert.is_resolved,
        resolved_at=alert.resolved_at,
        created_at=alert.created_at
    )


def _build_scrape_job_response(job: RankingScrapeJob) -> RankingScrapeJobResponse:
    """構建抓取任務響應"""
    progress = 0
    if job.total_keywords > 0:
        progress = int((job.processed_keywords / job.total_keywords) * 100)

    success_rate = None
    if job.processed_keywords > 0:
        success_rate = round(job.successful_keywords / job.processed_keywords * 100, 1)

    return RankingScrapeJobResponse(
        id=job.id,
        job_type=job.job_type,
        status=job.status,
        total_keywords=job.total_keywords,
        processed_keywords=job.processed_keywords,
        successful_keywords=job.successful_keywords,
        failed_keywords=job.failed_keywords,
        started_at=job.started_at,
        completed_at=job.completed_at,
        duration_seconds=job.duration_seconds,
        errors=job.errors or [],
        triggered_by=job.triggered_by,
        created_at=job.created_at,
        progress_percent=progress,
        success_rate=success_rate
    )


def _build_report_response(report: SEOReport) -> SEOReportResponse:
    """構建報告響應"""
    return SEOReportResponse(
        id=report.id,
        product_id=report.product_id,
        report_type=report.report_type.value if isinstance(report.report_type, ReportType) else report.report_type,
        report_title=report.report_title,
        report_period_start=report.report_period_start,
        report_period_end=report.report_period_end,
        google_summary=report.google_summary,
        hktvmall_summary=report.hktvmall_summary,
        keyword_details=report.keyword_details,
        competitor_comparison=report.competitor_comparison,
        recommendations=report.recommendations,
        improvement_score=report.improvement_score,
        status=report.status,
        generated_at=report.generated_at
    )


def _calculate_ranking_summary(rankings: list) -> RankingHistorySummary:
    """計算排名歷史摘要"""
    if not rankings:
        return RankingHistorySummary(
            total_records=0,
            date_range={"start": None, "end": None}
        )

    google_ranks = [r.google_rank for r in rankings if r.google_rank]
    hktvmall_ranks = [r.hktvmall_rank for r in rankings if r.hktvmall_rank]

    return RankingHistorySummary(
        total_records=len(rankings),
        date_range={
            "start": min(r.tracked_at for r in rankings),
            "end": max(r.tracked_at for r in rankings)
        },
        google_avg_rank=round(sum(google_ranks) / len(google_ranks), 1) if google_ranks else None,
        google_best_rank=min(google_ranks) if google_ranks else None,
        google_worst_rank=max(google_ranks) if google_ranks else None,
        hktvmall_avg_rank=round(sum(hktvmall_ranks) / len(hktvmall_ranks), 1) if hktvmall_ranks else None,
        hktvmall_best_rank=min(hktvmall_ranks) if hktvmall_ranks else None,
        hktvmall_worst_rank=max(hktvmall_ranks) if hktvmall_ranks else None
    )


def _calculate_health_score(configs: list) -> int:
    """計算 SEO 健康分數"""
    if not configs:
        return 0

    score = 0
    max_score = 100

    # 有排名數據的比例（30分）
    with_data = len([c for c in configs if c.latest_google_rank or c.latest_hktvmall_rank])
    data_ratio = with_data / len(configs) if configs else 0
    score += int(data_ratio * 30)

    # Google Top 30 比例（35分）
    google_top_30 = len([c for c in configs if c.latest_google_rank and c.latest_google_rank <= 30])
    google_ratio = google_top_30 / len(configs) if configs else 0
    score += int(google_ratio * 35)

    # HKTVmall Top 30 比例（35分）
    hktv_top_30 = len([c for c in configs if c.latest_hktvmall_rank and c.latest_hktvmall_rank <= 30])
    hktv_ratio = hktv_top_30 / len(configs) if configs else 0
    score += int(hktv_ratio * 35)

    return min(score, max_score)


def _build_ranking_summary(configs: list, source: str) -> RankingSummaryBySource:
    """構建按來源的排名摘要"""
    if source == "google":
        ranks = [c.latest_google_rank for c in configs if c.latest_google_rank]
        source_name = "google_hk"
    else:
        ranks = [c.latest_hktvmall_rank for c in configs if c.latest_hktvmall_rank]
        source_name = "hktvmall"

    total = len(configs)
    ranked = len(ranks)
    top_10 = len([r for r in ranks if r <= 10])
    top_30 = len([r for r in ranks if r <= 30])
    avg = round(sum(ranks) / len(ranks), 1) if ranks else None

    best = None
    worst = None
    if ranks:
        min_rank = min(ranks)
        max_rank = max(ranks)
        best_config = next((c for c in configs if (
            c.latest_google_rank == min_rank if source == "google"
            else c.latest_hktvmall_rank == min_rank
        )), None)
        worst_config = next((c for c in configs if (
            c.latest_google_rank == max_rank if source == "google"
            else c.latest_hktvmall_rank == max_rank
        )), None)

        if best_config:
            best = {"keyword": best_config.keyword, "rank": min_rank}
        if worst_config:
            worst = {"keyword": worst_config.keyword, "rank": max_rank}

    return RankingSummaryBySource(
        source=source_name,
        total_keywords=total,
        ranked_keywords=ranked,
        avg_rank=avg,
        top_10_count=top_10,
        top_30_count=top_30,
        best_keyword=best,
        worst_keyword=worst
    )


async def _get_ranking_trends(
    db: AsyncSession,
    product_id: Optional[UUID],
    start_date: datetime
) -> List[RankingTrendPoint]:
    """獲取排名趨勢數據"""
    # TODO: 實現按日期聚合的排名趨勢查詢
    # 這裡返回空列表，實際實現需要查詢 keyword_rankings 表並按日期聚合
    return []
