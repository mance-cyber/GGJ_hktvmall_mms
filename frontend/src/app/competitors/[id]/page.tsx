'use client'

import { useState, useMemo, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api, CompetitorProduct, CompetitorProductCreate, CompetitorProductUpdate } from '@/lib/api'
import Link from 'next/link'
import { useParams } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import {
  ArrowLeft,
  RefreshCw,
  AlertCircle,
  Plus,
  Search,
  ExternalLink,
  TrendingUp,
  TrendingDown,
  Minus,
  X,
  Check,
  ChevronLeft,
  ChevronRight,
  Package,
  LineChart,
  History,
  ShoppingCart,
  Zap,
  Clock,
  Filter,
  CheckSquare,
  Square,
  Trash2,
  Pencil,
  MoreHorizontal,
  SortAsc,
  SortDesc,
  Upload,
  FileSpreadsheet
} from 'lucide-react'
import { Input } from '@/components/ui/input'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from '@/components/ui/dropdown-menu'
import { Label } from '@/components/ui/label'
import { cn } from '@/lib/utils'
import { BulkImportDialog, ImportRow } from '@/components/bulk-import-dialog'

// =============================================
// Future Tech Design System Component Imports
// =============================================
import {
  PageTransition,
  HoloCard,
  HoloPanelHeader,
  HoloButton,
  HoloBadge,
  DataMetric,
  PulseStatus,
  HoloSkeleton,
  StaggerContainer,
} from '@/components/ui/future-tech'

// =============================================
// Type definitions
// =============================================

type SortField = 'name' | 'price' | 'price_change' | 'last_scraped'
type SortOrder = 'asc' | 'desc'

// =============================================
// Main page component
// =============================================

