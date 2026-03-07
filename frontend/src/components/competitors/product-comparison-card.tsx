'use client'

import { useState } from 'react'
import { ProductComparison } from '@/lib/api'
import { ChevronDown, ChevronUp, ExternalLink, Crown } from 'lucide-react'
import { cn } from '@/lib/utils'
import { TierBadge } from './tier-badge'
import { PriceBadge, PriceChangeIndicator } from './price-badge'
import { motion, AnimatePresence } from 'framer-motion'

interface ProductComparisonCardProps {
  data: ProductComparison
}

export function ProductComparisonCard({ data }: ProductComparisonCardProps) {
  const [expanded, setExpanded] = useState(false)
  const { product, competitors, our_price_rank, total_competitors } = data

  const isWeCheapest = our_price_rank === 1

  return (
    <div className={cn(
      'rounded-xl border transition-all shadow-sm',
      isWeCheapest
        ? 'border-emerald-200 bg-gradient-to-r from-white to-emerald-50/50'
        : 'border-gray-200 bg-white',
    )}>
      {/* Header — mobile: stack vertically */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full p-3 sm:p-4 flex items-center justify-between text-left"
      >
        <div className="flex items-center gap-2 sm:gap-3 flex-1 min-w-0">
          {product.category_tag && (
            <span className="hidden sm:inline-flex shrink-0 text-xs px-2 py-0.5 rounded-full bg-teal-50 text-teal-600 border border-teal-200">
              {product.category_tag}
            </span>
          )}

          <span className="font-medium text-gray-700 text-sm sm:text-base truncate min-w-0">
            {product.name.replace(/^GOGOJAP-/, '')}
          </span>

          {product.price && (
            <span className="shrink-0 font-mono text-sm font-bold text-teal-600">
              ${product.price.toFixed(0)}
            </span>
          )}

          {isWeCheapest && total_competitors > 0 && (
            <span className="shrink-0 flex items-center gap-0.5 text-[10px] sm:text-xs text-emerald-600 bg-emerald-50 px-1.5 sm:px-2 py-0.5 rounded-full border border-emerald-200">
              <Crown className="w-3 h-3" />
              <span className="hidden sm:inline">最平</span>
            </span>
          )}
        </div>

        <div className="flex items-center gap-2 sm:gap-3 shrink-0 ml-2">
          <span className="text-[10px] sm:text-xs text-gray-400">
            {total_competitors}
            <span className="hidden sm:inline"> 間競品</span>
          </span>
          {expanded ? (
            <ChevronUp className="w-4 h-4 text-gray-400" />
          ) : (
            <ChevronDown className="w-4 h-4 text-gray-400" />
          )}
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
              {/* Mobile: category tag shown here */}
              {product.category_tag && (
                <span className="sm:hidden inline-flex mb-2 text-[10px] px-2 py-0.5 rounded-full bg-teal-50 text-teal-600 border border-teal-200">
                  {product.category_tag}
                </span>
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
                        className="flex items-center gap-2 sm:gap-3 py-1.5 sm:py-2 px-2 sm:px-3 rounded-lg hover:bg-gray-50 transition-colors"
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
