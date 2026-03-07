'use client'

import { useState, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'
import { motion } from 'framer-motion'
import {
  Package, Building2, RefreshCw, Target, Globe,
  Download, Lightbulb,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { DashboardStats } from '@/components/competitors/dashboard-stats'
import { ProductComparisonCard } from '@/components/competitors/product-comparison-card'
import { MerchantOverviewCard } from '@/components/competitors/merchant-overview-card'
import { FilterBar, SortKey, SortDir } from '@/components/competitors/filter-bar'
import { PricingSuggestionsPanel } from '@/components/competitors/pricing-suggestions-panel'
import { PriceHistoryModal } from '@/components/competitors/price-history-modal'

type ViewMode = 'products' | 'merchants' | 'suggestions'
type ScopeMode = 'mapped' | 'all'

export default function CompetitorsPage() {
  const [view, setView] = useState<ViewMode>('products')
  const [scope, setScope] = useState<ScopeMode>('mapped')

  // Filter/Sort state
  const [search, setSearch] = useState('')
  const [categoryFilter, setCategoryFilter] = useState('')
  const [sortKey, setSortKey] = useState<SortKey>('threat')
  const [sortDir, setSortDir] = useState<SortDir>('desc')

  // Price history modal
  const [historyModal, setHistoryModal] = useState<{ id: string; name: string } | null>(null)

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

  // ─── Derived: unique categories
  const categories = useMemo(() => {
    if (!products?.items) return []
    const cats = new Set(products.items.map(i => i.product.category_tag).filter(Boolean) as string[])
    return Array.from(cats).sort()
  }, [products])

  // ─── Filtered + Sorted products
  const filteredProducts = useMemo(() => {
    let items = products?.items ?? []

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
      let aVal = 0, bVal = 0
      if (sortKey === 'threat' || sortKey === 'price_diff') {
        const aPrice = a.product.price
        const bPrice = b.product.price
        const aCheapest = a.competitors[0]?.price
        const bCheapest = b.competitors[0]?.price
        aVal = aPrice && aCheapest ? (aPrice - aCheapest) / aPrice * 100 : 0
        bVal = bPrice && bCheapest ? (bPrice - bCheapest) / bPrice * 100 : 0
      } else if (sortKey === 'competitors') {
        aVal = a.total_competitors
        bVal = b.total_competitors
      } else if (sortKey === 'name') {
        return sortDir === 'asc'
          ? a.product.name.localeCompare(b.product.name)
          : b.product.name.localeCompare(a.product.name)
      } else if (sortKey === 'rank') {
        aVal = a.our_price_rank
        bVal = b.our_price_rank
      }
      return sortDir === 'asc' ? aVal - bVal : bVal - aVal
    })

    return items
  }, [products, search, categoryFilter, sortKey, sortDir])

  // ─── Filtered + Sorted merchants
  const filteredMerchants = useMemo(() => {
    let items = merchants?.items ?? []

    if (search.trim()) {
      const q = search.toLowerCase()
      items = items.filter(i => i.competitor.name.toLowerCase().includes(q))
    }

    items = [...items].sort((a, b) => {
      if (sortKey === 'threat' || sortKey === 'price_diff') {
        const aVal = Math.abs(a.price_comparison.avg_price_diff_pct)
        const bVal = Math.abs(b.price_comparison.avg_price_diff_pct)
        return sortDir === 'desc' ? bVal - aVal : aVal - bVal
      } else if (sortKey === 'competitors') {
        return sortDir === 'desc'
          ? b.competitor.total_products - a.competitor.total_products
          : a.competitor.total_products - b.competitor.total_products
      } else if (sortKey === 'name') {
        return sortDir === 'asc'
          ? a.competitor.name.localeCompare(b.competitor.name)
          : b.competitor.name.localeCompare(a.competitor.name)
      }
      return 0
    })

    return items
  }, [merchants, search, sortKey, sortDir])

  const handleSortChange = (key: SortKey, dir: SortDir) => {
    setSortKey(key)
    setSortDir(dir)
  }

  // Reset filters when switching view
  const handleViewChange = (newView: ViewMode) => {
    setView(newView)
    setSearch('')
    setCategoryFilter('')
    setSortKey('threat')
    setSortDir('desc')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-teal-50/30 px-3 py-4 sm:p-6 overflow-x-hidden">
      <div className="max-w-7xl mx-auto space-y-4 sm:space-y-6 w-full">

        {/* ===== Header ===== */}
        <div className="flex items-start sm:items-center justify-between gap-2">
          <div className="min-w-0">
            <h1 className="text-lg sm:text-2xl font-bold text-gray-800 flex items-center gap-2">
              <span className="text-teal-500">⚔️</span> 競品監測
            </h1>
            <p className="text-xs sm:text-sm text-gray-400 mt-0.5">
              {summary?.total_competitors || '...'} 商戶 · {summary?.total_tracked_products || '...'} 商品
            </p>
          </div>
          <div className="flex items-center gap-1.5 shrink-0">
            {/* Export button */}
            <a
              href="/api/v1/competitors/comparison/export"
              download
              className="flex items-center gap-1 px-2.5 py-1.5 text-xs rounded-lg border border-gray-200 text-gray-500 hover:bg-gray-50 hover:border-gray-300 transition-colors"
              title="匯出 CSV"
            >
              <Download className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">匯出</span>
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

        {/* ===== Stats Cards ===== */}
        <DashboardStats summary={summary} isLoading={summaryLoading} />

        {/* ===== View + Scope Toggles ===== */}
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-2">
          <div className="flex items-center gap-1 p-1 rounded-lg bg-white border border-gray-200 shadow-sm">
            <button
              onClick={() => handleViewChange('products')}
              className={cn(
                'flex-1 sm:flex-none flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-md text-sm transition-all',
                view === 'products' ? 'bg-teal-500 text-white shadow-sm' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
              )}
            >
              <Package className="w-4 h-4" />
              商品
            </button>
            <button
              onClick={() => handleViewChange('merchants')}
              className={cn(
                'flex-1 sm:flex-none flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-md text-sm transition-all',
                view === 'merchants' ? 'bg-teal-500 text-white shadow-sm' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
              )}
            >
              <Building2 className="w-4 h-4" />
              商戶
            </button>
            <button
              onClick={() => handleViewChange('suggestions')}
              className={cn(
                'flex-1 sm:flex-none flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-md text-sm transition-all',
                view === 'suggestions' ? 'bg-amber-500 text-white shadow-sm' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
              )}
            >
              <Lightbulb className="w-4 h-4" />
              建議
            </button>
          </div>

          {view === 'products' && (
            <div className="flex items-center gap-1 p-1 rounded-lg bg-white border border-gray-200 shadow-sm">
              <button
                onClick={() => setScope('mapped')}
                className={cn(
                  'flex-1 sm:flex-none flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-md text-xs transition-all',
                  scope === 'mapped' ? 'bg-amber-500 text-white shadow-sm' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
                )}
              >
                <Target className="w-3.5 h-3.5" />
                自家競品
              </button>
              <button
                onClick={() => setScope('all')}
                className={cn(
                  'flex-1 sm:flex-none flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-md text-xs transition-all',
                  scope === 'all' ? 'bg-amber-500 text-white shadow-sm' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
                )}
              >
                <Globe className="w-3.5 h-3.5" />
                全部生鮮
              </button>
            </div>
          )}
        </div>

        {/* ===== Filter Bar (products + merchants only) ===== */}
        {(view === 'products' || view === 'merchants') && (
          <FilterBar
            search={search}
            onSearchChange={setSearch}
            categoryFilter={categoryFilter}
            onCategoryChange={setCategoryFilter}
            categories={categories}
            sortKey={sortKey}
            sortDir={sortDir}
            onSortChange={handleSortChange}
            resultCount={view === 'products' ? filteredProducts.length : filteredMerchants.length}
            totalCount={view === 'products' ? (products?.items.length ?? 0) : (merchants?.items.length ?? 0)}
            mode={view}
          />
        )}

        {/* ===== Content ===== */}
        <motion.div
          key={view}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.2 }}
        >
          {/* Products */}
          {view === 'products' && (
            <div className="space-y-2 sm:space-y-3">
              {productsLoading ? (
                Array.from({ length: 5 }).map((_, i) => (
                  <div key={i} className="rounded-xl border border-gray-200 bg-white p-3 sm:p-4 animate-pulse shadow-sm">
                    <div className="flex items-center gap-3">
                      <div className="h-5 bg-gray-100 rounded w-12" />
                      <div className="h-5 bg-gray-100 rounded w-32 sm:w-48" />
                      <div className="h-5 bg-gray-100 rounded w-16" />
                    </div>
                  </div>
                ))
              ) : filteredProducts.length === 0 ? (
                <div className="text-center py-16 sm:py-20 text-gray-400">
                  <Package className="w-10 h-10 sm:w-12 sm:h-12 mx-auto mb-3 opacity-30" />
                  <p className="text-sm">{search || categoryFilter ? '冇符合條件嘅商品' : '未有商品比較數據'}</p>
                </div>
              ) : (
                filteredProducts.map((item) => (
                  <ProductComparisonCard
                    key={item.product.id}
                    data={item}
                    onShowHistory={(id, name) => setHistoryModal({ id, name })}
                  />
                ))
              )}
            </div>
          )}

          {/* Merchants */}
          {view === 'merchants' && (
            <div className="space-y-2 sm:space-y-3">
              {merchantsLoading ? (
                Array.from({ length: 5 }).map((_, i) => (
                  <div key={i} className="rounded-xl border border-gray-200 bg-white p-3 sm:p-4 animate-pulse shadow-sm">
                    <div className="flex items-center gap-3">
                      <div className="h-5 bg-gray-100 rounded w-16" />
                      <div className="h-5 bg-gray-100 rounded w-32 sm:w-40" />
                      <div className="h-5 bg-gray-100 rounded w-20 sm:w-24" />
                    </div>
                  </div>
                ))
              ) : filteredMerchants.length === 0 ? (
                <div className="text-center py-16 sm:py-20 text-gray-400">
                  <Building2 className="w-10 h-10 sm:w-12 sm:h-12 mx-auto mb-3 opacity-30" />
                  <p className="text-sm">{search ? '冇符合條件嘅商戶' : '未有商戶數據'}</p>
                </div>
              ) : (
                filteredMerchants.map((item) => (
                  <MerchantOverviewCard key={item.competitor.id} data={item} />
                ))
              )}
            </div>
          )}

          {/* Pricing Suggestions */}
          {view === 'suggestions' && <PricingSuggestionsPanel />}
        </motion.div>
      </div>

      {/* Price History Modal */}
      {historyModal && (
        <PriceHistoryModal
          productId={historyModal.id}
          productName={historyModal.name}
          onClose={() => setHistoryModal(null)}
        />
      )}
    </div>
  )
}
