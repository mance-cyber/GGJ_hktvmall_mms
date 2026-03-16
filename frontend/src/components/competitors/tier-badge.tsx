'use client'

import { cn } from '@/lib/utils'
import { useLocale } from '@/components/providers/locale-provider'

const TIER_STYLE: Record<number, { labelKey: string; color: string; bg: string }> = {
  1: { labelKey: 'competitors.tier.tier_1', color: 'text-red-600', bg: 'bg-red-50 border-red-200' },
  2: { labelKey: 'competitors.tier.tier_2', color: 'text-amber-600', bg: 'bg-amber-50 border-amber-200' },
  3: { labelKey: 'competitors.tier.tier_3', color: 'text-gray-500', bg: 'bg-gray-50 border-gray-200' },
}

export function TierBadge({ tier }: { tier: number }) {
  const { t } = useLocale()
  const config = TIER_STYLE[tier] || TIER_STYLE[3]
  return (
    <span className={cn(
      'inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium border',
      config.bg, config.color,
    )}>
      {t(config.labelKey)}
    </span>
  )
}
