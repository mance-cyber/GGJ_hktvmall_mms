# =============================================
# 令牌桶速率限制器
# =============================================
# 使用 Redis 實現分佈式速率限制

import asyncio
import time
import random
from dataclasses import dataclass
from typing import Optional

import redis.asyncio as redis


@dataclass
class RateLimiterConfig:
    """速率限制配置"""
    requests_per_window: int = 10  # 每個時間窗口的請求數
    window_seconds: int = 60       # 時間窗口大小（秒）
    burst_size: int = 5            # 允許的突發大小
    max_wait_seconds: float = 30.0 # 最大等待時間


class TokenBucketRateLimiter:
    """
    令牌桶速率限制器

    實現原理：
    - 令牌以固定速率添加到桶中
    - 每次請求消耗一個令牌
    - 桶有最大容量（burst_size）
    - 若桶空則需要等待

    使用 Redis 實現分佈式限制，支持多進程/多實例
    """

    # Redis Lua 腳本：原子令牌桶操作
    LUA_SCRIPT = """
    local key = KEYS[1]
    local now = tonumber(ARGV[1])
    local rate = tonumber(ARGV[2])  -- 令牌生成速率（每秒）
    local burst = tonumber(ARGV[3]) -- 桶容量
    local requested = tonumber(ARGV[4]) -- 請求的令牌數

    -- 獲取當前狀態
    local data = redis.call('HMGET', key, 'tokens', 'last_update')
    local tokens = tonumber(data[1]) or burst
    local last_update = tonumber(data[2]) or now

    -- 計算自上次更新以來生成的令牌
    local elapsed = now - last_update
    local generated = elapsed * rate
    tokens = math.min(burst, tokens + generated)

    -- 嘗試消耗令牌
    if tokens >= requested then
        tokens = tokens - requested
        redis.call('HMSET', key, 'tokens', tokens, 'last_update', now)
        redis.call('EXPIRE', key, 300) -- 5 分鐘過期
        return tokens
    else
        -- 令牌不足，返回負數表示需要等待的時間
        local wait_time = (requested - tokens) / rate
        redis.call('HMSET', key, 'tokens', tokens, 'last_update', now)
        redis.call('EXPIRE', key, 300)
        return -wait_time
    end
    """

    def __init__(
        self,
        redis_client: redis.Redis,
        config: Optional[RateLimiterConfig] = None,
        key_prefix: str = "rate_limit"
    ):
        self.redis = redis_client
        self.config = config or RateLimiterConfig()
        self.key_prefix = key_prefix
        self._script_sha: Optional[str] = None

    async def _ensure_script(self) -> str:
        """確保 Lua 腳本已加載"""
        if self._script_sha is None:
            self._script_sha = await self.redis.script_load(self.LUA_SCRIPT)
        return self._script_sha

    def _get_key(self, identifier: str) -> str:
        """生成 Redis key"""
        return f"{self.key_prefix}:{identifier}"

    async def acquire(
        self,
        identifier: str,
        tokens: int = 1,
        wait: bool = True
    ) -> bool:
        """
        嘗試獲取令牌

        Args:
            identifier: 限制標識符（如域名、用戶 ID）
            tokens: 請求的令牌數
            wait: 是否等待直到獲取令牌

        Returns:
            是否成功獲取令牌
        """
        key = self._get_key(identifier)
        rate = self.config.requests_per_window / self.config.window_seconds
        burst = self.config.burst_size

        try:
            sha = await self._ensure_script()
            now = time.time()

            result = await self.redis.evalsha(
                sha,
                1,
                key,
                now,
                rate,
                burst,
                tokens
            )

            if result >= 0:
                # 成功獲取令牌
                return True

            if not wait:
                return False

            # 需要等待
            wait_time = abs(result)
            if wait_time > self.config.max_wait_seconds:
                return False

            # 添加隨機抖動避免驚群效應
            jitter = random.uniform(0.1, 0.5)
            await asyncio.sleep(wait_time + jitter)

            # 重試
            return await self.acquire(identifier, tokens, wait=False)

        except redis.RedisError:
            # Redis 不可用時，降級為允許請求
            return True

    async def get_remaining(self, identifier: str) -> int:
        """獲取剩餘令牌數"""
        key = self._get_key(identifier)
        try:
            data = await self.redis.hget(key, "tokens")
            return int(float(data)) if data else self.config.burst_size
        except (redis.RedisError, ValueError):
            return self.config.burst_size

    async def reset(self, identifier: str) -> None:
        """重置限制器"""
        key = self._get_key(identifier)
        try:
            await self.redis.delete(key)
        except redis.RedisError:
            pass


