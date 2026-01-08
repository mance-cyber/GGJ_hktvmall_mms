# 產品表結構說明

本系統共有 **3 種產品表**，分屬不同功能模組。

---

## 總覽

| 大類 | 表名 | 用途 | 數據來源 |
|------|------|------|----------|
| **自家商品** | `OwnProduct` | 管理自己店鋪的商品 | 手動錄入 / 批量導入 |
| **競爭商品** | `CompetitorProduct` | 監測競爭對手的商品價格 | 抓取對手商品頁面 |
| **類別商品** | `Product` | 監測 HKTVmall 某類別的所有商品 | 抓取 HKTVmall 類別頁 |

---

## 大類一：自家商品 (OwnProduct)

> **位置**：`/products` 頁面  
> **API**：`GET /products`、`POST /products`

### 欄位結構

| 欄位 | 類型 | 說明 | 必填 |
|------|------|------|------|
| `id` | string | 主鍵 UUID | 自動 |
| `sku` | string | 商品編號 | ✓ |
| `hktv_product_id` | string \| null | HKTVmall 商品 ID | |
| `name` | string | 商品名稱 | ✓ |
| `description` | string \| null | 商品描述 | |
| `category` | string \| null | 分類 | |
| `brand` | string \| null | 品牌 | |
| `price` | number \| null | 售價 | |
| `cost` | number \| null | 成本價 | |
| `stock_quantity` | number | 庫存數量 | 預設 0 |
| `status` | string | 狀態：`active` / `draft` / `archived` | 預設 `draft` |
| `images` | string[] \| null | 圖片 URL 列表 | |
| `attributes` | object \| null | 自定義屬性 | |
| `created_at` | string | 創建時間 | 自動 |
| `updated_at` | string | 更新時間 | 自動 |

### 小類（按 category 分組）

```
自家商品
├── 保健品 (health)
├── 美容護膚 (beauty)
├── 食品飲料 (food)
└── 其他 (未分類)
```

---

## 大類二：競爭商品 (CompetitorProduct)

> **位置**：`/competitors/[id]` 頁面  
> **API**：`GET /competitors/{id}/products`

### 欄位結構

| 欄位 | 類型 | 說明 | 必填 |
|------|------|------|------|
| `id` | string | 主鍵 UUID | 自動 |
| `competitor_id` | string | 所屬競爭對手 ID | ✓ |
| `name` | string | 商品名稱 | ✓ |
| `url` | string | 商品頁面 URL | ✓ |
| `sku` | string \| null | 商品編號 | |
| `category` | string \| null | 分類 | |
| `image_url` | string \| null | 商品圖片 | |
| `is_active` | boolean | 是否啟用監測 | 預設 true |
| `current_price` | number \| null | 當前價格 | |
| `previous_price` | number \| null | 上次價格 | |
| `price_change` | number \| null | 價格變動 (%) | |
| `stock_status` | string \| null | 庫存狀態 | |
| `last_scraped_at` | string \| null | 最後抓取時間 | |
| `created_at` | string | 創建時間 | 自動 |

### 小類（按 competitor_id 分組）

```
競爭商品
├── 競爭對手 A
│   ├── 商品 1
│   ├── 商品 2
│   └── ...
├── 競爭對手 B
│   ├── 商品 1
│   └── ...
└── 競爭對手 C
    └── ...
```

### 關聯表：價格歷史 (PriceSnapshot)

| 欄位 | 類型 | 說明 |
|------|------|------|
| `id` | string | 主鍵 |
| `price` | number \| null | 價格 |
| `original_price` | number \| null | 原價 |
| `discount_percent` | number \| null | 折扣 % |
| `stock_status` | string \| null | 庫存狀態 |
| `rating` | number \| null | 評分 |
| `review_count` | number \| null | 評論數 |
| `scraped_at` | string | 抓取時間 |

---

## 大類三：類別商品 (Product)

> **位置**：`/categories/[id]` 頁面  
> **API**：`GET /categories/{id}/products`

### 欄位結構

