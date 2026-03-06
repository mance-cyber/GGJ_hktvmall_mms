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
  color = 'cyan',
}: {
  icon: React.ElementType
  label: string
  value: string | number
  sub?: string
  color?: 'cyan' | 'emerald' | 'amber' | 'red' | 'purple' | 'blue'
}) {
  const colors = {
    cyan: 'text-cyan-400 bg-cyan-500/10 border-cyan-500/20',
    emerald: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
    amber: 'text-amber-400 bg-amber-500/10 border-amber-500/20',
    red: 'text-red-400 bg-red-500/10 border-red-500/20',
    purple: 'text-purple-400 bg-purple-500/10 border-purple-500/20',
    blue: 'text-blue-400 bg-blue-500/10 border-blue-500/20',
  }

  return (
    <div className={`rounded-xl border p-4 ${colors[color]}`}>
      <div className="flex items-center gap-2 mb-2">
        <Icon className="w-4 h-4 opacity-70" />
        <span className="text-xs text-slate-400">{label}</span>
      </div>
      <div className="text-2xl font-bold tracking-tight">{value}</div>
      {sub && <div className="text-xs text-slate-500 mt-1">{sub}</div>}
    </div>
  )
}

export function DashboardStats({ summary, isLoading }: DashboardStatsProps) {
  if (isLoading || !summary) {
    return (
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="rounded-xl border border-slate-800 p-4 animate-pulse">
            <div className="h-4 bg-slate-800 rounded w-20 mb-2" />
            <div className="h-8 bg-slate-800 rounded w-16" />
          </div>
        ))}
      </div>
    )
  }

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
      <StatCard
        icon={Building2}
        label="追蹤商戶"
        value={summary.total_competitors}
        color="cyan"
      />
      <StatCard
        icon={Package}
        label="競品商品"
        value={summary.total_tracked_products}
        sub={`已配對 ${summary.mapped_competitors}`}
        color="blue"
      />
      <StatCard
        icon={Target}
        label="自家商品"
        value={summary.our_products}
        color="purple"
      />
      <StatCard
        icon={TrendingUp}
        label="我哋最平"
        value={`${summary.we_are_cheapest_pct}%`}
        color="emerald"
      />
      <StatCard
        icon={AlertTriangle}
        label="24h 警報"
        value={summary.price_alerts_24h}
        color={summary.price_alerts_24h > 0 ? 'amber' : 'cyan'}
      />
      <StatCard
        icon={Clock}
        label="平均價差"
        value={`${summary.avg_price_diff_pct > 0 ? '+' : ''}${summary.avg_price_diff_pct}%`}
        sub={summary.last_scan ? `掃描: ${new Date(summary.last_scan).toLocaleTimeString('zh-HK', { hour: '2-digit', minute: '2-digit' })}` : '未掃描'}
        color={summary.avg_price_diff_pct > 0 ? 'emerald' : 'red'}
      />
    </div>
  )
}
