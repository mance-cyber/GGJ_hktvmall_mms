'use client'

// =============================================
// PriceTrend儀表板
// =============================================

import { useState } from 'react'
import {
  TrendingUp,
  AlertCircle,
  RefreshCw,
} from 'lucide-react'
import { useLocale } from '@/components/providers/locale-provider'
import {
  PageTransition,
  HoloCard,
  HoloSkeleton,
} from '@/components/ui/future-tech'
import { useProductsWithTrends, useProductPriceTrendWithDays } from './hooks/usePriceTrends'
import { TIME_RANGE_OPTIONS } from '@/lib/api/price-trends'
import {
  ProductSelector,
  TimeRangePicker,
  TrendKPICards,
  PriceTrendChart,
  PriceDataTable,
} from './components'

export default function TrendsPage() {
  const { t } = useLocale()
  // State
  const [selectedProductId, setSelectedProductId] = useState<string | null>(null)
  const [selectedDays, setSelectedDays] = useState(30)

  // FetchProductList
  const {
    data: productsData,
    isLoading: isLoadingProducts,
    error: productsError,
  } = useProductsWithTrends()

  // FetchPriceTrend
  const {
    data: trendData,
    isLoading: isLoadingTrend,
    error: trendError,
    refetch: refetchTrend,
  } = useProductPriceTrendWithDays(selectedProductId, selectedDays)

  // Loading state
  if (isLoadingProducts) {
    return (
      <PageTransition>
        <div className="space-y-6">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-500 text-white">
              <TrendingUp className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{t('trends.title')}</h1>
              <p className="text-gray-500 text-sm">{t('trends.subtitle')}</p>
            </div>
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
            {[...Array(4)].map((_, i) => (
              <HoloSkeleton key={i} variant="rectangular" height={100} />
            ))}
          </div>
          <HoloSkeleton variant="rectangular" height={400} />
        </div>
      </PageTransition>
    )
  }

  // ErrorState
  if (productsError) {
    return (
      <PageTransition>
        <div className="space-y-6">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-500 text-white">
              <TrendingUp className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{t('trends.title')}</h1>
            </div>
          </div>
          <HoloCard className="p-6 border-red-200 bg-red-50/50">
            <div className="flex items-center text-red-600">
              <AlertCircle className="w-5 h-5 mr-3" />
              <span className="font-medium">{t('trends.load_error')}</span>
            </div>
          </HoloCard>
        </div>
      </PageTransition>
    )
  }

  // 無ProductState
  if (!productsData?.products || productsData.products.length === 0) {
    return (
      <PageTransition>
        <div className="space-y-6">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-500 text-white">
              <TrendingUp className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{t('trends.title')}</h1>
              <p className="text-gray-500 text-sm">{t('trends.subtitle')}</p>
            </div>
          </div>
          <HoloCard className="p-12 text-center">
            <TrendingUp className="w-16 h-16 text-emerald-500 mx-auto mb-4 opacity-50" />
            <h2 className="text-xl font-semibold text-gray-700 mb-2">{t('trends.empty_title')}</h2>
            <p className="text-gray-500">
              {t('trends.empty_desc')}
            </p>
          </HoloCard>
        </div>
      </PageTransition>
    )
  }

  return (
    <PageTransition>
      <div className="space-y-6">
        {/* ========== Page title ========== */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-500 text-white">
              <TrendingUp className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{t('trends.title')}</h1>
              <p className="text-gray-500 text-sm">{t('trends.subtitle')}</p>
            </div>
          </div>
          {selectedProductId && (
            <button
              onClick={() => refetchTrend()}
              disabled={isLoadingTrend}
              className="flex items-center gap-2 px-3 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <RefreshCw className={`w-4 h-4 ${isLoadingTrend ? 'animate-spin' : ''}`} />
              {t('trends.refresh')}
            </button>
          )}
        </div>

        {/* ========== Filter控制 ========== */}
        <div className="relative z-[9999]">
          <div className="flex flex-col sm:flex-row gap-4 p-4 bg-white/70 backdrop-blur-xl border border-white/60 rounded-2xl shadow-[0_8px_32px_rgba(0,0,0,0.08)]">
            <div className="flex-1">
              <ProductSelector
                products={productsData.products}
                selectedId={selectedProductId}
                onSelect={setSelectedProductId}
              />
            </div>
            <div className="sm:w-auto">
              <TimeRangePicker
                options={TIME_RANGE_OPTIONS}
                selectedDays={selectedDays}
                onSelect={setSelectedDays}
              />
            </div>
          </div>
        </div>

        {/* ========== ContentArea ========== */}
        {!selectedProductId ? (
          <HoloCard className="p-12 text-center">
            <TrendingUp className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-gray-700 mb-2">{t('trends.select_product')}</h2>
            <p className="text-gray-500">
              {t('trends.select_hint')}
            </p>
          </HoloCard>
        ) : isLoadingTrend ? (
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {[...Array(4)].map((_, i) => (
                <HoloSkeleton key={i} variant="rectangular" height={100} />
              ))}
            </div>
            <HoloSkeleton variant="rectangular" height={400} />
            <HoloSkeleton variant="rectangular" height={300} />
          </div>
        ) : trendError ? (
          <HoloCard className="p-6 border-red-200 bg-red-50/50">
            <div className="flex items-center text-red-600">
              <AlertCircle className="w-5 h-5 mr-3" />
              <span className="font-medium">{t('trends.trend_load_error')}</span>
            </div>
          </HoloCard>
        ) : trendData ? (
          <>
            {/* KPI Card */}
            <TrendKPICards summary={trendData.summary} />

            {/* PriceTrendChart */}
            <HoloCard className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">{t('trends.section_chart')}</h3>
              <PriceTrendChart
                trends={trendData.trends}
                ownProduct={trendData.own_product}
                competitors={trendData.competitors}
              />
            </HoloCard>

            {/* DataTable */}
            <HoloCard className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">{t('trends.section_table')}</h3>
              <PriceDataTable
                trends={trendData.trends}
                ownProduct={trendData.own_product}
                competitors={trendData.competitors}
              />
            </HoloCard>
          </>
        ) : null}
      </div>
    </PageTransition>
  )
}