| 欄位 | 類型 | 說明 | 必填 |
|------|------|------|------|
| `id` | string | 主鍵 UUID | 自動 |
| `category_id` | string | 所屬類別 ID | ✓ |
| `name` | string | 商品名稱 | ✓ |
| `url` | string | 商品頁面 URL | ✓ |
| `sku` | string \| null | 商品編號 | |
| `brand` | string \| null | 品牌 | |
| `price` | number \| null | 當前價格 | |
| `original_price` | number \| null | 原價 | |
| `discount_percent` | number \| null | 折扣 % | |
| `unit_price` | number \| null | 單位價格 | |
| `unit_type` | string \| null | 單位類型 | |
| `stock_status` | string \| null | 庫存狀態 | |
| `is_available` | boolean | 是否有貨 | |
| `rating` | number \| null | 評分 | |
| `review_count` | number \| null | 評論數 | |
| `image_url` | string \| null | 商品圖片 | |
| `first_seen_at` | string | 首次發現時間 | 自動 |
| `last_updated_at` | string | 最後更新時間 | 自動 |

### 小類（按 category_id 分組）

```
類別商品
├── 類別：日本零食
│   ├── 商品 1
│   ├── 商品 2
│   └── ...
├── 類別：韓國美妝
│   └── ...
└── 類別：保健食品
    └── ...
```

### 關聯表：價格歷史 (PriceHistory)

| 欄位 | 類型 | 說明 |
|------|------|------|
| `product_id` | string | 商品 ID |
| `product_name` | string | 商品名稱 |
| `days` | number | 歷史天數 |
| `data_points` | number | 數據點數量 |
| `chart_data` | array | 圖表數據（日期、價格、折扣等） |
| `statistics` | object | 統計（最低/最高/平均價、趨勢） |

---

## 三表對比

| 維度 | OwnProduct | CompetitorProduct | Product |
|------|------------|-------------------|---------|
| **數據來源** | 手動錄入 | 抓取競爭對手 | 抓取 HKTVmall |
| **主要用途** | 庫存管理、定價 | 競品價格監測 | 市場趨勢分析 |
| **分組依據** | category (分類) | competitor_id (對手) | category_id (類別) |
| **價格歷史** | 無 | PriceSnapshot[] | PriceHistory |
| **抓取功能** | 無 | 有 (單個/批量) | 有 (預覽/直接) |
| **庫存管理** | 有 (stock_quantity) | 僅狀態 | 僅狀態 |
| **成本價** | 有 (cost) | 無 | 無 |

---

## 數據關係圖

```
┌─────────────────────────────────────────────────────────────────┐
│                         HKTVmall AI 系統                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────┐                                              │
│  │   Category    │ 1 ─────┬───── * ┌─────────────┐              │
│  │   (類別)      │        │        │   Product   │              │
│  └───────────────┘        │        │ (類別商品)   │              │
│                           │        └─────────────┘              │
│                           │              │                      │
│                           │              │ 1                    │
│                           │              │                      │
│                           │              ▼ *                    │
│                           │        ┌─────────────┐              │
│                           │        │PriceHistory │              │
│                           │        │ (價格歷史)   │              │
│                           │        └─────────────┘              │
│                           │                                     │
│  ┌───────────────┐        │                                     │
│  │  Competitor   │ 1 ─────┼───── * ┌─────────────────┐          │
│  │  (競爭對手)    │        │        │CompetitorProduct│          │
│  └───────────────┘        │        │   (競爭商品)     │          │
│                           │        └─────────────────┘          │
│                           │              │                      │
│                           │              │ 1                    │
│                           │              │                      │
│                           │              ▼ *                    │
│                           │        ┌─────────────┐              │
│                           │        │PriceSnapshot│              │
│                           │        │ (價格快照)   │              │
│                           │        └─────────────┘              │
│                           │                                     │
│  ┌───────────────┐        │                                     │
│  │  OwnProduct   │ ───────┘  (獨立，無關聯)                      │
│  │  (自家商品)    │                                              │
│  └───────────────┘                                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 建議整合方向

目前三種產品表**彼此獨立**，如需建立關聯，可考慮：

1. **自家商品 ↔ 競爭商品**
   - 添加 `matched_competitor_products: string[]` 欄位
   - 用於比價分析

2. **自家商品 ↔ 類別商品**
   - 添加 `matched_category_product_id: string` 欄位
   - 用於市場定位分析

3. **統一產品視圖**
   - 創建虛擬視圖，將三表數據合併展示
   - 按「自家 / 競爭 / 市場」分組

---

## 文件位置

| 相關文件 | 路徑 |
|----------|------|
| 類型定義 | `src/lib/api.ts` |
| 自家商品頁 | `src/app/products/page.tsx` |
| 競爭商品頁 | `src/app/competitors/[id]/page.tsx` |
| 類別商品頁 | `src/app/categories/[id]/page.tsx` |
