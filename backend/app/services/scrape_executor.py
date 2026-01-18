# =============================================
# 爬取執行器（優化版）
# =============================================
# 核心爬取邏輯，包含重試、錯誤處理、配置管理
# 優化：正確傳遞 timeout、使用 ScrapeOptions

import asyncio
import random
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List
from urllib.parse import urlparse

from app.connectors.firecrawl import (
    FirecrawlConnector, ProductInfo, get_firecrawl_connector,
    ScrapeOptions, ScrapeMode
)


class ErrorType(Enum):
    """錯誤類型分類"""
    NETWORK = "network"          # 網絡錯誤（可重試）
    RATE_LIMIT = "rate_limit"    # 速率限制（等待後重試）
    PARSE = "parse"              # 解析錯誤（可嘗試備用方案）
    NOT_FOUND = "not_found"      # 頁面不存在（不重試）
    BLOCKED = "blocked"          # 被封禁（需要代理/等待）
    TIMEOUT = "timeout"          # 超時（可重試）
    UNKNOWN = "unknown"          # 未知錯誤


@dataclass
class ScrapeConfig:
    """爬取配置（優化版）"""
    # 請求配置
    wait_time_ms: int = 3000
    use_actions: bool = False
    actions_config: Optional[List[Dict]] = None
    use_json_mode: bool = True

    # 重試配置
    max_retries: int = 3
    retry_delay_seconds: float = 5.0
    exponential_backoff: bool = True
    max_backoff_seconds: float = 60.0

    # 超時配置
    request_timeout_seconds: float = 30.0

    # 新增：高級選項
    skip_tls_verification: bool = False
    mobile: bool = False
    headers: Optional[Dict[str, str]] = None
    max_age: Optional[int] = None  # 緩存最大年齡（毫秒）

    def to_scrape_options(self) -> ScrapeOptions:
        """轉換為 ScrapeOptions"""
        return ScrapeOptions(
            wait_for=self.wait_time_ms,
            timeout=int(self.request_timeout_seconds * 1000),
            skip_tls_verification=self.skip_tls_verification,
            mobile=self.mobile,
            headers=self.headers,
            max_age=self.max_age,
        )

    @classmethod
    def for_hktvmall(cls) -> "ScrapeConfig":
        """HKTVmall 優化配置"""
        return cls(
            wait_time_ms=8000,
            request_timeout_seconds=60.0,
            skip_tls_verification=True,
            use_json_mode=True,
            max_retries=3,
        )

    @classmethod
    def for_google(cls) -> "ScrapeConfig":
        """Google SERP 配置"""
        return cls(
            wait_time_ms=5000,
            request_timeout_seconds=30.0,
            use_json_mode=False,
            headers={
                "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8"
            }
        )


@dataclass
class ScrapeResult:
    """爬取結果"""
    url: str
    success: bool
    product_info: Optional[ProductInfo] = None
    raw_data: Optional[Dict[str, Any]] = None
    error_type: Optional[ErrorType] = None
    error_message: Optional[str] = None
    attempts: int = 0
    duration_ms: int = 0
    scraped_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        result = {
            "url": self.url,
            "success": self.success,
            "attempts": self.attempts,
            "duration_ms": self.duration_ms,
            "scraped_at": self.scraped_at.isoformat(),
        }
        if self.product_info:
            result["product_info"] = {
                "name": self.product_info.name,
                "price": float(self.product_info.price) if self.product_info.price else None,
                "original_price": float(self.product_info.original_price) if self.product_info.original_price else None,
                "discount_percent": float(self.product_info.discount_percent) if self.product_info.discount_percent else None,
                "stock_status": self.product_info.stock_status,
                "rating": float(self.product_info.rating) if self.product_info.rating else None,
                "review_count": self.product_info.review_count,
                "image_url": self.product_info.image_url,
                "sku": self.product_info.sku,
                "brand": self.product_info.brand,
                "category": self.product_info.category,
                "description": self.product_info.description,
                "promotion_text": self.product_info.promotion_text,
            }
        if self.error_type:
            result["error_type"] = self.error_type.value
            result["error_message"] = self.error_message
        return result


