# GoGoJap 數據庫遷移策略 - 零停機方案

**創建日期:** 2026-02-10
**目標:** 最小化業務中斷，確保數據完整性

---

## 🎯 遷移原則

1. **業務優先** - 現有業務不受影響
2. **數據安全** - 多重備份保障
3. **可回滾** - 隨時可以回退
4. **最小停機** - 控制在 30-60 分鐘內

---

## 📅 時間線規劃

### Phase 1: 準備期（等待 Lightsail 批准，1-2 天）

#### ✅ 可以做的事（不影響現有系統）

**1. 繼續業務運營**
```yaml
Neon 數據庫:
  ✅ 繼續接收新數據
  ✅ Firecrawl 繼續抓取
  ✅ 價格監控繼續運行
  ✅ AI 分析繼續工作

說明: 所有現有功能照常運行
風險: 零
```

**2. 創建 AWS 資源**
```yaml
創建 RDS:
  ✅ 在 AWS 創建新的 PostgreSQL 實例
  ✅ 配置安全組
  ✅ 測試連接

創建 S3:
  ✅ 創建存儲桶
  ✅ 配置 CORS

說明: 新資源與現有系統隔離，互不影響
風險: 零
```

**3. 準備遷移工具**
```yaml
本地測試:
  ✅ 測試 pg_dump 命令
  ✅ 驗證 RDS 連接
  ✅ 運行 dry-run 測試

說明: 在本地環境測試，不影響生產數據
風險: 零
```

**4. 創建備份**
```yaml
備份策略:
  ✅ 導出 Neon 數據庫完整備份
  ✅ 保存到本地
  ✅ 上傳到 S3（額外備份）

說明: 多重備份確保安全
風險: 零
```

---

### Phase 2: 遷移日（選擇低峰時段）

#### 建議時間窗口

```yaml
最佳時間:
  - 週末凌晨 2:00-4:00
  - 或平日凌晨 3:00-5:00
  - 用戶最少的時段

準備:
  - 提前 24 小時通知用戶
  - 準備維護頁面
  - 團隊待命
```

#### 詳細步驟（30-60 分鐘）

**Step 1: 進入維護模式（5 分鐘）**

```bash
# ==================== 1. 顯示維護頁面 ====================
# 在前端顯示:
# "系統維護中，預計 30 分鐘後恢復"

# ==================== 2. 停止寫入操作 ====================
# 方式 A: 完全停機
sudo supervisorctl stop gogojap-celery
sudo supervisorctl stop gogojap

# 方式 B: 只讀模式（更優雅）
# 在應用中設置 READ_ONLY=True
# 用戶可以查看，但不能修改

# ==================== 3. 確認無活動連接 ====================
psql "$NEON_URL" -c "
  SELECT count(*) FROM pg_stat_activity
  WHERE datname = 'gogojap' AND state = 'active';
"
# 應該顯示 0 或很少
```

**Step 2: 最終備份（5 分鐘）**

```bash
# ==================== 創建時間戳 ====================
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="gogojap_final_backup_${TIMESTAMP}.dump"

# ==================== 導出完整數據 ====================
pg_dump "$NEON_URL" \
  --format=custom \
  --no-owner \
  --no-acl \
  --verbose \
  --file="$BACKUP_FILE"

# ==================== 記錄數據統計 ====================
psql "$NEON_URL" -c "
  SELECT
    tablename,
    n_live_tup as row_count
  FROM pg_stat_user_tables
  ORDER BY n_live_tup DESC;
" > pre_migration_stats.txt

echo "✅ 備份完成: $BACKUP_FILE"
```

**Step 3: 導入到 RDS（10-20 分鐘）**

```bash
# ==================== 導入數據 ====================
pg_restore "$RDS_URL" \
  --verbose \
  --clean \
  --if-exists \
  --no-owner \
  --no-acl \
  "$BACKUP_FILE"

# ==================== 驗證數據 ====================
psql "$RDS_URL" -c "
  SELECT
    tablename,
    n_live_tup as row_count
  FROM pg_stat_user_tables
  ORDER BY n_live_tup DESC;
" > post_migration_stats.txt

# ==================== 對比統計 ====================
echo "對比遷移前後數據:"
diff pre_migration_stats.txt post_migration_stats.txt

# 應該顯示: 無差異 或 完全相同
```

**Step 4: 切換應用（5 分鐘）**

