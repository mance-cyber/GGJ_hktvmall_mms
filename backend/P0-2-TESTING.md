# P0-2: 競品缺貨機會自動告警 + 提價提案 - 測試驗證計劃

## ✅ 已完成的修改

### 1. Pricer Agent 添加缺貨事件處理（pricer.py）

**新增 Handler**: `_on_competitor_stockout`

**核心邏輯**：
```python
競品缺貨事件觸發
    ↓
找到對應的我方商品
    ↓
檢查「所有」競品是否都缺貨  ← _check_all_competitors_stockout()
    ↓
如果是唯一有貨 → 黃金機會！
    ↓
生成提價提案（+7%）
    ↓
Telegram 推送「機會窗口」通知
```

**關鍵方法**：
1. `_on_competitor_stockout` - 主處理邏輯
2. `_check_all_competitors_stockout` - 檢查所有競品庫存狀態

### 2. MRC Dashboard 機會雷達（market_response.py）

**修改內容**：
- 填充 `opportunities` 列表（原本是空的 TODO）
- 填充 `price_alerts` 列表（原本是空的 TODO）
- 更新 `opportunities_count` 真實數據

**新增 Helper Functions**：
- `_get_stockout_opportunities()` - 查詢缺貨機會
- `_check_all_competitors_stockout()` - 檢查所有競品是否缺貨

---

## 🧪 測試計劃

### 測試場景 1: 競品缺貨事件流

#### 前置條件：
1. 至少有 1 個商品
2. 該商品有 2+ 個競品映射
3. 所有競品的最新 `PriceSnapshot.stock_status = 'out_of_stock'`

#### 觸發方式：
```bash
# 方法 1: 通過爬取自動觸發
# 當爬取發現競品缺貨時，scrape_tasks 會自動生成 PriceAlert
# Scout Agent 收到 SCRAPE_COMPLETED 事件後，發射 COMPETITOR_STOCKOUT 事件

# 方法 2: 手動觸發事件（測試用）
curl -X POST "http://localhost:8000/api/v1/agent-team/emit/competitor.stockout" \
  -H "Content-Type: application/json" \
  -d '{
    "competitor_product_id": "<競品商品 UUID>"
  }'
```

#### 預期結果：
1. ✅ Pricer Agent 接收到 `COMPETITOR_STOCKOUT` 事件
2. ✅ 查詢對應的我方商品
3. ✅ 檢查所有競品庫存（調用 `_check_all_competitors_stockout`）
4. ✅ 如果都缺貨 → 生成提價提案（+7%）
5. ✅ Telegram 推送「🎯 缺貨機會窗口」通知
6. ✅ 提案記錄寫入 `price_proposals` 表

**驗收SQL**：
```sql
-- 檢查是否生成了缺貨機會提案
SELECT
    p.sku,
    p.name_zh,
    pp.current_price,
    pp.proposed_price,
    pp.reason,
    pp.model,
    pp.status,
    pp.created_at
FROM price_proposals pp
JOIN products p ON pp.product_id = p.id
WHERE pp.model = 'agent_pricer_stockout_opportunity'
ORDER BY pp.created_at DESC
LIMIT 5;
```

預期：
- `model = 'agent_pricer_stockout_opportunity'`
- `reason` 包含「🎯 機會窗口」字樣
- `proposed_price > current_price`（提價約 7%）

---

### 測試場景 2: MRC Dashboard 機會雷達

#### API 調用：
```bash
curl -X GET "http://localhost:8000/api/v1/market-response/dashboard"
```

#### 預期響應：
```json
{
  "stats": {
    "opportunities_count": 3  ← 不再是 0
  },
  "opportunities": [  ← 不再是空陣列
    {
      "product_id": "xxx",
      "sku": "H0340001",
      "name": "日本 A5 和牛",
      "current_price": 398.0,
      "opportunity_type": "all_competitors_stockout",
      "competitor_count": 3,
      "description": "3 個競品都缺貨，搶市機會！"
    }
  ],
  "price_alerts": [  ← 不再是空陣列
    {
      "id": "xxx",
      "alert_type": "out_of_stock",
      "competitor_product_id": "yyy",
      "created_at": "2026-02-11T10:30:00Z"
    }
  ]
}
```

