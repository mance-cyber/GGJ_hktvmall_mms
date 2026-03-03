# Competitor Matching Relaxation — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Relax competitor matching so products of the same type (e.g. all wagyu) match regardless of origin/grade, and cap per-store cataloging at 200 products.

**Architecture:** Four independent changes to `competitor_matcher.py` (prompt, keyword gen, thresholds) and `cataloger.py` (per-store cap). No DB migration. No frontend changes.

**Tech Stack:** Python 3.11, pytest, Claude API prompts

**Design Doc:** `docs/plans/2026-03-03-competitor-matching-relaxation-design.md`

---

### Task 1: Add `extract_core_category()` and test it

**Files:**
- Modify: `backend/app/services/competitor_matcher.py:487-567` (add function + integrate into `generate_search_queries`)
- Create: `backend/tests/test_competitor_matcher.py`

**Step 1: Write the failing test**

Create `backend/tests/test_competitor_matcher.py`:

```python
"""競品匹配放寬：核心品類提取 + 搜索 keyword 生成"""
import pytest


# ==================== extract_core_category ====================

class TestExtractCoreCategory:
    """從商品名提取核心品類詞"""

    def test_wagyu_with_origin(self):
        from app.services.competitor_matcher import extract_core_category
        assert extract_core_category("宮崎 A5 和牛西冷") == "和牛"

    def test_salmon(self):
        from app.services.competitor_matcher import extract_core_category
        assert extract_core_category("挪威三文魚柳") == "三文魚"

    def test_scallop_sashimi(self):
        from app.services.competitor_matcher import extract_core_category
        assert extract_core_category("北海道帶子刺身") == "帶子"

    def test_no_match(self):
        from app.services.competitor_matcher import extract_core_category
        assert extract_core_category("有機蔬菜沙律") is None

    def test_empty_string(self):
        from app.services.competitor_matcher import extract_core_category
        assert extract_core_category("") is None

    def test_pork_chop(self):
        from app.services.competitor_matcher import extract_core_category
        assert extract_core_category("鹿兒島黑豚豬扒") == "豬扒"

    def test_priority_specific_over_generic(self):
        """和牛 should match before 牛肉 (more specific first)"""
        from app.services.competitor_matcher import extract_core_category
        assert extract_core_category("澳洲和牛牛肉") == "和牛"
```

**Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/test_competitor_matcher.py::TestExtractCoreCategory -v`
Expected: FAIL — `ImportError: cannot import name 'extract_core_category'`

**Step 3: Write the implementation**

Add before the `CompetitorMatcherService` class (around line 469) in `competitor_matcher.py`:

```python
# =============================================
# 核心品類詞表（用於寬泛搜索）
# =============================================
# 順序重要：更具體的詞排在前面（如「和牛」在「牛肉」之前）

CORE_CATEGORIES = [
    "和牛", "牛柳", "牛仔骨", "西冷", "肉眼", "牛肉",
    "豬扒", "豬腩", "排骨", "豬肉",
    "三文魚", "吞拿魚", "鰻魚", "魚柳",
    "刺身", "帶子", "蝦", "蟹", "鮑魚", "龍蝦", "海膽",
]


def extract_core_category(name: str) -> str | None:
    """從商品名提取核心品類詞（用於寬泛搜索 keyword）"""
    if not name:
        return None
    for cat in CORE_CATEGORIES:
        if cat in name:
            return cat
    return None
```

**Step 4: Run test to verify it passes**

Run: `cd backend && python -m pytest tests/test_competitor_matcher.py::TestExtractCoreCategory -v`
Expected: All 7 PASS

**Step 5: Integrate into `generate_search_queries()`**

In `competitor_matcher.py`, inside `generate_search_queries()`, add a new strategy between strategy 4 (分類子類) and strategy 5 (英文名). Insert after line 541:

```python
        # 策略 4.5: 核心品類詞（寬泛搜索，擴大候選池）
        if product.name_zh:
            core_cat = extract_core_category(product.name_zh)
            if core_cat and core_cat not in queries:
                queries.append(core_cat)
```

**Step 6: Commit**

```bash
git add backend/tests/test_competitor_matcher.py backend/app/services/competitor_matcher.py
git commit -m "feat: 新增核心品類提取 + 寬泛搜索 keyword