```bash
# ==================== 更新環境變量 ====================
# 在 Lightsail/EC2 實例上
nano /var/www/gogojap/backend/.env

# 修改:
# DATABASE_URL=postgresql://postgres:<pass>@<rds-endpoint>/gogojap

# ==================== 運行數據庫遷移 ====================
cd /var/www/gogojap/backend
source ../venv/bin/activate
alembic upgrade head

# ==================== 重啟服務 ====================
sudo supervisorctl restart gogojap
sudo supervisorctl restart gogojap-celery
sudo supervisorctl restart gogojap-celery-beat

# ==================== 檢查狀態 ====================
sudo supervisorctl status
# 所有服務應該顯示 RUNNING
```

**Step 5: 驗證功能（10 分鐘）**

```bash
# ==================== 1. API 健康檢查 ====================
curl https://api.gogojap.com/health
# 應該返回 200 OK

# ==================== 2. 測試數據庫查詢 ====================
curl https://api.gogojap.com/api/v1/products?limit=10
# 應該返回商品列表

# ==================== 3. 測試寫入操作 ====================
# 在應用中創建一個測試記錄
# 確認可以成功寫入 RDS

# ==================== 4. 檢查錯誤日誌 ====================
tail -f /var/log/gogojap/error.log
# 不應該有錯誤

# ==================== 5. 測試 Celery 任務 ====================
# 手動觸發一個抓取任務
# 確認可以正常執行
```

**Step 6: 恢復服務（5 分鐘）**

```bash
# ==================== 1. 移除維護通知 ====================
# 前端移除維護頁面

# ==================== 2. 恢復所有功能 ====================
# 取消只讀模式（如果使用）
# 重新啟動所有定時任務

# ==================== 3. 監控系統 ====================
# 持續監控 30 分鐘
# 檢查:
#   - API 響應時間
#   - 數據庫連接數
#   - 錯誤率
#   - 任務執行情況
```

---

### Phase 3: 遷移後（1-2 週）

#### 穩定期監控

```yaml
第 1 天:
  ✅ 密切監控所有指標
  ✅ 檢查數據一致性
  ✅ 保留 Neon 備份（不刪除）

第 1 週:
  ✅ 每日檢查系統運行
  ✅ 對比 RDS 和 Neon 數據（如果 Neon 還在運行）
  ✅ 收集性能數據

第 2 週:
  ✅ 確認系統穩定
  ✅ 準備清理舊資源
```

#### 清理舊資源

```yaml
確認穩定後（2 週+）:
  ⚠️ 保留 Neon 最終備份文件
  ⚠️ 可以停止 Neon 數據庫（但不刪除）
  ⚠️ 保留 Zeabur 應用作為緊急備份

1 個月後:
  ✅ 完全刪除 Neon 數據庫
  ✅ 取消 Zeabur 訂閱
  ✅ 清理 Cloudflare R2（如果已遷移到 S3）
```

---

## 🔄 應急回滾方案

### 如果遷移失敗怎麼辦？

**回滾步驟（5 分鐘內恢復）:**

```bash
# ==================== 1. 立即切換回 Neon ====================
# 修改環境變量
DATABASE_URL=<原來的 Neon URL>

# 重啟服務
sudo supervisorctl restart all

# ==================== 2. 驗證服務恢復 ====================
curl https://api.gogojap.com/health

# ==================== 3. 移除維護通知 ====================
# 系統恢復正常

# ==================== 4. 分析問題 ====================
# 檢查日誌
# 找出失敗原因
# 擇期重試
```

**關鍵點:**
- Neon 數據庫在確認穩定前**不要刪除**
- 隨時可以切換回去
- 零數據丟失風險

---

## 📊 數據完整性驗證

### 自動驗證腳本

