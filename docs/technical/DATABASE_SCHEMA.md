# GoGoJap HKTVmall AI System - 數據庫結構文檔

> 本文檔描述系統使用的 PostgreSQL 數據庫結構，供甲方參考。

## 數據庫概覽

```
PostgreSQL 14+
├── competitors          # 競爭對手
├── competitor_products  # 競品商品監測
├── price_snapshots      # 價格歷史快照
├── price_alerts         # 價格警報
├── products             # 自家商品
├── product_history      # 商品修改歷史
├── product_competitor_mapping  # 商品對照關係
├── ai_contents          # AI 生成內容
├── scrape_logs          # 爬取日誌
├── sync_logs            # 同步日誌
└── settings             # 系統設定
```

## 表結構詳細

### 1. competitors - 競爭對手

| 欄位 | 類型 | 說明 |
|------|------|------|
| id | UUID | 主鍵 |
| name | VARCHAR(255) | 競爭對手名稱 |
| platform | VARCHAR(100) | 平台 (hktvmall, watsons 等) |
| base_url | VARCHAR(500) | 基礎 URL |
| notes | TEXT | 備註 |
| is_active | BOOLEAN | 是否啟用 |
| created_at | TIMESTAMP | 創建時間 |
| updated_at | TIMESTAMP | 更新時間 |

### 2. competitor_products - 競品商品

| 欄位 | 類型 | 說明 |
|------|------|------|
| id | UUID | 主鍵 |
| competitor_id | UUID | 關聯競爭對手 |
| name | VARCHAR(500) | 商品名稱 |
| url | VARCHAR(1000) | 商品頁面 URL (唯一) |
| sku | VARCHAR(100) | SKU |
| category | VARCHAR(255) | 分類 |
| image_url | VARCHAR(1000) | 圖片 URL |
| is_active | BOOLEAN | 是否監測 |
| last_scraped_at | TIMESTAMP | 最後抓取時間 |
| scrape_error | TEXT | 抓取錯誤信息 |
| created_at | TIMESTAMP | 創建時間 |
| updated_at | TIMESTAMP | 更新時間 |

**索引：**
- `idx_competitor_products_competitor_id`
- `idx_competitor_products_url`
- `idx_competitor_products_is_active`

### 3. price_snapshots - 價格快照

| 欄位 | 類型 | 說明 |
|------|------|------|
| id | UUID | 主鍵 |
| competitor_product_id | UUID | 關聯競品 |
| price | NUMERIC(10,2) | 現價 |
| original_price | NUMERIC(10,2) | 原價（劃線價） |
| discount_percent | NUMERIC(5,2) | 折扣百分比 |
| currency | VARCHAR(10) | 貨幣 (默認 HKD) |
| stock_status | VARCHAR(50) | 庫存狀態 |
| rating | NUMERIC(3,2) | 評分 |
| review_count | INTEGER | 評論數 |
| promotion_text | TEXT | 促銷文字 |
| raw_data | JSONB | 原始抓取數據 |
| scraped_at | TIMESTAMP | 抓取時間 |

### 4. price_alerts - 價格警報

| 欄位 | 類型 | 說明 |
|------|------|------|
| id | UUID | 主鍵 |
| competitor_product_id | UUID | 關聯競品 |
| alert_type | VARCHAR(50) | 警報類型 |
| old_value | VARCHAR(100) | 舊值 |
| new_value | VARCHAR(100) | 新值 |
| change_percent | NUMERIC(5,2) | 變動百分比 |
| is_read | BOOLEAN | 是否已讀 |
| is_notified | BOOLEAN | 是否已通知 |
| created_at | TIMESTAMP | 創建時間 |

**alert_type 值：**
- `price_drop` - 降價
- `price_increase` - 漲價
- `out_of_stock` - 缺貨
- `back_in_stock` - 恢復庫存

### 5. products - 自家商品

| 欄位 | 類型 | 說明 |
|------|------|------|
| id | UUID | 主鍵 |
| sku | VARCHAR(100) | SKU (唯一) |
| hktv_product_id | VARCHAR(100) | HKTVmall 商品 ID |
| name | VARCHAR(500) | 商品名稱 |
| description | TEXT | 商品描述 |
| category | VARCHAR(255) | 分類 |
| brand | VARCHAR(255) | 品牌 |
| price | NUMERIC(10,2) | 售價 |
| cost | NUMERIC(10,2) | 成本價 |
| stock_quantity | INTEGER | 庫存數量 |
| status | VARCHAR(50) | 狀態 (active/inactive/pending) |
| images | JSONB | 圖片列表 |
| attributes | JSONB | 商品屬性 |
| hktv_data | JSONB | HKTVmall 原始數據 |
| created_at | TIMESTAMP | 創建時間 |
| updated_at | TIMESTAMP | 更新時間 |

