# GoGoJap 競品監測升級方案
## 用 HKTVmall Algolia API 取代 Firecrawl

**目標：** 零成本、全自動、每日更新競品價格  
**文件日期：** 2026-02-24

---

## 📌 背景

目前 GoGoJap 使用 **Firecrawl** 做競品爬蟲，存在以下問題：

| 問題 | 影響 |
|------|------|
| Firecrawl 按頁計費 | 月費持續支出，難以 scale |
| 需要瀏覽器環境 | 部署複雜，穩定性差 |
| 速度慢（秒級/頁） | 爬取 500 件需 10+ 分鐘 |
| 依賴第三方服務 | 服務故障即中斷監測 |

---

## ✅ 新方案：HKTVmall Algolia API

HKTVmall 內部使用 **Algolia** 搜尋引擎，Public API 可直接訪問，**無需任何認證或 Cookie**。

### API 規格

```
Algolia App ID:  8RN1Y79F02
Algolia API Key: 8e51a51f6078bd496eaa186bd08a3768
Index:           hktvProduct
Endpoint:        https://8RN1Y79F02-dsn.algolia.net/1/indexes/*/queries
```

### 效能對比

| 指標 | Firecrawl | Algolia API |
|------|-----------|-------------|
| 速度 | ~1-2s/頁 | **~200 products/sec** |
| 691 件商品 | ~10 min | **3.3 秒** |
| 費用 | 按頁計費 | **$0（完全免費）** |
| 瀏覽器依賴 | ✅ 需要 | ❌ 不需要 |
| 穩定性 | 受 bot detection 影響 | ✅ 穩定 Public API |
| 數據豐富度 | HTML 需解析 | **結構化 JSON 直出** |

### 可獲取數據欄位

```json
{
  "productName": "宮崎A5和牛肉眼扒 200g",
  "priceList": {
    "BUY": 328,       // 原價
    "DISCOUNT": 268,  // 現售價
    "PLUS": 248       // Plus 會員價
  },
  "brand": "GoGoJap",
  "storeName": "GoGoFoods",
  "ratingValue": 4.8,
  "numberOfReviews": 23,
  "soldQuantity": "100+",
  "originCountry": "Japan",
  "inventoryStatus": "IN_STOCK"
}
```

---

## 🏗️ 整合架構

```
┌─────────────────────────────────────┐
│         GoGoJap Backend             │
│                                     │
│  ┌─────────────┐  ┌──────────────┐  │
│  │  Celery     │  │  FastAPI     │  │
│  │  Beat Cron  │──▶  /monitor   │  │
│  └──────┬──────┘  └──────┬───────┘  │
│         │                │          │
│  ┌──────▼──────────────┐ │          │
│  │  hktvmall_algolia   │ │          │
│  │  競品監測模組        │ │          │
│  └──────┬──────────────┘ │          │
│         │                │          │
│  ┌──────▼──────────────┐ │          │
│  │  PostgreSQL (Neon)   │◀┘          │
│  │  competitor_prices   │           │
│  └─────────────────────┘           │
└─────────────────────────────────────┘
         │
         ▼ 每日 02:00 自動跑
```

---

## 📂 實施步驟

### Step 1：複製 Algolia 腳本到 GoGoJap

```bash
cp C:/Users/ktphi/clawd/scripts/hktvmall_algolia.py \
   E:/Mance/Mercury/Project/7.App\ dev/4.GoGoJap\ -\ HKTVmall\ AI\ system/backend/services/
```

### Step 2：建立資料庫 Schema

```sql
-- 競品價格記錄表
CREATE TABLE competitor_prices (
    id              SERIAL PRIMARY KEY,
    scraped_at      TIMESTAMPTZ DEFAULT NOW(),
    keyword         VARCHAR(100) NOT NULL,
    product_name    TEXT NOT NULL,
    store_name      VARCHAR(100),
    brand           VARCHAR(100),
    current_price   DECIMAL(10,2),
    original_price  DECIMAL(10,2),
    plus_price      DECIMAL(10,2),
    discount_pct    DECIMAL(5,2) GENERATED ALWAYS AS (
                        CASE WHEN original_price > 0
                        THEN ROUND((1 - current_price/original_price)*100, 2)
                        ELSE NULL END
                    ) STORED,
    sold_quantity   VARCHAR(50),
    rating          DECIMAL(3,1),
    review_count    INT,
    origin_country  VARCHAR(50),
    inventory_status VARCHAR(50),
    product_url     TEXT
);

-- 索引優化
CREATE INDEX idx_competitor_prices_keyword ON competitor_prices(keyword);
CREATE INDEX idx_competitor_prices_scraped_at ON competitor_prices(scraped_at);
CREATE INDEX idx_competitor_prices_store ON competitor_prices(store_name);
```

### Step 3：建立監測服務模組

