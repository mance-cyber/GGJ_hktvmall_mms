# Task: Competitor Dashboard v2 — Frontend

## Overview
Replace the existing competitors page with a new v2 dashboard that has two views:
- **View A (Product View)**: Each of our products with their competitor prices
- **View B (Merchant View)**: Each competitor merchant with their product catalog

Both views have a toggle: "自家競品" (only mapped products) vs "全部生鮮" (all fresh products)

## Tech Stack
- Next.js 14+ (App Router)
- TanStack React Query for data fetching
- Framer Motion for animations
- Tailwind CSS + shadcn/ui components
- Custom "future-tech" UI components in `@/components/ui/future-tech`
- i18n via `useLocale` from `@/components/providers/locale-provider`

## Design Requirements
- **Dark theme** (existing app is dark themed)
- **Clean, modern dashboard** feel
- Price comparisons: red = competitor is cheaper, green = we are cheaper
- Responsive (desktop primary, mobile secondary)

## Backend API Endpoints

The backend at `/api/v1/competitors` already has:
- `GET /api/v1/competitors` — list all competitors
- `GET /api/v1/competitors/{id}/products` — products for a competitor
- `GET /api/v1/competitors/products/{id}/price-history` — price history

We need NEW endpoints. Add them to `backend/app/api/v1/competitors.py`:

### New Endpoint 1: Product Comparison View
```
GET /api/v1/competitors/comparison/products
```
Returns our products with their competitor mappings and latest prices:
```json
{
  "items": [
    {
      "product": {
        "id": "...",
        "name": "A5 和牛西冷",
        "sku": "GGJ-001",
        "price": 388.0,
        "image_url": "...",
        "category_tag": "牛"
      },
      "competitors": [
        {
          "competitor_name": "Foodianna",
          "competitor_tier": 1,
          "product_name": "日本A5和牛西冷扒",
          "price": 358.0,
          "original_price": 428.0,
          "unit_price_per_100g": 179.0,
          "price_change_7d": -5.2,
          "stock_status": "in_stock",
          "url": "https://...",
          "last_updated": "2026-03-06T12:00:00"
        }
      ],
      "cheapest_competitor": "Foodianna",
      "our_price_rank": 2,
      "total_competitors": 5
    }
  ]
}
```

### New Endpoint 2: Merchant Overview
```
GET /api/v1/competitors/comparison/merchants
```
Returns merchant-level overview:
```json
{
  "items": [
    {
      "competitor": {
        "id": "...",
        "name": "Foodianna",
        "tier": 1,
        "store_code": "H6852001",
        "total_products": 156,
        "fresh_products": 142,
        "overlap_products": 18,
        "unique_products": 124
      },
      "price_comparison": {
        "cheaper_count": 8,
        "same_count": 2,
        "expensive_count": 8,
        "avg_price_diff_pct": -3.5
      },
      "recent_changes": [
        {
          "product_name": "...",
          "change_type": "price_drop",
          "old_price": 388,
          "new_price": 348,
          "change_pct": -10.3,
          "date": "2026-03-06"
        }
      ]
    }
  ]
}
```

### New Endpoint 3: Dashboard Summary Stats
```
GET /api/v1/competitors/comparison/summary
```
Returns high-level stats for the dashboard header:
```json
{
  "total_competitors": 17,
  "total_tracked_products": 450,
  "our_products": 23,
  "mapped_competitors": 120,
  "price_alerts_24h": 5,
  "we_are_cheapest_pct": 45,
  "avg_price_diff_pct": -2.3,
  "last_scan": "2026-03-06T15:00:00"
}
```

## Frontend Implementation

### File: `src/app/competitors/page.tsx` (REPLACE existing)

The page should have:

1. **Dashboard Header** — Summary stats cards (total competitors, tracked products, price alerts, etc.)

2. **View Toggle** — Two tabs: "📦 商品視角" and "🏪 商戶視角"

3. **Scope Toggle** — "🎯 自家競品" vs "🌊 全部生鮮"

4. **View A: Product View** (default)
   - Each of our 23 products as expandable cards
   - Show our price, number of competitors, cheapest competitor
   - Expand to see all competitor prices in a comparison table
   - Color coding: green if we're cheapest, red if competitor is cheaper
   - Sort by: name, price diff, competitor count

5. **View B: Merchant View**
   - Each merchant as a card showing tier badge, overlap count, price comparison summary
   - Click to expand and see product overlap details
   - Show "unique products" (things they sell that we don't)

### Components to Create

1. `src/components/competitors/dashboard-stats.tsx` — Stats cards header
2. `src/components/competitors/product-comparison-card.tsx` — Product with competitor prices
3. `src/components/competitors/merchant-overview-card.tsx` — Merchant summary card
4. `src/components/competitors/price-badge.tsx` — Price comparison badge (green/red/neutral)
5. `src/components/competitors/tier-badge.tsx` — Tier 1/2/3 badge

### API Client Updates

Add to `src/lib/api.ts`:
```typescript
// Competitor v2 comparison types
export interface CompetitorPrice {
  competitor_name: string
  competitor_tier: number
  product_name: string
  price: number | null
  original_price: number | null
  unit_price_per_100g: number | null
  price_change_7d: number | null
  stock_status: string | null
  url: string
  last_updated: string
}

export interface ProductComparison {
  product: {
    id: string
    name: string
    sku: string
    price: number | null
    image_url: string | null
    category_tag: string | null
  }
  competitors: CompetitorPrice[]
  cheapest_competitor: string | null
  our_price_rank: number
  total_competitors: number
}

export interface MerchantOverview {
  competitor: {
    id: string
    name: string
    tier: number
    store_code: string | null
    total_products: number
    fresh_products: number
    overlap_products: number
    unique_products: number
  }
  price_comparison: {
    cheaper_count: number
    same_count: number
    expensive_count: number
    avg_price_diff_pct: number
  }
  recent_changes: Array<{
    product_name: string
    change_type: string
    old_price: number
    new_price: number
    change_pct: number
    date: string
  }>
}

export interface ComparisonSummary {
  total_competitors: number
  total_tracked_products: number
  our_products: number
  mapped_competitors: number
  price_alerts_24h: number
  we_are_cheapest_pct: number
  avg_price_diff_pct: number
  last_scan: string | null
}

// API methods
getComparisonProducts: () => fetchAPI<{items: ProductComparison[]}>('/competitors/comparison/products'),
getComparisonMerchants: () => fetchAPI<{items: MerchantOverview[]}>('/competitors/comparison/merchants'),
getComparisonSummary: () => fetchAPI<ComparisonSummary>('/competitors/comparison/summary'),
```

## Important Notes

1. Keep the existing competitor CRUD functionality accessible (maybe as a "Manage" tab)
2. Use the existing `future-tech` components for consistent styling
3. The `useLocale` hook returns `{ t, locale }` — use `t('key')` for translations, but for v2 you can hardcode Chinese text first
4. Follow the existing code patterns in the app
5. Backend runs on port 8000, frontend on 3000, but API calls go through Next.js proxy
6. The existing `api.ts` has a `fetchAPI` helper — use it
7. Don't break existing functionality — the old page can be kept as a backup
