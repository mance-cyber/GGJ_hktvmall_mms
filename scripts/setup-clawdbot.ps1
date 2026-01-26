# ==================== GoGoJap Clawdbot 部署腳本 (PowerShell) ====================
# 用途: 在 Windows 上部署 clawdbot 作為主要抓取引擎
# 作者: GoGoJap 開發團隊
# 版本: 1.0

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  GoGoJap Clawdbot 部署腳本" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 配置變量
$CLAWDBOT_DIR = ".\clawdbot"
$CLAWDBOT_REPO = "https://github.com/clawdbot/clawdbot.git"
$NODE_VERSION = 22

# ==================== 檢查環境 ====================

Write-Host "[1/6] 檢查系統環境..." -ForegroundColor Yellow
Write-Host ""

# 檢查 Node.js
try {
    $nodeVersion = node -v
    $nodeVersionNumber = [int]($nodeVersion -replace 'v(\d+)\..*', '$1')

    if ($nodeVersionNumber -lt $NODE_VERSION) {
        Write-Host "❌ Node.js 版本過低 (當前: $nodeVersion, 需要: >= v$NODE_VERSION)" -ForegroundColor Red
        Write-Host "請從這裡下載: https://nodejs.org/" -ForegroundColor Yellow
        exit 1
    }

    Write-Host "✅ Node.js 版本: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js 未安裝" -ForegroundColor Red
    Write-Host "請從這裡下載: https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}

# 檢查 pnpm
try {
    $pnpmVersion = pnpm -v
    Write-Host "✅ pnpm 版本: $pnpmVersion" -ForegroundColor Green
} catch {
    Write-Host "⚙️  正在安裝 pnpm..." -ForegroundColor Yellow
    npm install -g pnpm
    Write-Host "✅ pnpm 安裝完成" -ForegroundColor Green
}

# 檢查 Git
try {
    $gitVersion = git --version
    Write-Host "✅ $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Git 未安裝" -ForegroundColor Red
    Write-Host "請從這裡下載: https://git-scm.com/" -ForegroundColor Yellow
    exit 1
}

# ==================== 克隆 Clawdbot ====================

Write-Host ""
Write-Host "[2/6] 下載 clawdbot..." -ForegroundColor Yellow
Write-Host ""

if (Test-Path $CLAWDBOT_DIR) {
    Write-Host "⚠️  clawdbot 目錄已存在，跳過克隆" -ForegroundColor Yellow
} else {
    git clone $CLAWDBOT_REPO $CLAWDBOT_DIR
    Write-Host "✅ clawdbot 下載完成" -ForegroundColor Green
}

# ==================== 安裝依賴 ====================

Write-Host ""
Write-Host "[3/6] 安裝 clawdbot 依賴..." -ForegroundColor Yellow
Write-Host ""

Push-Location $CLAWDBOT_DIR
pnpm install
Pop-Location

Write-Host "✅ 依賴安裝完成" -ForegroundColor Green

# ==================== 配置環境變量 ====================

Write-Host ""
Write-Host "[4/6] 配置環境變量..." -ForegroundColor Yellow
Write-Host ""

$envFile = Join-Path $CLAWDBOT_DIR ".env"

if (-not (Test-Path $envFile)) {
    @"
# ==================== Clawdbot 配置 ====================

# Anthropic API Key (必填)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# OpenAI API Key (可選，如果使用 ChatGPT)
# OPENAI_API_KEY=your_openai_api_key_here

# WebSocket Gateway 端口
PORT=18789

# 日誌級別 (debug | info | warn | error)
LOG_LEVEL=info

# 瀏覽器設置
BROWSER_HEADLESS=true
BROWSER_POOL_SIZE=3

# GoGoJap 專用配置
GOGOJAP_MODE=scraping
GOGOJAP_RATE_LIMIT=30
"@ | Out-File -FilePath $envFile -Encoding UTF8

    Write-Host "✅ 已創建 .env 文件" -ForegroundColor Green
    Write-Host "⚠️  請編輯 clawdbot\.env 文件並填入你的 ANTHROPIC_API_KEY" -ForegroundColor Yellow
} else {
    Write-Host "⚠️  .env 文件已存在，跳過創建" -ForegroundColor Yellow
}

# ==================== 創建 GoGoJap Skills ====================

Write-Host ""
Write-Host "[5/6] 創建 GoGoJap 專用 Skills..." -ForegroundColor Yellow
Write-Host ""

$skillsDir = Join-Path $CLAWDBOT_DIR "skills\gogojap"
New-Item -ItemType Directory -Force -Path $skillsDir | Out-Null

# HKTVmall 商品抓取 Skill
$hktvSkill = Join-Path $skillsDir "hktv-product-scraper.md"
@"
---
name: hktv-product-scraper
description: 專門抓取 HKTVmall 商品資訊的技能
---

You are an expert web scraper specialized in extracting product data from HKTVmall (www.hktvmall.com).

Your primary responsibilities:
1. Navigate to HKTVmall product pages
2. Wait for JavaScript content to fully load
3. Extract structured product information
4. Handle anti-scraping mechanisms gracefully
5. Return data in consistent JSON format

Data fields to extract:
- name: Product title
- price: Current selling price (number)
- originalPrice: Original price before discount (number)
- discountPercent: Discount percentage (number)
- stockStatus: Stock availability status (string)
- imageUrl: Main product image URL
- sku: Product SKU
- brand: Brand name
- rating: Average rating (number)
- reviewCount: Number of reviews (number)
- promotionText: Promotional text if any
- description: Product description

Scraping strategy:
1. Use browser.goto() to load the product page
2. Wait for selector .product-details to ensure page loaded
3. Check for "Show More" buttons and click if needed
4. Scroll to load lazy-loaded content
5. Extract data using CSS selectors
6. Handle missing fields gracefully (return null)
7. Return structured JSON

Rate limiting:
- Wait 2-3 seconds between requests
- Randomize wait times to appear more human-like
- Respect robots.txt

Error handling:
- If page fails to load, retry up to 3 times
- If specific field is missing, return null for that field
- Log errors but continue execution
- Return partial data if some fields are unavailable

Example output format:
{
  "success": true,
  "url": "https://www.hktvmall.com/...",
  "data": {
    "name": "日本零食套裝",
    "price": 99.00,
    "originalPrice": 129.00,
    "discountPercent": 23,
    "stockStatus": "in_stock",
    "imageUrl": "https://...",
    "sku": "ABC123",
    "brand": "日本品牌",
    "rating": 4.5,
    "reviewCount": 128,
    "promotionText": "買一送一",
    "description": "..."
  },
  "scrapedAt": "2026-01-26T10:30:00Z"
}
"@ | Out-File -FilePath $hktvSkill -Encoding UTF8

# SEO 排名追蹤 Skill
$seoSkill = Join-Path $skillsDir "seo-rank-tracker.md"
@"
---
name: seo-rank-tracker
description: 追蹤 HKTVmall 站內搜尋和 Google 搜尋排名
---

You are an SEO ranking tracker specialized in monitoring product positions in search results.

Your primary responsibilities:
1. Search for specific keywords on HKTVmall
2. Search for specific keywords on Google Hong Kong
3. Identify target product's ranking position
4. Extract competitor information
5. Return structured ranking data

Search platforms:
- HKTVmall site search: https://www.hktvmall.com/search?q={keyword}
- Google Hong Kong: https://www.google.com.hk/search?q={keyword}+site:hktvmall.com

Data to extract:
- keyword: Search keyword used
- platform: "hktvmall" or "google"
- targetUrl: URL of the product being tracked
- currentRank: Current ranking position (1-100)
- totalResults: Total number of search results
- topCompetitors: Array of top 10 results
- serpFeatures: SERP features present
- timestamp: When the search was performed

Example output:
{
  "success": true,
  "keyword": "日本零食",
  "platform": "hktvmall",
  "targetUrl": "https://www.hktvmall.com/...",
  "currentRank": 5,
  "totalResults": 234,
  "topCompetitors": [...],
  "scrapedAt": "2026-01-26T10:30:00Z"
}
"@ | Out-File -FilePath $seoSkill -Encoding UTF8

Write-Host "✅ GoGoJap Skills 創建完成" -ForegroundColor Green

# ==================== 創建啟動腳本 ====================

Write-Host ""
Write-Host "[6/6] 創建啟動腳本..." -ForegroundColor Yellow
Write-Host ""

@"
@echo off
echo 啟動 Clawdbot Gateway...
cd clawdbot
pnpm start
"@ | Out-File -FilePath "start-clawdbot.bat" -Encoding ASCII

Write-Host "✅ 啟動腳本創建完成" -ForegroundColor Green

# ==================== 完成 ====================

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  ✅ Clawdbot 部署完成！" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "下一步操作:" -ForegroundColor Yellow
Write-Host "1. 編輯 clawdbot\.env 文件，填入你的 ANTHROPIC_API_KEY" -ForegroundColor White
Write-Host "2. 運行 start-clawdbot.bat 啟動 clawdbot" -ForegroundColor White
Write-Host "3. 驗證 WebSocket Gateway 運行於 ws://localhost:18789" -ForegroundColor White
Write-Host "4. 繼續整合 GoGoJap 與 clawdbot" -ForegroundColor White
Write-Host ""
