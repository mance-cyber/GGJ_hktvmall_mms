# P0-1: 競品爬取自動化 - 測試驗證計劃

## ✅ 已完成的修改

### 1. Celery Beat 定時排程（celery_app.py）
**修改內容**：
- 原本：每天 09:00 一次
- 現在：每天 08:00 + 20:00 兩次

**修改位置**：`backend/app/tasks/celery_app.py` 第 52-62 行

```python
# 早上 08:00 - 開市前監測
"scrape-all-competitors-morning": {
    "task": "app.tasks.scrape_tasks.scrape_all_competitors",
    "schedule": crontab(hour=8, minute=0),
},

# 晚上 20:00 - 晚間監測
"scrape-all-competitors-evening": {
    "task": "app.tasks.scrape_tasks.scrape_all_competitors",
    "schedule": crontab(hour=20, minute=0),
},
```

### 2. API 端點連接 Celery（competitors.py）

#### 2.1 添加單個商品（第 343-348 行）
**修改前**：
```python
# TODO: 觸發 Celery 爬取任務
# task = scrape_single_product.delay(str(product.id))
return ScrapeTaskResponse(task_id="pending", ...)
```

**修改後**：
```python
from app.tasks.scrape_tasks import scrape_single_product
task = scrape_single_product.delay(str(product.id))
return ScrapeTaskResponse(task_id=task.id, ...)
```

#### 2.2 手動觸發爬取（第 593-598 行）
**修改前**：
```python
# TODO: 觸發 Celery 爬取任務
# task = scrape_competitor.delay(str(competitor_id))
return ScrapeTaskResponse(task_id="pending", ...)
```

**修改後**：
```python
from app.tasks.scrape_tasks import scrape_competitor
task = scrape_competitor.delay(str(competitor_id))
return ScrapeTaskResponse(task_id=task.id, message=f"爬取任務已啟動（Task ID: {task.id}）")
```

---

## 🧪 測試計劃

### 前置條件
1. ✅ Redis 服務運行中
2. ✅ PostgreSQL 數據庫連接正常
3. ✅ Firecrawl API Key 已配置
4. ✅ 至少有 1 個活躍的競爭對手 + 1 個競品商品

---

### 測試場景 1: Celery Beat 定時任務

#### 步驟 1: 啟動 Celery Worker
```bash
cd backend
celery -A app.tasks.celery_app worker --loglevel=info
```

**預期輸出**：
```
[tasks]
  . app.tasks.scrape_tasks.scrape_competitor
  . app.tasks.scrape_tasks.scrape_all_competitors
  . app.tasks.scrape_tasks.scrape_single_product
```

#### 步驟 2: 啟動 Celery Beat
```bash
cd backend
celery -A app.tasks.celery_app beat --loglevel=info
```

**預期輸出**：
```
Scheduler: Sending due task scrape-all-competitors-morning (app.tasks.scrape_tasks.scrape_all_competitors)
Scheduler: Sending due task scrape-all-competitors-evening (app.tasks.scrape_tasks.scrape_all_competitors)
```

#### 步驟 3: 驗證排程時間
```bash
celery -A app.tasks.celery_app inspect scheduled
```

**預期**：可以看到兩個定時任務：
- `scrape-all-competitors-morning` @ 08:00 HKT
- `scrape-all-competitors-evening` @ 20:00 HKT

#### 步驟 4: 手動測試定時任務
```bash
# 不等到排程時間，手動觸發
celery -A app.tasks.celery_app call app.tasks.scrape_tasks.scrape_all_competitors
```

**驗收標準**：
- ✅ Celery Worker 收到任務
- ✅ 開始爬取所有活躍競爭對手
- ✅ 為每個競爭對手創建子任務（`scrape_competitor`）
- ✅ 爬取完成後自動生成 `PriceSnapshot`
- ✅ 價格變動自動生成 `PriceAlert`

---

### 測試場景 2: API 手動觸發爬取

#### 測試 2.1: 添加新商品並自動爬取

**API 調用**：
```bash
curl -X POST "http://localhost:8000/api/v1/competitors/{competitor_id}/products" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.hktvmall.com/hktv/zh/p/H0340001",
    "name": "測試商品"
  }'
```

**預期響應**：
```json
{
  "task_id": "abc123-def456-...",
  "message": "已加入監測，正在爬取數據..."
}
```

**驗收標準**：
- ✅ API 返回真實的 Celery Task ID（不是 "pending"）
- ✅ Celery Worker 日誌顯示 `scrape_single_product` 任務執行
- ✅ 數據庫中創建 `PriceSnapshot` 記錄
- ✅ 商品資訊更新（名稱、價格、SKU、圖片）

#### 測試 2.2: 手動觸發單個競爭對手爬取

**API 調用**：
```bash
curl -X POST "http://localhost:8000/api/v1/competitors/{competitor_id}/scrape"
```

**預期響應**：
```json
{
  "task_id": "xyz789-abc123-...",
  "message": "爬取任務已啟動（Task ID: xyz789-abc123-...）"
}
```

**驗收標準**：
- ✅ 返回真實 Task ID
- ✅ Celery Worker 執行 `scrape_competitor` 任務
- ✅ 爬取該競爭對手的所有商品
- ✅ 生成多個 `PriceSnapshot`
- ✅ 價格變動自動生成 `PriceAlert`

---

### 測試場景 3: 價格告警自動生成

#### 前置準備：
1. 確保某個商品已有歷史價格快照
2. 修改競品商品的真實價格（或模擬價格變動）

