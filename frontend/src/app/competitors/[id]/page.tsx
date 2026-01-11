'use client'

import { useState, useMemo } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api, CompetitorProduct, CompetitorProductCreate } from '@/lib/api'
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
// Future Tech 設計系統組件導入
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
// 類型定義
// =============================================

type SortField = 'name' | 'price' | 'price_change' | 'last_scraped'
type SortOrder = 'asc' | 'desc'

// =============================================
// 主頁面組件
// =============================================

export default function CompetitorDetailPage() {
  const params = useParams()
  const competitorId = params.id as string
  const queryClient = useQueryClient()

  // 分頁和搜索
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [searchInput, setSearchInput] = useState('')
  const pageSize = 20

  // UI 狀態
  const [showAddForm, setShowAddForm] = useState(false)
  const [showBulkImport, setShowBulkImport] = useState(false)
  const [isImporting, setIsImporting] = useState(false)
  const [selectedProductId, setSelectedProductId] = useState<string | null>(null)
  const [selectedProducts, setSelectedProducts] = useState<Set<string>>(new Set())
  const [sortField, setSortField] = useState<SortField>('name')
  const [sortOrder, setSortOrder] = useState<SortOrder>('asc')
  const [stockFilter, setStockFilter] = useState<string | undefined>(undefined)

  // ========== 數據查詢 ==========

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

  // ========== 排序和過濾 ==========

  const sortedProducts = useMemo(() => {
    if (!products?.data) return []

    let filtered = [...products.data]

    // 庫存過濾
    if (stockFilter) {
      filtered = filtered.filter(p => p.stock_status === stockFilter)
    }

    // 排序
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

  const scrapeMutation = useMutation({
    mutationFn: () => api.triggerCompetitorScrape(competitorId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['competitor-products', competitorId] })
      queryClient.invalidateQueries({ queryKey: ['competitor', competitorId] })
    },
  })

  // ========== 事件處理 ==========

  // 批量導入處理
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

  // ========== 計算 ==========

  const totalPages = products ? Math.ceil(products.total / pageSize) : 0
  const isLoading = competitorLoading || productsLoading

  // 統計數據
  const stats = useMemo(() => {
    if (!products?.data) return null
    const inStock = products.data.filter(p => p.stock_status === 'in_stock').length
    const outOfStock = products.data.filter(p => p.stock_status === 'out_of_stock').length
    const priceUp = products.data.filter(p => (p.price_change || 0) > 0).length
    const priceDown = products.data.filter(p => (p.price_change || 0) < 0).length
    return { inStock, outOfStock, priceUp, priceDown }
  }, [products?.data])

  // ========== 渲染 ==========

  // Loading 狀態 - 使用 HoloSkeleton
  if (isLoading) {
    return (
      <PageTransition>
        <div className="space-y-6 max-w-7xl mx-auto">
          {/* 頂部骨架 */}
          <div className="space-y-4">
            <HoloSkeleton width={120} height={20} />
            <HoloSkeleton width="60%" height={36} />
            <div className="flex gap-2">
              <HoloSkeleton width={80} height={24} />
              <HoloSkeleton width={120} height={24} />
            </div>
          </div>

          {/* 統計卡片骨架 */}
          <div className="grid grid-cols-4 gap-4">
            {[1, 2, 3, 4].map((i) => (
              <HoloSkeleton key={i} height={100} className="rounded-xl" />
            ))}
          </div>

          {/* 主內容骨架 */}
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
            <span className="font-medium">無法載入商品列表，請稍後再試。</span>
          </div>
        </HoloCard>
      </PageTransition>
    )
  }

  return (
    <PageTransition className="space-y-6 max-w-7xl mx-auto">
      {/* ========== 頂部導航與標題 ========== */}
      <div className="space-y-4">
        <Link
          href="/competitors"
          className="inline-flex items-center text-sm font-medium text-muted-foreground hover:text-cyan-600 transition-colors group"
        >
          <div className="p-1.5 rounded-lg bg-slate-100 group-hover:bg-cyan-50 mr-2 transition-all group-hover:shadow-md group-hover:shadow-cyan-200/50">
            <ArrowLeft className="w-4 h-4 group-hover:text-cyan-600 transition-colors" />
          </div>
          返回競品列表
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
                {products?.total || 0} 個監測商品
              </span>
              {competitor?.last_scraped_at && (
                <>
                  <span className="text-slate-300">|</span>
                  <span className="text-muted-foreground flex items-center text-sm">
                    <Clock className="w-3.5 h-3.5 mr-1 text-cyan-500" />
                    最後更新: {new Date(competitor.last_scraped_at).toLocaleString('zh-HK')}
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
              立即抓取
            </HoloButton>
            <HoloButton
              variant="ghost"
              onClick={() => refetch()}
              icon={<RefreshCw className="w-4 h-4" />}
            >
              刷新
            </HoloButton>
            <HoloButton
              variant="secondary"
              onClick={() => setShowBulkImport(true)}
              icon={<FileSpreadsheet className="w-4 h-4 text-emerald-500" />}
              className="border-emerald-200 hover:border-emerald-300"
            >
              批量導入
            </HoloButton>
            <HoloButton
              variant="primary"
              onClick={() => setShowAddForm(true)}
              icon={<Plus className="w-4 h-4" />}
            >
              新增商品
            </HoloButton>
          </div>
        </div>
      </div>

      {/* ========== 統計卡片 - 使用 DataMetric ========== */}
      {stats && (
        <StaggerContainer className="grid grid-cols-4 gap-4" staggerDelay={0.08}>
          <DataMetric
            label="有貨商品"
            value={stats.inStock}
            icon={<Package className="w-5 h-5 text-emerald-500" />}
            color="green"
          />
          <DataMetric
            label="缺貨商品"
            value={stats.outOfStock}
            icon={<Package className="w-5 h-5 text-amber-500" />}
            color="orange"
          />
          <DataMetric
            label="價格上漲"
            value={stats.priceUp}
            icon={<TrendingUp className="w-5 h-5 text-red-500" />}
            color="purple"
          />
          <DataMetric
            label="價格下跌"
            value={stats.priceDown}
            icon={<TrendingDown className="w-5 h-5 text-emerald-500" />}
            color="cyan"
          />
        </StaggerContainer>
      )}

      {/* ========== 主要內容區域 ========== */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 左側：商品列表 */}
        <div className="lg:col-span-2 space-y-4">
          {/* 搜索和過濾欄 */}
          <div className="flex items-center space-x-3">
            <form onSubmit={handleSearch} className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                type="text"
                placeholder="搜索商品名稱、分類..."
                value={searchInput}
                onChange={(e) => setSearchInput(e.target.value)}
                className="pl-10 bg-white/70 backdrop-blur-sm border-slate-200/80 focus:border-cyan-300 focus:ring-cyan-200/50 transition-all"
              />
            </form>

            {/* 庫存過濾 */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <div>
                  <HoloButton variant="secondary" size="sm" icon={<Filter className="w-4 h-4" />}>
                    {stockFilter === 'in_stock' ? '有貨' :
                     stockFilter === 'out_of_stock' ? '缺貨' : '全部'}
                  </HoloButton>
                </div>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="bg-white/95 backdrop-blur-xl border-slate-200/80">
                <DropdownMenuItem onClick={() => setStockFilter(undefined)}>
                  全部
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setStockFilter('in_stock')}>
                  有貨
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setStockFilter('out_of_stock')}>
                  缺貨
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>

            {/* 排序 */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <div>
                  <HoloButton
                    variant="secondary"
                    size="sm"
                    icon={sortOrder === 'asc' ? <SortAsc className="w-4 h-4" /> : <SortDesc className="w-4 h-4" />}
                  >
                    排序
                  </HoloButton>
                </div>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="bg-white/95 backdrop-blur-xl border-slate-200/80">
                <DropdownMenuItem onClick={() => handleSort('name')}>
                  名稱 {sortField === 'name' && (sortOrder === 'asc' ? '↑' : '↓')}
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => handleSort('price')}>
                  價格 {sortField === 'price' && (sortOrder === 'asc' ? '↑' : '↓')}
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => handleSort('price_change')}>
                  價格變動 {sortField === 'price_change' && (sortOrder === 'asc' ? '↑' : '↓')}
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => handleSort('last_scraped')}>
                  更新時間 {sortField === 'last_scraped' && (sortOrder === 'asc' ? '↑' : '↓')}
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>

          {/* 批量操作欄 */}
          <AnimatePresence>
            {selectedProducts.size > 0 && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="flex items-center justify-between bg-gradient-to-r from-cyan-50 to-blue-50 rounded-xl px-4 py-3 border border-cyan-200/60 shadow-sm"
              >
                <span className="text-sm font-medium text-cyan-700">
                  已選擇 {selectedProducts.size} 個商品
                </span>
                <div className="flex items-center space-x-2">
                  <HoloButton size="sm" variant="ghost" onClick={() => setSelectedProducts(new Set())}>
                    取消選擇
                  </HoloButton>
                  <HoloButton
                    size="sm"
                    variant="secondary"
                    className="border-red-200 text-red-600 hover:bg-red-50"
                    icon={<Trash2 className="w-3.5 h-3.5" />}
                  >
                    刪除
                  </HoloButton>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* 商品列表 - 使用 HoloCard */}
          <HoloCard glowColor="cyan" className="overflow-hidden">
            {/* 列表頭部 */}
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
                {sortedProducts.length} 個商品
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
                    />
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>

            {/* 空狀態 */}
            {sortedProducts.length === 0 && (
              <div className="px-6 py-16 text-center">
                <div className="w-16 h-16 bg-gradient-to-br from-cyan-50 to-blue-50 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg shadow-cyan-100/50">
                  <Package className="w-8 h-8 text-cyan-400" />
                </div>
                <h3 className="text-lg font-medium text-gray-900">尚無監測商品</h3>
                <p className="text-muted-foreground mt-1">點擊右上角「新增商品」開始監測</p>
              </div>
            )}
          </HoloCard>

          {/* 分頁 */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between px-2">
              <div className="text-sm text-muted-foreground">
                第 {page} / {totalPages} 頁
              </div>
              <div className="flex items-center space-x-2">
                <HoloButton
                  variant="secondary"
                  size="sm"
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page <= 1}
                  icon={<ChevronLeft className="w-4 h-4" />}
                >
                  上一頁
                </HoloButton>
                <HoloButton
                  variant="secondary"
                  size="sm"
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  disabled={page >= totalPages}
                  icon={<ChevronRight className="w-4 h-4" />}
                >
                  下一頁
                </HoloButton>
              </div>
            </div>
          )}
        </div>

        {/* ========== 右側：價格歷史側邊欄 - 使用 HoloCard ========== */}
        <div className="lg:col-span-1">
          <HoloCard glowColor="blue" className="sticky top-6 overflow-hidden">
            <HoloPanelHeader
              title="價格走勢分析"
              icon={<LineChart className="w-5 h-5" />}
            />

            <div className="p-6">
              {!selectedProductId ? (
                <div className="text-center py-12">
                  <div className="w-16 h-16 bg-gradient-to-br from-cyan-50 to-blue-50 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg shadow-cyan-100/50 animate-pulse">
                    <LineChart className="w-8 h-8 text-cyan-400" />
                  </div>
                  <h3 className="text-base font-medium text-gray-900">尚未選擇商品</h3>
                  <p className="text-sm text-muted-foreground mt-1">
                    點擊左側列表中的商品<br/>查看詳細價格歷史與分析
                  </p>
                </div>
              ) : historyLoading ? (
                <div className="flex flex-col items-center justify-center py-12 space-y-4">
                  <div className="relative">
                    <div className="absolute inset-0 bg-cyan-500/20 blur-xl rounded-full animate-pulse" />
                    <RefreshCw className="relative w-8 h-8 animate-spin text-cyan-500" />
                  </div>
                  <span className="text-sm text-muted-foreground">正在分析數據...</span>
                </div>
              ) : priceHistory ? (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.4 }}
                  className="space-y-6"
                >
                  {/* 商品信息 */}
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
                          訪問商品頁面
                        </a>
                      )}
                      <HoloBadge
                        variant={priceHistory.product.stock_status === 'in_stock' ? 'success' : 'error'}
                        size="sm"
                      >
                        {priceHistory.product.stock_status === 'in_stock' ? '有貨' : '缺貨'}
                      </HoloBadge>
                    </div>
                  </div>

                  {/* 價格卡片 */}
                  <div className="grid grid-cols-2 gap-3">
                    <div className="bg-gradient-to-br from-slate-50 to-white p-3 rounded-xl border border-slate-100 shadow-sm">
                      <div className="text-xs text-muted-foreground mb-1">當前價格</div>
                      <div className="text-xl font-bold text-gray-900">
                        ${priceHistory.product.current_price?.toFixed(2) || '-'}
                      </div>
                    </div>
                    <div className="bg-gradient-to-br from-slate-50 to-white p-3 rounded-xl border border-slate-100 shadow-sm">
                      <div className="text-xs text-muted-foreground mb-1">價格變動</div>
                      <div className={cn(
                        "text-xl font-bold flex items-center",
                        (priceHistory.product.price_change || 0) > 0 ? "text-red-500" :
                        (priceHistory.product.price_change || 0) < 0 ? "text-emerald-500" : "text-gray-500"
                      )}>
                        {priceHistory.product.price_change ? (
                           priceHistory.product.price_change > 0 ? '+' : ''
                        ) : ''}
                        {priceHistory.product.price_change?.toFixed(1) || '0'}%
                        {(priceHistory.product.price_change || 0) > 0 && <TrendingUp className="w-4 h-4 ml-1" />}
                        {(priceHistory.product.price_change || 0) < 0 && <TrendingDown className="w-4 h-4 ml-1" />}
                      </div>
                    </div>
                  </div>

                  {/* 最後抓取時間 */}
                  {priceHistory.product.last_scraped_at && (
                    <div className="flex items-center text-xs text-slate-500 bg-gradient-to-r from-slate-50 to-white rounded-xl px-3 py-2 border border-slate-100">
                      <Clock className="w-3.5 h-3.5 mr-2 text-cyan-500" />
                      最後更新: {new Date(priceHistory.product.last_scraped_at).toLocaleString('zh-HK')}
                    </div>
                  )}

                  {/* 價格時間軸 */}
                  <div>
                    <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3 flex items-center">
                      <History className="w-3 h-3 mr-1 text-cyan-500" />
                      歷史記錄 (30天)
                    </h4>
                    <div className="relative border-l-2 border-cyan-200 ml-2 space-y-4 pb-2 max-h-[300px] overflow-y-auto">
                      {priceHistory.history.length === 0 ? (
                        <p className="text-sm text-muted-foreground pl-4 py-2">暫無價格記錄</p>
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
                                  ${snapshot.price?.toFixed(2) || '-'}
                                </span>
                                <span className="text-xs text-muted-foreground">
                                  {new Date(snapshot.scraped_at).toLocaleDateString('zh-HK')}
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

      {/* ========== 新增商品彈窗 ========== */}
      <AddProductDialog
        open={showAddForm}
        onOpenChange={setShowAddForm}
        onSubmit={(data) => addProductMutation.mutate(data)}
        isLoading={addProductMutation.isPending}
      />

      {/* ========== 批量導入彈窗 ========== */}
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
// 子組件
// =============================================

function ProductRow({
  product,
  isSelected,
  isChecked,
  onSelect,
  onToggleCheck,
}: {
  product: CompetitorProduct
  isSelected: boolean
  isChecked: boolean
  onSelect: () => void
  onToggleCheck: () => void
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
      {/* 複選框 */}
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

      {/* 商品信息 */}
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
                {new Date(product.last_scraped_at).toLocaleDateString('zh-HK')}
              </span>
            )}
          </div>
        </div>
      </div>

      {/* 價格和狀態 */}
      <div className="flex items-center space-x-4">
        <div className="text-right min-w-[80px]">
          <p className="text-sm font-bold text-gray-900 font-mono">
            ${product.current_price?.toFixed(2) || '-'}
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
                {product.price_change?.toFixed(1)}%
              </span>
            </div>
          )}
        </div>

        <HoloBadge
          variant={product.stock_status === 'in_stock' ? 'success' :
                   product.stock_status === 'out_of_stock' ? 'error' : 'default'}
          size="sm"
        >
          {product.stock_status === 'in_stock' ? '有貨' : product.stock_status === 'out_of_stock' ? '缺貨' : '未知'}
        </HoloBadge>

        {/* 更多操作 */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button className="p-1.5 rounded-lg opacity-0 group-hover:opacity-100 hover:bg-slate-100 transition-all">
              <MoreHorizontal className="w-4 h-4 text-slate-500" />
            </button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="bg-white/95 backdrop-blur-xl border-slate-200/80">
            <DropdownMenuItem className="flex items-center">
              <Zap className="w-4 h-4 mr-2 text-amber-500" />
              重新抓取
            </DropdownMenuItem>
            <DropdownMenuItem className="flex items-center">
              <ExternalLink className="w-4 h-4 mr-2 text-cyan-500" />
              訪問頁面
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem className="text-red-600 flex items-center">
              <Trash2 className="w-4 h-4 mr-2" />
              刪除
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
            新增監測商品
          </DialogTitle>
          <DialogDescription>
            輸入商品鏈接，系統將自動抓取價格和庫存信息。
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6 mt-4">
          <div className="space-y-4">
            <div className="grid gap-2">
              <Label htmlFor="product-url" className="text-slate-700">
                商品 URL <span className="text-red-500">*</span>
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
              <Label htmlFor="product-name" className="text-slate-700">自定義名稱（可選）</Label>
              <Input
                id="product-name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="留空則使用自動抓取的名稱"
                className="bg-white/70 backdrop-blur-sm border-slate-200/80 focus:border-cyan-300 focus:ring-cyan-200/50"
              />
            </div>

            <div className="grid gap-2">
              <Label htmlFor="product-category" className="text-slate-700">分類標籤（可選）</Label>
              <Input
                id="product-category"
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                placeholder="例如：飲品 / 保健品"
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
              取消
            </HoloButton>
            <HoloButton
              type="submit"
              variant="primary"
              loading={isLoading}
              icon={!isLoading ? <Check className="w-4 h-4" /> : undefined}
            >
              開始監測
            </HoloButton>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}
