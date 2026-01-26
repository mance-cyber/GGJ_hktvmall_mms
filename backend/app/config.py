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
        """C-01: 驗證 SECRET_KEY 強度 - 生產環境必須使用強密鑰"""
        app_env = info.data.get('app_env', 'production')
        if app_env != 'development':
            # 生產環境必須檢查
            if not v:
                raise ValueError(
                    "SECRET_KEY is required in production. "
                    "Generate one with: python -c \"import secrets; print(secrets.token_urlsafe(64))\""
                )
            if 'dev-secret-key' in v.lower() or 'change' in v.lower() or 'default' in v.lower():
                raise ValueError(
                    "SECRET_KEY contains unsafe default value. Please set a strong random key. "
                    "Generate one with: python -c \"import secrets; print(secrets.token_urlsafe(64))\""
                )
            if len(v) < 32:
                raise ValueError(
                    f"SECRET_KEY is too short ({len(v)} chars). Minimum 32 characters required. "
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

    # Nano-Banana 圖片生成 API
    nano_banana_api_base: str = Field(default="https://ai.t8star.cn/v1", alias="NANO_BANANA_API_BASE")
    nano_banana_api_key: str = Field(default="", alias="NANO_BANANA_API_KEY")
    nano_banana_model: str = Field(default="nano-banana-2-4k", alias="NANO_BANANA_MODEL")
    upload_dir: str = Field(default="./uploads", alias="UPLOAD_DIR")

    # Gemini Thinking 模型（用於圖片分析，第一階段）
    gemini_thinking_model: str = Field(default="gemini-3-pro-preview-thinking-0325", alias="GEMINI_THINKING_MODEL")

    # 存儲配置
    use_r2_storage: bool = Field(default=False, alias="USE_R2_STORAGE")

    # CORS 配置
    cors_origins_production: str = Field(
        default="https://ggj-front.zeabur.app,https://ggj-back.zeabur.app",
        alias="CORS_ORIGINS_PRODUCTION"
    )
    cors_origins_development: str = Field(
        default="http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001,http://127.0.0.1:3001,http://localhost:8000,http://127.0.0.1:8000",
        alias="CORS_ORIGINS_DEVELOPMENT"
    )

    # OpenAI 兼容 API（用於 AI 設定服務的預設值）
    openai_base_url: str = Field(
        default="https://api.openai.com/v1",
        alias="OPENAI_BASE_URL"
    )
    openai_default_model: str = Field(
        default="gpt-4o",
        alias="OPENAI_DEFAULT_MODEL"
    )

    def get_cors_origins(self) -> list[str]:
        """獲取 CORS 允許的來源列表"""
        origins = [o.strip() for o in self.cors_origins_production.split(",") if o.strip()]
        if self.debug:
            origins.extend([o.strip() for o in self.cors_origins_development.split(",") if o.strip()])
        return origins

    @field_validator('nano_banana_api_key')
    @classmethod
    def validate_nano_banana_key(cls, v, info):
        """驗證 Nano-Banana API Key"""
        app_env = info.data.get('app_env', 'production')
        if not v and app_env == 'production':
            warnings.warn(
                "NANO_BANANA_API_KEY is not set. Image generation features will be unavailable.",
                RuntimeWarning
            )
        return v

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
