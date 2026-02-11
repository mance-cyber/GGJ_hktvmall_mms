# 切換到 Neon PostgreSQL 指南

**創建日期:** 2026-02-10
**目的:** 從 Zeabur PostgreSQL 切換到 Neon PostgreSQL
**原因:** 數據庫為空，Neon 更方便且免費

---

## 🎯 為什麼切換到 Neon？

### **優勢：**

```yaml
1. 成本:
   Zeabur: ~$10-20/月
   Neon: $0 (免費層)
   節省: $10-20/月 ✅

2. 訪問:
   Zeabur: 內部服務名，難訪問
   Neon: 公網訪問，容易管理 ✅

3. 導出:
   Zeabur: 需要特殊方式
   Neon: 直接 pg_dump ✅

4. 備份:
   Zeabur: 困難
   Neon: 自動備份 + 手動導出 ✅

5. 未來遷移:
   Zeabur → RDS: 複雜
   Neon → RDS: 超簡單 ✅
```

### **沒有缺點：**

```yaml
當前狀況:
  ✅ 數據庫為空 (無需遷移數據)
  ✅ 只需要更新連接字符串
  ✅ 運行 Alembic 創建表結構
  ✅ 5-10 分鐘完成
```

---

## 🚀 完整步驟 (10 分鐘)

### **Phase 1: 創建 Neon 數據庫**

#### Step 1.1: 註冊/登入 Neon

```
🔗 https://console.neon.tech/

可用:
  - Google 帳號
  - GitHub 帳號
  - Email
```

#### Step 1.2: 創建項目

```yaml
1. 點擊 "New Project" 或 "Create a project"

2. 配置:
   Project name: gogojap-production
   Region: Asia Pacific (Singapore)
   PostgreSQL version: 16 (推薦最新)
   Compute size: 保持默認 (免費層)

3. 點擊 "Create"

4. 等待 30 秒，項目創建完成
```

#### Step 1.3: 獲取連接信息

```yaml
項目創建後會顯示:

Connection string:
  postgresql://user:pass@ep-xxx-xxx.ap-southeast-1.aws.neon.tech/neondb

Host:
  ep-xxx-xxx.ap-southeast-1.aws.neon.tech

Database:
  neondb

User:
  user_xxx

Password:
  xxxxx

⚠️ 重要: 複製並保存所有信息！
```

---

### **Phase 2: 在 Neon 創建表結構**

#### Step 2.1: 在本地運行 Alembic

```bash
# ==================== 1. 進入後端目錄 ====================
cd backend

# ==================== 2. 激活虛擬環境 ====================
# Linux/Mac:
source venv/bin/activate

# Windows:
venv\Scripts\activate

# ==================== 3. 臨時設置環境變量 ====================
# Linux/Mac:
export DATABASE_URL="postgresql://user:pass@ep-xxx.neon.tech/neondb"

# Windows (PowerShell):
$env:DATABASE_URL="postgresql://user:pass@ep-xxx.neon.tech/neondb"

# Windows (CMD):
set DATABASE_URL=postgresql://user:pass@ep-xxx.neon.tech/neondb

# ==================== 4. 測試連接 ====================
psql "$DATABASE_URL" -c "SELECT version();"
# 應該顯示 PostgreSQL 版本

# ==================== 5. 運行遷移創建所有表 ====================
alembic upgrade head

# 應該看到:
# INFO  [alembic.runtime.migration] Running upgrade ... -> xxx
# ...
# INFO  [alembic.runtime.migration] Running upgrade xxx -> head

# ==================== 6. 驗證表已創建 ====================
psql "$DATABASE_URL" -c "\dt"

# 應該看到所有表:
# products, users, competitors, pricing_suggestions, 等等
```

---

### **Phase 3: 更新 Zeabur 配置**

#### Step 3.1: 訪問 Zeabur Dashboard

```
🔗 https://zeabur.com/
```

#### Step 3.2: 更新環境變量

```yaml
1. 找到你的後端服務

2. 點擊服務名稱進入詳情

3. 找到 "Variables" 或 "Environment Variables" 標籤

4. 找到或添加 DATABASE_URL:

   舊值 (Zeabur):
   postgresql://root:xxx@service-695f445ee2d178cb4f475df6:5432/zeabur

   新值 (Neon):
   postgresql://user:pass@ep-xxx.neon.tech/neondb

5. 保存變更

6. 重新部署:
   - Zeabur 通常自動重啟
   - 或手動點擊 "Redeploy"
```

#### Step 3.3: 等待部署完成

```yaml
等待時間: 1-3 分鐘

狀態檢查:
  - 查看 Zeabur 部署日誌
  - 確保沒有錯誤
  - 看到 "Deployment successful"
```

---

### **Phase 4: 驗證和測試**

#### Step 4.1: 測試數據庫連接

```bash
# ==================== 連接到 Neon ====================
psql "postgresql://user:pass@ep-xxx.neon.tech/neondb"

# ==================== 檢查表 ====================
\dt

# ==================== 檢查表結構 ====================
\d products

# ==================== 退出 ====================
\q
```