class ScrapeExecutor:
    """
    爬取執行器

    職責：
    1. 執行單個 URL 的爬取
    2. 處理錯誤分類和重試邏輯
    3. 應用配置（等待時間、Actions 等）
    """

    def __init__(self, connector: Optional[FirecrawlConnector] = None):
        self.connector = connector or get_firecrawl_connector()

    def _classify_error(self, error: Exception) -> ErrorType:
        """
        分類錯誤類型

        根據錯誤類型決定重試策略
        """
        error_str = str(error).lower()

        # 速率限制
        if any(kw in error_str for kw in ["rate limit", "too many requests", "429"]):
            return ErrorType.RATE_LIMIT

        # 超時
        if any(kw in error_str for kw in ["timeout", "timed out"]):
            return ErrorType.TIMEOUT

        # 網絡錯誤
        if any(kw in error_str for kw in ["connection", "network", "dns", "refused"]):
            return ErrorType.NETWORK

        # 頁面不存在
        if any(kw in error_str for kw in ["404", "not found"]):
            return ErrorType.NOT_FOUND

        # 被封禁
        if any(kw in error_str for kw in ["403", "forbidden", "blocked", "captcha"]):
            return ErrorType.BLOCKED

        # 解析錯誤
        if any(kw in error_str for kw in ["parse", "json", "decode", "extract"]):
            return ErrorType.PARSE

        return ErrorType.UNKNOWN

    def _should_retry(self, error_type: ErrorType) -> bool:
        """判斷是否應該重試"""
        return error_type in {
            ErrorType.NETWORK,
            ErrorType.RATE_LIMIT,
            ErrorType.TIMEOUT,
            ErrorType.PARSE,
            ErrorType.UNKNOWN,
        }

    def _calculate_backoff(
        self,
        attempt: int,
        base_delay: float,
        exponential: bool,
        max_backoff: float
    ) -> float:
        """
        計算退避時間

        使用指數退避 + 隨機抖動
        """
        if exponential:
            delay = base_delay * (2 ** attempt)
        else:
            delay = base_delay

        # 添加隨機抖動（±25%）
        jitter = delay * random.uniform(-0.25, 0.25)
        delay = delay + jitter

        # 限制最大退避時間
        return min(delay, max_backoff)

    async def execute(
        self,
        url: str,
        config: Optional[ScrapeConfig] = None
    ) -> ScrapeResult:
        """
        執行爬取（無重試）（優化版）

        Args:
            url: 要爬取的 URL
            config: 爬取配置

        Returns:
            ScrapeResult 爬取結果
        """
        config = config or ScrapeConfig()
        start_time = time.time()

        # 轉換為 ScrapeOptions（正確傳遞 timeout）
        scrape_options = config.to_scrape_options()

        try:
            # 根據配置決定爬取方式
            if config.use_actions and config.actions_config:
                raw_data = self.connector.scrape_with_actions(
                    url,
                    actions=config.actions_config,
                    take_screenshot=False,
                    options=scrape_options  # 傳遞選項
                )
            else:
                raw_data = self.connector.scrape_url(
                    url,
                    use_json_mode=config.use_json_mode,
                    options=scrape_options  # 傳遞選項（包含 timeout）
                )

            # 解析商品信息
            product_info = self.connector.extract_product_info(url, use_actions=config.use_actions)

            duration_ms = int((time.time() - start_time) * 1000)

            return ScrapeResult(
                url=url,
                success=True,
                product_info=product_info,
                raw_data=raw_data,
                attempts=1,
                duration_ms=duration_ms,
            )

        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            error_type = self._classify_error(e)

            return ScrapeResult(
                url=url,
                success=False,
                error_type=error_type,
                error_message=str(e),
                attempts=1,
                duration_ms=duration_ms,
            )

    async def execute_with_retry(
        self,
        url: str,
        config: Optional[ScrapeConfig] = None
    ) -> ScrapeResult:
        """
        執行爬取（含重試）

        Args:
            url: 要爬取的 URL
            config: 爬取配置

        Returns:
            ScrapeResult 爬取結果
        """
        config = config or ScrapeConfig()
        total_start_time = time.time()
        last_result: Optional[ScrapeResult] = None

        for attempt in range(config.max_retries + 1):
            # 執行爬取
            result = await self.execute(url, config)
            result.attempts = attempt + 1
            last_result = result

            if result.success:
                # 成功
                result.duration_ms = int((time.time() - total_start_time) * 1000)
                return result

            # 檢查是否應該重試
            if not self._should_retry(result.error_type):
                return result

            if attempt >= config.max_retries:
                # 已達最大重試次數
                return result

            # 計算退避時間
            backoff = self._calculate_backoff(
                attempt,
                config.retry_delay_seconds,
                config.exponential_backoff,
                config.max_backoff_seconds
            )

            # 速率限制錯誤需要更長等待
            if result.error_type == ErrorType.RATE_LIMIT:
                backoff = max(backoff, 10.0)

            # 等待後重試
            await asyncio.sleep(backoff)

        # 返回最後一次結果
        if last_result:
            last_result.duration_ms = int((time.time() - total_start_time) * 1000)
            return last_result

        # 不應該到達這裡
        return ScrapeResult(
            url=url,
            success=False,
            error_type=ErrorType.UNKNOWN,
            error_message="未知錯誤",
            attempts=config.max_retries + 1,
            duration_ms=int((time.time() - total_start_time) * 1000),
        )


