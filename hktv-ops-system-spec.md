# HKTVmall AI 營運系統 - 完整開發規劃

## 📋 系統概覽

### 系統目標
- 競品價格監測（自動爬取、價格追蹤、異動通知）
- AI 內容生成（商品文案、多版本輸出）
- HKTVmall 數據同步（等待 MMS API）

### 技術棧
- **前端**：Next.js 14 (App Router) + Tailwind CSS + shadcn/ui
- **後端**：FastAPI + Celery + Redis
- **數據庫**：PostgreSQL (Neon)
- **儲存**：Cloudflare R2
- **認證**：Cloudflare Access
- **部署**：Cloudflare Pages (前端) + Zeabur (後端)

### 預計成本
| 服務 | 月費 (HKD) |
|------|------------|
| Cloudflare (Pages/Access/R2) | 免費 |
| Zeabur | 80-120 |
| Neon PostgreSQL | 免費 (0.5GB) |
| Firecrawl API | 150 (Hobby) |
| Claude API | 50-100 |
| **總計** | **280-370** |

---

## 📁 項目結構

```
hktv-ops-system/
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI 入口
│   │   ├── config.py               # 環境配置
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── router.py       # API 路由聚合
│   │   │       ├── competitors.py  # 競品監測 API
│   │   │       ├── products.py     # 商品管理 API
│   │   │       ├── content.py      # AI 內容 API
│   │   │       └── analytics.py    # 分析 API
│   │   │
│   │   ├── connectors/
│   │   │   ├── __init__.py
│   │   │   ├── firecrawl.py        # Firecrawl 爬蟲
│   │   │   ├── claude.py           # Claude AI
│   │   │   ├── r2.py               # Cloudflare R2
│   │   │   └── hktv/
│   │   │       ├── __init__.py
│   │   │       ├── interface.py    # 抽象接口
│   │   │       ├── mock.py         # Mock 實現
│   │   │       └── mms.py          # MMS API (待實現)
│   │   │
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── competitor_service.py
│   │   │   ├── product_service.py
│   │   │   ├── content_service.py
│   │   │   └── analytics_service.py
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── database.py         # SQLAlchemy 設定
│   │   │   ├── competitor.py
│   │   │   ├── product.py
│   │   │   ├── market.py
│   │   │   └── content.py
│   │   │
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── competitor.py       # Pydantic schemas
│   │   │   ├── product.py
│   │   │   └── content.py
│   │   │
│   │   ├── tasks/
│   │   │   ├── __init__.py
│   │   │   ├── celery_app.py       # Celery 配置
│   │   │   ├── scrape_tasks.py     # 爬蟲任務
│   │   │   ├── sync_tasks.py       # 同步任務
│   │   │   └── content_tasks.py    # 內容生成任務
│   │   │
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── helpers.py
│   │
│   ├── alembic/                    # 數據庫遷移
│   │   ├── versions/
│   │   ├── env.py
│   │   └── alembic.ini
│   │
│   ├── tests/
│   │   └── ...
│   │
│   ├── requirements.txt
│   ├── Dockerfile
│   └── pyproject.toml
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx            # Dashboard 首頁
│   │   │   ├── competitors/
│   │   │   │   └── page.tsx        # 競品監測頁
│   │   │   ├── products/
│   │   │   │   └── page.tsx        # 商品管理頁
│   │   │   ├── content/
│   │   │   │   └── page.tsx        # AI 內容頁
│   │   │   └── settings/
│   │   │       └── page.tsx        # 設定頁
│   │   │
│   │   ├── components/
│   │   │   ├── ui/                 # shadcn/ui 組件
│   │   │   ├── layout/
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   └── Header.tsx
│   │   │   ├── competitors/
│   │   │   │   ├── CompetitorTable.tsx
│   │   │   │   ├── PriceChart.tsx
│   │   │   │   └── AddCompetitorForm.tsx
│   │   │   └── content/
│   │   │       ├── CopyGenerator.tsx
│   │   │       └── CopyHistory.tsx
│   │   │
│   │   └── lib/
│   │       ├── api.ts              # API client
│   │       └── utils.ts
│   │
│   ├── package.json
│   ├── next.config.js
│   ├── tailwind.config.js
│   └── tsconfig.json
│
├── docker/
│   ├── docker-compose.yml          # 本地開發
│   └── docker-compose.prod.yml
│
├── .env.example
├── .gitignore
└── README.md
```