export default function CompetitorDetailPage() {
  const params = useParams()
  const competitorId = params.id as string
  const queryClient = useQueryClient()

  // Pagination and search
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [searchInput, setSearchInput] = useState('')
  const pageSize = 20

  // UI State
  const [showAddForm, setShowAddForm] = useState(false)
  const [showBulkImport, setShowBulkImport] = useState(false)
  const [isImporting, setIsImporting] = useState(false)
  const [selectedProductId, setSelectedProductId] = useState<string | null>(null)
  const [selectedProducts, setSelectedProducts] = useState<Set<string>>(new Set())
  const [sortField, setSortField] = useState<SortField>('name')
  const [sortOrder, setSortOrder] = useState<SortOrder>('asc')
  const [stockFilter, setStockFilter] = useState<string | undefined>(undefined)
  const [editingProduct, setEditingProduct] = useState<CompetitorProduct | null>(null)

  // ========== Data queries ==========

  const { data: competitor, isLoading: competitorLoading } = useQuery({
    queryKey: ['competitor', competitorId],
    queryFn: () => api.getCompetitor(competitorId),
  })

  const { data: products, isLoading: productsLoading, error, refetch } = useQuery({
    queryKey: ['competitor-products', competitorId, page, search],
    queryFn: () => api.getCompetitorProducts(competitorId, page, pageSize, search || undefined),
  })

  const { data: priceHistory, isLoading: historyLoading } = useQuery({
    queryKey: ['price-history', selectedProductId],
    queryFn: () => api.getCompetitorProductHistory(selectedProductId!, 30),
    enabled: !!selectedProductId,
  })

  // ========== Sort and filter ==========

  const sortedProducts = useMemo(() => {
    if (!products?.data) return []

    let filtered = [...products.data]

    // Stock filter
    if (stockFilter) {
      filtered = filtered.filter(p => p.stock_status === stockFilter)
    }

    // Sort
    filtered.sort((a, b) => {
      let comparison = 0
      switch (sortField) {
        case 'name':
          comparison = a.name.localeCompare(b.name)
          break
        case 'price':
          comparison = (a.current_price || 0) - (b.current_price || 0)
          break
        case 'price_change':
          comparison = (a.price_change || 0) - (b.price_change || 0)
          break
        case 'last_scraped':
          comparison = new Date(a.last_scraped_at || 0).getTime() - new Date(b.last_scraped_at || 0).getTime()
          break
      }
      return sortOrder === 'asc' ? comparison : -comparison
    })

    return filtered
  }, [products?.data, sortField, sortOrder, stockFilter])

  // ========== Mutations ==========

  const addProductMutation = useMutation({
    mutationFn: (data: CompetitorProductCreate) => api.addCompetitorProduct(competitorId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['competitor-products', competitorId] })
      queryClient.invalidateQueries({ queryKey: ['competitor', competitorId] })
      setShowAddForm(false)
    },
  })

  const updateProductMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: CompetitorProductUpdate }) =>
      api.updateCompetitorProduct(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['competitor-products', competitorId] })
      setEditingProduct(null)
    },
  })

  const deleteProductMutation = useMutation({
    mutationFn: (id: string) => api.deleteCompetitorProduct(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['competitor-products', competitorId] })
      queryClient.invalidateQueries({ queryKey: ['competitor', competitorId] })
    },
  })

  const scrapeMutation = useMutation({
    mutationFn: () => api.triggerCompetitorScrape(competitorId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['competitor-products', competitorId] })
      queryClient.invalidateQueries({ queryKey: ['competitor', competitorId] })
    },
  })

  // ========== Event handlers ==========

  // Bulk import handler
  const handleBulkImport = async (rows: ImportRow[]) => {
    setIsImporting(true)
    try {
      for (const row of rows) {
        await api.addCompetitorProduct(competitorId, {
          url: row.url,
          name: row.name,
          category: row.category,
        })
      }
      queryClient.invalidateQueries({ queryKey: ['competitor-products', competitorId] })
      queryClient.invalidateQueries({ queryKey: ['competitor', competitorId] })
      setShowBulkImport(false)
    } finally {
      setIsImporting(false)
    }
  }

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    setSearch(searchInput)
    setPage(1)
  }

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')
    } else {
      setSortField(field)
      setSortOrder('asc')
    }
  }

  const toggleProductSelection = (productId: string) => {
    const newSet = new Set(selectedProducts)
    if (newSet.has(productId)) {
      newSet.delete(productId)
    } else {
      newSet.add(productId)
    }
    setSelectedProducts(newSet)
  }

  const toggleSelectAll = () => {
    if (selectedProducts.size === sortedProducts.length) {
      setSelectedProducts(new Set())
    } else {
      setSelectedProducts(new Set(sortedProducts.map(p => p.id)))
    }
  }

  // ========== Calculate ==========

  const totalPages = products ? Math.ceil(products.total / pageSize) : 0
  const isLoading = competitorLoading || productsLoading

  // Statistics
  const stats = useMemo(() => {
    if (!products?.data) return null
    const inStock = products.data.filter(p => p.stock_status === 'in_stock').length
    const outOfStock = products.data.filter(p => p.stock_status === 'out_of_stock').length
    const priceUp = products.data.filter(p => (p.price_change || 0) > 0).length
    const priceDown = products.data.filter(p => (p.price_change || 0) < 0).length
    return { inStock, outOfStock, priceUp, priceDown }
  }, [products?.data])

  // ========== Rendering ==========

  // Loading State - using HoloSkeleton
  if (isLoading) {
    return (
      <PageTransition>
        <div className="space-y-6 max-w-7xl mx-auto">
          {/* Top skeleton */}
          <div className="space-y-4">
            <HoloSkeleton width={120} height={20} />
            <HoloSkeleton width="60%" height={36} />
            <div className="flex gap-2">
              <HoloSkeleton width={80} height={24} />
              <HoloSkeleton width={120} height={24} />
            </div>
          </div>

          {/* Statistics card skeleton */}
          <div className="grid grid-cols-4 gap-4">
            {[1, 2, 3, 4].map((i) => (
              <HoloSkeleton key={i} height={100} className="rounded-xl" />
            ))}
          </div>

          {/* Main content skeleton */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 space-y-4">
              <HoloSkeleton height={44} className="rounded-xl" />
              <HoloSkeleton height={400} className="rounded-xl" />
            </div>
            <div className="lg:col-span-1">
              <HoloSkeleton height={500} className="rounded-xl" />
            </div>
          </div>
        </div>
      </PageTransition>
    )
  }

  if (error) {
    return (
      <PageTransition>
        <HoloCard glowColor="purple" className="max-w-7xl mx-auto border-red-200/50 bg-red-50/50 p-6">
          <div className="flex items-center text-red-600">
            <AlertCircle className="w-5 h-5 mr-3" />
            <span className="font-medium">Unable to load product list, please try again later.</span>
          </div>
        </HoloCard>
      </PageTransition>
    )
  }

  return (
    <PageTransition className="space-y-6 max-w-7xl mx-auto">
      {/* ========== Top navigation and title ========== */}
      <div className="space-y-4">
        <Link
          href="/competitors"
          className="inline-flex items-center text-sm font-medium text-muted-foreground hover:text-cyan-600 transition-colors group"
        >
          <div className="p-1.5 rounded-lg bg-slate-100 group-hover:bg-cyan-50 mr-2 transition-all group-hover:shadow-md group-hover:shadow-cyan-200/50">
            <ArrowLeft className="w-4 h-4 group-hover:text-cyan-600 transition-colors" />
          </div>
          Back to competitors list
        </Link>

        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-slate-800 to-slate-600 bg-clip-text text-transparent">
              {competitor?.name}
            </h1>
            <div className="flex items-center space-x-3 mt-2">
              <HoloBadge variant="info">
                {competitor?.platform}
              </HoloBadge>
              <span className="text-slate-300">|</span>
              <span className="text-muted-foreground flex items-center">
                <Package className="w-4 h-4 mr-1 text-cyan-500" />
                {products?.total || 0} monitored products
              </span>
              {competitor?.last_scraped_at && (
                <>
                  <span className="text-slate-300">|</span>
                  <span className="text-muted-foreground flex items-center text-sm">
                    <Clock className="w-3.5 h-3.5 mr-1 text-cyan-500" />
                    Last updated: {new Date(competitor.last_scraped_at).toLocaleString('en-HK')}
                  </span>
                </>
              )}
            </div>
          </div>

          <div className="flex space-x-3">
            <HoloButton
              variant="secondary"
              onClick={() => scrapeMutation.mutate()}
              loading={scrapeMutation.isPending}
              icon={scrapeMutation.isPending ? undefined : <Zap className="w-4 h-4 text-amber-500" />}
            >
              Scrape Now
            </HoloButton>
            <HoloButton
              variant="ghost"
              onClick={() => refetch()}
              icon={<RefreshCw className="w-4 h-4" />}
            >
              Refresh
            </HoloButton>
            <HoloButton
              variant="secondary"
              onClick={() => setShowBulkImport(true)}
              icon={<FileSpreadsheet className="w-4 h-4 text-emerald-500" />}
              className="border-emerald-200 hover:border-emerald-300"
            >
              Batch Import
            </HoloButton>
            <HoloButton
              variant="primary"
              onClick={() => setShowAddForm(true)}
              icon={<Plus className="w-4 h-4" />}
            >
              Add Product
            </HoloButton>
          </div>
        </div>
      </div>

      {/* ========== Statistics cards - using DataMetric ========== */}
      {stats && (
        <StaggerContainer className="grid grid-cols-4 gap-4" staggerDelay={0.08}>
          <DataMetric
            label="In Stock Products"
            value={stats.inStock}
            icon={<Package className="w-5 h-5 text-emerald-500" />}
            color="green"
          />
          <DataMetric
            label="Out of Stock Products"
            value={stats.outOfStock}
            icon={<Package className="w-5 h-5 text-amber-500" />}
            color="orange"
          />
          <DataMetric
            label="Price increase"
            value={stats.priceUp}
            icon={<TrendingUp className="w-5 h-5 text-red-500" />}
            color="purple"
          />
          <DataMetric
            label="Price decrease"
            value={stats.priceDown}
            icon={<TrendingDown className="w-5 h-5 text-emerald-500" />}
            color="cyan"
          />
        </StaggerContainer>
      )}

      {/* ========== Main content area ========== */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Product list */}
        <div className="lg:col-span-2 space-y-4">
          {/* Search and filter bar */}
          <div className="flex items-center space-x-3">
            <form onSubmit={handleSearch} className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                type="text"
                placeholder="Search product name, category..."
                value={searchInput}
                onChange={(e) => setSearchInput(e.target.value)}
                className="pl-10 bg-white/70 backdrop-blur-sm border-slate-200/80 focus:border-cyan-300 focus:ring-cyan-200/50 transition-all"
              />
            </form>

            {/* Stock filter */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <div>
                  <HoloButton variant="secondary" size="sm" icon={<Filter className="w-4 h-4" />}>
                    {stockFilter === 'in_stock' ? 'In stock' :
                     stockFilter === 'out_of_stock' ? 'Out of stock' : 'All'}
                  </HoloButton>
                </div>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="bg-white/95 backdrop-blur-xl border-slate-200/80">
                <DropdownMenuItem onClick={() => setStockFilter(undefined)}>
                  All
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setStockFilter('in_stock')}>
                  In stock
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setStockFilter('out_of_stock')}>
                  Out of stock
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>

            {/* Sort */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <div>
                  <HoloButton
                    variant="secondary"
                    size="sm"
                    icon={sortOrder === 'asc' ? <SortAsc className="w-4 h-4" /> : <SortDesc className="w-4 h-4" />}
                  >
                    Sort
                  </HoloButton>
                </div>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="bg-white/95 backdrop-blur-xl border-slate-200/80">
                <DropdownMenuItem onClick={() => handleSort('name')}>
                  Name {sortField === 'name' && (sortOrder === 'asc' ? '↑' : '↓')}
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => handleSort('price')}>
                  Price {sortField === 'price' && (sortOrder === 'asc' ? '↑' : '↓')}
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => handleSort('price_change')}>
                  Price change {sortField === 'price_change' && (sortOrder === 'asc' ? '↑' : '↓')}
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => handleSort('last_scraped')}>
                  Update time {sortField === 'last_scraped' && (sortOrder === 'asc' ? '↑' : '↓')}
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>

          {/* Batch operations bar */}
          <AnimatePresence>
            {selectedProducts.size > 0 && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="flex items-center justify-between bg-gradient-to-r from-cyan-50 to-blue-50 rounded-xl px-4 py-3 border border-cyan-200/60 shadow-sm"
              >
                <span className="text-sm font-medium text-cyan-700">
                  Selected {selectedProducts.size} products
                </span>
                <div className="flex items-center space-x-2">
                  <HoloButton size="sm" variant="ghost" onClick={() => setSelectedProducts(new Set())}>
                    Deselect
                  </HoloButton>
                  <HoloButton
                    size="sm"
                    variant="secondary"
                    className="border-red-200 text-red-600 hover:bg-red-50"
                    icon={<Trash2 className="w-3.5 h-3.5" />}
                  >
                    Delete
                  </HoloButton>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Product list - using HoloCard */}
          <HoloCard glowColor="cyan" className="overflow-hidden">
            {/* List header */}
            <div className="px-4 py-3 bg-gradient-to-r from-slate-50/80 to-white/80 border-b border-slate-100/80 flex items-center">
              <button
                onClick={toggleSelectAll}
                className="p-1.5 hover:bg-cyan-100 rounded-lg mr-3 transition-colors"
              >
                {selectedProducts.size === sortedProducts.length && sortedProducts.length > 0 ? (
                  <CheckSquare className="w-4 h-4 text-cyan-600" />
                ) : (
                  <Square className="w-4 h-4 text-slate-400" />
                )}
              </button>
              <span className="text-xs font-medium text-slate-500">
                {sortedProducts.length} products
              </span>
            </div>

            <div className="divide-y divide-slate-100/80 max-h-[600px] overflow-y-auto">
              <AnimatePresence>
                {sortedProducts.map((product, index) => (
                  <motion.div
                    key={product.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.03, duration: 0.3 }}
                  >
                    <ProductRow
                      product={product}
                      isSelected={selectedProductId === product.id}
                      isChecked={selectedProducts.has(product.id)}
                      onSelect={() => setSelectedProductId(product.id)}
                      onToggleCheck={() => toggleProductSelection(product.id)}
                      onEdit={() => setEditingProduct(product)}
                      onDelete={() => deleteProductMutation.mutate(product.id)}
                    />
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>

            {/* Empty state */}
            {sortedProducts.length === 0 && (
              <div className="px-6 py-16 text-center">
                <div className="w-16 h-16 bg-gradient-to-br from-cyan-50 to-blue-50 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg shadow-cyan-100/50">
                  <Package className="w-8 h-8 text-cyan-400" />
                </div>
                <h3 className="text-lg font-medium text-gray-900">No monitored products yet</h3>
                <p className="text-muted-foreground mt-1">Click "Add Product" in the top right to start monitoring</p>
              </div>
            )}
          </HoloCard>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between px-2">
              <div className="text-sm text-muted-foreground">
                Page {page} / {totalPages}
              </div>
              <div className="flex items-center space-x-2">
                <HoloButton
                  variant="secondary"
                  size="sm"
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page <= 1}
                  icon={<ChevronLeft className="w-4 h-4" />}
                >
                  Previous
                </HoloButton>
                <HoloButton
                  variant="secondary"
                  size="sm"
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  disabled={page >= totalPages}
                  icon={<ChevronRight className="w-4 h-4" />}
                >
                  Next
                </HoloButton>
              </div>
            </div>
          )}
        </div>

        {/* ========== Right: Price history sidebar - using HoloCard ========== */}
        <div className="lg:col-span-1">
          <HoloCard glowColor="blue" className="sticky top-6 overflow-hidden">
            <HoloPanelHeader
              title="Price Trend Analysis"
              icon={<LineChart className="w-5 h-5" />}
            />

            <div className="p-6">
              {!selectedProductId ? (
                <div className="text-center py-12">
                  <div className="w-16 h-16 bg-gradient-to-br from-cyan-50 to-blue-50 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg shadow-cyan-100/50 animate-pulse">
                    <LineChart className="w-8 h-8 text-cyan-400" />
                  </div>
                  <h3 className="text-base font-medium text-gray-900">No product selected</h3>
                  <p className="text-sm text-muted-foreground mt-1">
                    Click a product in the left list<br/>View detailed price history and analysis
                  </p>
                </div>
              ) : historyLoading ? (
                <div className="flex flex-col items-center justify-center py-12 space-y-4">
                  <div className="relative">
                    <div className="absolute inset-0 bg-cyan-500/20 blur-xl rounded-full animate-pulse" />
                    <RefreshCw className="relative w-8 h-8 animate-spin text-cyan-500" />
                  </div>
                  <span className="text-sm text-muted-foreground">Analyzing data...</span>
                </div>
              ) : priceHistory ? (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.4 }}
                  className="space-y-6"
                >
                  {/* Product info */}
                  <div>
                    <h3 className="text-sm font-semibold text-gray-900 leading-relaxed mb-2">
                      {priceHistory.product.name}
                    </h3>
                    <div className="flex items-center space-x-2">
                      {priceHistory.product.url && (
                        <a
                          href={priceHistory.product.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center text-xs text-cyan-600 hover:text-cyan-700 bg-cyan-50 px-2.5 py-1 rounded-lg transition-colors hover:bg-cyan-100"
                        >
                          <ExternalLink className="w-3 h-3 mr-1" />
                          Visit product page
                        </a>
                      )}
                      <HoloBadge
                        variant={priceHistory.product.stock_status === 'in_stock' ? 'success' : 'error'}
                        size="sm"
                      >
                        {priceHistory.product.stock_status === 'in_stock' ? 'In stock' : 'Out of stock'}
                      </HoloBadge>
                    </div>
                  </div>

                  {/* Price cards */}
                  <div className="grid grid-cols-2 gap-3">
                    <div className="bg-gradient-to-br from-slate-50 to-white p-3 rounded-xl border border-slate-100 shadow-sm">
                      <div className="text-xs text-muted-foreground mb-1">Current Price</div>
                      <div className="text-xl font-bold text-gray-900">
                        ${priceHistory.product.current_price ? Number(priceHistory.product.current_price).toFixed(2) : '-'}
                      </div>
                    </div>
                    <div className="bg-gradient-to-br from-slate-50 to-white p-3 rounded-xl border border-slate-100 shadow-sm">
                      <div className="text-xs text-muted-foreground mb-1">Price change</div>
                      <div className={cn(
                        "text-xl font-bold flex items-center",
                        (priceHistory.product.price_change || 0) > 0 ? "text-red-500" :
                        (priceHistory.product.price_change || 0) < 0 ? "text-emerald-500" : "text-gray-500"
                      )}>
                        {priceHistory.product.price_change ? (
                           priceHistory.product.price_change > 0 ? '+' : ''
                        ) : ''}
                        {priceHistory.product.price_change ? Number(priceHistory.product.price_change).toFixed(1) : '0'}%
                        {(priceHistory.product.price_change || 0) > 0 && <TrendingUp className="w-4 h-4 ml-1" />}
                        {(priceHistory.product.price_change || 0) < 0 && <TrendingDown className="w-4 h-4 ml-1" />}
                      </div>
                    </div>
                  </div>

                  {/* Last scrape time */}
                  {priceHistory.product.last_scraped_at && (
                    <div className="flex items-center text-xs text-slate-500 bg-gradient-to-r from-slate-50 to-white rounded-xl px-3 py-2 border border-slate-100">
                      <Clock className="w-3.5 h-3.5 mr-2 text-cyan-500" />
                      Last updated: {new Date(priceHistory.product.last_scraped_at).toLocaleString('en-HK')}
                    </div>
                  )}

                  {/* Price timeline */}
                  <div>
                    <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3 flex items-center">
                      <History className="w-3 h-3 mr-1 text-cyan-500" />
                      History (30 days)
                    </h4>
                    <div className="relative border-l-2 border-cyan-200 ml-2 space-y-4 pb-2 max-h-[300px] overflow-y-auto">
                      {priceHistory.history.length === 0 ? (
                        <p className="text-sm text-muted-foreground pl-4 py-2">No price records yet</p>
                      ) : (
                        priceHistory.history.map((snapshot, idx) => (
                          <motion.div
                            key={snapshot.id}
                            className="relative pl-4"
                            initial={{ opacity: 0, x: -10 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: idx * 0.05 }}
                          >
                            <div className={cn(
                              "absolute -left-[5px] top-1.5 w-2.5 h-2.5 rounded-full border-2 border-white shadow-sm",
                              idx === 0 ? "bg-cyan-500 ring-2 ring-cyan-100" : "bg-slate-300"
                            )} />
                            <div className="flex justify-between items-start">
                              <div>
                                <span className="text-sm font-bold text-gray-900 block">
                                  ${snapshot.price ? Number(snapshot.price).toFixed(2) : '-'}
                                </span>
                                <span className="text-xs text-muted-foreground">
                                  {new Date(snapshot.scraped_at).toLocaleDateString('en-HK')}
                                </span>
                              </div>
                              {snapshot.discount_percent && snapshot.discount_percent > 0 && (
                                <HoloBadge variant="error" size="sm">
                                  -{snapshot.discount_percent}% Off
                                </HoloBadge>
                              )}
                            </div>
                          </motion.div>
                        ))
                      )}
                    </div>
                  </div>
                </motion.div>
              ) : null}
            </div>
          </HoloCard>
        </div>
      </div>

      {/* ========== Add Product Dialog ========== */}
      <AddProductDialog
        open={showAddForm}
        onOpenChange={setShowAddForm}
        onSubmit={(data) => addProductMutation.mutate(data)}
        isLoading={addProductMutation.isPending}
      />

      {/* ========== Edit Product Dialog ========== */}
      <EditProductDialog
        product={editingProduct}
        onOpenChange={(open) => { if (!open) setEditingProduct(null) }}
        onSubmit={(data) => {
          if (editingProduct) updateProductMutation.mutate({ id: editingProduct.id, data })
        }}
        isLoading={updateProductMutation.isPending}
      />

      {/* ========== Batch Import Dialog ========== */}
      <BulkImportDialog
        open={showBulkImport}
        onOpenChange={setShowBulkImport}
        onImport={handleBulkImport}
        isLoading={isImporting}
      />
    </PageTransition>
  )
}

