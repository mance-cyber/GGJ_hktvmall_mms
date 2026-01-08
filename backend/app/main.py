# =============================================
# FastAPI 應用入口
# =============================================

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.config import get_settings
from app.models.database import init_db
from app.api.v1.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """應用程式生命週期管理"""
    # 啟動時初始化數據庫
    await init_db()
    yield
    # 關閉時清理資源


def create_app() -> FastAPI:
    """創建 FastAPI 應用實例"""
    settings = get_settings()

    app = FastAPI(
        title="HKTVmall AI 營運系統",
        description="競品監測、AI 文案生成、HKTVmall 數據同步",
        version="1.0.0",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        lifespan=lifespan,
    )

    # CORS 設定
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.debug else ["https://your-domain.com"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 註冊 API 路由
    app.include_router(api_router, prefix="/api/v1")

    # 靜態文件服務
    static_dir = Path(__file__).parent.parent / "static"
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    # 健康檢查
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "env": settings.app_env}

    return app


# 創建應用實例
app = create_app()