```bash
#!/bin/bash
# verify-migration.sh - 驗證遷移完整性

echo "==================== 驗證數據遷移 ===================="

# 連接字符串
NEON_URL="postgresql://..."
RDS_URL="postgresql://..."

# 1. 表數量對比
echo "1. 檢查表數量..."
NEON_TABLES=$(psql "$NEON_URL" -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")
RDS_TABLES=$(psql "$RDS_URL" -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")

if [ "$NEON_TABLES" -eq "$RDS_TABLES" ]; then
  echo "✅ 表數量一致: $NEON_TABLES"
else
  echo "❌ 表數量不一致! Neon: $NEON_TABLES, RDS: $RDS_TABLES"
  exit 1
fi

# 2. 行數對比
echo "2. 檢查各表行數..."
psql "$NEON_URL" -t -c "
  SELECT tablename, n_live_tup
  FROM pg_stat_user_tables
  ORDER BY tablename;
" > /tmp/neon_rows.txt

psql "$RDS_URL" -t -c "
  SELECT tablename, n_live_tup
  FROM pg_stat_user_tables
  ORDER BY tablename;
" > /tmp/rds_rows.txt

if diff /tmp/neon_rows.txt /tmp/rds_rows.txt > /dev/null; then
  echo "✅ 所有表行數一致"
else
  echo "⚠️ 行數差異:"
  diff /tmp/neon_rows.txt /tmp/rds_rows.txt
fi

# 3. 索引檢查
echo "3. 檢查索引..."
NEON_INDEXES=$(psql "$NEON_URL" -t -c "SELECT COUNT(*) FROM pg_indexes WHERE schemaname = 'public';")
RDS_INDEXES=$(psql "$RDS_URL" -t -c "SELECT COUNT(*) FROM pg_indexes WHERE schemaname = 'public';")

if [ "$NEON_INDEXES" -eq "$RDS_INDEXES" ]; then
  echo "✅ 索引數量一致: $NEON_INDEXES"
else
  echo "⚠️ 索引數量不一致! Neon: $NEON_INDEXES, RDS: $RDS_INDEXES"
fi

# 4. 序列檢查
echo "4. 檢查序列..."
NEON_SEQUENCES=$(psql "$NEON_URL" -t -c "SELECT COUNT(*) FROM information_schema.sequences WHERE sequence_schema = 'public';")
RDS_SEQUENCES=$(psql "$RDS_URL" -t -c "SELECT COUNT(*) FROM information_schema.sequences WHERE sequence_schema = 'public';")

if [ "$NEON_SEQUENCES" -eq "$RDS_SEQUENCES" ]; then
  echo "✅ 序列數量一致: $NEON_SEQUENCES"
else
  echo "⚠️ 序列數量不一致! Neon: $NEON_SEQUENCES, RDS: $RDS_SEQUENCES"
fi

echo ""
echo "==================== 驗證完成 ===================="
echo "如果所有檢查都是 ✅，遷移成功！"
```

---

## 💡 最佳實踐提示

### 1. **通知用戶**
```
提前 24 小時發送通知:
"系統將於 X 月 X 日凌晨 2:00-3:00 進行維護升級，
期間服務可能短暫中斷。感謝您的理解！"
```

### 2. **選擇低峰時段**
```
查看 Google Analytics / 訪問日誌
找出用戶最少的時段
通常是凌晨 2:00-5:00
```

### 3. **團隊待命**
```
確保至少 1 人待命
可以處理突發問題
快速回滾（如需要）
```

### 4. **準備維護頁面**
```html
<!-- maintenance.html -->
<div class="maintenance">
  <h1>系統維護中</h1>
  <p>預計 30 分鐘後恢復</p>
  <p>造成不便，敬請見諒</p>
</div>
```

### 5. **記錄一切**
```
記錄每個步驟的時間
截圖重要信息
保存所有日誌
方便事後復盤
```

---

## 📈 成功指標

### 遷移成功的標準

```yaml
數據完整性:
  ✅ 所有表都已遷移
  ✅ 行數完全一致
  ✅ 索引和序列正確

功能正常:
  ✅ API 所有 endpoints 正常
  ✅ 數據庫查詢成功
  ✅ 寫入操作正常
  ✅ Celery 任務執行正常

性能達標:
  ✅ API 響應時間 < 200ms
  ✅ 數據庫查詢 < 50ms
  ✅ 無錯誤日誌

用戶體驗:
  ✅ 停機時間 < 60 分鐘
  ✅ 功能無損失
  ✅ 用戶無感知（除了短暫維護）
```

---

## 🎯 總結

### 關鍵原則

1. **準備期可以繼續採集數據** - 不影響遷移
2. **多重備份** - 確保安全
3. **可回滾** - 隨時可以退回
4. **最小停機** - 控制在 30-60 分鐘
5. **驗證充分** - 確保數據完整

### 時間規劃

```
準備期: 1-2 天（等待批准 + 創建資源）
  → 業務照常運行 ✅

遷移日: 30-60 分鐘
  → 選擇低峰時段

穩定期: 1-2 週
  → 保留所有備份

清理期: 1 個月後
  → 刪除舊資源
```

---

**創建日期:** 2026-02-10
**版本:** 1.0
**狀態:** 準備就緒
