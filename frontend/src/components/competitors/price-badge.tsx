'use client'

import { cn } from '@/lib/utils'
import { TrendingDown, TrendingUp } from 'lucide-react'
import { useLocale } from '@/components/providers/locale-provider'

interface PriceBadgeProps {
  ourPrice: number | null
  competitorPrice: number | null
  showDiff?: boolean
}

export function PriceBadge({ ourPrice, competitorPrice, showDiff = true }: PriceBadgeProps) {
  const { t } = useLocale()
  if (!ourPrice || !competitorPrice) {
    return <span className="text-gray-400 text-sm">{t('competitors.price_badge.na')}</span>
  }

  const diff = competitorPrice - ourPrice
  const diffPct = (diff / ourPrice) * 100

  const isWeAreCheaper = diff > 0
  const isSame = Math.abs(diffPct) < 3

  return (
    <div className="flex items-center gap-1.5">
      <span className={cn(
        'font-mono text-sm font-semibold',
        isSame ? 'text-gray-500' :
        isWeAreCheaper ? 'text-emerald-500' : 'text-red-500'
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
  const { t } = useLocale()
  if (change7d === null || change7d === undefined) return null
  if (Math.abs(change7d) < 1) return null

  return (
    <span className={cn(
      'flex items-center gap-0.5 text-xs',
      change7d < 0 ? 'text-emerald-500' : 'text-red-500'
    )}>
      {change7d < 0 ? '↓' : '↑'}{Math.abs(change7d).toFixed(0)}%
      <span className="text-gray-400">{t('competitors.price_badge.period_7d')}</span>
    </span>
  )
}
