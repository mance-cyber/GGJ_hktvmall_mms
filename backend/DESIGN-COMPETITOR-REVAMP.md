# 競品抓取系統重構設計

> 狀態：待確認
> 日期：2026-03-06
> 作者：Eve

---

## 問題

1. **抓到唔關事嘅商品** — Algolia 搜「和牛」返回和牛味薯片、湯底、零食，全部入庫
2. **expand_competitor_stores 掃全店** — Foodianna 一間就 1,984 件（佔 46%），大部分唔關事
3. **冇庫存狀態** — Algolia 回傳 `hasStock` 但從未被 parse
4. **邏輯倒轉** — 而家係「搜關鍵詞 → 入庫 → 再配對自家商品」，應該係「以自家商品為起點 → 搵佢嘅競品」

## 現狀數據

- 自家商品：23 件（20 件有 category_tag + sub_tag）
- 競品商品：4,295 件（大量冗餘）
- 4,295 件入面，真正有 mapping 到自家商品的有多少？待查

---

## 新設計：Product-Driven Competitor Discovery

### 核心邏輯

```
自家商品（23 件）
  │
  ├─ 每件商品 → 生成搜索策略
  │   ├─ Query 1（精確）：商品全名（如「宮崎A5和牛西冷」）
  │   ├─ Query 2（品類）：sub_tag（如「和牛 西冷」）
  │   └─ Query 3（大類）：category_tag（如「牛扒」「牛肉」）
  │
  ├─ Algolia 搜索 → 品類過濾 → 入庫
  │   ├─ ✅ catNameZh 含食品/超市/肉類/海鮮 → 保留
  │   ├─ ❌ catNameZh 含零食/調味/日用 → 排除
  │   ├─ ❌ 名字含「味」「拉麵」「湯底」「醬」「零食」→ 排除
  │   └─ ✅ 解析 hasStock → stock_status
  │
  └─ 自動建立 product_competitor_mapping
      ├─ match_level=1：名字高度相似（直接替代品）
      ├─ match_level=2：同 sub_tag（近似競品）
      └─ match_level=3：同 category_tag（品類競品）
```

### 搜索策略表

基於自家商品的 `category_tag` + `sub_tag` 自動生成搜索 queries：

| category_tag | sub_tag | 生成的搜索 Queries |
|---|---|---|
| 牛 | 和牛 | `"和牛"`, `"A5和牛"`, `"和牛 西冷"`, `"和牛 肉眼"` |
| 牛 | 牛扒 | `"牛扒"`, `"西冷牛扒"`, `"肉眼牛扒"` |
| 魚 | 刺身 | `"刺身"`, `"三文魚刺身"`, `"吞拿魚刺身"` |
| 魚 | 魚柳 | `"魚柳"`, `"三文魚柳"`, `"鱈魚柳"` |
| 豬 | 豬扒 | `"豬扒"`, `"急凍豬扒"`, `"厚切豬扒"` |
| 蝦 | 蝦 | `"蝦"`, `"急凍蝦"`, `"虎蝦"`, `"甜蝦"` |
| 貝 | 帶子 | `"帶子"`, `"急凍帶子"`, `"北海道帶子"` |

### 品類過濾規則

**Algolia catNameZh 白名單（保留）：**
```python
FOOD_CATEGORIES = {
    "急凍食品", "肉類", "海鮮", "魚類", "蝦蟹貝類",
    "超級市場", "新鮮食品", "凍肉", "刺身",
    "牛肉", "豬肉", "雞肉", "羊肉",
}
```

**名字黑名單（排除）：**
```python
NON_FOOD_KEYWORDS = {
    "味", "拉麵", "湯底", "醬", "調味", "零食",
    "薯片", "餅乾", "糖果", "飲品", "杯麵",
    "貓", "狗", "寵物",  # 沿用現有
    "清潔", "廚具", "餐具",
}
```

### hasStock 解析

Algolia 已回傳 `hasStock` 但未被使用。修改 `_parse_algolia_hits()`：

```python
# hasStock 解析
has_stock = hit.get("hasStock")
stock_status = None
if has_stock is True:
    stock_status = "in_stock"
elif has_stock is False:
    stock_status = "out_of_stock"
```

寫入 `HKTVProduct` 新增 `stock_status` 字段 → 寫入 `PriceSnapshot.stock_status`。

---

## 改動範圍

### 新建

| 檔案 | 說明 |
|---|---|
| `services/product_competitor_finder.py` | 新服務：以自家商品為起點搵競品 |
| `scripts/run_competitor_finder.py` | CLI 入口 |

### 修改