---

## 🗄️ 數據庫 Schema

### SQL 創建語句

```sql
-- =============================================
-- 競品監測相關表
-- =============================================

-- 競爭對手
CREATE TABLE competitors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    platform VARCHAR(100) NOT NULL,  -- 'hktvmall', 'watsons', 'mannings', etc.
    base_url VARCHAR(500),
    notes TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 競品商品
CREATE TABLE competitor_products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    competitor_id UUID REFERENCES competitors(id) ON DELETE CASCADE,
    name VARCHAR(500) NOT NULL,
    url VARCHAR(1000) NOT NULL UNIQUE,
    sku VARCHAR(100),
    category VARCHAR(255),
    image_url VARCHAR(1000),
    is_active BOOLEAN DEFAULT true,
    last_scraped_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 價格快照（歷史記錄）
CREATE TABLE price_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    competitor_product_id UUID REFERENCES competitor_products(id) ON DELETE CASCADE,
    price DECIMAL(10, 2),
    original_price DECIMAL(10, 2),
    discount_percent DECIMAL(5, 2),
    stock_status VARCHAR(50),  -- 'in_stock', 'out_of_stock', 'low_stock'
    rating DECIMAL(3, 2),
    review_count INTEGER,
    raw_data JSONB,  -- 完整爬取數據
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 價格警報
CREATE TABLE price_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    competitor_product_id UUID REFERENCES competitor_products(id) ON DELETE CASCADE,
    alert_type VARCHAR(50) NOT NULL,  -- 'price_drop', 'price_increase', 'out_of_stock', 'back_in_stock'
    old_value VARCHAR(100),
    new_value VARCHAR(100),
    change_percent DECIMAL(5, 2),
    is_read BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================
-- 自家商品相關表
-- =============================================

-- 商品
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sku VARCHAR(100) UNIQUE NOT NULL,
    hktv_product_id VARCHAR(100),
    name VARCHAR(500) NOT NULL,
    description TEXT,
    category VARCHAR(255),
    brand VARCHAR(255),
    price DECIMAL(10, 2),
    cost DECIMAL(10, 2),
    stock_quantity INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'active',  -- 'active', 'inactive', 'pending'
    images JSONB,  -- ["url1", "url2"]
    attributes JSONB,  -- {"color": "red", "size": "M"}
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 商品-競品關聯（用於比較）
CREATE TABLE product_competitor_mapping (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    competitor_product_id UUID REFERENCES competitor_products(id) ON DELETE CASCADE,
    match_confidence DECIMAL(3, 2),  -- 0.00 - 1.00
    is_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(product_id, competitor_product_id)
);

-- =============================================
-- AI 內容相關表
-- =============================================

-- AI 生成內容
CREATE TABLE ai_contents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    content_type VARCHAR(50) NOT NULL,  -- 'title', 'description', 'selling_points', 'full_copy'
    style VARCHAR(50),  -- 'formal', 'casual', 'playful', 'professional'
    content TEXT NOT NULL,
    version INTEGER DEFAULT 1,
    status VARCHAR(50) DEFAULT 'draft',  -- 'draft', 'approved', 'published', 'rejected'
    metadata JSONB,  -- {"tokens_used": 500, "model": "claude-sonnet"}
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    approved_at TIMESTAMP WITH TIME ZONE,
    approved_by VARCHAR(255)
);

-- =============================================
-- 系統相關表
-- =============================================

-- 爬取任務日誌
CREATE TABLE scrape_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id VARCHAR(255),
    competitor_id UUID REFERENCES competitors(id),
    status VARCHAR(50) NOT NULL,  -- 'pending', 'running', 'success', 'failed'
    products_scraped INTEGER DEFAULT 0,
    errors JSONB,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 系統設定
CREATE TABLE settings (
    key VARCHAR(255) PRIMARY KEY,
    value JSONB NOT NULL,
    description TEXT,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================
-- 索引
-- =============================================

CREATE INDEX idx_competitor_products_competitor_id ON competitor_products(competitor_id);
CREATE INDEX idx_competitor_products_url ON competitor_products(url);
CREATE INDEX idx_price_snapshots_product_id ON price_snapshots(competitor_product_id);
CREATE INDEX idx_price_snapshots_scraped_at ON price_snapshots(scraped_at DESC);
CREATE INDEX idx_price_alerts_created_at ON price_alerts(created_at DESC);
CREATE INDEX idx_price_alerts_is_read ON price_alerts(is_read);
CREATE INDEX idx_products_sku ON products(sku);
CREATE INDEX idx_ai_contents_product_id ON ai_contents(product_id);
CREATE INDEX idx_ai_contents_status ON ai_contents(status);

-- =============================================
-- 初始設定數據
-- =============================================

INSERT INTO settings (key, value, description) VALUES
('scrape_schedule', '{"frequency": "daily", "time": "09:00"}', '爬取排程設定'),
('notification_email', '{"enabled": true, "email": ""}', 'Email 通知設定'),
('price_alert_threshold', '{"percentage": 10}', '價格變動警報門檻');
```

