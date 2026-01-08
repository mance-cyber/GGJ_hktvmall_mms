from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import get_db
from app.services.pricing_service import PricingService
from app.schemas.pricing import PriceProposalResponse, ProductPricingConfig
from app.models.product import Product
from sqlalchemy import update

router = APIRouter()

@router.get("/proposals/pending", response_model=List[PriceProposalResponse])
async def get_pending_proposals(db: AsyncSession = Depends(get_db)):
    service = PricingService(db)
    proposals = await service.get_pending_proposals()
    
    # Enrich with product info (Should be done via join in service, but this works for MVP)
    # Actually, SQLAlchemy relationship lazy loading might fail in async if not eager loaded
    # But let's assume simple attribute access works if session is open or we fix service query
    
    # Better approach: Fix service to Eager Load product
    from sqlalchemy.orm import selectinload
    from app.models.pricing import PriceProposal, ProposalStatus
    from sqlalchemy import select, desc
    
    # Re-implementing query here to ensure eager load (or move to service)
    query = select(PriceProposal).options(
        selectinload(PriceProposal.product)
    ).where(
        PriceProposal.status == ProposalStatus.PENDING
    ).order_by(desc(PriceProposal.created_at))
    
    result = await db.execute(query)
    items = result.scalars().all()
    
    responses = []
    for p in items:
        resp = PriceProposalResponse.model_validate(p)
        if p.product:
            resp.product_name = p.product.name
            resp.product_sku = p.product.sku
        responses.append(resp)
        
    return responses

@router.post("/proposals/{id}/approve")
async def approve_proposal(id: UUID, db: AsyncSession = Depends(get_db)):
    service = PricingService(db)
    try:
        return await service.approve_proposal(id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/proposals/{id}/reject")
async def reject_proposal(id: UUID, db: AsyncSession = Depends(get_db)):
    service = PricingService(db)
    try:
        return await service.reject_proposal(id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/products/{id}/config")
async def update_product_pricing_config(
    id: UUID, 
    config: ProductPricingConfig,
    db: AsyncSession = Depends(get_db)
):
    """更新產品的定價設定 (成本, 底價)"""
    # Verify product exists
    product = await db.get(Product, id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
        
    # Update fields
    values = config.model_dump(exclude_unset=True)
    await db.execute(
        update(Product)
        .where(Product.id == id)
        .values(**values)
    )
    await db.commit()
    return {"status": "success"}

@router.post("/analyze")
async def analyze_prices(db: AsyncSession = Depends(get_db)):
    """手動觸發 AI 價格分析"""
    service = PricingService(db)
    count = await service.generate_proposals()
    return {"status": "success", "generated_proposals": count}
