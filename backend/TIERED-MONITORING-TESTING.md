# 分級監測策略 - 測試驗證計劃

## ✅ 已完成的修改

### 1. Product 模型添加監測優先級字段

**新增字段**：
```python
monitoring_priority: Mapped[str] = mapped_column(
    String(10),
    default="B",
    comment="監測優先級: A=核心商品(3次/天), B=一般商品(2次/天), C=低優先(1次/天)"
)
```

**數據庫遷移**：`20260211_1547_2a0ebbab370c_add_monitoring_priority_to_products.py`

---

### 2. Celery Beat 定時任務（celery_app.py）

**修改前**：
```python
# 08:00: 所有商品
# 20:00: 所有商品
```

**修改後**：
```python
# 08:00: A + B + C（所有商品）
# 14:00: A（僅核心商品）
# 20:00: A + B（核心 + 一般商品）
# 02:00: 自動分類商品優先級
```

**關鍵任務**：
1. `scrape-competitors-morning-all` - 08:00，爬取所有商品
2. `scrape-competitors-afternoon-priority` - 14:00，僅爬取 A 級商品
3. `scrape-competitors-evening-ab` - 20:00，爬取 A + B 級商品
4. `auto-classify-monitoring-priority` - 02:00，自動分類優先級

---

### 3. 分級爬取任務（scrape_tasks.py）

**新增任務**：

#### 3.1 `scrape_by_priority(priorities)`
- 按優先級爬取競品商品
- 參數：`priorities` - 優先級列表，例如 `["A", "B", "C"]`
- 邏輯：查詢符合優先級的商品映射的競品，為每個競爭對手創建爬取任務

#### 3.2 `auto_classify_monitoring_priority()`
- 自動分類商品監測優先級（基於利潤率）
- 分類標準：
  - A級：利潤率 > 50% 且有競品映射
  - B級：利潤率 20-50%
  - C級：利潤率 < 20% 或無競品映射

---

### 4. API 端點（products.py）

**新增端點**：

#### 4.1 `PATCH /api/v1/products/{product_id}/monitoring-priority`
- 手動更新商品的監測優先級

#### 4.2 `GET /api/v1/products/monitoring-priority/stats`
- 獲取監測優先級統計（各級別商品數量、預估每日爬取次數）

#### 4.3 `POST /api/v1/products/monitoring-priority/auto-classify`
- 手動觸發自動分類任務

---

## 📊 分級監測策略說明

### 商品分級標準

| 級別 | 類型 | 監測頻率 | 每日爬取次數 | 適用商品 |
|------|------|---------|-------------|---------|
| **A 級** | 核心商品 | 每天 3 次 | 08:00, 14:00, 20:00 | 高利潤率 (>50%) + 有競品映射 |
| **B 級** | 一般商品 | 每天 2 次 | 08:00, 20:00 | 中等利潤率 (20-50%) |
| **C 級** | 低優先 | 每天 1 次 | 08:00 | 低利潤率 (<20%) 或無競品 |

### 配額影響（假設 150 個商品）

| 分配方案 | A級 | B級 | C級 | 每日消耗 | 每月消耗 | 使用率（Standard Plan） |
|---------|-----|-----|-----|---------|---------|------------------------|
| **均勻分配** | 50 | 50 | 50 | (50×3)+(50×2)+(50×1)=300 | 9,000 | 9% |
| **金字塔分配** | 30 | 60 | 60 | (30×3)+(60×2)+(60×1)=270 | 8,100 | 8.1% |
| **核心優先** | 60 | 60 | 30 | (60×3)+(60×2)+(30×1)=330 | 9,900 | 9.9% |

**結論**：所有分配方案都在 Standard Plan 的充足範圍內（< 10% 使用率）。

---

## 🧪 測試計劃

### 前置條件

1. ✅ 執行數據庫遷移：`alembic upgrade head`
2. ✅ Celery Worker 和 Beat 運行中
3. ✅ 至少有 10 個商品，且有不同的利潤率
4. ✅ 部分商品有競品映射

