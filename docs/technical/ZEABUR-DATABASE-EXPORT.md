# Zeabur PostgreSQL 數據庫導出指南

**創建日期:** 2026-02-10
**數據庫類型:** Zeabur PostgreSQL
**目標:** 導出數據以遷移到 AWS RDS

---

## 📋 當前數據庫信息

```yaml
類型: Zeabur PostgreSQL
主機名: service-695f445ee2d178cb4f475df6 (內部服務名)
端口: 5432
數據庫: zeabur
用戶: root
密碼: gr5E768NxHFPikqDe42KIw03G1dC9Tuz
```

**連接字符串:**
```
postgresql://root:gr5E768NxHFPikqDe42KIw03G1dC9Tuz@service-695f445ee2d178cb4f475df6:5432/zeabur
```

---

## 🔍 問題：內部服務名無法直接訪問

### **挑戰：**

```yaml
主機名: service-695f445ee2d178cb4f475df6
  → 這是 Zeabur 內部 Docker 網絡的服務名
  → 無法從外部直接訪問
  → 需要特殊方式導出數據
```

---

## 🎯 導出方案（4 種選擇）

### **方案 1: Zeabur Dashboard 備份功能** ⭐ 最簡單

#### 步驟：

```yaml
1. 登入 Zeabur Dashboard:
   https://zeabur.com/

2. 找到你的項目

3. 找到 PostgreSQL 服務

4. 查看是否有以下功能:
   - "Backup" 或 "備份"
   - "Export" 或 "導出"
   - "Download" 或 "下載"

5. 如果有備份功能:
   - 點擊創建備份
   - 下載備份文件
   - 備份格式通常是 .sql 或 .dump

6. 完成！
```

**優點：**
- ✅ 最簡單
- ✅ 不需要命令行
- ✅ Zeabur 官方支持

**缺點：**
- ⚠️ 需要 Zeabur 有此功能

---

### **方案 2: 通過應用容器導出** ⭐ 推薦

#### 前提條件：

Zeabur CLI 已安裝：
```bash
# 安裝 Zeabur CLI
npm install -g @zeabur/cli

# 或
curl -fsSL https://cli.zeabur.com/install.sh | bash

# 登入
zeabur login
```

#### 步驟：

```bash
# ==================== 1. 列出所有服務 ====================
zeabur service list

# 找到你的後端服務名稱，例如: gogojap-backend

# ==================== 2. 進入應用容器 ====================
zeabur exec gogojap-backend /bin/bash

# ==================== 3. 在容器內導出數據庫 ====================
# 此時在容器內，可以訪問內部服務名
pg_dump "$DATABASE_URL" \
  --format=custom \
  --no-owner \
  --no-acl \
  --verbose \
  --file=/tmp/zeabur_backup.dump

# 或使用明文 SQL 格式
pg_dump "$DATABASE_URL" \
  --format=plain \
  --no-owner \
  --no-acl \
  --verbose \
  --file=/tmp/zeabur_backup.sql

# ==================== 4. 退出容器 ====================
exit

# ==================== 5. 下載備份文件到本地 ====================
# 方式 A: 如果 Zeabur 支持文件下載
zeabur download gogojap-backend /tmp/zeabur_backup.dump

# 方式 B: 通過 SCP（如果容器有 SSH）
zeabur scp gogojap-backend:/tmp/zeabur_backup.dump ./zeabur_backup.dump
```

**優點：**
- ✅ 可靠
- ✅ 完全控制
- ✅ 支持所有 pg_dump 選項

**缺點：**
- ⚠️ 需要 CLI 工具
- ⚠️ 稍微複雜

---

### **方案 3: 暴露公網端點** ⚠️ 臨時方案

#### 在 Zeabur Dashboard：

```yaml
1. 找到 PostgreSQL 服務

2. 查看服務設置

3. 查找以下選項:
   - "Public Access" / "公網訪問"
   - "External Endpoint" / "外部端點"
   - "Expose to Internet" / "暴露到互聯網"

4. 如果有，啟用公網訪問:
   - 會獲得一個公網 URL
   - 格式類似: xxx.zeabur.app:5432
   - 或一個 IP 地址

5. 使用公網連接字符串導出:
   postgresql://root:password@xxx.zeabur.app:5432/zeabur
```

#### 導出命令：

```bash
# 使用公網連接字符串
pg_dump "postgresql://root:gr5E768NxHFPikqDe42KIw03G1dC9Tuz@[公網地址]:5432/zeabur" \
  --format=custom \
  --no-owner \
  --no-acl \
  --verbose \
  --file=zeabur_backup_$(date +%Y%m%d).dump
```

#### ⚠️ 安全注意：

```yaml
重要:
  1. 導出完成後立即關閉公網訪問
  2. 不要長期暴露數據庫到公網
  3. 確保使用強密碼
```

**優點：**
- ✅ 可以從本地機器導出
- ✅ 使用標準 pg_dump 命令

**缺點：**
- ❌ 安全風險
- ⚠️ 需要 Zeabur 支持此功能
- ⚠️ 必須記得關閉公網訪問

---

### **方案 4: 通過應用 API 導出** 🔧 自定義

#### 創建臨時導出端點：

在 FastAPI 應用中添加臨時路由：