**驗收標準**：
- ✅ `opportunities_count` 顯示真實數字
- ✅ `opportunities` 列表包含缺貨機會
- ✅ 每個機會包含：商品名稱、當前價格、競品數量、機會描述
- ✅ `price_alerts` 顯示最近 10 條未讀告警

---

### 測試場景 3: Telegram 通知內容

#### 預期通知格式：
```
🎯 缺貨機會窗口

商品 日本 A5 和牛 的所有競品都缺貨！

當前價格: $398
建議提價: $426 (+7.0%)

這是搶佔市場份額的黃金機會 💰

[查看提案] [忽略]
```

**驗收標準**：
- ✅ 標題包含「🎯 缺貨機會窗口」
- ✅ 顯示商品名稱（使用 `name_zh`）
- ✅ 顯示當前價格和建議價格
- ✅ 顯示提價百分比（+7.0%）
- ✅ 包含「黃金機會」等激勵性文案

---

### 測試場景 4: 完整事件流閉環

```
Celery Beat (08:00/20:00)
    ↓
scrape_all_competitors()
    ↓
發現競品缺貨 → 生成 PriceAlert(alert_type='out_of_stock')
    ↓
scrape_tasks._check_price_alert() → 觸發 execute_alert_workflow.delay()
    ↓
EventBus: SCRAPE_COMPLETED → Scout Agent
    ↓
Scout._on_scrape_completed() → 分類告警
    ↓
alert_type == "out_of_stock" → EventBus: COMPETITOR_STOCKOUT
    ↓
Pricer Agent._on_competitor_stockout()
    ↓
檢查所有競品庫存 → 都缺貨 → 生成提價提案
    ↓
Telegram 推送「機會窗口」通知
    ↓
MRC Dashboard 顯示機會清單
```

**驗收標準**：
- ✅ 從爬取到通知，整個鏈路暢通
- ✅ 每個環節的事件都正確發射和接收
- ✅ 提案自動生成並記錄到數據庫
- ✅ Telegram 通知及時到達
- ✅ Dashboard 實時更新機會數量

---

## 📊 驗證檢查清單

### 數據庫驗證

#### 1. 檢查缺貨告警
```sql
SELECT
    cp.name AS product_name,
    pa.alert_type,
    pa.old_value,
    pa.new_value,
    pa.created_at
FROM price_alerts pa
JOIN competitor_products cp ON pa.competitor_product_id = cp.id
WHERE pa.alert_type = 'out_of_stock'
ORDER BY pa.created_at DESC
LIMIT 10;
```

#### 2. 檢查提價提案
```sql
SELECT
    p.sku,
    pp.current_price,
    pp.proposed_price,
    (pp.proposed_price - pp.current_price) / pp.current_price * 100 AS increase_percent,
    pp.reason,
    pp.status,
    pp.created_at
FROM price_proposals pp
JOIN products p ON pp.product_id = p.id
WHERE pp.model LIKE '%stockout%'
ORDER BY pp.created_at DESC;
```

#### 3. 檢查競品庫存狀態
```sql
-- 找出所有競品都缺貨的商品
WITH latest_snapshots AS (
    SELECT DISTINCT ON (cp.id)
        cp.id AS cp_id,
        cp.name,
        ps.stock_status,
        pcm.product_id
    FROM competitor_products cp
    JOIN price_snapshots ps ON cp.id = ps.competitor_product_id
    JOIN product_competitor_mappings pcm ON cp.id = pcm.competitor_product_id
    ORDER BY cp.id, ps.scraped_at DESC
)
SELECT
    p.sku,
    p.name_zh,
    COUNT(*) AS competitor_count,
    SUM(CASE WHEN ls.stock_status = 'out_of_stock' THEN 1 ELSE 0 END) AS out_of_stock_count
FROM products p
JOIN latest_snapshots ls ON p.id = ls.product_id
GROUP BY p.id, p.sku, p.name_zh
HAVING COUNT(*) = SUM(CASE WHEN ls.stock_status = 'out_of_stock' THEN 1 ELSE 0 END)
  AND COUNT(*) > 0;
```