搜索 query 從 ['宮崎A5和牛西冷'] 變為 ['宮崎A5和牛西冷', '和牛']，
先精確搜再寬泛搜，擴大候選池。"
```

---

### Task 2: Relax Claude matching prompts

**Files:**
- Modify: `backend/app/services/competitor_matcher.py:180-215` (`build_match_prompt`)
- Modify: `backend/app/services/competitor_matcher.py:391-421` (`build_batch_match_prompt`)

**Step 1: Update `build_match_prompt()` (single match, line 180-215)**

Replace the prompt definition block (lines 181-215) with:

```python
        return f"""
你是一位專業的日本海鮮/食材專家。請判斷以下兩個商品是否為「同類商品」。

「同類商品」定義：
- 同類型產品（如：都是和牛、都是刺身、都是三文魚）
- 產地不同（宮崎 vs 鹿兒島）仍算同類 → is_match: true
- 等級不同（A5 vs A4）仍算同類 → is_match: true
- 規格差異（重量/包裝）作為參考，不影響是否匹配
- 只有完全不同類型才判 false（如：和牛 vs 三文魚）

---

我方商品（GogoJap）:
- 中文名: {our_product.get('name_zh', 'N/A')}
- 日文名: {our_product.get('name_ja', 'N/A')}
- 英文名/規格: {our_product.get('name_en', 'N/A')}
- 分類: {our_product.get('category_main', '')} > {our_product.get('category_sub', '')}
- 單位: {our_product.get('unit', 'N/A')}

---

對手商品:
- 名稱: {candidate.get('name', 'N/A')}
- 價格: {candidate.get('price', 'N/A')}
- 描述: {candidate.get('description', 'N/A')[:500] if candidate.get('description') else 'N/A'}

---

請以 JSON 格式回答：
{{
  "is_match": true/false,
  "confidence": 0.0-1.0,
  "reason": "判斷理由（簡短說明）",
  "key_differences": ["差異1", "差異2"] // 如果不匹配，列出主要差異
}}

只輸出 JSON，不要其他內容。
"""
```

**Step 2: Update `build_batch_match_prompt()` (batch match, line 391-421)**

Replace the prompt definition block (lines 391-397) with:

```python
        return f"""你是一位專業的日本海鮮/食材專家。請判斷以下每個對手商品是否與我方商品為「同類商品」。

「同類商品」定義：
- 同類型產品（如：都是和牛、都是刺身、都是三文魚）
- 產地不同（宮崎 vs 鹿兒島）仍算同類 → is_match: true
- 等級不同（A5 vs A4）仍算同類 → is_match: true
- 規格差異（重量/包裝）作為參考，不影響是否匹配
- 只有完全不同類型才判 false（如：和牛 vs 三文魚）
```

(Rest of the batch prompt from `---` onward stays unchanged.)

**Step 3: Verify no other prompt references**

Run: `grep -n "同級商品" backend/app/services/competitor_matcher.py`
Expected: 0 results (all replaced with 同類商品)

**Step 4: Commit**

```bash
git add backend/app/services/competitor_matcher.py
git commit -m "feat: 放寬 Claude 匹配 prompt — 同級商品 → 同類商品

產地不同（宮崎 vs 鹿兒島）、等級不同（A5 vs A4）仍算 match，
只有完全不同類型（和牛 vs 三文魚）才判 false。"
```

---

### Task 3: Adjust dynamic thresholds

**Files:**
- Modify: `backend/app/services/competitor_matcher.py` (3 locations: lines 727, 809, 875)

**Step 1: Find all threshold locations**

Run: `grep -n "0.3 if n <= 2 else 0.4 if n <= 5 else 0.5" backend/app/services/competitor_matcher.py`
Expected: 3 matches (lines ~727, ~809, ~875)

**Step 2: Replace all 3 occurrences**

Change each from:
```python
threshold = 0.3 if n <= 2 else 0.4 if n <= 5 else 0.5
```
To:
```python
threshold = 0.3 if n <= 3 else 0.4 if n <= 8 else 0.5
```

**Step 3: Verify**

Run: `grep -n "0.3 if n <= 3 else 0.4 if n <= 8 else 0.5" backend/app/services/competitor_matcher.py`
Expected: 3 matches

Run: `grep -n "0.3 if n <= 2" backend/app/services/competitor_matcher.py`
Expected: 0 matches

**Step 4: Commit**

```bash
git add backend/app/services/competitor_matcher.py
git commit -m "feat: 放寬動態匹配 threshold 分段

n<=3 用 0.3（原 n<=2），n<=8 用 0.4（原 n<=5），
配合放寬的 prompt 擴大接受範圍。"
```

---

### Task 4: Add per-store cap to Cataloger and test it

**Files:**
- Modify: `backend/app/services/cataloger.py:41-46` (add constant), `:128-178` (add store counting logic)
- Modify: `backend/tests/test_competitor_matcher.py` (add cataloger tests)

**Step 1: Write the failing test**

Add to `backend/tests/test_competitor_matcher.py`:

```python
class TestCatalogerStoreLimit:
    """Cataloger per-store 上限"""

    def test_constant_exists(self):
        from app.services.cataloger import HKTV_MAX_PRODUCTS_PER_STORE
        assert HKTV_MAX_PRODUCTS_PER_STORE == 200

    def test_constant_is_reasonable(self):
        from app.services.cataloger import HKTV_MAX_PRODUCTS_PER_STORE
        assert 50 <= HKTV_MAX_PRODUCTS_PER_STORE <= 500
```

**Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/test_competitor_matcher.py::TestCatalogerStoreLimit -v`
Expected: FAIL — `ImportError: cannot import name 'HKTV_MAX_PRODUCTS_PER_STORE'`

**Step 3: Add constant and store counting to `cataloger.py`**

After line 63 (`WELLCOME_MAX_PAGES = 5`), add:

```python
# 每個店鋪最多入庫商品數（防止單一店鋪灌水）
HKTV_MAX_PRODUCTS_PER_STORE = 200
```

In `_catalog_hktvmall()`, after `stats = {...}` (line 130), add:

```python
        store_counts: dict[str, int] = {}  # store_name → 已入庫數量
```

Replace the product processing loop (lines 144-168) with:

```python
                    for product in products:
                        if not product.url or product.url in seen_urls:
                            continue

                        # per-store 上限檢查
                        store = product.store_name or "unknown"
                        if store_counts.get(store, 0) >= HKTV_MAX_PRODUCTS_PER_STORE:
                            stats["skipped_store_limit"] = stats.get("skipped_store_limit", 0) + 1
                            continue

                        seen_urls.add(product.url)
                        stats["total_fetched"] += 1
                        store_counts[store] = store_counts.get(store, 0) + 1

                        # 組裝擴展數據（plus_price）
                        extra_data = (
                            {"plus_price": str(product.plus_price)}
                            if product.plus_price is not None else None
                        )

                        action = await CatalogService._upsert_competitor_product(
                            db=db,
                            competitor_id=competitor.id,
                            url=product.url,
                            name=product.name,
                            price=product.price,
                            sku=product.sku,
                            platform="hktvmall",
                            original_price=product.original_price,
                            review_count=product.review_count,
                            extra_data=extra_data,
                        )
                        stats[action] += 1
```

Also update the final log message (around line 182) to include store limit skips:

```python
        logger.info(
            f"hktvmall 建庫完成: 去重後 {stats['total_fetched']} 商品, "
            f"新增 {stats['new']}, 更新 {stats['updated']}, "
            f"無變化 {stats['unchanged']}, "
            f"店鋪上限跳過 {stats.get('skipped_store_limit', 0)}"
        )
```

**Step 4: Run tests**

Run: `cd backend && python -m pytest tests/test_competitor_matcher.py -v`
Expected: All tests PASS

**Step 5: Commit**

```bash
git add backend/app/services/cataloger.py backend/tests/test_competitor_matcher.py
git commit -m "feat: Cataloger per-store 上限 200 件

防止單一店鋪（如 Foodianna）灌入過多商品。
超限商品跳過並記錄 skipped_store_limit 統計。"
```

---

### Task 5: Final verification

**Step 1: Run all tests**

Run: `cd backend && python -m pytest tests/test_competitor_matcher.py -v`
Expected: All PASS

**Step 2: Grep sanity checks**

```bash
# 確認沒有殘留的「同級商品」
grep -rn "同級商品" backend/app/services/competitor_matcher.py
# Expected: 0 results

# 確認所有 threshold 已更新
grep -n "0.3 if n <= 2" backend/app/services/competitor_matcher.py
# Expected: 0 results

# 確認 extract_core_category 已導出
grep -n "extract_core_category" backend/app/services/competitor_matcher.py
# Expected: function def + usage in generate_search_queries
```

**Step 3: Quick import check**

```bash
cd backend && python -c "
from app.services.competitor_matcher import extract_core_category, CORE_CATEGORIES
from app.services.cataloger import HKTV_MAX_PRODUCTS_PER_STORE
print(f'CORE_CATEGORIES: {len(CORE_CATEGORIES)} items')
print(f'HKTV_MAX_PRODUCTS_PER_STORE: {HKTV_MAX_PRODUCTS_PER_STORE}')
print(f'extract_core_category(\"宮崎A5和牛西冷\"): {extract_core_category(\"宮崎A5和牛西冷\")}')
print('All imports OK')
"
```
Expected: Prints counts and "和牛" and "All imports OK"

**Step 4: Update design doc status**

Change the design doc header from `狀態：已批准，待實現` to `狀態：已實現`

**Step 5: Final commit**

```bash
git add docs/plans/2026-03-03-competitor-matching-relaxation-design.md
git commit -m "docs: 標記競品匹配放寬設計為已實現"
```
