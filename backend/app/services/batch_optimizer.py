# =============================================
# 批量爬取優化器
# =============================================
# 優化批量爬取的並發、分組、優先級

import asyncio
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, List, AsyncGenerator, Callable
from urllib.parse import urlparse
import logging

from app.services.scrape_executor import (
    ScrapeExecutor,
    SmartScrapeExecutor,
    ScrapeConfig,
    ScrapeResult,
    get_smart_scrape_executor,
)
from app.services.rate_limiter import (
    TokenBucketRateLimiter,
    ConcurrencyLimiter,
    RateLimiterConfig,
)

logger = logging.getLogger(__name__)


@dataclass
class BatchConfig:
    """批量爬取配置"""
    max_concurrent: int = 5           # 全局最大並發
    domain_concurrent: int = 2         # 單域名最大並發
    batch_size: int = 50              # 每批處理數量
    adaptive_concurrency: bool = True  # 動態調整並發
    success_rate_threshold: float = 0.8  # 成功率閾值（低於此值降低並發）


@dataclass
class BatchProgress:
    """批量處理進度"""
    total: int = 0
    processed: int = 0
    successful: int = 0
    failed: int = 0
    current_concurrency: int = 0
    started_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @property
    def progress_percent(self) -> float:
        return (self.processed / self.total * 100) if self.total > 0 else 0

    @property
    def success_rate(self) -> float:
        return (self.successful / self.processed) if self.processed > 0 else 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total": self.total,
            "processed": self.processed,
            "successful": self.successful,
            "failed": self.failed,
            "progress_percent": round(self.progress_percent, 1),
            "success_rate": round(self.success_rate * 100, 1),
            "current_concurrency": self.current_concurrency,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class BatchOptimizer:
    """
    批量爬取優化器

    功能：
    1. URL 分組（按域名）
    2. 動態調整並發
    3. 優先級排序
    4. 進度追蹤
    """

    def __init__(
        self,
        executor: Optional[SmartScrapeExecutor] = None,
        config: Optional[BatchConfig] = None,
    ):
        self.executor = executor or get_smart_scrape_executor()
        self.config = config or BatchConfig()
        self._progress = BatchProgress()
        self._current_concurrency = self.config.max_concurrent
        self._domain_semaphores: Dict[str, asyncio.Semaphore] = {}
        self._global_semaphore: Optional[asyncio.Semaphore] = None

    def _get_domain(self, url: str) -> str:
        """從 URL 提取域名"""
        parsed = urlparse(url)
        return parsed.netloc.lower()

    def _group_by_domain(self, urls: List[str]) -> Dict[str, List[str]]:
        """按域名分組 URL"""
        groups: Dict[str, List[str]] = defaultdict(list)
        for url in urls:
            domain = self._get_domain(url)
            groups[domain].append(url)
        return dict(groups)

    def _get_domain_semaphore(self, domain: str) -> asyncio.Semaphore:
        """獲取域名信號量"""
        if domain not in self._domain_semaphores:
            self._domain_semaphores[domain] = asyncio.Semaphore(
                self.config.domain_concurrent
            )
        return self._domain_semaphores[domain]

    def _adjust_concurrency(self) -> None:
        """動態調整並發（基於成功率）"""
        if not self.config.adaptive_concurrency:
            return

        if self._progress.processed < 10:
            return  # 樣本太少

        success_rate = self._progress.success_rate

        if success_rate < self.config.success_rate_threshold:
            # 降低並發
            new_concurrency = max(1, self._current_concurrency - 1)
            if new_concurrency != self._current_concurrency:
                logger.info(
                    f"成功率 {success_rate:.1%} 低於閾值，降低並發: "
                    f"{self._current_concurrency} -> {new_concurrency}"
                )
                self._current_concurrency = new_concurrency
        elif success_rate > 0.95 and self._current_concurrency < self.config.max_concurrent:
            # 提高並發
            new_concurrency = min(
                self.config.max_concurrent,
                self._current_concurrency + 1
            )
            if new_concurrency != self._current_concurrency:
                logger.info(
                    f"成功率 {success_rate:.1%} 優秀，提高並發: "
                    f"{self._current_concurrency} -> {new_concurrency}"
                )
                self._current_concurrency = new_concurrency

    async def _scrape_with_limits(
        self,
        url: str,
        domain_semaphore: asyncio.Semaphore,
    ) -> ScrapeResult:
        """帶限制的爬取"""
        # 獲取域名信號量
        async with domain_semaphore:
            # 獲取全局信號量
            if self._global_semaphore:
                async with self._global_semaphore:
                    return await self.executor.smart_execute(url)
            else:
                return await self.executor.smart_execute(url)

    async def process_batch(
        self,
        urls: List[str],
        on_progress: Optional[Callable[[BatchProgress], None]] = None,
    ) -> AsyncGenerator[ScrapeResult, None]:
        """
        處理批量 URL

        Args:
            urls: URL 列表
            on_progress: 進度回調

        Yields:
            ScrapeResult 爬取結果（按完成順序）
        """
        # 初始化進度
        self._progress = BatchProgress(
            total=len(urls),
            processed=0,
            successful=0,
            failed=0,
            current_concurrency=self._current_concurrency,
            started_at=datetime.utcnow(),
        )

        # 初始化全局信號量
        self._global_semaphore = asyncio.Semaphore(self._current_concurrency)

        # 按域名分組
        domain_groups = self._group_by_domain(urls)
        logger.info(f"批量爬取: {len(urls)} URLs, {len(domain_groups)} 域名")

        # 創建所有任務
        async def process_url(url: str) -> ScrapeResult:
            domain = self._get_domain(url)
            domain_semaphore = self._get_domain_semaphore(domain)
            return await self._scrape_with_limits(url, domain_semaphore)

        # 使用 asyncio.as_completed 按完成順序返回
        tasks = [asyncio.create_task(process_url(url)) for url in urls]

        for future in asyncio.as_completed(tasks):
            try:
                result = await future

                # 更新進度
                self._progress.processed += 1
                if result.success:
                    self._progress.successful += 1
                else:
                    self._progress.failed += 1
                self._progress.updated_at = datetime.utcnow()
                self._progress.current_concurrency = self._current_concurrency

                # 動態調整並發
                self._adjust_concurrency()

                # 回調
                if on_progress:
                    on_progress(self._progress)

                yield result

            except Exception as e:
                logger.error(f"批量處理錯誤: {e}")
                self._progress.processed += 1
                self._progress.failed += 1

    async def process_batch_all(
        self,
        urls: List[str],
        on_progress: Optional[Callable[[BatchProgress], None]] = None,
    ) -> List[ScrapeResult]:
        """
        處理批量 URL（返回所有結果）

        Args:
            urls: URL 列表
            on_progress: 進度回調

        Returns:
            所有爬取結果
        """
        results = []
        async for result in self.process_batch(urls, on_progress):
            results.append(result)
        return results

    def get_progress(self) -> BatchProgress:
        """獲取當前進度"""
        return self._progress


