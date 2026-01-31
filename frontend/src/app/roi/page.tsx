// =============================================
// ROI 儀表板頁面
// 展示 GoGoJap 為用戶創造的價值
// =============================================

'use client'

import { useState } from 'react'
import { TrendingUp, Brain, Eye, BarChart3 } from 'lucide-react'
import { HoloCard } from '@/components/ui/future-tech'
import { ROISummaryCards } from './components/ROISummaryCards'
import { ROITrendChart } from './components/ROITrendChart'
import { TimeRangeSelector } from './components/TimeRangeSelector'
import { PricingImpactTable } from './components/PricingImpactTable'
import { CompetitorValueCard } from './components/CompetitorValueCard'
import type { ROIPeriod } from '@/lib/api/roi'

export default function ROIDashboardPage() {
  const [period, setPeriod] = useState<ROIPeriod>('month')

  // 根據 period 計算趨勢天數
  const getTrendDays = (p: ROIPeriod): number => {
    switch (p) {
      case 'today': return 1
      case 'week': return 7
      case 'month': return 30
      case 'quarter': return 90
      default: return 30
    }
  }

  return (
    <div className="space-y-6 p-6">
      {/* 頁面標題 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <TrendingUp className="w-7 h-7 text-green-500" />
            投資回報分析
          </h1>
          <p className="text-gray-500 mt-1">GoGoJap 幫你賺了多少錢</p>
        </div>

        {/* 時間範圍選擇 */}
        <TimeRangeSelector value={period} onChange={setPeriod} />
      </div>

      {/* KPI 卡片 */}
      <ROISummaryCards period={period} />

      {/* 趨勢圖表 */}
      <HoloCard className="p-6">
        <div className="flex items-center gap-2 mb-4">
          <BarChart3 className="w-5 h-5 text-gray-400" />
          <h2 className="text-lg font-semibold text-gray-900">價值趨勢</h2>
        </div>
        <ROITrendChart days={getTrendDays(period)} />
      </HoloCard>

      {/* 雙列佈局 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 左側: AI 改價影響 */}
        <HoloCard className="p-6">
          <div className="flex items-center gap-2 mb-4">
            <Brain className="w-5 h-5 text-purple-500" />
            <h2 className="text-lg font-semibold text-gray-900">AI 改價影響</h2>
          </div>
          <PricingImpactTable />
        </HoloCard>

        {/* 右側: 競品監測價值 */}
        <HoloCard className="p-6">
          <div className="flex items-center gap-2 mb-4">
            <Eye className="w-5 h-5 text-cyan-500" />
            <h2 className="text-lg font-semibold text-gray-900">競品監測價值</h2>
          </div>
          <CompetitorValueCard period={period} />
        </HoloCard>
      </div>

      {/* 頁腳說明 */}
      <div className="text-center text-xs text-gray-400 py-4">
        <p>ROI 計算基於 AI 改價提案、競品價格告警等數據進行估算</p>
        <p className="mt-1">實際收益可能因市場變化而有所不同</p>
      </div>
    </div>
  )
}
