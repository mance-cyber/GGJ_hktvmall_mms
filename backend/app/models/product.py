# =============================================
# 自家商品相關模型
# =============================================

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from sqlalchemy import String, Text, Boolean, ForeignKey, Numeric, Integer, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.database import Base, utcnow


class Product(Base):
    """自家商品 - GogoJap SKU 核心母體"""
    __tablename__ = "products"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sku: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    hktv_product_id: Mapped[Optional[str]] = mapped_column(String(100), comment="HKTVmall 商品 ID")
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    category: Mapped[Optional[str]] = mapped_column(String(255))
    brand: Mapped[Optional[str]] = mapped_column(String(255))
    price: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    cost: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), comment="成本價")
    
    # 定價保護欄位
    min_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), comment="最低售價 (保護價)")
    max_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), comment="最高售價")
    auto_pricing_enabled: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否啟用 AI 自動定價")

    # 監測優先級（分級監測策略）
    monitoring_priority: Mapped[str] = mapped_column(
        String(10),
        default="B",
        comment="監測優先級: A=核心商品(3次/天), B=一般商品(2次/天), C=低優先(1次/天)"
    )

    stock_quantity: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(50), default="active", comment="active, inactive, pending")
    images: Mapped[Optional[list]] = mapped_column(JSONB, default=[])
    attributes: Mapped[Optional[dict]] = mapped_column(JSONB, default={})
    hktv_data: Mapped[Optional[dict]] = mapped_column(JSONB, comment="HKTVmall MMS API 原始數據")
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow, onupdate=utcnow)

    # =============================================
    # Market Response Center (MRC) 擴展欄位
    # =============================================
    # 多語言商品名稱 (用於智能搜索匹配)
    name_zh: Mapped[Optional[str]] = mapped_column(String(500), comment="中文品名")
    name_ja: Mapped[Optional[str]] = mapped_column(String(500), comment="日文品名 - 核心搜索鍵")
    name_en: Mapped[Optional[str]] = mapped_column(String(500), comment="英文品名/規格")

    # 分類層級
    category_main: Mapped[Optional[str]] = mapped_column(String(100), comment="大分類: 飛機貨、乾貨、急凍...")
    category_sub: Mapped[Optional[str]] = mapped_column(String(100), comment="小分類: 鮮魚、貝類、蝦蟹...")

    # 商品屬性
    unit: Mapped[Optional[str]] = mapped_column(String(50), comment="單位: KG, PK, PC, BTL...")
    season_tag: Mapped[Optional[str]] = mapped_column(String(100), comment="季節標籤: ALL, WINTER, SPRING-SUMMER...")

    # 數據來源追蹤
    source: Mapped[Optional[str]] = mapped_column(String(50), default="manual", comment="數據來源: gogojap_csv, hktv_api, manual")

    # 競品建庫重設計：自家商品標籤
    category_tag: Mapped[Optional[str]] = mapped_column(String(50), comment="大類標籤：牛/豬/羊/雞鴨/魚/蝦/蟹/貝")
    sub_tag: Mapped[Optional[str]] = mapped_column(String(50), comment="細分標籤：西冷/肉眼/牛柳/牛仔骨/三文魚/刺身...")

    # 關聯
    history: Mapped[List["ProductHistory"]] = relationship(back_populates="product", cascade="all, delete-orphan")
    competitor_mappings: Mapped[List["ProductCompetitorMapping"]] = relationship(back_populates="product", cascade="all, delete-orphan")
    ai_contents: Mapped[List["AIContent"]] = relationship(back_populates="product")
    price_proposals: Mapped[List["PriceProposal"]] = relationship(back_populates="product")
    price_snapshots: Mapped[List["OwnPriceSnapshot"]] = relationship(back_populates="product", cascade="all, delete-orphan")
    # SEO & GEO 關聯
    seo_contents: Mapped[List["SEOContent"]] = relationship(back_populates="product")
    structured_data: Mapped[List["StructuredData"]] = relationship(back_populates="product")

    __table_args__ = (
        Index("idx_products_sku", "sku"),
        Index("idx_products_hktv_id", "hktv_product_id"),
        Index("idx_products_status", "status"),
        # MRC 搜索優化索引
        Index("idx_products_name_ja", "name_ja"),
        Index("idx_products_season_tag", "season_tag"),
        Index("idx_products_category_main", "category_main"),
        Index("idx_products_source", "source"),
        Index("idx_products_category_tag", "category_tag"),
    )


class ProductHistory(Base):
    """商品修改歷史"""
    __tablename__ = "product_history"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"))
    field_changed: Mapped[str] = mapped_column(String(100), nullable=False)
    old_value: Mapped[Optional[str]] = mapped_column(Text)
    new_value: Mapped[Optional[str]] = mapped_column(Text)
    changed_at: Mapped[datetime] = mapped_column(default=utcnow)

    # 關聯
    product: Mapped["Product"] = relationship(back_populates="history")


class ProductCompetitorMapping(Base):
    """自家商品與競品的對應關係"""
    __tablename__ = "product_competitor_mapping"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"))
    competitor_product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("competitor_products.id", ondelete="CASCADE"))
    match_confidence: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2), comment="0.00 - 1.00 匹配信心度")
    match_level: Mapped[Optional[int]] = mapped_column(Integer, comment="匹配層級：1=直接替代 2=近似競品 3=品類競品")
    match_reason: Mapped[Optional[str]] = mapped_column(Text, comment="AI 匹配理由")
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, comment="人工確認")
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)

    # 關聯
    product: Mapped["Product"] = relationship(back_populates="competitor_mappings")
    competitor_product: Mapped["CompetitorProduct"] = relationship()

    __table_args__ = (
        UniqueConstraint("product_id", "competitor_product_id", name="uq_product_competitor"),
        Index("idx_pcm_match_level", "match_level"),
    )


class OwnPriceSnapshot(Base):
    """
    自家產品價格歷史快照

    用於追蹤自家產品的價格變化趨勢，與 PriceSnapshot（競品）對應。
    Mock 數據使用 MOCK- 前綴的 product_id 關聯，可通過 cleanup 腳本清除。
    """
    __tablename__ = "own_price_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"))
    price: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    original_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), comment="原價（劃線價）")
    discount_percent: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    stock_status: Mapped[Optional[str]] = mapped_column(String(50), comment="in_stock, out_of_stock, low_stock")
    promotion_text: Mapped[Optional[str]] = mapped_column(Text)
    recorded_at: Mapped[datetime] = mapped_column(default=utcnow)

    # 關聯
    product: Mapped["Product"] = relationship(back_populates="price_snapshots")

    __table_args__ = (
        Index("idx_own_price_snapshots_product_id", "product_id"),
        Index("idx_own_price_snapshots_recorded_at", "recorded_at"),
    )


# 避免循環導入
from app.models.content import AIContent
from app.models.seo import SEOContent, StructuredData
# from app.models.pricing import PriceProposal  # 注意: 這裡不能循環導入，只能使用字串引用 "PriceProposal"
