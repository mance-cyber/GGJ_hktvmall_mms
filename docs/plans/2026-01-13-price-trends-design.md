# 價格趨勢功能設計文檔

**日期**：2026-01-13
**狀態**：已批准，待實現
**預計工作量**：6-9 小時

---

## 1. 功能概述

開發價格趨勢儀表板，讓用戶可以：
- 追蹤自家產品 vs 競爭對手的價格走勢
- 選擇不同時間範圍（7天/30天/90天/自定義）
- 查看價格、折扣、庫存狀態、促銷標籤等完整數據
- 通過 KPI 卡片快速了解價差與波動情況

**初期使用 Mock 數據**，待真實爬蟲數據就緒後無縫切換。

---

## 2. 整體架構

```
┌─────────────────────────────────────────────────────────────┐
│                    價格趨勢儀表板                              │
├─────────────────────────────────────────────────────────────┤
│  [產品選擇下拉] ▼        [時間範圍: 7天|30天|90天|自定義]      │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐        │
│  │ 當前價差  │ │ 平均價差  │ │ 最低競爭價 │ │ 價格波動率 │       │
│  │  +12.5%  │ │  +8.3%   │ │  $128    │ │  ±5.2%   │        │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│     價格趨勢圖（Recharts LineChart）                          │
│     ── 自家產品（紫色實線）                                    │
│     -- 競爭對手A（青色虛線）                                   │
│     -- 競爭對手B（橙色虛線）                                   │
│     ● 缺貨標記點  ⬇ 促銷標記                                  │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  數據表格：日期 | 自家價 | 競A價 | 競B價 | 價差 | 庫存 | 促銷    │
└─────────────────────────────────────────────────────────────┘
```

**技術棧**：
- **前端**：Next.js + Recharts + HoloCard 組件
- **後端**：FastAPI + SQLAlchemy
- **資料庫**：PostgreSQL（現有 price_snapshots 表）

---

## 3. 後端 API 設計

### 3.1 路由文件

`backend/app/api/v1/price_trends.py`

### 3.2 端點定義

```
GET /api/v1/price-trends/products
  → 返回有價格歷史的自家產品列表（供下拉選單用）
  → Response: [{id, sku, name, competitor_count}]

GET /api/v1/price-trends/product/{product_id}
  → 返回單個產品及其競爭對手的價格趨勢
  → Query Params:
      - start_date: 開始日期 (YYYY-MM-DD)
      - end_date: 結束日期 (YYYY-MM-DD)
      - interval: hour|day|week（數據聚合粒度）
  → Response:
      {
        own_product: {id, name, sku, current_price},
        competitors: [{id, name, platform, current_price}],
        trends: {
          own: [{date, price, original_price, discount_pct, stock_status, promotion_text}],
          competitors: {
            "competitor_id_1": [{date, price, ...}],
            "competitor_id_2": [{date, price, ...}]
          }
        },
        summary: {
          price_gap_current: 12.5,
          price_gap_avg: 8.3,
          lowest_competitor_price: 128,
          volatility: 5.2
        }
      }
```

### 3.3 數據聚合邏輯

| 時間範圍 | 聚合粒度 | 說明 |
|----------|----------|------|
| 7 天內 | 按小時 | 取每小時最後一筆 |
| 30 天內 | 按天 | 取每天收盤價 |
| 90 天以上 | 按週 | 取每週平均值 |

---

## 4. Mock 數據設計

### 4.1 Seed 腳本

`backend/scripts/seed_price_trends.py`

### 4.2 數據規模

- **自家產品**：10 個（日本食材主題）
- **競爭對手**：每個產品 3-5 個
- **時間跨度**：90 天
- **預計筆數**：約 3,600 筆 price_snapshots

### 4.3 產品列表

```python
OWN_PRODUCTS = [
    {"sku": "WAGYU-A5-001", "name": "A5和牛肩胛肉", "base_price": 388},
    {"sku": "SALMON-NO-001", "name": "挪威三文魚柳", "base_price": 128},
    {"sku": "UNI-HOK-001", "name": "北海道馬糞海膽", "base_price": 268},
    {"sku": "SCALLOP-HOK-001", "name": "北海道帆立貝", "base_price": 198},
    {"sku": "TUNA-JP-001", "name": "日本藍鰭吞拿魚", "base_price": 458},
    {"sku": "MISO-JP-001", "name": "京都白味噌", "base_price": 68},
    {"sku": "SOY-JP-001", "name": "龜甲萬醬油", "base_price": 45},
    {"sku": "RICE-JP-001", "name": "新潟越光米", "base_price": 158},
    {"sku": "MATCHA-KYO-001", "name": "宇治抹茶粉", "base_price": 128},
    {"sku": "WAGASHI-001", "name": "京都和菓子禮盒", "base_price": 188},
]
```

### 4.4 價格波動模擬

```python
def generate_price_history(base_price, days=90):
    prices = []
    for day in range(days):
        # 基礎波動 ±5%
        daily_variation = random.uniform(-0.05, 0.05)

        # 週末促銷（-10% ~ -15%）
        if day % 7 in [5, 6]:
            daily_variation -= random.uniform(0.10, 0.15)

        # 隨機缺貨（5% 機率）
        stock_status = "out_of_stock" if random.random() < 0.05 else "in_stock"

        # 隨機促銷標籤（15% 機率）
        promotion = "限時特價" if random.random() < 0.15 else None

        prices.append({
            "date": start_date + timedelta(days=day),
            "price": round(base_price * (1 + daily_variation), 1),
            "stock_status": stock_status,
            "promotion_text": promotion
        })
    return prices
```

