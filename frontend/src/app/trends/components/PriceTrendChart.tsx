// =============================================
// PriceTrendChart組items
// =============================================

'use client'

import { useMemo, useState } from 'react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'
import { Check, Eye, EyeOff } from 'lucide-react'
import {
  CHART_COLORS,
  getCompetitorColor,
  type PriceDataPoint,
  type CompetitorInfo,
  type OwnProductInfo,
} from '@/lib/api/price-trends'

interface PriceTrendChartProps {
  trends: Record<string, PriceDataPoint[]>
  ownProduct: OwnProductInfo
  competitors: CompetitorInfo[]
}

export function PriceTrendChart({
  trends,
  ownProduct,
  competitors,
}: PriceTrendChartProps) {
  // 可見性State
  const [visibleLines, setVisibleLines] = useState<Record<string, boolean>>(() => {
    const initial: Record<string, boolean> = { own: true }
    competitors.forEach((comp) => {
      initial[comp.id] = true
    })
    return initial
  })

  // 切換可見性
  const toggleVisibility = (key: string) => {
    setVisibleLines((prev) => ({
      ...prev,
      [key]: !prev[key],
    }))
  }

  // 全選/全不選
  const toggleAll = (visible: boolean) => {
    const newState: Record<string, boolean> = { own: visible }
    competitors.forEach((comp) => {
      newState[comp.id] = visible
    })
    setVisibleLines(newState)
  }

  // ProcessingChartData
  const chartData = useMemo(() => {
    // 收集所有Date
    const allDates = new Set<string>()
    Object.values(trends).forEach((points) => {
      points.forEach((p) => {
        const dateStr = new Date(p.date).toLocaleDateString('zh-HK', {
          month: 'short',
          day: 'numeric',
        })
        allDates.add(dateStr)
      })
    })

    // 按DateSort
    const sortedDates = Array.from(allDates).sort((a, b) => {
      return new Date(a).getTime() - new Date(b).getTime()
    })

    // 建立Date到Data的Map
    const dateDataMap: Record<string, { date: string; [key: string]: string | number | null }> = {}

    // Initialize所有Date
    sortedDates.forEach((date) => {
      dateDataMap[date] = { date }
    })

    // 填充自家ProductData
    if (trends.own) {
      trends.own.forEach((point) => {
        const dateStr = new Date(point.date).toLocaleDateString('zh-HK', {
          month: 'short',
          day: 'numeric',
        })
        if (dateDataMap[dateStr]) {
          dateDataMap[dateStr].own = point.price ? Number(point.price) : null
        }
      })
    }

    // 填充競爭CompetitorData
    competitors.forEach((comp) => {
      const compTrends = trends[comp.id]
      if (compTrends) {
        compTrends.forEach((point) => {
          const dateStr = new Date(point.date).toLocaleDateString('zh-HK', {
            month: 'short',
            day: 'numeric',
          })
          if (dateDataMap[dateStr]) {
            dateDataMap[dateStr][comp.id] = point.price
              ? Number(point.price)
              : null
          }
        })
      }
    })

    return Object.values(dateDataMap)
  }, [trends, competitors])

  // Calculate Y 軸Range（只Calculate可見的線）
  const yAxisDomain = useMemo(() => {
    let min = Infinity
    let max = -Infinity

    chartData.forEach((item) => {
      Object.entries(item).forEach(([key, value]) => {
        if (key !== 'date' && typeof value === 'number' && visibleLines[key]) {
          min = Math.min(min, value)
          max = Math.max(max, value)
        }
      })
    })

    if (min === Infinity) return [0, 100]

    const padding = (max - min) * 0.1
    return [Math.floor(min - padding), Math.ceil(max + padding)]
  }, [chartData, visibleLines])

  // Custom Tooltip
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (!active || !payload?.length) return null

    return (
      <div className="bg-white border border-gray-200 rounded-lg shadow-lg p-3 z-50">
        <div className="font-medium text-gray-900 mb-2">{label}</div>
        {payload.map((entry: any, index: number) => (
          <div
            key={index}
            className="flex items-center justify-between gap-4 text-sm"
          >
            <div className="flex items-center gap-2">
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: entry.color }}
              />
              <span className="text-gray-600">{entry.name}</span>
            </div>
            <span className="font-medium" style={{ color: entry.color }}>
              {entry.value !== null ? `$${entry.value.toLocaleString()}` : '--'}
            </span>
          </div>
        ))}
      </div>
    )
  }

  // 如果沒有Data
  if (chartData.length === 0) {
    return (
      <div className="h-[400px] flex items-center justify-center text-gray-500">
        暫無PriceData
      </div>
    )
  }

  // Calculate有多少條線可見
  const visibleCount = Object.values(visibleLines).filter(Boolean).length
  const totalCount = 1 + competitors.length

  return (
    <div>
      {/* Chart */}
      <div className="h-[400px]">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={chartData}
            margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis
              dataKey="date"
              tick={{ fontSize: 12 }}
              stroke="#9ca3af"
              tickLine={false}
            />
            <YAxis
              domain={yAxisDomain}
              tick={{ fontSize: 12 }}
              stroke="#9ca3af"
              tickLine={false}
              tickFormatter={(value) => `$${value}`}
            />
            <Tooltip content={<CustomTooltip />} />

            {/* Own product line (solid, thicker and more visible) */}
            {visibleLines.own && (
              <Line
                type="monotone"
                dataKey="own"
                name={ownProduct.name}
                stroke={CHART_COLORS.own}
                strokeWidth={5}
                dot={{ r: 6, fill: CHART_COLORS.own, strokeWidth: 2, stroke: '#fff' }}
                activeDot={{ r: 8, strokeWidth: 2, stroke: '#fff' }}
                connectNulls
                style={{
                  filter: 'drop-shadow(0 0 4px rgba(139, 92, 246, 0.5))',
                }}
              />
            )}

            {/* 競爭Competitor線（虛線） */}
            {competitors.map((comp, index) => (
              visibleLines[comp.id] && (
                <Line
                  key={comp.id}
                  type="monotone"
                  dataKey={comp.id}
                  name={`${comp.name} - ${comp.product_name}`}
                  stroke={getCompetitorColor(index)}
                  strokeWidth={2}
                  strokeDasharray="5 5"
                  dot={{ r: 3, fill: getCompetitorColor(index) }}
                  activeDot={{ r: 5 }}
                  connectNulls
                />
              )
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Display控制 Checkbox */}
      <div className="mt-4 pt-4 border-t border-gray-100">
        <div className="flex items-center justify-between mb-3">
          <span className="text-sm font-medium text-gray-700">
            DisplayData線 ({visibleCount}/{totalCount})
          </span>
          <div className="flex gap-2">
            <button
              onClick={() => toggleAll(true)}
              className="text-xs px-2 py-1 text-emerald-600 hover:bg-emerald-50 rounded transition-colors"
            >
              全選
            </button>
            <button
              onClick={() => toggleAll(false)}
              className="text-xs px-2 py-1 text-gray-500 hover:bg-gray-100 rounded transition-colors"
            >
              全不選
            </button>
          </div>
        </div>

        <div className="flex flex-wrap gap-3">
          {/* 自家Product */}
          <label
            className={`inline-flex items-center gap-2 px-3 py-2 rounded-lg border-2 cursor-pointer transition-all ${
              visibleLines.own
                ? 'border-purple-500 bg-purple-50'
                : 'border-gray-200 bg-gray-50 opacity-60'
            }`}
          >
            <input
              type="checkbox"
              checked={visibleLines.own}
              onChange={() => toggleVisibility('own')}
              className="sr-only"
            />
            <div
              className={`w-5 h-5 rounded flex items-center justify-center ${
                visibleLines.own ? 'bg-purple-500' : 'bg-gray-300'
              }`}
            >
              {visibleLines.own && <Check className="w-3 h-3 text-white" />}
            </div>
            <div
              className="w-4 h-1 rounded-full"
              style={{ backgroundColor: CHART_COLORS.own }}
            />
            <span className="text-sm font-medium text-gray-700">
              {ownProduct.name}
            </span>
            <span className="text-xs px-1.5 py-0.5 bg-purple-100 text-purple-700 rounded">
              自家
            </span>
          </label>

          {/* 競爭Competitor */}
          {competitors.map((comp, index) => (
            <label
              key={comp.id}
              className={`inline-flex items-center gap-2 px-3 py-2 rounded-lg border-2 cursor-pointer transition-all ${
                visibleLines[comp.id]
                  ? 'border-gray-300 bg-white'
                  : 'border-gray-200 bg-gray-50 opacity-60'
              }`}
            >
              <input
                type="checkbox"
                checked={visibleLines[comp.id] || false}
                onChange={() => toggleVisibility(comp.id)}
                className="sr-only"
              />
              <div
                className={`w-5 h-5 rounded flex items-center justify-center`}
                style={{
                  backgroundColor: visibleLines[comp.id]
                    ? getCompetitorColor(index)
                    : '#d1d5db',
                }}
              >
                {visibleLines[comp.id] && <Check className="w-3 h-3 text-white" />}
              </div>
              <div
                className="w-4 h-0.5 rounded-full"
                style={{
                  backgroundColor: getCompetitorColor(index),
                  borderStyle: 'dashed',
                }}
              />
              <span className="text-sm text-gray-700">
                {comp.name}
              </span>
            </label>
          ))}
        </div>
      </div>
    </div>
  )
}