| 檔案 | 改動 |
|---|---|
| `connectors/hktv_api.py` | `_parse_algolia_hits()` 加 `hasStock` 解析 + `HKTVProduct` 加 `stock_status` |
| `connectors/hktv_api.py` | `HKTVProduct` dataclass 加 `stock_status` 和 `category` 字段 |
| `services/cataloger.py` | `_upsert_competitor_product()` 傳入 `stock_status` |

### 不改（保留）

| 檔案 | 原因 |
|---|---|
| `models/competitor.py` | Schema 已經夠用（`PriceSnapshot.stock_status` 已有） |
| `models/product.py` | `ProductCompetitorMapping` 已有 `match_level`、`match_confidence` |
| `services/matcher.py` | AI matcher 保留，可選用做精細 matching |

### 棄用（唔再使用）

| 檔案 | 原因 |
|---|---|
| `scripts/expand_competitor_stores.py` | 掃全店邏輯不再需要 |
| `scripts/expand_remaining.py` | 同上 |
| `HKTV_KEYWORDS` in cataloger.py | 改用自家商品 tag 動態生成 |

---

## 新服務：ProductCompetitorFinder

```python
class ProductCompetitorFinder:
    """
    以自家商品為起點，搵 HKTVmall 上嘅競品
    
    流程：
    1. 讀取所有有 tag 嘅自家商品
    2. 每件商品 → 生成搜索 queries
    3. Algolia 搜索 → 品類過濾 → 入庫
    4. 自動建 product_competitor_mapping
    5. 記錄 stock_status
    """
    
    async def find_all(self, db) -> dict:
        """全量搜索所有自家商品的競品"""
        
    async def find_for_product(self, db, product_id) -> dict:
        """搜索單件自家商品的競品"""
        
    def _generate_queries(self, product) -> list[str]:
        """基於商品 tag 生成搜索 queries"""
        
    def _is_relevant(self, hit, product) -> bool:
        """品類過濾：判斷搜索結果是否為相關食材"""
        
    def _calculate_match_level(self, product, competitor) -> int:
        """計算 match_level：1=直接替代、2=近似、3=品類"""
```

### Query 生成邏輯

```python
def _generate_queries(self, product: Product) -> list[str]:
    queries = []
    
    # Level 1：精確名字（去掉品牌和規格）
    if product.name:
        # "宮崎A5和牛西冷 200g" → "宮崎A5和牛西冷"
        clean_name = re.sub(r'\d+[gGkK]+.*$', '', product.name).strip()
        queries.append(clean_name)
    
    # Level 2：sub_tag 組合
    if product.sub_tag:
        queries.append(product.sub_tag)  # "和牛"
        if product.category_tag:
            queries.append(f"{product.sub_tag} {product.category_tag}")  # "和牛 牛"
    
    # Level 3：category_tag
    if product.category_tag:
        queries.append(f"急凍{product.category_tag}")  # "急凍牛"
    
    return list(dict.fromkeys(queries))  # 去重保序
```

### 品類過濾邏輯

```python
def _is_relevant(self, hit: dict, product: Product) -> bool:
    name = hit.get("nameZh", "")
    categories = hit.get("catNameZh", [])
    cat_text = " ".join(categories) if categories else ""
    
    # 黑名單排除
    for kw in NON_FOOD_KEYWORDS:
        if kw in name:
            return False
    
    # 白名單檢查（catNameZh 至少命中一個食品分類）
    if categories:
        if not any(fc in cat_text for fc in FOOD_CATEGORIES):
            return False
    
    # 排除自家商品（GoGoJap 自己的店鋪）
    store = hit.get("storeNameZh", "")
    if "GoGoJap" in store or "GoGoFoods" in store:
        return False
    
    return True
```

---

## 數據清理計劃

### Phase 1：先跑新系統
1. 唔刪現有數據
2. 跑 `ProductCompetitorFinder.find_all()` → 新增有效競品 + mapping
3. 比較新舊數據差異

### Phase 2：清理（需要 Mance 確認）
1. 標記冇 mapping 到任何自家商品嘅競品為 `is_active=False`
2. 或者直接刪除（但建議先 soft delete）

---

## 預期效果

| 指標 | 而家 | 改造後（估算） |
|---|---|---|
| 競品商品數 | 4,295 | ~200-400（真正相關的） |
| 有 mapping 到自家商品 | 待查 | 100%（入庫即 mapping） |
| 有庫存狀態 | 0% | 100% |
| Foodianna 1,984 件 | 全部入庫 | 只保留相關食材 |
| 更新頻率 | keyword 掃描 | 以 23 件自家商品為單位 |

---

## 執行計劃

1. ✅ 設計確認
2. 修改 `hktv_api.py` — 加 `hasStock` + `stock_status` + `category`
3. 新建 `services/product_competitor_finder.py`
4. 新建 `scripts/run_competitor_finder.py`
5. 測試：跑 dry-run 睇結果
6. 清理：soft delete 無關競品