---

## 🔌 API 設計

### Base URL
```
Production: https://api.your-domain.com/api/v1
Development: http://localhost:8000/api/v1
```

### 認證
所有 API 通過 Cloudflare Access 保護，無需額外實現認證。

---

### 競品監測 API

#### 列出所有競爭對手
```
GET /competitors

Response 200:
{
  "data": [
    {
      "id": "uuid",
      "name": "Watsons",
      "platform": "watsons",
      "base_url": "https://www.watsons.com.hk",
      "is_active": true,
      "product_count": 15,
      "last_scraped_at": "2025-01-05T10:00:00Z"
    }
  ],
  "total": 5
}
```

#### 新增競爭對手
```
POST /competitors

Request:
{
  "name": "Watsons",
  "platform": "watsons",
  "base_url": "https://www.watsons.com.hk",
  "notes": "主要監測保健品類"
}

Response 201:
{
  "id": "uuid",
  "name": "Watsons",
  ...
}
```

#### 列出競品商品
```
GET /competitors/{competitor_id}/products

Query params:
- page: int (default: 1)
- limit: int (default: 20)
- search: string

Response 200:
{
  "data": [
    {
      "id": "uuid",
      "name": "維他命C 1000mg",
      "url": "https://...",
      "current_price": 159.00,
      "previous_price": 169.00,
      "price_change": -5.9,
      "stock_status": "in_stock",
      "last_scraped_at": "2025-01-05T10:00:00Z"
    }
  ],
  "total": 15,
  "page": 1,
  "limit": 20
}
```

#### 新增競品商品
```
POST /competitors/{competitor_id}/products

Request:
{
  "url": "https://www.watsons.com.hk/product/12345",
  "name": "維他命C 1000mg",  // 可選，會自動爬取
  "category": "保健品"
}

Response 201:
{
  "id": "uuid",
  "message": "已加入監測，正在爬取數據..."
}
```

#### 獲取價格歷史
```
GET /competitors/products/{product_id}/history

Query params:
- days: int (default: 30)

Response 200:
{
  "product": {
    "id": "uuid",
    "name": "維他命C 1000mg"
  },
  "history": [
    {
      "date": "2025-01-05",
      "price": 159.00,
      "stock_status": "in_stock"
    },
    {
      "date": "2025-01-04",
      "price": 169.00,
      "stock_status": "in_stock"
    }
  ]
}
```

#### 手動觸發爬取
```
POST /competitors/{competitor_id}/scrape

Response 202:
{
  "task_id": "celery-task-id",
  "message": "爬取任務已啟動"
}
```

#### 獲取價格警報
```
GET /alerts

Query params:
- is_read: boolean
- type: string (price_drop, price_increase, out_of_stock)
- limit: int (default: 50)

Response 200:
{
  "data": [
    {
      "id": "uuid",
      "product_name": "維他命C 1000mg",
      "competitor_name": "Watsons",
      "alert_type": "price_drop",
      "old_value": "169.00",
      "new_value": "159.00",
      "change_percent": -5.9,
      "is_read": false,
      "created_at": "2025-01-05T10:00:00Z"
    }
  ],
  "unread_count": 3
}
```

