# =============================================
# 競品監測相關模型
# =============================================

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from sqlalchemy import String, Text, Boolean, ForeignKey, Numeric, Integer, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.database import Base, utcnow


class Competitor(Base):
    """競爭對手/店舖"""
    __tablename__ = "competitors"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    platform: Mapped[str] = mapped_column(String(100), nullable=False, comment="平台：hktvmall, watsons, mannings 等")
    base_url: Mapped[Optional[str]] = mapped_column(String(500))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # v2 新增：商戶分級 + Algolia 店鋪代碼
    tier: Mapped[int] = mapped_column(Integer, default=2, comment="1=直接對手, 2=品類重疊, 3=參考")
    store_code: Mapped[Optional[str]] = mapped_column(String(50), comment="HKTVmall 店鋪代碼（Algolia storeCode）")

    category_patterns: Mapped[Optional[list]] = mapped_column(JSONB, default=list)

    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow, onupdate=utcnow)

    # 關聯
    products: Mapped[List["CompetitorProduct"]] = relationship(back_populates="competitor", cascade="all, delete-orphan")
    import_jobs: Mapped[List["ImportJob"]] = relationship(back_populates="competitor")


class CompetitorProduct(Base):
    """競品商品監測列表"""
    __tablename__ = "competitor_products"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    competitor_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("competitors.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    url: Mapped[str] = mapped_column(String(2000), nullable=False, unique=True)
    sku: Mapped[Optional[str]] = mapped_column(String(100))
    category: Mapped[Optional[str]] = mapped_column(String(255))
    image_url: Mapped[Optional[str]] = mapped_column(String(1000))

    # 新增欄位
    brand: Mapped[Optional[str]] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text)
    specs: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict, comment="商品規格")
    images: Mapped[Optional[list]] = mapped_column(JSONB, default=list, comment="多張商品圖片")

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_scraped_at: Mapped[Optional[datetime]] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow, onupdate=utcnow)

    # v2：商品分類（AI 判斷）
    product_type: Mapped[Optional[str]] = mapped_column(String(20), default='unknown', comment="fresh/frozen/processed/unknown")
    # category 欄位保留，重新用途：牛/豬/魚/蝦/蟹/貝/蠔/其他
    unit_weight_g: Mapped[Optional[int]] = mapped_column(Integer, comment="重量（克），用於計算每100g單價")
    last_seen_at: Mapped[Optional[datetime]] = mapped_column(comment="最後一次在 Algolia 出現的時間")

    # 關聯
    competitor: Mapped["Competitor"] = relationship(back_populates="products")
    price_snapshots: Mapped[List["PriceSnapshot"]] = relationship(back_populates="product", cascade="all, delete-orphan")
    alerts: Mapped[List["PriceAlert"]] = relationship(back_populates="product", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_competitor_products_competitor_id", "competitor_id"),
        Index("idx_competitor_products_url", "url"),
        Index("idx_competitor_products_is_active", "is_active"),
        Index("idx_cp_product_type", "product_type"),
        Index("idx_cp_category", "category"),
        Index("idx_cp_last_seen_at", "last_seen_at"),
    )


class PriceSnapshot(Base):
    """價格歷史快照"""
    __tablename__ = "price_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    competitor_product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("competitor_products.id", ondelete="CASCADE"))
    price: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    original_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), comment="原價（劃線價）")
    discount_percent: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    currency: Mapped[str] = mapped_column(String(10), default="HKD")
    stock_status: Mapped[Optional[str]] = mapped_column(String(50), comment="in_stock, out_of_stock, low_stock, preorder")
    rating: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2))
    review_count: Mapped[Optional[int]] = mapped_column(Integer)
    promotion_text: Mapped[Optional[str]] = mapped_column(Text)
    raw_data: Mapped[Optional[dict]] = mapped_column(JSONB, comment="Firecrawl 返回的完整數據")
    scraped_at: Mapped[datetime] = mapped_column(default=utcnow)

    # 新增欄位
    brand: Mapped[Optional[str]] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text)
    specs: Mapped[Optional[dict]] = mapped_column(JSONB)
    images: Mapped[Optional[list]] = mapped_column(JSONB)

    # v2 新增：每 100g 單位價（方便比較）
    unit_price_per_100g: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), comment="每 100g 價格（HKD）")

    # 關聯
    product: Mapped["CompetitorProduct"] = relationship(back_populates="price_snapshots")

    __table_args__ = (
        Index("idx_price_snapshots_product_id", "competitor_product_id"),
        Index("idx_price_snapshots_scraped_at", "scraped_at"),
    )


class PriceAlert(Base):
    """價格/庫存變動警報"""
    __tablename__ = "price_alerts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    competitor_product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("competitor_products.id", ondelete="CASCADE"))
    alert_type: Mapped[str] = mapped_column(String(50), nullable=False, comment="price_drop, price_increase, out_of_stock, back_in_stock")
    old_value: Mapped[Optional[str]] = mapped_column(String(100))
    new_value: Mapped[Optional[str]] = mapped_column(String(100))
    change_percent: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    is_notified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)

    # 關聯
    product: Mapped["CompetitorProduct"] = relationship(back_populates="alerts")

    __table_args__ = (
        Index("idx_price_alerts_product_id", "competitor_product_id"),
        Index("idx_price_alerts_created_at", "created_at"),
        Index("idx_price_alerts_type", "alert_type"),
    )
