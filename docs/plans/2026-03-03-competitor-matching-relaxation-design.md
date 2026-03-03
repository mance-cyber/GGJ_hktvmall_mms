# 競品匹配放寬設計

> 日期：2026-03-03
> 狀態：已批准，待實現

## 問題

1. **Matching 過嚴**：搜索 keyword 帶產地（「宮崎 A5 和牛西冷」），Claude prompt 要求「同級商品」（相似等級），導致「鹿兒島 A5 和牛」不匹配「宮崎 A5 和牛」。多數對手只 match 到 0-1 件商品。
2. **Cataloger 無限建庫**：`_catalog_hktvmall()` 無 per-store 上限，Foodianna 一個店被灌入 1594 件商品。

## 方案：放寬 Prompt + 寬泛搜索 + Store 上限

改動最少、風險最低的方案。3 個改動點獨立生效。

---

## 改動 1：放寬 Claude Prompt

**文件**：`backend/app/services/competitor_matcher.py`

將「同級商品」改為「同類商品」，產地/等級作為參考而非過濾：

```
「同類商品」定義：
- 同類型產品（如：都是和牛、都是刺身、都是三文魚）
- 產地不同（宮崎 vs 鹿兒島）仍算同類 → is_match: true
- 等級不同（A5 vs A4）仍算同類 → is_match: true
- 規格差異（重量/包裝）作為參考，不影響是否匹配
- 只有完全不同類型才判 false（如：和牛 vs 三文魚）
```

涉及 3 處 prompt：
- `build_match_prompt()`（單一匹配）
- `build_batch_match_prompt()`（批量匹配）
- `_heuristic_match()` 的 threshold 維持 0.4 不變

## 改動 2：搜索 Keyword 加入核心品類

**文件**：`backend/app/services/competitor_matcher.py` → `generate_search_queries()`

新增 `extract_core_category()` 函數，從商品名提取核心品類詞作為寬泛搜索 keyword：

```python
CORE_CATEGORIES = [
    "和牛", "牛肉", "牛柳", "牛仔骨", "西冷", "肉眼",
    "豬扒", "豬腩", "排骨", "豬肉",
    "三文魚", "刺身", "帶子", "蝦", "蟹", "鮑魚", "龍蝦", "魚柳",
    "吞拿魚", "鰻魚", "海膽",
]
```

搜索 query 變為 `["宮崎A5和牛西冷", "和牛"]`，先精確後寬泛。

## 改動 3：Cataloger per-store 上限

**文件**：`backend/app/services/cataloger.py`

```python
HKTV_MAX_PRODUCTS_PER_STORE = 200
```

在 `_catalog_hktvmall()` 中追蹤 per-store 計數，超限則跳過。防止單一店鋪（如 Foodianna）灌入過多商品。

## 改動 4：動態 Threshold 微調

**文件**：`backend/app/services/competitor_matcher.py`

```python
# 之前
threshold = 0.3 if n <= 2 else 0.4 if n <= 5 else 0.5

# 之後（配合放寬 prompt，適度放寬分段）
threshold = 0.3 if n <= 3 else 0.4 if n <= 8 else 0.5
```

`save_match_to_db()` 的 save threshold 維持 0.4 不變。

---

## 不改的部分

- 三層搜索策略（API → Playwright → Firecrawl）不變
- v3 keyword 的 light_clean 邏輯不變
- 惠康搜索路徑不變
- DB schema 不變（無需 migration）
- 前端不改（後續可加 match_level filter）

## 預期效果

- 每個對手平均 match 數：1 件 → 5-15 件
- Foodianna 新建庫上限：200 件（現有 1594 件不影響，下次 rebuild 時生效）
- 搜索覆蓋面：精確+寬泛雙策略，不遺漏同類競品

## 驗證方式

```bash
# 1. 選一個有產地限定的 SKU（如宮崎 A5 和牛）
# 2. 觸發 batch matching
# 3. 檢查是否能 match 到其他產地的和牛
# 4. 檢查 Foodianna store 的商品數不超過 200
```