```python
# backend/services/competitor_monitor.py

from hktvmall_algolia import search_all
from database import get_db
from datetime import datetime
import logging

# GoGoJap 主力產品監測關鍵字
MONITOR_KEYWORDS = [
    "宮崎和牛",
    "宮崎A5",
    "和牛肉眼",
    "和牛西冷",
    "黑毛和牛",
    "A5和牛",
    "日本和牛",
    "北海道豬",
]

async def run_daily_monitor():
    """每日競品價格監測主函式"""
    db = await get_db()
    total_saved = 0
    
    for keyword in MONITOR_KEYWORDS:
        logging.info(f"🔍 監測關鍵字: {keyword}")
        
        try:
            products = search_all(keyword)
            
            for p in products:
                await db.execute("""
                    INSERT INTO competitor_prices 
                    (keyword, product_name, store_name, brand,
                     current_price, original_price, plus_price,
                     sold_quantity, rating, review_count,
                     origin_country, inventory_status, product_url)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
                """, keyword, p['name'], p['store'], p['brand'],
                    p['price_discount'], p['price_buy'], p['price_plus'],
                    p['sold'], p['rating'], p['reviews'],
                    p['origin'], p['status'], p['url'])
                total_saved += 1
                
        except Exception as e:
            logging.error(f"❌ 關鍵字 {keyword} 失敗: {e}")
    
    logging.info(f"✅ 今日監測完成，共儲存 {total_saved} 筆競品數據")
    return total_saved
```

### Step 4：設定 Celery Beat Cron

```python
# backend/celery_config.py

from celery.schedules import crontab

CELERYBEAT_SCHEDULE = {
    # 競品價格監測 — 每日凌晨 2:00
    'competitor-price-monitor': {
        'task': 'tasks.monitor.run_daily_monitor',
        'schedule': crontab(hour=2, minute=0),
        'options': {'queue': 'monitor'}
    },
    
    # 現有任務保留...
}
```

### Step 5：建立 FastAPI 端點（供前端 Dashboard 查詢）

```python
# backend/routers/monitor.py

@router.get("/api/monitor/latest")
async def get_latest_prices(keyword: str = "宮崎和牛"):
    """取得最新競品價格"""
    return await db.fetch("""
        SELECT DISTINCT ON (product_name, store_name)
            product_name, store_name, brand,
            current_price, original_price, discount_pct,
            sold_quantity, rating, scraped_at
        FROM competitor_prices
        WHERE keyword = $1
        ORDER BY product_name, store_name, scraped_at DESC
    """, keyword)

@router.get("/api/monitor/price-trend")
async def get_price_trend(product_name: str, days: int = 30):
    """取得產品價格走勢（30天）"""
    return await db.fetch("""
        SELECT DATE(scraped_at) as date,
               MIN(current_price) as min_price,
               AVG(current_price) as avg_price
        FROM competitor_prices
        WHERE product_name ILIKE $1
          AND scraped_at >= NOW() - INTERVAL '$2 days'
        GROUP BY DATE(scraped_at)
        ORDER BY date ASC
    """, f"%{product_name}%", days)

@router.get("/api/monitor/alert")
async def get_price_alerts():
    """取得需要注意的競品（比 GoGoJap 便宜 20% 以上）"""
    gogojap_prices = {
        "肉眼扒": 298,
        "西冷扒": 298,
        "火鍋片": 198,
    }
    # 比對邏輯...
```

---

## 📊 預期成效

| 指標 | 目前（無監測）| 整合後 |
|------|-------------|--------|
| 競品數據更新頻率 | 手動/不定期 | **每日自動** |
| 監測關鍵字數 | 0 | **8 個主力關鍵字** |
| 監測商品數 | 0 | **~400-500 件/日** |
| 月費成本 | Firecrawl 費用 | **$0** |
| 反應時間（發現競品降價）| 數天 | **24 小時內** |

---

## 🗓️ 實施時間表

| 日期 | 任務 | 工時 |
|------|------|------|
| Day 1 | 複製腳本 + 建立 DB Schema | 1h |
| Day 1 | 寫 competitor_monitor.py | 2h |
| Day 2 | 整合 Celery Beat | 1h |
| Day 2 | 建立 FastAPI 端點 | 2h |
| Day 3 | 前端 Dashboard 顯示 | 3h |
| Day 3 | 測試 + 部署 | 2h |

**總工時估算：約 11 小時**

---

## ⚠️ 注意事項

1. **Algolia Public Key 可能更新** — 建議儲存到 env variable，方便替換
2. **Rate Limit** — 目前測試無限制，但建議每次查詢間隔 0.5s 以防萬一
3. **數據去重** — 同一產品可能出現在多個關鍵字搜尋，需要用 `product_url` 去重
4. **歷史數據保留** — 建議只保留 90 天，避免 Neon 免費額度超標

---

## 🔗 相關文件

- 腳本位置：`C:\Users\ktphi\clawd\scripts\hktvmall_algolia.py`
- 競品分析報告：`deliverables/hktvmall-wagyu-report.md`
- GoGoJap Backend：`E:\Mance\Mercury\Project\7.App dev\4.GoGoJap - HKTVmall AI system`

---

*計劃由 Eve 整理*  
*2026-02-24*
