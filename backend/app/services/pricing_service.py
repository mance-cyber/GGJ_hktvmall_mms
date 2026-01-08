# =============================================
# 智能定價服務
# =============================================

from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from uuid import UUID
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, desc

from app.models.pricing import PriceProposal, ProposalStatus, AuditLog, ProposalType
from app.models.product import Product, ProductCompetitorMapping
from app.models.competitor import CompetitorProduct
from app.services.hktvmall import HKTVMallClient, HKTVMallMockClient
from app.config import settings

logger = logging.getLogger(__name__)

class PricingService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_proposal(self, 
                            product_id: UUID, 
                            proposed_price: Decimal, 
                            reason: str, 
                            model: str = "manual") -> PriceProposal:
        """創建一個新的改價提案"""
        # 1. Get current product info
        product = await self.db.get(Product, product_id)
        if not product:
            raise ValueError(f"Product {product_id} not found")
            
        current_price = product.price
        
        # 2. Create proposal
        proposal = PriceProposal(
            product_id=product_id,
            proposal_type=ProposalType.PRICE_UPDATE,
            status=ProposalStatus.PENDING,
            current_price=current_price,
            proposed_price=proposed_price,
            reason=reason,
            ai_model_used=model
        )
        
        self.db.add(proposal)
        
        # 3. Log it
        log = AuditLog(
            action="CREATE_PROPOSAL",
            entity_type="proposal",
            entity_id=str(product_id),
            details={
                "sku": product.sku,
                "current": float(current_price) if current_price else 0,
                "proposed": float(proposed_price),
                "reason": reason
            }
        )
        self.db.add(log)
        
        await self.db.commit()
        await self.db.refresh(proposal)
        return proposal

    async def get_pending_proposals(self) -> List[PriceProposal]:
        """獲取所有待審批的提案"""
        query = select(PriceProposal).where(
            PriceProposal.status == ProposalStatus.PENDING
        ).order_by(desc(PriceProposal.created_at))
        
        result = await self.db.execute(query)
        return result.scalars().all()

    async def approve_proposal(self, proposal_id: UUID, user_id: str = "admin") -> PriceProposal:
        """批准提案 -> 執行改價"""
        proposal = await self.db.get(PriceProposal, proposal_id)
        if not proposal:
            raise ValueError("Proposal not found")
            
        if proposal.status != ProposalStatus.PENDING:
            raise ValueError(f"Proposal is {proposal.status}, cannot approve")
            
        # 1. Update Proposal Status
        proposal.status = ProposalStatus.APPROVED
        proposal.reviewed_at = datetime.utcnow()
        proposal.reviewed_by = user_id
        proposal.final_price = proposal.proposed_price # Default to proposed
        
        # 2. Execute Price Update (Call HKTVmall API here)
        try:
            # Execute
            await self._execute_hktv_update(proposal.product_id, proposal.final_price)
            
            proposal.status = ProposalStatus.EXECUTED
            proposal.executed_at = datetime.utcnow()
            
            # Update Local Product Price
            await self.db.execute(
                update(Product)
                .where(Product.id == proposal.product_id)
                .values(price=proposal.final_price)
            )
            
            # Log
            self.db.add(AuditLog(
                action="EXECUTE_PRICE_UPDATE",
                entity_type="product",
                entity_id=str(proposal.product_id),
                user_id=user_id,
                details={
                    "proposal_id": str(proposal.id),
                    "new_price": float(proposal.final_price)
                }
            ))
            
        except Exception as e:
            logger.error(f"Failed to execute price update: {e}")
            proposal.status = ProposalStatus.FAILED
            proposal.error_message = str(e)
            
        await self.db.commit()
        await self.db.refresh(proposal)
        return proposal

    async def reject_proposal(self, proposal_id: UUID, user_id: str = "admin") -> PriceProposal:
        """拒絕提案"""
        proposal = await self.db.get(PriceProposal, proposal_id)
        if not proposal:
            raise ValueError("Proposal not found")
            
        proposal.status = ProposalStatus.REJECTED
        proposal.reviewed_at = datetime.utcnow()
        proposal.reviewed_by = user_id
        
        self.db.add(AuditLog(
            action="REJECT_PROPOSAL",
            entity_type="proposal",
            entity_id=str(proposal.id),
            user_id=user_id
        ))
        
        await self.db.commit()
        return proposal

    async def generate_proposals(self) -> int:
        """AI 策略引擎：掃描市場並生成建議"""
        # 1. Find enabled products
        stmt = select(Product).where(Product.auto_pricing_enabled == True)
        result = await self.db.execute(stmt)
        products = result.scalars().all()
        
        generated_count = 0
        
        for product in products:
            # Skip if pending proposal exists
            existing = await self.db.execute(
                select(PriceProposal).where(
                    PriceProposal.product_id == product.id,
                    PriceProposal.status == ProposalStatus.PENDING
                )
            )
            if existing.scalar_one_or_none():
                continue
                
            # 2. Get competitors
            mappings_stmt = (
                select(CompetitorProduct)
                .join(ProductCompetitorMapping, ProductCompetitorMapping.competitor_product_id == CompetitorProduct.id)
                .where(ProductCompetitorMapping.product_id == product.id)
            )
            mappings_result = await self.db.execute(mappings_stmt)
            competitors = mappings_result.scalars().all()
            
            if not competitors:
                continue
                
            # Find lowest price competitor
            min_comp_price = None
            target_comp = None
            
            for comp in competitors:
                if comp.price and (min_comp_price is None or comp.price < min_comp_price):
                    min_comp_price = comp.price
                    target_comp = comp
            
            if not min_comp_price or not product.price:
                continue
                
            # Strategy: Undercut by $1 if possible
            if min_comp_price < product.price:
                suggested_price = min_comp_price - Decimal('1.0')
                
                # Safety Checks
                # Floor is max(min_price, cost * 1.05)
                # If min_price is None, use cost logic
                # If cost is None, default to 0 (dangerous, but handled by logic below)
                
                cost_floor = (product.cost or Decimal('0')) * Decimal('1.05')
                hard_floor = product.min_price or Decimal('0')
                
                final_floor = max(cost_floor, hard_floor)
                
                # If floor is 0 (no config), we skip to avoid selling at $1
                if final_floor == 0:
                    # Log warning or skip
                    continue
                
                if suggested_price >= final_floor:
                    await self.create_proposal(
                        product_id=product.id,
                        proposed_price=suggested_price,
                        reason=f"競爭對手 {target_comp.name} 降價至 ${min_comp_price}，建議跟進 (已扣除安全利潤)",
                        model="rule_based_v1"
                    )
                    generated_count += 1
                    
        return generated_count

    async def _execute_hktv_update(self, product_id: UUID, price: Decimal):
        """(Private) Call HKTVmall API"""
        product = await self.db.get(Product, product_id)
        if not product:
            raise ValueError(f"Product {product_id} not found")
            
        sku = product.sku
        if not sku:
            raise ValueError(f"Product {product_id} has no SKU")
            
        # Decide which client to use
        # Use Mock if no token or in dev mode (optional, but sticking to token check for now)
        if settings.hktv_access_token and settings.hktv_access_token != "mock_token":
            logger.info(f"Using Real HKTVmall API for {sku}")
            client = HKTVMallClient()
        else:
            logger.info(f"Using Mock HKTVmall API for {sku}")
            client = HKTVMallMockClient()
            
        # Call API
        try:
            result = await client.update_price(sku_code=sku, price=float(price))
            logger.info(f"HKTVmall Update Result: {result}")
            return True
        except Exception as e:
            logger.error(f"HKTVmall API Failed: {e}")
            raise e
