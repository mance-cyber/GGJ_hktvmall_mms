# Task: Competitor Monitoring v2 — Backend Refactoring

## Overview
Refactor the competitor monitoring system from scratch. The old system was broken (scrape-everything-then-filter approach, is_active conflicts, wrong mappings). We're keeping the tables but clearing all data and reworking the schema + services.

## Database: Neon PostgreSQL
- Connection string is in `.env` as `DATABASE_URL`
- Uses SQLAlchemy + Alembic for migrations
- Models in `app/models/`, services in `app/services/`

## Phase 1: Schema Migration

### 1.1 Modify `competitors` table — add `tier` and `store_code`
```python
# In app/models/competitor.py - Competitor class
tier: Mapped[int] = mapped_column(Integer, default=2, comment="1=direct competitor, 2=category overlap, 3=reference")
store_code: Mapped[Optional[str]] = mapped_column(String(50), comment="HKTVmall store code for Algolia queries")
```

### 1.2 Modify `competitor_products` table
Remove these columns (drop from model, create migration):
- `category_tag` 
- `sub_tag`
- `needs_matching`
- `tag_source`
- `scrape_config_override`
- `scrape_error`

Add these columns:
```python
product_type: Mapped[Optional[str]] = mapped_column(String(20), default='unknown', comment="fresh/frozen/processed/unknown")
# Keep existing `category` column but repurpose for: 牛/豬/魚/蝦/蟹/貝/蠔/其他
unit_weight_g: Mapped[Optional[int]] = mapped_column(Integer, comment="weight in grams for unit price calc")
```

### 1.3 Modify `price_snapshots` table
Add:
```python
unit_price_per_100g: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
```

### 1.4 Modify `product_competitor_mapping` table  
Add:
```python
match_type: Mapped[str] = mapped_column(String(20), default='ai_matched', comment="ai_matched / manual")
```

### 1.5 Fix Alembic config to use .env DATABASE_URL
The `alembic.ini` has a hardcoded localhost URL but the real DB is Neon PostgreSQL (from `.env`). 
Update `alembic/env.py` to read DATABASE_URL from `.env` and override `sqlalchemy.url`:
```python
import os
from dotenv import load_dotenv
load_dotenv()
db_url = os.getenv("DATABASE_URL")
if db_url:
    config.set_main_option("sqlalchemy.url", db_url)
```

### 1.6 Create Alembic migration
- Create a new migration in `alembic/versions/`
- The migration should:
  1. TRUNCATE all data from: `price_alerts`, `price_snapshots`, `product_competitor_mapping`, `competitor_products`, then competitors (in order due to FKs)
  2. Add new columns
  3. Drop removed columns
  4. Add new indexes

### 1.7 Remove `scrape_config` FK from Competitor
The `scrape_config_id` FK and relationship should be removed from the Competitor model (we use Algolia now, not scraping configs).

## Phase 2: New Services

### 2.1 `services/algolia_fetcher.py` — NEW
Fetch products from HKTVmall via Algolia API.

Reference the existing working code:
- `../../scripts/hktvmall_algolia.py` (standalone script, sync)
- `app/connectors/hktv_api.py` (async, has `search_by_store_code` method)

Algolia config:
- App ID: `8RN1Y79F02`  
- API Key: `8e51a51f6078bd496eaa186bd08a3768`
- Index: `hktvProduct`
- URL: `https://8RN1Y79F02-dsn.algolia.net/1/indexes/*/queries`

For store_code filtering, use facetFilters:
```python
facet_filters = json.dumps([["storeCode:" + store_code]])
# Pass as: &facetFilters={url_encode(facet_filters)}
```

Two modes:
1. **Search by keyword** — for Line A (finding competitors for our products)
2. **Search by store_code** — for Line B (getting all products from a merchant)

```python
class AlgoliaFetcher:
    async def search_by_keyword(self, keyword: str, max_results: int = 50) -> list[dict]:
        """Search HKTVmall products by keyword"""
        
    async def search_by_store(self, store_code: str, max_results: int = 500) -> list[dict]:
        """Get all products from a specific store"""
        
    async def get_product_details(self, product_code: str) -> dict:
        """Get single product details"""
```

### 2.2 `services/ai_filter.py` — NEW
Use OpenClaw Gateway API to classify products as fresh/frozen/processed.

```python
class AIProductFilter:
    async def classify_products(self, products: list[dict]) -> list[dict]:
        """
        Batch classify products using Claude Sonnet via OpenClaw Gateway.
        
        Input: list of {name, sku, category, image_url}
        Output: list of {sku, relevant: bool, category: str, product_type: str, unit_weight_g: int|None, reason: str}
        
        Batch size: 50 products per API call
        """
```

OpenClaw Gateway API call example:
```python
import httpx

async def call_openclaw(prompt: str) -> str:
    """Call OpenClaw Gateway for AI classification"""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "http://localhost:3577/v1/chat/completions",
            json={
                "model": "anthropic/claude-sonnet-4-5",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1,
            },
            headers={"Authorization": "Bearer not-needed-for-local"},
            timeout=60.0,
        )
        return resp.json()["choices"][0]["message"]["content"]
```

