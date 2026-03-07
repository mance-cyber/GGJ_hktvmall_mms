'use client'

import { cn } from '@/lib/utils'

const TIER_CONFIG: Record<number, { label: string; color: string; bg: string }> = {
  1: { label: 'Tier 1', color: 'text-red-600', bg: 'bg-red-50 border-red-200' },
  2: { label: 'Tier 2', color: 'text-amber-600', bg: 'bg-amber-50 border-amber-200' },
  3: { label: 'Tier 3', color: 'text-gray-500', bg: 'bg-gray-50 border-gray-200' },
}

export function TierBadge({ tier }: { tier: number }) {
  const config = TIER_CONFIG[tier] || TIER_CONFIG[3]
  return (
    <span className={cn(
      'inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium border',
      config.bg, config.color,
    )}>
      {config.label}
    </span>
  )
}
