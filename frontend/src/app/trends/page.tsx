'use client'

// =============================================
// 價格趨勢儀表板
// =============================================

import { useState } from 'react'
import {
  TrendingUp,
  AlertCircle,
  RefreshCw,
} from 'lucide-react'
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
  // 狀態
  const [selectedProductId, setSelectedProductId] = useState<string | null>(null)
  const [selectedDays, setSelectedDays] = useState(30)

  // 獲取產品列表
  const {
    data: productsData,
    isLoading: isLoadingProducts,
    error: productsError,
  } = useProductsWithTrends()

  // 獲取價格趨勢
  const {
    data: trendData,
    isLoading: isLoadingTrend,
    error: trendError,
    refetch: refetchTrend,
  } = useProductPriceTrendWithDays(selectedProductId, selectedDays)

  // 加載狀態
  if (isLoadingProducts) {
    return (
      <PageTransition>
        <div className="space-y-6">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-500 text-white">
              <TrendingUp className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">價格趨勢</h1>
              <p className="text-gray-500 text-sm">自家產品 vs 競爭對手價格對比</p>
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

  // 錯誤狀態
  if (productsError) {
    return (
      <PageTransition>
        <div className="space-y-6">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-500 text-white">
              <TrendingUp className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">價格趨勢</h1>
            </div>
          </div>
          <HoloCard className="p-6 border-red-200 bg-red-50/50">
            <div className="flex items-center text-red-600">
              <AlertCircle className="w-5 h-5 mr-3" />
              <span className="font-medium">無法載入產品數據，請稍後再試。</span>
            </div>
          </HoloCard>
        </div>
      </PageTransition>
    )
  }

  // 無產品狀態
  if (!productsData?.products || productsData.products.length === 0) {
    return (
      <PageTransition>
        <div className="space-y-6">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-500 text-white">
              <TrendingUp className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">價格趨勢</h1>
              <p className="text-gray-500 text-sm">自家產品 vs 競爭對手價格對比</p>
            </div>
          </div>
          <HoloCard className="p-12 text-center">
            <TrendingUp className="w-16 h-16 text-emerald-500 mx-auto mb-4 opacity-50" />
            <h2 className="text-xl font-semibold text-gray-700 mb-2">暫無數據</h2>
            <p className="text-gray-500">
              請先添加產品並關聯競爭對手，才能查看價格趨勢。
            </p>
          </HoloCard>
        </div>
      </PageTransition>
    )
  }

  return (
    <PageTransition>
      <div className="space-y-6">
        {/* ========== 頁面標題 ========== */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-500 text-white">
              <TrendingUp className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">價格趨勢</h1>
              <p className="text-gray-500 text-sm">自家產品 vs 競爭對手價格對比</p>
            </div>
          </div>
          {selectedProductId && (
            <button
              onClick={() => refetchTrend()}
              disabled={isLoadingTrend}
              className="flex items-center gap-2 px-3 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <RefreshCw className={`w-4 h-4 ${isLoadingTrend ? 'animate-spin' : ''}`} />
              重新整理
            </button>
          )}
        </div>

        {/* ========== 篩選控制 ========== */}
        <div className="flex flex-col sm:flex-row gap-4 p-4 bg-white/70 backdrop-blur-xl border border-white/60 rounded-2xl shadow-[0_8px_32px_rgba(0,0,0,0.08)] overflow-visible">
          <div className="flex-1 relative z-50">
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

        {/* ========== 內容區域 ========== */}
        {!selectedProductId ? (
          <HoloCard className="p-12 text-center">
            <TrendingUp className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-gray-700 mb-2">請選擇產品</h2>
            <p className="text-gray-500">
              從上方下拉選單選擇一個產品，查看價格趨勢分析。
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
              <span className="font-medium">無法載入趨勢數據，請稍後再試。</span>
            </div>
          </HoloCard>
        ) : trendData ? (
          <>
            {/* KPI 卡片 */}
            <TrendKPICards summary={trendData.summary} />

            {/* 價格趨勢圖表 */}
            <HoloCard className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">價格走勢</h3>
              <PriceTrendChart
                trends={trendData.trends}
                ownProduct={trendData.own_product}
                competitors={trendData.competitors}
              />
            </HoloCard>

            {/* 數據表格 */}
            <HoloCard className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">詳細數據</h3>
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
