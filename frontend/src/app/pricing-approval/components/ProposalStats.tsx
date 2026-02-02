// =============================================
// 提案統計卡片組件
// =============================================

'use client'

import { Clock, CheckCircle, XCircle, AlertTriangle } from 'lucide-react'
import { HoloCard } from '@/components/ui/future-tech'

interface ProposalStatsProps {
  pending: number
  approved: number
  rejected: number
  failed: number
}

export function ProposalStats({ pending, approved, rejected, failed }: ProposalStatsProps) {
  const stats = [
    {
      title: '待審批',
      value: pending,
      icon: Clock,
      color: 'orange',
    },
    {
      title: '已批准',
      value: approved,
      icon: CheckCircle,
      color: 'green',
    },
    {
      title: '已拒絕',
      value: rejected,
      icon: XCircle,
      color: 'gray',
    },
    {
      title: '執行失敗',
      value: failed,
      icon: AlertTriangle,
      color: 'red',
    },
  ]

  const colorConfig: Record<string, { bg: string; text: string; icon: string; border: string }> = {
    orange: {
      bg: 'bg-orange-50',
      text: 'text-orange-600',
      icon: 'text-orange-500',
      border: 'border-orange-200',
    },
    green: {
      bg: 'bg-green-50',
      text: 'text-green-600',
      icon: 'text-green-500',
      border: 'border-green-200',
    },
    gray: {
      bg: 'bg-gray-50',
      text: 'text-gray-600',
      icon: 'text-gray-500',
      border: 'border-gray-200',
    },
    red: {
      bg: 'bg-red-50',
      text: 'text-red-600',
      icon: 'text-red-500',
      border: 'border-red-200',
    },
  }

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      {stats.map((stat) => {
        const colors = colorConfig[stat.color]
        const Icon = stat.icon

        return (
          <HoloCard key={stat.title} className={`p-4 ${colors.bg} ${colors.border} border`}>
            <div className="flex items-center gap-3">
              <div className={`p-2 rounded-lg ${colors.bg}`}>
                <Icon className={`w-5 h-5 ${colors.icon}`} />
              </div>
              <div>
                <p className="text-sm text-gray-500">{stat.title}</p>
                <p className={`text-2xl font-bold ${colors.text}`}>{stat.value}</p>
              </div>
            </div>
          </HoloCard>
        )
      })}
    </div>
  )
}
