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
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
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
  
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <div className="relative">
          <div className="absolute inset-0 bg-blue-500/20 blur-xl rounded-full animate-pulse" />
          <RefreshCw className="relative w-12 h-12 animate-spin text-primary" />
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="glass-panel border-destructive/20 bg-destructive/5 p-6 rounded-xl flex items-center text-destructive">
        <AlertCircle className="w-5 h-5 mr-3" />
        <span className="font-medium">無法載入商品列表，請稍後再試。</span>
      </div>
    )
  }

  return (
    <div className="space-y-6 animate-fade-in-up">
      {/* ========== 頂部導航與標題 ========== */}
      <div className="space-y-4">
        <Link
          href="/competitors"
          className="inline-flex items-center text-sm font-medium text-muted-foreground hover:text-primary transition-colors group"
        >
          <div className="p-1 rounded-full bg-slate-100 group-hover:bg-blue-50 mr-2 transition-colors">
            <ArrowLeft className="w-4 h-4" />
          </div>
          返回競品列表
        </Link>
        
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-foreground">
              {competitor?.name}
            </h1>
            <div className="flex items-center space-x-3 mt-2">
              <Badge variant="secondary" className="font-normal text-slate-600">
                {competitor?.platform}
              </Badge>
              <span className="text-slate-300">|</span>
              <span className="text-muted-foreground flex items-center">
                <Package className="w-4 h-4 mr-1" />
                {products?.total || 0} 個監測商品
              </span>
              {competitor?.last_scraped_at && (
                <>
                  <span className="text-slate-300">|</span>
                  <span className="text-muted-foreground flex items-center text-sm">
                    <Clock className="w-3.5 h-3.5 mr-1" />
                    最後更新: {new Date(competitor.last_scraped_at).toLocaleString('zh-HK')}
                  </span>
                </>
              )}
            </div>
          </div>
          
          <div className="flex space-x-3">
            <Button
              variant="outline"
              onClick={() => scrapeMutation.mutate()}
              disabled={scrapeMutation.isPending}
              className={cn(
                "transition-all",
                scrapeMutation.isPending && "bg-blue-50"
              )}
            >
              {scrapeMutation.isPending ? (
                <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <Zap className="w-4 h-4 mr-2 text-yellow-500" />
              )}
              立即抓取
            </Button>
            <Button
              variant="outline"
              onClick={() => refetch()}
              className="glass-card hover:bg-white/60"
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              刷新
            </Button>
            <Button
              variant="outline"
              onClick={() => setShowBulkImport(true)}
              className="border-green-200 text-green-700 hover:bg-green-50"
            >
              <FileSpreadsheet className="w-4 h-4 mr-2" />
              批量導入
            </Button>
            <Button
              onClick={() => setShowAddForm(true)}
              className="bg-primary hover:bg-primary/90 shadow-lg shadow-blue-500/20"
            >
              <Plus className="w-4 h-4 mr-2" />
              新增商品
            </Button>
          </div>
        </div>
      </div>

      {/* ========== 統計卡片 ========== */}
      {stats && (
        <div className="grid grid-cols-4 gap-4">
          <StatCard 
            label="有貨商品" 
            value={stats.inStock} 
            icon={Package}
            color="green"
          />
          <StatCard 
            label="缺貨商品" 
            value={stats.outOfStock} 
            icon={Package}
            color="red"
          />
          <StatCard 
            label="價格上漲" 
            value={stats.priceUp} 
            icon={TrendingUp}
            color="red"
          />
          <StatCard 
            label="價格下跌" 
            value={stats.priceDown} 
            icon={TrendingDown}
            color="green"
          />
        </div>
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
                className="pl-10 bg-white/50 border-white/40"
              />
            </form>
            
            {/* 庫存過濾 */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="sm" className="h-10">
                  <Filter className="w-4 h-4 mr-2" />
                  {stockFilter === 'in_stock' ? '有貨' : 
                   stockFilter === 'out_of_stock' ? '缺貨' : '全部'}
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
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
                <Button variant="outline" size="sm" className="h-10">
                  {sortOrder === 'asc' ? <SortAsc className="w-4 h-4 mr-2" /> : <SortDesc className="w-4 h-4 mr-2" />}
                  排序
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
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
                className="flex items-center justify-between bg-blue-50 rounded-lg px-4 py-2 border border-blue-200"
              >
                <span className="text-sm text-blue-700">
                  已選擇 {selectedProducts.size} 個商品
                </span>
                <div className="flex items-center space-x-2">
                  <Button size="sm" variant="ghost" onClick={() => setSelectedProducts(new Set())}>
                    取消選擇
                  </Button>
                  <Button size="sm" variant="destructive" className="h-8">
                    <Trash2 className="w-3.5 h-3.5 mr-1" />
                    刪除
                  </Button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* 商品列表 */}
          <div className="glass-panel rounded-xl overflow-hidden border border-white/40">
            {/* 列表頭部 */}
            <div className="px-4 py-2 bg-slate-50/80 border-b border-slate-100 flex items-center">
              <button 
                onClick={toggleSelectAll}
                className="p-1 hover:bg-slate-200 rounded mr-3"
              >
                {selectedProducts.size === sortedProducts.length && sortedProducts.length > 0 ? (
                  <CheckSquare className="w-4 h-4 text-blue-600" />
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
                    transition={{ delay: index * 0.03 }}
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
                <div className="w-16 h-16 bg-slate-50 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Package className="w-8 h-8 text-slate-300" />
                </div>
                <h3 className="text-lg font-medium text-gray-900">尚無監測商品</h3>
                <p className="text-muted-foreground mt-1">點擊右上角「新增商品」開始監測</p>
              </div>
            )}
          </div>

          {/* 分頁 */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between px-2">
              <div className="text-sm text-muted-foreground">
                第 {page} / {totalPages} 頁
              </div>
              <div className="flex items-center space-x-2">
                <Button
                  variant="outline"
                  size="icon"
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page <= 1}
                  className="bg-white/50"
                >
                  <ChevronLeft className="w-4 h-4" />
                </Button>
                <Button
                  variant="outline"
                  size="icon"
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  disabled={page >= totalPages}
                  className="bg-white/50"
                >
                  <ChevronRight className="w-4 h-4" />
                </Button>
              </div>
            </div>
          )}
        </div>

        {/* ========== 右側：價格歷史側邊欄 ========== */}
        <div className="lg:col-span-1">
          <div className="glass-panel rounded-xl sticky top-6 overflow-hidden border border-white/40 shadow-xl shadow-blue-500/5">
            <div className="p-4 bg-gradient-to-r from-slate-50 to-white border-b border-slate-100">
              <h2 className="text-lg font-semibold text-gray-900 flex items-center">
                <LineChart className="w-5 h-5 mr-2 text-primary" />
                價格走勢分析
              </h2>
            </div>

            <div className="p-6">
              {!selectedProductId ? (
                <div className="text-center py-12">
                  <div className="w-16 h-16 bg-blue-50 rounded-full flex items-center justify-center mx-auto mb-4 animate-pulse">
                    <LineChart className="w-8 h-8 text-blue-300" />
                  </div>
                  <h3 className="text-base font-medium text-gray-900">尚未選擇商品</h3>
                  <p className="text-sm text-muted-foreground mt-1">
                    點擊左側列表中的商品<br/>查看詳細價格歷史與分析
                  </p>
                </div>
              ) : historyLoading ? (
                <div className="flex flex-col items-center justify-center py-12">
                  <RefreshCw className="w-8 h-8 animate-spin text-primary mb-3" />
                  <span className="text-sm text-muted-foreground">正在分析數據...</span>
                </div>
              ) : priceHistory ? (
                <div className="space-y-6 animate-fade-in-up">
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
                          className="inline-flex items-center text-xs text-blue-600 hover:text-blue-700 bg-blue-50 px-2 py-1 rounded-md transition-colors"
                        >
                          <ExternalLink className="w-3 h-3 mr-1" />
                          訪問商品頁面
                        </a>
                      )}
                      <Badge 
                        variant="secondary"
                        className={cn(
                          "text-xs",
                          priceHistory.product.stock_status === 'in_stock' 
                            ? 'bg-green-100 text-green-700' 
                            : 'bg-red-100 text-red-700'
                        )}
                      >
                        {priceHistory.product.stock_status === 'in_stock' ? '有貨' : '缺貨'}
                      </Badge>
                    </div>
                  </div>

                  {/* 價格卡片 */}
                  <div className="grid grid-cols-2 gap-3">
                    <div className="bg-slate-50 p-3 rounded-lg border border-slate-100">
                      <div className="text-xs text-muted-foreground mb-1">當前價格</div>
                      <div className="text-xl font-bold text-gray-900">
                        ${priceHistory.product.current_price?.toFixed(2) || '-'}
                      </div>
                    </div>
                    <div className="bg-slate-50 p-3 rounded-lg border border-slate-100">
                      <div className="text-xs text-muted-foreground mb-1">價格變動</div>
                      <div className={cn(
                        "text-xl font-bold flex items-center",
                        (priceHistory.product.price_change || 0) > 0 ? "text-red-500" : 
                        (priceHistory.product.price_change || 0) < 0 ? "text-green-500" : "text-gray-500"
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
                    <div className="flex items-center text-xs text-slate-500 bg-slate-50 rounded-lg px-3 py-2">
                      <Clock className="w-3.5 h-3.5 mr-2" />
                      最後更新: {new Date(priceHistory.product.last_scraped_at).toLocaleString('zh-HK')}
                    </div>
                  )}

                  {/* 價格時間軸 */}
                  <div>
                    <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3 flex items-center">
                      <History className="w-3 h-3 mr-1" />
                      歷史記錄 (30天)
                    </h4>
                    <div className="relative border-l-2 border-slate-200 ml-2 space-y-4 pb-2 max-h-[300px] overflow-y-auto">
                      {priceHistory.history.length === 0 ? (
                        <p className="text-sm text-muted-foreground pl-4 py-2">暫無價格記錄</p>
                      ) : (
                        priceHistory.history.map((snapshot, idx) => (
                          <div key={snapshot.id} className="relative pl-4">
                            <div className={cn(
                              "absolute -left-[5px] top-1.5 w-2.5 h-2.5 rounded-full border-2 border-white",
                              idx === 0 ? "bg-blue-500 ring-2 ring-blue-100" : "bg-slate-300"
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
                                <Badge variant="secondary" className="text-xs bg-red-50 text-red-600 border-red-100">
                                  -{snapshot.discount_percent}% Off
                                </Badge>
                              )}
                            </div>
                          </div>
                        ))
                      )}
                    </div>
                  </div>
                </div>
              ) : null}
            </div>
          </div>
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
    </div>
  )
}

