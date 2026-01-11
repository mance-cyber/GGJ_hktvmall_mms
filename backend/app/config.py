# =============================================
# 環境配置管理
# =============================================

from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
import warnings


class Settings(BaseSettings):
    """應用程式設定，從環境變數讀取"""

    # 基本設定
    app_env: str = Field(default="development", alias="APP_ENV")
    debug: bool = Field(default=False, alias="DEBUG")  # C-04: 預設關閉 DEBUG
    secret_key: str = Field(default="dev-secret-key-CHANGE-IN-PRODUCTION", alias="SECRET_KEY")

    @field_validator('secret_key')
    @classmethod
    def validate_secret_key(cls, v, info):
        """C-01: 驗證 SECRET_KEY 強度"""
        app_env = info.data.get('app_env', 'production')
        if app_env != 'development':
            if 'dev-secret-key' in v or len(v) < 32:
                raise ValueError(
                    "SECRET_KEY must be a strong random string (min 32 chars) in production. "
                    "Generate one with: python -c \"import secrets; print(secrets.token_urlsafe(64))\""
                )
        return v

    @field_validator('debug')
    @classmethod
    def validate_debug(cls, v, info):
        """C-04: 生產環境警告 DEBUG 開啟"""
        app_env = info.data.get('app_env', 'production')
        if v and app_env == 'production':
            warnings.warn("WARNING: DEBUG is enabled in production environment!", RuntimeWarning)
        return v

    # 數據庫
    database_url: str = Field(alias="DATABASE_URL")

    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")

    # Firecrawl API
    firecrawl_api_key: str = Field(default="", alias="FIRECRAWL_API_KEY")

    # Claude AI
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")
    ai_model: str = Field(default="claude-sonnet-4-20250514", alias="AI_MODEL")

    @field_validator('anthropic_api_key')
    @classmethod
    def validate_anthropic_key(cls, v, info):
        """M-08: 驗證 AI API Key"""
        app_env = info.data.get('app_env', 'production')
        if not v and app_env == 'production':
            warnings.warn(
                "ANTHROPIC_API_KEY is not set. AI features will be unavailable.",
                RuntimeWarning
            )
        return v

    # Google Auth
    google_client_id: str = Field(default="", alias="GOOGLE_CLIENT_ID")
    # 允許登入的 Google 郵箱白名單（逗號分隔，留空表示允許所有）
    google_allowed_emails: str = Field(default="", alias="GOOGLE_ALLOWED_EMAILS")
    # 角色映射（逗號分隔）
    google_admin_emails: str = Field(default="", alias="GOOGLE_ADMIN_EMAILS")
    google_operator_emails: str = Field(default="", alias="GOOGLE_OPERATOR_EMAILS")

    # Cloudflare R2
    r2_access_key: str = Field(default="", alias="R2_ACCESS_KEY")
    r2_secret_key: str = Field(default="", alias="R2_SECRET_KEY")
    r2_bucket: str = Field(default="hktv-ops-storage", alias="R2_BUCKET")
    r2_endpoint: str = Field(default="", alias="R2_ENDPOINT")
    r2_public_url: str = Field(default="", alias="R2_PUBLIC_URL")

    # HKTVmall Connector
    hktv_connector_type: str = Field(default="mock", alias="HKTV_CONNECTOR_TYPE")
    
    # HKTVmall MMS API (New)
    hktv_api_base_url: str = Field(default="https://merchant-oapi.shoalter.com/oapi/api", alias="HKTVMALL_API_BASE_URL")
    hktv_store_code: str = Field(default="", alias="HKTVMALL_STORE_CODE")
    hktv_access_token: str = Field(default="", alias="HKTVMALL_ACCESS_TOKEN")

    # 通知
    notification_email: str = Field(default="", alias="NOTIFICATION_EMAIL")

    # Telegram 通知
    telegram_bot_token: str = Field(default="", alias="TELEGRAM_BOT_TOKEN")
    telegram_chat_id: str = Field(default="", alias="TELEGRAM_CHAT_ID")
    telegram_enabled: bool = Field(default=False, alias="TELEGRAM_ENABLED")

    # 爬取設定
    scrape_time: str = Field(default="09:00", alias="SCRAPE_TIME")
    price_alert_threshold: int = Field(default=10, alias="PRICE_ALERT_THRESHOLD")

    # AI Agent 模擬模式（用於測試，設為 true 啟用模擬數據）
    agent_mock_mode: bool = Field(default=False, alias="AGENT_MOCK_MODE")

    # Celery
    celery_broker_url: str = Field(default="redis://localhost:6379/0", alias="CELERY_BROKER_URL")
    celery_result_backend: str = Field(default="redis://localhost:6379/0", alias="CELERY_RESULT_BACKEND")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore"
    }


@lru_cache
def get_settings() -> Settings:
    """獲取快取的設定實例"""
    return Settings()

# Alias for backwards compatibility if needed
settings = get_settings()
