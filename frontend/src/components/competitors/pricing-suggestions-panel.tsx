'use client'

import { useQuery } from '@tanstack/react-query'
import { api, PricingSuggestion } from '@/lib/api'
import { TrendingDown, TrendingUp, Minus, AlertCircle, CheckCircle2, Info } from 'lucide-react'
import { cn } from '@/lib/utils'

function SuggestionCard({ s }: { s: PricingSuggestion }) {
  const isRaise = s.action === 'raise'
  const isLower = s.action === 'lower'

  const priorityColor = {
    high: 'border-red-200 bg-red-50/50',
    medium: 'border-amber-200 bg-amber-50/50',
    low: 'border-gray-200 bg-white',
  }[s.priority]

  const actionIcon = isLower
    ? <TrendingDown className="w-4 h-4 text-red-500" />
    : isRaise
      ? <TrendingUp className="w-4 h-4 text-emerald-500" />
      : <Minus className="w-4 h-4 text-gray-400" />

  const actionLabel = isLower ? '建議降價' : isRaise ? '建議加價' : '維持現價'
  const actionColor = isLower ? 'text-red-600 bg-red-50 border-red-200' : isRaise ? 'text-emerald-600 bg-emerald-50 border-emerald-200' : 'text-gray-500 bg-gray-50 border-gray-200'

  return (
    <div className={cn('rounded-xl border p-3 sm:p-4 shadow-sm space-y-2', priorityColor)}>
      {/* Header */}
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-2 min-w-0">
          {actionIcon}
          <span className="font-medium text-gray-700 text-sm truncate">{s.product_name}</span>
          {s.category && (
            <span className="hidden sm:inline-flex shrink-0 text-[10px] px-1.5 py-0.5 rounded-full bg-teal-50 text-teal-600 border border-teal-200">
              {s.category}
            </span>
          )}
        </div>
        <div className="flex items-center gap-1.5 shrink-0">
          {s.priority === 'high' && (
            <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-red-100 text-red-600 font-medium">緊急</span>
          )}
          <span className={cn('text-[10px] sm:text-xs px-2 py-0.5 rounded-full border', actionColor)}>
            {actionLabel}
          </span>
        </div>
      </div>

      {/* Price comparison */}
      <div className="flex items-center gap-3 sm:gap-4 text-xs flex-wrap">
        <div>
          <span className="text-gray-400">現時 </span>
          <span className="font-mono font-bold text-teal-600">${s.our_price.toFixed(0)}</span>
        </div>
        <div>
          <span className="text-gray-400">最平競品 </span>
          <span className={cn('font-mono font-bold', isLower ? 'text-red-500' : 'text-gray-600')}>
            ${s.cheapest_competitor_price.toFixed(0)}
          </span>
        </div>
        <div>
          <span className="text-gray-400">差距 </span>
          <span className={cn('font-mono font-medium', isLower ? 'text-red-500' : 'text-emerald-500')}>
            {s.price_diff_pct > 0 ? '+' : ''}{s.price_diff_pct.toFixed(1)}%
          </span>
        </div>
        {s.suggested_price && (
          <div>
            <span className="text-gray-400">建議 </span>
            <span className="font-mono font-bold text-teal-600">${s.suggested_price.toFixed(0)}</span>
          </div>
        )}
      </div>

      {/* Reason */}
      <p className="text-[10px] sm:text-xs text-gray-500 flex items-start gap-1">
        <Info className="w-3 h-3 mt-0.5 shrink-0" />
        {s.reason}
      </p>

      {/* Stats strip */}
      <div className="flex items-center gap-2 sm:gap-3 text-[10px] text-gray-400">
        <span>{s.cheaper_count}/{s.total_competitors} 間比我平</span>
        {s.stockout_pct > 0 && <span>{s.stockout_pct.toFixed(0)}% 競品缺貨</span>}
        <span>均價 ${s.avg_competitor_price.toFixed(0)}</span>
      </div>
    </div>
  )
}

export function PricingSuggestionsPanel() {
  const { data, isLoading } = useQuery({
    queryKey: ['pricing-suggestions'],
    queryFn: () => api.getPricingSuggestions(),
    staleTime: 5 * 60 * 1000,
  })

  const suggestions = data?.suggestions ?? []
  const highCount = suggestions.filter(s => s.priority === 'high').length
  const lowerCount = suggestions.filter(s => s.action === 'lower').length
  const raiseCount = suggestions.filter(s => s.action === 'raise').length

  if (isLoading) {
    return (
      <div className="space-y-3">
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="rounded-xl border border-gray-200 bg-white p-4 animate-pulse shadow-sm">
            <div className="h-4 bg-gray-100 rounded w-48 mb-2" />
            <div className="h-3 bg-gray-100 rounded w-64" />
          </div>
        ))}
      </div>
    )
  }

  if (suggestions.length === 0) {
    return (
      <div className="text-center py-16 text-gray-400">
        <CheckCircle2 className="w-12 h-12 mx-auto mb-3 text-emerald-300" />
        <p className="text-sm font-medium text-gray-600">定價狀態良好！</p>
        <p className="text-xs mt-1">無需要特別調整嘅商品</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Summary bar */}
      <div className="flex items-center gap-3 p-3 bg-white rounded-xl border border-gray-200 shadow-sm flex-wrap">
        <span className="text-xs text-gray-500">共 {suggestions.length} 條建議：</span>
        {highCount > 0 && <span className="text-xs text-red-600 bg-red-50 px-2 py-0.5 rounded-full border border-red-200">🚨 緊急 {highCount}</span>}
        {lowerCount > 0 && <span className="text-xs text-amber-600 bg-amber-50 px-2 py-0.5 rounded-full border border-amber-200">↓ 降價 {lowerCount}</span>}
        {raiseCount > 0 && <span className="text-xs text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">↑ 加價 {raiseCount}</span>}
      </div>

      {/* Suggestion cards */}
      <div className="space-y-2 sm:space-y-3">
        {suggestions.map(s => <SuggestionCard key={s.product_id} s={s} />)}
      </div>
    </div>
  )
}
