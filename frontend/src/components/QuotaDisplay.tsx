'use client'

import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'
import { Zap, TrendingUp, AlertCircle, Calendar, RefreshCw } from 'lucide-react'

interface QuotaDisplayProps {
  compact?: boolean
}

export default function QuotaDisplay({ compact = false }: QuotaDisplayProps) {
  const { data: quota, isLoading, error, refetch } = useQuery({
    queryKey: ['quota-usage'],
    queryFn: () => api.getQuotaUsage(),
    refetchInterval: 60000, // 每分鐘刷新
  })

  if (isLoading || !quota) {
    return (
      <div className="animate-pulse bg-gray-100 rounded-lg h-8 w-32" />
    )
  }

  // 計算剩餘百分比
  const remainingPercent = quota.plan_credits > 0
    ? Math.round((quota.remaining_credits / quota.plan_credits) * 100)
    : 0

  const usagePercent = Math.round(quota.usage_percent)

  // 格式化日期
  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return 'N/A'
    const date = new Date(dateStr)
    return date.toLocaleDateString('zh-HK', { month: 'short', day: 'numeric' })
  }

  if (compact) {
    return (
      <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-sm ${
        quota.is_critical ? 'bg-red-100 text-red-700' :
        quota.is_low ? 'bg-yellow-100 text-yellow-700' :
        'bg-blue-100 text-blue-700'
      }`}>
        <Zap className="w-4 h-4" />
        <span>{quota.remaining_credits.toLocaleString()} / {quota.plan_credits.toLocaleString()}</span>
        {quota.error_message && (
          <span title={quota.error_message}>
            <AlertCircle className="w-4 h-4 text-red-500" />
          </span>
        )}
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg border p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-medium text-gray-900 flex items-center gap-2">
          <Zap className="w-5 h-5 text-blue-500" />
          Firecrawl API 配額
        </h3>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => refetch()}
            className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
            title="刷新配額"
            aria-label="刷新配額"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
          {quota.is_critical && (
            <span className="flex items-center gap-1 text-xs text-red-600 bg-red-50 px-2 py-1 rounded-full">
              <AlertCircle className="w-3 h-3" />
              配額不足
            </span>
          )}
        </div>
      </div>

      {/* 錯誤信息 */}
      {quota.error_message && (
        <div className="mb-3 p-2 bg-red-50 text-red-700 text-sm rounded-lg flex items-start gap-2">
          <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
          <span>{quota.error_message}</span>
        </div>
      )}

      {/* 進度條 */}
      <div className="mb-3">
        <div className="flex justify-between text-sm text-gray-600 mb-1">
          <span>已使用 {usagePercent}%</span>
          <span>{quota.used_credits.toLocaleString()} / {quota.plan_credits.toLocaleString()} credits</span>
        </div>
        <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full transition-all ${
              quota.is_critical ? 'bg-red-500' :
              quota.is_low ? 'bg-yellow-500' :
              'bg-blue-500'
            }`}
            style={{ width: `${Math.min(usagePercent, 100)}%` }}
          />
        </div>
      </div>

      {/* 詳細信息 */}
      <div className="grid grid-cols-2 gap-3 text-sm">
        <div className="bg-gray-50 rounded-lg p-2">
          <div className="text-gray-500 flex items-center gap-1">
            <TrendingUp className="w-3 h-3" />
            剩餘配額
          </div>
          <div className={`font-medium ${
            quota.is_critical ? 'text-red-600' :
            quota.is_low ? 'text-yellow-600' :
            'text-green-600'
          }`}>
            {quota.remaining_credits.toLocaleString()} credits
          </div>
        </div>
        <div className="bg-gray-50 rounded-lg p-2">
          <div className="text-gray-500 flex items-center gap-1">
            <Calendar className="w-3 h-3" />
            計費週期
          </div>
          <div className="font-medium text-gray-900">
            {quota.days_remaining} 天剩餘
          </div>
        </div>
      </div>

      {/* 本地統計 */}
      <div className="mt-3 pt-3 border-t">
        <div className="text-xs text-gray-500 mb-2">本地使用統計</div>
        <div className="grid grid-cols-2 gap-3 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-500">今日使用</span>
            <span className="font-medium">{quota.daily_usage} credits</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500">本月使用</span>
            <span className="font-medium">{quota.monthly_usage} credits</span>
          </div>
        </div>
      </div>

      {/* 週期信息 */}
      {quota.billing_period_start && quota.billing_period_end && (
        <div className="mt-3 text-xs text-gray-400 text-center">
          計費週期: {formatDate(quota.billing_period_start)} - {formatDate(quota.billing_period_end)}
        </div>
      )}

      {/* 提示 */}
      {quota.is_low && (
        <div className={`mt-3 p-2 rounded-lg text-xs ${
          quota.is_critical ? 'bg-red-50 text-red-700' : 'bg-yellow-50 text-yellow-700'
        }`}>
          <div className="flex items-start gap-2">
            <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
            <div>
              {quota.is_critical
                ? '配額即將用盡，請升級計劃以繼續使用。'
                : '配額偏低，建議使用智能抓取以節省消耗。'}
              <a
                href="https://firecrawl.dev/pricing"
                target="_blank"
                rel="noopener noreferrer"
                className="ml-1 underline hover:no-underline"
              >
                升級計劃
              </a>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
