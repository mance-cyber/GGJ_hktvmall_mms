# =============================================
# 價格警報 API
# =============================================

from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.models.database import get_db
from app.models.competitor import PriceAlert, CompetitorProduct, Competitor
from app.schemas.competitor import PriceAlertResponse, PriceAlertListResponse

router = APIRouter()


class MarkReadRequest(BaseModel):
    """批量標記已讀請求"""
    ids: List[UUID]


class UnreadCountResponse(BaseModel):
    """未讀數量響應"""
    count: int


@router.get("", response_model=PriceAlertListResponse)
async def list_alerts(
    db: AsyncSession = Depends(get_db),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    alert_type: Optional[str] = None,
    is_read: Optional[bool] = None,
):
    """獲取警報列表"""
    query = select(PriceAlert)

    if alert_type:
        query = query.where(PriceAlert.alert_type == alert_type)
    if is_read is not None:
        query = query.where(PriceAlert.is_read == is_read)

    # 分頁
    query = query.order_by(PriceAlert.created_at.desc())
    query = query.offset((page - 1) * limit).limit(limit)

    result = await db.execute(query)
    alerts = result.scalars().all()

    # 獲取未讀數量
    unread_query = select(func.count(PriceAlert.id)).where(PriceAlert.is_read == False)
    unread_result = await db.execute(unread_query)
    unread_count = unread_result.scalar() or 0

    # 構建響應
    data = []
    for alert in alerts:
        # 獲取商品和競爭對手名稱
        product_query = select(
            CompetitorProduct.name,
            Competitor.name.label("competitor_name")
        ).join(
            Competitor, CompetitorProduct.competitor_id == Competitor.id
        ).where(
            CompetitorProduct.id == alert.competitor_product_id
        )
        product_result = await db.execute(product_query)
        product_row = product_result.first()

        data.append(PriceAlertResponse(
            id=alert.id,
            product_name=product_row[0] if product_row else "未知商品",
            competitor_name=product_row[1] if product_row else "未知競爭對手",
            alert_type=alert.alert_type,
            old_value=alert.old_value,
            new_value=alert.new_value,
            change_percent=alert.change_percent,
            is_read=alert.is_read,
            created_at=alert.created_at,
        ))

    return PriceAlertListResponse(data=data, unread_count=unread_count)


@router.get("/unread-count", response_model=UnreadCountResponse)
async def get_unread_count(
    db: AsyncSession = Depends(get_db),
):
    """獲取未讀警報數量"""
    query = select(func.count(PriceAlert.id)).where(PriceAlert.is_read == False)
    result = await db.execute(query)
    count = result.scalar() or 0

    return UnreadCountResponse(count=count)


@router.get("/{alert_id}", response_model=PriceAlertResponse)
async def get_alert(
    alert_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """獲取單個警報"""
    result = await db.execute(
        select(PriceAlert).where(PriceAlert.id == alert_id)
    )
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="警報不存在")

    # 獲取商品和競爭對手名稱
    product_query = select(
        CompetitorProduct.name,
        Competitor.name.label("competitor_name")
    ).join(
        Competitor, CompetitorProduct.competitor_id == Competitor.id
    ).where(
        CompetitorProduct.id == alert.competitor_product_id
    )
    product_result = await db.execute(product_query)
    product_row = product_result.first()

    return PriceAlertResponse(
        id=alert.id,
        product_name=product_row[0] if product_row else "未知商品",
        competitor_name=product_row[1] if product_row else "未知競爭對手",
        alert_type=alert.alert_type,
        old_value=alert.old_value,
        new_value=alert.new_value,
        change_percent=alert.change_percent,
        is_read=alert.is_read,
        created_at=alert.created_at,
    )


@router.patch("/{alert_id}/read")
async def mark_alert_read(
    alert_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """標記警報為已讀"""
    result = await db.execute(
        select(PriceAlert).where(PriceAlert.id == alert_id)
    )
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="警報不存在")

    alert.is_read = True
    await db.flush()

    return {"message": "已標記為已讀"}


@router.patch("/batch-read")
async def batch_mark_read(
    request: MarkReadRequest,
    db: AsyncSession = Depends(get_db),
):
    """批量標記為已讀"""
    stmt = (
        update(PriceAlert)
        .where(PriceAlert.id.in_(request.ids))
        .values(is_read=True)
    )
    result = await db.execute(stmt)

    return {"updated": result.rowcount}


@router.patch("/mark-all-read")
async def mark_all_read(
    db: AsyncSession = Depends(get_db),
):
    """標記所有為已讀"""
    stmt = (
        update(PriceAlert)
        .where(PriceAlert.is_read == False)
        .values(is_read=True)
    )
    result = await db.execute(stmt)

    return {"updated": result.rowcount}
