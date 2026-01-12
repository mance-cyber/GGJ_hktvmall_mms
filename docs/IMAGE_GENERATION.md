# 圖片生成功能文檔

> AI 驅動的產品圖片生成系統，支持白底圖和專業攝影圖兩種模式

## 📋 目錄

- [功能概述](#功能概述)
- [系統架構](#系統架構)
- [使用指南](#使用指南)
- [API 文檔](#api-文檔)
- [部署說明](#部署說明)
- [故障排查](#故障排查)

---

## 🎯 功能概述

### 核心功能

**圖片生成系統**允許用戶上傳產品圖片，由 AI 自動生成專業的電商展示圖片。

### 支持的生成模式

1. **白底 TopView 正面圖**
   - 生成數量：1 張
   - 特點：純白背景（RGB 255,255,255）、俯視角度
   - 用途：電商平台展示（如 HKTVmall）
   - 輸出格式：PNG, 1024x1024

2. **專業美食攝影圖**
   - 生成數量：3 張
   - 特點：多角度、專業打光、高質感
   - 用途：社交媒體、廣告宣傳
   - 支持風格自定義（例如：溫暖陽光、木質餐桌背景）

### 技術特性

- ✅ 支持最多 5 張輸入圖片
- ✅ 支持格式：JPG, PNG, WEBP
- ✅ 單張圖片最大 10MB
- ✅ 異步處理（Celery 任務隊列）
- ✅ 實時進度追蹤（0-100%）
- ✅ 自動重試和錯誤處理

---

## 🏗️ 系統架構

### 架構圖

```
┌─────────────┐       ┌─────────────┐       ┌──────────────┐
│   前端      │       │   後端      │       │   Celery     │
│  (Next.js)  │◄─────►│  (FastAPI)  │◄─────►│   Worker     │
└─────────────┘       └─────────────┘       └──────────────┘
                             │                      │
                             │                      │
                             ▼                      ▼
                      ┌─────────────┐       ┌──────────────┐
                      │  PostgreSQL │       │ Nano-Banana  │
                      │   資料庫    │       │   AI API     │
                      └─────────────┘       └──────────────┘
                             │
                             ▼
                      ┌─────────────┐
                      │    Redis    │
                      │  (Celery)   │
                      └─────────────┘
```

### 核心組件

#### 1. 資料庫模型

**ImageGenerationTask（任務表）**
- `id`: UUID 主鍵
- `user_id`: 用戶 ID
- `mode`: 生成模式（white_bg_topview / professional_photo）
- `style_description`: 風格描述（可選）
- `status`: 任務狀態（pending / processing / completed / failed）
- `progress`: 進度百分比（0-100）
- `error_message`: 錯誤訊息
- `celery_task_id`: Celery 任務 ID

**InputImage（輸入圖片表）**
- `id`: UUID 主鍵
- `task_id`: 關聯任務 ID
- `file_path`: 文件路徑
- `file_name`: 文件名稱
- `file_size`: 文件大小（bytes）
- `upload_order`: 上傳順序（1-5）

**OutputImage（輸出圖片表）**
- `id`: UUID 主鍵
- `task_id`: 關聯任務 ID
- `file_path`: 文件路徑
- `prompt_used`: 使用的 Prompt
- `generation_params`: 生成參數（JSON）

#### 2. Celery 任務處理流程

```python
# 任務處理流程
def process_image_generation(task_id):
    # 1. 更新狀態為 PROCESSING (progress: 10%)
    task.status = TaskStatus.PROCESSING
    task.progress = 10

    # 2. 獲取輸入圖片 (progress: 20%)
    input_images = get_input_images(task_id)

    # 3. 調用 Nano-Banana API (progress: 30-60%)
    api_response = client.generate_xxx(input_images)

    # 4. 保存生成圖片 (progress: 80%)
    output_paths = save_images(api_response)

    # 5. 更新任務狀態為 COMPLETED (progress: 100%)
    task.status = TaskStatus.COMPLETED
    task.progress = 100
```

#### 3. API 端點

| 端點 | 方法 | 功能 |
|------|------|------|
| `/api/v1/image-generation/tasks` | POST | 創建任務 |
| `/api/v1/image-generation/tasks/{id}/upload` | POST | 上傳圖片 |
| `/api/v1/image-generation/tasks/{id}/start` | POST | 開始生成 |
| `/api/v1/image-generation/tasks/{id}` | GET | 獲取任務狀態 |
| `/api/v1/image-generation/tasks` | GET | 列出任務 |

---

## 📖 使用指南

### 前端使用流程

#### Step 1: 訪問上傳頁面

訪問：`https://your-domain.com/image-generation/upload`

#### Step 2: 選擇生成模式

- **白底 TopView 正面圖**：生成 1 張純白背景產品圖
- **專業美食攝影圖**：生成 3 張高質感攝影圖

#### Step 3: 上傳產品圖片

- 拖放或點擊選擇圖片
- 最多上傳 5 張
- 支持格式：JPG, PNG, WEBP
- 單張最大 10MB

#### Step 4: 填寫風格描述（可選）

僅在「專業攝影模式」下可用，例如：
- "溫暖陽光灑落、木質餐桌背景"
- "清新自然風格、淡雅色調"

#### Step 5: 開始生成

點擊「開始生成」按鈕，自動跳轉到結果頁面。

#### Step 6: 查看結果

結果頁面會顯示：
- 實時進度條（0-100%）
- 任務狀態（處理中/已完成/失敗）
- 生成的圖片（可查看大圖、下載）

---

## 🔌 API 文檔

### 1. 創建圖片生成任務

**端點**: `POST /api/v1/image-generation/tasks`

**請求體**:
```json
{
  "mode": "white_bg_topview",
  "style_description": "溫暖陽光"  // 可選
}
```

**響應**:
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "mode": "white_bg_topview",
  "status": "pending",
  "progress": 0,
  "created_at": "2026-01-12T14:00:00Z",
  "input_images": [],
  "output_images": []
}
```

---

### 2. 上傳輸入圖片

**端點**: `POST /api/v1/image-generation/tasks/{task_id}/upload`

**請求**: `multipart/form-data`
```
files: File[]  // 最多 5 個文件
```

**響應**:
```json
[
  {
    "id": "img-001",
    "file_name": "product.jpg",
    "file_size": 2048576,
    "upload_order": 1
  }
]
```

---

### 3. 開始圖片生成

**端點**: `POST /api/v1/image-generation/tasks/{task_id}/start`

**響應**:
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "processing",
  "progress": 10,
  "celery_task_id": "abc123..."
}
```

---

### 4. 獲取任務狀態

**端點**: `GET /api/v1/image-generation/tasks/{task_id}`

**響應**:
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "mode": "white_bg_topview",
  "status": "completed",
  "progress": 100,
  "input_images": [
    {
      "id": "img-001",
      "file_name": "product.jpg",
      "upload_order": 1
    }
  ],
  "output_images": [
    {
      "id": "out-001",
      "file_name": "generated_1.png",
      "file_path": "/uploads/generated/xxx/generated_1.png",
      "file_size": 3145728
    }
  ]
}
```

---

### 5. 列出任務

**端點**: `GET /api/v1/image-generation/tasks?page=1&page_size=20`

**響應**:
```json
{
  "tasks": [...],
  "total": 50,
  "page": 1,
  "page_size": 20
}
```

---

## 🚀 部署說明

### 環境變數配置

在 `.env` 文件中添加：

```bash
# Nano-Banana API
NANO_BANANA_API_BASE=https://ai.t8star.cn/v1
NANO_BANANA_API_KEY=your-api-key-here
NANO_BANANA_MODEL=nano-banana

# 文件存儲
UPLOAD_DIR=./uploads
USE_R2_STORAGE=false  # 開發環境使用本地存儲

# Cloudflare R2（生產環境推薦，設 USE_R2_STORAGE=true）
# R2_ACCESS_KEY=your-r2-access-key
# R2_SECRET_KEY=your-r2-secret-key
# R2_BUCKET=gogojap-images
# R2_ENDPOINT=https://your-account-id.r2.cloudflarestorage.com
# R2_PUBLIC_URL=https://images.gogojap.com

# Celery（使用 Redis）
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

**存儲模式說明：**

| 模式 | 環境 | 配置 | 優勢 |
|------|------|------|------|
| **本地存儲** | 開發/測試 | `USE_R2_STORAGE=false` | 簡單、免費、快速 |
| **R2 存儲** | 生產環境 | `USE_R2_STORAGE=true` | CDN 加速、免費出站流量、無限擴展 |

### 啟動服務

#### 1. 啟動 Redis

```bash
redis-server
```

#### 2. 運行資料庫遷移

```bash
cd backend
alembic upgrade head
```

#### 3. 啟動後端服務

```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### 4. 啟動 Celery Worker

```bash
cd backend
celery -A app.tasks.celery_app worker --loglevel=info
```

#### 5. 啟動前端

```bash
cd frontend
npm run dev
```

### Docker 部署（推薦）

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./backend
    environment:
      - NANO_BANANA_API_KEY=${NANO_BANANA_API_KEY}
    depends_on:
      - postgres
      - redis

  celery:
    build: ./backend
    command: celery -A app.tasks.celery_app worker --loglevel=info
    depends_on:
      - redis
      - postgres

  redis:
    image: redis:7-alpine

  postgres:
    image: postgres:15-alpine
```

---

## 🔧 故障排查

### 常見問題

#### 1. 任務一直停留在 `processing` 狀態

**原因**：Celery worker 未啟動或已崩潰

**解決方案**：
```bash
# 檢查 Celery worker 狀態
celery -A app.tasks.celery_app inspect active

# 重啟 Celery worker
celery -A app.tasks.celery_app worker --loglevel=info
```

---

#### 2. API 返回 500 錯誤

**原因**：Nano-Banana API Key 未配置或無效

**解決方案**：
```bash
# 檢查環境變數
echo $NANO_BANANA_API_KEY

# 重新設置
export NANO_BANANA_API_KEY=your-api-key
```

---

#### 3. 圖片上傳失敗

**原因**：文件大小超過限制或格式不支持

**解決方案**：
- 確保圖片小於 10MB
- 確保格式為 JPG, PNG, WEBP
- 檢查 `UPLOAD_DIR` 目錄權限

---

#### 4. 生成的圖片無法顯示

**原因**：文件路徑配置錯誤

**解決方案**：

**本地存儲模式：**
- 檢查 `UPLOAD_DIR` 是否正確
- 確保前端可以訪問圖片路徑（配置靜態文件路由）

**R2 存儲模式（生產環境推薦）：**

1. **創建 Cloudflare R2 Bucket**
   ```bash
   # 登入 Cloudflare Dashboard
   # 選擇 R2 Object Storage → Create Bucket
   # Bucket 名稱：gogojap-images
   ```

2. **獲取 API 憑證**
   ```bash
   # R2 → Manage R2 API Tokens → Create API Token
   # 權限：Object Read & Write
   # 保存 Access Key 和 Secret Key
   ```

3. **配置 .env**
   ```bash
   USE_R2_STORAGE=true
   R2_ACCESS_KEY=your-access-key
   R2_SECRET_KEY=your-secret-key
   R2_BUCKET=gogojap-images
   R2_ENDPOINT=https://your-account-id.r2.cloudflarestorage.com
   R2_PUBLIC_URL=https://images.gogojap.com  # 或使用 R2 自定義域名
   ```

4. **重啟服務**
   ```bash
   # 重啟後端和 Celery Worker
   # 圖片將自動上傳到 R2
   ```

**R2 優勢：**
- ✅ 10GB 免費存儲 + 無限出站流量
- ✅ CDN 加速（全球訪問快速）
- ✅ 自動備份和容災

---

## 📊 性能指標

### 平均處理時間

| 模式 | 輸入圖片數 | 平均時間 |
|------|-----------|---------|
| 白底圖 | 1-5 張 | 30-60 秒 |
| 專業攝影 | 1-5 張 | 60-120 秒 |

### 並發處理

- 單個 Celery worker 可同時處理：1 個任務
- 建議配置：4-8 個 Celery worker
- 最大並發數：根據 Nano-Banana API 限制

---

## 🔐 安全考量

1. **認證授權**：所有 API 端點需要有效的 Bearer Token
2. **文件驗證**：嚴格驗證上傳文件的格式和大小
3. **速率限制**：全局限速 60 req/min，登入限速 5 req/min
4. **文件存儲**：使用 UUID 生成唯一文件名，避免路徑遍歷
5. **錯誤處理**：不暴露內部錯誤詳情

---

## 📝 更新日誌

### v1.0.0 (2026-01-12)

**新功能**：
- ✅ 白底 TopView 圖片生成
- ✅ 專業美食攝影圖生成
- ✅ 實時進度追蹤
- ✅ 批量圖片上傳（最多 5 張）
- ✅ 風格自定義描述

**技術實現**：
- ✅ 資料庫遷移（3 個新表）
- ✅ Celery 異步任務處理
- ✅ 5 個 RESTful API 端點
- ✅ Next.js 前端頁面（上傳 + 結果）
- ✅ E2E 測試腳本

---

## 📞 支持

如有問題，請聯繫：
- GitHub Issues: [提交問題](https://github.com/your-repo/issues)
- Email: support@gogojap.com

---

**最後更新**: 2026-01-12
**版本**: v1.0.0
**作者**: GoGoJap Team
