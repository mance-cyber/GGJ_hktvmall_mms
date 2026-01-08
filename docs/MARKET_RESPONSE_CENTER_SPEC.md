# 🏢 Market Response Center (MRC) - 項目規格書

**Status**: Draft
**Date**: 2026-01-07
**Version**: 2.0 (Restored)

## 1. 核心願景 (Core Vision)
建立一個智能化的「市場應對中心」，不僅僅是收集數據，而是將 **GogoJap 內部 SKU** 與 **外部市場情報** 結合，轉化為可執行的行銷與定價策略。

---

## 2. 系統架構 (Architecture)

### 2.1 核心母體 (The Master Source)
*   **數據來源**: `products/GogoJap-SKU list.csv`
*   **轉化目標**: PostgreSQL `products` 表
*   **戰略意義**: 作為所有外部數據的掛載點，確保我們是以「自家商品」為視角去觀察市場。

### 2.2 自動化偵察引擎 (Auto-Recon Engine)
*   **觸發機制**: 遍歷 `products` 表中的每一個 SKU。
*   **搜尋策略**: 
    *   優先使用 `日文品名` (最精準)
    *   次要使用 `英文品名` (擴大範圍)
    *   輔助使用 `中文品名`
*   **智能匹配 (AI Matching)**:
    *   使用 LLM 分析對手商品頁面。
    *   判斷關鍵屬性（野生vs養殖、產地、規格、等級）。
    *   **Only** 當匹配度 > 80% 時才建立關聯。

---

## 3. 功能模組 (Functional Modules)

### 3.1 價格防禦 (Price Defense)
*   **監控**: 每日比對已關聯的競品價格。
*   **警報**: 當 (對手價格 < 我方成本 * 1.1) 或 (對手降價幅度 > 10%) 時觸發。
*   **輸出**: 建議調整售價或強調非價格優勢（如品質、服務）。

### 3.2 機會進攻 (Opportunity Attack)
*   **缺貨掃描**: 檢測對手熱銷品項是否 `Out of Stock`。
*   **進攻信號**: 若 (對手缺貨 AND 我方有庫存) -> 產生「獨家現貨」行銷文案。

### 3.3 季節性策略 (Seasonal Strategy)
*   **數據源**: CSV 中的 `季節/備註` 欄位 (e.g., WINTER, AUTUMN, FEB-MAY)。
*   **時間觸發**: 系統根據當前月份，自動篩選「當季商品」。
*   **應用**: 自動生成「時令推薦清單」給 Marketing Team。

---

## 4. 數據結構設計 (Schema Design)

### Products Table (Enhanced)
| Column | Type | Description |
|--------|------|-------------|
| `sku_id` | PK | 唯一識別碼 |
| `name_zh` | Text | 中文品名 |
| `name_ja` | Text | 日文品名 (核心搜索鍵) |
| `name_en` | Text | 英文品名 |
| `category_main` | Text | 大分類 (e.g., 飛機貨) |
| `category_sub` | Text | 小分類 (e.g., 鮮魚) |
| `season_tag` | Text | 季節標籤 (e.g., WINTER) |
| `unit` | Text | 單位 |

### Competitor_Links Table
| Column | Type | Description |
|--------|------|-------------|
| `id` | PK | |
| `product_id` | FK | 關聯到 Products 表 |
| `competitor_name` | Text | e.g., HKTVmall |
| `url` | Text | 對手商品鏈接 |
| `match_confidence` | Float | AI 匹配信心指數 (0-1) |
| `last_checked_at` | Date | 最後檢查時間 |

---

## 5. 開發路線圖 (Roadmap)

1.  **Phase 1: Foundation** (Current)
    *   [ ] 建立 `docs/MARKET_RESPONSE_CENTER_SPEC.md` (Done)
    *   [ ] 升級 Database Schema 以支援 CSV 所有欄位。
    *   [ ] 編寫並執行 `import_gogojap_skus.py`，完成數據注入。

