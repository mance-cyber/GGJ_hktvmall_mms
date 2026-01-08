# =============================================
# 爬取配置模型
# =============================================

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
import uuid

from sqlalchemy import Column, String, Integer, Boolean, Text, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.models.database import Base


class ScrapeConfig(Base):
    """平台爬取配置"""

    __tablename__ = "scrape_configs"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    platform: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # 解析配置
    product_schema: Mapped[Optional[Dict]] = mapped_column(JSONB, nullable=True)
    selectors: Mapped[Optional[Dict]] = mapped_column(JSONB, nullable=True)

    # 請求配置
    user_agents: Mapped[List] = mapped_column(JSONB, default=list)
    request_headers: Mapped[Dict] = mapped_column(JSONB, default=dict)
    wait_time_ms: Mapped[int] = mapped_column(Integer, default=3000)
    use_actions: Mapped[bool] = mapped_column(Boolean, default=False)
    actions_config: Mapped[Optional[Dict]] = mapped_column(JSONB, nullable=True)

    # 速率限制
    rate_limit_requests: Mapped[int] = mapped_column(Integer, default=10)
    rate_limit_window_seconds: Mapped[int] = mapped_column(Integer, default=60)
    concurrent_limit: Mapped[int] = mapped_column(Integer, default=3)

    # 重試配置
    max_retries: Mapped[int] = mapped_column(Integer, default=3)
    retry_delay_seconds: Mapped[int] = mapped_column(Integer, default=5)
    exponential_backoff: Mapped[bool] = mapped_column(Boolean, default=True)

    # 代理配置
    proxy_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    proxy_pool: Mapped[List] = mapped_column(JSONB, default=list)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # 關聯
    competitors = relationship("Competitor", back_populates="scrape_config")

    __table_args__ = (
        Index("idx_scrape_configs_platform", "platform"),
        Index("idx_scrape_configs_is_active", "is_active"),
    )

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "id": str(self.id),
            "platform": self.platform,
            "name": self.name,
            "product_schema": self.product_schema,
            "selectors": self.selectors,
            "user_agents": self.user_agents,
            "request_headers": self.request_headers,
            "wait_time_ms": self.wait_time_ms,
            "use_actions": self.use_actions,
            "actions_config": self.actions_config,
            "rate_limit_requests": self.rate_limit_requests,
            "rate_limit_window_seconds": self.rate_limit_window_seconds,
            "concurrent_limit": self.concurrent_limit,
            "max_retries": self.max_retries,
            "retry_delay_seconds": self.retry_delay_seconds,
            "exponential_backoff": self.exponential_backoff,
            "proxy_enabled": self.proxy_enabled,
            "proxy_pool": self.proxy_pool,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