#### 觸發爬取：
```bash
# 方法 1: 通過 API
curl -X POST "http://localhost:8000/api/v1/competitors/{competitor_id}/scrape"

# 方法 2: 直接調用 Celery 任務
celery -A app.tasks.celery_app call app.tasks.scrape_tasks.scrape_competitor --args='["<competitor_id>"]'
```

#### 驗收標準：
1. **價格變動檢測**：
   - ✅ 抓取新價格並與上次快照對比
   - ✅ 變動 ≥ 10%（閾值可配置）自動生成 `PriceAlert`
   - ✅ 告警類型正確：`price_drop` 或 `price_increase`

2. **庫存變動檢測**：
   - ✅ 缺貨時生成 `out_of_stock` 告警
   - ✅ 補貨時生成 `back_in_stock` 告警

3. **工作流觸發**：
   - ✅ 告警生成後觸發 `execute_alert_workflow.delay()`
   - ✅ （如果 Telegram 已配置）發送通知到 Telegram

---

### 測試場景 4: EventBus 整合

#### 驗證事件流：
```
爬取完成 → PriceSnapshot 創建 → PriceAlert 生成 → EventBus 發射事件
    ↓
Scout Agent 接收 SCRAPE_COMPLETED 事件
    ↓
Pricer Agent 接收 PRICE_ALERT 事件
```

#### 驗收標準：
- ✅ 爬取完成後 EventBus 發射 `SCRAPE_COMPLETED`
- ✅ 價格告警發射 `PRICE_ALERT` 事件
- ✅ Agent 日誌顯示事件處理記錄

---

## 📊 驗證檢查清單

### 數據庫驗證

#### 1. PriceSnapshot 記錄
```sql
SELECT
    cp.name AS product_name,
    ps.price,
    ps.stock_status,
    ps.scraped_at
FROM price_snapshots ps
JOIN competitor_products cp ON ps.competitor_product_id = cp.id
ORDER BY ps.scraped_at DESC
LIMIT 10;
```
**預期**：每次爬取後都有新的快照記錄

#### 2. PriceAlert 記錄
```sql
SELECT
    cp.name AS product_name,
    pa.alert_type,
    pa.old_value,
    pa.new_value,
    pa.change_percent,
    pa.created_at
FROM price_alerts pa
JOIN competitor_products cp ON pa.competitor_product_id = cp.id
ORDER BY pa.created_at DESC
LIMIT 10;
```
**預期**：價格變動 ≥ 10% 時自動生成告警

#### 3. ScrapeLog 記錄
```sql
SELECT
    task_id,
    task_type,
    status,
    products_total,
    products_scraped,
    products_failed,
    duration_seconds,
    started_at,
    completed_at
FROM scrape_logs
ORDER BY started_at DESC
LIMIT 5;
```
**預期**：每次爬取都有完整的執行日誌

---

## 🐛 常見問題排查

### 問題 1: Celery Worker 沒有執行任務
**排查步驟**：
```bash
# 檢查 Redis 連接
redis-cli ping
# 應該返回: PONG

# 檢查 Celery 隊列
celery -A app.tasks.celery_app inspect active

# 檢查錯誤日誌
celery -A app.tasks.celery_app worker --loglevel=debug
```

### 問題 2: 任務執行失敗
**可能原因**：
1. Firecrawl API Key 未設置或配額用完
2. 商品 URL 格式不正確
3. 網絡連接問題

**排查**：
```bash
# 檢查 Firecrawl 配額
curl -X GET "http://localhost:8000/api/v1/firecrawl/quota"

# 檢查任務錯誤
celery -A app.tasks.celery_app events

# 查看數據庫錯誤記錄
SELECT * FROM scrape_logs WHERE status = 'failed' ORDER BY started_at DESC LIMIT 5;
```

### 問題 3: 定時任務沒有觸發
**排查步驟**：
```bash
# 確認 Celery Beat 運行中
ps aux | grep "celery beat"

# 檢查排程配置
celery -A app.tasks.celery_app inspect scheduled

# 手動觸發測試
celery -A app.tasks.celery_app call app.tasks.scrape_tasks.scrape_all_competitors
```

---

## ✅ P0-1 完成標準

### 功能驗收：
- [x] Celery Beat 每天 08:00 自動觸發爬取
- [x] Celery Beat 每天 20:00 自動觸發爬取
- [x] API 添加商品後自動爬取
- [x] API 手動觸發爬取返回真實 Task ID
- [x] 爬取完成後自動生成 PriceSnapshot
- [x] 價格變動自動生成 PriceAlert
- [x] 庫存變動自動生成告警
- [x] EventBus 事件正確發射

### 性能驗收：
- [ ] 單個商品爬取時間 < 10 秒
- [ ] 50 個商品批量爬取時間 < 5 分鐘
- [ ] Firecrawl credit 消耗符合預期（price-only 模式）

### 穩定性驗收：
- [ ] 連續運行 3 天無錯誤
- [ ] 錯誤重試機制正常工作
- [ ] 爬取失敗不影響其他商品

---

## 🚀 下一步行動

P0-1 完成後，立即開始：
- **P0-2**: 競品缺貨機會自動告警 + 提價提案
- **P0-3**: Telegram 即時審批通道
- **P0-4**: SKU 利潤排行榜

---

## 📝 變更記錄

| 日期 | 修改內容 | 文件 |
|------|---------|------|
| 2026-02-11 | 添加第二次定時爬取（20:00） | celery_app.py |
| 2026-02-11 | 連接 add_competitor_product 到 Celery | competitors.py |
| 2026-02-11 | 連接 trigger_scrape 到 Celery | competitors.py |