---

### AI 內容 API

#### 生成文案
```
POST /content/generate

Request:
{
  "product_id": "uuid",  // 可選，如果有已存在商品
  "product_info": {      // 或直接提供商品資料
    "name": "天然維他命C",
    "brand": "YourBrand",
    "features": ["1000mg", "60粒裝", "美國進口"],
    "target_audience": "注重健康的成年人"
  },
  "content_type": "full_copy",  // title, description, selling_points, full_copy
  "style": "professional",       // formal, casual, playful, professional
  "language": "zh-HK"
}

Response 200:
{
  "id": "uuid",
  "content_type": "full_copy",
  "content": {
    "title": "【美國進口】天然維他命C 1000mg 60粒裝",
    "selling_points": [
      "高劑量1000mg，每日一粒足夠",
      "美國原裝進口，品質保證",
      "天然配方，易於吸收"
    ],
    "description": "..."
  },
  "metadata": {
    "tokens_used": 450,
    "model": "claude-sonnet-4-20250514"
  }
}
```

#### 批量生成
```
POST /content/batch-generate

Request:
{
  "product_ids": ["uuid1", "uuid2", "uuid3"],
  "content_type": "full_copy",
  "style": "professional"
}

Response 202:
{
  "task_id": "celery-task-id",
  "message": "批量生成任務已啟動",
  "product_count": 3
}
```

#### 獲取生成歷史
```
GET /content/history

Query params:
- product_id: uuid
- status: string (draft, approved, published)
- limit: int

Response 200:
{
  "data": [
    {
      "id": "uuid",
      "product_name": "維他命C",
      "content_type": "full_copy",
      "style": "professional",
      "status": "draft",
      "preview": "【美國進口】天然維他命C...",
      "generated_at": "2025-01-05T10:00:00Z"
    }
  ]
}
```

#### 審批內容
```
PUT /content/{content_id}/approve

Response 200:
{
  "id": "uuid",
  "status": "approved",
  "approved_at": "2025-01-05T10:30:00Z"
}
```

---

### Dashboard API

#### 獲取總覽數據
```
GET /dashboard

Response 200:
{
  "competitors": {
    "total": 5,
    "active": 4,
    "products_monitored": 50
  },
  "alerts": {
    "unread": 3,
    "today": 5,
    "price_drops": 2,
    "price_increases": 3
  },
  "content": {
    "generated_today": 10,
    "pending_approval": 5
  },
  "recent_alerts": [
    {
      "id": "uuid",
      "product_name": "維他命C",
      "alert_type": "price_drop",
      "change_percent": -5.9,
      "created_at": "2025-01-05T10:00:00Z"
    }
  ],
  "price_trends": [
    {
      "date": "2025-01-01",
      "avg_price_change": -2.5
    }
  ]
}
```

---

## 🐳 Docker 配置

### docker-compose.yml（本地開發）

```yaml
version: '3.8'

services:
  # PostgreSQL
  db:
    image: postgres:16-alpine
    restart: unless-stopped
    environment:
      POSTGRES_USER: hktv
      POSTGRES_PASSWORD: hktv_dev_password
      POSTGRES_DB: hktv_ops
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U hktv -d hktv_ops"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis
  redis:
    image: redis:7-alpine
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # FastAPI Backend
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://hktv:hktv_dev_password@db:5432/hktv_ops
      - REDIS_URL=redis://redis:6379/0
      - FIRECRAWL_API_KEY=${FIRECRAWL_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - R2_ACCESS_KEY=${R2_ACCESS_KEY}
      - R2_SECRET_KEY=${R2_SECRET_KEY}
      - R2_BUCKET=${R2_BUCKET}
      - R2_ENDPOINT=${R2_ENDPOINT}
    volumes:
      - ./backend:/app
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  # Celery Worker
  celery-worker:
    build:
      context: ./backend
      dockerfile: Dockerfile
    restart: unless-stopped
    environment:
      - DATABASE_URL=postgresql://hktv:hktv_dev_password@db:5432/hktv_ops
      - REDIS_URL=redis://redis:6379/0
      - FIRECRAWL_API_KEY=${FIRECRAWL_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    volumes:
      - ./backend:/app
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    command: celery -A app.tasks.celery_app worker --loglevel=info

  # Celery Beat (Scheduler)
  celery-beat:
    build:
      context: ./backend
      dockerfile: Dockerfile
    restart: unless-stopped
    environment:
      - DATABASE_URL=postgresql://hktv:hktv_dev_password@db:5432/hktv_ops
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - ./backend:/app
    depends_on:
      - redis
    command: celery -A app.tasks.celery_app beat --loglevel=info

volumes:
  postgres_data:
  redis_data:
```

