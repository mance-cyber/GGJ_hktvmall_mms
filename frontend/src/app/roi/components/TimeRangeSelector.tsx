// =============================================
// 時間範圍選擇器組件
// =============================================

'use client'

import { Calendar } from 'lucide-react'
import type { ROIPeriod } from '@/lib/api/roi'

interface TimeRangeSelectorProps {
  value: ROIPeriod
  onChange: (period: ROIPeriod) => void
}

const periods: { value: ROIPeriod; label: string }[] = [
  { value: 'today', label: '今日' },
  { value: 'week', label: '本週' },
  { value: 'month', label: '本月' },
  { value: 'quarter', label: '本季' },
]

export function TimeRangeSelector({ value, onChange }: TimeRangeSelectorProps) {
  return (
    <div className="flex items-center gap-2">
      <Calendar className="w-4 h-4 text-gray-400" />
      <div className="flex bg-gray-100 rounded-lg p-1">
        {periods.map((period) => (
          <button
            key={period.value}
            onClick={() => onChange(period.value)}
            className={`px-4 py-2 text-sm font-medium rounded-md transition-all ${
              value === period.value
                ? 'bg-white text-purple-600 shadow-sm'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            {period.label}
          </button>
        ))}
      </div>
    </div>
  )
}