### 6. product_history - 商品修改歷史

| 欄位 | 類型 | 說明 |
|------|------|------|
| id | UUID | 主鍵 |
| product_id | UUID | 關聯商品 |
| field_changed | VARCHAR(100) | 修改欄位 |
| old_value | TEXT | 舊值 |
| new_value | TEXT | 新值 |
| changed_at | TIMESTAMP | 修改時間 |

### 7. product_competitor_mapping - 商品對照

| 欄位 | 類型 | 說明 |
|------|------|------|
| id | UUID | 主鍵 |
| product_id | UUID | 自家商品 ID |
| competitor_product_id | UUID | 競品 ID |
| match_confidence | NUMERIC(3,2) | 匹配信心度 (0-1) |
| is_verified | BOOLEAN | 是否人工確認 |
| notes | TEXT | 備註 |
| created_at | TIMESTAMP | 創建時間 |

### 8. ai_contents - AI 生成內容

| 欄位 | 類型 | 說明 |
|------|------|------|
| id | UUID | 主鍵 |
| product_id | UUID | 關聯商品 |
| content_type | VARCHAR(50) | 內容類型 |
| style | VARCHAR(50) | 風格 |
| language | VARCHAR(10) | 語言 (zh-HK) |
| content | TEXT | 生成的內容 |
| content_json | JSONB | 結構化內容 |
| version | INTEGER | 版本號 |
| status | VARCHAR(50) | 狀態 |
| generation_metadata | JSONB | 生成元數據 |
| input_data | JSONB | 輸入資料 |
| generated_at | TIMESTAMP | 生成時間 |
| approved_at | TIMESTAMP | 審批時間 |
| approved_by | VARCHAR(255) | 審批人 |
| rejected_reason | TEXT | 拒絕原因 |

**content_type 值：**
- `title` - 商品標題
- `description` - 商品描述
- `selling_points` - 賣點
- `full_copy` - 完整文案

### 9. scrape_logs - 爬取日誌

| 欄位 | 類型 | 說明 |
|------|------|------|
| id | UUID | 主鍵 |
| task_id | VARCHAR(255) | Celery 任務 ID |
| task_type | VARCHAR(50) | 任務類型 |
| competitor_id | UUID | 關聯競爭對手 |
| status | VARCHAR(50) | 狀態 |
| products_total | INTEGER | 總商品數 |
| products_scraped | INTEGER | 成功抓取數 |
| products_failed | INTEGER | 失敗數 |
| errors | JSONB | 錯誤列表 |
| started_at | TIMESTAMP | 開始時間 |
| completed_at | TIMESTAMP | 完成時間 |
| duration_seconds | INTEGER | 耗時（秒） |
| created_at | TIMESTAMP | 創建時間 |

### 10. sync_logs - 同步日誌

| 欄位 | 類型 | 說明 |
|------|------|------|
| id | UUID | 主鍵 |
| task_id | VARCHAR(255) | 任務 ID |
| sync_type | VARCHAR(50) | 同步類型 |
| source | VARCHAR(50) | 來源 |
| status | VARCHAR(50) | 狀態 |
| records_total | INTEGER | 總記錄數 |
| records_synced | INTEGER | 同步成功數 |
| records_failed | INTEGER | 失敗數 |
| errors | JSONB | 錯誤列表 |
| started_at | TIMESTAMP | 開始時間 |
| completed_at | TIMESTAMP | 完成時間 |
| created_at | TIMESTAMP | 創建時間 |

### 11. settings - 系統設定

| 欄位 | 類型 | 說明 |
|------|------|------|
| key | VARCHAR(255) | 主鍵 |
| value | JSONB | 設定值 |
| description | TEXT | 說明 |
| updated_at | TIMESTAMP | 更新時間 |

## 關係圖

```
competitors
    │
    └──< competitor_products
              │
              ├──< price_snapshots
              │
              ├──< price_alerts
              │
              └──< product_competitor_mapping >── products
                                                      │
                                                      ├──< product_history
                                                      │
                                                      └──< ai_contents
```

## 數據導出指令

```bash
# 導出完整數據庫
pg_dump -h host -U username -d database_name > backup.sql

# 只導出結構（無數據）
pg_dump -h host -U username -d database_name --schema-only > schema.sql

# 只導出數據
pg_dump -h host -U username -d database_name --data-only > data.sql
```

## 備註

- 所有 UUID 使用 PostgreSQL 原生 UUID 類型
- 時間戳均為 UTC 時區
- JSONB 欄位用於存儲靈活結構數據
- 外鍵刪除策略多為 CASCADE 或 SET NULL