### Backend Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 安裝 Python 依賴
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製代碼
COPY . .

# 暴露端口
EXPOSE 8000

# 啟動命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### requirements.txt

```
# Web Framework
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-multipart==0.0.6

# Database
sqlalchemy==2.0.25
asyncpg==0.29.0
alembic==1.13.1

# Task Queue
celery==5.3.6
redis==5.0.1

# External APIs
firecrawl-py==0.0.16
anthropic==0.18.1
boto3==1.34.34  # For R2 (S3 compatible)

# Utilities
pydantic==2.6.0
pydantic-settings==2.1.0
python-dotenv==1.0.1
httpx==0.26.0

# Development
pytest==8.0.0
pytest-asyncio==0.23.4
black==24.1.1
ruff==0.2.0
```

---

## ⚙️ 環境變數

### .env.example

```bash
# ===== 基本設定 =====
APP_ENV=development
DEBUG=true
SECRET_KEY=your-secret-key-change-in-production

# ===== 數據庫 =====
# 本地開發
DATABASE_URL=postgresql://hktv:hktv_dev_password@localhost:5432/hktv_ops
# 生產 (Neon)
# DATABASE_URL=postgresql://user:pass@ep-xxx.ap-southeast-1.aws.neon.tech/hktv_ops?sslmode=require

# ===== Redis =====
# 本地開發
REDIS_URL=redis://localhost:6379/0
# 生產 (Upstash)
# REDIS_URL=rediss://default:xxx@apn1-xxx.upstash.io:6379

# ===== Firecrawl =====
FIRECRAWL_API_KEY=fc-your-api-key

# ===== Claude AI =====
ANTHROPIC_API_KEY=sk-ant-your-api-key
AI_MODEL=claude-sonnet-4-20250514

# ===== Cloudflare R2 =====
R2_ACCESS_KEY=your-access-key
R2_SECRET_KEY=your-secret-key
R2_BUCKET=hktv-ops-storage
R2_ENDPOINT=https://your-account-id.r2.cloudflarestorage.com

# ===== HKTVmall (未來) =====
HKTV_CONNECTOR_TYPE=mock
# HKTV_MMS_API_URL=
# HKTV_MMS_CLIENT_ID=
# HKTV_MMS_CLIENT_SECRET=

# ===== 通知 =====
NOTIFICATION_EMAIL=your-email@example.com
```

---

## 🚀 Zeabur 部署配置

### zeabur.yaml（放在 backend/ 目錄）

```yaml
# API Service
name: hktv-api
template: dockerfile
dockerfile: Dockerfile
port: 8000
env:
  - DATABASE_URL
  - REDIS_URL
  - FIRECRAWL_API_KEY
  - ANTHROPIC_API_KEY
  - R2_ACCESS_KEY
  - R2_SECRET_KEY
  - R2_BUCKET
  - R2_ENDPOINT
```

### Celery Worker 需要另外建立 Service

在 Zeabur 控制台：
1. 建立新 Service → Docker
2. 設定 Start Command: `celery -A app.tasks.celery_app worker --loglevel=info`
3. 設定相同嘅環境變數

### Celery Beat 同樣

1. 建立新 Service → Docker
2. 設定 Start Command: `celery -A app.tasks.celery_app beat --loglevel=info`

---

## 📋 開發任務清單

### Phase 1：基礎架構 (Week 1)

- [ ] **Task 1.1**：初始化後端項目
  - FastAPI 基本結構
  - config.py 環境配置
  - 健康檢查 endpoint

