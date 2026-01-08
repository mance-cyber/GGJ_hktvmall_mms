# Zeabur 部署指南

> 5 分鐘將 GoGoJap 部署到 Zeabur 雲端

---

## 前置準備

1. GitHub 帳號（代碼已推送到 GitHub）
2. [Zeabur 帳號](https://zeabur.com)（用 GitHub 登入）
3. 以下 API Keys：
   - `ANTHROPIC_API_KEY` - Claude AI（必需）
   - `FIRECRAWL_API_KEY` - 網頁爬蟲（可選）
   - `HKTVMALL_ACCESS_TOKEN` - HKTVmall API（可選）

---

## 部署步驟

### Step 1：創建 Project

1. 登入 [Zeabur Dashboard](https://dash.zeabur.com)
2. 點擊 **Create Project**
3. 選擇 Region: **Hong Kong** 或 **Singapore**（推薦香港，連 HKTVmall 更快）

### Step 2：部署 PostgreSQL

1. 點擊 **+ Create Service**
2. 選擇 **Marketplace**
3. 搜尋並選擇 **PostgreSQL**
4. 等待部署完成（約 30 秒）

### Step 3：部署 Redis

1. 點擊 **+ Create Service**
2. 選擇 **Marketplace**
3. 搜尋並選擇 **Redis**
4. 等待部署完成（約 30 秒）

### Step 4：部署 Backend

1. 點擊 **+ Create Service**
2. 選擇 **Git**
3. 授權並選擇你的 GitHub Repo
4. **Root Directory**: 輸入 `backend`
5. Zeabur 會自動偵測到 Dockerfile 並開始構建

#### 設置環境變數

在 Backend Service 的 **Variables** 頁面添加：

```env
# 必需
SECRET_KEY=<使用 openssl rand -hex 32 生成>
ANTHROPIC_API_KEY=sk-ant-xxx

# 可選（開發階段可以先跳過）
FIRECRAWL_API_KEY=fc-xxx
HKTVMALL_ACCESS_TOKEN=xxx
HKTVMALL_STORE_CODE=xxx
HKTV_CONNECTOR_TYPE=mock
```

**注意**：`DATABASE_URL` 和 `REDIS_URL` 會由 Zeabur 自動注入，無需手動設置！

#### 綁定數據庫

1. 在 Backend Service 頁面，點擊 **Bind**
2. 選擇剛才創建的 **PostgreSQL** 服務
3. 選擇剛才創建的 **Redis** 服務

### Step 5：部署 Frontend

1. 點擊 **+ Create Service**
2. 選擇 **Git**
3. 選擇同一個 GitHub Repo
4. **Root Directory**: 輸入 `frontend`
5. Zeabur 會自動偵測到 Dockerfile 並開始構建

#### 設置環境變數

在 Frontend Service 的 **Variables** 頁面添加：

```env
NEXT_PUBLIC_API_URL=https://<backend-service-name>.zeabur.app
```

**獲取 Backend URL**：
- 在 Backend Service 的 **Networking** 頁面
- 點擊 **Generate Domain**
- 複製生成的 URL

### Step 6：配置域名

#### Frontend 域名

1. 進入 Frontend Service 的 **Networking**
2. 點擊 **Generate Domain**（免費 `.zeabur.app` 域名）
3. 或者綁定自己的域名

#### Backend 域名

1. 進入 Backend Service 的 **Networking**
2. 點擊 **Generate Domain**
3. 記下這個 URL，更新到 Frontend 的 `NEXT_PUBLIC_API_URL`

---

## 部署架構圖

```
┌─────────────────────────────────────────────────────┐
│                    Zeabur Project                   │
│  Region: Hong Kong                                  │
│                                                     │
│  ┌─────────────┐      ┌─────────────┐              │
│  │  Frontend   │ ──── │   Backend   │              │
│  │  (Next.js)  │      │  (FastAPI)  │              │
│  │  :3000      │      │  :8000      │              │
│  └─────────────┘      └──────┬──────┘              │
│                              │                      │
│         ┌────────────────────┼────────────────┐    │
│         │                    │                │    │
│  ┌──────┴──────┐      ┌──────┴──────┐        │    │
│  │  PostgreSQL │      │    Redis    │        │    │
│  │  (Database) │      │   (Cache)   │        │    │
│  └─────────────┘      └─────────────┘        │    │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 常見問題

### Q: 構建失敗怎麼辦？

1. 檢查 **Logs** 頁面的錯誤訊息
2. 確保 `Root Directory` 設置正確（`backend` 或 `frontend`）
3. 確保代碼已推送到 GitHub

### Q: Backend 無法連接數據庫？

1. 確認已 **Bind** PostgreSQL 服務
2. 不要手動設置 `DATABASE_URL`，讓 Zeabur 自動注入

### Q: Frontend 無法連接 Backend？

1. 確認 `NEXT_PUBLIC_API_URL` 設置正確
2. 確認 Backend 已部署成功且有公開域名
3. 檢查 Backend 的 CORS 設置

### Q: 如何查看日誌？

1. 點擊對應服務
2. 選擇 **Logs** 頁面
3. 可以選擇 Build Logs 或 Runtime Logs

### Q: 如何重新部署？

1. 推送新代碼到 GitHub，Zeabur 會自動重新部署
2. 或者在服務頁面點擊 **Redeploy**

---

## 費用估算

| 項目 | 免費額度 | 超出後 |
|------|---------|--------|
| 計算資源 | ~$5 USD/月 | 按用量計費 |
| PostgreSQL | 包含在額度 | 按用量 |
| Redis | 包含在額度 | 按用量 |
| 帶寬 | 100GB/月 | $0.1/GB |

**開發環境通常免費額度足夠使用！**

---

## 下一步

部署成功後：

1. 訪問 Frontend URL 測試系統
2. 訪問 Backend URL `/docs` 查看 API 文檔
3. 如果一切正常，開始配置 HKTVmall API 等服務

---

## 本地開發

如果需要本地開發並連接 Zeabur 數據庫：

```bash
# 從 Zeabur Dashboard 複製 PostgreSQL 連接字串
export DATABASE_URL="postgresql://..."

# 啟動本地後端
cd backend
uvicorn app.main:app --reload

# 啟動本地前端
cd frontend
npm run dev
```

---

**有問題？** 查看 [Zeabur 官方文檔](https://zeabur.com/docs) 或在 Dashboard 提交 Support Ticket。
