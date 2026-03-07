'use client'

import { useState } from 'react'
import { ProductComparison } from '@/lib/api'
import { ChevronDown, ChevronUp, ExternalLink, Crown, TrendingDown, LineChart } from 'lucide-react'
import { cn } from '@/lib/utils'
import { TierBadge } from './tier-badge'
import { PriceBadge, PriceChangeIndicator } from './price-badge'
import { motion, AnimatePresence } from 'framer-motion'

interface ProductComparisonCardProps {
  data: ProductComparison
  onShowHistory?: (productId: string, productName: string) => void
}

export function ProductComparisonCard({ data, onShowHistory }: ProductComparisonCardProps) {
  const [expanded, setExpanded] = useState(false)
  const { product, competitors, our_price_rank, total_competitors, cheapest_competitor } = data

  const isWeCheapest = our_price_rank === 1
  const cheapestPrice = competitors.length > 0 && competitors[0]?.price ? competitors[0].price : null
  const ourPrice = product.price || null

  // Calculate threat level
  let threatLevel: 'safe' | 'warning' | 'danger' = 'safe'
  let priceDiffPct = 0
  if (ourPrice && cheapestPrice && !isWeCheapest) {
    priceDiffPct = ((ourPrice - cheapestPrice) / ourPrice) * 100
    if (priceDiffPct > 20) threatLevel = 'danger'
    else if (priceDiffPct > 5) threatLevel = 'warning'
  }

  // Stock stats
  const inStockCount = competitors.filter(c => c.stock_status === 'in_stock').length
  const outOfStockCount = competitors.filter(c => c.stock_status === 'out_of_stock').length
  const cheaperCount = competitors.filter(c => c.price && ourPrice && c.price < ourPrice).length

  return (
    <div className={cn(
      'rounded-xl border transition-all shadow-sm',
      threatLevel === 'danger'
        ? 'border-red-200 bg-gradient-to-r from-white to-red-50/30'
        : isWeCheapest
          ? 'border-emerald-200 bg-gradient-to-r from-white to-emerald-50/50'
          : threatLevel === 'warning'
            ? 'border-amber-200 bg-gradient-to-r from-white to-amber-50/30'
            : 'border-gray-200 bg-white',
    )}>
      {/* Header — rich info even when collapsed */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full p-3 sm:p-4 text-left"
      >
        {/* Row 1: Product info */}
        <div className="flex items-center gap-2 sm:gap-3 mb-1.5 sm:mb-2">
          {product.category_tag && (
            <span className="shrink-0 text-[10px] sm:text-xs px-1.5 sm:px-2 py-0.5 rounded-full bg-teal-50 text-teal-600 border border-teal-200">
              {product.category_tag}
            </span>
          )}

          <span className="font-medium text-gray-700 text-sm sm:text-base truncate min-w-0 flex-1">
            {product.name.replace(/^GOGOJAP-/, '')}
          </span>

          {expanded ? (
            <ChevronUp className="w-4 h-4 text-gray-400 shrink-0" />
          ) : (
            <ChevronDown className="w-4 h-4 text-gray-400 shrink-0" />
          )}
        </div>

        {/* Row 2: Price comparison strip */}
        <div className="flex items-center gap-2 sm:gap-4 flex-wrap">
          {/* Our price */}
          <div className="flex items-center gap-1">
            <span className="text-[10px] sm:text-xs text-gray-400">我哋</span>
            <span className="font-mono text-sm sm:text-base font-bold text-teal-600">
              ${ourPrice?.toFixed(0) || 'N/A'}
            </span>
          </div>

          {/* Separator */}
          <span className="text-gray-200">|</span>

          {/* Cheapest competitor */}
          {cheapestPrice && (
            <div className="flex items-center gap-1">
              <span className="text-[10px] sm:text-xs text-gray-400">最平</span>
              <span className={cn(
                'font-mono text-sm font-semibold',
                isWeCheapest ? 'text-emerald-500' :
                threatLevel === 'danger' ? 'text-red-500' :
                threatLevel === 'warning' ? 'text-amber-500' : 'text-gray-600'
              )}>
                ${cheapestPrice.toFixed(0)}
              </span>
              {!isWeCheapest && priceDiffPct > 1 && (
                <span className={cn(
                  'text-[10px] sm:text-xs font-mono',
                  threatLevel === 'danger' ? 'text-red-500' : 'text-amber-500'
                )}>
                  (-{priceDiffPct.toFixed(0)}%)
                </span>
              )}
            </div>
          )}

          {/* Separator */}
          <span className="text-gray-200 hidden sm:inline">|</span>

          {/* Rank */}
          <div className="flex items-center gap-1">
            {isWeCheapest ? (
              <span className="flex items-center gap-0.5 text-[10px] sm:text-xs text-emerald-600 bg-emerald-50 px-1.5 py-0.5 rounded-full border border-emerald-200">
                <Crown className="w-3 h-3" /> 最平
              </span>
            ) : (
              <span className={cn(
                'text-[10px] sm:text-xs px-1.5 py-0.5 rounded-full border',
                threatLevel === 'danger'
                  ? 'text-red-600 bg-red-50 border-red-200'
                  : threatLevel === 'warning'
                    ? 'text-amber-600 bg-amber-50 border-amber-200'
                    : 'text-gray-500 bg-gray-50 border-gray-200'
              )}>
                第{our_price_rank}/{total_competitors}
              </span>
            )}
          </div>

          {/* Separator */}
          <span className="text-gray-200 hidden sm:inline">|</span>

          {/* Threat indicators */}
          <div className="hidden sm:flex items-center gap-2 text-[10px] sm:text-xs">
            {cheaperCount > 0 && (
              <span className="text-red-400 flex items-center gap-0.5">
                <TrendingDown className="w-3 h-3" />
                {cheaperCount}間更平
              </span>
            )}
            {inStockCount > 0 && (
              <span className="text-gray-400">
                {inStockCount}/{total_competitors} 有貨
              </span>
            )}
          </div>

          {/* Mobile: compact threat info */}
          <div className="sm:hidden flex items-center gap-2 text-[10px]">
            {cheaperCount > 0 && (
              <span className="text-red-400">{cheaperCount}間更平</span>
            )}
            <span className="text-gray-400">{total_competitors}間</span>
          </div>
        </div>
      </button>

      {/* Expanded: competitor price list */}
      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="px-3 sm:px-4 pb-3 sm:pb-4">
              {onShowHistory && (
                <div className="mb-2 pt-2">
                  <button
                    onClick={e => { e.stopPropagation(); onShowHistory(product.id, product.name.replace(/^GOGOJAP-/, '')) }}
                    className="flex items-center gap-1 text-[10px] sm:text-xs text-teal-500 hover:text-teal-700 bg-teal-50 hover:bg-teal-100 border border-teal-200 px-2 py-1 rounded-lg transition-colors"
                  >
                    <LineChart className="w-3 h-3" /> 查看 30 日趨勢
                  </button>
                </div>
              )}
              <div className="border-t border-gray-100 pt-2 sm:pt-3">
                {competitors.length === 0 ? (
                  <p className="text-sm text-gray-400 text-center py-4">
                    未有競品配對
                  </p>
                ) : (
                  <div className="space-y-1">
                    {/* Our price row */}
                    <div className="flex items-center gap-2 sm:gap-3 py-2 px-2 sm:px-3 rounded-lg bg-teal-50 border border-teal-100">
                      <span className="text-xs font-medium text-teal-600 w-20 sm:w-28 shrink-0 truncate">GoGoJap</span>
                      <span className="font-mono text-sm font-bold text-teal-600">
                        ${product.price?.toFixed(0) || 'N/A'}
                      </span>
                      <span className="text-[10px] text-teal-400 hidden sm:inline">我哋</span>
                    </div>

                    {/* Competitor rows */}
                    {competitors.map((comp, i) => (
                      <div
                        key={i}
                        className={cn(
                          'flex items-center gap-2 sm:gap-3 py-1.5 sm:py-2 px-2 sm:px-3 rounded-lg transition-colors',
                          i === 0 && !isWeCheapest ? 'bg-red-50/50' : 'hover:bg-gray-50'
                        )}
                      >
                        <div className="flex items-center gap-1 sm:gap-2 w-20 sm:w-28 shrink-0">
                          <span className="hidden sm:inline"><TierBadge tier={comp.competitor_tier} /></span>
                          <span className="text-[10px] sm:text-xs text-gray-500 truncate">
                            {comp.competitor_name}
                          </span>
                        </div>

                        <div className="w-16 sm:w-20">
                          <PriceBadge
                            ourPrice={product.price}
                            competitorPrice={comp.price}
                          />
                        </div>

                        <span className="hidden sm:inline">
                          <PriceChangeIndicator change7d={comp.price_change_7d} />
                        </span>

                        <span className={cn(
                          'text-[10px] sm:text-xs px-1 sm:px-1.5 py-0.5 rounded',
                          comp.stock_status === 'in_stock' ? 'text-emerald-600 bg-emerald-50' :
                          comp.stock_status === 'out_of_stock' ? 'text-red-500 bg-red-50' :
                          'text-gray-400'
                        )}>
                          {comp.stock_status === 'in_stock' ? '有貨' :
                           comp.stock_status === 'out_of_stock' ? '缺貨' : ''}
                        </span>

                        <div className="flex-1" />

                        <a
                          href={comp.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-gray-300 hover:text-teal-500 transition-colors"
                          onClick={(e) => e.stopPropagation()}
                        >
                          <ExternalLink className="w-3 h-3 sm:w-3.5 sm:h-3.5" />
                        </a>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
