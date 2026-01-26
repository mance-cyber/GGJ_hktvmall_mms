# Clawdbot 快速啟動指南

## 🎯 目標
將 clawdbot 作為 GoGoJap 的主要抓取引擎，運行 WebSocket Gateway 供 GoGoJap 調用。

---

## ⚙️ 配置步驟

### 步驟 1: 配置 Anthropic API Key

你需要在兩個地方配置 API Key：

#### 方式 A: 使用 clawdbot 配置系統 (推薦)

```bash
cd clawdbot
node scripts/run-node.mjs config set ANTHROPIC_API_KEY sk-ant-api03-你的密鑰
```

#### 方式 B: 編輯 .env 文件

編輯 `clawdbot\.env`:
```env
ANTHROPIC_API_KEY=sk-ant-api03-你的密鑰
```

💡 **獲取 API Key**: https://console.anthropic.com/

---

## 🚀 啟動 Clawdbot Gateway

### 標準啟動 (用於 GoGoJap)

```bash
cd clawdbot
node scripts/run-node.mjs gateway --port 18789
```

**預期輸出**:
```
✅ Gateway running on ws://127.0.0.1:18789
🔧 Browser pool initialized
📊 Skills loaded
```

### 常用選項

```bash
# 強制啟動 (殺死占用端口的進程)
node scripts/run-node.mjs gateway --port 18789 --force

# 開發模式 (不同端口，隔離狀態)
node scripts/run-node.mjs --dev gateway

# 查看日誌
node scripts/run-node.mjs logs --follow
```

---

## 🧪 測試 Clawdbot

### 測試 1: 檢查健康狀態

新終端窗口運行:
```bash
cd clawdbot
node scripts/run-node.mjs health
```

預期輸出:
```json
{
  "status": "ok",
  "gateway": "running",
  "port": 18789
}
```

### 測試 2: 測試瀏覽器

```bash
node scripts/run-node.mjs browser status
```

### 測試 3: GoGoJap 整合測試

1. **確保 Clawdbot Gateway 正在運行**
   ```bash
   # 終端 1
   cd clawdbot
   node scripts/run-node.mjs gateway --port 18789
   ```

2. **啟動 GoGoJap**
   ```bash
   # 終端 2
   cd ..
   npm run dev
   ```

3. **打開測試頁面**
   ```
   http://localhost:3000/scrape/clawdbot-test
   ```

4. **驗證連接**
   - 頁面應該顯示 "Clawdbot 服務狀態: 已連接" (綠色)

5. **測試抓取**
   - 輸入任意 HKTVmall 商品 URL
   - 點擊 "開始抓取"
   - 查看結果

---

## 📊 完整架構

```
┌─────────────────────────────────────────┐
│  GoGoJap Frontend                       │
│  http://localhost:3000                  │
│  └─ /scrape/clawdbot-test               │
└────────────┬────────────────────────────┘
             │ HTTP API
             ▼
┌─────────────────────────────────────────┐
│  GoGoJap Backend                        │
│  POST /api/v1/scrape/clawdbot           │
│  └─ ClawdbotConnector                   │
└────────────┬────────────────────────────┘
             │ WebSocket
             ▼
┌─────────────────────────────────────────┐
│  Clawdbot Gateway                       │
│  ws://127.0.0.1:18789                   │
│  ├─ Browser Pool (3 instances)          │
│  ├─ Skills: hktv-product-scraper        │
│  └─ Skills: seo-rank-tracker            │
└────────────┬────────────────────────────┘
             │ HTTPS
             ▼
┌─────────────────────────────────────────┐
│  目標網站                                │
│  - HKTVmall.com                         │
│  - Google.com.hk                        │
└─────────────────────────────────────────┘
```

---

## 🔍 故障排除

### 問題 1: Gateway 無法啟動

**症狀**: `EADDRINUSE: address already in use`

**解決**:
```bash
# 方式 1: 使用 --force 標誌
node scripts/run-node.mjs gateway --port 18789 --force

# 方式 2: 手動殺死進程
# Windows
netstat -ano | findstr :18789
taskkill /PID [PID號] /F

# Linux/Mac
lsof -ti:18789 | xargs kill -9
```

### 問題 2: API Key 錯誤

**症狀**: `Invalid API key` 或 `Authentication failed`

**解決**:
1. 檢查 API Key 是否正確
2. 確認 API Key 有餘額
3. 重新設置:
   ```bash
   node scripts/run-node.mjs config set ANTHROPIC_API_KEY sk-ant-api03-新密鑰
   ```

### 問題 3: GoGoJap 顯示 "未連接"

**檢查清單**:
- [ ] Clawdbot Gateway 是否正在運行？
- [ ] 端口是否為 18789？
- [ ] 防火牆是否阻止 localhost:18789？
- [ ] 查看 Clawdbot 日誌: `node scripts/run-node.mjs logs`

### 問題 4: 瀏覽器無法啟動

**解決**:
```bash
# 檢查瀏覽器狀態
node scripts/run-node.mjs browser status

# 重新初始化瀏覽器
node scripts/run-node.mjs browser reset

# 手動下載 Chromium
node scripts/run-node.mjs browser install
```

---

## 📝 常用命令速查

| 命令 | 用途 |
|-----|------|
| `node scripts/run-node.mjs gateway --port 18789` | 啟動 Gateway |
| `node scripts/run-node.mjs health` | 健康檢查 |
| `node scripts/run-node.mjs logs --follow` | 實時日誌 |
| `node scripts/run-node.mjs browser status` | 瀏覽器狀態 |
| `node scripts/run-node.mjs config get ANTHROPIC_API_KEY` | 查看 API Key |
| `node scripts/run-node.mjs doctor` | 診斷問題 |
| `node scripts/run-node.mjs status` | 查看整體狀態 |

---

## 🎯 下一步

1. ✅ 配置 API Key
2. ✅ 啟動 Gateway
3. ✅ 測試 GoGoJap 整合
4. 📊 開始抓取 HKTVmall 商品
5. 🚀 替換 Firecrawl (成本節省 83%)

---

## 💡 技巧

### 後台運行 Gateway

**Windows**:
```batch
start /B node scripts/run-node.mjs gateway --port 18789
```

**Linux/Mac**:
```bash
nohup node scripts/run-node.mjs gateway --port 18789 &
```

### 查看 Gateway 進程

**Windows**:
```batch
tasklist | findstr node
```

**Linux/Mac**:
```bash
ps aux | grep gateway
```

### 停止 Gateway

```bash
node scripts/run-node.mjs gateway stop
```

或直接 `Ctrl+C`

---

## 📚 更多資源

- **Clawdbot 官方文檔**: https://docs.clawd.bot
- **GoGoJap 整合指南**: `docs/clawdbot-implementation-guide.md`
- **API 參考**: `lib/connectors/clawdbot-connector.ts`

---

**🎉 準備好了？運行這個命令開始：**

```bash
cd clawdbot
node scripts/run-node.mjs gateway --port 18789
```

然後在另一個終端運行:
```bash
npm run dev
```

打開: http://localhost:3000/scrape/clawdbot-test