---

### 測試場景 1: 數據庫遷移驗證

#### 步驟 1: 執行遷移
```bash
cd backend
alembic upgrade head
```

**預期輸出**：
```
INFO  [alembic.runtime.migration] Running upgrade add_outputs_per_image -> 2a0ebbab370c, add_monitoring_priority_to_products
```

#### 步驟 2: 驗證欄位添加
```sql
-- 檢查 products 表是否有 monitoring_priority 欄位
SELECT column_name, data_type, column_default
FROM information_schema.columns
WHERE table_name = 'products' AND column_name = 'monitoring_priority';
```

**預期結果**：
```
column_name          | monitoring_priority
data_type            | character varying(10)
column_default       | 'B'::character varying
```

#### 步驟 3: 檢查現有商品的默認值
```sql
SELECT sku, monitoring_priority
FROM products
LIMIT 5;
```

**預期結果**：所有商品的 `monitoring_priority` 都是 `'B'`（默認值）

---

### 測試場景 2: 自動分類功能

#### 步驟 1: 準備測試數據

```sql
-- 創建不同利潤率的商品
-- A級候選：高利潤率 > 50% + 有競品
UPDATE products SET price = 300, cost = 150, monitoring_priority = 'B' WHERE sku = 'TEST-001';

-- B級候選：中等利潤率 20-50%
UPDATE products SET price = 200, cost = 160, monitoring_priority = 'B' WHERE sku = 'TEST-002';

-- C級候選：低利潤率 < 20%
UPDATE products SET price = 100, cost = 90, monitoring_priority = 'B' WHERE sku = 'TEST-003';

-- 確保 TEST-001 有競品映射
-- （假設已有）
```

#### 步驟 2: 手動觸發自動分類

**API 調用**：
```bash
curl -X POST "http://localhost:8000/api/v1/products/monitoring-priority/auto-classify"
```

**預期響應**：
```json
{
  "success": true,
  "task_id": "abc123-def456-...",
  "message": "自動分類任務已啟動，請稍後查看結果"
}
```

#### 步驟 3: 等待任務完成（約 10 秒）

#### 步驟 4: 驗證分類結果

```sql
SELECT
    sku,
    price,
    cost,
    ROUND(((price - cost) / cost * 100)::numeric, 2) AS profit_margin,
    monitoring_priority
FROM products
WHERE sku IN ('TEST-001', 'TEST-002', 'TEST-003');
```

**預期結果**：
```
sku        | price | cost | profit_margin | monitoring_priority
-----------|-------|------|---------------|--------------------
TEST-001   | 300   | 150  | 100.00        | A  (利潤率 > 50% + 有競品)
TEST-002   | 200   | 160  | 25.00         | B  (利潤率 20-50%)
TEST-003   | 100   | 90   | 11.11         | C  (利潤率 < 20%)
```

---

### 測試場景 3: 手動設置監測優先級

#### API 調用：
```bash
# 將 TEST-002 升級為 A 級
curl -X PATCH "http://localhost:8000/api/v1/products/<product_id>/monitoring-priority" \
  -H "Content-Type: application/json" \
  -d '{"priority": "A"}'
```

#### 預期響應：
```json
{
  "id": "...",
  "sku": "TEST-002",
  "monitoring_priority": "A",
  ...
}
```

#### 驗證：
```sql
SELECT sku, monitoring_priority FROM products WHERE sku = 'TEST-002';
```

**預期結果**：`monitoring_priority = 'A'`

---

### 測試場景 4: 監測優先級統計

#### API 調用：
```bash
curl -X GET "http://localhost:8000/api/v1/products/monitoring-priority/stats"
```

#### 預期響應：
```json
{
  "a_count": 30,
  "b_count": 60,
  "c_count": 60,
  "total": 150,
  "daily_scrapes_estimate": 270
}
```

