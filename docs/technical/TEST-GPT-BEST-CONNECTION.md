# GPT-Best 連接測試指南

## 🎯 測試目的

驗證 Zeabur 環境變數配置是否正確，以及 GPT-Best API 是否能成功調用 Claude 模型。

---

## 📋 測試方法（3 種）

### 方法 1：環境變數檢查（最簡單）

**不需要 API 調用，只檢查配置是否載入**

```bash
# 使用 curl 或瀏覽器訪問
curl https://ggj-back.zeabur.app/api/v1/ai/test-env-config
```

**預期響應**：
```json
{
  "status": "ready",
  "using_relay_api": true,
  "has_api_key": true,
  "config": {
    "ai_base_url": {
      "value": "https://api.gpt-best.com/v1",
      "set": true,
      "source": "環境變數 AI_BASE_URL"
    },
    "ai_api_key": {
      "value": "sk-xxxxx...xxxx",
      "set": true,
      "source": "環境變數 AI_API_KEY"
    },
    "ai_model_simple": {
      "value": "claude-haiku-4-5-20251001-thinking",
      "set": true
    },
    "ai_model_medium": {
      "value": "claude-opus-4-6-thinking",
      "set": true
    }
  },
  "recommendations": [],
  "summary": "✅ 配置完整 | 使用中轉 API"
}
```

**如果有問題**，會在 `recommendations` 中看到建議。

---

### 方法 2：Claude API 連接測試（推薦）

**會實際調用 GPT-Best API，驗證模型可用性**

```bash
# 測試 Haiku 模型（簡單任務）
curl -X POST https://ggj-back.zeabur.app/api/v1/ai/test-claude-connection \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "sk-xxxxxxxxxxxxxxxx",
    "base_url": "https://api.gpt-best.com/v1",
    "model": "claude-haiku-4-5-20251001-thinking"
  }'
```

**成功響應**：
```json
{
  "valid": true,
  "message": "✅ Claude API 連接成功！",
  "model": "claude-haiku-4-5-20251001-thinking",
  "response": "你好！很高興認識你。",
  "tokens": {
    "input": 12,
    "output": 8,
    "total": 20
  }
}
```

**測試 Opus 模型**（中高階任務）：
```bash
curl -X POST https://ggj-back.zeabur.app/api/v1/ai/test-claude-connection \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "sk-xxxxxxxxxxxxxxxx",
    "base_url": "https://api.gpt-best.com/v1",
    "model": "claude-opus-4-6-thinking"
  }'
```

---

### 方法 3：通過前端測試（最直觀）

1. 訪問 GoGoJap 後台：https://ggj-front.zeabur.app
2. 登入系統
3. 進入「商品管理」
4. 選擇任一商品
5. 點擊「AI 文案生成」
6. 查看是否成功生成內容

**成功標誌**：
- 生成的文案出現在畫面上
- 沒有錯誤提示
- 日誌中顯示使用的模型名稱

---

## 🔍 Zeabur 日誌檢查

### 查看啟動日誌

1. 登入 Zeabur Dashboard
2. 選擇 GoGoJap Backend 服務
3. 點擊「Logs」標籤

**正確配置的日誌範例**：
```
[INFO] Starting GoGoJap Backend...
[INFO] Environment: production
[INFO] AI Configuration:
  - Base URL: https://api.gpt-best.com/v1
  - API Key: sk-****...****
  - Simple Model: claude-haiku-4-5-20251001-thinking
  - Medium Model: claude-opus-4-6-thinking
  - Complex Model: claude-opus-4-6-thinking
[INFO] ✅ AI Config loaded successfully
```

### 查看 API 調用日誌

當你使用 AI 功能時，日誌應顯示：
```
[INFO] AI Call Started
  - Model: claude-haiku-4-5-20251001-thinking
  - Task: generate_content
  - Complexity: SIMPLE
[INFO] AI Call Completed
  - Input Tokens: 245
  - Output Tokens: 120
  - Total: 365
  - Cost: ¥0.003 (estimated)
```

---

## ❌ 常見錯誤與解決

### 錯誤 1：401 Unauthorized

**症狀**：
```json
{
  "valid": false,
  "error": "❌ API Key 無效或已過期",
  "status_code": 401
}
```

**解決**：
1. 登入 GPT-Best 平台檢查 API Key 是否正確
2. 確認帳戶餘額充足
3. 重新生成 API Key
4. 更新 Zeabur 環境變數 `AI_API_KEY`

---

### 錯誤 2：404 Not Found

**症狀**：
```json
{
  "valid": false,
  "error": "❌ 端點不存在",
  "status_code": 404,
  "hint": "正確格式例如：https://api.gpt-best.com/v1"
}
```

**解決**：
1. 檢查 `AI_BASE_URL` 是否包含 `/v1`
2. 確認 Base URL 格式：
   - ✅ `https://api.gpt-best.com/v1`
   - ❌ `https://api.gpt-best.com`
   - ❌ `https://gpt-best.apifox.cn`

---

### 錯誤 3：Model not found

