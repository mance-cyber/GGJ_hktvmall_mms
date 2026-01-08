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

  if (categoryLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="w-8 h-8 animate-spin text-blue-500" />
      </div>
    )
  }

  // 預覽審核界面
  if (previewMode && previewData) {
    return (
      <div className="space-y-6">
        {/* 預覽標題 */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button
              onClick={cancelPreview}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <ArrowLeft className="w-5 h-5 text-gray-600" />
            </button>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">審核抓取結果</h1>
              <p className="text-gray-500 mt-1">
                已抓取 {previewData.total_scraped} 個商品，請選擇要保存的商品
              </p>
            </div>
          </div>
          <div className="flex space-x-3">
            <button
              onClick={cancelPreview}
              className="flex items-center px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <X className="w-4 h-4 mr-2" />
              取消
            </button>
            <button
              onClick={() => {
                setIsConfirming(true)
                confirmMutation.mutate()
              }}
              disabled={isConfirming || selectedPreviewIndices.size === 0}
              className="flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50"
            >
              {isConfirming ? (
                <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <Check className="w-4 h-4 mr-2" />
              )}
              確認保存 ({selectedPreviewIndices.size})
            </button>
          </div>
        </div>

        {/* 錯誤提示 */}
        {previewData.errors.length > 0 && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <div className="flex items-start">
              <AlertTriangle className="w-5 h-5 text-yellow-600 mt-0.5 mr-3" />
              <div>
                <h4 className="text-sm font-medium text-yellow-800">部分抓取失敗</h4>
                <ul className="mt-2 text-sm text-yellow-700 space-y-1">
                  {previewData.errors.slice(0, 3).map((err, i) => (
                    <li key={i}>{err}</li>
                  ))}
                  {previewData.errors.length > 3 && (
                    <li>還有 {previewData.errors.length - 3} 個錯誤...</li>
                  )}
                </ul>
              </div>
            </div>
          </div>
        )}

        {/* 預覽商品列表 */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
            <h3 className="text-lg font-semibold text-gray-900">
              待審核商品 ({previewData.products.length})
            </h3>
            <button
              onClick={togglePreviewSelectAll}
              className="text-sm text-blue-600 hover:text-blue-800"
            >
              {selectedPreviewIndices.size === previewData.products.length ? '取消全選' : '全選'}
            </button>
          </div>
          <div className="divide-y divide-gray-200 max-h-[600px] overflow-y-auto">
            {previewData.products.map((product, index) => (
              <div
                key={index}
                className={`px-6 py-4 flex items-center space-x-4 hover:bg-gray-50 ${
                  selectedPreviewIndices.has(index) ? 'bg-blue-50' : ''
                }`}
              >
                <button
                  onClick={() => togglePreviewSelection(index)}
                  className="flex-shrink-0"
                >
                  {selectedPreviewIndices.has(index) ? (
                    <CheckSquare className="w-5 h-5 text-blue-600" />
                  ) : (
                    <Square className="w-5 h-5 text-gray-400" />
                  )}
                </button>
                {product.image_url && (
                  <img
                    src={product.image_url}
                    alt={product.name}
                    className="w-16 h-16 object-cover rounded-lg flex-shrink-0"
                  />
                )}
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">{product.name}</p>
                  <p className="text-xs text-gray-500">
                    {product.brand || '未知品牌'} {product.sku && `| SKU: ${product.sku}`}
                  </p>
                </div>
                <div className="text-right flex-shrink-0">
                  <p className="text-sm font-bold text-blue-600">
                    {product.price ? `$${Number(product.price).toFixed(0)}` : '-'}
                  </p>
                  {product.discount_percent && Number(product.discount_percent) > 0 && (
                    <span className="text-xs text-red-600">
                      -{Number(product.discount_percent).toFixed(0)}%
                    </span>
                  )}
                </div>
                <a
                  href={product.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="p-2 hover:bg-gray-100 rounded-lg transition-colors flex-shrink-0"
                >
                  <ExternalLink className="w-4 h-4 text-gray-500" />
                </a>
              </div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* 頁面標題 */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link
            href="/categories"
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ArrowLeft className="w-5 h-5 text-gray-600" />
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{category?.name}</h1>
            <p className="text-gray-500 mt-1">{category?.description || '類別商品監測'}</p>
          </div>
        </div>
        <div className="flex items-center space-x-3">
          <QuotaDisplay compact />
          <button
            onClick={() => {
              setIsSmartScraping(true)
              smartScrapeMutation.mutate()
            }}
            disabled={isSmartScraping}
            className="flex items-center px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50"
            title="使用緩存 + 增量更新，節省 API 配額"
          >
            {isSmartScraping ? (
              <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
            ) : (
              <Zap className="w-4 h-4 mr-2" />
            )}
            {isSmartScraping ? '智能更新中...' : '智能抓取'}
          </button>
          <button
            onClick={() => {
              setIsScraping(true)
              previewMutation.mutate()
            }}
            disabled={isScrapng}
            className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
          >
            {isScrapng ? (
              <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
            ) : (
              <Eye className="w-4 h-4 mr-2" />
            )}
            {isScrapng ? '抓取中...' : '預覽抓取'}
          </button>
          <a
            href={`/api/v1/categories/${params.id}/export/excel`}
            className="flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
          >
            <Download className="w-4 h-4 mr-2" />
            導出 Excel
          </a>
        </div>
      </div>

      {/* 智能抓取結果通知 */}
      {smartScrapeResult && (
        <div className={`rounded-lg p-4 ${smartScrapeResult.success ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'}`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Zap className={`w-5 h-5 ${smartScrapeResult.success ? 'text-green-600' : 'text-red-600'}`} />
              <div>
                <p className={`font-medium ${smartScrapeResult.success ? 'text-green-800' : 'text-red-800'}`}>
                  {smartScrapeResult.message}
                </p>
                <p className="text-sm text-gray-600 mt-1">
                  新增 {smartScrapeResult.new_products} 個 | 更新 {smartScrapeResult.updated_products} 個 |
                  消耗 <span className="font-medium text-purple-600">{smartScrapeResult.credits_used}</span> credits
                </p>
              </div>
            </div>
            <button
              type="button"
              onClick={() => setSmartScrapeResult(null)}
              className="p-1 hover:bg-gray-200 rounded"
              title="關閉通知"
              aria-label="關閉通知"
            >
              <X className="w-4 h-4 text-gray-500" />
            </button>
          </div>
        </div>
      )}

      {/* 統計卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="商品總數"
          value={stats?.total_products || 0}
          subtitle={`${stats?.available_products || 0} 個有貨`}
          icon={Package}
          color="blue"
        />
        <StatCard
          title="平均價格"
          value={stats?.avg_price ? `$${Number(stats.avg_price).toFixed(0)}` : '-'}
          subtitle={stats?.price_range ? `波動 $${Number(stats.price_range).toFixed(0)}` : '-'}
          icon={DollarSign}
          color="green"
        />
        <StatCard
          title="最低價"
          value={stats?.min_price ? `$${Number(stats.min_price).toFixed(0)}` : '-'}
          subtitle="類別最便宜"
          icon={TrendingDown}
          color="blue"
        />
        <StatCard
          title="品牌數量"
          value={stats?.brands_count || 0}
          subtitle="不同品牌"
          icon={BarChart3}
          color="purple"
        />
      </div>

      {/* 圖表區域 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 價格分佈 */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">價格分佈</h3>
          {overview?.price_distribution && overview.price_distribution.length > 0 ? (
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={overview.price_distribution}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="range" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip />
                <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-[250px] flex items-center justify-center text-gray-400">
              暫無數據
            </div>
          )}
        </div>

        {/* 品牌比較 */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">品牌價格比較</h3>
          {overview?.brand_comparison && overview.brand_comparison.length > 0 ? (
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={overview.brand_comparison.slice(0, 6)} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" tick={{ fontSize: 12 }} />
                <YAxis dataKey="brand" type="category" tick={{ fontSize: 11 }} width={80} />
                <Tooltip />
                <Bar dataKey="avg_price" fill="#10b981" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-[250px] flex items-center justify-center text-gray-400">
              暫無數據
            </div>
          )}
        </div>
      </div>

      {/* 最優惠商品 */}
      {overview?.top_deals && overview.top_deals.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">最優惠商品</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {overview.top_deals.slice(0, 6).map((deal, index) => (
              <a
                key={index}
                href={deal.url}
                target="_blank"
                rel="noopener noreferrer"
                className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 hover:shadow-sm transition-all"
              >
                <div className="flex items-start justify-between">
                  <h4 className="text-sm font-medium text-gray-900 line-clamp-2">{deal.name}</h4>
                  <span className="ml-2 px-2 py-0.5 bg-red-100 text-red-700 text-xs font-medium rounded">
                    -{deal.discount_percent?.toFixed(0)}%
                  </span>
                </div>
                <div className="mt-2 flex items-baseline space-x-2">
                  <span className="text-lg font-bold text-blue-600">${deal.price?.toFixed(0)}</span>
                  {deal.original_price && (
                    <span className="text-sm text-gray-400 line-through">
                      ${deal.original_price.toFixed(0)}
                    </span>
                  )}
                </div>
              </a>
            ))}
          </div>
        </div>
      )}

      {/* 商品價格歷史 */}
      {selectedProduct && priceHistory && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">
              價格趨勢: {priceHistory.product_name}
            </h3>
            <button
              onClick={() => setSelectedProduct(null)}
              className="text-gray-400 hover:text-gray-600"
            >
              關閉
            </button>
          </div>
          {priceHistory.chart_data.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={priceHistory.chart_data}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip />
                <Line type="monotone" dataKey="price" stroke="#3b82f6" strokeWidth={2} dot={{ r: 4 }} />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-[300px] flex items-center justify-center text-gray-400">
              暫無價格歷史數據
            </div>
          )}
        </div>
      )}

      {/* 商品列表 */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900">商品列表</h3>
          {selectedProducts.size > 0 && (
            <button
              onClick={() => {
                if (confirm(`確定要刪除選中的 ${selectedProducts.size} 個商品嗎？`)) {
                  setIsDeleting(true)
                  bulkDeleteMutation.mutate(Array.from(selectedProducts))
                }
              }}
              disabled={isDeleting}
              className="flex items-center px-3 py-1.5 bg-red-600 text-white text-sm rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50"
            >
              {isDeleting ? (
                <RefreshCw className="w-4 h-4 mr-1 animate-spin" />
              ) : (
                <Trash2 className="w-4 h-4 mr-1" />
              )}
              刪除選中 ({selectedProducts.size})
            </button>
          )}
        </div>
        {productsLoading ? (
          <div className="flex items-center justify-center py-12">
            <RefreshCw className="w-6 h-6 animate-spin text-blue-500" />
          </div>
        ) : (
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left">
                  <button onClick={toggleSelectAll}>
                    {products?.items && selectedProducts.size === products.items.length ? (
                      <CheckSquare className="w-5 h-5 text-blue-600" />
                    ) : (
                      <Square className="w-5 h-5 text-gray-400" />
                    )}
                  </button>
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">商品名稱</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">品牌</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">價格</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">單位價</th>
                <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">狀態</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">操作</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {products?.items.map((product) => (
                <tr key={product.id} className={`hover:bg-gray-50 ${selectedProducts.has(product.id) ? 'bg-blue-50' : ''}`}>
                  <td className="px-4 py-4">
                    <button onClick={() => toggleProductSelection(product.id)}>
                      {selectedProducts.has(product.id) ? (
                        <CheckSquare className="w-5 h-5 text-blue-600" />
                      ) : (
                        <Square className="w-5 h-5 text-gray-400" />
                      )}
                    </button>
                  </td>
                  <td className="px-4 py-4">
                    <div className="max-w-xs">
                      <p className="text-sm font-medium text-gray-900 truncate">{product.name}</p>
                      {product.sku && (
                        <p className="text-xs text-gray-500">SKU: {product.sku}</p>
                      )}
                    </div>
                  </td>
                  <td className="px-4 py-4 text-sm text-gray-500">
                    {product.brand || '-'}
                  </td>
                  <td className="px-4 py-4 text-right">
                    <div>
                      <span className="text-sm font-medium text-gray-900">
                        {product.price ? `$${Number(product.price).toFixed(0)}` : '-'}
                      </span>
                      {product.discount_percent && Number(product.discount_percent) > 0 && (
                        <span className="ml-2 text-xs text-red-600">
                          -{Number(product.discount_percent).toFixed(0)}%
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="px-4 py-4 text-right text-sm text-gray-500">
                    {product.unit_price ? `$${Number(product.unit_price).toFixed(2)}/${product.unit_type || 'unit'}` : '-'}
                  </td>
                  <td className="px-4 py-4 text-center">
                    <span
                      className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                        product.is_available
                          ? 'bg-green-100 text-green-800'
                          : 'bg-red-100 text-red-800'
                      }`}
                    >
                      {product.is_available ? '有貨' : '缺貨'}
                    </span>
                  </td>
                  <td className="px-4 py-4 text-right">
                    <div className="flex items-center justify-end space-x-1">
                      <button
                        onClick={() => setSelectedProduct(product.id)}
                        className="p-1.5 hover:bg-blue-50 text-blue-600 rounded transition-colors"
                        title="查看價格趨勢"
                      >
                        <BarChart3 className="w-4 h-4" />
                      </button>
                      <a
                        href={product.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="p-1.5 hover:bg-gray-100 text-gray-600 rounded transition-colors"
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
                        className="p-1.5 hover:bg-red-50 text-red-600 rounded transition-colors"
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
        )}
        {products?.items.length === 0 && (
          <div className="py-12 text-center text-gray-500">
            <Package className="w-12 h-12 mx-auto text-gray-300 mb-3" />
            <p>此類別暫無商品</p>
            <p className="text-sm mt-1">點擊「預覽抓取」獲取商品數據</p>
          </div>
        )}
      </div>
    </div>
  )
}

function StatCard({
  title,
  value,
  subtitle,
  icon: Icon,
  color,
}: {
  title: string
  value: string | number
  subtitle: string
  icon: React.ElementType
  color: 'blue' | 'green' | 'red' | 'purple'
}) {
  const colorClasses = {
    blue: 'bg-blue-50 text-blue-600',
    green: 'bg-green-50 text-green-600',
    red: 'bg-red-50 text-red-600',
    purple: 'bg-purple-50 text-purple-600',
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-500">{title}</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
          <p className="text-sm text-gray-500 mt-1">{subtitle}</p>
        </div>
        <div className={`p-3 rounded-lg ${colorClasses[color]}`}>
          <Icon className="w-6 h-6" />
        </div>
      </div>
    </div>
  )
}