class PriorityBatchOptimizer(BatchOptimizer):
    """
    優先級批量優化器

    支持 URL 優先級排序
    """

    def __init__(
        self,
        executor: Optional[SmartScrapeExecutor] = None,
        config: Optional[BatchConfig] = None,
    ):
        super().__init__(executor, config)
        self._priority_rules: List[Callable[[str], int]] = []

    def add_priority_rule(self, rule: Callable[[str], int]) -> None:
        """
        添加優先級規則

        Args:
            rule: 接受 URL 返回優先級（數字越大優先級越高）
        """
        self._priority_rules.append(rule)

    def _calculate_priority(self, url: str) -> int:
        """計算 URL 優先級"""
        if not self._priority_rules:
            return 0
        return sum(rule(url) for rule in self._priority_rules)

    def _sort_by_priority(self, urls: List[str]) -> List[str]:
        """按優先級排序 URL"""
        return sorted(urls, key=self._calculate_priority, reverse=True)

    async def process_batch(
        self,
        urls: List[str],
        on_progress: Optional[Callable[[BatchProgress], None]] = None,
    ) -> AsyncGenerator[ScrapeResult, None]:
        """處理批量 URL（按優先級）"""
        sorted_urls = self._sort_by_priority(urls)
        async for result in super().process_batch(sorted_urls, on_progress):
            yield result


# =============================================
# 批量導入處理器
# =============================================

@dataclass
class ImportResult:
    """導入結果"""
    url: str
    success: bool
    is_duplicate: bool = False
    product_id: Optional[str] = None
    error_message: Optional[str] = None


class BatchImportProcessor:
    """
    批量導入處理器

    處理 URL 導入流程：
    1. 驗證 URL
    2. 檢查重複
    3. 爬取數據
    4. 入庫
    """

    def __init__(
        self,
        optimizer: Optional[BatchOptimizer] = None,
    ):
        self.optimizer = optimizer or BatchOptimizer()
        self._existing_urls: set = set()

    def set_existing_urls(self, urls: List[str]) -> None:
        """設置已存在的 URL（用於重複檢查）"""
        self._existing_urls = set(urls)

    def validate_url(self, url: str) -> Optional[str]:
        """
        驗證 URL

        Returns:
            錯誤信息，None 表示有效
        """
        if not url:
            return "URL 為空"

        if not url.startswith(("http://", "https://")):
            return "URL 必須以 http:// 或 https:// 開頭"

        try:
            parsed = urlparse(url)
            if not parsed.netloc:
                return "無效的 URL 格式"
        except Exception:
            return "無法解析 URL"

        return None

    def check_duplicate(self, url: str) -> bool:
        """檢查是否重複"""
        return url in self._existing_urls

    async def process_import(
        self,
        urls: List[str],
        on_progress: Optional[Callable[[BatchProgress], None]] = None,
    ) -> AsyncGenerator[ImportResult, None]:
        """
        處理導入

        Yields:
            ImportResult 導入結果
        """
        # 驗證和去重
        valid_urls = []
        for url in urls:
            # 驗證
            error = self.validate_url(url)
            if error:
                yield ImportResult(url=url, success=False, error_message=error)
                continue

            # 重複檢查
            if self.check_duplicate(url):
                yield ImportResult(url=url, success=False, is_duplicate=True)
                continue

            valid_urls.append(url)

        # 批量爬取
        async for result in self.optimizer.process_batch(valid_urls, on_progress):
            if result.success:
                # 添加到已存在集合
                self._existing_urls.add(result.url)
                yield ImportResult(
                    url=result.url,
                    success=True,
                    # product_id 由調用者處理入庫後填充
                )
            else:
                yield ImportResult(
                    url=result.url,
                    success=False,
                    error_message=result.error_message,
                )


# =============================================
# 工廠函數
# =============================================

_batch_optimizer: Optional[BatchOptimizer] = None
_priority_optimizer: Optional[PriorityBatchOptimizer] = None


def get_batch_optimizer() -> BatchOptimizer:
    """獲取批量優化器單例"""
    global _batch_optimizer
    if _batch_optimizer is None:
        _batch_optimizer = BatchOptimizer()
    return _batch_optimizer


def get_priority_batch_optimizer() -> PriorityBatchOptimizer:
    """獲取優先級批量優化器單例"""
    global _priority_optimizer
    if _priority_optimizer is None:
        _priority_optimizer = PriorityBatchOptimizer()
    return _priority_optimizer