**症狀**：
```json
{
  "valid": false,
  "error": "❌ 請求錯誤: model 'xxx' not found",
  "status_code": 400,
  "hint": "可能原因：模型 'xxx' 不存在或不可用"
}
```

**解決**：
1. 登入 GPT-Best 平台
2. 查看「模型列表」頁面
3. 確認實際可用的模型名稱
4. 更新環境變數為正確的模型名稱：

如果 thinking 模式不可用，改用標準版本：
```bash
AI_MODEL_SIMPLE=claude-3-5-haiku
AI_MODEL_MEDIUM=claude-3-5-sonnet
AI_MODEL_COMPLEX=claude-opus-4
```

---

### 錯誤 4：Connection Timeout

**症狀**：
```json
{
  "valid": false,
  "error": "❌ 連接超時（60秒）"
}
```

**解決**：
1. 檢查網絡連接
2. 確認 GPT-Best 服務狀態
3. 嘗試在瀏覽器直接訪問 Base URL
4. 聯繫 GPT-Best 技術支持

---

## 🧪 完整測試流程（推薦順序）

### Step 1：環境變數檢查
```bash
curl https://ggj-back.zeabur.app/api/v1/ai/test-env-config
```
✅ 確認 `status: "ready"` 且 `using_relay_api: true`

### Step 2：測試 Haiku 模型
```bash
curl -X POST https://ggj-back.zeabur.app/api/v1/ai/test-claude-connection \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "<your-api-key>",
    "base_url": "https://api.gpt-best.com/v1",
    "model": "claude-haiku-4-5-20251001-thinking"
  }'
```
✅ 確認 `valid: true` 且返回 AI 響應

### Step 3：測試 Opus 模型
```bash
curl -X POST https://ggj-back.zeabur.app/api/v1/ai/test-claude-connection \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "<your-api-key>",
    "base_url": "https://api.gpt-best.com/v1",
    "model": "claude-opus-4-6-thinking"
  }'
```
✅ 確認 `valid: true` 且返回 AI 響應

### Step 4：前端實際測試
1. 訪問前端系統
2. 生成一段 AI 文案
3. 檢查是否成功

---

## 📊 成本監控

每次測試調用會消耗少量 tokens：
- 測試調用：~20-50 tokens（約 ¥0.001）
- 文案生成：~500-1000 tokens（約 ¥0.01-0.02）

**建議**：
- 測試時使用 Haiku 模型（成本最低）
- 測試完成後記錄 token 使用量
- 定期檢查 GPT-Best 平台的用量報告

---

## 🎯 驗證清單

完整測試通過標準：

- [ ] 環境變數檢查顯示 `status: "ready"`
- [ ] Haiku 模型連接成功（`valid: true`）
- [ ] Opus 模型連接成功（`valid: true`）
- [ ] Token 使用量正常顯示
- [ ] 前端 AI 文案生成功能正常
- [ ] Zeabur 日誌無錯誤信息

---

## 🔗 相關文檔

- [GPT-Best 配置指南](./GPT-BEST-CONFIG.md)
- [多模型分級策略](./MULTI-MODEL-STRATEGY.md)
- [成本優化指南](./COST-OPTIMIZATION.md)

---

## 💡 測試技巧

### 快速測試腳本

創建 `test-gpt-best.sh`：
```bash
#!/bin/bash

API_KEY="sk-xxxxxxxxxxxxxxxx"
BASE_URL="https://api.gpt-best.com/v1"
BACKEND="https://ggj-back.zeabur.app"

echo "🔍 Step 1: 檢查環境變數..."
curl -s "$BACKEND/api/v1/ai-settings/test-env-config" | jq .

echo ""
echo "🧪 Step 2: 測試 Haiku 模型..."
curl -s -X POST "$BACKEND/api/v1/ai-settings/test-claude-connection" \
  -H "Content-Type: application/json" \
  -d "{\"api_key\":\"$API_KEY\",\"base_url\":\"$BASE_URL\",\"model\":\"claude-haiku-4-5-20251001-thinking\"}" | jq .

echo ""
echo "🧪 Step 3: 測試 Opus 模型..."
curl -s -X POST "$BACKEND/api/v1/ai-settings/test-claude-connection" \
  -H "Content-Type: application/json" \
  -d "{\"api_key\":\"$API_KEY\",\"base_url\":\"$BASE_URL\",\"model\":\"claude-opus-4-6-thinking\"}" | jq .

echo ""
echo "✅ 測試完成！"
```

使用方式：
```bash
chmod +x test-gpt-best.sh
./test-gpt-best.sh
```

---

## 📞 需要幫助？

如果測試仍有問題：

1. **GPT-Best 平台**：
   - 查看平台文檔
   - 聯繫客服支持

2. **GoGoJap 系統**：
   - 檢查 Zeabur 日誌
   - 查看 GitHub Issues
   - 參考技術文檔

3. **緊急處理**：
   - 切換回官方 Anthropic API（移除 `AI_BASE_URL` 環境變數）
   - 使用單一模型而非分級策略