class SmartScrapeExecutor(ScrapeExecutor):
    """
    智能爬取執行器

    額外功能：
    1. 自動選擇最佳爬取策略
    2. 基於域名的配置管理
    3. 失敗時自動切換備用方案
    """

    def __init__(self, connector: Optional[FirecrawlConnector] = None):
        super().__init__(connector)
        self._domain_configs: Dict[str, ScrapeConfig] = {}

    def get_domain(self, url: str) -> str:
        """從 URL 提取域名"""
        parsed = urlparse(url)
        return parsed.netloc.lower()

    def set_domain_config(self, domain: str, config: ScrapeConfig) -> None:
        """設置域名特定配置"""
        self._domain_configs[domain] = config

    def get_config_for_url(self, url: str) -> ScrapeConfig:
        """獲取 URL 對應的配置"""
        domain = self.get_domain(url)

        # 查找域名配置
        if domain in self._domain_configs:
            return self._domain_configs[domain]

        # 檢查是否匹配子域名
        for config_domain, config in self._domain_configs.items():
            if domain.endswith(f".{config_domain}") or domain == config_domain:
                return config

        # 返回默認配置
        return ScrapeConfig()

    async def smart_execute(self, url: str) -> ScrapeResult:
        """
        智能爬取（優化版）

        自動選擇配置並處理失敗重試
        """
        config = self.get_config_for_url(url)

        # 第一次嘗試：使用 JSON Mode
        result = await self.execute_with_retry(url, config)
        if result.success:
            return result

        # JSON Mode 失敗，嘗試備用方案
        if result.error_type == ErrorType.PARSE:
            # 禁用 JSON Mode，使用更長等待時間
            fallback_config = ScrapeConfig(
                wait_time_ms=config.wait_time_ms + 3000,  # 增加 3 秒
                request_timeout_seconds=config.request_timeout_seconds + 15,  # 增加 15 秒
                use_actions=True,
                actions_config=[
                    {"type": "wait", "milliseconds": 3000},
                    {"type": "scroll", "direction": "down", "amount": 500},
                    {"type": "wait", "milliseconds": 2000},
                    {"type": "scroll", "direction": "down", "amount": 500},
                    {"type": "wait", "milliseconds": 1000},
                ],
                use_json_mode=False,
                max_retries=1,
                skip_tls_verification=config.skip_tls_verification,
            )
            fallback_result = await self.execute_with_retry(url, fallback_config)
            if fallback_result.success:
                return fallback_result

        # 超時錯誤，嘗試更長超時
        if result.error_type == ErrorType.TIMEOUT:
            timeout_config = ScrapeConfig(
                wait_time_ms=config.wait_time_ms,
                request_timeout_seconds=90.0,  # 90 秒超時
                use_json_mode=config.use_json_mode,
                max_retries=1,
                skip_tls_verification=True,
            )
            timeout_result = await self.execute_with_retry(url, timeout_config)
            if timeout_result.success:
                return timeout_result

        return result


# =============================================
# 工廠函數
# =============================================

_executor: Optional[ScrapeExecutor] = None
_smart_executor: Optional[SmartScrapeExecutor] = None


def get_scrape_executor() -> ScrapeExecutor:
    """獲取爬取執行器單例"""
    global _executor
    if _executor is None:
        _executor = ScrapeExecutor()
    return _executor


def get_smart_scrape_executor() -> SmartScrapeExecutor:
    """獲取智能爬取執行器單例"""
    global _smart_executor
    if _smart_executor is None:
        _smart_executor = SmartScrapeExecutor()
    return _smart_executor
