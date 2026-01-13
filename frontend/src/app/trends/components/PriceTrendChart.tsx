// =============================================
// 價格趨勢圖表組件
// =============================================

'use client'

import { useMemo } from 'react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts'
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
  // 處理圖表數據
  const chartData = useMemo(() => {
    // 收集所有日期
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

    // 按日期排序
    const sortedDates = Array.from(allDates).sort((a, b) => {
      // 解析日期進行排序
      return new Date(a).getTime() - new Date(b).getTime()
    })

    // 建立日期到數據的映射
    const dateDataMap: Record<string, { date: string; [key: string]: string | number | null }> = {}

    // 初始化所有日期
    sortedDates.forEach((date) => {
      dateDataMap[date] = { date }
    })

    // 填充自家產品數據
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

    // 填充競爭對手數據
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

  // 計算 Y 軸範圍
  const yAxisDomain = useMemo(() => {
    let min = Infinity
    let max = -Infinity

    chartData.forEach((item) => {
      Object.entries(item).forEach(([key, value]) => {
        if (key !== 'date' && typeof value === 'number') {
          min = Math.min(min, value)
          max = Math.max(max, value)
        }
      })
    })

    if (min === Infinity) return [0, 100]

    const padding = (max - min) * 0.1
    return [Math.floor(min - padding), Math.ceil(max + padding)]
  }, [chartData])

  // 自定義 Tooltip
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (!active || !payload?.length) return null

    return (
      <div className="bg-white border border-gray-200 rounded-lg shadow-lg p-3">
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

  // 如果沒有數據
  if (chartData.length === 0) {
    return (
      <div className="h-[400px] flex items-center justify-center text-gray-500">
        暫無價格數據
      </div>
    )
  }

  return (
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
          <Legend
            wrapperStyle={{ paddingTop: 20 }}
            iconType="circle"
            iconSize={8}
          />

          {/* 自家產品線（實線） */}
          <Line
            type="monotone"
            dataKey="own"
            name={ownProduct.name}
            stroke={CHART_COLORS.own}
            strokeWidth={3}
            dot={{ r: 4, fill: CHART_COLORS.own }}
            activeDot={{ r: 6 }}
            connectNulls
          />

          {/* 競爭對手線（虛線） */}
          {competitors.map((comp, index) => (
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
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
