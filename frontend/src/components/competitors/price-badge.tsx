'use client'

import { cn } from '@/lib/utils'
import { TrendingDown, TrendingUp, Minus } from 'lucide-react'

interface PriceBadgeProps {
  ourPrice: number | null
  competitorPrice: number | null
  showDiff?: boolean
}

export function PriceBadge({ ourPrice, competitorPrice, showDiff = true }: PriceBadgeProps) {
  if (!ourPrice || !competitorPrice) {
    return <span className="text-slate-500 text-sm">N/A</span>
  }

  const diff = competitorPrice - ourPrice
  const diffPct = (diff / ourPrice) * 100

  const isWeAreCheaper = diff > 0
  const isSame = Math.abs(diffPct) < 3

  return (
    <div className="flex items-center gap-1.5">
      <span className={cn(
        'font-mono text-sm font-semibold',
        isSame ? 'text-slate-300' :
        isWeAreCheaper ? 'text-emerald-400' : 'text-red-400'
      )}>
        ${competitorPrice.toFixed(0)}
      </span>
      {showDiff && !isSame && (
        <span className={cn(
          'flex items-center gap-0.5 text-xs',
          isWeAreCheaper ? 'text-emerald-500' : 'text-red-500'
        )}>
          {isWeAreCheaper ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
          {Math.abs(diffPct).toFixed(0)}%
        </span>
      )}
    </div>
  )
}

export function PriceChangeIndicator({ change7d }: { change7d: number | null }) {
  if (change7d === null || change7d === undefined) return null
  if (Math.abs(change7d) < 1) return null

  return (
    <span className={cn(
      'flex items-center gap-0.5 text-xs',
      change7d < 0 ? 'text-emerald-500' : 'text-red-500'
    )}>
      {change7d < 0 ? '↓' : '↑'}{Math.abs(change7d).toFixed(0)}%
      <span className="text-slate-600">7d</span>
    </span>
  )
}
