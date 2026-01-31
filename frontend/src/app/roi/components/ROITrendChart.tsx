// =============================================
// ROI 趨勢圖表組件
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
  Legend,
} from 'recharts'
import { Check, Loader2 } from 'lucide-react'
import { useROITrends } from '../hooks/useROIData'

interface ROITrendChartProps {
  days?: number
}

// 圖表顏色配置
const CHART_COLORS = {
  cumulative: '#22c55e',   // 綠色 - 累計價值
  ai_pricing: '#8b5cf6',   // 紫色 - AI 定價
  monitoring: '#06b6d4',   // 青色 - 競品監測
  risk: '#f59e0b',         // 橙色 - 風險規避
}

export function ROITrendChart({ days = 30 }: ROITrendChartProps) {
  const { data, isLoading, error } = useROITrends(days)

  // 可見性狀態
  const [visibleLines, setVisibleLines] = useState({
    cumulative: true,
    ai_pricing: true,
    monitoring: true,
    risk_avoidance: false,
  })

  // 切換可見性
  const toggleVisibility = (key: keyof typeof visibleLines) => {
    setVisibleLines((prev) => ({ ...prev, [key]: !prev[key] }))
  }

  // 處理圖表數據
  const chartData = useMemo(() => {
    if (!data?.trends) return []

    return data.trends.map((point) => ({
      date: new Date(point.date).toLocaleDateString('zh-HK', {
        month: 'short',
        day: 'numeric',
      }),
      cumulative: Number(point.cumulative_value),
      ai_pricing: Number(point.ai_pricing),
      monitoring: Number(point.monitoring),
      risk_avoidance: Number(point.risk_avoidance),
    }))
  }, [data])

  // 自定義 Tooltip
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
              ${entry.value.toLocaleString()}
            </span>
          </div>
        ))}
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="h-[400px] flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="h-[400px] flex items-center justify-center text-red-500">
        載入失敗
      </div>
    )
  }

  if (chartData.length === 0) {
    return (
      <div className="h-[400px] flex items-center justify-center text-gray-500">
        暫無趨勢數據
      </div>
    )
  }

  // 數據線配置
  const lines = [
    { key: 'cumulative', name: '累計價值', color: CHART_COLORS.cumulative, strokeWidth: 3 },
    { key: 'ai_pricing', name: 'AI 定價貢獻', color: CHART_COLORS.ai_pricing, strokeWidth: 2 },
    { key: 'monitoring', name: '競品監測價值', color: CHART_COLORS.monitoring, strokeWidth: 2 },
    { key: 'risk_avoidance', name: '風險規避', color: CHART_COLORS.risk, strokeWidth: 2, strokeDasharray: '5 5' },
  ]

  return (
    <div>
      {/* 圖表 */}
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
              tick={{ fontSize: 12 }}
              stroke="#9ca3af"
              tickLine={false}
              tickFormatter={(value) => `$${value}`}
            />
            <Tooltip content={<CustomTooltip />} />

            {lines.map((line) =>
              visibleLines[line.key as keyof typeof visibleLines] ? (
                <Line
                  key={line.key}
                  type="monotone"
                  dataKey={line.key}
                  name={line.name}
                  stroke={line.color}
                  strokeWidth={line.strokeWidth}
                  strokeDasharray={line.strokeDasharray}
                  dot={{ r: 3, fill: line.color }}
                  activeDot={{ r: 5 }}
                  connectNulls
                />
              ) : null
            )}
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* 圖例控制 */}
      <div className="mt-4 pt-4 border-t border-gray-100">
        <div className="flex flex-wrap gap-3">
          {lines.map((line) => (
            <label
              key={line.key}
              className={`inline-flex items-center gap-2 px-3 py-2 rounded-lg border-2 cursor-pointer transition-all ${
                visibleLines[line.key as keyof typeof visibleLines]
                  ? 'border-gray-300 bg-white'
                  : 'border-gray-200 bg-gray-50 opacity-60'
              }`}
            >
              <input
                type="checkbox"
                checked={visibleLines[line.key as keyof typeof visibleLines]}
                onChange={() => toggleVisibility(line.key as keyof typeof visibleLines)}
                className="sr-only"
              />
              <div
                className="w-5 h-5 rounded flex items-center justify-center"
                style={{
                  backgroundColor: visibleLines[line.key as keyof typeof visibleLines]
                    ? line.color
                    : '#d1d5db',
                }}
              >
                {visibleLines[line.key as keyof typeof visibleLines] && (
                  <Check className="w-3 h-3 text-white" />
                )}
              </div>
              <div
                className="w-4 h-0.5 rounded-full"
                style={{ backgroundColor: line.color }}
              />
              <span className="text-sm text-gray-700">{line.name}</span>
            </label>
          ))}
        </div>
      </div>
    </div>
  )
}
