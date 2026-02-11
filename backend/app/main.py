# =============================================
# FastAPI 應用入口
# =============================================

from contextlib import asynccontextmanager
from collections import defaultdict
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from pathlib import Path
import time

from app.config import get_settings
from app.models.database import init_db
from app.api.v1.router import api_router
from app.core.logging import setup_logging
from app.core.exceptions import register_exception_handlers


# =============================================
# H-03: 全局限速中間件 (In-Memory)
# =============================================
class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    基於滑動窗口的速率限制中間件

    採用簡單的內存存儲，適用於單實例部署。
    多實例部署需改用 Redis 版本。
    """

    def __init__(self, app, requests_per_minute: int = 60, login_limit: int = 5):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.login_limit = login_limit
        self.window_seconds = 60
        # {client_ip: [(timestamp, path), ...]}
        self._requests: dict = defaultdict(list)
        self._cleanup_interval = 300  # 5 分鐘清理一次過期記錄
        self._last_cleanup = time.time()

    def _get_client_ip(self, request: Request) -> str:
        """獲取客戶端 IP，支持反向代理"""
        # 優先檢查 X-Forwarded-For 標頭
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            # 取第一個 IP (原始客戶端)
            return forwarded.split(",")[0].strip()
        # 直連情況
        return request.client.host if request.client else "unknown"

    def _cleanup_old_records(self, now: float) -> None:
        """清理過期的請求記錄"""
        if now - self._last_cleanup < self._cleanup_interval:
            return

        cutoff = now - self.window_seconds
        for ip in list(self._requests.keys()):
            self._requests[ip] = [
                (ts, path) for ts, path in self._requests[ip]
                if ts > cutoff
            ]
            if not self._requests[ip]:
                del self._requests[ip]

        self._last_cleanup = now

    def _count_requests(self, ip: str, now: float, path_filter: str = None) -> int:
        """計算指定時間窗口內的請求數"""
        cutoff = now - self.window_seconds
        requests = self._requests[ip]

        if path_filter:
            return sum(1 for ts, path in requests if ts > cutoff and path_filter in path)
        return sum(1 for ts, path in requests if ts > cutoff)

    async def dispatch(self, request: Request, call_next):
        settings = get_settings()

        # 開發環境可選擇放寬限制
        if settings.debug:
            # 開發環境仍然限速，但限制更寬鬆
            limit_multiplier = 3
        else:
            limit_multiplier = 1

        client_ip = self._get_client_ip(request)
        now = time.time()
        path = request.url.path

        # 定期清理過期記錄
        self._cleanup_old_records(now)

        # 跳過健康檢查和靜態資源
        if path in ["/health", "/docs", "/redoc", "/openapi.json"] or path.startswith("/static"):
            return await call_next(request)

        # 對登入端點應用更嚴格的限制 (防止暴力破解)
        if "/auth/login" in path or "/auth/google" in path:
            login_count = self._count_requests(client_ip, now, "/auth/")
            if login_count >= self.login_limit * limit_multiplier:
                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": "登入嘗試過於頻繁，請稍後再試",
                        "retry_after": self.window_seconds
                    },
                    headers={"Retry-After": str(self.window_seconds)}
                )

        # 全局限速檢查
        total_count = self._count_requests(client_ip, now)
        if total_count >= self.requests_per_minute * limit_multiplier:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "請求過於頻繁，請稍後再試",
                    "retry_after": self.window_seconds
                },
                headers={"Retry-After": str(self.window_seconds)}
            )

        # 記錄本次請求
        self._requests[client_ip].append((now, path))

        # 添加限速標頭到響應
        response = await call_next(request)
        remaining = max(0, self.requests_per_minute * limit_multiplier - total_count - 1)
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute * limit_multiplier)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(now + self.window_seconds))

        return response


# =============================================
# H-02: 安全響應標頭中間件
# =============================================
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """添加安全響應標頭"""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        settings = get_settings()

        # 基礎安全標頭
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

        # HTTPS 相關 (僅生產環境)
        if not settings.debug:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    """應用程式生命週期管理"""
    settings = get_settings()
    # H-04: 初始化日誌系統（含敏感數據過濾）
    setup_logging(debug=settings.debug)
    # 啟動時初始化數據庫
    await init_db()
    # 啟動 Agent Team（依賴 DB 已初始化）
    from app.agents import startup_agents, shutdown_agents
    await startup_agents()
    yield
    # 關閉時清理資源
    await shutdown_agents()


def create_app() -> FastAPI:
    """創建 FastAPI 應用實例"""
    settings = get_settings()

    app = FastAPI(
        title="HKTVmall AI 營運系統",
        description="競品監測、AI 文案生成、HKTVmall 數據同步、AI 圖片生成",
        version="1.0.1",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        lifespan=lifespan,
    )

    # H-02: 添加安全標頭中間件
    app.add_middleware(SecurityHeadersMiddleware)

    # H-03: 添加全局限速中間件
    # 注意：Starlette 中間件按添加順序的逆序執行
    # 限速中間件應該在安全標頭之後、CORS 之前
    app.add_middleware(
        RateLimitMiddleware,
        requests_per_minute=60,  # 每分鐘 60 次請求
        login_limit=5,           # 登入每分鐘 5 次
    )

    # C-02: CORS 設定 - 從配置讀取允許的來源
    # 生產環境和開發環境的 CORS 來源可通過環境變數配置
    allowed_origins = settings.get_cors_origins()

    # 確保前端域名始終被允許（Zeabur 部署）
    required_origins = [
        "https://ggj-front.zeabur.app",
        "https://ggj-back.zeabur.app",
    ]
    for origin in required_origins:
        if origin not in allowed_origins:
            allowed_origins.append(origin)

    logger.info(f"CORS allowed origins: {allowed_origins}")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=["Authorization", "Content-Type", "X-Requested-With", "Accept"],
        expose_headers=["Content-Type", "X-Total-Count"],
        max_age=3600,  # 預檢請求緩存 1 小時
    )

    # 註冊標準化異常處理器
    register_exception_handlers(app)

    # 註冊 API 路由
    app.include_router(api_router, prefix="/api/v1")

    # 靜態文件服務
    static_dir = Path(__file__).parent.parent / "static"
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    # L-01: 健康檢查 - 不暴露環境信息
    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}

    return app


# 創建應用實例
app = create_app()
