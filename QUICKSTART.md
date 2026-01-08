# 🚀 快速開始指南

## 開始之前

### 1. 註冊所需服務帳戶

| 服務 | 用途 | 連結 |
|------|------|------|
| **Firecrawl** | 競品爬取 | https://firecrawl.dev |
| **Anthropic** | AI 文案生成 | https://console.anthropic.com |
| **Neon** | PostgreSQL 數據庫 | https://neon.tech |
| **Zeabur** | 後端部署 | https://zeabur.com |
| **Cloudflare** | 前端 + 認證 + 儲存 | https://dash.cloudflare.com |

### 2. 安裝開發工具

```bash
# 必須
- Docker Desktop
- Node.js 18+
- Git

# 推薦
- VS Code / Cursor
- Postman / Insomnia (API 測試)
```

---

## 第一步：本地開發環境

### 1.1 Clone 項目（或建立新項目）

```bash
mkdir hktv-ops-system
cd hktv-ops-system
```

### 1.2 建立後端項目

```bash
mkdir -p backend/app/{api/v1,connectors,services,models,schemas,tasks,utils}
mkdir -p backend/alembic/versions
mkdir -p backend/tests
```

### 1.3 建立前端項目

```bash
npx create-next-app@latest frontend --typescript --tailwind --app --src-dir
cd frontend
npx shadcn@latest init
```

### 1.4 設定環境變數

```bash
# 複製環境變數範例
cp .env.example .env

# 編輯 .env 填入你的 API Keys
```

### 1.5 啟動本地服務

```bash
# 啟動 PostgreSQL + Redis
docker-compose up -d db redis

# 確認服務運行
docker-compose ps
```

---

## 第二步：開發後端

### 2.1 建立 Python 虛擬環境

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2.2 初始化數據庫

```bash
# 執行 SQL schema
psql -h localhost -U hktv -d hktv_ops -f ../schema.sql

# 或使用 Alembic
alembic upgrade head
```

### 2.3 啟動後端

```bash
# 開發模式（自動重載）
uvicorn app.main:app --reload --port 8000

# 測試 API
curl http://localhost:8000/health
```

### 2.4 啟動 Celery Worker

```bash
# 新開一個 terminal
celery -A app.tasks.celery_app worker --loglevel=info

# 新開一個 terminal（定時任務）
celery -A app.tasks.celery_app beat --loglevel=info
```

---

## 第三步：開發前端

### 3.1 安裝依賴

```bash
cd frontend
npm install
```

### 3.2 安裝 UI 組件

```bash
# 安裝常用 shadcn 組件
npx shadcn@latest add button card input table tabs dialog toast chart
```

### 3.3 啟動開發伺服器

```bash
npm run dev
# 訪問 http://localhost:3000
```

---

## 第四步：部署

### 4.1 Neon PostgreSQL

1. 登入 https://neon.tech
2. 建立新 Project（選擇 Singapore region）
3. 複製 Connection String
4. 更新 `.env` 的 `DATABASE_URL`

### 4.2 Zeabur 部署後端

```bash
# 1. 登入 Zeabur
# 2. 建立新 Project
# 3. 新增 Service → Git → 選擇 backend 目錄
# 4. 設定環境變數（從 .env 複製）
# 5. 新增 Redis Service（從模板）
# 6. 部署
```

需要建立 3 個 Services：
- `hktv-api` - FastAPI 主服務
- `hktv-worker` - Celery Worker
- `hktv-beat` - Celery Beat

### 4.3 Cloudflare Pages 部署前端

```bash
# 1. 登入 Cloudflare Dashboard
# 2. Pages → Create a project → Connect to Git
# 3. 選擇 frontend 目錄
# 4. Build command: npm run build
# 5. Output directory: .next
# 6. 設定環境變數: NEXT_PUBLIC_API_URL
```

### 4.4 Cloudflare Access 認證

```bash
# 1. Cloudflare Dashboard → Zero Trust → Access
# 2. Applications → Add an application
# 3. Self-hosted → 填入你的域名
# 4. 設定 Policy（Allow emails ending in @your-domain.com）
# 5. 或設定特定 Email 白名單
```

### 4.5 Cloudflare R2 儲存

```bash
# 1. Cloudflare Dashboard → R2
# 2. Create bucket: hktv-ops-storage
# 3. Settings → CORS policy:
[
  {
    "AllowedOrigins": ["*"],
    "AllowedMethods": ["GET", "PUT", "POST", "DELETE"],
    "AllowedHeaders": ["*"]
  }
]
# 4. 建立 API Token
# 5. 更新 .env 的 R2 設定
```

---

## 開發順序建議

### Week 1：基礎架構
```
Day 1-2: 後端項目結構 + FastAPI 基本設定
Day 3-4: 數據庫 models + migrations
Day 5-7: 前端項目結構 + 基本 layout
```

### Week 2：競品監測核心
```
Day 1-2: Firecrawl 連接器
Day 3-4: 競品 CRUD API
Day 5-7: 前端競品列表頁
```

### Week 3：競品監測完善
```
Day 1-2: Celery 定時爬取任務
Day 3-4: 價格警報邏輯
Day 5-7: 前端價格圖表 + 警報列表
```

### Week 4：AI 文案
```
Day 1-2: Claude API 連接器
Day 3-4: 內容生成 API
Day 5-7: 前端文案生成介面
```

### Week 5：部署
```
Day 1-2: Neon + Zeabur 部署
Day 3-4: Cloudflare Pages + Access
Day 5-7: 測試 + 修復
```

---

## 常見問題

### Q: Docker 啟動失敗？
```bash
# 檢查 port 是否被佔用
lsof -i :5432
lsof -i :6379

# 重啟 Docker
docker-compose down
docker-compose up -d
```

### Q: 數據庫連接失敗？
```bash
# 檢查 PostgreSQL 是否運行
docker-compose ps

# 測試連接
psql -h localhost -U hktv -d hktv_ops
```

### Q: Celery 任務沒執行？
```bash
# 檢查 Redis 是否運行
redis-cli ping

# 檢查 Worker 日誌
celery -A app.tasks.celery_app worker --loglevel=debug
```

### Q: Firecrawl 爬取失敗？
```bash
# 檢查 API Key 是否正確
# 檢查目標網站是否支援
# 查看 Firecrawl Dashboard 的用量
```

---

## 有用指令

```bash
# 後端
uvicorn app.main:app --reload              # 開發模式
pytest                                      # 運行測試
alembic revision --autogenerate -m "xxx"   # 生成遷移
alembic upgrade head                        # 執行遷移

# 前端
npm run dev                                 # 開發模式
npm run build                               # 構建
npm run lint                                # 檢查代碼

# Docker
docker-compose up -d                        # 啟動所有服務
docker-compose down                         # 停止所有服務
docker-compose logs -f backend              # 查看日誌

# Celery
celery -A app.tasks.celery_app inspect active  # 查看活躍任務
celery -A app.tasks.celery_app purge           # 清空隊列
```

---

## 下一步

1. 按照上面順序開發
2. 每完成一個功能就測試
3. 遇到問題可以問 AI 助手
4. 等有 MMS API 再做 HKTVmall 整合

Good luck! 🚀
