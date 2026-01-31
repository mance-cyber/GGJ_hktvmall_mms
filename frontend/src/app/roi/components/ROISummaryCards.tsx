// =============================================
// ROI 總覽 KPI 卡片組件
// =============================================

'use client'

import { DollarSign, Brain, Eye, TrendingUp, Loader2 } from 'lucide-react'
import { HoloCard } from '@/components/ui/future-tech'
import { useROISummary } from '../hooks/useROIData'
import type { ROIPeriod } from '@/lib/api/roi'

interface ROISummaryCardsProps {
  period: ROIPeriod
}

export function ROISummaryCards({ period }: ROISummaryCardsProps) {
  const { data: summary, isLoading, error } = useROISummary(period)

  // 格式化金額
  const formatMoney = (value: number | undefined) => {
    if (value === undefined || value === null) return '$0'
    return `$${Number(value).toLocaleString('zh-HK', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`
  }

  // 格式化百分比
  const formatPercent = (value: number | undefined) => {
    if (value === undefined || value === null) return '0%'
    const sign = value > 0 ? '+' : ''
    return `${sign}${value.toFixed(1)}%`
  }

  // KPI 卡片配置
  const kpis = [
    {
      title: '總價值創造',
      value: formatMoney(summary?.total_value_generated),
      description: '本期間 GoGoJap 幫你創造的總價值',
      icon: DollarSign,
      color: 'green',
    },
    {
      title: 'AI 定價貢獻',
      value: formatMoney(summary?.ai_pricing_contribution),
      description: '智能改價帶來的額外收益',
      icon: Brain,
      color: 'purple',
    },
    {
      title: '競品監測價值',
      value: formatMoney(summary?.competitor_monitoring_value),
      description: '掌握競品動態避免的損失',
      icon: Eye,
      color: 'cyan',
    },
    {
      title: '投資回報率',
      value: formatPercent(summary?.roi_percentage),
      description: '總投資回報百分比',
      icon: TrendingUp,
      color: summary?.roi_percentage && summary.roi_percentage > 0 ? 'green' : 'gray',
    },
  ]

  // 顏色配置
  const colorConfig: Record<string, { bg: string; text: string; icon: string; border: string }> = {
    green: {
      bg: 'bg-green-50',
      text: 'text-green-600',
      icon: 'text-green-500',
      border: 'border-green-200',
    },
    purple: {
      bg: 'bg-purple-50',
      text: 'text-purple-600',
      icon: 'text-purple-500',
      border: 'border-purple-200',
    },
    cyan: {
      bg: 'bg-cyan-50',
      text: 'text-cyan-600',
      icon: 'text-cyan-500',
      border: 'border-cyan-200',
    },
    gray: {
      bg: 'bg-gray-50',
      text: 'text-gray-600',
      icon: 'text-gray-500',
      border: 'border-gray-200',
    },
  }

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => (
          <HoloCard key={i} className="p-6">
            <div className="flex items-center justify-center h-24">
              <Loader2 className="w-6 h-6 animate-spin text-gray-400" />
            </div>
          </HoloCard>
        ))}
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center text-red-500 py-4">
        載入失敗: {error instanceof Error ? error.message : '未知錯誤'}
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {kpis.map((kpi) => {
        const colors = colorConfig[kpi.color] || colorConfig.gray
        const Icon = kpi.icon

        return (
          <HoloCard key={kpi.title} className="p-6">
            <div className="flex items-start justify-between">
              <div className="space-y-2">
                <p className="text-sm font-medium text-gray-500">{kpi.title}</p>
                <p className={`text-2xl font-bold ${colors.text}`}>
                  {kpi.value}
                </p>
                <p className="text-xs text-gray-400">{kpi.description}</p>
              </div>
              <div className={`p-3 rounded-lg ${colors.bg} ${colors.border} border`}>
                <Icon className={`w-5 h-5 ${colors.icon}`} />
              </div>
            </div>
          </HoloCard>
        )
      })}
    </div>
  )
}
