// =============================================
// 競品監測價值卡片組件
// =============================================

'use client'

import { Loader2, Bell, TrendingDown, TrendingUp, DollarSign } from 'lucide-react'
import { useCompetitorInsights } from '../hooks/useROIData'
import type { ROIPeriod } from '@/lib/api/roi'

interface CompetitorValueCardProps {
  period: ROIPeriod
}

export function CompetitorValueCard({ period }: CompetitorValueCardProps) {
  const { data, isLoading, error } = useCompetitorInsights(period)

  // 格式化金額
  const formatMoney = (value: number) => {
    return `$${Number(value).toLocaleString('zh-HK', { minimumFractionDigits: 0 })}`
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64 text-red-500">
        載入失敗
      </div>
    )
  }

  const stats = [
    {
      icon: Bell,
      label: '觸發告警',
      value: data?.price_alerts_triggered || 0,
      color: 'text-blue-500',
      bg: 'bg-blue-50',
    },
    {
      icon: TrendingDown,
      label: '偵測降價',
      value: data?.price_drops_detected || 0,
      color: 'text-red-500',
      bg: 'bg-red-50',
    },
    {
      icon: TrendingUp,
      label: '偵測加價',
      value: data?.price_increases_detected || 0,
      color: 'text-green-500',
      bg: 'bg-green-50',
    },
  ]

  return (
    <div className="space-y-6">
      {/* 潛在節省金額 - 突出顯示 */}
      <div className="text-center p-6 bg-gradient-to-br from-cyan-50 to-blue-50 rounded-xl border border-cyan-200">
        <div className="flex items-center justify-center gap-2 mb-2">
          <DollarSign className="w-6 h-6 text-cyan-500" />
          <span className="text-sm font-medium text-gray-500">潛在節省金額</span>
        </div>
        <div className="text-4xl font-bold text-cyan-600">
          {formatMoney(data?.potential_savings || 0)}
        </div>
        <div className="text-xs text-gray-400 mt-2">
          基於警報響應計算的估算值
        </div>
      </div>

      {/* 告警統計 */}
      <div className="grid grid-cols-3 gap-4">
        {stats.map((stat) => {
          const Icon = stat.icon
          return (
            <div key={stat.label} className="text-center">
              <div className={`inline-flex p-3 rounded-lg ${stat.bg} mb-2`}>
                <Icon className={`w-5 h-5 ${stat.color}`} />
              </div>
              <div className="text-2xl font-bold text-gray-900">{stat.value}</div>
              <div className="text-xs text-gray-500">{stat.label}</div>
            </div>
          )
        })}
      </div>

      {/* 說明文字 */}
      <div className="text-xs text-gray-400 text-center">
        競品監測幫助你及時掌握市場動態，避免定價失誤造成的損失
      </div>
    </div>
  )
}