The classification prompt should be:
```
你是 HKTVmall 生鮮食材分類專家。

判斷以下商品是否為「生鮮或冷凍食材」：
✅ 包括：生肉、冷凍肉、海鮮、冷凍海鮮、刺身、急凍魚生
❌ 排除：薯片、零食、便當、湯底、醬汁、調味料、即食品、飲品、日用品、加工食品（丸類、腸仔）、罐頭

對每件商品只返回 JSON array（不要其他文字）：
[
  {
    "sku": "商品SKU",
    "relevant": true/false,
    "category": "牛/豬/魚/蝦/蟹/貝/蠔/其他",
    "product_type": "fresh/frozen",
    "unit_weight_g": 200,
    "reason": "排除原因（只有 relevant=false 時填）"
  }
]

商品列表：
{products_json}
```

### 2.3 `services/competitor_builder.py` — NEW (replaces cataloger.py + product_competitor_finder.py)
The main orchestrator for building the competitor database.

```python
class CompetitorBuilder:
    """Build and maintain the competitor product database"""
    
    async def build_line_a(self):
        """Line A: For each of our 23 products, find competitors"""
        # 1. Get our products from DB
        # 2. For each, generate search keywords from name_zh / name
        # 3. Search Algolia
        # 4. Rule-based pre-filter (exclude obvious non-food by category)
        # 5. AI filter remaining
        # 6. Save to competitor_products
        # 7. Create mappings in product_competitor_mapping
    
    async def build_line_b(self):
        """Line B: For each Tier 1/2 merchant, get all fresh products"""
        # 1. Get active competitors with tier <= 2
        # 2. For each, search Algolia by store_code
        # 3. AI filter for fresh/frozen only
        # 4. Save to competitor_products (without mappings)
    
    async def refresh_prices(self):
        """Daily price refresh: fetch current prices for all active competitor products"""
        # 1. Get all active competitor_products
        # 2. Fetch current price from Algolia
        # 3. Create price_snapshots
        # 4. Calculate unit_price_per_100g
        # 5. Compare with previous snapshot, create alerts if needed
    
    async def discover_new_merchants(self):
        """Weekly: search for new competing merchants"""
        # Use category keywords to find new stores
        # Notify via return value (don't send Telegram directly)
```

### 2.4 `services/price_alerter.py` — NEW (replaces parts of monitor.py)
```python
class PriceAlerter:
    """Generate and manage price alerts"""
    
    async def check_alerts(self, new_snapshot: PriceSnapshot, previous_snapshot: PriceSnapshot) -> Optional[PriceAlert]:
        """Compare snapshots and generate alert if needed"""
        # Alert conditions:
        # - Direct competitor price drop > 10%
        # - Our product is cheapest in category
        # - New product from core merchant
        # - Competitor product delisted (was available, now not)
    
    async def get_pending_alerts(self) -> list[PriceAlert]:
        """Get unread alerts for notification"""
```

## Phase 3: Scripts

### 3.1 `scripts/init_competitors.py` — NEW
Initialize the competitor database with known merchants.

```python
INITIAL_COMPETITORS = [
    {"name": "Foodianna", "store_code": "H6852001", "tier": 1, "platform": "hktvmall"},
    {"name": "Ocean Three 皇海三寶", "store_code": "H0147001", "tier": 2, "platform": "hktvmall"},
    # Add more as Mance specifies
]
```

### 3.2 `scripts/run_competitor_build.py` — NEW
CLI script to run the competitor build process.

```python
"""
Usage:
    python scripts/run_competitor_build.py --mode full    # Full rebuild (Line A + B)
    python scripts/run_competitor_build.py --mode line-a  # Only Line A
    python scripts/run_competitor_build.py --mode line-b  # Only Line B
    python scripts/run_competitor_build.py --mode prices  # Price refresh only
    python scripts/run_competitor_build.py --mode discover # New merchant discovery
"""
```

## Phase 4: Delete Old Code

After the new services are working, these files should be cleaned up:
- `services/cataloger.py` — replaced by competitor_builder.py
- `services/product_competitor_finder.py` — replaced by competitor_builder.py
- `services/competitor_matcher.py` — replaced by ai_filter.py
- `services/matcher.py` — replaced by ai_filter.py
- `services/monitor.py` — replaced by price_alerter.py + competitor_builder.refresh_prices()

## Important Notes

1. **DO NOT delete the old files yet** — just create the new ones. We'll delete old ones after testing.
2. **Run the Alembic migration** after creating it: `cd backend && alembic upgrade head`
3. **Test with**: `python scripts/run_competitor_build.py --mode line-a` (after migration)
4. The frontend will be done separately — focus only on backend.
5. Use `async/await` throughout — the project uses FastAPI.
6. Import patterns: follow existing code style in the project.
7. The existing `app/connectors/hktv_api.py` has some Algolia code — check it for reference but create the new service fresh.

## File Structure After Changes

```
backend/
├── app/
│   ├── models/
│   │   ├── competitor.py      # MODIFIED (add tier, store_code, remove old fields)
│   │   └── ...
│   ├── services/
│   │   ├── algolia_fetcher.py  # NEW
│   │   ├── ai_filter.py        # NEW  
│   │   ├── competitor_builder.py # NEW
│   │   ├── price_alerter.py    # NEW
│   │   └── ...existing...
│   └── connectors/
│       └── hktv_api.py        # REFERENCE ONLY (has Algolia code to look at)
├── alembic/
│   └── versions/
│       └── xxxx_competitor_v2.py  # NEW migration
├── scripts/
│   ├── init_competitors.py    # NEW
│   └── run_competitor_build.py # NEW
└── TASK-competitor-v2.md      # This file (delete when done)
```
