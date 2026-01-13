// =============================================
// 時間範圍選擇器組件
// =============================================

'use client'

import { Calendar } from 'lucide-react'

interface TimeRangeOption {
  label: string
  value: number
}

interface TimeRangePickerProps {
  options: readonly TimeRangeOption[]
  selectedDays: number
  onSelect: (days: number) => void
}

export function TimeRangePicker({
  options,
  selectedDays,
  onSelect,
}: TimeRangePickerProps) {
  return (
    <div className="flex items-center gap-2">
      <div className="p-2 rounded-lg bg-gray-100 text-gray-500">
        <Calendar className="w-4 h-4" />
      </div>
      <div className="flex bg-gray-100 rounded-lg p-1">
        {options.map((option) => (
          <button
            key={option.value}
            type="button"
            onClick={() => onSelect(option.value)}
            className={`px-4 py-2 text-sm font-medium rounded-md transition-all ${
              selectedDays === option.value
                ? 'bg-white text-emerald-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            {option.label}
          </button>
        ))}
      </div>
    </div>
  )
}
