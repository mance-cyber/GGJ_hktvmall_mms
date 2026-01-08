# =============================================
# API 路由聚合
# =============================================

from fastapi import APIRouter

from app.api.v1 import competitors, products, content, analytics, scrape, categories, telegram, market_response, ai_settings, agent, hktvmall, pricing

api_router = APIRouter()

# 競品監測
api_router.include_router(
    competitors.router,
    prefix="/competitors",
    tags=["競品監測"]
)

# 警報
api_router.include_router(
    competitors.alerts_router,
    prefix="/alerts",
    tags=["警報"]
)

# 商品管理
api_router.include_router(
    products.router,
    prefix="/products",
    tags=["商品管理"]
)

# AI 內容
api_router.include_router(
    content.router,
    prefix="/content",
    tags=["AI 內容"]
)

# 分析/Dashboard
api_router.include_router(
    analytics.router,
    tags=["分析"]
)

# 數據抓取
api_router.include_router(
    scrape.router,
    prefix="/scrape",
    tags=["數據抓取"]
)

# 類別數據庫
api_router.include_router(
    categories.router,
    prefix="/categories",
    tags=["類別數據庫"]
)

# Telegram 通知管理
api_router.include_router(
    telegram.router,
    prefix="/telegram",
    tags=["Telegram 通知"]
)

# Market Response Center (MRC) 市場應對中心
api_router.include_router(
    market_response.router,
    prefix="/mrc",
    tags=["市場應對中心"]
)

# AI 設定與分析
api_router.include_router(
    ai_settings.router,
    prefix="/ai",
    tags=["AI 設定與分析"]
)

# AI Agent 對話
api_router.include_router(
    agent.router,
    prefix="/agent",
    tags=["AI Agent 對話"]
)

# HKTVmall 集成
api_router.include_router(
    hktvmall.router,
    prefix="/hktvmall",
    tags=["HKTVmall 集成"]
)

# 智能定價
api_router.include_router(
    pricing.router,
    prefix="/pricing",  # Final URL: /api/v1/pricing/...
    tags=["智能定價"]
)
