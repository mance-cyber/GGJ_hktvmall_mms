# Clawdbot Gateway 部署指南（無需 VPS）

## 概述

Clawdbot Gateway 可以部署到多個**免費平台**，完全不需要購買 VPS。

## 🎯 推薦方案對比

| 平台 | 免費額度 | 優點 | 缺點 |
|------|---------|------|------|
| **Zeabur** | 5GB 流量/月 | 與現有服務同平台 | 免費額度較少 |
| **Fly.io** | 3 個 VMs 免費 | 永久免費、全球部署 | 需綁定信用卡 |
| **Render** | 750 小時/月 | 簡單易用 | 15 分鐘無活動會休眠 |
| **Railway** | $5 免費額度 | 易用、支持持久化 | 需綁定信用卡 |

---

## 方案 A：Zeabur 部署（推薦）

### 優點
- ✅ 與 GoGoJap 前後端在同一平台
- ✅ 統一管理、統一計費
- ✅ 內網通訊速度快

### 步驟

#### 1. 提交 Zeabur 配置到 Git

```bash
cd clawdbot
git add zeabur.json
git commit -m "feat: 添加 Clawdbot Gateway Zeabur 配置"
git push
```

#### 2. 在 Zeabur 創建新服務

1. 登入 [Zeabur Dashboard](https://zeabur.com/)
2. 選擇 GoGoJap 項目
3. 點擊 "Create Service" → "Git Repository"
4. 選擇你的 GitHub repo
5. **Root Directory**: `clawdbot`
6. Branch: `main`

#### 3. 設定環境變數

```bash
PORT=3000
NODE_ENV=production
CLAWDBOT_STATE_DIR=/data/.clawdbot
CLAWDBOT_WORKSPACE_DIR=/data/workspace
```

#### 4. 添加持久化存儲（重要）

1. Service Settings → Volumes
2. 添加 Volume:
   - **Name**: `clawdbot-data`
   - **Mount Path**: `/data`
   - **Size**: 1GB

#### 5. 部署並獲取 URL

部署完成後會得到：
```
https://clawdbot-xxx.zeabur.app
```

#### 6. 登入 Claude.ai 並配置

```bash
# 訪問 Gateway UI
https://clawdbot-xxx.zeabur.app

# 或使用 CLI（需先設定 endpoint）
clawdbot gateway --endpoint https://clawdbot-xxx.zeabur.app
clawdbot auth login --provider anthropic
```

#### 7. 連接到 GoGoJap Backend

修改 `backend/app/connectors/claude.py`：

```python
# 如果使用 Clawdbot Gateway
CLAWDBOT_GATEWAY_URL = os.getenv(
    "CLAWDBOT_GATEWAY_URL",
    "https://clawdbot-xxx.zeabur.app"
)
```

**Backend 環境變數**：
```bash
CLAWDBOT_GATEWAY_URL=https://clawdbot-xxx.zeabur.app
CLAWDBOT_GATEWAY_TOKEN=<從 gateway 獲取>
```

---

## 方案 B：Fly.io 部署（永久免費）

### 優點
- ✅ 完全免費（3 個 shared-cpu VMs）
- ✅ 全球 CDN
- ✅ 自動 SSL

### 步驟

#### 1. 安裝 Fly CLI

```bash
# macOS
brew install flyctl

# Linux/WSL
curl -L https://fly.io/install.sh | sh

# Windows (PowerShell)
pwsh -Command "iwr https://fly.io/install.ps1 -useb | iex"
```

#### 2. 登入 Fly.io

```bash
fly auth login
```

#### 3. 部署 Clawdbot

```bash
cd clawdbot

# 創建應用（首次）
fly launch --copy-config --no-deploy

# 設定環境變數
fly secrets set CLAUDE_SESSION_KEY=sk-ant-sid03-xxx
fly secrets set CLAUDE_ORG_ID=org-xxx

# 部署
fly deploy
```

#### 4. 查看部署狀態

```bash
fly status
fly logs
```

你會得到 URL：
```
https://clawdbot.fly.dev
```

---

## 方案 C：Render 部署（簡單）

### 優點
- ✅ 最簡單（點幾下就完成）
- ✅ 自動 SSL
- ✅ 750 小時免費

### 缺點
- ⚠️ 15 分鐘無活動會休眠
- ⚠️ 冷啟動需要 30-60 秒

### 步驟

#### 1. 提交到 Git

確保 `render.yaml` 已在 repo 中：
```bash
cd clawdbot
git add render.yaml
git commit -m "feat: Render 部署配置"
git push
```

#### 2. 連接 Render

1. 訪問 [Render Dashboard](https://render.com/)
2. 點擊 "New +" → "Blueprint"
3. 連接 GitHub repo
4. 選擇 `clawdbot` 目錄
5. Render 會自動讀取 `render.yaml`

#### 3. 設定環境變數

在 Render Dashboard 設定：
```bash
CLAUDE_SESSION_KEY=sk-ant-sid03-xxx
CLAUDE_ORG_ID=org-xxx
```

#### 4. 部署

點擊 "Deploy"，完成後得到：
```
https://clawdbot.onrender.com
```

---

## 方案 D：簡化方案 - 不用 Gateway

### 概念

**不部署獨立的 Clawdbot Gateway**，直接在 GoGoJap Backend 中整合 Session Token 認證。

### 優點
- ✅ 不需要額外服務
- ✅ 節省資源
- ✅ 簡化架構

### 缺點
- ⚠️ 需要手動提取 Session Token
- ⚠️ 無法使用 Clawdbot 的其他功能（WhatsApp/Telegram 集成等）

### 實現

已完成！參考之前的修改：
- `backend/app/connectors/claude.py` - 已支持 Session Token
- `backend/app/config.py` - 已添加環境變數

只需在 Zeabur Backend 設定：
```bash
CLAUDE_SESSION_KEY=sk-ant-sid03-xxx
CLAUDE_ORG_ID=org-xxx
```

**手動提取 Session Token**：
1. 登入 claude.ai
2. F12 → Application → Cookies
3. 複製 `sessionKey` 值

---

## 🎯 推薦選擇

### 如果你想要...

**最簡單 + 統一管理**
→ **方案 A (Zeabur)** 或 **方案 D (簡化方案)**

**完全免費 + 長期穩定**
→ **方案 B (Fly.io)**

**快速試用**
→ **方案 C (Render)**

---

## 成本對比

| 方案 | 月費 | 備註 |
|------|------|------|
| Zeabur | ~$0-5 | 免費額度內可能足夠 |
| Fly.io | $0 | 永久免費（3 VMs） |
| Render | $0 | 750 小時免費 |
| 簡化方案 | $0 | 無額外成本 |

---

## 連接 GoGoJap Backend

### 如果使用 Gateway（方案 A/B/C）

修改 `backend/app/connectors/claude.py`：

```python
import os
import httpx

class ClaudeConnector:
    def __init__(self):
        settings = get_settings()

        # 優先使用 Clawdbot Gateway
        gateway_url = os.getenv("CLAWDBOT_GATEWAY_URL")
        gateway_token = os.getenv("CLAWDBOT_GATEWAY_TOKEN")

        if gateway_url:
            self.client = self._create_gateway_client(
                gateway_url,
                gateway_token
            )
        elif settings.claude_session_key:
            self.client = self._create_session_client(
                settings.claude_session_key
            )
        else:
            self.client = anthropic.Anthropic(
                api_key=settings.anthropic_api_key
            )

    def _create_gateway_client(self, url, token):
        """通過 Clawdbot Gateway 調用"""
        return httpx.AsyncClient(
            base_url=f"{url}/v1",
            headers={"Authorization": f"Bearer {token}"}
        )
```

**Backend 環境變數（Zeabur）**：
```bash
CLAWDBOT_GATEWAY_URL=https://clawdbot-xxx.zeabur.app
CLAWDBOT_GATEWAY_TOKEN=<從 gateway 獲取>
```

### 如果使用簡化方案（方案 D）

無需修改代碼！只需設定：
```bash
CLAUDE_SESSION_KEY=sk-ant-sid03-xxx
CLAUDE_ORG_ID=org-xxx
```

---

## 驗證部署

### 檢查 Gateway 健康狀態

```bash
curl https://your-gateway-url/health
# 應返回: {"status":"ok"}
```

### 測試 Claude 認證

```bash
# 如果使用 Gateway
curl -X POST https://your-gateway-url/v1/messages \
  -H "Authorization: Bearer $CLAWDBOT_GATEWAY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-opus-4-6-20250229",
    "messages": [{"role": "user", "content": "Hello"}],
    "max_tokens": 100
  }'

# 如果使用簡化方案
# 直接測試 GoGoJap API
curl -X POST https://ggj-back.zeabur.app/api/v1/content/generate \
  -H "Authorization: Bearer <your-jwt>" \
  -H "Content-Type: application/json" \
  -d '{"product_id":"xxx"}'
```

---

## 故障排除

### Gateway 無法訪問

**症狀**: `curl: (7) Failed to connect`

**解決**:
1. 檢查服務是否正在運行
2. 檢查 Health Check 是否通過
3. 查看部署日誌

### Session Token 過期

**症狀**: `401 Unauthorized`

**解決**:
1. 重新登入 claude.ai
2. 提取新的 Session Token
3. 更新環境變數
4. 重啟服務

### Gateway 消耗太多流量

**解決**:
- 啟用 Response Caching
- 使用 CDN (Cloudflare)
- 限制請求頻率

---

## 總結

**最推薦**:
1. **簡化方案（方案 D）** - 無需額外服務，直接用 Session Token
2. **Zeabur 部署（方案 A）** - 如果需要 Gateway 的完整功能

**開始步驟**:
```bash
# 簡化方案
1. 登入 claude.ai
2. 提取 Session Token
3. 在 Zeabur Backend 設定環境變數
4. 重啟服務

# Gateway 方案
1. 選擇平台（Zeabur/Fly.io/Render）
2. 部署 Clawdbot Gateway
3. 登入並配置 Claude
4. 連接到 GoGoJap Backend
```
