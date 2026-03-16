'use client'

import { useState, useMemo, useRef, useCallback, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { api, ProductComparison } from '@/lib/api'
import { useLocale } from '@/components/providers/locale-provider'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Package, Building2, RefreshCw, Target, Globe,
  Download, Lightbulb, ChevronDown, ChevronRight,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { DashboardStats } from '@/components/competitors/dashboard-stats'
import { ProductComparisonCard } from '@/components/competitors/product-comparison-card'
import { ProductDetailPanel } from '@/components/competitors/product-detail-panel'
import { MerchantOverviewCard } from '@/components/competitors/merchant-overview-card'
import { FilterBar, SortKey, SortDir } from '@/components/competitors/filter-bar'
import { PricingSuggestionsPanel } from '@/components/competitors/pricing-suggestions-panel'

type ViewMode = 'products' | 'merchants' | 'suggestions'
type ScopeMode = 'mapped' | 'all'

type ThreatLevel = 'danger' | 'warning' | 'cheapest' | 'normal'

function getThreatLevel(item: ProductComparison): ThreatLevel {
  const ourPrice = item.product.price
  const cheapestPrice = item.competitors[0]?.price
  if (item.our_price_rank === 1) return 'cheapest'
  if (ourPrice && cheapestPrice) {
    const diff = ((ourPrice - cheapestPrice) / ourPrice) * 100
    if (diff > 20) return 'danger'
    if (diff > 5) return 'warning'
  }
  return 'normal'
}

const THREAT_GROUPS_STYLE: { key: ThreatLevel; labelKey: string; color: string; badge: string }[] = [
  { key: 'danger',   labelKey: 'competitors.page.threat_danger',   color: 'border-red-200 bg-red-50/60',     badge: 'bg-red-100 text-red-700 border-red-200' },
  { key: 'warning',  labelKey: 'competitors.page.threat_warning',  color: 'border-amber-200 bg-amber-50/60', badge: 'bg-amber-100 text-amber-700 border-amber-200' },
  { key: 'normal',   labelKey: 'competitors.page.threat_normal',   color: 'border-gray-200 bg-gray-50/60',   badge: 'bg-gray-100 text-gray-600 border-gray-200' },
  { key: 'cheapest', labelKey: 'competitors.page.threat_cheapest', color: 'border-emerald-200 bg-emerald-50/60', badge: 'bg-emerald-100 text-emerald-700 border-emerald-200' },
]

export default function CompetitorsPage() {
  const { t } = useLocale()
  const [view, setView] = useState<ViewMode>('products')
  const [scope, setScope] = useState<ScopeMode>('mapped')

  // Filter/Sort state
  const [search, setSearch] = useState('')
  const [categoryFilter, setCategoryFilter] = useState('')
  const [sortKey, setSortKey] = useState<SortKey>('threat')
  const [sortDir, setSortDir] = useState<SortDir>('desc')

  // Split panel state
  const [selectedProduct, setSelectedProduct] = useState<ProductComparison | null>(null)
  const [collapsedGroups, setCollapsedGroups] = useState<Set<ThreatLevel>>(new Set())
  const [detailOffset, setDetailOffset] = useState(0)
  const listContainerRef = useRef<HTMLDivElement>(null)

  const handleSelectProduct = useCallback((item: ProductComparison) => {
    const isSame = selectedProduct?.product.id === item.product.id
    setSelectedProduct(isSame ? null : item)
    if (!isSame) {
      // Calculate offset of the clicked card relative to the product list container
      requestAnimationFrame(() => {
        if (!listContainerRef.current) return
        const card = listContainerRef.current.querySelector(
          `[data-product-id="${item.product.id}"]`
        ) as HTMLElement | null
        if (card) {
          const containerRect = listContainerRef.current.getBoundingClientRect()
          const cardRect = card.getBoundingClientRect()
          setDetailOffset(cardRect.top - containerRect.top)
        }
      })
    } else {
      setDetailOffset(0)
    }
  }, [selectedProduct])

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

  const toggleGroup = (key: ThreatLevel) => {
    setCollapsedGroups(prev => {
      const next = new Set(prev)
      if (next.has(key)) next.delete(key)
      else next.add(key)
      return next
    })
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
      items = items.filter(i => (i.product.name_en || i.product.name).toLowerCase().includes(q) || i.product.name.toLowerCase().includes(q))
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
    setSelectedProduct(null)
  }

  // Grouped products
  const groupedProducts = useMemo(() => {
    const groups: Record<ThreatLevel, ProductComparison[]> = {
      danger: [], warning: [], normal: [], cheapest: []
    }
    filteredProducts.forEach(item => {
      groups[getThreatLevel(item)].push(item)
    })
    return groups
  }, [filteredProducts])

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-teal-50/30 px-3 py-4 sm:p-6 overflow-x-hidden w-full">
      <div className="max-w-7xl mx-auto space-y-4 sm:space-y-6 w-full overflow-x-hidden">

        {/* ===== Header ===== */}
        <div className="flex items-start sm:items-center justify-between gap-2">
          <div className="min-w-0">
            <h1 className="text-lg sm:text-2xl font-bold text-gray-800 flex items-center gap-2">
              <span className="text-teal-500">⚔️</span> {t('competitors.title')}
            </h1>
            <p className="text-xs sm:text-sm text-gray-400 mt-0.5">
              {summary?.total_competitors || '...'} merchants · {summary?.total_tracked_products || '...'} products
            </p>
          </div>
          <div className="flex items-center gap-1.5 shrink-0">
            {/* Export button */}
            <a
              href="/api/v1/competitors/comparison/export"
              download
              className="flex items-center gap-1 px-2.5 py-1.5 text-xs rounded-lg border border-gray-200 text-gray-500 hover:bg-gray-50 hover:border-gray-300 transition-colors"
              title={t('competitors.page.export_csv')}
            >
              <Download className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">{t('competitors.page.export_csv')}</span>
            </a>
            <Button
              variant="outline"
              size="sm"
              onClick={handleRefresh}
              className="border-teal-200 text-teal-600 hover:bg-teal-50 hover:text-teal-700 hover:border-teal-300"
            >
              <RefreshCw className="w-4 h-4 sm:mr-1.5" />
              <span className="hidden sm:inline">Refresh</span>
            </Button>
          </div>
        </div>

        {/* ===== Stats Cards ===== */}
        <DashboardStats summary={summary} isLoading={summaryLoading} />

        {/* ===== View + Scope Toggles ===== */}
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-2 overflow-x-hidden">
          <div className="flex items-center gap-1 p-1 rounded-lg bg-white border border-gray-200 shadow-sm min-w-0">
            <button
              onClick={() => handleViewChange('products')}
              className={cn(
                'flex-1 sm:flex-none flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-md text-sm transition-all',
                view === 'products' ? 'bg-teal-500 text-white shadow-sm' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
              )}
            >
              <Package className="w-4 h-4" />
              {t('competitors.page.tab_products')}
            </button>
            <button
              onClick={() => handleViewChange('merchants')}
              className={cn(
                'flex-1 sm:flex-none flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-md text-sm transition-all',
                view === 'merchants' ? 'bg-teal-500 text-white shadow-sm' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
              )}
            >
              <Building2 className="w-4 h-4" />
              {t('competitors.page.tab_merchants')}
            </button>
            <button
              onClick={() => handleViewChange('suggestions')}
              className={cn(
                'flex-1 sm:flex-none flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-md text-sm transition-all',
                view === 'suggestions' ? 'bg-amber-500 text-white shadow-sm' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
              )}
            >
              <Lightbulb className="w-4 h-4" />
              {t('competitors.page.tab_suggestions')}
            </button>
          </div>

          {view === 'products' && (
            <div className="flex items-center gap-1 p-1 rounded-lg bg-white border border-gray-200 shadow-sm shrink-0">
              <button
                onClick={() => setScope('mapped')}
                className={cn(
                  'flex items-center justify-center gap-1 px-2.5 py-1.5 rounded-md text-xs transition-all whitespace-nowrap',
                  scope === 'mapped' ? 'bg-amber-500 text-white shadow-sm' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
                )}
              >
                <Target className="w-3.5 h-3.5 shrink-0" />
                {t('competitors.page.scope_own')}
              </button>
              <button
                onClick={() => setScope('all')}
                className={cn(
                  'flex items-center justify-center gap-1 px-2.5 py-1.5 rounded-md text-xs transition-all whitespace-nowrap',
                  scope === 'all' ? 'bg-amber-500 text-white shadow-sm' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
                )}
              >
                <Globe className="w-3.5 h-3.5 shrink-0" />
                {t('competitors.page.scope_all')}
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
          {/* Products — Split Panel */}
          {view === 'products' && (
            <div className="flex gap-4 items-start">
              {/* ── Left: Product List ── */}
              <div
                ref={listContainerRef}
                className={cn(
                'min-w-0 flex-shrink-0 space-y-3',
                selectedProduct ? 'w-full lg:w-[40%]' : 'w-full'
              )}>
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
                    <p className="text-sm">{search || categoryFilter ? t('competitors.page.empty_filtered') : t('competitors.page.empty_no_data')}</p>
                  </div>
                ) : (
                  THREAT_GROUPS_STYLE.map(group => {
                    const items = groupedProducts[group.key]
                    if (items.length === 0) return null
                    const isCollapsed = collapsedGroups.has(group.key)
                    return (
                      <div key={group.key} className={cn('rounded-xl border overflow-hidden', group.color)}>
                        {/* Group Header */}
                        <button
                          onClick={() => toggleGroup(group.key)}
                          className="w-full flex items-center gap-2 px-3 py-2 hover:bg-black/5 transition-colors"
                        >
                          {isCollapsed
                            ? <ChevronRight className="w-3.5 h-3.5 text-gray-400 shrink-0" />
                            : <ChevronDown className="w-3.5 h-3.5 text-gray-400 shrink-0" />
                          }
                          <span className={cn(
                            'text-[11px] font-semibold px-2 py-0.5 rounded-full border',
                            group.badge
                          )}>
                            {group.key === 'cheapest' ? `${t(group.labelKey)} 🏆` : t(group.labelKey)}
                          </span>
                          <span className="text-[10px] text-gray-400 ml-auto">{t('competitors.page.items_count', { n: items.length })}</span>
                        </button>

                        {/* Group Items */}
                        <AnimatePresence initial={false}>
                          {!isCollapsed && (
                            <motion.div
                              initial={{ height: 0, opacity: 0 }}
                              animate={{ height: 'auto', opacity: 1 }}
                              exit={{ height: 0, opacity: 0 }}
                              transition={{ duration: 0.18 }}
                              className="overflow-hidden"
                            >
                              <div className="px-2 pb-2 space-y-1.5">
                                {items.map(item => (
                                  <div key={item.product.id} data-product-id={item.product.id}>
                                    <ProductComparisonCard
                                      data={item}
                                      selected={selectedProduct?.product.id === item.product.id}
                                      onClick={() => handleSelectProduct(item)}
                                    />
                                  </div>
                                ))}
                              </div>
                            </motion.div>
                          )}
                        </AnimatePresence>
                      </div>
                    )
                  })
                )}
              </div>

              {/* ── Right: Detail Panel (desktop sticky, mobile hidden) ── */}
              <AnimatePresence>
                {selectedProduct && (
                  <motion.div
                    initial={{ opacity: 0, x: 16 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 16 }}
                    transition={{ duration: 0.2 }}
                    className="hidden lg:block lg:w-[60%] sticky top-4"
                    style={{ maxHeight: 'calc(100vh - 2rem)', marginTop: `${detailOffset}px` }}
                  >
                    <ProductDetailPanel
                      data={selectedProduct}
                      onClose={() => setSelectedProduct(null)}
                    />
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          )}

          {/* Mobile Detail Sheet */}
          <AnimatePresence>
            {view === 'products' && selectedProduct && (
              <motion.div
                initial={{ y: '100%' }}
                animate={{ y: 0 }}
                exit={{ y: '100%' }}
                transition={{ type: 'spring', damping: 30, stiffness: 300 }}
                className="lg:hidden fixed inset-x-0 bottom-0 z-40 bg-white rounded-t-2xl shadow-2xl border-t border-gray-200"
                style={{ maxHeight: '75vh' }}
              >
                <div className="w-10 h-1 bg-gray-200 rounded-full mx-auto mt-3 mb-1" />
                <div style={{ height: 'calc(75vh - 20px)', overflow: 'hidden' }}>
                  <ProductDetailPanel
                    data={selectedProduct}
                    onClose={() => setSelectedProduct(null)}
                  />
                </div>
              </motion.div>
            )}
          </AnimatePresence>

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
                  <p className="text-sm">{search ? t('competitors.page.empty_merchants_filtered') : t('competitors.page.empty_merchants_no_data')}</p>
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

      {/* Mobile overlay backdrop */}
      {view === 'products' && selectedProduct && (
        <div
          className="lg:hidden fixed inset-0 z-30 bg-black/20"
          onClick={() => setSelectedProduct(null)}
        />
      )}
    </div>
  )
}
