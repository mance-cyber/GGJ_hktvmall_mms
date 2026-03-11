'use client'

import { useQuery } from '@tanstack/react-query'
import { api, ProductComparison } from '@/lib/api'
import { X, TrendingUp, ExternalLink } from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { cn } from '@/lib/utils'
import { TierBadge } from './tier-badge'

const CHART_COLORS = ['#ef4444', '#f97316', '#eab308', '#22c55e', '#3b82f6', '#8b5cf6', '#ec4899']

/* ── Tiny inline sparkline (SVG) ── */
function Sparkline({ data, color = '#94a3b8', width = 64, height = 20 }: {
  data: (number | null)[]
  color?: string
  width?: number
  height?: number
}) {
  const nums = data.filter((v): v is number => v !== null)
  if (nums.length < 2) return <span className="text-[10px] text-gray-300">—</span>

  const min = Math.min(...nums)
  const max = Math.max(...nums)
  const range = max - min || 1

  const points = nums.map((v, i) => {
    const x = (i / (nums.length - 1)) * width
    const y = height - ((v - min) / range) * (height - 4) - 2
    return `${x},${y}`
  }).join(' ')

  // Trend color: compare last vs first
  const trend = nums[nums.length - 1] > nums[0] ? '#ef4444' : nums[nums.length - 1] < nums[0] ? '#22c55e' : color

  return (
    <svg width={width} height={height} className="inline-block">
      <polyline
        points={points}
        fill="none"
        stroke={trend}
        strokeWidth={1.5}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  )
}

interface ProductDetailPanelProps {
  data: ProductComparison
  onClose?: () => void
}

