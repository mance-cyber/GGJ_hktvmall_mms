# Task: 競品監測 Dashboard UI Redesign

## Objective
Redesign the competitor monitoring dashboard to match the reference layout (split-panel, threat-grouped cards, inline chart) while keeping our existing teal-based color system.

## Reference Layout (from screenshot)
The design should follow this structure:

### 1. Header
- Title: "競品監測" with subtitle showing merchant/product counts
- Right side: "匯出 CSV" + "刷新" buttons (ALREADY EXISTS, keep as-is)

### 2. Stats Cards Row (ALREADY EXISTS, minor tweaks)
- 5-6 cards in a row, keep current color mapping
- No changes needed here

### 3. Tab Navigation (ALREADY EXISTS, keep as-is)
- 商品視角 | 商戶視角 | 改價建議
- Scope toggle: 自家競品 | 全部生鮮

### 4. Filter Bar (ALREADY EXISTS, keep as-is)
- Search + category dropdown + sort chips

### 5. ⭐ MAIN CHANGE: Split-Panel Layout (Products View)
**Left Panel (~55% width on desktop, full-width on mobile):**
- Product cards GROUPED by threat level:
  - 🟢 "最小最低價格" group — we're cheapest (emerald badge/border)
  - 🟡 "商戶超越 · 價差 5-20%" group — warning (amber badge/border)
  - 🔴 "威脅程度 · 價差 >20%" group — danger (red badge/border)
  - ⚪ "正常範圍" group — no competitor data or neutral (gray badge/border)
- Each group has a colored header badge + expand/collapse
- Each product card shows in a structured row:
  - GoGoJap 價格
  - 最低競手價格
  - 價差 (amount + percentage)
  - 便宜競比數 (how many are cheaper)
  - 排名
  - 股貨狀態

**Right Panel (~45% width on desktop, hidden on mobile until product selected):**
- Shows details for the SELECTED product (clicking a product card selects it)
- Price History Chart (30-day, multi-line, using recharts — ALREADY EXISTS in price-history-modal.tsx)
  - Move chart from modal to inline panel
  - Show "查看 30 日趨勢" button inside chart area
- Competitor Price Table below chart:
  - Columns: 商戶名稱 | 售價 | 7天價格趨勢 (sparkline) | 股數 | 外規 (external link)
  - GoGoJap row highlighted in teal
  - Each competitor row shows tier badge
  - Sparkline for 7-day trend (use recharts tiny line or simple SVG)

### 6. Mobile Behavior
- On mobile (<768px): full-width single column
- Product list shows normally
- Tapping a product opens the detail panel as a slide-up sheet or expandable section
- Detail panel has a close/back button on mobile

## Color System (DO NOT CHANGE)
- **Teal** (#0d9488 / teal-500): primary accent, GoGoJap price text, selected states
- **Teal-50**: backgrounds, highlights
- **Emerald**: positive signals (we're cheapest, competitor more expensive)
- **Amber**: warning signals (5-20% gap)
- **Red**: danger signals (>20% gap)
- **Purple**: neutral emphasis (unique products count)
- **Gray scale**: text hierarchy (800 → 600 → 400 → 200)
- Gradient cards: `from-white to-{color}-50/50`
- Page bg: `from-gray-50 via-white to-teal-50/30`

## Files to Modify
All in `src/`:

1. **`app/competitors/page.tsx`** — Main page, add split-panel layout + selected product state
2. **`components/competitors/product-comparison-card.tsx`** — Simplify to list-item style (not full expandable card), add click-to-select
3. **NEW `components/competitors/product-detail-panel.tsx`** — Right panel with chart + competitor table
4. **NEW `components/competitors/threat-group.tsx`** — Grouped container with colored badge header
5. **`components/competitors/price-history-modal.tsx`** — Keep as fallback for mobile, but main usage moves to inline panel

## Existing API Types (DO NOT CHANGE)
```typescript
interface ProductComparison {
  product: { id, name, sku, price, image_url, category_tag }
  competitors: CompetitorPrice[]  // { competitor_name, competitor_tier, price, price_change_7d, stock_status, url, ... }
  cheapest_competitor: string | null
  our_price_rank: number
  total_competitors: number
}
```

API endpoints already exist — no backend changes needed.

## Tech Stack
- Next.js 14 (App Router)
- React + TypeScript
- Tailwind CSS
- Framer Motion (for animations)
- Recharts (for charts)
- Lucide icons
- @tanstack/react-query

## Important Notes
- Keep all existing functionality (search, sort, filter, export, refresh)
- Merchants view and Suggestions view stay the same (single column)
- Only Products view gets the split-panel treatment
- Use `cn()` from `@/lib/utils` for conditional classnames
- Animation transitions should be 0.2s, subtle
- Selected product should have a visual indicator (teal left border or highlight)