**解釋**：
- A級 30 個 × 3 次 = 90
- B級 60 個 × 2 次 = 120
- C級 60 個 × 1 次 = 60
- **每日總爬取次數**: 270

**每月消耗**: 270 × 30 = **8,100 credits**（8.1% 使用率）

---

### 測試場景 5: 分級爬取驗證

#### 步驟 1: 等待 Celery Beat 自動觸發（或手動觸發）

**08:00（所有商品）**：
```bash
celery -A app.tasks.celery_app call app.tasks.scrape_tasks.scrape_by_priority --kwargs='{"priorities": ["A", "B", "C"]}'
```

**14:00（僅 A 級）**：
```bash
celery -A app.tasks.celery_app call app.tasks.scrape_tasks.scrape_by_priority --kwargs='{"priorities": ["A"]}'
```

**20:00（A + B 級）**：
```bash
celery -A app.tasks.celery_app call app.tasks.scrape_tasks.scrape_by_priority --kwargs='{"priorities": ["A", "B"]}'
```

#### 步驟 2: 驗證爬取記錄

```sql
-- 檢查最新的爬取日誌
SELECT
    task_id,
    task_type,
    status,
    products_total,
    products_scraped,
    started_at,
    completed_at
FROM scrape_logs
ORDER BY started_at DESC
LIMIT 5;
```

**預期**：
- 08:00 爬取：`products_total` 應該最多（包含所有商品）
- 14:00 爬取：`products_total` 應該最少（僅 A 級商品）
- 20:00 爬取：`products_total` 介於兩者之間（A + B 級商品）

---

### 測試場景 6: 定時任務驗證

#### 步驟 1: 檢查 Celery Beat 排程

```bash
celery -A app.tasks.celery_app inspect scheduled
```

**預期輸出**：應該看到以下任務：
- `scrape-competitors-morning-all` @ 08:00
- `scrape-competitors-afternoon-priority` @ 14:00
- `scrape-competitors-evening-ab` @ 20:00
- `auto-classify-monitoring-priority` @ 02:00

#### 步驟 2: 驗證任務執行（檢查日誌）

```bash
# 檢查 Celery Beat 日誌
tail -f backend/logs/celery-beat.log | grep "scrape-competitors"

# 檢查 Celery Worker 日誌
tail -f backend/logs/celery-worker.log | grep "scrape_by_priority"
```

---

## 📊 驗證檢查清單

### 功能驗收：
- [ ] 數據庫遷移成功，`monitoring_priority` 欄位已添加
- [ ] 自動分類功能正確（A/B/C 級分類準確）
- [ ] 手動設置監測優先級 API 正常工作
- [ ] 監測優先級統計 API 返回正確數據
- [ ] 分級爬取任務按優先級正確爬取
- [ ] Celery Beat 定時任務按排程執行
- [ ] 08:00 爬取所有商品（A+B+C）
- [ ] 14:00 僅爬取 A 級商品
- [ ] 20:00 爬取 A+B 級商品
- [ ] 02:00 自動分類商品優先級

### 配額驗收：
- [ ] 150 商品分級監測：每月消耗 < 10,000 credits
- [ ] 配額使用率 < 10%（Standard Plan）
- [ ] Firecrawl 配額監控正常

### 商業驗收：
- [ ] A 級核心商品監測頻率更高，反應更快
- [ ] B 級一般商品監測適中，平衡成本和效果
- [ ] C 級低優先商品減少監測，節省配額
- [ ] 配額使用更高效，覆蓋更多商品

---

## 💰 成本效益分析

### 配額優化效果

**優化前（P0-1）**：
- 150 商品 × 2 次/天 = 300 credits/天
- 每月消耗：9,000 credits

**優化後（分級監測）**：
- 假設分配：30 A級 + 60 B級 + 60 C級
- 每日消耗：(30×3) + (60×2) + (60×1) = 270 credits/天
- 每月消耗：8,100 credits
- **節省**：10%

