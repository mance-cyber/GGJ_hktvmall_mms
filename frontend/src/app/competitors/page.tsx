'use client'

import { useState, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'
import { motion } from 'framer-motion'
import { Package, Building2, RefreshCw, Target, Globe, Download, Lightbulb } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { DashboardStats } from '@/components/competitors/dashboard-stats'
import { ProductComparisonCard } from '@/components/competitors/product-comparison-card'
import { MerchantOverviewCard } from '@/components/competitors/merchant-overview-card'
import { FilterBar, SortKey, SortDir } from '@/components/competitors/filter-bar'
import { PriceHistoryModal } from '@/components/competitors/price-history-modal'
import { PricingSuggestionsPanel } from '@/components/competitors/pricing-suggestions-panel'

type ViewMode = 'products' | 'merchants' | 'suggestions'
type ScopeMode = 'mapped' | 'all'

export default function CompetitorsPage() {
  const [view, setView] = useState<ViewMode>('products')
  const [scope, setScope] = useState<ScopeMode>('mapped')

  // Filter/sort state
  const [search, setSearch] = useState('')
  const [categoryFilter, setCategoryFilter] = useState('')
  const [sortKey, setSortKey] = useState<SortKey>('threat')
  const [sortDir, setSortDir] = useState<SortDir>('desc')

  // Price history modal
  const [historyProduct, setHistoryProduct] = useState<{ id: string; name: string } | null>(null)

  // ── Queries ──────────────────────────────────
  const { data: summary, isLoading: summaryLoading, refetch: refetchSummary } = useQuery({
    queryKey: ['comparison-summary'],
    queryFn: () => api.getComparisonSummary(),
  })

  const { data: products, isLoading: productsLoading, refetch: refetchProducts } = useQuery({
    queryKey: ['comparison-products', scope],
    queryFn: () => api.getComparisonProducts(scope),
    enabled: view === 'products',
  })

  const { data: merchants, isLoading: merchantsLoading, refetch: refetchMerchants } = useQuery({
    queryKey: ['comparison-merchants'],
    queryFn: () => api.getComparisonMerchants(),
    enabled: view === 'merchants',
  })

  const handleRefresh = () => {
    refetchSummary()
    if (view === 'products') refetchProducts()
    if (view === 'merchants') refetchMerchants()
  }

  // ── Categories (for filter dropdown) ─────────
  const categories = useMemo(() => {
    if (!products?.items) return []
    const cats = new Set(products.items.map(i => i.product.category_tag).filter(Boolean) as string[])
    return Array.from(cats).sort()
  }, [products])

  // ── Filter + Sort products ────────────────────
  const filteredProducts = useMemo(() => {
    if (!products?.items) return []
    let items = products.items

    // Search
    if (search.trim()) {
      const q = search.toLowerCase()
      items = items.filter(i => i.product.name.toLowerCase().includes(q))
    }

    // Category
    if (categoryFilter) {
      items = items.filter(i => i.product.category_tag === categoryFilter)
    }

    // Sort
    items = [...items].sort((a, b) => {
      let va: number, vb: number
      const ourA = a.product.price || 0
      const ourB = b.product.price || 0
      const cheapA = a.competitors[0]?.price || 0
      const cheapB = b.competitors[0]?.price || 0

      switch (sortKey) {
        case 'threat':
          // Higher diff% = more threat
          va = cheapA && ourA ? (ourA - cheapA) / ourA * 100 : -999
          vb = cheapB && ourB ? (ourB - cheapB) / ourB * 100 : -999
          break
        case 'price_diff':
          va = cheapA && ourA ? Math.abs((ourA - cheapA) / ourA * 100) : 0
          vb = cheapB && ourB ? Math.abs((ourB - cheapB) / ourB * 100) : 0
          break
        case 'rank':
          va = a.our_price_rank
          vb = b.our_price_rank
          break
        case 'competitors':
          va = a.total_competitors
          vb = b.total_competitors
          break
        case 'name':
        default:
          return sortDir === 'asc'
            ? a.product.name.localeCompare(b.product.name)
            : b.product.name.localeCompare(a.product.name)
      }
      return sortDir === 'desc' ? vb - va : va - vb
    })

    return items
  }, [products, search, categoryFilter, sortKey, sortDir])

  // ── Filter + Sort merchants ────────────────────
  const filteredMerchants = useMemo(() => {
    if (!merchants?.items) return []
    let items = merchants.items

    if (search.trim()) {
      const q = search.toLowerCase()
      items = items.filter(i => i.competitor.name.toLowerCase().includes(q))
    }

    items = [...items].sort((a, b) => {
      let va: number, vb: number
      switch (sortKey) {
        case 'threat':
          va = -a.price_comparison.avg_price_diff_pct
          vb = -b.price_comparison.avg_price_diff_pct
          break
        case 'competitors':
          va = a.competitor.total_products
          vb = b.competitor.total_products
          break
        case 'name':
        default:
          return sortDir === 'asc'
            ? a.competitor.name.localeCompare(b.competitor.name)
            : b.competitor.name.localeCompare(a.competitor.name)
      }
      return sortDir === 'desc' ? vb - va : va - vb
    })

    return items
  }, [merchants, search, sortKey, sortDir])

  const showFilterBar = view === 'products' || view === 'merchants'
  const isListLoading = view === 'products' ? productsLoading : merchantsLoading
  const listTotal = view === 'products' ? (products?.items.length ?? 0) : (merchants?.items.length ?? 0)
  const listFiltered = view === 'products' ? filteredProducts.length : filteredMerchants.length

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-teal-50/30 px-3 py-4 sm:p-6 overflow-x-hidden">
      <div className="max-w-7xl mx-auto space-y-4 sm:space-y-6 w-full">

        {/* ── Header ── */}
        <div className="flex items-start sm:items-center justify-between gap-2">
          <div className="min-w-0">
            <h1 className="text-lg sm:text-2xl font-bold text-gray-800 flex items-center gap-2">
              <span className="text-teal-500">⚔️</span> 競品監測
            </h1>
            <p className="text-xs sm:text-sm text-gray-400 mt-0.5">
              {summary?.total_competitors || '...'} 商戶 · {summary?.total_tracked_products || '...'} 商品
            </p>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            {/* Export CSV */}
            <a
              href="/api/v1/competitors/comparison/export"
              download
              className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 text-xs border border-teal-200 text-teal-600 hover:bg-teal-50 rounded-lg transition-colors"
            >
              <Download className="w-3.5 h-3.5" /> 匯出 CSV
            </a>
            <Button
              variant="outline"
              size="sm"
              onClick={handleRefresh}
              className="border-teal-200 text-teal-600 hover:bg-teal-50 hover:text-teal-700 hover:border-teal-300"
            >
              <RefreshCw className="w-4 h-4 sm:mr-1.5" />
              <span className="hidden sm:inline">刷新</span>
            </Button>
          </div>
        </div>

        {/* ── Stats ── */}
        <DashboardStats summary={summary} isLoading={summaryLoading} />

        {/* ── View Toggle ── */}
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-2">
          <div className="flex items-center gap-1 p-1 rounded-lg bg-white border border-gray-200 shadow-sm">
            <button onClick={() => setView('products')} className={cn('flex-1 sm:flex-none flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-md text-sm transition-all', view === 'products' ? 'bg-teal-500 text-white shadow-sm' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50')}>
              <Package className="w-4 h-4" /> 商品視角
            </button>
            <button onClick={() => setView('merchants')} className={cn('flex-1 sm:flex-none flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-md text-sm transition-all', view === 'merchants' ? 'bg-teal-500 text-white shadow-sm' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50')}>
              <Building2 className="w-4 h-4" /> 商戶視角
            </button>
            <button onClick={() => setView('suggestions')} className={cn('flex-1 sm:flex-none flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-md text-sm transition-all', view === 'suggestions' ? 'bg-amber-500 text-white shadow-sm' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50')}>
              <Lightbulb className="w-4 h-4" /> 改價建議
            </button>
          </div>

          {view === 'products' && (
            <div className="flex items-center gap-1 p-1 rounded-lg bg-white border border-gray-200 shadow-sm">
              <button onClick={() => setScope('mapped')} className={cn('flex-1 sm:flex-none flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-md text-xs transition-all', scope === 'mapped' ? 'bg-amber-500 text-white shadow-sm' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50')}>
                <Target className="w-3.5 h-3.5" /> 自家競品
              </button>
              <button onClick={() => setScope('all')} className={cn('flex-1 sm:flex-none flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-md text-xs transition-all', scope === 'all' ? 'bg-amber-500 text-white shadow-sm' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50')}>
                <Globe className="w-3.5 h-3.5" /> 全部生鮮
              </button>
            </div>
          )}

          {/* Mobile export */}
          {view === 'products' && (
            <a href="/api/v1/competitors/comparison/export" download className="sm:hidden flex items-center justify-center gap-1.5 px-3 py-2 text-xs border border-teal-200 text-teal-600 hover:bg-teal-50 rounded-lg transition-colors">
              <Download className="w-3.5 h-3.5" /> 匯出 CSV
            </a>
          )}
        </div>

        {/* ── Filter Bar ── */}
        {showFilterBar && !isListLoading && listTotal > 0 && (
          <FilterBar
            search={search}
            onSearchChange={setSearch}
            categoryFilter={categoryFilter}
            onCategoryChange={setCategoryFilter}
            categories={categories}
            sortKey={sortKey}
            sortDir={sortDir}
            onSortChange={(k, d) => { setSortKey(k); setSortDir(d) }}
            resultCount={listFiltered}
            totalCount={listTotal}
            mode={view as 'products' | 'merchants'}
          />
        )}

        {/* ── Content ── */}
        <motion.div key={view} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.2 }}>

          {/* Products view */}
          {view === 'products' && (
            <div className="space-y-2 sm:space-y-3">
              {productsLoading ? (
                Array.from({ length: 5 }).map((_, i) => (
                  <div key={i} className="rounded-xl border border-gray-200 bg-white p-3 sm:p-4 animate-pulse shadow-sm">
                    <div className="flex items-center gap-3"><div className="h-5 bg-gray-100 rounded w-12" /><div className="h-5 bg-gray-100 rounded w-32 sm:w-48" /></div>
                  </div>
                ))
              ) : filteredProducts.length === 0 ? (
                <div className="text-center py-16 text-gray-400">
                  <Package className="w-10 h-10 mx-auto mb-3 opacity-30" />
                  <p className="text-sm">{search || categoryFilter ? '冇符合條件的商品' : '未有商品比較數據'}</p>
                </div>
              ) : (
                filteredProducts.map(item => (
                  <ProductComparisonCard
                    key={item.product.id}
                    data={item}
                    onShowHistory={(id, name) => setHistoryProduct({ id, name })}
                  />
                ))
              )}
            </div>
          )}

          {/* Merchants view */}
          {view === 'merchants' && (
            <div className="space-y-2 sm:space-y-3">
              {merchantsLoading ? (
                Array.from({ length: 5 }).map((_, i) => (
                  <div key={i} className="rounded-xl border border-gray-200 bg-white p-3 sm:p-4 animate-pulse shadow-sm">
                    <div className="flex items-center gap-3"><div className="h-5 bg-gray-100 rounded w-16" /><div className="h-5 bg-gray-100 rounded w-32" /></div>
                  </div>
                ))
              ) : filteredMerchants.length === 0 ? (
                <div className="text-center py-16 text-gray-400">
                  <Building2 className="w-10 h-10 mx-auto mb-3 opacity-30" />
                  <p className="text-sm">{search ? '冇符合條件的商戶' : '未有商戶數據'}</p>
                </div>
              ) : (
                filteredMerchants.map(item => (
                  <MerchantOverviewCard key={item.competitor.id} data={item} />
                ))
              )}
            </div>
          )}

          {/* Pricing suggestions view */}
          {view === 'suggestions' && <PricingSuggestionsPanel />}
        </motion.div>
      </div>

      {/* Price history modal */}
      {historyProduct && (
        <PriceHistoryModal
          productId={historyProduct.id}
          productName={historyProduct.name}
          onClose={() => setHistoryProduct(null)}
        />
      )}
    </div>
  )
}