---

## 🐛 常見問題排查

### 問題 1: 沒有生成提價提案

**可能原因**：
1. 競品沒有全部缺貨（至少有一個有貨）
2. 商品沒有啟用自動定價（`auto_pricing_enabled = False`）
3. 商品沒有設置價格或成本

**排查**：
```sql
-- 檢查商品配置
SELECT
    sku,
    name_zh,
    price,
    cost,
    min_price,
    max_price,
    auto_pricing_enabled
FROM products
WHERE id = '<product_id>';

-- 檢查競品庫存
SELECT
    cp.name,
    ps.stock_status,
    ps.scraped_at
FROM competitor_products cp
JOIN price_snapshots ps ON cp.id = ps.competitor_product_id
JOIN product_competitor_mappings pcm ON cp.id = pcm.competitor_product_id
WHERE pcm.product_id = '<product_id>'
  AND ps.scraped_at = (
      SELECT MAX(scraped_at)
      FROM price_snapshots
      WHERE competitor_product_id = cp.id
  );
```

### 問題 2: Telegram 沒有收到通知

**可能原因**：
1. Telegram 配置未設置（`TELEGRAM_BOT_TOKEN` 或 `TELEGRAM_CHAT_ID`）
2. Telegram 服務未啟用（`TELEGRAM_ENABLED = False`）
3. Bot 權限不足或 Chat ID 錯誤

**排查**：
```bash
# 檢查環境變量
echo $TELEGRAM_BOT_TOKEN
echo $TELEGRAM_CHAT_ID
echo $TELEGRAM_ENABLED

# 測試 Telegram 連接
curl -X GET "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getMe"
```

### 問題 3: MRC Dashboard 顯示機會數為 0

**可能原因**：
1. 沒有商品的所有競品都缺貨
2. 沒有競品映射（`product_competitor_mappings` 表為空）
3. 沒有價格快照數據

**排查**：
```sql
-- 檢查是否有競品映射
SELECT COUNT(*) FROM product_competitor_mappings;

-- 檢查是否有價格快照
SELECT COUNT(*) FROM price_snapshots;

-- 手動運行機會查詢邏輯
-- （複製 market_response.py 中的 SQL）
```

---

## ✅ P0-2 完成標準

### 功能驗收：
- [x] Pricer Agent 訂閱 `COMPETITOR_STOCKOUT` 事件
- [x] 檢測所有競品是否都缺貨
- [x] 生成提價提案（+7%）
- [x] Telegram 推送機會通知
- [x] MRC Dashboard 顯示機會清單
- [x] `opportunities_count` 顯示真實數字
- [x] `price_alerts` 顯示最近未讀告警

### 商業驗收：
- [ ] 模擬競品缺貨場景，成功生成提案
- [ ] Telegram 通知文案清晰易懂
- [ ] 提價百分比合理（5-10%）
- [ ] 機會識別準確（無誤報）

### 穩定性驗收：
- [ ] 多個商品同時缺貨，系統正常處理
- [ ] 部分競品缺貨時不生成提案
- [ ] 錯誤情況下不影響其他功能

---

## 🚀 預期商業影響

**月增利潤**: HKD 3,000-8,000

**原理**：
- 日本食材供應鏈波動大，競品缺貨頻繁
- 搶佔缺貨窗口期，提價 7% 同時銷量增長（因為是唯一選擇）
- 假設每月 5 次機會，每次平均利潤增量 HKD 600-1,600

---

## 📝 變更記錄

| 日期 | 修改內容 | 文件 |
|------|---------|------|
| 2026-02-11 | Pricer Agent 添加缺貨事件處理 | pricer.py |
| 2026-02-11 | 新增 `_on_competitor_stockout` 方法 | pricer.py |
| 2026-02-11 | 新增 `_check_all_competitors_stockout` 方法 | pricer.py |
| 2026-02-11 | MRC Dashboard 填充機會清單 | market_response.py |
| 2026-02-11 | 新增 `_get_stockout_opportunities` helper | market_response.py |
