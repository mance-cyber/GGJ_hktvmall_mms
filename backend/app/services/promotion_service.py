from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Optional
from datetime import datetime, timedelta
from decimal import Decimal
import random

from app.models.promotion import PromotionProposal
from app.models.product import Product
from app.schemas.promotion import PromotionStats

class PromotionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_proposals(self, status: str = "pending") -> List[PromotionProposal]:
        """獲取推廣建議列表"""
        query = select(PromotionProposal).where(
            PromotionProposal.status == status
        ).order_by(desc(PromotionProposal.created_at))
        
        # Eager load product to get name/sku
        # In async sqlalchemy we usually use selectinload, but for now we'll do manual join or lazy load if session open
        # Let's try to just fetch and rely on lazy load if session is active, or use join
        from sqlalchemy.orm import selectinload
        query = query.options(selectinload(PromotionProposal.product))
        
        result = await self.db.execute(query)
        return result.scalars().all()

    async def generate_suggestions(self) -> int:
        """AI 分析並生成推廣建議"""
        # 1. 獲取可售產品
        query = select(Product).where(Product.status == "Active").limit(50)
        result = await self.db.execute(query)
        products = result.scalars().all()
        
        count = 0
        for product in products:
            # 檢查是否已有 pending 建議，避免重複
            existing = await self.db.execute(
                select(PromotionProposal).where(
                    PromotionProposal.product_id == product.id,
                    PromotionProposal.status == "pending"
                )
            )
            if existing.scalars().first():
                continue

            # 2. 簡單的財務分析 (Mock Logic)
            # 假設：如果沒有設定成本，默認成本為售價的 60%
            price = product.price or Decimal(0)
            if price <= 0: continue
            
            cost = product.cost
            if not cost:
                cost = price * Decimal("0.6")
            
            # 估算當前毛利
            margin = (price - cost) / price
            
            # 3. 決策邏輯
            discount_suggestion = Decimal(0)
            reason = ""
            
            if margin > Decimal("0.5"): # 高利潤 (>50%)
                discount_suggestion = Decimal("15.0")
                reason = "高利潤商品，建議 85 折激發銷量，預計可顯著提升轉化率"
            elif margin > Decimal("0.3"): # 中利潤 (>30%)
                discount_suggestion = Decimal("5.0")
                reason = "利潤空間健康，建議 95 折作為會員回饋或限時優惠"
            else:
                continue # 利潤太低不建議打折
                
            # 4. 計算預期結果
            discounted_price = price * (Decimal("1") - (discount_suggestion / Decimal("100")))
            # 假設 HKTVmall 佣金 15% + 運費 $30
            commission = discounted_price * Decimal("0.15")
            shipping = Decimal("30.0")
            
            projected_profit = discounted_price - cost - commission - shipping
            
            if projected_profit <= 0:
                continue # 打折後會虧本，跳過
            
            projected_margin = (projected_profit / discounted_price) * 100
            
            # 5. 創建建議
            proposal = PromotionProposal(
                product_id=product.id,
                promotion_type="discount_single",
                original_price=price,
                discount_percent=discount_suggestion,
                discounted_price=discounted_price,
                projected_profit=projected_profit,
                projected_margin=projected_margin,
                start_date=datetime.now() + timedelta(days=1),
                end_date=datetime.now() + timedelta(days=7),
                reason=reason,
                marketing_copy=f"【限時優惠】{product.name} 激減 {discount_suggestion}%！立即搶購！",
                status="pending"
            )
            self.db.add(proposal)
            count += 1
            
        await self.db.commit()
        return count

    async def approve_proposal(self, id: str):
        """批准建議 (將狀態改為 active)"""
        # 未來這裡會調用 HKTVmall API 真正設置優惠
        proposal = await self.db.get(PromotionProposal, id)
        if proposal:
            proposal.status = "active"
            await self.db.commit()
            return proposal
        raise ValueError("Proposal not found")
        
    async def reject_proposal(self, id: str):
        proposal = await self.db.get(PromotionProposal, id)
        if proposal:
            proposal.status = "rejected"
            await self.db.commit()
            return proposal
        raise ValueError("Proposal not found")

    async def get_stats(self) -> PromotionStats:
        # Mock stats
        return PromotionStats(
            active_count=await self._count_by_status("active"),
            pending_count=await self._count_by_status("pending"),
            avg_discount=12.5
        )
        
    async def _count_by_status(self, status: str) -> int:
        query = select(PromotionProposal).where(PromotionProposal.status == status)
        result = await self.db.execute(query)
        return len(result.scalars().all())
