// =============================================
// Trend KPI Card組items
// =============================================

'use client'

import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  Activity,
  Target,
  BarChart3,
} from 'lucide-react'
import { HoloCard } from '@/components/ui/future-tech'
import type { TrendSummary } from '@/lib/api/price-trends'

interface TrendKPICardsProps {
  summary: TrendSummary
}

export function TrendKPICards({ summary }: TrendKPICardsProps) {
  // Format化Percentage
  const formatPercent = (value: number | null) => {
    if (value === null) return '--'
    const sign = value > 0 ? '+' : ''
    return `${sign}${value.toFixed(1)}%`
  }

  // Format化Price
  const formatPrice = (value: number | null) => {
    if (value === null) return '--'
    return `$${Number(value).toLocaleString()}`
  }

  // KPI CardData
  const kpis = [
    {
      title: '當前價差',
      value: formatPercent(summary.price_gap_current),
      description: '與競爭Competitor平均PriceCompare',
      icon: Target,
      color:
        summary.price_gap_current === null
          ? 'gray'
          : summary.price_gap_current > 0
          ? 'red'
          : summary.price_gap_current < 0
          ? 'green'
          : 'gray',
      trend: summary.price_gap_current,
    },
    {
      title: '平均價差',
      value: formatPercent(summary.price_gap_avg),
      description: '期間內平均Price差異',
      icon: BarChart3,
      color:
        summary.price_gap_avg === null
          ? 'gray'
          : summary.price_gap_avg > 0
          ? 'red'
          : summary.price_gap_avg < 0
          ? 'green'
          : 'gray',
      trend: summary.price_gap_avg,
    },
    {
      title: '競爭Competitor最低價',
      value: formatPrice(summary.lowest_competitor_price),
      description: '競爭Competitor中的最低Price',
      icon: DollarSign,
      color: 'blue',
      trend: null,
    },
    {
      title: 'Price波動率',
      value: formatPercent(summary.volatility),
      description: '自家ProductPrice波動程度',
      icon: Activity,
      color:
        summary.volatility === null
          ? 'gray'
          : summary.volatility > 10
          ? 'orange'
          : 'green',
      trend: null,
    },
  ]

  // 顏色Configuration
  const colorConfig: Record<string, { bg: string; text: string; icon: string }> = {
    green: {
      bg: 'bg-green-50',
      text: 'text-green-600',
      icon: 'text-green-500',
    },
    red: {
      bg: 'bg-red-50',
      text: 'text-red-600',
      icon: 'text-red-500',
    },
    blue: {
      bg: 'bg-blue-50',
      text: 'text-blue-600',
      icon: 'text-blue-500',
    },
    orange: {
      bg: 'bg-orange-50',
      text: 'text-orange-600',
      icon: 'text-orange-500',
    },
    gray: {
      bg: 'bg-gray-50',
      text: 'text-gray-600',
      icon: 'text-gray-400',
    },
  }

  return (
    <div className="grid grid-cols-2 md:grid-cols-2 lg:grid-cols-4 gap-2 sm:gap-4">
      {kpis.map((kpi) => {
        const colors = colorConfig[kpi.color]
        const Icon = kpi.icon

        return (
          <HoloCard key={kpi.title} className="p-2.5 sm:p-4">
            <div className="flex items-start justify-between gap-2">
              <div className="flex-1 min-w-0">
                <div className="text-xs sm:text-sm text-gray-500 mb-0.5 sm:mb-1 truncate">{kpi.title}</div>
                <div className={`text-lg sm:text-2xl font-bold ${colors.text}`}>
                  {kpi.value}
                </div>
                <div className="text-[10px] sm:text-xs text-gray-400 mt-0.5 sm:mt-1 line-clamp-2">
                  {kpi.description}
                </div>
              </div>
              <div className={`p-1.5 sm:p-2 rounded-lg shrink-0 ${colors.bg}`}>
                <Icon className={`w-4 h-4 sm:w-5 sm:h-5 ${colors.icon}`} />
              </div>
            </div>

            {/* Trend指示器 */}
            {kpi.trend !== null && (
              <div className="mt-2 sm:mt-3 pt-2 sm:pt-3 border-t border-gray-100">
                <div className="flex items-center gap-1 text-xs sm:text-sm">
                  {kpi.trend > 0 ? (
                    <>
                      <TrendingUp className="w-3 h-3 sm:w-4 sm:h-4 text-red-500" />
                      <span className="text-red-600 truncate">高於競爭Competitor</span>
                    </>
                  ) : kpi.trend < 0 ? (
                    <>
                      <TrendingDown className="w-3 h-3 sm:w-4 sm:h-4 text-green-500" />
                      <span className="text-green-600 truncate">低於競爭Competitor</span>
                    </>
                  ) : (
                    <span className="text-gray-500 truncate">與競爭Competitor持平</span>
                  )}
                </div>
              </div>
            )}
          </HoloCard>
        )
      })}
    </div>
  )
}
