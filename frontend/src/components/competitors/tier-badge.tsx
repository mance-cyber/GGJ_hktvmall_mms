'use client'

import { cn } from '@/lib/utils'

const TIER_CONFIG: Record<number, { label: string; color: string; bg: string }> = {
  1: { label: 'Tier 1', color: 'text-red-400', bg: 'bg-red-500/10 border-red-500/30' },
  2: { label: 'Tier 2', color: 'text-amber-400', bg: 'bg-amber-500/10 border-amber-500/30' },
  3: { label: 'Tier 3', color: 'text-slate-400', bg: 'bg-slate-500/10 border-slate-500/30' },
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
