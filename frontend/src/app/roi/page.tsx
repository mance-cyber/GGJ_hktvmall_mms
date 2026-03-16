// =============================================
// ROI Dashboard Page
// Showcase the value GoGoJap creates for users
// =============================================

'use client'

import { useState } from 'react'
import { useLocale } from '@/components/providers/locale-provider'
import { TrendingUp, Brain, Eye, BarChart3 } from 'lucide-react'
import { HoloCard } from '@/components/ui/future-tech'
import { ROISummaryCards } from './components/ROISummaryCards'
import { ROITrendChart } from './components/ROITrendChart'
import { TimeRangeSelector } from './components/TimeRangeSelector'
import { PricingImpactTable } from './components/PricingImpactTable'
import { CompetitorValueCard } from './components/CompetitorValueCard'
import type { ROIPeriod } from '@/lib/api/roi'

export default function ROIDashboardPage() {
  const { t } = useLocale()
  const [period, setPeriod] = useState<ROIPeriod>('month')

  // Calculate trend days based on period

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
      {/* Page Title */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <TrendingUp className="w-7 h-7 text-green-500" />
            {t('roi.title')}
          </h1>
          <p className="text-gray-500 mt-1">{t('roi.subtitle')}</p>
        </div>

        {/* Time Range Selector */}
        <TimeRangeSelector value={period} onChange={setPeriod} />
      </div>

      {/* KPI Cards */}
      <ROISummaryCards period={period} />

      {/* Trend Chart */}
      <HoloCard className="p-6">
        <div className="flex items-center gap-2 mb-4">
          <BarChart3 className="w-5 h-5 text-gray-400" />
          <h2 className="text-lg font-semibold text-gray-900">{t('roi.value_trend')}</h2>
        </div>
        <ROITrendChart days={getTrendDays(period)} />
      </HoloCard>

      {/* Two-Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left: AI Pricing Impact */}
        <HoloCard className="p-6">
          <div className="flex items-center gap-2 mb-4">
            <Brain className="w-5 h-5 text-purple-500" />
            <h2 className="text-lg font-semibold text-gray-900">{t('roi.pricing_impact')}</h2>
          </div>
          <PricingImpactTable />
        </HoloCard>

        {/* Right: Competitor Monitoring Value */}
        <HoloCard className="p-6">
          <div className="flex items-center gap-2 mb-4">
            <Eye className="w-5 h-5 text-cyan-500" />
            <h2 className="text-lg font-semibold text-gray-900">{t('roi.competitor_value')}</h2>
          </div>
          <CompetitorValueCard period={period} />
        </HoloCard>
      </div>

      {/* Footer Notes */}
      <div className="text-center text-xs text-gray-400 py-4">
        <p>{t('roi.footer_note1')}</p>
        <p className="mt-1">{t('roi.footer_note2')}</p>
      </div>
    </div>
  )
}
