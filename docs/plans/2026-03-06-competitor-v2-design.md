# GoGoJap 競品監測系統 v2 — 設計文件

**日期：** 2026-03-06
**狀態：** ✅ 已批准

---

## 背景

v1 系統問題：
- 先爬商戶全部商品再 filter → 4,494 件入面得 1,232 件有關
- `is_active` 被 monitor 同 orphan cleanup 互相覆蓋
- mapping 太泛（category_tag 匹配），和牛薯片都算和牛競品
- 數據庫混亂，難以維護

## 核心理念

**「以自家商品出發，只追蹤真正嘅生鮮競品」**

兩條線並行：
- **Line A：自家商品 → 搵競品（精準配對）**
- **Line B：核心商戶 → 爬全部生鮮（市場情報）**

## 數據流程

```
Line A: 自家 23 件商品
  → 每件生成搜索關鍵詞
  → Algolia 搜 HKTVmall
  → 規則快速過濾明顯加工品
  → OpenClaw Gateway (Sonnet) AI 判斷剩餘
  → 建立精準 mapping

Line B: 核心商戶（Tier 1/2）
  → Algolia 按 store_code 爬全部商品
  → 同上 AI 過濾，只留生鮮/冷凍
  → 入庫但不一定有 mapping（市場情報用）

前端 toggle：
  🎯 自家競品 — 只顯示有 mapping 嘅（Line A）
  🌊 全部生鮮 — 顯示所有生鮮商品（Line A + B）
```

## 數據庫設計

### 保留 + 修改

**`competitors`** — 加 `tier` 欄位
```sql
ALTER TABLE competitors ADD COLUMN tier INTEGER DEFAULT 2; -- 1=直接對手, 2=品類重疊, 3=參考
-- 清空後重新指定商戶
```

**`competitor_products`** — 簡化 + 加新欄位
```sql
-- 清空所有數據
TRUNCATE competitor_products CASCADE;

-- 刪除舊欄位
ALTER TABLE competitor_products
  DROP COLUMN IF EXISTS category_tag,
  DROP COLUMN IF EXISTS sub_tag,
  DROP COLUMN IF EXISTS needs_matching,
  DROP COLUMN IF EXISTS tag_source,
  DROP COLUMN IF EXISTS scrape_config_override,
  DROP COLUMN IF EXISTS scrape_error;

-- 加新欄位
ALTER TABLE competitor_products
  ADD COLUMN product_type VARCHAR(20) DEFAULT 'unknown', -- fresh/frozen/processed/unknown
  ADD COLUMN category VARCHAR(50),                        -- 牛/豬/魚/蝦/蟹/貝/蠔...
  ADD COLUMN unit_weight_g INTEGER;                       -- 用嚟算單位價
```

**`price_snapshots`** — 加 `unit_price_per_100g`
```sql
TRUNCATE price_snapshots CASCADE;
ALTER TABLE price_snapshots
  ADD COLUMN unit_price_per_100g NUMERIC(10,2);
```

**`product_competitor_mapping`** — 簡化
```sql
TRUNCATE product_competitor_mapping;
ALTER TABLE product_competitor_mapping
  ADD COLUMN match_type VARCHAR(20) DEFAULT 'ai_matched'; -- ai_matched / manual
-- 保留 confidence 欄位
```

**`price_alerts`** — 清空
```sql
TRUNCATE price_alerts;
```

### 刪除（如有）
- `scrape_configs` 相關邏輯不再需要（Algolia 取代）
- `import_jobs` / `import_job_items` — 不再需要批量導入

## AI 配對引擎

### 過濾 Prompt

```
你是 HKTVmall 生鮮食材分類專家。

判斷以下商品是否為「生鮮或冷凍食材」：
✅ 包括：生肉、冷凍肉、海鮮、冷凍海鮮、刺身
❌ 排除：薯片、零食、便當、湯底、醬汁、調味料、即食品、飲品、日用品

對每件商品返回 JSON：
{
  "relevant": true/false,
  "category": "牛/豬/魚/蝦/蟹/貝/蠔/其他",
  "product_type": "fresh/frozen",
  "unit_weight_g": 200,        // 從商品名提取，無則 null
  "reason": "排除原因"          // 只有 relevant=false 時填
}
```

### 調用方式
- OpenClaw Gateway → Claude Sonnet
- 每次 batch 50 件商品
- 首次建庫：~46 次 call，< 5 分鐘
- 日常更新：只判斷新商品，call 數極少

## 商戶管理

### Tier 分級
| Tier | 定義 | 監測頻率 | 例子 |
|------|------|---------|------|
| 1 | 直接對手（同定位日本食材店） | 每日兩次 | Foodianna |
| 2 | 品類重疊（有賣日本食材） | 每日兩次 | Ocean Three |
| 3 | 參考（大型超市偶爾有） | 每週一次 | — |

### 新商戶發現
- 每週一 04:00
- 用品類關鍵詞搜 Algolia
- 發現新商戶 → Telegram 通知，等確認後加入追蹤

## 監測排程

| 時間 | 任務 |
|------|------|
| 06:00 | 第一輪：Algolia 爬價格 + 新品 AI 判斷 |
| 08:00 | Morning Brief 加入競品摘要 |
| 15:00 | 第二輪：同上 |
| 週一 04:00 | 新商戶發現 |

### 即時通知
- 🔴 直接對手減價 >10%
- 🟢 你係某品類最平
- 🆕 核心商戶新上架生鮮
- ⚠️ 競品下架（可能斷貨）

## 前端 Dashboard

### View A — 自家商品視角（預設）
- 每件自家商品展開顯示所有競品價格
- 紅色 = 對手平過你，綠色 = 你較平
- 點入去見價格趨勢圖
- Toggle：自家競品 / 全部生鮮

### View B — 競爭對手視角
- 每間商戶顯示：重疊商品 + 獨有商品
- 獨有商品 = 佢有你冇 → 入貨機會
- Tier badge 顯示

## 實施步驟

1. 清空舊數據 + migrate schema
2. 重寫 AI 配對引擎
3. 重寫 Algolia 爬取邏輯
4. 重寫監測排程
5. 重寫前端 Dashboard
6. 首次建庫 + 測試
7. 上線

## 刪除嘅舊代碼

- `services/cataloger.py` — 重寫
- `services/product_competitor_finder.py` — 重寫
- `services/monitor.py` — 重寫
- `services/competitor_matcher.py` — 刪除
- `services/matcher.py` — 刪除
- `scripts/expand_competitor_stores.py` — 刪除
- `scripts/expand_remaining.py` — 刪除
- `scripts/soft_delete_orphan_competitors.py` — 刪除
- `scripts/run_competitor_finder.py` — 刪除
- `scripts/batch_match_competitors.py` — 簡化或刪除
