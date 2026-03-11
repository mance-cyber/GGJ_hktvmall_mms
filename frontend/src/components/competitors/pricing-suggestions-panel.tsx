'use client'

import { useQuery } from '@tanstack/react-query'
import { api, PricingSuggestion } from '@/lib/api'
import { TrendingDown, TrendingUp, Minus, AlertTriangle, CheckCircle2, XCircle, Loader2 } from 'lucide-react'
import { cn } from '@/lib/utils'
import { useState } from 'react'

const priorityConfig = {
  high: { label: '🔴 High', bg: 'bg-red-50', border: 'border-red-200', text: 'text-red-700' },
  medium: { label: '🟡 Medium', bg: 'bg-amber-50', border: 'border-amber-200', text: 'text-amber-700' },
  low: { label: '🟢 Low', bg: 'bg-green-50', border: 'border-green-200', text: 'text-green-700' },
}

const actionConfig = {
  lower: { icon: TrendingDown, label: 'Suggest price cut', color: 'text-red-600', bg: 'bg-red-50' },
  raise: { icon: TrendingUp, label: 'Consider raising price', color: 'text-green-600', bg: 'bg-green-50' },
  maintain: { icon: Minus, label: 'Maintain current price', color: 'text-gray-600', bg: 'bg-gray-50' },
}

export function PricingSuggestionsPanel() {
  const { data, isLoading } = useQuery({
    queryKey: ['pricing-suggestions'],
    queryFn: () => api.getPricingSuggestions(),
  })

  const [dismissed, setDismissed] = useState<Set<string>>(new Set())

  const suggestions = data?.suggestions.filter(s => !dismissed.has(s.product_id)) ?? []
  const highCount = suggestions.filter(s => s.priority === 'high').length
  const mediumCount = suggestions.filter(s => s.priority === 'medium').length

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-16">
        <Loader2 className="w-5 h-5 text-teal-500 animate-spin" />
        <span className="text-sm text-gray-400 ml-2">Analyzing...</span>
      </div>
    )
  }

  if (suggestions.length === 0) {
    return (
      <div className="text-center py-16 text-gray-400">
        <CheckCircle2 className="w-10 h-10 mx-auto mb-3 opacity-30" />
        <p className="text-sm">No pricing suggestions</p>
        <p className="text-xs mt-1">All products are reasonably priced 👍</p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {/* Summary bar */}
      <div className="flex items-center gap-3 bg-white rounded-xl border border-gray-200 shadow-sm p-3">
        <AlertTriangle className="w-4 h-4 text-amber-500 shrink-0" />
        <p className="text-sm text-gray-600">
          Total: <span className="font-bold">{suggestions.length}</span> suggestions
          {highCount > 0 && <span className="text-red-600 font-semibold ml-2">🔴 {highCount} require attention</span>}
          {mediumCount > 0 && <span className="text-amber-600 font-semibold ml-2">🟡 {mediumCount} can be optimized</span>}
        </p>
      </div>

      {/* Cards */}
      {suggestions.map(s => {
        const pCfg = priorityConfig[s.priority]
        const aCfg = actionConfig[s.action]
        const ActionIcon = aCfg.icon

        return (
          <div
            key={s.product_id}
            className={cn(
              'rounded-xl border shadow-sm p-3 sm:p-4',
              pCfg.bg, pCfg.border,
            )}
          >
            {/* Header */}
            <div className="flex items-start justify-between gap-2 mb-2">
              <div className="min-w-0">
                {s.category && (
                  <span className="text-[10px] text-gray-400 uppercase tracking-wider">{s.category}</span>
                )}
                <h4 className="font-semibold text-gray-800 text-sm truncate">{s.product_name}</h4>
              </div>
              <span className={cn('text-[10px] px-2 py-0.5 rounded-full border shrink-0', pCfg.bg, pCfg.border, pCfg.text)}>
                {pCfg.label}
              </span>
            </div>

            {/* Action + Reason */}
            <div className={cn('flex items-center gap-2 rounded-lg px-2.5 py-1.5 mb-2', aCfg.bg)}>
              <ActionIcon className={cn('w-4 h-4 shrink-0', aCfg.color)} />
              <span className={cn('text-xs font-medium', aCfg.color)}>{aCfg.label}</span>
            </div>
            <p className="text-xs text-gray-600 mb-3">{s.reason}</p>

            {/* Price comparison */}
            <div className="grid grid-cols-3 gap-2 text-center text-[10px] sm:text-xs mb-3">
              <div className="bg-white/60 rounded-lg px-2 py-1.5 border border-white">
                <div className="text-gray-400">Current Price</div>
                <div className="font-mono font-bold text-gray-800">${s.our_price.toFixed(0)}</div>
              </div>
              <div className="bg-white/60 rounded-lg px-2 py-1.5 border border-white">
                <div className="text-gray-400">Cheapest Competitor</div>
                <div className="font-mono font-bold text-gray-800">${s.cheapest_competitor_price.toFixed(0)}</div>
              </div>
              <div className="bg-white/60 rounded-lg px-2 py-1.5 border border-white">
                <div className="text-gray-400">Suggested Price</div>
                <div className={cn('font-mono font-bold', s.suggested_price ? aCfg.color : 'text-gray-400')}>
                  {s.suggested_price ? `$${s.suggested_price.toFixed(0)}` : '—'}
                </div>
              </div>
            </div>

            {/* Stats row */}
            <div className="flex items-center gap-3 text-[10px] text-gray-400 mb-2">
              <span>Price Gap {s.price_diff_pct > 0 ? '+' : ''}{s.price_diff_pct.toFixed(1)}%</span>
              <span>·</span>
              <span>{s.cheaper_count}/{s.total_competitors} cheaper</span>
              <span>·</span>
              <span>{s.stockout_pct.toFixed(0)}% Out of stock</span>
            </div>

            {/* Action buttons */}
            <div className="flex gap-2">
              <button
                onClick={() => setDismissed(prev => new Set(prev).add(s.product_id))}
                className="flex-1 flex items-center justify-center gap-1 text-xs px-3 py-1.5 rounded-lg border border-gray-200 text-gray-500 hover:bg-white transition-colors"
              >
                <XCircle className="w-3 h-3" /> Ignore
              </button>
              <button className="flex-1 flex items-center justify-center gap-1 text-xs px-3 py-1.5 rounded-lg bg-teal-500 text-white hover:bg-teal-600 transition-colors">
                <CheckCircle2 className="w-3 h-3" /> Accept
              </button>
            </div>
          </div>
        )
      })}
    </div>
  )
}