---

## 5. 前端組件結構

### 5.1 目錄結構

```
frontend/src/app/trends/
├── page.tsx                    # 主頁面
├── components/
│   ├── ProductSelector.tsx     # 產品下拉選單
│   ├── TimeRangePicker.tsx     # 時間範圍選擇器
│   ├── TrendKPICards.tsx       # 頂部 KPI 卡片
│   ├── PriceTrendChart.tsx     # 主圖表
│   └── PriceDataTable.tsx      # 數據表格
└── hooks/
    └── usePriceTrends.ts       # React Query hook
```

### 5.2 組件職責

| 組件 | 職責 | 使用的 UI 組件 |
|------|------|---------------|
| ProductSelector | 下拉選單，顯示產品名 + 競爭對手數量 | HoloCard + Radix Select |
| TimeRangePicker | 4 個按鈕 + 自定義日期 | HoloButton group |
| TrendKPICards | 4 個指標卡片，帶趨勢箭頭 | DataMetric × 4 |
| PriceTrendChart | 多線圖，支持 hover tooltip | Recharts LineChart |
| PriceDataTable | 可排序表格，顯示每日明細 | 現有表格樣式 |

### 5.3 數據流

```
ProductSelector (選擇產品)
        ↓
TimeRangePicker (選擇時間)
        ↓
usePriceTrends(productId, dateRange) ← React Query
        ↓
   ┌────┴────┐
   ↓         ↓
TrendKPICards  PriceTrendChart
               ↓
         PriceDataTable
```

---

## 6. 圖表視覺設計

### 6.1 顏色方案

```typescript
const COLORS = {
  own: '#8b5cf6',        // 紫色 - 自家產品（實線）
  competitor1: '#06b6d4', // 青色 - 競爭對手 1（虛線）
  competitor2: '#f59e0b', // 橙色 - 競爭對手 2（虛線）
  competitor3: '#22c55e', // 綠色 - 競爭對手 3（虛線）
  competitor4: '#ef4444', // 紅色 - 競爭對手 4（虛線）
  outOfStock: '#dc2626',  // 缺貨標記點
  promotion: '#facc15',   // 促銷標記
}
```

### 6.2 互動功能

- **Hover Tooltip**：顯示該日所有產品價格 + 價差百分比
- **Legend 點擊**：顯示/隱藏特定產品線
- **缺貨標記**：紅色圓點，hover 顯示「缺貨」
- **促銷標記**：黃色箭頭，hover 顯示促銷文字

### 6.3 響應式設計

- **Desktop**：完整圖表 + 側邊圖例
- **Mobile**：圖表全寬，圖例移至下方，表格可橫向滾動

---

## 7. 實現文件清單

| 優先級 | 文件路徑 | 操作 | 說明 |
|--------|----------|------|------|
| 1 | `backend/scripts/seed_price_trends.py` | 新增 | Mock 數據 seed 腳本 |
| 2 | `backend/app/api/v1/price_trends.py` | 新增 | 價格趨勢 API 路由 |
| 3 | `backend/app/schemas/price_trends.py` | 新增 | API 請求/響應 Schema |
| 4 | `backend/app/api/v1/__init__.py` | 修改 | 註冊新路由 |
| 5 | `frontend/src/lib/api/price-trends.ts` | 新增 | API 客戶端方法 |
| 6 | `frontend/src/app/trends/page.tsx` | 重寫 | 主頁面組件 |
| 7 | `frontend/src/app/trends/components/*.tsx` | 新增 | 5 個子組件 |
| 8 | `frontend/src/app/trends/hooks/usePriceTrends.ts` | 新增 | React Query hook |

---

## 8. 實現順序

```
Phase 1: 數據層
├── 1. 編寫 seed 腳本
├── 2. 執行 seed，驗證數據
└── 3. 建立 API 路由 + Schema

Phase 2: 前端基礎
├── 4. API 客戶端
├── 5. React Query hook
└── 6. 主頁面框架

Phase 3: 組件開發
├── 7. ProductSelector + TimeRangePicker
├── 8. TrendKPICards
├── 9. PriceTrendChart
└── 10. PriceDataTable

Phase 4: 整合測試
└── 11. 端對端測試 + 修復
```

---

## 9. 後續擴展（未來考慮）

以下功能不在本次實現範圍，但設計時已預留擴展空間：

- 匯出 CSV/PDF 報表
- 價格警報通知（價格跌破閾值時）
- 多產品同時對比
- 價格預測（AI 趨勢分析）
- 競爭對手自動發現

---

## 10. 驗收標準

1. 可選擇自家產品，自動顯示關聯競爭對手
2. 時間範圍切換正常（7天/30天/90天/自定義）
3. KPI 卡片顯示正確的統計數據
4. 圖表可互動（hover、legend 切換）
5. 數據表格可排序
6. 響應式設計在 Mobile/Desktop 正常顯示
7. Mock 數據結構與真實數據一致，可無縫切換