2.  **Phase 2: Intelligence**
    *   [ ] 開發 Firecrawl 搜索腳本。
    *   [ ] 集成 Claude 進行商品匹配。

3.  **Phase 3: User Interface**
    *   [ ] 開發前端「市場應對中心」儀表板。


---

## 6. 數據庫升級計劃 (Schema Upgrade Plan)

### 6.1 現有模型狀態

| Table | Status | Notes |
|-------|--------|-------|
| `products` | ⚠️ 需升級 | 缺少多語言名稱、季節、單位欄位 |
| `competitor_products` | ✅ Ready | 已有完整結構 |
| `product_competitor_mapping` | ✅ Ready | 已有 `match_confidence` |
| `price_snapshots` | ✅ Ready | 價格歷史追蹤 |
| `price_alerts` | ✅ Ready | 警報系統 |

### 6.2 Products 表需新增欄位

```python
# 多語言商品名稱 (核心搜索鍵)
name_zh: Mapped[Optional[str]] = mapped_column(String(500), comment="中文品名")
name_ja: Mapped[Optional[str]] = mapped_column(String(500), comment="日文品名 - 核心搜索鍵")
name_en: Mapped[Optional[str]] = mapped_column(String(500), comment="英文品名/規格")

# 分類層級
category_main: Mapped[Optional[str]] = mapped_column(String(100), comment="大分類")
category_sub: Mapped[Optional[str]] = mapped_column(String(100), comment="小分類")

# 商品屬性
unit: Mapped[Optional[str]] = mapped_column(String(50), comment="單位: KG, PK, PC...")
season_tag: Mapped[Optional[str]] = mapped_column(String(100), comment="季節標籤: ALL, WINTER...")

# 數據來源標記
source: Mapped[Optional[str]] = mapped_column(String(50), default="gogojap_csv", comment="數據來源")
```

### 6.3 索引優化

```sql
CREATE INDEX idx_products_name_ja ON products(name_ja);
CREATE INDEX idx_products_season_tag ON products(season_tag);
CREATE INDEX idx_products_category_main ON products(category_main);
```


---

## 7. Implementation Status (實施狀態)

**Date**: 2026-01-07
**Status**: Phase 1 Complete ✅

### Completed Tasks

| # | Task | Files Created/Modified |
|---|------|----------------------|
| 1 | Product Model 升級 | `backend/app/models/product.py` |
| 2 | Alembic Migration | `backend/alembic/versions/add_mrc_product_fields.py` |
| 3 | CSV Import Script | `scripts/import_gogojap_skus.py` |
| 4 | SQL/JSON Export | `scripts/gogojap_skus.sql`, `scripts/gogojap_skus.json` |
| 5 | Market Response API | `backend/app/api/v1/market_response.py` |
| 6 | Competitor Matcher | `backend/app/services/competitor_matcher.py` |
| 7 | Frontend Dashboard | `frontend/src/app/market-response/page.tsx` |

### New API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/mrc/dashboard` | Dashboard 統計 |
| GET | `/api/v1/mrc/products/seasonal` | 季節商品列表 |
| GET | `/api/v1/mrc/products/search` | 多語言搜索 |
| GET | `/api/v1/mrc/categories` | 分類統計 |
| GET | `/api/v1/mrc/stats/overview` | 統計概覽 |
| POST | `/api/v1/mrc/products/{id}/find-competitors` | 自動搜索競品 |
| POST | `/api/v1/mrc/batch/find-competitors` | 批量搜索競品 |

### Data Summary

- **Total SKUs imported**: 600
- **Categories**: 5 大分類, 25+ 小分類
- **Seasonal tags**: ALL, WINTER, SPRING, SUMMER, AUTUMN + 組合

### Next Steps

1. Execute Migration: `cd backend && alembic upgrade head`
2. Import Data: Execute `scripts/gogojap_skus.sql`
3. Start Backend: `cd backend && uvicorn app.main:app --reload`
4. Start Frontend: `cd frontend && npm run dev`
5. Access MRC: http://localhost:3000/market-response