- [ ] **Task 1.2**：數據庫設定
  - SQLAlchemy models
  - Alembic 遷移
  - 執行上述 SQL schema

- [ ] **Task 1.3**：初始化前端項目
  - Next.js 14 + App Router
  - Tailwind CSS + shadcn/ui
  - 基本 layout（Sidebar + Header）

- [ ] **Task 1.4**：Docker 本地環境
  - docker-compose.yml
  - 測試所有服務啟動

---

### Phase 2：競品監測 (Week 2-3) ⭐ 優先

- [ ] **Task 2.1**：Firecrawl 連接器
  ```python
  # 功能：
  # - scrape_url(url) -> dict
  # - extract_product_info(url) -> ProductInfo
  ```

- [ ] **Task 2.2**：競品 CRUD API
  ```
  GET    /competitors
  POST   /competitors
  GET    /competitors/{id}
  DELETE /competitors/{id}
  GET    /competitors/{id}/products
  POST   /competitors/{id}/products
  ```

- [ ] **Task 2.3**：爬取任務（Celery）
  ```python
  # 定時任務：每日 9am 爬取所有競品
  # 手動觸發：POST /competitors/{id}/scrape
  ```

- [ ] **Task 2.4**：價格警報邏輯
  ```python
  # 偵測價格變動 > 10%
  # 偵測庫存狀態變化
  # 建立 alert 記錄
  ```

- [ ] **Task 2.5**：前端 - 競品列表頁
  - 競爭對手列表
  - 新增競爭對手表單
  - 競品商品列表

- [ ] **Task 2.6**：前端 - 價格圖表
  - 價格走勢圖（Recharts）
  - 價格比較表
  - 警報列表

---

### Phase 3：AI 內容 (Week 4)

- [ ] **Task 3.1**：Claude API 連接器
  ```python
  # 功能：
  # - generate_copy(product_info, style) -> str
  # - generate_title(product_info) -> str
  # - generate_selling_points(product_info) -> list
  ```

- [ ] **Task 3.2**：內容生成 API
  ```
  POST   /content/generate
  POST   /content/batch-generate
  GET    /content/history
  PUT    /content/{id}/approve
  ```

- [ ] **Task 3.3**：前端 - 文案生成介面
  - 商品資料輸入表單
  - 風格選擇
  - 生成結果顯示
  - 複製/編輯/審批

---

### Phase 4：部署 (Week 5)

- [ ] **Task 4.1**：Neon PostgreSQL 設定
  - 建立 database
  - 執行 migrations
  - 設定連接

- [ ] **Task 4.2**：Zeabur 部署
  - API service
  - Celery worker
  - Celery beat
  - Redis (Zeabur 模板)

- [ ] **Task 4.3**：Cloudflare Pages
  - 連接 GitHub
  - 設定 build command
  - 設定環境變數

- [ ] **Task 4.4**：Cloudflare Access
  - 建立 Application
  - 設定 Email 認證
  - 綁定域名

- [ ] **Task 4.5**：Cloudflare R2
  - 建立 Bucket
  - 設定 CORS
  - 測試上傳

---

## 🔗 有用連結

- [FastAPI 文檔](https://fastapi.tiangolo.com/)
- [Celery 文檔](https://docs.celeryq.dev/)
- [Next.js 14 文檔](https://nextjs.org/docs)
- [Firecrawl API](https://docs.firecrawl.dev/)
- [Claude API](https://docs.anthropic.com/)
- [Zeabur 文檔](https://zeabur.com/docs)
- [Neon 文檔](https://neon.tech/docs)
- [Cloudflare R2](https://developers.cloudflare.com/r2/)
- [shadcn/ui](https://ui.shadcn.com/)

---

## 📞 後續：MMS API 整合

當你拿到 HKTVmall MMS API 權限後，需要實現：

1. `backend/app/connectors/hktv/mms.py` - 真實 API 實現
2. 商品同步任務
3. 訂單同步任務
4. 庫存同步任務
5. 前端相應頁面

目前所有 HKTV 相關功能都用 Mock 實現，切換只需改 `HKTV_CONNECTOR_TYPE` 環境變數。