```python
# backend/app/api/v1/admin.py

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
import subprocess
import os
from datetime import datetime

router = APIRouter()

@router.post("/database/export")
async def export_database():
    """臨時端點：導出數據庫（僅用於遷移）"""

    # ⚠️ 安全：生產環境應該需要管理員權限
    # current_user = Depends(get_current_admin_user)

    # 生成備份文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"/tmp/zeabur_backup_{timestamp}.dump"

    # 執行 pg_dump
    database_url = os.getenv("DATABASE_URL")

    cmd = [
        "pg_dump",
        database_url,
        "--format=custom",
        "--no-owner",
        "--no-acl",
        f"--file={backup_file}"
    ]

    subprocess.run(cmd, check=True)

    # 返回文件供下載
    return FileResponse(
        backup_file,
        media_type="application/octet-stream",
        filename=f"zeabur_backup_{timestamp}.dump"
    )
```

#### 使用：

```bash
# 1. 部署包含導出端點的代碼到 Zeabur

# 2. 調用 API 導出
curl -X POST https://your-app.zeabur.app/api/v1/admin/database/export \
  -o zeabur_backup.dump

# 3. 遷移完成後刪除此端點
```

**優點：**
- ✅ 完全控制
- ✅ 可以添加安全驗證

**缺點：**
- ⚠️ 需要修改代碼
- ⚠️ 需要重新部署
- ⚠️ 記得刪除臨時代碼

---

## 📋 推薦流程

### **Step 1: 檢查 Zeabur Dashboard**

```yaml
1. 登入 Zeabur
2. 找到 PostgreSQL 服務
3. 查看是否有內置備份功能

如果有:
  → 使用方案 1（最簡單）

如果沒有:
  → 繼續 Step 2
```

### **Step 2: 安裝 Zeabur CLI**

```bash
# 安裝
npm install -g @zeabur/cli

# 登入
zeabur login

# 測試
zeabur service list
```

### **Step 3: 通過容器導出**

```bash
# 進入容器
zeabur exec <service-name> /bin/bash

# 導出
pg_dump "$DATABASE_URL" \
  --format=custom \
  --no-owner \
  --no-acl \
  --file=/tmp/backup.dump

# 退出
exit

# 下載
zeabur download <service-name> /tmp/backup.dump
```

---

## ✅ 驗證備份

### **導出完成後驗證：**

```bash
# ==================== 檢查文件大小 ====================
ls -lh zeabur_backup.dump
# 應該 > 1MB（取決於數據量）

# ==================== 檢查備份內容 ====================
pg_restore --list zeabur_backup.dump

# 應該列出所有表和數據

# ==================== 測試恢復（可選）====================
# 在本地 PostgreSQL 測試恢復
createdb test_restore
pg_restore -d test_restore zeabur_backup.dump
psql test_restore -c "\dt"
# 應該看到所有表

# 清理測試
dropdb test_restore
```

---

## 🔄 遷移到 RDS

### **備份文件準備好後：**

```bash
# ==================== 1. 導入到 RDS ====================
pg_restore "$RDS_URL" \
  --verbose \
  --clean \
  --if-exists \
  --no-owner \
  --no-acl \
  zeabur_backup.dump

# ==================== 2. 驗證數據 ====================
psql "$RDS_URL" -c "
  SELECT
    tablename,
    n_live_tup as row_count
  FROM pg_stat_user_tables
  ORDER BY n_live_tup DESC;
"

# ==================== 3. 對比數據量 ====================
# 在 Zeabur（通過容器）
zeabur exec <service> psql "$DATABASE_URL" -c "
  SELECT SUM(n_live_tup) FROM pg_stat_user_tables;
"

# 在 RDS
psql "$RDS_URL" -c "
  SELECT SUM(n_live_tup) FROM pg_stat_user_tables;
"

# 兩者應該相同
```

---

## 🚨 故障排查

### **問題 1: pg_dump 命令不存在**

```bash
# 在 Zeabur 容器內安裝
apt-get update
apt-get install -y postgresql-client

# 或
apk add postgresql-client  # Alpine Linux
```

### **問題 2: 無法訪問內部服務名**

```bash
# 確保在應用容器內執行
# 不要在本地執行

# 檢查連接
zeabur exec <service> env | grep DATABASE_URL
```

### **問題 3: 權限不足**

```bash
# 確保使用 root 用戶（從 DATABASE_URL）
# 或聯繫 Zeabur 支持獲取完整權限
```

---

## 📞 需要幫助？

### **Zeabur 官方支持：**

```
文檔: https://zeabur.com/docs
Discord: https://discord.gg/zeabur
Support: support@zeabur.com
```

---

## 📝 檢查清單

導出前：
- [ ] 已登入 Zeabur Dashboard
- [ ] 已找到 PostgreSQL 服務
- [ ] 已記錄數據庫連接信息
- [ ] 已決定使用哪種導出方案

導出後：
- [ ] 備份文件已下載到本地
- [ ] 已驗證文件大小 > 0
- [ ] 已測試備份可以恢復
- [ ] 已保存多個備份副本

準備遷移：
- [ ] RDS 已創建並可訪問
- [ ] 已測試 RDS 連接
- [ ] 已準備遷移腳本
- [ ] 已選擇遷移時間窗口

---

**創建日期:** 2026-02-10
**數據庫類型:** Zeabur PostgreSQL
**狀態:** 準備就緒
