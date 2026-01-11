'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api, Product, PreviewProduct, PreviewScrapeResponse } from '@/lib/api'
import Link from 'next/link'
import {
  ArrowLeft,
  RefreshCw,
  Download,
  Play,
  ExternalLink,
  TrendingDown,
  Package,
  DollarSign,
  BarChart3,
  Trash2,
  CheckSquare,
  Square,
  Eye,
  X,
  Check,
  AlertTriangle,
  Zap,
} from 'lucide-react'
import QuotaDisplay from '@/components/QuotaDisplay'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
} from 'recharts'
import {
  PageTransition,
  HoloCard,
  HoloPanelHeader,
  HoloButton,
  HoloBadge,
  DataMetric,
  HoloSkeleton,
  StaggerContainer,
} from '@/components/ui/future-tech'

export default function CategoryDetailPage({ params }: { params: { id: string } }) {
  const queryClient = useQueryClient()
  const [selectedProduct, setSelectedProduct] = useState<string | null>(null)
  const [isScrapng, setIsScraping] = useState(false)
  const [selectedProducts, setSelectedProducts] = useState<Set<string>>(new Set())
  const [isDeleting, setIsDeleting] = useState(false)

  // 預覽模式狀態
  const [previewMode, setPreviewMode] = useState(false)
  const [previewData, setPreviewData] = useState<PreviewScrapeResponse | null>(null)
  const [selectedPreviewIndices, setSelectedPreviewIndices] = useState<Set<number>>(new Set())
  const [isConfirming, setIsConfirming] = useState(false)

  // 智能抓取狀態
  const [isSmartScraping, setIsSmartScraping] = useState(false)
  const [smartScrapeResult, setSmartScrapeResult] = useState<{
    success: boolean
    message: string
    credits_used: number
    new_products: number
    updated_products: number
  } | null>(null)

  const { data: category, isLoading: categoryLoading } = useQuery({
    queryKey: ['category', params.id],
    queryFn: () => api.getCategory(params.id),
  })

  const { data: stats } = useQuery({
    queryKey: ['category-stats', params.id],
    queryFn: () => api.getCategoryStats(params.id),
  })

  const { data: overview } = useQuery({
    queryKey: ['category-overview', params.id],
    queryFn: () => api.getCategoryPriceOverview(params.id),
  })

  const { data: products, isLoading: productsLoading } = useQuery({
    queryKey: ['category-products', params.id],
    queryFn: () => api.getCategoryProducts(params.id, 1, 50),
  })

  const { data: priceHistory } = useQuery({
    queryKey: ['price-history', params.id, selectedProduct],
    queryFn: () => selectedProduct ? api.getProductPriceHistory(params.id, selectedProduct, 30) : null,
    enabled: !!selectedProduct,
  })

  // 預覽抓取 mutation
  const previewMutation = useMutation({
    mutationFn: () => api.previewScrape(params.id, 30),
    onSuccess: (data) => {
      setPreviewData(data)
      setPreviewMode(true)
      // 默認全選
      setSelectedPreviewIndices(new Set(data.products.map((_, i) => i)))
      setIsScraping(false)
    },
    onError: () => {
      setIsScraping(false)
      alert('抓取失敗，請稍後重試')
    },
  })

  // 智能抓取 mutation（優化版，節省 API 配額）
  const smartScrapeMutation = useMutation({
    mutationFn: () => api.smartScrape(params.id, { max_new_products: 10, max_updates: 20 }),
    onSuccess: (data) => {
      setSmartScrapeResult(data)
      setIsSmartScraping(false)
      queryClient.invalidateQueries({ queryKey: ['category', params.id] })
      queryClient.invalidateQueries({ queryKey: ['category-stats', params.id] })
      queryClient.invalidateQueries({ queryKey: ['category-products', params.id] })
      queryClient.invalidateQueries({ queryKey: ['quota-usage'] })
    },
    onError: (error) => {
      setIsSmartScraping(false)
      alert(`智能抓取失敗: ${error}`)
    },
  })

  // 確認保存 mutation
  const confirmMutation = useMutation({
    mutationFn: () => {
      if (!previewData) return Promise.reject('No preview data')
      const indices = Array.from(selectedPreviewIndices)
      return api.confirmScrape(params.id, previewData.preview_id, indices.length === previewData.products.length ? undefined : indices)
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['category', params.id] })
      queryClient.invalidateQueries({ queryKey: ['category-products', params.id] })
      queryClient.invalidateQueries({ queryKey: ['category-stats', params.id] })
      setPreviewMode(false)
      setPreviewData(null)
      setSelectedPreviewIndices(new Set())
      setIsConfirming(false)
      alert(`成功保存 ${data.saved_count} 個商品`)
    },
    onError: () => {
      setIsConfirming(false)
      alert('保存失敗，請稍後重試')
    },
  })

  // 刪除單個商品
  const deleteProductMutation = useMutation({
    mutationFn: (productId: string) => api.deleteProduct(params.id, productId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['category-products', params.id] })
      queryClient.invalidateQueries({ queryKey: ['category-stats', params.id] })
    },
  })

  // 批量刪除
  const bulkDeleteMutation = useMutation({
    mutationFn: (productIds: string[]) => api.bulkDeleteProducts(params.id, productIds),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['category-products', params.id] })
      queryClient.invalidateQueries({ queryKey: ['category-stats', params.id] })
      setSelectedProducts(new Set())
      setIsDeleting(false)
      alert(`成功刪除 ${data.deleted_count} 個商品`)
    },
    onError: () => {
      setIsDeleting(false)
      alert('刪除失敗')
    },
  })

  // 切換商品選擇
  const toggleProductSelection = (productId: string) => {
    const newSet = new Set(selectedProducts)
    if (newSet.has(productId)) {
      newSet.delete(productId)
    } else {
      newSet.add(productId)
    }
    setSelectedProducts(newSet)
  }

  // 全選/取消全選
  const toggleSelectAll = () => {
    if (products?.items) {
      if (selectedProducts.size === products.items.length) {
        setSelectedProducts(new Set())
      } else {
        setSelectedProducts(new Set(products.items.map(p => p.id)))
      }
    }
  }

  // 切換預覽商品選擇
  const togglePreviewSelection = (index: number) => {
    const newSet = new Set(selectedPreviewIndices)
    if (newSet.has(index)) {
      newSet.delete(index)
    } else {
      newSet.add(index)
    }
    setSelectedPreviewIndices(newSet)
  }

  // 預覽全選/取消全選
  const togglePreviewSelectAll = () => {
    if (previewData) {
      if (selectedPreviewIndices.size === previewData.products.length) {
        setSelectedPreviewIndices(new Set())
      } else {
        setSelectedPreviewIndices(new Set(previewData.products.map((_, i) => i)))
      }
    }
  }

  // 取消預覽
  const cancelPreview = () => {
    if (previewData) {
      api.cancelPreview(params.id, previewData.preview_id)
    }
    setPreviewMode(false)
    setPreviewData(null)
    setSelectedPreviewIndices(new Set())
  }

  // ==================== 加載狀態 ====================
  if (categoryLoading) {
    return (
      <PageTransition>
        <div className="space-y-6">
          {/* 標題骨架屏 */}
          <div className="flex items-center space-x-4">
            <HoloSkeleton width={40} height={40} variant="circular" />
            <div className="space-y-2">
              <HoloSkeleton width={200} height={28} />
              <HoloSkeleton width={150} height={16} />
            </div>
          </div>
          {/* 統計卡片骨架屏 */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[1, 2, 3, 4].map((i) => (
              <HoloCard key={i} className="p-6">
                <div className="flex items-center justify-between">
                  <div className="space-y-2">
                    <HoloSkeleton width={80} height={14} />
                    <HoloSkeleton width={100} height={32} />
                    <HoloSkeleton width={60} height={14} />
                  </div>
                  <HoloSkeleton width={48} height={48} variant="rectangular" className="rounded-lg" />
                </div>
              </HoloCard>
            ))}
          </div>
          {/* 圖表骨架屏 */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <HoloCard className="p-6">
              <HoloSkeleton width={120} height={24} className="mb-4" />
              <HoloSkeleton height={250} />
            </HoloCard>
            <HoloCard className="p-6">
              <HoloSkeleton width={120} height={24} className="mb-4" />
              <HoloSkeleton height={250} />
            </HoloCard>
          </div>
        </div>
      </PageTransition>
    )
  }

  // ==================== 預覽審核界面 ====================
  if (previewMode && previewData) {
    return (
      <PageTransition>
        <div className="space-y-6">
          {/* 預覽標題 */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <HoloButton
                variant="ghost"
                size="sm"
                onClick={cancelPreview}
                icon={<ArrowLeft className="w-5 h-5" />}
              >
                返回
              </HoloButton>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-slate-800 to-slate-600 bg-clip-text text-transparent">
                  審核抓取結果
                </h1>
                <p className="text-slate-500 mt-1">
                  已抓取 <span className="font-semibold text-cyan-600">{previewData.total_scraped}</span> 個商品，請選擇要保存的商品
                </p>
              </div>
            </div>
            <div className="flex space-x-3">
              <HoloButton
                variant="secondary"
                onClick={cancelPreview}
                icon={<X className="w-4 h-4" />}
              >
                取消
              </HoloButton>
              <HoloButton
                variant="primary"
                onClick={() => {
                  setIsConfirming(true)
                  confirmMutation.mutate()
                }}
                disabled={isConfirming || selectedPreviewIndices.size === 0}
                loading={isConfirming}
                icon={<Check className="w-4 h-4" />}
              >
                確認保存 ({selectedPreviewIndices.size})
              </HoloButton>
            </div>
          </div>

          {/* 錯誤提示 */}
          {previewData.errors.length > 0 && (
            <HoloCard glowColor="purple" className="p-4 bg-amber-50/80">
              <div className="flex items-start">
                <AlertTriangle className="w-5 h-5 text-amber-600 mt-0.5 mr-3 flex-shrink-0" />
                <div>
                  <h4 className="text-sm font-medium text-amber-800">部分抓取失敗</h4>
                  <ul className="mt-2 text-sm text-amber-700 space-y-1">
                    {previewData.errors.slice(0, 3).map((err, i) => (
                      <li key={i}>{err}</li>
                    ))}
                    {previewData.errors.length > 3 && (
                      <li>還有 {previewData.errors.length - 3} 個錯誤...</li>
                    )}
                  </ul>
                </div>
              </div>
            </HoloCard>
          )}

          {/* 預覽商品列表 */}
          <HoloCard glowColor="cyan">
            <HoloPanelHeader
              title={`待審核商品 (${previewData.products.length})`}
              icon={<Package className="w-5 h-5" />}
              action={
                <button
                  onClick={togglePreviewSelectAll}
                  className="text-sm font-medium text-cyan-600 hover:text-cyan-700 transition-colors"
                >
                  {selectedPreviewIndices.size === previewData.products.length ? '取消全選' : '全選'}
                </button>
              }
            />
            <div className="divide-y divide-slate-100 max-h-[600px] overflow-y-auto">
              {previewData.products.map((product, index) => (
                <div
                  key={index}
                  className={`px-6 py-4 flex items-center space-x-4 transition-all duration-200 hover:bg-slate-50/80 ${
                    selectedPreviewIndices.has(index) ? 'bg-cyan-50/50' : ''
                  }`}
                >
                  <button
                    onClick={() => togglePreviewSelection(index)}
                    className="flex-shrink-0 transition-transform hover:scale-110"
                  >
                    {selectedPreviewIndices.has(index) ? (
                      <CheckSquare className="w-5 h-5 text-cyan-600" />
                    ) : (
                      <Square className="w-5 h-5 text-slate-400" />
                    )}
                  </button>
                  {product.image_url && (
                    <img
                      src={product.image_url}
                      alt={product.name}
                      className="w-16 h-16 object-cover rounded-xl flex-shrink-0 border border-slate-200/50 shadow-sm"
                    />
                  )}
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-slate-800 truncate">{product.name}</p>
                    <p className="text-xs text-slate-500">
                      {product.brand || '未知品牌'} {product.sku && `| SKU: ${product.sku}`}
                    </p>
                  </div>
                  <div className="text-right flex-shrink-0">
                    <p className="text-sm font-bold text-cyan-600">
                      {product.price ? `$${Number(product.price).toFixed(0)}` : '-'}
                    </p>
                    {product.discount_percent && Number(product.discount_percent) > 0 && (
                      <HoloBadge variant="error" size="sm">
                        -{Number(product.discount_percent).toFixed(0)}%
                      </HoloBadge>
                    )}
                  </div>
                  <a
                    href={product.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="p-2 hover:bg-slate-100 rounded-lg transition-colors flex-shrink-0"
                  >
                    <ExternalLink className="w-4 h-4 text-slate-500" />
                  </a>
                </div>
              ))}
            </div>
          </HoloCard>
        </div>
      </PageTransition>
    )
  }

  // ==================== 主頁面 ====================
  return (
    <PageTransition>
      <div className="space-y-6">
        {/* 頁面標題 */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Link
              href="/categories"
              className="p-2 hover:bg-slate-100 rounded-xl transition-colors"
            >
              <ArrowLeft className="w-5 h-5 text-slate-600" />
            </Link>
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-slate-800 to-slate-600 bg-clip-text text-transparent">
                {category?.name}
              </h1>
              <p className="text-slate-500 mt-1">{category?.description || '類別商品監測'}</p>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <QuotaDisplay compact />
            <HoloButton
              variant="secondary"
              onClick={() => {
                setIsSmartScraping(true)
                smartScrapeMutation.mutate()
              }}
              disabled={isSmartScraping}
              loading={isSmartScraping}
              icon={<Zap className="w-4 h-4" />}
            >
              {isSmartScraping ? '智能更新中...' : '智能抓取'}
            </HoloButton>
            <HoloButton
              variant="primary"
              onClick={() => {
                setIsScraping(true)
                previewMutation.mutate()
              }}
              disabled={isScrapng}
              loading={isScrapng}
              icon={<Eye className="w-4 h-4" />}
            >
              {isScrapng ? '抓取中...' : '預覽抓取'}
            </HoloButton>
            <a
              href={`/api/v1/categories/${params.id}/export/excel`}
              className="inline-flex items-center px-4 py-2 text-sm font-medium rounded-xl gap-2
                bg-gradient-to-r from-emerald-500 to-green-500 text-white
                hover:from-emerald-400 hover:to-green-400
                shadow-lg shadow-emerald-500/25 hover:shadow-emerald-500/40
                border border-emerald-400/30 transition-all duration-200"
            >
              <Download className="w-4 h-4" />
              導出 Excel
            </a>
          </div>
        </div>

        {/* 智能抓取結果通知 */}
        {smartScrapeResult && (
          <HoloCard
            glowColor={smartScrapeResult.success ? 'green' : 'purple'}
            className={`p-4 ${smartScrapeResult.success ? 'bg-emerald-50/80' : 'bg-red-50/80'}`}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className={`p-2 rounded-xl ${smartScrapeResult.success ? 'bg-emerald-100' : 'bg-red-100'}`}>
                  <Zap className={`w-5 h-5 ${smartScrapeResult.success ? 'text-emerald-600' : 'text-red-600'}`} />
                </div>
                <div>
                  <p className={`font-medium ${smartScrapeResult.success ? 'text-emerald-800' : 'text-red-800'}`}>
                    {smartScrapeResult.message}
                  </p>
                  <p className="text-sm text-slate-600 mt-1">
                    新增 <span className="font-semibold text-cyan-600">{smartScrapeResult.new_products}</span> 個 |
                    更新 <span className="font-semibold text-cyan-600">{smartScrapeResult.updated_products}</span> 個 |
                    消耗 <span className="font-semibold text-violet-600">{smartScrapeResult.credits_used}</span> credits
                  </p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setSmartScrapeResult(null)}
                className="p-2 hover:bg-slate-200/50 rounded-lg transition-colors"
                title="關閉通知"
                aria-label="關閉通知"
              >
                <X className="w-4 h-4 text-slate-500" />
              </button>
            </div>
          </HoloCard>
        )}

        {/* 統計卡片 */}
        <StaggerContainer className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <DataMetric
            label="商品總數"
            value={stats?.total_products || 0}
            suffix={`個 (${stats?.available_products || 0} 有貨)`}
            icon={<Package className="w-5 h-5 text-cyan-600" />}
            color="cyan"
          />
          <DataMetric
            label="平均價格"
            value={stats?.avg_price ? Number(stats.avg_price) : 0}
            prefix="$"
            suffix={stats?.price_range ? ` (波動 $${Number(stats.price_range).toFixed(0)})` : ''}
            icon={<DollarSign className="w-5 h-5 text-green-600" />}
            color="green"
          />
          <DataMetric
            label="最低價"
            value={stats?.min_price ? Number(stats.min_price) : 0}
            prefix="$"
            suffix=" 類別最便宜"
            icon={<TrendingDown className="w-5 h-5 text-blue-600" />}
            color="blue"
          />
          <DataMetric
            label="品牌數量"
            value={stats?.brands_count || 0}
            suffix=" 不同品牌"
            icon={<BarChart3 className="w-5 h-5 text-purple-600" />}
            color="purple"
          />
        </StaggerContainer>

        {/* 圖表區域 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* 價格分佈 */}
          <HoloCard glowColor="blue">
            <HoloPanelHeader
              title="價格分佈"
              icon={<BarChart3 className="w-5 h-5" />}
            />
            <div className="p-6">
              {overview?.price_distribution && overview.price_distribution.length > 0 ? (
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={overview.price_distribution}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                    <XAxis dataKey="range" tick={{ fontSize: 12, fill: '#64748b' }} />
                    <YAxis tick={{ fontSize: 12, fill: '#64748b' }} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'rgba(255,255,255,0.95)',
                        border: '1px solid #e2e8f0',
                        borderRadius: '12px',
                        boxShadow: '0 4px 20px rgba(0,0,0,0.1)',
                      }}
                    />
                    <Bar dataKey="count" fill="url(#blueGradient)" radius={[6, 6, 0, 0]} />
                    <defs>
                      <linearGradient id="blueGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#06b6d4" />
                        <stop offset="100%" stopColor="#3b82f6" />
                      </linearGradient>
                    </defs>
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-[250px] flex items-center justify-center text-slate-400">
                  <div className="text-center">
                    <BarChart3 className="w-12 h-12 mx-auto mb-2 opacity-50" />
                    <p>暫無數據</p>
                  </div>
                </div>
              )}
            </div>
          </HoloCard>

          {/* 品牌比較 */}
          <HoloCard glowColor="green">
            <HoloPanelHeader
              title="品牌價格比較"
              icon={<DollarSign className="w-5 h-5" />}
            />
            <div className="p-6">
              {overview?.brand_comparison && overview.brand_comparison.length > 0 ? (
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={overview.brand_comparison.slice(0, 6)} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                    <XAxis type="number" tick={{ fontSize: 12, fill: '#64748b' }} />
                    <YAxis dataKey="brand" type="category" tick={{ fontSize: 11, fill: '#64748b' }} width={80} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'rgba(255,255,255,0.95)',
                        border: '1px solid #e2e8f0',
                        borderRadius: '12px',
                        boxShadow: '0 4px 20px rgba(0,0,0,0.1)',
                      }}
                    />
                    <Bar dataKey="avg_price" fill="url(#greenGradient)" radius={[0, 6, 6, 0]} />
                    <defs>
                      <linearGradient id="greenGradient" x1="0" y1="0" x2="1" y2="0">
                        <stop offset="0%" stopColor="#10b981" />
                        <stop offset="100%" stopColor="#22c55e" />
                      </linearGradient>
                    </defs>
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-[250px] flex items-center justify-center text-slate-400">
                  <div className="text-center">
                    <DollarSign className="w-12 h-12 mx-auto mb-2 opacity-50" />
                    <p>暫無數據</p>
                  </div>
                </div>
              )}
            </div>
          </HoloCard>
        </div>

        {/* 最優惠商品 */}
        {overview?.top_deals && overview.top_deals.length > 0 && (
          <HoloCard glowColor="purple">
            <HoloPanelHeader
              title="最優惠商品"
              subtitle="目前折扣最大的商品"
              icon={<TrendingDown className="w-5 h-5" />}
            />
            <div className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {overview.top_deals.slice(0, 6).map((deal, index) => (
                  <a
                    key={index}
                    href={deal.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="group relative p-4 rounded-xl border border-slate-200/60 bg-white/50
                      hover:border-cyan-300 hover:shadow-lg hover:shadow-cyan-500/10 transition-all duration-300"
                  >
                    <div className="flex items-start justify-between">
                      <h4 className="text-sm font-medium text-slate-800 line-clamp-2 group-hover:text-cyan-700 transition-colors">
                        {deal.name}
                      </h4>
                      <HoloBadge variant="error" size="sm">
                        -{deal.discount_percent?.toFixed(0)}%
                      </HoloBadge>
                    </div>
                    <div className="mt-3 flex items-baseline space-x-2">
                      <span className="text-xl font-bold bg-gradient-to-r from-cyan-600 to-blue-600 bg-clip-text text-transparent">
                        ${deal.price?.toFixed(0)}
                      </span>
                      {deal.original_price && (
                        <span className="text-sm text-slate-400 line-through">
                          ${deal.original_price.toFixed(0)}
                        </span>
                      )}
                    </div>
                    <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
                      <ExternalLink className="w-4 h-4 text-cyan-500" />
                    </div>
                  </a>
                ))}
              </div>
            </div>
          </HoloCard>
        )}

        {/* 商品價格歷史 */}
        {selectedProduct && priceHistory && (
          <HoloCard glowColor="cyan" scanLine>
            <HoloPanelHeader
              title={`價格趨勢: ${priceHistory.product_name}`}
              icon={<BarChart3 className="w-5 h-5" />}
              action={
                <HoloButton
                  variant="ghost"
                  size="sm"
                  onClick={() => setSelectedProduct(null)}
                  icon={<X className="w-4 h-4" />}
                >
                  關閉
                </HoloButton>
              }
            />
            <div className="p-6">
              {priceHistory.chart_data.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={priceHistory.chart_data}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                    <XAxis dataKey="date" tick={{ fontSize: 12, fill: '#64748b' }} />
                    <YAxis tick={{ fontSize: 12, fill: '#64748b' }} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'rgba(255,255,255,0.95)',
                        border: '1px solid #e2e8f0',
                        borderRadius: '12px',
                        boxShadow: '0 4px 20px rgba(0,0,0,0.1)',
                      }}
                    />
                    <Line
                      type="monotone"
                      dataKey="price"
                      stroke="url(#lineGradient)"
                      strokeWidth={3}
                      dot={{ r: 4, fill: '#06b6d4', strokeWidth: 2, stroke: '#fff' }}
                      activeDot={{ r: 6, fill: '#06b6d4', strokeWidth: 2, stroke: '#fff' }}
                    />
                    <defs>
                      <linearGradient id="lineGradient" x1="0" y1="0" x2="1" y2="0">
                        <stop offset="0%" stopColor="#06b6d4" />
                        <stop offset="100%" stopColor="#3b82f6" />
                      </linearGradient>
                    </defs>
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-[300px] flex items-center justify-center text-slate-400">
                  <div className="text-center">
                    <BarChart3 className="w-12 h-12 mx-auto mb-2 opacity-50" />
                    <p>暫無價格歷史數據</p>
                  </div>
                </div>
              )}
            </div>
          </HoloCard>
        )}

        {/* 商品列表 */}
        <HoloCard glowColor="cyan">
          <HoloPanelHeader
            title="商品列表"
            icon={<Package className="w-5 h-5" />}
            action={
              selectedProducts.size > 0 && (
                <HoloButton
                  variant="secondary"
                  size="sm"
                  onClick={() => {
                    if (confirm(`確定要刪除選中的 ${selectedProducts.size} 個商品嗎？`)) {
                      setIsDeleting(true)
                      bulkDeleteMutation.mutate(Array.from(selectedProducts))
                    }
                  }}
                  disabled={isDeleting}
                  loading={isDeleting}
                  icon={<Trash2 className="w-4 h-4" />}
                  className="!text-red-600 !border-red-200 hover:!bg-red-50"
                >
                  刪除選中 ({selectedProducts.size})
                </HoloButton>
              )
            }
          />
          {productsLoading ? (
            <div className="p-6 space-y-4">
              {[1, 2, 3, 4, 5].map((i) => (
                <div key={i} className="flex items-center space-x-4">
                  <HoloSkeleton width={20} height={20} variant="rectangular" />
                  <HoloSkeleton width={200} height={16} />
                  <HoloSkeleton width={80} height={16} className="ml-auto" />
                  <HoloSkeleton width={60} height={16} />
                  <HoloSkeleton width={50} height={24} variant="rectangular" className="rounded-full" />
                </div>
              ))}
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-slate-100">
                <thead className="bg-slate-50/50">
                  <tr>
                    <th className="px-4 py-3 text-left">
                      <button onClick={toggleSelectAll} className="hover:scale-110 transition-transform">
                        {products?.items && selectedProducts.size === products.items.length ? (
                          <CheckSquare className="w-5 h-5 text-cyan-600" />
                        ) : (
                          <Square className="w-5 h-5 text-slate-400" />
                        )}
                      </button>
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">商品名稱</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">品牌</th>
                    <th className="px-4 py-3 text-right text-xs font-semibold text-slate-500 uppercase tracking-wider">價格</th>
                    <th className="px-4 py-3 text-right text-xs font-semibold text-slate-500 uppercase tracking-wider">單位價</th>
                    <th className="px-4 py-3 text-center text-xs font-semibold text-slate-500 uppercase tracking-wider">狀態</th>
                    <th className="px-4 py-3 text-right text-xs font-semibold text-slate-500 uppercase tracking-wider">操作</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {products?.items.map((product) => (
                    <tr
                      key={product.id}
                      className={`transition-colors hover:bg-slate-50/80 ${selectedProducts.has(product.id) ? 'bg-cyan-50/50' : ''}`}
                    >
                      <td className="px-4 py-4">
                        <button
                          onClick={() => toggleProductSelection(product.id)}
                          className="hover:scale-110 transition-transform"
                        >
                          {selectedProducts.has(product.id) ? (
                            <CheckSquare className="w-5 h-5 text-cyan-600" />
                          ) : (
                            <Square className="w-5 h-5 text-slate-400" />
                          )}
                        </button>
                      </td>
                      <td className="px-4 py-4">
                        <div className="max-w-xs">
                          <p className="text-sm font-medium text-slate-800 truncate">{product.name}</p>
                          {product.sku && (
                            <p className="text-xs text-slate-500">SKU: {product.sku}</p>
                          )}
                        </div>
                      </td>
                      <td className="px-4 py-4 text-sm text-slate-500">
                        {product.brand || '-'}
                      </td>
                      <td className="px-4 py-4 text-right">
                        <div className="flex items-center justify-end gap-2">
                          <span className="text-sm font-semibold text-slate-800">
                            {product.price ? `$${Number(product.price).toFixed(0)}` : '-'}
                          </span>
                          {product.discount_percent && Number(product.discount_percent) > 0 && (
                            <HoloBadge variant="error" size="sm">
                              -{Number(product.discount_percent).toFixed(0)}%
                            </HoloBadge>
                          )}
                        </div>
                      </td>
                      <td className="px-4 py-4 text-right text-sm text-slate-500">
                        {product.unit_price ? `$${Number(product.unit_price).toFixed(2)}/${product.unit_type || 'unit'}` : '-'}
                      </td>
                      <td className="px-4 py-4 text-center">
                        <HoloBadge variant={product.is_available ? 'success' : 'error'} size="sm">
                          {product.is_available ? '有貨' : '缺貨'}
                        </HoloBadge>
                      </td>
                      <td className="px-4 py-4 text-right">
                        <div className="flex items-center justify-end space-x-1">
                          <button
                            onClick={() => setSelectedProduct(product.id)}
                            className="p-2 hover:bg-cyan-50 text-cyan-600 rounded-lg transition-all hover:scale-105"
                            title="查看價格趨勢"
                          >
                            <BarChart3 className="w-4 h-4" />
                          </button>
                          <a
                            href={product.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="p-2 hover:bg-slate-100 text-slate-600 rounded-lg transition-all hover:scale-105"
                            title="前往商品頁面"
                          >
                            <ExternalLink className="w-4 h-4" />
                          </a>
                          <button
                            onClick={() => {
                              if (confirm(`確定要刪除「${product.name}」嗎？`)) {
                                deleteProductMutation.mutate(product.id)
                              }
                            }}
                            className="p-2 hover:bg-red-50 text-red-500 rounded-lg transition-all hover:scale-105"
                            title="刪除商品"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          {products?.items.length === 0 && (
            <div className="py-16 text-center">
              <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-slate-100 flex items-center justify-center">
                <Package className="w-8 h-8 text-slate-400" />
              </div>
              <p className="text-slate-600 font-medium">此類別暫無商品</p>
              <p className="text-sm text-slate-400 mt-1">點擊「預覽抓取」獲取商品數據</p>
            </div>
          )}
        </HoloCard>
      </div>
    </PageTransition>
  )
}
