# Claude OAuth 認證設定指南

## 概述

GoGoJap 系統現已支持兩種 Claude AI 認證方式：

| 認證方式 | 用途 | 優點 | 缺點 |
|---------|------|------|------|
| **API Key** | 官方 API Console | 穩定、官方支援 | 按 Token 計費 |
| **Session Token** | Claude.ai Pro/Max 訂閱 | 使用訂閱額度、免費 | 非官方、可能不穩定 |

---

## 方法 1：API Key 認證（推薦）

### 步驟

1. **申請 API Key**
   - 訪問：https://console.anthropic.com/
   - 創建 API Key（格式：`sk-ant-api03-xxxxx`）

2. **設定環境變數（Zeabur）**
   ```bash
   ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxx
   AI_MODEL=claude-opus-4-6-20250229
   ```

3. **重啟服務**
   - Zeabur 會自動重新部署

---

## 方法 2：Session Token 認證（Claude Pro/Max 訂閱）

### 前置條件

- ✅ 擁有 Claude Pro 或 Claude Max 訂閱
- ✅ 已登入 claude.ai

### 步驟 A：手動提取 Session Token

1. **登入 Claude.ai**
   ```
   https://claude.ai/
   ```

2. **打開瀏覽器開發者工具**
   - Chrome/Edge: `F12` 或 `Ctrl+Shift+I`
   - Safari: `Cmd+Option+I`

3. **提取 Session Token**
   ```
   Application → Cookies → https://claude.ai
   找到 `sessionKey`，複製其值
   ```

4. **提取 Organization ID**
   ```
   Application → Local Storage → https://claude.ai
   找到 `lastActiveOrg`，複製其值
   ```

5. **設定環境變數（Zeabur）**
   ```bash
   CLAUDE_SESSION_KEY=sk-ant-sid03-xxxxx
   CLAUDE_ORG_ID=org-xxxxx
   ```

### 步驟 B：使用 Clawdbot CLI（自動化）

1. **安裝 Clawdbot**
   ```bash
   cd clawdbot
   npm install -g clawdbot@latest
   ```

2. **登入 Claude.ai**
   ```bash
   clawdbot auth login --provider anthropic
   ```

   這會打開瀏覽器，登入後自動提取 Session Token

3. **查看憑證**
   ```bash
   clawdbot auth list
   ```

4. **複製到 Zeabur 環境變數**
   ```bash
   CLAUDE_SESSION_KEY=<從 clawdbot 獲取>
   CLAUDE_ORG_ID=<從 clawdbot 獲取>
   ```

---

## 安裝所需套件（如果使用 Session Token）

### 方法 A：使用 claude-api（Python）

```bash
cd backend
pip install claude-api
```

**添加到 requirements.txt**：
```
claude-api>=2.0.0
```

### 方法 B：使用 Clawdbot Gateway（推薦）

不需要修改後端代碼，通過 Clawdbot Gateway 作為代理：

```bash
# 1. 啟動 Clawdbot Gateway
cd clawdbot
clawdbot gateway --port 18789

# 2. 修改 GoGoJap 後端 API 端點
# 將 https://api.anthropic.com
# 改為 http://localhost:18789/v1
```

---

## 認證優先級

系統會按以下順序檢查：

1. **Session Token** (`CLAUDE_SESSION_KEY`) - 如果設定
2. **API Key** (`ANTHROPIC_API_KEY`) - 回退選項
3. **Mock 模式** - 無任何認證時返回模擬數據

---

## 驗證設定

### 測試 API Key

```bash
curl -X POST https://ggj-back.zeabur.app/api/v1/content/generate \
  -H "Authorization: Bearer <your-jwt-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "xxx",
    "tone": "professional"
  }'
```

### 測試 Session Token

檢查後端日誌：
```bash
# 應該看到
[INFO] Using Claude Session Token authentication
[INFO] Model: claude-opus-4-6-20250229
```

---

## 注意事項

### ⚠️ Session Token 風險

1. **違反服務條款**
   - Anthropic 官方不支持此方式
   - 可能導致帳號被封禁

2. **不穩定**
   - Session Token 會過期（通常 30-90 天）
   - Claude.ai 內部 API 可能隨時變更

3. **無官方支援**
   - 出問題無法聯繫 Anthropic 技術支持

### ✅ 最佳實踐

- **生產環境**：使用 API Key
- **開發/測試**：可使用 Session Token
- **定期更新** Session Token（設提醒）
- **監控使用情況**（避免超出訂閱限制）

---

## 成本對比

| 方式 | Claude Pro | Claude Max | API Key |
|-----|-----------|-----------|---------|
| **月費** | $20 USD | $60 USD | 按用量 |
| **每日請求** | ~100 次 | ~200 次 | 無限制 |
| **模型** | Opus 4.5/4.6 | Opus 4.5/4.6 | 所有模型 |
| **Context** | 最高 200K | 最高 500K | 視模型 |
| **適合** | 個人輕度使用 | 個人重度使用 | 商業生產 |

---

## 故障排除

### Session Token 無效

**症狀**：
```
[ERROR] Authentication failed: Invalid session token
```

**解決**：
1. 重新登入 claude.ai
2. 提取新的 Session Token
3. 更新 Zeabur 環境變數

### API Key 配額不足

**症狀**：
```
[ERROR] Rate limit exceeded
```

**解決**：
1. 檢查 Anthropic Console 的用量
2. 升級 API 配額
3. 或切換到 Session Token

---

## 參考資料

- [Anthropic API 文檔](https://docs.anthropic.com/claude/reference)
- [Clawdbot 文檔](https://docs.clawd.bot/)
- [Claude.ai](https://claude.ai/)
- [API Console](https://console.anthropic.com/)
