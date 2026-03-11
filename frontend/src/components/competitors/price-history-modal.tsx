'use client'

import { useQuery } from '@tanstack/react-query'
import { api, PriceHistoryData } from '@/lib/api'
import { X, TrendingUp } from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

const COLORS = ['#ef4444', '#f97316', '#eab308', '#22c55e', '#3b82f6', '#8b5cf6', '#ec4899', '#14b8a6']

interface PriceHistoryModalProps {
  productId: string
  productName: string
  onClose: () => void
}

export function PriceHistoryModal({ productId, productName, onClose }: PriceHistoryModalProps) {
  const { data, isLoading } = useQuery({
    queryKey: ['price-history', productId],
    queryFn: () => api.getPriceHistory(productId, 30),
  })

  // Build recharts data
  const chartData = data?.dates.map((date, i) => {
    const point: Record<string, string | number | null> = { date: date.slice(5) } // MM-DD
    data.series.forEach(s => {
      point[s.name] = s.data[i]
    })
    return point
  }) ?? []

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40" onClick={onClose}>
      <div
        className="bg-white rounded-2xl shadow-xl w-full max-w-3xl max-h-[90vh] overflow-hidden"
        onClick={e => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-100">
          <div className="flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-teal-500" />
            <div>
              <h3 className="font-semibold text-gray-800 text-sm sm:text-base">{productName}</h3>
              <p className="text-xs text-gray-400">Competitor Price Trends Over Last 30 Days</p>
            </div>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 p-1">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Chart */}
        <div className="p-4">
          {isLoading ? (
            <div className="h-64 flex items-center justify-center">
              <div className="text-sm text-gray-400 animate-pulse">Loading...</div>
            </div>
          ) : chartData.length === 0 || !data?.series.length ? (
            <div className="h-64 flex items-center justify-center">
              <p className="text-sm text-gray-400">Not enough historical data</p>
            </div>
          ) : (
            <>
              {/* Our price reference */}
              {data?.our_price && (
                <div className="mb-3 inline-flex items-center gap-2 bg-teal-50 border border-teal-200 rounded-lg px-3 py-1.5">
                  <span className="text-xs text-teal-600">GoGoJap current price:</span>
                  <span className="font-mono font-bold text-teal-700">${data.our_price.toFixed(0)}</span>
                </div>
              )}
              <ResponsiveContainer width="100%" height={280}>
                <LineChart data={chartData} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis dataKey="date" tick={{ fontSize: 10 }} tickLine={false} />
                  <YAxis tick={{ fontSize: 10 }} tickLine={false} axisLine={false} tickFormatter={v => `$${v}`} />
                  <Tooltip
                    formatter={(value: number, name: string) => [`$${value?.toFixed(0) || 'N/A'}`, name]}
                    contentStyle={{ fontSize: 12, borderRadius: 8, border: '1px solid #e5e7eb' }}
                  />
                  <Legend wrapperStyle={{ fontSize: 11 }} />
                  {/* Our price as reference line */}
                  {data?.our_price && (
                    <Line type="monotone" dataKey="GoGoJap" stroke="#0d9488" strokeWidth={2} strokeDasharray="4 4" dot={false} connectNulls={false} name="GoGoJap" />
                  )}
                  {data?.series.map((s, i) => (
                    <Line
                      key={s.id}
                      type="monotone"
                      dataKey={s.name}
                      stroke={COLORS[i % COLORS.length]}
                      strokeWidth={1.5}
                      dot={false}
                      connectNulls
                    />
                  ))}
                </LineChart>
              </ResponsiveContainer>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
