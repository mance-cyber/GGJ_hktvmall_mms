# =============================================
# 類別數據庫模型
# =============================================

from sqlalchemy import Column, String, Integer, Numeric, Boolean, Text, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.models.database import Base


class CategoryDatabase(Base):
    """類別數據庫"""
    __tablename__ = "category_databases"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)                    # 如：「和牛類」
    description = Column(Text)                                     # 類別描述
    hktv_category_url = Column(Text)                              # HKTVmall 類別頁面 URL

    total_products = Column(Integer, default=0)                   # 類別內商品總數
    last_scraped_at = Column(DateTime)                            # 最後抓取時間
    scrape_frequency = Column(String(50))                         # 抓取頻率
    is_active = Column(Boolean, default=True)                     # 是否啟用

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 關聯
    products = relationship("CategoryProduct", back_populates="category", cascade="all, delete-orphan")
    reports = relationship("CategoryAnalysisReport", back_populates="category", cascade="all, delete-orphan")


class CategoryProduct(Base):
    """類別內的商品"""
    __tablename__ = "category_products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_id = Column(UUID(as_uuid=True), ForeignKey("category_databases.id"), nullable=False)

    # 基本資訊
    name = Column(String(500), nullable=False)
    url = Column(Text, nullable=False)
    sku = Column(String(255))
    brand = Column(String(255))

    # 價格資訊
    price = Column(Numeric(10, 2))
    original_price = Column(Numeric(10, 2))
    discount_percent = Column(Numeric(5, 2))

    # 商品屬性（JSON 格式）
    attributes = Column(JSONB)                                    # {
                                                                  #   "origin": "日本",
                                                                  #   "grade": "A5",
                                                                  #   "weight": 500,
                                                                  #   "weight_unit": "g",
                                                                  #   "cut": "西冷"
                                                                  # }

    # 標準化單價（用於對比）
    unit_price = Column(Numeric(10, 2))                          # 每 100g 價格
    unit_type = Column(String(50), default="per_100g")           # 單位類型

    # 狀態
    stock_status = Column(String(50))
    is_available = Column(Boolean, default=True)

    # 評價
    rating = Column(Numeric(3, 2))
    review_count = Column(Integer)

    # 圖片
    image_url = Column(Text)

    # =============================================
    # 監控優化字段（新增）
    # =============================================
    monitor_priority = Column(String(20), default="normal")      # high, normal, low
    update_frequency_hours = Column(Integer, default=168)        # 更新頻率（小時），默認 7 天
    last_price_change_at = Column(DateTime)                      # 最後價格變動時間
    price_volatility = Column(Numeric(5, 2))                     # 價格波動率（%）
    scrape_error_count = Column(Integer, default=0)              # 連續抓取錯誤次數
    is_monitored = Column(Boolean, default=True)                 # 是否納入監控

    # 時間戳
    first_seen_at = Column(DateTime, default=datetime.utcnow)
    last_updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 關聯
    category = relationship("CategoryDatabase", back_populates="products")
    price_snapshots = relationship("CategoryPriceSnapshot", back_populates="product", cascade="all, delete-orphan")


class CategoryPriceSnapshot(Base):
    """類別商品價格快照"""
    __tablename__ = "category_price_snapshots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_product_id = Column(UUID(as_uuid=True), ForeignKey("category_products.id"), nullable=False)

    price = Column(Numeric(10, 2))
    original_price = Column(Numeric(10, 2))
    discount_percent = Column(Numeric(5, 2))
    unit_price = Column(Numeric(10, 2))                          # 標準化單價

    stock_status = Column(String(50))
    is_available = Column(Boolean)

    scraped_at = Column(DateTime, default=datetime.utcnow)

    # 關聯
    product = relationship("CategoryProduct", back_populates="price_snapshots")


class CategoryAnalysisReport(Base):
    """AI 分析報告"""
    __tablename__ = "category_analysis_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_id = Column(UUID(as_uuid=True), ForeignKey("category_databases.id"), nullable=False)

    report_type = Column(String(50))                             # price_analysis, competition, trend
    report_title = Column(String(255))

    # AI 生成的分析內容
    summary = Column(Text)                                        # 摘要
    key_findings = Column(JSONB)                                 # 關鍵發現（JSON 格式）
    recommendations = Column(JSONB)                              # 建議（JSON 格式）

    # 數據快照（分析時的原始數據）
    data_snapshot = Column(JSONB)

    # 元數據
    generated_by = Column(String(50))                            # AI 模型名稱
    generated_at = Column(DateTime, default=datetime.utcnow)

    created_at = Column(DateTime, default=datetime.utcnow)

    # 關聯
    category = relationship("CategoryDatabase", back_populates="reports")


class CategoryUrlCache(Base):
    """
    類別 URL 緩存

    用途：緩存已發現的商品 URL，避免重複調用 Firecrawl Map API
    節省：每次類別抓取可節省 3-6 credits
    """
    __tablename__ = "category_url_cache"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_id = Column(UUID(as_uuid=True), ForeignKey("category_databases.id"), nullable=False)

    # URL 資訊
    url = Column(Text, nullable=False)
    url_hash = Column(String(64), nullable=False, index=True)    # URL 的 SHA256 hash，用於快速查詢

    # 發現元數據
    discovered_at = Column(DateTime, default=datetime.utcnow)
    last_verified_at = Column(DateTime)                          # 最後驗證 URL 有效時間
    is_valid = Column(Boolean, default=True)                     # URL 是否仍然有效
    verification_error = Column(Text)                            # 驗證失敗的錯誤信息

    # 關聯的商品（如果已抓取）
    product_id = Column(UUID(as_uuid=True), ForeignKey("category_products.id"))

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ScrapeQuotaUsage(Base):
    """
    抓取配額使用記錄

    用途：追蹤 Firecrawl API 使用量，方便用戶了解消耗
    """
    __tablename__ = "scrape_quota_usage"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # 操作類型
    operation_type = Column(String(50), nullable=False)          # scrape, map, crawl
    credits_used = Column(Integer, default=1)                    # 消耗的 credits

    # 關聯
    category_id = Column(UUID(as_uuid=True), ForeignKey("category_databases.id"))
    product_id = Column(UUID(as_uuid=True), ForeignKey("category_products.id"))

    # 結果
    success = Column(Boolean, default=True)
    error_message = Column(Text)
    url = Column(Text)

    # 時間戳
    created_at = Column(DateTime, default=datetime.utcnow)