#### Step 4.2: 測試應用 API

```bash
# ==================== 健康檢查 ====================
curl https://your-app.zeabur.app/health

# 應該返回 200 OK

# ==================== 測試數據庫查詢 ====================
curl https://your-app.zeabur.app/api/v1/products

# 應該返回空數組 [] (因為數據庫為空)
# 或 {"items": [], "total": 0}

# ==================== 測試寫入 ====================
# 在前端或通過 API 創建一個測試記錄
# 確認可以成功寫入
```

#### Step 4.3: 檢查應用日誌

```bash
# 在 Zeabur Dashboard 查看應用日誌
# 確保沒有數據庫連接錯誤

# 應該看到類似:
# ✓ Connected to database
# ✓ Database connection pool initialized
```

---

## ✅ 完成檢查清單

```yaml
Phase 1: Neon 創建
  - [ ] Neon 帳號已註冊
  - [ ] 項目已創建
  - [ ] 連接字符串已保存

Phase 2: 表結構創建
  - [ ] Alembic 遷移已運行
  - [ ] 所有表已創建
  - [ ] 表結構已驗證

Phase 3: Zeabur 更新
  - [ ] DATABASE_URL 已更新
  - [ ] 服務已重新部署
  - [ ] 部署成功無錯誤

Phase 4: 驗證
  - [ ] 數據庫連接正常
  - [ ] API 健康檢查通過
  - [ ] 可以讀取和寫入數據
  - [ ] 應用日誌無錯誤
```

---

## 🔧 故障排查

### **問題 1: Alembic 遷移失敗**

```bash
錯誤: "Could not connect to database"

解決:
  1. 檢查 DATABASE_URL 是否正確
  2. 檢查網絡連接
  3. 確認 Neon 項目已啟動
  4. 檢查密碼中是否有特殊字符需要編碼
```

### **問題 2: Zeabur 無法連接到 Neon**

```bash
錯誤: "Connection refused" 或 "Timeout"

解決:
  1. 檢查 DATABASE_URL 格式
  2. 確保沒有多餘的空格
  3. 檢查 Neon 項目狀態 (是否暫停)
  4. 查看 Zeabur 日誌詳細錯誤
```

### **問題 3: 表結構不完整**

```bash
錯誤: "Table does not exist"

解決:
  1. 重新運行 Alembic: alembic upgrade head
  2. 檢查 alembic/versions/ 目錄
  3. 確保所有遷移文件都存在
  4. 查看 Alembic 日誌
```

---

## 📊 切換前後對比

### **架構變化：**

```yaml
舊架構:
  ├─ Cloudflare Pages (前端)
  ├─ Zeabur (後端)
  ├─ Zeabur PostgreSQL (數據庫) ← 問題
  └─ Cloudflare R2 (存儲)

新架構:
  ├─ Cloudflare Pages (前端)
  ├─ Zeabur (後端)
  ├─ Neon PostgreSQL (數據庫) ← 改善！✅
  └─ Cloudflare R2 (存儲)
```

### **成本變化：**

```yaml
舊成本:
  Zeabur (後端 + 數據庫): ~$20-30/月
  Cloudflare R2: ~$5/月
  總計: ~$25-35/月

新成本:
  Zeabur (只有後端): ~$10-20/月
  Neon: $0 (免費層)
  Cloudflare R2: ~$5/月
  總計: ~$15-25/月

節省: ~$10/月 ✅
```

---

## 🔄 未來遷移路徑

### **遷移到 AWS 變得超簡單：**

```yaml
當前 (切換到 Neon 後):
  ✅ Neon 有公網訪問
  ✅ 可以直接 pg_dump
  ✅ 免費且穩定

等 AWS Lightsail 批准後:
  Step 1: 導出 Neon (2 分鐘)
    pg_dump <neon-url> --file=backup.dump

  Step 2: 導入 RDS (5 分鐘)
    pg_restore <rds-url> backup.dump

  Step 3: 更新配置 (1 分鐘)
    DATABASE_URL = <rds-url>

  完成！超簡單！
```

---

## 📝 記錄信息

### **保存以下信息供未來使用：**

```yaml
Neon 連接信息:
  Project name: ____________________
  Region: Asia Pacific (Singapore)

  Connection string:
    postgresql://________________

  Host:
    ep-_________.ap-southeast-1.aws.neon.tech

  Database: neondb
  User: _______
  Password: _______

切換日期: 2026-02-10
操作人: Mance
狀態: ✅ 完成
```

---

## 🎉 完成後的好處

```yaml
✅ 成本降低: 省 $10/月
✅ 管理簡化: 獨立數據庫控制台
✅ 備份簡單: 自動備份 + 手動導出
✅ 訪問方便: 公網訪問，任何地方都能連
✅ 未來遷移: Neon → RDS 超簡單
✅ 性能穩定: Neon 專業數據庫服務
```

---

**創建日期:** 2026-02-10
**預計時間:** 10 分鐘
**難度:** ⭐⭐ (簡單)
**狀態:** 準備就緒
