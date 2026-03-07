'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'
import { motion } from 'framer-motion'
import {
  Package,
  Building2,
  RefreshCw,
  Target,
  Globe,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { DashboardStats } from '@/components/competitors/dashboard-stats'
import { ProductComparisonCard } from '@/components/competitors/product-comparison-card'
import { MerchantOverviewCard } from '@/components/competitors/merchant-overview-card'

type ViewMode = 'products' | 'merchants'
type ScopeMode = 'mapped' | 'all'

export default function CompetitorsPage() {
  const [view, setView] = useState<ViewMode>('products')
  const [scope, setScope] = useState<ScopeMode>('mapped')

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

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-teal-50/30 px-3 py-4 sm:p-6">
      <div className="max-w-7xl mx-auto space-y-4 sm:space-y-6">

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
          <Button
            variant="outline"
            size="sm"
            onClick={handleRefresh}
            className="shrink-0 border-teal-200 text-teal-600 hover:bg-teal-50 hover:text-teal-700 hover:border-teal-300"
          >
            <RefreshCw className="w-4 h-4 sm:mr-1.5" />
            <span className="hidden sm:inline">刷新</span>
          </Button>
        </div>

        {/* ===== Stats Cards ===== */}
        <DashboardStats summary={summary} isLoading={summaryLoading} />

        {/* ===== View + Scope Toggles ===== */}
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-2">
          <div className="flex items-center gap-1 p-1 rounded-lg bg-white border border-gray-200 shadow-sm">
            <button
              onClick={() => setView('products')}
              className={cn(
                'flex-1 sm:flex-none flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-md text-sm transition-all',
                view === 'products'
                  ? 'bg-teal-500 text-white shadow-sm'
                  : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
              )}
            >
              <Package className="w-4 h-4" />
              商品視角
            </button>
            <button
              onClick={() => setView('merchants')}
              className={cn(
                'flex-1 sm:flex-none flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-md text-sm transition-all',
                view === 'merchants'
                  ? 'bg-teal-500 text-white shadow-sm'
                  : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
              )}
            >
              <Building2 className="w-4 h-4" />
              商戶視角
            </button>
          </div>

          {view === 'products' && (
            <div className="flex items-center gap-1 p-1 rounded-lg bg-white border border-gray-200 shadow-sm">
              <button
                onClick={() => setScope('mapped')}
                className={cn(
                  'flex-1 sm:flex-none flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-md text-xs transition-all',
                  scope === 'mapped'
                    ? 'bg-amber-500 text-white shadow-sm'
                    : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
                )}
              >
                <Target className="w-3.5 h-3.5" />
                自家競品
              </button>
              <button
                onClick={() => setScope('all')}
                className={cn(
                  'flex-1 sm:flex-none flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-md text-xs transition-all',
                  scope === 'all'
                    ? 'bg-amber-500 text-white shadow-sm'
                    : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
                )}
              >
                <Globe className="w-3.5 h-3.5" />
                全部生鮮
              </button>
            </div>
          )}
        </div>

        {/* ===== Content ===== */}
        <motion.div
          key={view}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.2 }}
        >
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
              ) : products?.items.length === 0 ? (
                <div className="text-center py-16 sm:py-20 text-gray-400">
                  <Package className="w-10 h-10 sm:w-12 sm:h-12 mx-auto mb-3 opacity-30" />
                  <p className="text-sm">未有商品比較數據</p>
                  <p className="text-xs mt-1">請先跑 competitor build（Line A）</p>
                </div>
              ) : (
                products?.items.map((item) => (
                  <ProductComparisonCard key={item.product.id} data={item} />
                ))
              )}
            </div>
          )}

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
              ) : merchants?.items.length === 0 ? (
                <div className="text-center py-16 sm:py-20 text-gray-400">
                  <Building2 className="w-10 h-10 sm:w-12 sm:h-12 mx-auto mb-3 opacity-30" />
                  <p className="text-sm">未有商戶數據</p>
                  <p className="text-xs mt-1">請先初始化商戶</p>
                </div>
              ) : (
                merchants?.items.map((item) => (
                  <MerchantOverviewCard key={item.competitor.id} data={item} />
                ))
              )}
            </div>
          )}
        </motion.div>
      </div>
    </div>
  )
}
