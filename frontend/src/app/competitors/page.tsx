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

  // ========== Data queries ==========

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
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 p-6">
      <div className="max-w-7xl mx-auto space-y-6">

        {/* ===== Header ===== */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
              <span className="text-cyan-400">⚔️</span> 競品監測 Dashboard
            </h1>
            <p className="text-sm text-slate-500 mt-1">
              追蹤 {summary?.total_competitors || '...'} 間商戶、{summary?.total_tracked_products || '...'} 件商品
            </p>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={handleRefresh}
            className="border-slate-700 text-slate-400 hover:text-slate-200"
          >
            <RefreshCw className="w-4 h-4 mr-1.5" />
            刷新
          </Button>
        </div>

        {/* ===== Stats Cards ===== */}
        <DashboardStats summary={summary} isLoading={summaryLoading} />

        {/* ===== View + Scope Toggles ===== */}
        <div className="flex items-center justify-between">
          {/* View toggle */}
          <div className="flex items-center gap-1 p-1 rounded-lg bg-slate-800/50 border border-slate-800">
            <button
              onClick={() => setView('products')}
              className={cn(
                'flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm transition-all',
                view === 'products'
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30'
                  : 'text-slate-400 hover:text-slate-300'
              )}
            >
              <Package className="w-4 h-4" />
              商品視角
            </button>
            <button
              onClick={() => setView('merchants')}
              className={cn(
                'flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm transition-all',
                view === 'merchants'
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30'
                  : 'text-slate-400 hover:text-slate-300'
              )}
            >
              <Building2 className="w-4 h-4" />
              商戶視角
            </button>
          </div>

          {/* Scope toggle (only for product view) */}
          {view === 'products' && (
            <div className="flex items-center gap-1 p-1 rounded-lg bg-slate-800/50 border border-slate-800">
              <button
                onClick={() => setScope('mapped')}
                className={cn(
                  'flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs transition-all',
                  scope === 'mapped'
                    ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                    : 'text-slate-400 hover:text-slate-300'
                )}
              >
                <Target className="w-3.5 h-3.5" />
                自家競品
              </button>
              <button
                onClick={() => setScope('all')}
                className={cn(
                  'flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs transition-all',
                  scope === 'all'
                    ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                    : 'text-slate-400 hover:text-slate-300'
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
            <div className="space-y-2">
              {productsLoading ? (
                Array.from({ length: 5 }).map((_, i) => (
                  <div key={i} className="rounded-xl border border-slate-800 p-4 animate-pulse">
                    <div className="flex items-center gap-3">
                      <div className="h-5 bg-slate-800 rounded w-12" />
                      <div className="h-5 bg-slate-800 rounded w-48" />
                      <div className="h-5 bg-slate-800 rounded w-16" />
                    </div>
                  </div>
                ))
              ) : products?.items.length === 0 ? (
                <div className="text-center py-20 text-slate-500">
                  <Package className="w-12 h-12 mx-auto mb-3 opacity-30" />
                  <p>未有商品比較數據</p>
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
            <div className="space-y-2">
              {merchantsLoading ? (
                Array.from({ length: 5 }).map((_, i) => (
                  <div key={i} className="rounded-xl border border-slate-800 p-4 animate-pulse">
                    <div className="flex items-center gap-3">
                      <div className="h-5 bg-slate-800 rounded w-16" />
                      <div className="h-5 bg-slate-800 rounded w-40" />
                      <div className="h-5 bg-slate-800 rounded w-24" />
                    </div>
                  </div>
                ))
              ) : merchants?.items.length === 0 ? (
                <div className="text-center py-20 text-slate-500">
                  <Building2 className="w-12 h-12 mx-auto mb-3 opacity-30" />
                  <p>未有商戶數據</p>
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