class DomainRateLimiter:
    """
    基於域名的速率限制器

    為不同平台/域名應用不同的速率限制策略
    """

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self._limiters: dict[str, TokenBucketRateLimiter] = {}
        self._default_config = RateLimiterConfig()

    def get_limiter(
        self,
        domain: str,
        config: Optional[RateLimiterConfig] = None
    ) -> TokenBucketRateLimiter:
        """獲取域名對應的限制器"""
        if domain not in self._limiters:
            self._limiters[domain] = TokenBucketRateLimiter(
                redis_client=self.redis,
                config=config or self._default_config,
                key_prefix=f"rate_limit:{domain}"
            )
        return self._limiters[domain]

    async def acquire(
        self,
        domain: str,
        config: Optional[RateLimiterConfig] = None
    ) -> bool:
        """獲取域名的請求許可"""
        limiter = self.get_limiter(domain, config)
        return await limiter.acquire(domain)


# =============================================
# 並發限制器（信號量）
# =============================================

class ConcurrencyLimiter:
    """
    並發限制器

    限制同時進行的請求數量
    """

    def __init__(
        self,
        redis_client: redis.Redis,
        max_concurrent: int = 5,
        key_prefix: str = "concurrent"
    ):
        self.redis = redis_client
        self.max_concurrent = max_concurrent
        self.key_prefix = key_prefix

    def _get_key(self, identifier: str) -> str:
        return f"{self.key_prefix}:{identifier}"

    async def acquire(self, identifier: str, timeout: float = 30.0) -> bool:
        """
        獲取並發許可

        使用 Redis INCR + EXPIRE 實現
        """
        key = self._get_key(identifier)
        try:
            # 增加計數
            count = await self.redis.incr(key)
            # 設置過期時間（防止死鎖）
            await self.redis.expire(key, int(timeout) + 10)

            if count <= self.max_concurrent:
                return True

            # 超過限制，回退計數
            await self.redis.decr(key)
            return False

        except redis.RedisError:
            return True  # 降級為允許

    async def release(self, identifier: str) -> None:
        """釋放並發許可"""
        key = self._get_key(identifier)
        try:
            await self.redis.decr(key)
        except redis.RedisError:
            pass

    async def get_current(self, identifier: str) -> int:
        """獲取當前並發數"""
        key = self._get_key(identifier)
        try:
            count = await self.redis.get(key)
            return int(count) if count else 0
        except (redis.RedisError, ValueError):
            return 0


# =============================================
# 上下文管理器
# =============================================

class RateLimitContext:
    """速率限制上下文管理器"""

    def __init__(
        self,
        rate_limiter: TokenBucketRateLimiter,
        concurrency_limiter: Optional[ConcurrencyLimiter],
        identifier: str
    ):
        self.rate_limiter = rate_limiter
        self.concurrency_limiter = concurrency_limiter
        self.identifier = identifier
        self._acquired_concurrency = False

    async def __aenter__(self):
        # 獲取速率限制許可
        await self.rate_limiter.acquire(self.identifier)

        # 獲取並發限制許可
        if self.concurrency_limiter:
            self._acquired_concurrency = await self.concurrency_limiter.acquire(
                self.identifier
            )
            if not self._acquired_concurrency:
                raise Exception(f"並發限制已達上限: {self.identifier}")

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # 釋放並發限制
        if self.concurrency_limiter and self._acquired_concurrency:
            await self.concurrency_limiter.release(self.identifier)
        return False
