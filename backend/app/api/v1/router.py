# =============================================
# API 路由聚合
# =============================================

from fastapi import APIRouter

from app.api.v1 import (
    competitors, products, content, analytics, scrape, categories,
    telegram, market_response, ai_settings, agent, agent_team, hktvmall,
    pricing, orders, inbox, finance, promotions, auth, image_generation,
    price_trends, seo, geo, content_pipeline, seo_ranking, roi, workflow
)

api_router = APIRouter()

# 認證
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["認證"]
)

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

# Agent Team Dashboard
api_router.include_router(
    agent_team.router,
    prefix="/agent-team",
    tags=["Agent Team"]
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
    prefix="/pricing",
    tags=["智能定價"]
)

# 訂單管理
api_router.include_router(
    orders.router,
    prefix="/orders",
    tags=["訂單管理"]
)

# 客服收件箱
api_router.include_router(
    inbox.router,
    prefix="/inbox",
    tags=["客服收件箱"]
)

# 財務管理
api_router.include_router(
    finance.router,
    prefix="/finance",
    tags=["財務管理"]
)

# 智能推廣
api_router.include_router(
    promotions.router,
    prefix="/promotions",
    tags=["智能推廣"]
)

# 圖片生成
api_router.include_router(
    image_generation.router,
    prefix="/image-generation",
    tags=["圖片生成"]
)

# 價格趨勢
api_router.include_router(
    price_trends.router,
    prefix="/price-trends",
    tags=["價格趨勢"]
)

# SEO 優化
api_router.include_router(
    seo.router,
    prefix="/seo",
    tags=["SEO 優化"]
)

# GEO 結構化數據
api_router.include_router(
    geo.router,
    prefix="/geo",
    tags=["GEO 結構化數據"]
)

# 統一內容生成流水線
api_router.include_router(
    content_pipeline.router,
    prefix="/content-pipeline",
    tags=["內容生成流水線"]
)

# SEO 排名追蹤
api_router.include_router(
    seo_ranking.router,
    prefix="/seo-ranking",
    tags=["SEO 排名追蹤"]
)

# ROI 分析
api_router.include_router(
    roi.router,
    prefix="/roi",
    tags=["ROI 分析"]
)

# 工作流自動化
api_router.include_router(
    workflow.router,
    tags=["工作流自動化"]
)