// =============================================
// 子組件
// =============================================

function StatCard({ 
  label, 
  value, 
  icon: Icon, 
  color 
}: { 
  label: string
  value: number
  icon: React.ElementType
  color: 'green' | 'red' | 'blue' | 'yellow'
}) {
  const colorClasses = {
    green: 'bg-green-50 text-green-600 border-green-100',
    red: 'bg-red-50 text-red-600 border-red-100',
    blue: 'bg-blue-50 text-blue-600 border-blue-100',
    yellow: 'bg-yellow-50 text-yellow-600 border-yellow-100'
  }
  
  return (
    <div className={cn(
      "rounded-xl p-4 border transition-all hover:shadow-md",
      colorClasses[color]
    )}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs font-medium opacity-80">{label}</p>
          <p className="text-2xl font-bold mt-1">{value}</p>
        </div>
        <Icon className="w-8 h-8 opacity-50" />
      </div>
    </div>
  )
}

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
      ? <TrendingDown className="w-4 h-4 text-green-500" />
      : <Minus className="w-4 h-4 text-gray-400" />
    : null

  return (
    <div
      className={cn(
        "group flex items-center p-4 cursor-pointer transition-all duration-200 border-l-4",
        isSelected 
          ? "bg-blue-50/60 border-l-blue-500" 
          : "hover:bg-slate-50/50 border-l-transparent hover:border-l-slate-300"
      )}
    >
      {/* 複選框 */}
      <button 
        onClick={(e) => { e.stopPropagation(); onToggleCheck(); }}
        className="p-1 hover:bg-slate-200 rounded mr-3"
      >
        {isChecked ? (
          <CheckSquare className="w-4 h-4 text-blue-600" />
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
          "w-12 h-12 rounded-lg flex items-center justify-center shrink-0 overflow-hidden border border-slate-100",
          product.image_url ? "bg-white" : "bg-slate-50"
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
            isSelected ? "text-blue-700" : "text-gray-900"
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
                  product.price_change < 0 ? 'text-green-600' : 'text-gray-500'
                )}
              >
                {product.price_change > 0 ? '+' : ''}
                {product.price_change?.toFixed(1)}%
              </span>
            </div>
          )}
        </div>

        <Badge 
          variant="secondary"
          className={cn(
            "min-w-[60px] justify-center",
            product.stock_status === 'in_stock' ? 'bg-green-100 text-green-700' : 
            product.stock_status === 'out_of_stock' ? 'bg-red-100 text-red-700' : 'bg-slate-100 text-slate-600'
          )}
        >
          {product.stock_status === 'in_stock' ? '有貨' : product.stock_status === 'out_of_stock' ? '缺貨' : '未知'}
        </Badge>

        {/* 更多操作 */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon" className="h-8 w-8 opacity-0 group-hover:opacity-100">
              <MoreHorizontal className="w-4 h-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem>
              <Zap className="w-4 h-4 mr-2" />
              重新抓取
            </DropdownMenuItem>
            <DropdownMenuItem>
              <ExternalLink className="w-4 h-4 mr-2" />
              訪問頁面
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem className="text-red-600">
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
      <DialogContent className="sm:max-w-[500px] glass-panel border-white/40">
        <DialogHeader>
          <DialogTitle>新增監測商品</DialogTitle>
          <DialogDescription>
            輸入商品鏈接，系統將自動抓取價格和庫存信息。
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6 mt-4">
          <div className="space-y-4">
            <div className="grid gap-2">
              <Label htmlFor="product-url">商品 URL <span className="text-destructive">*</span></Label>
              <div className="relative">
                <ShoppingCart className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  id="product-url"
                  type="url"
                  required
                  value={formData.url}
                  onChange={(e) => setFormData({ ...formData, url: e.target.value })}
                  className="pl-9 bg-white/50"
                  placeholder="https://..."
                />
              </div>
            </div>

            <div className="grid gap-2">
              <Label htmlFor="product-name">自定義名稱（可選）</Label>
              <Input
                id="product-name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="留空則使用自動抓取的名稱"
                className="bg-white/50"
              />
            </div>

            <div className="grid gap-2">
              <Label htmlFor="product-category">分類標籤（可選）</Label>
              <Input
                id="product-category"
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                placeholder="例如：飲品 / 保健品"
                className="bg-white/50"
              />
            </div>
          </div>

          <div className="flex justify-end space-x-3">
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
            >
              取消
            </Button>
            <Button
              type="submit"
              disabled={isLoading}
              className="bg-primary hover:bg-primary/90"
            >
              {isLoading ? (
                <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <Check className="w-4 h-4 mr-2" />
              )}
              開始監測
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}
