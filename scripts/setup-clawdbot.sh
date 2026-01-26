#!/bin/bash

# ==================== GoGoJap Clawdbot 部署腳本 ====================
# 用途: 在本地部署 clawdbot 作為主要抓取引擎
# 作者: GoGoJap 開發團隊
# 版本: 1.0

set -e  # 遇到錯誤立即退出

echo "=========================================="
echo "  GoGoJap Clawdbot 部署腳本"
echo "=========================================="

# 配置變量
CLAWDBOT_DIR="./clawdbot"
CLAWDBOT_REPO="https://github.com/clawdbot/clawdbot.git"
NODE_VERSION="22"

# ==================== 檢查環境 ====================

echo ""
echo "[1/6] 檢查系統環境..."

# 檢查 Node.js 版本
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 未安裝"
    echo "請安裝 Node.js >= $NODE_VERSION: https://nodejs.org/"
    exit 1
fi

CURRENT_NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$CURRENT_NODE_VERSION" -lt "$NODE_VERSION" ]; then
    echo "❌ Node.js 版本過低 (當前: v$CURRENT_NODE_VERSION, 需要: >= v$NODE_VERSION)"
    exit 1
fi

echo "✅ Node.js 版本: $(node -v)"

# 檢查 pnpm
if ! command -v pnpm &> /dev/null; then
    echo "⚙️  安裝 pnpm..."
    npm install -g pnpm
fi

echo "✅ pnpm 版本: $(pnpm -v)"

# ==================== 克隆 Clawdbot ====================

echo ""
echo "[2/6] 下載 clawdbot..."

if [ -d "$CLAWDBOT_DIR" ]; then
    echo "⚠️  clawdbot 目錄已存在，跳過克隆"
else
    git clone "$CLAWDBOT_REPO" "$CLAWDBOT_DIR"
    echo "✅ clawdbot 下載完成"
fi

# ==================== 安裝依賴 ====================

echo ""
echo "[3/6] 安裝 clawdbot 依賴..."

cd "$CLAWDBOT_DIR"
pnpm install

echo "✅ 依賴安裝完成"

# ==================== 配置環境變量 ====================

echo ""
echo "[4/6] 配置環境變量..."

if [ ! -f ".env" ]; then
    cat > .env << 'EOF'
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
GOGOJAP_RATE_LIMIT=30  # 每分鐘最多 30 次請求
EOF

    echo "✅ 已創建 .env 文件"
    echo "⚠️  請編輯 .env 文件並填入你的 ANTHROPIC_API_KEY"
else
    echo "⚠️  .env 文件已存在，跳過創建"
fi

cd ..

# ==================== 創建 GoGoJap Skills ====================

echo ""
echo "[5/6] 創建 GoGoJap 專用 Skills..."

mkdir -p "$CLAWDBOT_DIR/skills/gogojap"

# HKTVmall 商品抓取 Skill
cat > "$CLAWDBOT_DIR/skills/gogojap/hktv-product-scraper.md" << 'EOF'
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
1. Use `browser.goto()` to load the product page
2. Wait for selector `.product-details` to ensure page loaded
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
```json
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
```
EOF

# SEO 排名追蹤 Skill
cat > "$CLAWDBOT_DIR/skills/gogojap/seo-rank-tracker.md" << 'EOF'
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
- topCompetitors: Array of top 10 results with {rank, url, title, price}
- serPfeatures: SERP features present (shopping ads, featured snippets, etc.)
- timestamp: When the search was performed

Scraping strategy:
1. Navigate to search page with keyword
2. Wait for search results to load
3. Scroll to load more results if needed
4. Find target product URL in results
5. Record its position
6. Extract top 10 competitor information
7. Return structured JSON

Anti-detection measures:
- Randomize user agent
- Add random delays between actions (2-5 seconds)
- Simulate human mouse movements
- Clear cookies between searches

Example output:
```json
{
  "success": true,
  "keyword": "日本零食",
  "platform": "hktvmall",
  "targetUrl": "https://www.hktvmall.com/...",
  "currentRank": 5,
  "totalResults": 234,
  "topCompetitors": [
    {
      "rank": 1,
      "url": "https://...",
      "title": "競品 A",
      "price": 89.00
    },
    ...
  ],
  "scrapedAt": "2026-01-26T10:30:00Z"
}
```
EOF

echo "✅ GoGoJap Skills 創建完成"

# ==================== 創建啟動腳本 ====================

echo ""
echo "[6/6] 創建啟動腳本..."

cat > start-clawdbot.sh << 'EOF'
#!/bin/bash

echo "啟動 Clawdbot Gateway..."
cd clawdbot
pnpm start
EOF

chmod +x start-clawdbot.sh

echo "✅ 啟動腳本創建完成"

# ==================== 完成 ====================

echo ""
echo "=========================================="
echo "  ✅ Clawdbot 部署完成！"
echo "=========================================="
echo ""
echo "下一步操作:"
echo "1. 編輯 clawdbot/.env 文件，填入你的 ANTHROPIC_API_KEY"
echo "2. 運行 ./start-clawdbot.sh 啟動 clawdbot"
echo "3. 驗證 WebSocket Gateway 運行於 ws://localhost:18789"
echo "4. 繼續整合 GoGoJap 與 clawdbot"
echo ""
