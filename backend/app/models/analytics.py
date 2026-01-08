# =============================================
# 分析與報告模型
# =============================================

from datetime import datetime, date
from typing import Optional, List, Dict, Any
from uuid import UUID
import uuid
from decimal import Decimal

from sqlalchemy import Column, String, Integer, Boolean, Text, ForeignKey, Index, Date, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.models.database import Base


class PriceAnalytics(Base):
    """價格分析聚合數據"""

    __tablename__ = "price_analytics"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # 聚合維度
    competitor_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("competitors.id", ondelete="CASCADE"), nullable=True
    )
    category: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    date: Mapped[date] = mapped_column(Date, nullable=False)

    # 價格統計
    avg_price: Mapped[Optional[Decimal]] = mapped_column(nullable=True)
    min_price: Mapped[Optional[Decimal]] = mapped_column(nullable=True)
    max_price: Mapped[Optional[Decimal]] = mapped_column(nullable=True)
    median_price: Mapped[Optional[Decimal]] = mapped_column(nullable=True)
    price_std_dev: Mapped[Optional[Decimal]] = mapped_column(nullable=True)

    # 變動統計
    avg_price_change_percent: Mapped[Optional[Decimal]] = mapped_column(nullable=True)
    price_drops_count: Mapped[int] = mapped_column(Integer, default=0)
    price_increases_count: Mapped[int] = mapped_column(Integer, default=0)

    # 庫存統計
    in_stock_count: Mapped[int] = mapped_column(Integer, default=0)
    out_of_stock_count: Mapped[int] = mapped_column(Integer, default=0)
    low_stock_count: Mapped[int] = mapped_column(Integer, default=0)

    # 商品計數
    total_products: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # 關聯
    competitor = relationship("Competitor")

    __table_args__ = (
        UniqueConstraint("competitor_id", "category", "date", name="uq_price_analytics_dim"),
        Index("idx_price_analytics_date", "date"),
        Index("idx_price_analytics_competitor", "competitor_id", "date"),
        Index("idx_price_analytics_category", "category", "date"),
    )

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "id": str(self.id),
            "competitor_id": str(self.competitor_id) if self.competitor_id else None,
            "category": self.category,
            "date": self.date.isoformat() if self.date else None,
            "avg_price": float(self.avg_price) if self.avg_price else None,
            "min_price": float(self.min_price) if self.min_price else None,
            "max_price": float(self.max_price) if self.max_price else None,
            "median_price": float(self.median_price) if self.median_price else None,
            "price_std_dev": float(self.price_std_dev) if self.price_std_dev else None,
            "avg_price_change_percent": (
                float(self.avg_price_change_percent) if self.avg_price_change_percent else None
            ),
            "price_drops_count": self.price_drops_count,
            "price_increases_count": self.price_increases_count,
            "in_stock_count": self.in_stock_count,
            "out_of_stock_count": self.out_of_stock_count,
            "low_stock_count": self.low_stock_count,
            "total_products": self.total_products,
        }


class MarketReport(Base):
    """市場研究報告"""

    __tablename__ = "market_reports"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    report_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # price_comparison, trend_analysis, category_overview, competitor_analysis

    # 報告配置
    config: Mapped[Dict] = mapped_column(JSONB, nullable=False)

    # 報告數據
    data: Mapped[Optional[Dict]] = mapped_column(JSONB, nullable=True)

    # 生成狀態
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="pending"
    )  # pending, generating, completed, failed
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # 導出
    export_formats: Mapped[List] = mapped_column(JSONB, default=lambda: ["csv", "xlsx", "pdf"])
    file_urls: Mapped[Dict] = mapped_column(JSONB, default=dict)

    # 時間
    generated_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    __table_args__ = (
        Index("idx_market_reports_status", "status"),
        Index("idx_market_reports_type", "report_type"),
        Index("idx_market_reports_created_at", "created_at"),
    )

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "id": str(self.id),
            "name": self.name,
            "report_type": self.report_type,
            "config": self.config,
            "data": self.data,
            "status": self.status,
            "error_message": self.error_message,
            "export_formats": self.export_formats,
            "file_urls": self.file_urls,
            "generated_at": self.generated_at.isoformat() if self.generated_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
