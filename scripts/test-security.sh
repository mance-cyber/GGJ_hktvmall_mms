#!/bin/bash
# ==================== 安全修復驗證測試 ====================
# 用途: 測試所有 Critical 安全修復是否正常工作
# 使用: ./scripts/test-security.sh

set -e

API_URL="${API_URL:-http://localhost:3000}"
API_KEY="${SCRAPER_API_KEYS}"

if [ -z "$API_KEY" ]; then
  echo "❌ 請先設置 SCRAPER_API_KEYS 環境變量"
  echo "提示: source .env.local"
  exit 1
fi

echo "🧪 開始安全測試..."
echo "API URL: $API_URL"
echo "API Key: ${API_KEY:0:8}***${API_KEY: -8}"
echo ""

# 測試計數器
PASSED=0
FAILED=0

# 測試函數
test_case() {
  local name="$1"
  local expected="$2"
  shift 2
  
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "🧪 測試: $name"
  echo "預期: $expected"
  echo ""
  
  if eval "$@"; then
    echo "✅ 通過"
    PASSED=$((PASSED + 1))
  else
    echo "❌ 失敗"
    FAILED=$((FAILED + 1))
  fi
  echo ""
}

# ==================== CRIT-2: 認證測試 ====================

test_case "認證測試 - 無 API Key（應該拒絕）" "401 Unauthorized" \
  'curl -s -o /dev/null -w "%{http_code}" -X POST "$API_URL/api/v1/scrape/clawdbot" | grep -q "401"'

test_case "認證測試 - 有效 API Key（應該通過）" "非 401" \
  'curl -s -o /dev/null -w "%{http_code}" -X POST "$API_URL/api/v1/scrape/clawdbot" -H "x-api-key: $API_KEY" | grep -qv "401"'

test_case "認證測試 - 無效 API Key（應該拒絕）" "401 Unauthorized" \
  'curl -s -o /dev/null -w "%{http_code}" -X POST "$API_URL/api/v1/scrape/clawdbot" -H "x-api-key: invalid_key_123" | grep -q "401"'

# ==================== CRIT-1: SSRF 防護測試 ====================

test_case "SSRF 防護 - localhost URL（應該拒絕）" "400 Bad Request" \
  'curl -s -X POST "$API_URL/api/v1/scrape/clawdbot" \
    -H "x-api-key: $API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"action\":\"scrape_product\",\"params\":{\"url\":\"http://localhost:8080\"}}" \
    | grep -q "URL 驗證失敗"'

test_case "SSRF 防護 - 私有 IP（應該拒絕）" "400 Bad Request" \
  'curl -s -X POST "$API_URL/api/v1/scrape/clawdbot" \
    -H "x-api-key: $API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"action\":\"scrape_product\",\"params\":{\"url\":\"http://192.168.1.1\"}}" \
    | grep -q "URL 驗證失敗"'

test_case "SSRF 防護 - HTTP 協議（應該拒絕）" "400 Bad Request" \
  'curl -s -X POST "$API_URL/api/v1/scrape/clawdbot" \
    -H "x-api-key: $API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"action\":\"scrape_product\",\"params\":{\"url\":\"http://hktvmall.com\"}}" \
    | grep -q "只允許 HTTPS"'

test_case "SSRF 防護 - 非白名單域名（應該拒絕）" "400 Bad Request" \
  'curl -s -X POST "$API_URL/api/v1/scrape/clawdbot" \
    -H "x-api-key: $API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"action\":\"scrape_product\",\"params\":{\"url\":\"https://evil.com\"}}" \
    | grep -q "不在白名單中"'

test_case "SSRF 防護 - 合法 URL（應該接受）" "非 400" \
  'curl -s -o /dev/null -w "%{http_code}" -X POST "$API_URL/api/v1/scrape/clawdbot" \
    -H "x-api-key: $API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"action\":\"scrape_product\",\"params\":{\"url\":\"https://hktvmall.com/p/H123_456\"}}" \
    | grep -qv "400"'

# ==================== CRIT-3: 批量限制測試 ====================

test_case "批量限制 - 超過 50 個 URL（應該拒絕）" "400 Bad Request" \
  'curl -s -X POST "$API_URL/api/v1/scrape/clawdbot" \
    -H "x-api-key: $API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"action\":\"scrape_batch\",\"params\":{\"urls\":[$(printf "\"%s\"," {1..51} | sed "s/,$//" | sed "s/[0-9]*/\"https:\/\/hktvmall.com\/p\/H\0_123\"/g")]}}" \
    | grep -q "最多支持 50 個"'

test_case "批量限制 - 50 個 URL（應該接受）" "非 400" \
  'curl -s -o /dev/null -w "%{http_code}" -X POST "$API_URL/api/v1/scrape/clawdbot" \
    -H "x-api-key: $API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"action\":\"scrape_batch\",\"params\":{\"urls\":[$(printf "\"%s\"," {1..50} | sed "s/,$//" | sed "s/[0-9]*/\"https:\/\/hktvmall.com\/p\/H\0_123\"/g")]}}" \
    | grep -qv "400"'

# ==================== 健康檢查測試 ====================

test_case "健康檢查 - GET 端點（不需要認證）" "200 OK" \
  'curl -s -o /dev/null -w "%{http_code}" -X GET "$API_URL/api/v1/scrape/clawdbot" | grep -q "200"'

test_case "健康檢查 - 返回安全配置" "包含 authRequired" \
  'curl -s -X GET "$API_URL/api/v1/scrape/clawdbot" | grep -q "authRequired"'

# ==================== 測試摘要 ====================

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 測試摘要"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✅ 通過: $PASSED"
echo "❌ 失敗: $FAILED"
echo "📊 總計: $((PASSED + FAILED))"
echo ""

if [ $FAILED -eq 0 ]; then
  echo "🎉 所有測試通過！"
  echo "✅ 安全修復驗證成功"
  exit 0
else
  echo "⚠️  有 $FAILED 個測試失敗"
  echo "請檢查配置和服務器狀態"
  exit 1
fi
