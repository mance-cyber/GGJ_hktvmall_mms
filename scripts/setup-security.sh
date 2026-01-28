#!/bin/bash
# ==================== 安全配置快速設置腳本 ====================
# 用途: 自動生成 API Keys 並配置環境變量
# 使用: ./scripts/setup-security.sh

set -e

echo "🔒 開始安全配置..."
echo ""

# 1. 生成 API Key
echo "📝 生成 Scraper API Key..."
SCRAPER_API_KEY=$(openssl rand -hex 32)
echo "✅ 已生成: $SCRAPER_API_KEY"
echo ""

# 2. 檢查 .env.local 是否存在
if [ -f .env.local ]; then
  echo "⚠️  .env.local 已存在"
  read -p "是否覆蓋？(y/N): " -n 1 -r
  echo ""
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ 已取消"
    exit 1
  fi
  mv .env.local .env.local.backup
  echo "📦 舊配置已備份為 .env.local.backup"
fi

# 3. 創建 .env.local
echo "📝 創建 .env.local..."
cat > .env.local <<EOF
# ==================== Scraper API 安全配置 ====================
# 自動生成時間: $(date)

# 🔒 Scraper API Key（用於保護 /api/v1/scrape/* 端點）
SCRAPER_API_KEYS=$SCRAPER_API_KEY

# 🔧 Clawdbot 配置
CLAWDBOT_GATEWAY_URL=ws://127.0.0.1:18789

# 🔧 環境
NODE_ENV=development

# 📝 如需使用 Firecrawl（生產環境），請手動添加：
# FIRECRAWL_API_KEY=fc-your-key-here
# FIRECRAWL_API_URL=https://api.firecrawl.dev/v1
# NODE_ENV=production
EOF

echo "✅ .env.local 已創建"
echo ""

# 4. 驗證 .gitignore
if ! grep -q ".env.local" .gitignore 2>/dev/null; then
  echo "📝 添加 .env.local 到 .gitignore..."
  echo ".env.local" >> .gitignore
  echo "✅ 已添加"
else
  echo "✅ .gitignore 已包含 .env.local"
fi
echo ""

# 5. 顯示配置摘要
echo "=========================================="
echo "🎉 安全配置完成！"
echo "=========================================="
echo ""
echo "📋 配置摘要："
echo "  - API Key: ${SCRAPER_API_KEY:0:8}***${SCRAPER_API_KEY: -8}"
echo "  - 配置文件: .env.local"
echo "  - 備份文件: .env.local.backup (如有)"
echo ""
echo "📝 下一步："
echo "  1. 查看配置: cat .env.local"
echo "  2. 啟動開發服務器: npm run dev"
echo "  3. 測試 API:"
echo ""
echo "     curl -X POST http://localhost:3000/api/v1/scrape/clawdbot \\"
echo "       -H 'x-api-key: $SCRAPER_API_KEY' \\"
echo "       -H 'Content-Type: application/json' \\"
echo "       -d '{\"action\":\"scrape_product\",\"params\":{\"url\":\"https://hktvmall.com/...\"}}'"
echo ""
echo "🔒 重要提醒："
echo "  - 不要將 .env.local 提交到 Git"
echo "  - 不要在日誌中輸出完整 API Key"
echo "  - 定期輪換 API Keys"
echo ""
echo "=========================================="