// =============================================
// Sub-components
// =============================================

function ProductRow({
  product,
  isSelected,
  isChecked,
  onSelect,
  onToggleCheck,
  onEdit,
  onDelete,
}: {
  product: CompetitorProduct
  isSelected: boolean
  isChecked: boolean
  onSelect: () => void
  onToggleCheck: () => void
  onEdit: () => void
  onDelete: () => void
}) {
  const priceChangeIcon = product.price_change
    ? product.price_change > 0
      ? <TrendingUp className="w-4 h-4 text-red-500" />
      : product.price_change < 0
      ? <TrendingDown className="w-4 h-4 text-emerald-500" />
      : <Minus className="w-4 h-4 text-gray-400" />
    : null

  return (
    <div
      className={cn(
        "group flex items-center p-4 cursor-pointer transition-all duration-300 border-l-4",
        isSelected
          ? "bg-gradient-to-r from-cyan-50/60 to-blue-50/30 border-l-cyan-500"
          : "hover:bg-gradient-to-r hover:from-slate-50/50 hover:to-white border-l-transparent hover:border-l-cyan-300"
      )}
    >
      {/* Checkbox */}
      <button
        onClick={(e) => { e.stopPropagation(); onToggleCheck(); }}
        className="p-1.5 hover:bg-cyan-100 rounded-lg mr-3 transition-colors"
      >
        {isChecked ? (
          <CheckSquare className="w-4 h-4 text-cyan-600" />
        ) : (
          <Square className="w-4 h-4 text-slate-400" />
        )}
      </button>

      {/* Product info */}
      <div
        className="flex items-center space-x-4 flex-1 min-w-0"
        onClick={onSelect}
      >
        <div className={cn(
          "w-12 h-12 rounded-xl flex items-center justify-center shrink-0 overflow-hidden border transition-all",
          product.image_url ? "bg-white border-slate-100" : "bg-gradient-to-br from-slate-50 to-white border-slate-100",
          isSelected && "ring-2 ring-cyan-200 ring-offset-1"
        )}>
          {product.image_url ? (
            <img
              src={product.image_url}
              alt={product.name}
              className="w-full h-full object-cover transition-transform group-hover:scale-110"
            />
          ) : (
            <Package className="w-6 h-6 text-slate-300" />
          )}
        </div>
        <div className="flex-1 min-w-0">
          <h3 className={cn(
            "text-sm font-medium truncate transition-colors",
            isSelected ? "text-cyan-700" : "text-gray-900"
          )}>
            {product.name}
          </h3>
          <div className="flex items-center space-x-2 mt-0.5">
            {product.category && (
              <span className="text-xs text-muted-foreground">{product.category}</span>
            )}
            {product.last_scraped_at && (
              <span className="text-xs text-slate-400 flex items-center">
                <Clock className="w-3 h-3 mr-1" />
                {new Date(product.last_scraped_at).toLocaleDateString('en-HK')}
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Price and status */}
      <div className="flex items-center space-x-4">
        <div className="text-right min-w-[80px]">
          <p className="text-sm font-bold text-gray-900 font-mono">
            ${product.current_price ? Number(product.current_price).toFixed(2) : '-'}
          </p>
          {product.price_change !== null && (
            <div className="flex items-center justify-end text-xs mt-0.5">
              {priceChangeIcon}
              <span
                className={cn("ml-1 font-medium",
                  product.price_change > 0 ? 'text-red-600' :
                  product.price_change < 0 ? 'text-emerald-600' : 'text-gray-500'
                )}
              >
                {product.price_change > 0 ? '+' : ''}
                {product.price_change ? Number(product.price_change).toFixed(1) : '0'}%
              </span>
            </div>
          )}
        </div>

        <HoloBadge
          variant={product.stock_status === 'in_stock' ? 'success' :
                   product.stock_status === 'out_of_stock' ? 'error' : 'default'}
          size="sm"
        >
          {product.stock_status === 'in_stock' ? 'In stock' : product.stock_status === 'out_of_stock' ? 'Out of stock' : 'Unknown'}
        </HoloBadge>

        {/* More actions */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button className="p-1.5 rounded-lg opacity-0 group-hover:opacity-100 hover:bg-slate-100 transition-all">
              <MoreHorizontal className="w-4 h-4 text-slate-500" />
            </button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="bg-white/95 backdrop-blur-xl border-slate-200/80">
            <DropdownMenuItem className="flex items-center" onClick={onEdit}>
              <Pencil className="w-4 h-4 mr-2 text-blue-500" />
              Edit Product
            </DropdownMenuItem>
            <DropdownMenuItem className="flex items-center" onClick={() => window.open(product.url, '_blank')}>
              <ExternalLink className="w-4 h-4 mr-2 text-cyan-500" />
              Visit page
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem
              className="text-red-600 flex items-center"
              onClick={() => { if (confirm(`Are you sure you want to delete "${product.name}"?`)) onDelete() }}
            >
              <Trash2 className="w-4 h-4 mr-2" />
              Delete
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </div>
  )
}

function AddProductDialog({
  open,
  onOpenChange,
  onSubmit,
  isLoading,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSubmit: (data: CompetitorProductCreate) => void
  isLoading: boolean
}) {
  const [formData, setFormData] = useState<CompetitorProductCreate>({
    url: '',
    name: '',
    category: '',
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit(formData)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px] bg-white/95 backdrop-blur-xl border-slate-200/80 shadow-2xl">
        <DialogHeader>
          <DialogTitle className="text-xl font-semibold bg-gradient-to-r from-slate-800 to-slate-600 bg-clip-text text-transparent">
            Add Monitored Product
          </DialogTitle>
          <DialogDescription>
            Enter a product URL. The system will automatically scrape price and stock information.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6 mt-4">
          <div className="space-y-4">
            <div className="grid gap-2">
              <Label htmlFor="product-url" className="text-slate-700">
                Product URL <span className="text-red-500">*</span>
              </Label>
              <div className="relative">
                <ShoppingCart className="absolute left-3 top-3 h-4 w-4 text-cyan-500" />
                <Input
                  id="product-url"
                  type="url"
                  required
                  value={formData.url}
                  onChange={(e) => setFormData({ ...formData, url: e.target.value })}
                  className="pl-9 bg-white/70 backdrop-blur-sm border-slate-200/80 focus:border-cyan-300 focus:ring-cyan-200/50"
                  placeholder="https://..."
                />
              </div>
            </div>

            <div className="grid gap-2">
              <Label htmlFor="product-name" className="text-slate-700">Custom Name (Optional)</Label>
              <Input
                id="product-name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="Leave blank to use the auto-scraped name"
                className="bg-white/70 backdrop-blur-sm border-slate-200/80 focus:border-cyan-300 focus:ring-cyan-200/50"
              />
            </div>

            <div className="grid gap-2">
              <Label htmlFor="product-category" className="text-slate-700">Category Tag (Optional)</Label>
              <Input
                id="product-category"
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                placeholder="e.g.: Beverages / Health Products"
                className="bg-white/70 backdrop-blur-sm border-slate-200/80 focus:border-cyan-300 focus:ring-cyan-200/50"
              />
            </div>
          </div>

          <div className="flex justify-end space-x-3">
            <HoloButton
              type="button"
              variant="ghost"
              onClick={() => onOpenChange(false)}
            >
              Cancel
            </HoloButton>
            <HoloButton
              type="submit"
              variant="primary"
              loading={isLoading}
              icon={!isLoading ? <Check className="w-4 h-4" /> : undefined}
            >
              Start Monitoring
            </HoloButton>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}


// =============================================
// Edit Product Dialog
// =============================================

function EditProductDialog({
  product,
  onOpenChange,
  onSubmit,
  isLoading,
}: {
  product: CompetitorProduct | null
  onOpenChange: (open: boolean) => void
  onSubmit: (data: CompetitorProductUpdate) => void
  isLoading: boolean
}) {
  const [formData, setFormData] = useState({ url: '', name: '', category: '' })
  const [error, setError] = useState('')
  const open = !!product

  // Sync form when product changes
  useEffect(() => {
    if (product) {
      setFormData({
        url: product.url,
        name: product.name || '',
        category: product.category || '',
      })
      setError('')
    }
  }, [product])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    // HKTVmall URL format validation
    if (formData.url.includes('hktvmall.com') && !/\/p\/[A-Z]\d{7,}[A-Za-z0-9_-]*/i.test(formData.url)) {
      setError('HKTVmall URL must include /p/{SKU} format, e.g.: .../p/H0340001 or .../p/B1600001_S_F03A-00')
      return
    }

    const data: CompetitorProductUpdate = {}
    if (product && formData.url !== product.url) data.url = formData.url
    if (product && formData.name !== (product.name || '')) data.name = formData.name
    if (product && formData.category !== (product.category || '')) data.category = formData.category

    if (Object.keys(data).length === 0) {
      onOpenChange(false)
      return
    }
    onSubmit(data)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px] bg-white/95 backdrop-blur-xl border-slate-200/80 shadow-2xl">
        <DialogHeader>
          <DialogTitle className="text-xl font-semibold bg-gradient-to-r from-slate-800 to-slate-600 bg-clip-text text-transparent">
            Edit Product
          </DialogTitle>
          <DialogDescription>
            {"Edit product URL, name, or category. HKTVmall URLs must include /p/H{SKU} format."}
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6 mt-4">
          <div className="space-y-4">
            <div className="grid gap-2">
              <Label htmlFor="edit-url" className="text-slate-700">
                Product URL <span className="text-red-500">*</span>
              </Label>
              <div className="relative">
                <ShoppingCart className="absolute left-3 top-3 h-4 w-4 text-cyan-500" />
                <Input
                  id="edit-url"
                  type="url"
                  required
                  value={formData.url}
                  onChange={(e) => { setFormData({ ...formData, url: e.target.value }); setError('') }}
                  className="pl-9 bg-white/70 backdrop-blur-sm border-slate-200/80 focus:border-cyan-300 focus:ring-cyan-200/50"
                  placeholder="https://www.hktvmall.com/hktv/zh/main/.../p/H0340001"
                />
              </div>
              {error && <p className="text-sm text-red-500">{error}</p>}
            </div>

            <div className="grid gap-2">
              <Label htmlFor="edit-name" className="text-slate-700">Product Name</Label>
              <Input
                id="edit-name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="bg-white/70 backdrop-blur-sm border-slate-200/80 focus:border-cyan-300 focus:ring-cyan-200/50"
              />
            </div>

            <div className="grid gap-2">
              <Label htmlFor="edit-category" className="text-slate-700">Category Tag</Label>
              <Input
                id="edit-category"
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                placeholder="e.g.: Beverages / Health Products"
                className="bg-white/70 backdrop-blur-sm border-slate-200/80 focus:border-cyan-300 focus:ring-cyan-200/50"
              />
            </div>
          </div>

          <div className="flex justify-end space-x-3">
            <HoloButton
              type="button"
              variant="ghost"
              onClick={() => onOpenChange(false)}
            >
              Cancel
            </HoloButton>
            <HoloButton
              type="submit"
              variant="primary"
              loading={isLoading}
              icon={!isLoading ? <Check className="w-4 h-4" /> : undefined}
            >
              Save
            </HoloButton>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}
