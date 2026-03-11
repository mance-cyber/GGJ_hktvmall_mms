'use client'

import { ComparisonSummary } from '@/lib/api'
import { Building2, Package, AlertTriangle, TrendingUp, Clock, Target } from 'lucide-react'

interface DashboardStatsProps {
  summary: ComparisonSummary | undefined
  isLoading: boolean
}

function StatCard({
  icon: Icon,
  label,
  value,
  sub,
  color = 'teal',
}: {
  icon: React.ElementType
  label: string
  value: string | number
  sub?: string
  color?: 'teal' | 'emerald' | 'amber' | 'red' | 'purple' | 'blue'
}) {
  const colors = {
    teal: 'border-teal-200 bg-gradient-to-br from-white to-teal-50/50 text-teal-600',
    emerald: 'border-emerald-200 bg-gradient-to-br from-white to-emerald-50/50 text-emerald-600',
    amber: 'border-amber-200 bg-gradient-to-br from-white to-amber-50/50 text-amber-600',
    red: 'border-red-200 bg-gradient-to-br from-white to-red-50/50 text-red-600',
    purple: 'border-purple-200 bg-gradient-to-br from-white to-purple-50/50 text-purple-600',
    blue: 'border-blue-200 bg-gradient-to-br from-white to-blue-50/50 text-blue-600',
  }

  return (
    <div className={`rounded-xl border p-3 sm:p-4 shadow-sm ${colors[color]}`}>
      <div className="flex items-center gap-1.5 mb-1 sm:mb-2">
        <Icon className="w-3.5 h-3.5 sm:w-4 sm:h-4 opacity-60" />
        <span className="text-[10px] sm:text-xs text-gray-500">{label}</span>
      </div>
      <div className="text-xl sm:text-2xl font-bold tracking-tight">{value}</div>
      {sub && <div className="text-[10px] sm:text-xs text-gray-400 mt-0.5 sm:mt-1 truncate">{sub}</div>}
    </div>
  )
}

export function DashboardStats({ summary, isLoading }: DashboardStatsProps) {
  if (isLoading || !summary) {
    return (
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2 sm:gap-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="rounded-xl border border-gray-200 bg-white p-3 sm:p-4 animate-pulse shadow-sm">
            <div className="h-3 sm:h-4 bg-gray-100 rounded w-14 sm:w-20 mb-2" />
            <div className="h-6 sm:h-8 bg-gray-100 rounded w-10 sm:w-16" />
          </div>
        ))}
      </div>
    )
  }

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2 sm:gap-3">
      <StatCard
        icon={Building2}
        label="Tracked Merchants"
        value={summary.total_competitors}
        color="teal"
      />
      <StatCard
        icon={Package}
        label="Competitor Products"
        value={summary.total_tracked_products}
        sub={`${summary.mapped_competitors} paired`}
        color="blue"
      />
      <StatCard
        icon={Target}
        label="Own Products"
        value={summary.our_products}
        color="purple"
      />
      <StatCard
        icon={TrendingUp}
        label="We Are Cheapest"
        value={`${summary.we_are_cheapest_pct}%`}
        color="emerald"
      />
      <StatCard
        icon={AlertTriangle}
        label="24h Alert"
        value={summary.price_alerts_24h}
        color={summary.price_alerts_24h > 0 ? 'amber' : 'teal'}
      />
      <StatCard
        icon={Clock}
        label="Avg. Price Gap"
        value={`${summary.avg_price_diff_pct > 0 ? '+' : ''}${summary.avg_price_diff_pct}%`}
        sub={summary.last_scan ? `Scan: ${new Date(summary.last_scan).toLocaleTimeString('en-HK', { hour: '2-digit', minute: '2-digit' })}` : 'Not scanned'}
        color={summary.avg_price_diff_pct > 0 ? 'emerald' : 'red'}
      />
    </div>
  )
}