export function ProductDetailPanel({ data, onClose }: ProductDetailPanelProps) {
  const { product, competitors, our_price_rank, total_competitors } = data
  const productName = product.name.replace(/^GOGOJAP-/, '')

  const { data: history, isLoading: historyLoading } = useQuery({
    queryKey: ['price-history', product.id],
    queryFn: () => api.getPriceHistory(product.id, 30),
  })

  const chartData = history?.dates.map((date, i) => {
    const point: Record<string, string | number | null> = { date: date.slice(5) }
    history.series.forEach(s => {
      point[s.name] = s.data[i]
    })
    return point
  }) ?? []

  const isWeCheapest = our_price_rank === 1
  const ourPrice = product.price || null
  const cheapestPrice = competitors[0]?.price || null
  let priceDiffPct = 0
  if (ourPrice && cheapestPrice && !isWeCheapest) {
    priceDiffPct = ((ourPrice - cheapestPrice) / ourPrice) * 100
  }

  // Build sparkline data per competitor from history
  const sparklineMap = new Map<string, (number | null)[]>()
  if (history) {
    history.series.forEach(s => {
      // Last 7 data points for sparkline
      const last7 = s.data.slice(-7)
      sparklineMap.set(s.name, last7)
    })
  }

  return (
    <div className="flex flex-col h-full bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
      {/* Panel Header */}
      <div className="flex items-start justify-between gap-2 p-3 sm:p-4 border-b border-gray-100 bg-gradient-to-r from-teal-50/50 to-white shrink-0">
        <div className="min-w-0">
          {product.category_tag && (
            <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-teal-100 text-teal-600 border border-teal-200 mb-1 inline-block">
              {product.category_tag}
            </span>
          )}
          <h3 className="font-semibold text-gray-800 text-sm leading-snug">{productName}</h3>
          <div className="flex items-center gap-2 mt-1 flex-wrap">
            <span className="text-xs text-gray-400">GoGoJap</span>
            <span className="font-mono font-bold text-teal-600 text-sm">${ourPrice?.toFixed(0) || 'N/A'}</span>
            {!isWeCheapest && cheapestPrice && (
              <>
                <span className="text-gray-200">|</span>
                <span className="text-xs text-gray-400">Lowest Price Gap</span>
                <span className={cn(
                  'font-mono font-semibold text-sm',
                  priceDiffPct > 20 ? 'text-red-500' : priceDiffPct > 5 ? 'text-amber-500' : 'text-gray-600'
                )}>${cheapestPrice.toFixed(0)}</span>
                {priceDiffPct > 1 && (
                  <span className={cn(
                    'text-[10px] font-mono',
                    priceDiffPct > 20 ? 'text-red-500' : 'text-amber-500'
                  )}>-{priceDiffPct.toFixed(1)}%</span>
                )}
              </>
            )}
            {isWeCheapest && (
              <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-emerald-50 text-emerald-600 border border-emerald-200">
                Lowest Price 🏆
              </span>
            )}
          </div>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="shrink-0 text-gray-300 hover:text-gray-500 transition-colors p-1 rounded-lg hover:bg-gray-100"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Scrollable content */}
      <div className="flex-1 overflow-y-auto">
        {/* Price History Chart */}
        <div className="p-3 sm:p-4 border-b border-gray-100">
          <div className="flex items-center gap-1.5 mb-3">
            <TrendingUp className="w-3.5 h-3.5 text-teal-500" />
            <span className="text-xs font-medium text-gray-600">30-Day Price Trend</span>
          </div>

          {historyLoading ? (
            <div className="h-44 flex items-center justify-center">
              <div className="text-xs text-gray-400 animate-pulse">Loading...</div>
            </div>
          ) : chartData.length === 0 || !history?.series.length ? (
            <div className="h-44 flex items-center justify-center">
              <p className="text-xs text-gray-400">Not enough historical data</p>
            </div>
          ) : (
            <>
              {history?.our_price && (
                <div className="mb-2 inline-flex items-center gap-1.5 bg-teal-50 border border-teal-200 rounded-lg px-2.5 py-1">
                  <span className="text-[10px] text-teal-500">Current</span>
                  <span className="font-mono font-bold text-teal-700 text-xs">${history.our_price.toFixed(0)}</span>
                </div>
              )}
              <ResponsiveContainer width="100%" height={180}>
                <LineChart data={chartData} margin={{ top: 4, right: 8, left: -16, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
                  <XAxis dataKey="date" tick={{ fontSize: 9 }} tickLine={false} interval="preserveStartEnd" />
                  <YAxis tick={{ fontSize: 9 }} tickLine={false} axisLine={false} tickFormatter={v => `$${v}`} />
                  <Tooltip
                    formatter={(value: number, name: string) => [`$${value?.toFixed(0) || 'N/A'}`, name]}
                    contentStyle={{ fontSize: 11, borderRadius: 8, border: '1px solid #e5e7eb' }}
                  />
                  <Legend wrapperStyle={{ fontSize: 10 }} />
                  {history?.our_price && (
                    <Line type="monotone" dataKey="GoGoJap" stroke="#0d9488" strokeWidth={2.5} strokeDasharray="4 4" dot={false} connectNulls={false} />
                  )}
                  {history?.series.map((s, i) => (
                    <Line
                      key={s.id}
                      type="monotone"
                      dataKey={s.name}
                      stroke={CHART_COLORS[i % CHART_COLORS.length]}
                      strokeWidth={1.5}
                      dot={false}
                      connectNulls
                    />
                  ))}
                </LineChart>
              </ResponsiveContainer>

              {/* "30-Day Trend" label below chart */}
              <div className="mt-1.5 text-center">
                <span className="text-[10px] text-gray-400 bg-gray-50 px-2 py-0.5 rounded-full">
                  30-Day Trend
                </span>
              </div>
            </>
          )}
        </div>

        {/* Competitor Table */}
        <div className="p-3 sm:p-4">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-medium text-gray-600">Competitor Prices ({total_competitors} merchants)</span>
            <span className="text-[10px] text-gray-400">Ranking {our_price_rank}/{total_competitors}</span>
          </div>

          {competitors.length === 0 ? (
            <p className="text-xs text-gray-400 text-center py-6">No competitor pairs yet</p>
          ) : (
            <div className="overflow-x-auto -mx-1">
              <table className="w-full text-xs">
                <thead>
                  <tr className="border-b border-gray-100">
                    <th className="text-left text-[10px] text-gray-400 font-normal py-1.5 px-2">Merchant</th>
                    <th className="text-left text-[10px] text-gray-400 font-normal py-1.5 px-2">Competitor Product</th>
                    <th className="text-right text-[10px] text-gray-400 font-normal py-1.5 px-2">Price</th>
                    <th className="text-center text-[10px] text-gray-400 font-normal py-1.5 px-2 hidden sm:table-cell">7-Day Trend</th>
                    <th className="text-center text-[10px] text-gray-400 font-normal py-1.5 px-2">Stock</th>
                    <th className="text-right text-[10px] text-gray-400 font-normal py-1.5 px-2">Link</th>
                  </tr>
                </thead>
                <tbody>
                  {/* GoGoJap row */}
                  <tr className="bg-teal-50/70 border-b border-teal-100">
                    <td className="py-2 px-2 font-semibold text-teal-700 whitespace-nowrap">GoGoJap ⭐</td>
                    <td className="py-2 px-2 text-xs text-teal-600">{productName}</td>
                    <td className="py-2 px-2 text-right font-mono font-bold text-teal-600">
                      ${product.price?.toFixed(0) || 'N/A'}
                    </td>
                    <td className="py-2 px-2 text-center hidden sm:table-cell">
                      {sparklineMap.get('GoGoJap') ? (
                        <Sparkline data={sparklineMap.get('GoGoJap')!} color="#0d9488" />
                      ) : (
                        <span className="text-gray-300">—</span>
                      )}
                    </td>
                    <td className="py-2 px-2 text-center text-teal-500">In stock</td>
                    <td className="py-2 px-2 text-right text-gray-300">—</td>
                  </tr>

                  {/* Competitor rows */}
                  {competitors.map((comp, i) => {
                    const sparkData = sparklineMap.get(comp.competitor_name)
                    return (
                      <tr
                        key={i}
                        className={cn(
                          'border-b border-gray-50 transition-colors hover:bg-gray-50/80',
                          i === 0 && !isWeCheapest && 'bg-red-50/30'
                        )}
                      >
                        <td className="py-2 px-2">
                          <div className="flex items-center gap-1.5">
                            <TierBadge tier={comp.competitor_tier} />
                            <span className="text-gray-700 truncate max-w-[120px]">{comp.competitor_name}</span>
                          </div>
                        </td>
                        <td className="py-2 px-2">
                          <span className="text-[11px] text-gray-500 line-clamp-2 leading-tight" title={comp.product_name}>
                            {comp.product_name}
                          </span>
                        </td>
                        <td className="py-2 px-2 text-right">
                          <span className={cn(
                            'font-mono font-semibold',
                            ourPrice && comp.price && comp.price < ourPrice ? 'text-red-500' :
                            ourPrice && comp.price && comp.price > ourPrice ? 'text-emerald-500' :
                            'text-gray-700'
                          )}>
                            ${comp.price?.toFixed(0) || 'N/A'}
                          </span>
                        </td>
                        <td className="py-2 px-2 text-center hidden sm:table-cell">
                          {sparkData ? (
                            <Sparkline data={sparkData} />
                          ) : (
                            <span className="text-gray-300">—</span>
                          )}
                        </td>
                        <td className="py-2 px-2 text-center">
                          <span className={cn(
                            'text-[10px] px-1.5 py-0.5 rounded',
                            comp.stock_status === 'out_of_stock' ? 'text-red-500 bg-red-50' :
                            comp.stock_level !== null && comp.stock_level !== undefined && comp.stock_level <= 10 ? 'text-amber-600 bg-amber-50' :
                            comp.stock_status === 'in_stock' ? 'text-emerald-600 bg-emerald-50' : 'text-gray-400'
                          )}>
                            {comp.stock_status === 'out_of_stock' ? 'Out of stock' :
                             comp.stock_status === 'in_stock'
                               ? (comp.stock_level !== null && comp.stock_level !== undefined ? `${comp.stock_level} items` : 'In stock')
                               : '-'}
                          </span>
                        </td>
                        <td className="py-2 px-2 text-right">
                          {comp.url ? (
                            <a
                              href={comp.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-gray-400 hover:text-teal-500 transition-colors inline-flex items-center gap-0.5 text-[10px]"
                              onClick={e => e.stopPropagation()}
                            >
                              <ExternalLink className="w-3 h-3" />
                            </a>
                          ) : (
                            <span className="text-gray-300">—</span>
                          )}
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
