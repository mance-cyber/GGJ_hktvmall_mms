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
      'rounded-xl border transition-all',
      isWeCheapest
        ? 'border-emerald-500/30 bg-emerald-500/5'
        : 'border-slate-800 bg-slate-900/50',
    )}>
      {/* Header */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full p-4 flex items-center justify-between text-left"
      >
        <div className="flex items-center gap-3 flex-1 min-w-0">
          {/* Category badge */}
          {product.category_tag && (
            <span className="shrink-0 text-xs px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
              {product.category_tag}
            </span>
          )}

          {/* Product name */}
          <span className="font-medium text-slate-200 truncate">
            {product.name}
          </span>

          {/* Our price */}
          {product.price && (
            <span className="shrink-0 font-mono text-sm font-bold text-cyan-400">
              ${product.price.toFixed(0)}
            </span>
          )}

          {/* Rank badge */}
          {isWeCheapest && total_competitors > 0 && (
            <span className="shrink-0 flex items-center gap-1 text-xs text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full">
              <Crown className="w-3 h-3" /> 最平
            </span>
          )}
        </div>

        <div className="flex items-center gap-3 shrink-0 ml-3">
          {/* Competitor count */}
          <span className="text-xs text-slate-500">
            {total_competitors} 間競品
          </span>

          {/* Expand icon */}
          {expanded ? (
            <ChevronUp className="w-4 h-4 text-slate-500" />
          ) : (
            <ChevronDown className="w-4 h-4 text-slate-500" />
          )}
        </div>
      </button>

      {/* Expanded: competitor price table */}
      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="px-4 pb-4">
              <div className="border-t border-slate-800 pt-3">
                {competitors.length === 0 ? (
                  <p className="text-sm text-slate-500 text-center py-4">
                    未有競品配對
                  </p>
                ) : (
                  <div className="space-y-2">
                    {/* Our price row */}
                    <div className="flex items-center gap-3 py-2 px-3 rounded-lg bg-cyan-500/5 border border-cyan-500/20">
                      <span className="text-xs font-medium text-cyan-400 w-28 shrink-0">GoGoJap</span>
                      <span className="font-mono text-sm font-bold text-cyan-400 w-20">
                        ${product.price?.toFixed(0) || 'N/A'}
                      </span>
                      <span className="text-xs text-cyan-400/60">我哋</span>
                    </div>

                    {/* Competitor rows */}
                    {competitors.map((comp, i) => (
                      <div
                        key={i}
                        className="flex items-center gap-3 py-2 px-3 rounded-lg hover:bg-slate-800/50 transition-colors"
                      >
                        <div className="flex items-center gap-2 w-28 shrink-0">
                          <TierBadge tier={comp.competitor_tier} />
                          <span className="text-xs text-slate-400 truncate">
                            {comp.competitor_name}
                          </span>
                        </div>

                        <div className="w-20">
                          <PriceBadge
                            ourPrice={product.price}
                            competitorPrice={comp.price}
                          />
                        </div>

                        <PriceChangeIndicator change7d={comp.price_change_7d} />

                        <span className={cn(
                          'text-xs px-1.5 py-0.5 rounded',
                          comp.stock_status === 'in_stock' ? 'text-emerald-500 bg-emerald-500/10' :
                          comp.stock_status === 'out_of_stock' ? 'text-red-500 bg-red-500/10' :
                          'text-slate-500'
                        )}>
                          {comp.stock_status === 'in_stock' ? '有貨' :
                           comp.stock_status === 'out_of_stock' ? '缺貨' : ''}
                        </span>

                        <div className="flex-1" />

                        <a
                          href={comp.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-slate-600 hover:text-cyan-400 transition-colors"
                          onClick={(e) => e.stopPropagation()}
                        >
                          <ExternalLink className="w-3.5 h-3.5" />
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
