'use client'

import { ProductComparison } from '@/lib/api'
import { Crown, ChevronUp, ChevronDown } from 'lucide-react'
import { cn } from '@/lib/utils'

interface ProductComparisonCardProps {
  data: ProductComparison
  selected?: boolean
  onClick?: () => void
  onShowHistory?: (productId: string, productName: string) => void
}

export function ProductComparisonCard({ data, selected, onClick }: ProductComparisonCardProps) {
  const { product, competitors, our_price_rank, total_competitors } = data

  const isWeCheapest = our_price_rank === 1
  const cheapestPrice = competitors.length > 0 && competitors[0]?.price ? competitors[0].price : null
  const ourPrice = product.price || null

  // Threat level
  let threatLevel: 'safe' | 'warning' | 'danger' = 'safe'
  let priceDiffPct = 0
  let priceDiffAbs = 0
  if (ourPrice && cheapestPrice && !isWeCheapest) {
    priceDiffAbs = ourPrice - cheapestPrice
    priceDiffPct = (priceDiffAbs / ourPrice) * 100
    if (priceDiffPct > 20) threatLevel = 'danger'
    else if (priceDiffPct > 5) threatLevel = 'warning'
  }

  const cheaperCount = competitors.filter(c => c.price && ourPrice && c.price < ourPrice).length
  const inStockCount = competitors.filter(c => c.stock_status === 'in_stock').length
  const outOfStockCount = competitors.filter(c => c.stock_status === 'out_of_stock').length

  // Stock label
  const stockLabel = outOfStockCount > 0 && inStockCount === 0
    ? '已退車'
    : outOfStockCount > 0
      ? `${inStockCount}有/${outOfStockCount}缺`
      : inStockCount > 0
        ? '有貨'
        : '無資料'

  return (
    <button
      onClick={onClick}
      className={cn(
        'w-full text-left rounded-xl border transition-all duration-150',
        selected
          ? 'border-teal-400 bg-white shadow-md ring-1 ring-teal-300/50'
          : 'border-gray-100 bg-white hover:border-gray-300 hover:shadow-sm',
      )}
    >
      <div className="p-3 sm:p-4">
        {/* Row 1: Product name */}
        <div className="flex items-center gap-2 mb-2.5">
          {product.category_tag && (
            <span className="shrink-0 text-[10px] px-1.5 py-0.5 rounded-full bg-teal-50 text-teal-600 border border-teal-200">
              {product.category_tag}
            </span>
          )}
          <span className={cn(
            'font-medium text-sm truncate min-w-0 flex-1',
            selected ? 'text-teal-700' : 'text-gray-800'
          )}>
            {product.name.replace(/^GOGOJAP-/, '')}
          </span>
          {selected ? (
            <ChevronUp className="w-3.5 h-3.5 text-teal-400 shrink-0" />
          ) : (
            <ChevronDown className="w-3.5 h-3.5 text-gray-300 shrink-0" />
          )}
        </div>

        {/* Row 2: Data grid — mimicking reference layout */}
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-x-3 gap-y-2 text-xs">
          {/* GoGoJap 價格 */}
          <div>
            <div className="text-[10px] text-gray-400 mb-0.5">GoGoJap 價格</div>
            <div className="font-mono font-bold text-teal-600 text-sm">
              ${ourPrice?.toFixed(0) || 'N/A'}
            </div>
          </div>

          {/* 最低競手價 + 價差 */}
          <div>
            <div className="text-[10px] text-gray-400 mb-0.5">最低競手價格</div>
            <div className="flex items-baseline gap-1.5">
              {cheapestPrice ? (
                <>
                  <span className={cn(
                    'font-mono font-semibold',
                    isWeCheapest ? 'text-emerald-500' :
                    threatLevel === 'danger' ? 'text-red-500' :
                    threatLevel === 'warning' ? 'text-amber-500' : 'text-gray-700'
                  )}>
                    ${cheapestPrice.toFixed(0)}
                  </span>
                  {!isWeCheapest && priceDiffPct > 1 && (
                    <span className={cn(
                      'text-[10px] font-mono font-medium',
                      threatLevel === 'danger' ? 'text-red-500' : 'text-amber-500'
                    )}>
                      -{priceDiffPct.toFixed(1)}%
                    </span>
                  )}
                </>
              ) : (
                <span className="text-gray-400">-</span>
              )}
            </div>
          </div>

          {/* 便宜競比數 */}
          <div>
            <div className="text-[10px] text-gray-400 mb-0.5">便宜競比數</div>
            <div className={cn(
              'font-semibold',
              cheaperCount > 0 ? 'text-red-500' : 'text-emerald-500'
            )}>
              {cheaperCount}
            </div>
          </div>

          {/* 排名 */}
          <div>
            <div className="text-[10px] text-gray-400 mb-0.5">排名</div>
            <div className="flex items-center gap-1">
              {isWeCheapest ? (
                <span className="flex items-center gap-0.5 text-emerald-600 font-semibold">
                  <Crown className="w-3 h-3" /> 1/{total_competitors}
                </span>
              ) : (
                <span className={cn(
                  'font-semibold',
                  threatLevel === 'danger' ? 'text-red-600' :
                  threatLevel === 'warning' ? 'text-amber-600' : 'text-gray-600'
                )}>
                  {our_price_rank}/{total_competitors}
                </span>
              )}
            </div>
          </div>

          {/* 股貨狀態 */}
          <div>
            <div className="text-[10px] text-gray-400 mb-0.5">股貨狀態</div>
            <div className={cn(
              'font-medium text-[11px]',
              outOfStockCount > 0 && inStockCount === 0 ? 'text-red-500' :
              outOfStockCount > 0 ? 'text-amber-500' :
              inStockCount > 0 ? 'text-emerald-500' : 'text-gray-400'
            )}>
              {stockLabel}
            </div>
          </div>
        </div>
      </div>
    </button>
  )
}