**但是！更重要的是**：
- A 級核心商品：監測頻率 **提高 50%**（2次 → 3次）
- 反應時間：最快 6 小時檢測到變化（vs 12 小時）
- 更精準地分配監測資源到高價值商品

---

## 🎯 推薦配置

### 金字塔分配（推薦）

| 級別 | 商品數 | 佔比 | 每日爬取 | 特點 |
|------|-------|------|---------|------|
| **A級** | 30 | 20% | 90 次 | 高利潤、高競爭的核心商品 |
| **B級** | 60 | 40% | 120 次 | 主力商品 |
| **C級** | 60 | 40% | 60 次 | 長尾商品或低優先級 |

**每月消耗**：8,100 credits（8.1% 使用率）

**優勢**：
- 核心商品監測頻率最高
- 配額分配合理
- 覆蓋所有商品

---

## 🐛 常見問題排查

### 問題 1: 遷移失敗

**可能原因**：
1. 數據庫連接問題
2. 欄位已存在

**排查**：
```bash
# 檢查當前遷移版本
alembic current

# 查看遷移歷史
alembic history

# 如果需要回滾
alembic downgrade -1
```

### 問題 2: 自動分類沒有正確分類

**可能原因**：
1. 商品沒有設置 `price` 或 `cost`
2. 商品沒有競品映射

**排查**：
```sql
-- 檢查哪些商品沒有價格或成本
SELECT sku, price, cost
FROM products
WHERE price IS NULL OR cost IS NULL OR cost = 0;

-- 檢查哪些商品沒有競品映射
SELECT p.sku, COUNT(pcm.id) AS competitor_count
FROM products p
LEFT JOIN product_competitor_mappings pcm ON p.id = pcm.product_id
GROUP BY p.sku
HAVING COUNT(pcm.id) = 0;
```

### 問題 3: Celery Beat 沒有執行分級爬取

**可能原因**：
1. Celery Beat 沒有重啟（配置未生效）
2. 時區設置錯誤

**排查**：
```bash
# 重啟 Celery Beat
pkill -f "celery.*beat"
celery -A app.tasks.celery_app beat --loglevel=info

# 檢查排程
celery -A app.tasks.celery_app inspect scheduled
```

---

## ✅ 分級監測策略完成標準

### 功能驗收：
- [x] 數據庫模型添加 `monitoring_priority` 欄位
- [x] 數據庫遷移創建並測試通過
- [x] Celery Beat 配置分級定時任務
- [x] 實現 `scrape_by_priority` 任務
- [x] 實現 `auto_classify_monitoring_priority` 任務
- [x] API 端點：手動設置優先級
- [x] API 端點：獲取優先級統計
- [x] API 端點：觸發自動分類

### 商業驗收：
- [ ] A 級核心商品監測頻率提高 50%
- [ ] 配額使用更高效（節省 10% 或覆蓋更多商品）
- [ ] 自動分類準確率 > 95%
- [ ] 手動調整靈活方便

### 穩定性驗收：
- [ ] 連續運行 7 天無錯誤
- [ ] 分級爬取按排程準確執行
- [ ] 自動分類每天正常運行
- [ ] 配額使用在預期範圍內

---

## 📝 變更記錄

| 日期 | 修改內容 | 文件 |
|------|---------|------|
| 2026-02-11 | 添加 monitoring_priority 欄位到 Product 模型 | product.py |
| 2026-02-11 | 創建數據庫遷移 | 2a0ebbab370c_add_monitoring_priority_to_products.py |
| 2026-02-11 | 修改 Celery Beat 配置為分級監測 | celery_app.py |
| 2026-02-11 | 實現 scrape_by_priority 任務 | scrape_tasks.py |
| 2026-02-11 | 實現 auto_classify_monitoring_priority 任務 | scrape_tasks.py |
| 2026-02-11 | 添加監測優先級管理 API | products.py |
